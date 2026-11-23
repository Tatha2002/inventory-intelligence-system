
from django.urls import path
from inventory import views

urlpatterns = [
    path("upload/", views.upload_inventory, name="upload_inventory"),
    path("task-status/<str:task_id>/", views.inventory_task_status, name="inventory_task_status"),
]
