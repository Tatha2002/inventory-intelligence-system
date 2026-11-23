
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import User, EmailOTP


# REGISTRATION SERIALIZER
class RegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[(User.Role.STORE_MANAGER, 'Store Manager'), (User.Role.INVENTORY_STAFF, 'Inventory Staff')])

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered.")
        return value

    def validate_password(self, value):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError

        try:
            validate_password(value)
        except ValidationError as error:
            raise serializers.ValidationError(error.messages)

        return value

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(email=validated_data['email'], password=validated_data['password'], name=validated_data['name'], phone=validated_data['phone'], role=validated_data['role'], is_active=False, is_email_verified=False)

            otp = str(secrets.randbelow(900000) + 100000)
            otp_obj = EmailOTP(user=user, expires_at=timezone.now() + timedelta(minutes=5))
            otp_obj.set_otp(otp)
            otp_obj.save()

            send_mail(subject="Inventory Portal Email Verification OTP", message=f"Hello {user.name},\n\nYour verification OTP is {otp}.\nIt expires in 5 minutes.", from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email], fail_silently=False)

        return user


# EMAIL VERIFICATION SERIALIZER
class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        email = attrs['email'].strip().lower()
        user = User.objects.filter(email__iexact=email).first()

        if not user:
            raise serializers.ValidationError({"email": "User not found."})

        if user.is_email_verified:
            raise serializers.ValidationError({"email": "Email is already verified."})

        otp_obj = EmailOTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()

        if not otp_obj:
            raise serializers.ValidationError({"otp": "OTP not found. Please request a new OTP."})

        if not otp_obj.verify_otp(attrs['otp'].strip()):
            raise serializers.ValidationError({"otp": "Invalid or expired OTP."})

        attrs['user'] = user
        attrs['otp_obj'] = otp_obj
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=validated_data['user'].pk)
            otp_obj = EmailOTP.objects.select_for_update().get(pk=validated_data['otp_obj'].pk)

            if user.is_email_verified or not otp_obj.verify_otp(validated_data['otp'].strip()):
                raise serializers.ValidationError("OTP is invalid, expired or already used.")

            otp_obj.is_used = True
            otp_obj.save(update_fields=['is_used'])
            EmailOTP.objects.filter(user=user, is_used=False).update(is_used=True)

            user.is_email_verified = True
            user.is_active = True
            user.save(update_fields=['is_email_verified', 'is_active'])

        return user


# LOGIN SERIALIZER
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs['email'].strip().lower()
        user = User.objects.filter(email__iexact=email).first()

        if not user or not user.check_password(attrs['password']):
            raise serializers.ValidationError("Invalid email or password.")

        if user.role not in [User.Role.STORE_MANAGER, User.Role.INVENTORY_STAFF]:
            raise serializers.ValidationError("This account cannot use the inventory API login.")

        if not user.is_email_verified:
            raise serializers.ValidationError("Please verify your email first.")

        if not user.is_active:
            raise serializers.ValidationError("Your account is inactive.")

        attrs['user'] = user
        return attrs
