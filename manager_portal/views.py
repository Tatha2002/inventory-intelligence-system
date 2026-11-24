
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q

from inventory.models import Product, ProductImage
from inventory.forms import ProductForm

from django.db import transaction
from django.db.models import Q, Sum, F
from inventory.models import InventoryBatch, StockAdjustment
from inventory.forms import StockAdjustmentForm

from django.contrib import messages
from manager_portal.models import ProductReturnRequest
from manager_portal.forms import ProductReturnRequestForm
from permissionApp.decorators import permission_required


def is_manager(user):
    return user.is_superuser or user.role == "STORE_MANAGER"


@login_required
@user_passes_test(is_manager)
def product_list(request):
    products = Product.objects.select_related(
        "category", "supplier"
    ).all()

    search = request.GET.get("search", "").strip()

    if search:
        products = products.filter(
            Q(sku__icontains=search) |
            Q(product_name__icontains=search)
        )

    return render(
        request,
        "manager/product_list.html",
        {
            "products": products,
            "search": search
        }
    )


@login_required
@user_passes_test(is_manager)
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related(
            "category", "supplier"
        ).prefetch_related(
            "inventory_batches__warehouse"
        ),
        pk=pk
    )

    return render(
        request,
        "manager/product_detail.html",
        {"product": product}
    )


@login_required
@user_passes_test(is_manager)
def product_create(request):
    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        product = form.save()

        for image in request.FILES.getlist("images"):
            ProductImage.objects.create(product=product, image=image)

        return redirect("product_list")

    return render(request, "manager/product_form.html", {"form": form, "title": "Add Product"})


@login_required
@user_passes_test(is_manager)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)

    if request.method == "POST" and form.is_valid():
        product = form.save()

        for image in request.FILES.getlist("images"):
            ProductImage.objects.create(product=product, image=image)

        return redirect("product_list")

    return render(request, "manager/product_form.html", {"form": form, "title": "Update Product"})

@login_required
@permission_required('manage_stock')
@user_passes_test(is_manager)
def stock_overview(request):
    batches = InventoryBatch.objects.select_related("product", "warehouse").all()

    search = request.GET.get("search", "").strip()
    if search:
        batches = batches.filter(Q(product__sku__icontains=search) | Q(product__product_name__icontains=search) | Q(warehouse__name__icontains=search))

    total_stock = batches.aggregate(total=Sum("stock_quantity"))["total"] or 0
    low_stock_count = batches.filter(stock_quantity__lte=F("reorder_level")).count()

    return render(request, "manager/stock_overview.html", {
        "batches": batches,
        "search": search,
        "total_stock": total_stock,
        "low_stock_count": low_stock_count
    })


@login_required
@user_passes_test(is_manager)
def stock_adjustment(request):
    form = StockAdjustmentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            batch = InventoryBatch.objects.select_for_update().get(pk=form.cleaned_data["batch"].pk)
            quantity = form.cleaned_data["quantity"]
            adjustment_type = form.cleaned_data["adjustment_type"]

            if adjustment_type == StockAdjustment.AdjustmentType.INCREASE:
                batch.stock_quantity += quantity
            elif quantity > batch.stock_quantity:
                form.add_error("quantity", "Insufficient stock. Cannot decrease more than available quantity.")
            else:
                batch.stock_quantity -= quantity

            if not form.errors:
                batch.save(update_fields=["stock_quantity", "updated_at"])
                StockAdjustment.objects.create(batch=batch, adjustment_type=adjustment_type, quantity=quantity, reason=form.cleaned_data["reason"], adjusted_by=request.user)
                return redirect("stock_overview")

    return render(request, "manager/stock_adjustment.html", {"form": form})




@login_required
@user_passes_test(is_manager)
def return_request_list(request):

    return_requests = ProductReturnRequest.objects.select_related(
        "product",
        "created_by",
        "assigned_to"
    ).order_by("-created_at")

    return render(
        request,
        "manager/return_list.html",
        {"return_requests": return_requests}
    )


@login_required
@user_passes_test(is_manager)
def return_request_create(request):

    form = ProductReturnRequestForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():

        return_request = form.save(commit=False)

        return_request.created_by = request.user
        return_request.status = ProductReturnRequest.Status.ASSIGNED

        return_request.save()

        messages.success(
            request,
            "Return request created and assigned successfully."
        )

        return redirect("manager-return-list")

    return render(
        request,
        "manager/return_form.html",
        {"form": form}
    )


@login_required
@user_passes_test(is_manager)
def return_request_detail(request, pk):

    return_request = get_object_or_404(
        ProductReturnRequest.objects.select_related(
            "product",
            "created_by",
            "assigned_to"
        ),
        pk=pk
    )

    return render(
        request,
        "manager/return_detail.html",
        {"return_request": return_request}
    )
