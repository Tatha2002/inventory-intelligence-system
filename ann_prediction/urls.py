
from django.urls import path
from ann_prediction import views

urlpatterns = [
    path(
        "demand-analysis/",
        views.demand_analysis,
        name="ann-demand-analysis"
    ),
]
