
from django import forms
from inventory.models import InventoryBatch, StockAdjustment

class InventoryUploadForm(forms.Form):
    file = forms.FileField(label="Select Inventory CSV")

    def clean_file(self):
        file = self.cleaned_data["file"]

        if not file.name.lower().endswith(".csv"):
            raise forms.ValidationError("Only CSV files are supported.")

        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File size must be below 5 MB.")

        return file

from inventory.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["sku", "product_name", "category", "supplier", "brand", "purchase_price", "selling_price"]





class StockAdjustmentForm(forms.Form):
    batch = forms.ModelChoiceField(queryset=InventoryBatch.objects.select_related("product", "warehouse").all(), label="Select Product / Warehouse")
    adjustment_type = forms.ChoiceField(choices=StockAdjustment.AdjustmentType.choices, widget=forms.Select(attrs={"class": "form-select"}))
    quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={"class": "form-control"}))
    reason = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter adjustment reason"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"

