
from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from inventory.models import InventoryBatch
from .models import DemandPredictionHistory
from .tasks import generate_demand_prediction_task


def is_manager(user):
    return user.is_superuser or user.role == "STORE_MANAGER"


@login_required
@user_passes_test(is_manager)
def demand_prediction_dashboard(request):
    batches = InventoryBatch.objects.select_related(
        "product", "warehouse"
    ).all()

    predictions = DemandPredictionHistory.objects.select_related(
        "product",
        "inventory_batch",
        "inventory_batch__warehouse"
    ).order_by("-predicted_at")[:20]

    context = {
        "batches": batches,
        "predictions": predictions,
    }

    return render(
        request,
        "machine_learning/demand_dashboard.html",
        context
    )


@login_required
@user_passes_test(is_manager)
@require_POST
def generate_demand_prediction(request, batch_id):

    batch = get_object_or_404(InventoryBatch, id=batch_id)

    # Start background Celery task
    task = generate_demand_prediction_task.delay(batch.id)

    # Return task ID to JavaScript
    return JsonResponse({
        "success": True,
        "task_id": task.id,
        "message": "Demand prediction task started."
    })


@login_required
@user_passes_test(is_manager)
def demand_prediction_task_status(request, task_id):

    task = AsyncResult(task_id)

    response = {
        "status": task.state,
        "progress": 0,
        "message": "Waiting for task..."
    }

    if task.state == "PENDING":

        response["message"] = "Waiting for a Celery worker..."

    elif task.state == "STARTED":

        response["progress"] = 10
        response["message"] = "Demand prediction started..."

    elif task.state == "PROGRESS":

        task_info = task.info or {}

        response["progress"] = task_info.get("progress", 0)
        response["message"] = task_info.get(
            "message",
            "Processing demand prediction..."
        )

    elif task.state == "SUCCESS":

        response["progress"] = 100
        response["message"] = "Prediction completed successfully."
        response["result"] = task.result

    elif task.state == "FAILURE":

        response["message"] = str(task.info)
        response["progress"] = 0

    return JsonResponse(response)
