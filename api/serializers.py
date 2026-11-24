from rest_framework import serializers

from inventory.models import (Product,Supplier,Complaint,)
from machine_learning.models import DemandPredictionHistory


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Product._meta.get_field("category").remote_field.model.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "product_name",
            "category",
            "supplier",
            "brand",
            "purchase_price",
            "selling_price",
            "is_discontinued",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            "id",
            "product",
            "complaint_text",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]


class DemandPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandPredictionHistory
        fields = "__all__"
        read_only_fields = ["id", "predicted_at"]


class InventoryUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.lower().endswith(".csv"):
            raise serializers.ValidationError("Only CSV files are allowed.")
        return value


class TaskStatusSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    status = serializers.CharField()
    progress = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)
    result = serializers.JSONField(required=False)
    error = serializers.CharField(required=False)


class DashboardSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    total_suppliers = serializers.IntegerField()
    total_stock = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    open_complaints = serializers.IntegerField()
    total_predictions = serializers.IntegerField()
