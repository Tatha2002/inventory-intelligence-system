
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class PortalRegistrationForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=[(User.Role.STORE_MANAGER, 'Store Manager'), (User.Role.INVENTORY_STAFF, 'Inventory Staff')])

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email already registered")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Phone number already registered")
        return phone

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise ValidationError("Password must contain at least 8 characters")
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")
        return cleaned_data


class PortalOTPVerificationForm(forms.Form):
    email = forms.EmailField()
    otp = forms.CharField(max_length=6, min_length=6)


class PortalLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(self.request, username=email.strip().lower(), password=password)
            if user is None:
                raise ValidationError("Invalid email or password")
            if not user.is_email_verified:
                raise ValidationError("Please verify your email first")
            if not user.is_active:
                raise ValidationError("Your account is inactive")
            cleaned_data['user'] = user
        return cleaned_data
