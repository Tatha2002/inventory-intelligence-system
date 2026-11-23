from django.urls import path
from manager_portal import views

urlpatterns = [
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_create, name="product_create"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/edit/", views.product_update, name="product_update"),
    path("stock/", views.stock_overview, name="stock_overview"),
    path("stock/adjust/", views.stock_adjustment, name="stock_adjustment"),
    path(
        "returns/",
        views.return_request_list,
        name="manager-return-list"
    ),

    path(
        "returns/create/",
        views.return_request_create,
        name="manager-return-create"
    ),

    path(
        "returns/<int:pk>/",
        views.return_request_detail,
        name="manager-return-detail"
    ),
]