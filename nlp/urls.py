from django.urls import path
from . import views

urlpatterns = [
    path("complaints/", views.complaint_analysis_view, name="nlp-complaints"),
    path("complaints/task-status/<str:task_id>/", views.complaint_analysis_task_status, name="nlp_complaint_task_status"),
]