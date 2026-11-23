
import os
import pickle
import pandas as pd
from django.conf import settings
from django.db import models
from inventory.models import OrderSummary
from .models import DemandPredictionHistory

MODEL_PATH = os.path.join(settings.BASE_DIR, "machine_learning", "saved_models", "demand_model.pkl")

def predict_batch_demand(batch):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Trained demand prediction model not found. Train the model first.")

    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    order_count = OrderSummary.objects.filter(product=batch.product).aggregate(total=models.Sum("order_count"))["total"] or 0
    return_count = OrderSummary.objects.filter(product=batch.product).aggregate(total=models.Sum("return_count"))["total"] or 0

    input_data = pd.DataFrame([{
        "stock_quantity": batch.stock_quantity,
        "reorder_level": batch.reorder_level,
        "order_count": order_count,
        "return_count": return_count,
        "selling_price": float(batch.product.selling_price),
        "category": batch.product.category.name if batch.product.category else "Unknown",
        "brand": batch.product.brand or "Unknown",
        "warehouse": batch.warehouse.name if batch.warehouse else "Unknown",
        "supplier_code": batch.product.supplier.supplier_code if batch.product.supplier else "Unknown"
    }])

    predicted_label = model.predict(input_data)[0]

    if batch.stock_quantity <= batch.reorder_level:
        reorder_risk = "HIGH"
    elif predicted_label == "High":
        reorder_risk = "MEDIUM"
    else:
        reorder_risk = "LOW"

    prediction = DemandPredictionHistory.objects.create(product=batch.product, inventory_batch=batch, predicted_demand=predicted_label, reorder_risk=reorder_risk)

    return prediction
