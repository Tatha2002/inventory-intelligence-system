
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    supplier_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.supplier_code} - {self.name}"


class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=20, unique=True)
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="products")
    brand = models.CharField(max_length=100)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    is_discontinued = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def profit_margin(self):
        if self.selling_price:
            return self.selling_price - self.purchase_price
        return Decimal("0.00")

    def __str__(self):
        return f"{self.sku} - {self.product_name}"


class InventoryBatch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory_batches")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="inventory_batches")
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["product", "warehouse"], name="unique_product_warehouse")]

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

    @property
    def stock_value(self):
        return self.stock_quantity * self.product.purchase_price

    def __str__(self):
        return f"{self.product.sku} - {self.warehouse.name}"


class OrderSummary(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_summaries")
    order_count = models.PositiveIntegerField(default=0)
    return_count = models.PositiveIntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.sku} - Orders: {self.order_count}"


class ReturnRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="returns")
    quantity = models.PositiveIntegerField(default=1)
    reason = models.CharField(max_length=255)
    returned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return - {self.product.sku}"


class Complaint(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        RESOLVED = "RESOLVED", "Resolved"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="complaints")
    complaint_text = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint - {self.product.sku}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image - {self.product.sku}"


class DemandPrediction(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="demand_predictions")
    historical_demand_label = models.CharField(max_length=20, choices=RiskLevel.choices)
    predicted_demand = models.PositiveIntegerField(default=0)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.MEDIUM)
    predicted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.sku} - {self.risk_level} risk"


class QualityReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="quality_reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.sku} - {self.rating}/5"



class StockAdjustment(models.Model):
    class AdjustmentType(models.TextChoices):
        INCREASE = "INCREASE", "Increase"
        DECREASE = "DECREASE", "Decrease"

    batch = models.ForeignKey(InventoryBatch, on_delete=models.PROTECT, related_name="adjustments")
    adjustment_type = models.CharField(max_length=10, choices=AdjustmentType.choices)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reason = models.CharField(max_length=255)
    adjusted_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.batch.product.sku} - {self.adjustment_type} - {self.quantity}"
