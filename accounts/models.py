
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")

        email = self.normalize_email(email)

        if extra_fields.get("role") == "ADMIN" and not extra_fields.get("is_superuser", False):
            raise ValueError("ADMIN accounts can only be created as superusers.")

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)
        extra_fields.setdefault("role", "ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        extra_fields["role"] = "ADMIN"
        return self.create_user(email, password, **extra_fields)


# Custom User Model
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STORE_MANAGER = "STORE_MANAGER", "Store Manager"
        INVENTORY_STAFF = "INVENTORY_STAFF", "Inventory Staff"

    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, unique=True)
    employee_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STORE_MANAGER)
    is_email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.role in [self.Role.STORE_MANAGER, self.Role.INVENTORY_STAFF] and not self.employee_code:
            self.employee_code = f"EMP{self.pk:05d}"
            super().save(update_fields=["employee_code"], using=kwargs.get("using"))

    def __str__(self):
        return f"{self.name} ({self.role})"


# Email OTP Model
class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_otps")
    otp_hash = models.CharField(max_length=256)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_otp(self, otp):
        self.otp_hash = make_password(otp)

    def verify_otp(self, otp):
        return not self.is_used and self.expires_at > timezone.now() and check_password(otp, self.otp_hash)

    def __str__(self):
        return f"OTP for {self.user.email}"


# Refresh Token Model
class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refresh_tokens")
    jti = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_valid(self):
        return self.revoked_at is None and self.expires_at > timezone.now()

    def __str__(self):
        return f"Refresh token for {self.user.email}"
