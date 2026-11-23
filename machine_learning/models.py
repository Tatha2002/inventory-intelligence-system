
from django.db import models
from inventory.models import Product, InventoryBatch

class DemandPredictionHistory(models.Model):
    class DemandLabel(models.TextChoices):
        HIGH = "High", "High"
        MEDIUM = "Medium", "Medium"
        LOW = "Low", "Low"

    class RiskLevel(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ml_predictions")
    inventory_batch = models.ForeignKey(InventoryBatch, on_delete=models.CASCADE, related_name="ml_predictions")
    predicted_demand = models.CharField(max_length=20, choices=DemandLabel.choices)
    reorder_risk = models.CharField(max_length=20, choices=RiskLevel.choices)
    predicted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.sku} - {self.predicted_demand}"
