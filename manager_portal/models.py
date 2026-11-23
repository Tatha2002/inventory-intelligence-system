
from django.db import models
from django.conf import settings
from inventory.models import Product


class ProductReturnRequest(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ASSIGNED = "ASSIGNED", "Assigned"
        PROCESSING = "PROCESSING", "Processing"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="return_requests"
    )

    quantity = models.PositiveIntegerField(default=1)

    reason = models.CharField(max_length=255)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_return_requests"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_return_requests",
        null=True,
        blank=True,
        limit_choices_to={"role": "INVENTORY_STAFF"}
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return Request #{self.id} - {self.product.sku}"
