
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from inventory.models import Product, InventoryBatch

from django.contrib import messages
from django.shortcuts import redirect
from manager_portal.models import ProductReturnRequest


@login_required
def product_list(request):
    if request.user.role != "INVENTORY_STAFF":
        raise PermissionDenied

    products = Product.objects.filter(is_discontinued=False).select_related("category", "supplier").annotate(total_stock=Sum("inventory_batches__stock_quantity")).order_by("product_name")

    return render(request, "staff_portal/product_list.html", {"products": products})


@login_required
def product_detail(request, product_id):
    if request.user.role != "INVENTORY_STAFF":
        raise PermissionDenied

    product = get_object_or_404(Product.objects.select_related("category", "supplier").prefetch_related("images", "inventory_batches__warehouse"), id=product_id, is_discontinued=False)

    inventory_batches = product.inventory_batches.select_related("warehouse").all()
    total_stock = inventory_batches.aggregate(total=Sum("stock_quantity"))["total"] or 0

    return render(request, "staff_portal/product_detail.html", {"product": product, "inventory_batches": inventory_batches, "total_stock": total_stock})



@login_required
def return_list(request):

    if request.user.role != "INVENTORY_STAFF":
        raise PermissionDenied

    return_requests = ProductReturnRequest.objects.filter(
        assigned_to=request.user
    ).select_related(
        "product",
        "created_by"
    ).order_by("-created_at")

    return render(
        request,
        "staff_portal/return_list.html",
        {"return_requests": return_requests}
    )


@login_required
def return_detail(request, pk):

    if request.user.role != "INVENTORY_STAFF":
        raise PermissionDenied

    return_request = get_object_or_404(
        ProductReturnRequest.objects.select_related(
            "product",
            "created_by"
        ),
        pk=pk,
        assigned_to=request.user
    )

    allowed_statuses = [
        ProductReturnRequest.Status.PROCESSING,
        ProductReturnRequest.Status.APPROVED,
        ProductReturnRequest.Status.REJECTED,
        ProductReturnRequest.Status.COMPLETED
    ]

    if request.method == "POST":

        new_status = request.POST.get("status")

        if new_status not in allowed_statuses:
            messages.error(request, "Invalid return status.")

        elif return_request.status in [
            ProductReturnRequest.Status.COMPLETED,
            ProductReturnRequest.Status.REJECTED
        ]:
            messages.error(
                request,
                "This return request is already closed."
            )

        else:
            return_request.status = new_status
            return_request.save(update_fields=[
                "status",
                "updated_at"
            ])

            messages.success(
                request,
                "Return status updated successfully."
            )

            return redirect(
                "staff-return-detail",
                pk=return_request.pk
            )

    return render(
        request,
        "staff_portal/return_detail.html",
        {
            "return_request": return_request,
            "allowed_statuses": allowed_statuses
        }
    )
