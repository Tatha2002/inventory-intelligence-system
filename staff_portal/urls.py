
from django.urls import path
from staff_portal import views

urlpatterns = [
    path("products/", views.product_list, name="staff-product-list"),
    path("products/<int:product_id>/", views.product_detail, name="staff-product-detail"),
    path(
        "returns/",
        views.return_list,
        name="staff-return-list"
    ),

    path(
        "returns/<int:pk>/",
        views.return_detail,
        name="staff-return-detail"
    ),
    path("reorder-alerts/", views.reorder_alerts, name="staff-reorder-alerts"),
]
