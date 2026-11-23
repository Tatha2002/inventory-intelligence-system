
from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.demand_prediction_dashboard,
        name="demand_prediction_dashboard"
    ),

    path(
        "generate/<int:batch_id>/",
        views.generate_demand_prediction,
        name="generate_demand_prediction"
    ),

    path(
        "task-status/<str:task_id>/",
        views.demand_prediction_task_status,
        name="demand_prediction_task_status"
    ),
]
