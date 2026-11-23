
import os
import tempfile
import pandas as pd

from django.db import transaction

from inventory.models import (
    Category, Supplier, Product, Warehouse,
    InventoryBatch, OrderSummary, Complaint, DemandPrediction
)

from core_python.file_handler import read_inventory_file
from core_python.validators import validate_inventory_row
from core_python.exceptions import InvalidInventoryRow


def import_inventory_csv(uploaded_file):
    valid_count = 0
    invalid_records = []
    updated_count = 0

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        temp_path = temp_file.name

    try:
        data = read_inventory_file(temp_path)

        for index, row in enumerate(data.to_dict(orient="records"), start=2):
            try:
                # Convert pandas empty values into empty strings
                row = {key: "" if pd.isna(value) else value for key, value in row.items()}

                validate_inventory_row(row)

                if not row["product_name"] or not row["category"] or not row["brand"] or not row["warehouse"]:
                    raise ValueError("Product name, category, brand and warehouse are required.")

                if row["selling_price"] < row["purchase_price"]:
                    raise ValueError("Selling price cannot be less than purchase price.")

                with transaction.atomic():
                    category, _ = Category.objects.get_or_create(name=row["category"].strip())

                    supplier, _ = Supplier.objects.get_or_create(
                        supplier_code=row["supplier_code"].strip().upper(),
                        defaults={"name": row["supplier_code"].strip().upper()}
                    )

                    warehouse, _ = Warehouse.objects.get_or_create(
                        name=row["warehouse"].strip(),
                        defaults={"location": row["warehouse"].strip()}
                    )

                    product, created = Product.objects.update_or_create(
                        sku=row["sku"].strip().upper(),
                        defaults={
                            "product_name": row["product_name"].strip(),
                            "category": category,
                            "supplier": supplier,
                            "brand": row["brand"].strip(),
                            "purchase_price": row["purchase_price"],
                            "selling_price": row["selling_price"],
                        }
                    )

                    InventoryBatch.objects.update_or_create(
                        product=product,
                        warehouse=warehouse,
                        defaults={
                            "stock_quantity": row["stock_quantity"],
                            "reorder_level": row["reorder_level"],
                        }
                    )

                    order_summary = OrderSummary.objects.filter(product=product).order_by("-recorded_at").first()

                    if order_summary:
                        order_summary.order_count = row["order_count"]
                        order_summary.return_count = row["return_count"]
                        order_summary.save(update_fields=["order_count", "return_count"])
                    else:
                        OrderSummary.objects.create(
                            product=product,
                            order_count=row["order_count"],
                            return_count=row["return_count"]
                        )

                    if row["complaint_text"]:
                        Complaint.objects.get_or_create(
                            product=product,
                            complaint_text=row["complaint_text"].strip()
                        )

                    demand = DemandPrediction.objects.filter(product=product).order_by("-predicted_at").first()

                    if demand:
                        demand.historical_demand_label = row["historical_demand_label"].strip().upper()
                        demand.risk_level = row["historical_demand_label"].strip().upper()
                        demand.save(update_fields=["historical_demand_label", "risk_level"])
                    else:
                        DemandPrediction.objects.create(
                            product=product,
                            historical_demand_label=row["historical_demand_label"].strip().upper(),
                            risk_level=row["historical_demand_label"].strip().upper()
                        )

                    valid_count += 1
                    if not created:
                        updated_count += 1

            except (InvalidInventoryRow, ValueError, TypeError) as error:
                invalid_records.append({
                    "row": index,
                    "sku": str(row.get("sku", "")),
                    "error": str(error)
                })

        return {
            "total": len(data),
            "valid": valid_count,
            "updated": updated_count,
            "invalid": len(invalid_records),
            "errors": invalid_records
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
