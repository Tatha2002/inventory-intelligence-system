
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

from inventory.models import Product, InventoryBatch, OrderSummary


@login_required(login_url="portal-login")
def demand_analysis(request):

    # Allow only Inventory Staff
    if request.user.role != "INVENTORY_STAFF":
        raise PermissionDenied

    products = Product.objects.filter(
        is_discontinued=False
    ).order_by("product_name")

    result = None
    selected_product = None
    error = None

    if request.method == "POST":

        product_id = request.POST.get("product_id")

        selected_product = get_object_or_404(
            products,
            id=product_id
        )

        # Get inventory batches
        batches = InventoryBatch.objects.filter(
            product=selected_product
        ).select_related("warehouse")

        if not batches.exists():
            error = "No inventory information is available for this product."

        else:
            # Aggregate stock and reorder level
            stock_quantity = batches.aggregate(
                total=Sum("stock_quantity")
            )["total"] or 0

            reorder_level = batches.aggregate(
                total=Sum("reorder_level")
            )["total"] or 0

            # Select warehouse with highest stock
            main_batch = batches.order_by(
                "-stock_quantity"
            ).first()

            # Get latest order summary
            order_summary = OrderSummary.objects.filter(
                product=selected_product
            ).order_by("-recorded_at").first()

            order_count = (
                order_summary.order_count if order_summary else 0
            )

            return_count = (
                order_summary.return_count if order_summary else 0
            )

            # Prepare ANN input
            features = {
                "stock_quantity": stock_quantity,
                "reorder_level": reorder_level,
                "order_count": order_count,
                "return_count": return_count,
                "selling_price": float(selected_product.selling_price),
                "category": selected_product.category.name,
                "brand": selected_product.brand,
                "warehouse": main_batch.warehouse.name,
                "supplier_code": selected_product.supplier.supplier_code
            }

            try:
                from ann_prediction.predict import predict_demand

                result = predict_demand(features)

            except Exception as exc:
                error = (
                    "Prediction failed. Check whether the ANN model "
                    "and preprocessing files have been trained and saved. "
                    f"Details: {exc}"
                )

    context = {
        "products": products,
        "result": result,
        "selected_product": selected_product,
        "error": error
    }

    return render(
        request,
        "ann_prediction/demand_analysis.html",
        context
    )
