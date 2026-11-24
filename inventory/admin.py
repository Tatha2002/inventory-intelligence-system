

from django.contrib import admin
from .models import (
    Category,
    Supplier,
    Warehouse,
    Product,
    InventoryBatch,
    OrderSummary,
    ReturnRecord,
    Complaint,
    ProductImage,
    DemandPrediction,
    QualityReview,
    StockAdjustment,
)


admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Warehouse)
admin.site.register(Product)
admin.site.register(InventoryBatch)
admin.site.register(OrderSummary)
admin.site.register(ReturnRecord)
admin.site.register(Complaint)
admin.site.register(ProductImage)
admin.site.register(DemandPrediction)
admin.site.register(QualityReview)
admin.site.register(StockAdjustment)
