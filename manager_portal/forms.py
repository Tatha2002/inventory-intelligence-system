
from django import forms
from accounts.models import User
from inventory.models import Product
from manager_portal.models import ProductReturnRequest


class ProductReturnRequestForm(forms.ModelForm):

    class Meta:
        model = ProductReturnRequest
        fields = [
            "product",
            "quantity",
            "reason",
            "assigned_to"
        ]

        widgets = {
            "product": forms.Select(attrs={
                "class": "form-control"
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "reason": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter return reason"
            }),
            "assigned_to": forms.Select(attrs={
                "class": "form-control"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = Product.objects.filter(
            is_discontinued=False
        )

        self.fields["assigned_to"].queryset = User.objects.filter(
            role=User.Role.INVENTORY_STAFF,
            is_active=True
        )

        self.fields["assigned_to"].required = True

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity < 1:
            raise forms.ValidationError(
                "Quantity must be at least 1."
            )

        return quantity
