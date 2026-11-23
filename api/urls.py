from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, SupplierViewSet, ComplaintListCreateAPIView, InventoryUploadAPIView, InventoryUploadStatusAPIView, DemandPredictionAPIView, DemandPredictionTaskStatusAPIView, DashboardSummaryAPIView

router = DefaultRouter()

router.register("products", ProductViewSet, basename="product")
router.register("suppliers", SupplierViewSet, basename="supplier")

urlpatterns = [
    # Product and Supplier CRUD
    path("", include(router.urls)),

    # Complaint
    path("complaints/", ComplaintListCreateAPIView.as_view(), name="complaint-list-create"),

    # Inventory upload and status
    path("inventory/upload/", InventoryUploadAPIView.as_view(), name="inventory-upload"),
    path("inventory/status/<str:task_id>/", InventoryUploadStatusAPIView.as_view(), name="inventory-upload-status"),

    # Demand prediction
    path("demand-predictions/", DemandPredictionAPIView.as_view(), name="demand-predictions"),
    path("demand-predictions/generate/<int:batch_id>/", DemandPredictionAPIView.as_view(), name="generate-demand-prediction"),
    path("demand-predictions/status/<str:task_id>/", DemandPredictionTaskStatusAPIView.as_view(), name="demand-prediction-status"),

    # Dashboard
    path("dashboard/", DashboardSummaryAPIView.as_view(), name="dashboard-summary"),
]


# Method	Endpoint	Operation
# GET	http://127.0.0.1:8000/api/products/	List all products
# POST	http://127.0.0.1:8000/api/products/	Create a new product
# GET	http://127.0.0.1:8000/api/products/1/	Retrieve product details
# PUT	http://127.0.0.1:8000/api/products/1/	Update complete product details
# PATCH	http://127.0.0.1:8000/api/products/1/	Partially update product details
# DELETE	http://127.0.0.1:8000/api/products/1/	Delete a product

# 2. Supplier APIs
# Method	Endpoint	Operation
# GET	http://127.0.0.1:8000/api/suppliers/	List all suppliers
# POST	http://127.0.0.1:8000/api/suppliers/	Create a new supplier
# GET	http://127.0.0.1:8000/api/suppliers/1/	Retrieve supplier details
# PUT	http://127.0.0.1:8000/api/suppliers/1/	Update complete supplier details
# PATCH	http://127.0.0.1:8000/api/suppliers/1/	Partially update supplier details
# DELETE	http://127.0.0.1:8000/api/suppliers/1/	Delete a supplier

# 3. Complaint APIs
# Method	Endpoint	Operation
# GET	http://127.0.0.1:8000/api/complaints/	List all complaints
# POST	http://127.0.0.1:8000/api/complaints/	Create a new complaint

# 4. Inventory Upload APIs
# Method	Endpoint	Operation
# POST	http://127.0.0.1:8000/api/inventory/upload/	Upload inventory CSV file and start background processing
# GET	http://127.0.0.1:8000/api/inventory/status/TASK_ID/	Check inventory upload task status and progress

# 5. Demand Prediction APIs
# Method	Endpoint	Operation
# GET	http://127.0.0.1:8000/api/demand-predictions/	List all demand prediction records
# POST	http://127.0.0.1:8000/api/demand-predictions/generate/1/	Generate demand prediction for a specific inventory batch
# GET	http://127.0.0.1:8000/api/demand-predictions/status/TASK_ID/	Check demand prediction task status and progress

# 6. Dashboard API
# Method	Endpoint	Operation
# GET	http://127.0.0.1:8000/api/dashboard/	Retrieve inventory dashboard summary and statistics