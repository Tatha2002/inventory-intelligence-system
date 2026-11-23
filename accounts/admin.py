
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm as DjangoUserChangeForm
from .models import User, EmailOTP, RefreshToken


class CustomUserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'phone', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [(User.Role.STORE_MANAGER, 'Store Manager'), (User.Role.INVENTORY_STAFF, 'Inventory Staff')]


class CustomUserChangeForm(DjangoUserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    ordering = ('email',)

    list_display = ('email', 'name', 'phone', 'employee_code', 'role', 'is_email_verified', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_email_verified')
    search_fields = ('email', 'name', 'phone', 'employee_code')

    fieldsets = (
        ('Personal Information', {'fields': ('email', 'name', 'phone', 'employee_code')}),
        ('Role Information', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        ('Create User', {'classes': ('wide',), 'fields': ('email', 'name', 'phone', 'role', 'password1', 'password2')}),
    )

    readonly_fields = ('employee_code', 'last_login', 'date_joined')


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'expires_at', 'is_used', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('user', 'otp_hash', 'expires_at', 'is_used', 'created_at')


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'jti', 'expires_at', 'revoked_at', 'created_at')
    search_fields = ('user__email', 'jti')
    readonly_fields = ('user', 'jti', 'expires_at', 'revoked_at', 'created_at')
