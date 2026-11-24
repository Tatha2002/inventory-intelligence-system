import os
import uuid

from celery.result import AsyncResult

from django.core.files.storage import default_storage
from django.db.models import Sum, F
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied

from accounts.authentication import JWTAuthentication

from inventory.models import (Product, Supplier, Complaint, InventoryBatch,)

from machine_learning.models import DemandPredictionHistory
from machine_learning.tasks import generate_demand_prediction_task

from inventory.tasks import upload_inventory_task

from .serializers import (
    ProductSerializer,
    SupplierSerializer,
    ComplaintSerializer,
    DemandPredictionSerializer,
    InventoryUploadSerializer,
    TaskStatusSerializer,
    DashboardSerializer,
)

from .permissions import (IsAdminOrManager, IsManagerOrStaff,)


# --------------------------------------------------
# PRODUCT CRUD API
# --------------------------------------------------

class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.select_related("category", "supplier").all()

    serializer_class = ProductSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsManagerOrStaff()]

        return [IsAdminOrManager()]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "message": (
                        "This product is associated with inventory "
                        "records and cannot be deleted."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# --------------------------------------------------
# SUPPLIER CRUD API
# --------------------------------------------------

class SupplierViewSet(viewsets.ModelViewSet):

    queryset = Supplier.objects.all()

    serializer_class = SupplierSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsManagerOrStaff()]

        return [IsAdminOrManager()]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "message": (
                        "This supplier is associated with products "
                        "and cannot be deleted."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# --------------------------------------------------
# COMPLAINT API
# --------------------------------------------------

class ComplaintListCreateAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not IsAdminOrManager().has_permission(request, self):
            raise PermissionDenied(
                "Only Admin and Store Manager can view complaints."
            )

        complaints = Complaint.objects.select_related("product").all().order_by("-created_at")

        serializer = ComplaintSerializer(complaints, many=True)

        return Response(serializer.data)

    def post(self, request):

        if not IsManagerOrStaff().has_permission(request, self):
            raise PermissionDenied(
                "You do not have permission to create complaints."
            )

        serializer = ComplaintSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Complaint created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# --------------------------------------------------
# INVENTORY CSV UPLOAD API
# --------------------------------------------------

class InventoryUploadAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        if not IsAdminOrManager().has_permission(request, self):
            raise PermissionDenied(
                "Only Admin and Store Manager can upload inventory."
            )

        serializer = InventoryUploadSerializer(
            data=request.data
        )

        if serializer.is_valid():

            uploaded_file = serializer.validated_data["file"]

            safe_filename = os.path.basename(uploaded_file.name)

            file_path = default_storage.save(
                f"inventory_uploads/{uuid.uuid4().hex}_{safe_filename}",
                uploaded_file,
            )

            try:
                task = upload_inventory_task.delay(file_path)

            except Exception:
                default_storage.delete(file_path)
                raise

            return Response(
                {
                    "message": "Inventory upload started successfully.",
                    "task_id": task.id,
                    "status": "PENDING",
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# --------------------------------------------------
# INVENTORY UPLOAD STATUS API
# --------------------------------------------------

class InventoryUploadStatusAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):

        if not IsAdminOrManager().has_permission(request, self):
            raise PermissionDenied(
                "Only Admin and Store Manager can check upload status."
            )

        task = AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "status": task.state,
        }

        if task.state == "PROGRESS":

            progress_data = task.info or {}

            response_data.update({
                "progress": progress_data.get("progress", 0),
                "message": progress_data.get(
                    "message",
                    "Processing inventory..."
                ),
            })

        elif task.state == "SUCCESS":

            result_data = task.result or {}

            response_data.update({
                "progress": 100,
                "message": result_data.get(
                    "message",
                    "Inventory upload completed."
                ),
                "result": result_data.get("result", {}),
            })

        elif task.state == "FAILURE":

            response_data.update({
                "message": "Inventory upload failed.",
                "error": str(task.info),
            })

        return Response(
            TaskStatusSerializer(response_data).data
        )


# --------------------------------------------------
# DEMAND PREDICTION API
# --------------------------------------------------

class DemandPredictionAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not IsAdminOrManager().has_permission(request, self):
            raise PermissionDenied(
                "Only Admin and Store Manager can view predictions."
            )

        predictions = DemandPredictionHistory.objects.select_related(
            "product", "inventory_batch"
        ).all().order_by("-predicted_at")

        serializer = DemandPredictionSerializer(
            predictions,
            many=True
        )

        return Response(serializer.data)

    def post(self, request, batch_id):

        if not IsAdminOrManager().has_permission(request, self):
            raise PermissionDenied(
                "Only Admin and Store Manager can generate predictions."
            )

        batch = get_object_or_404(
            InventoryBatch,
            pk=batch_id
        )

        task = generate_demand_prediction_task.delay(batch.id)

        return Response(
            {
                "message": "Demand prediction started successfully.",
                "task_id": task.id,
                "status": "PENDING",
                "batch_id": batch.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


# --------------------------------------------------
# DEMAND PREDICTION TASK STATUS API
# --------------------------------------------------

class DemandPredictionTaskStatusAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):

        if not IsAdminOrManager().has_permission(request, self):
            raise PermissionDenied(
                "Only Admin and Store Manager can check prediction status."
            )

        task = AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "status": task.state,
        }

        if task.state == "PROGRESS":

            progress_data = task.info or {}

            response_data.update({
                "progress": progress_data.get("progress", 0),
                "message": progress_data.get("message", ""),
            })

        elif task.state == "SUCCESS":

            response_data.update({
                "progress": 100,
                "message": "Demand prediction completed.",
                "result": task.result,
            })

        elif task.state == "FAILURE":

            response_data.update({
                "message": "Demand prediction failed.",
                "error": str(task.info),
            })

        return Response(
            TaskStatusSerializer(response_data).data
        )


# --------------------------------------------------
# DASHBOARD SUMMARY API
# --------------------------------------------------

class DashboardSummaryAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    permission_classes = [IsAdminOrManager]

    def get(self, request):

        total_products = Product.objects.count()

        total_suppliers = Supplier.objects.count()

        total_stock = (
            InventoryBatch.objects.aggregate(
                total=Sum("stock_quantity")
            )["total"] or 0
        )

        low_stock_items = InventoryBatch.objects.filter(stock_quantity__lte=F("reorder_level")).count()

        open_complaints = Complaint.objects.filter(
            status="OPEN"
        ).count()

        total_predictions = DemandPredictionHistory.objects.count()

        data = {
            "total_products": total_products,
            "total_suppliers": total_suppliers,
            "total_stock": total_stock,
            "low_stock_items": low_stock_items,
            "open_complaints": open_complaints,
            "total_predictions": total_predictions,
        }

        serializer = DashboardSerializer(data)

        return Response(serializer.data)
