
from celery import shared_task
from inventory.models import InventoryBatch
from .predict import predict_batch_demand


@shared_task(bind=True)
def generate_demand_prediction_task(self, batch_id):

    self.update_state(
        state="PROGRESS",
        meta={
            "progress": 20,
            "message": "Fetching inventory batch..."
        }
    )

    batch = InventoryBatch.objects.select_related(
        "product",
        "warehouse",
        "product__category",
        "product__supplier"
    ).get(id=batch_id)

    self.update_state(
        state="PROGRESS",
        meta={
            "progress": 50,
            "message": "Running demand prediction model..."
        }
    )

    prediction = predict_batch_demand(batch)

    self.update_state(
        state="PROGRESS",
        meta={
            "progress": 90,
            "message": "Saving prediction results..."
        }
    )

    return {
        "success": True,
        "prediction_id": prediction.id,
        "product": str(prediction.product.product_name),
        "predicted_demand": str(prediction.predicted_demand),
        "reorder_risk": str(prediction.reorder_risk),
        "message": "Demand prediction completed successfully."
    }
