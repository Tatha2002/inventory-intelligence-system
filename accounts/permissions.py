
from rest_framework.permissions import BasePermission


class IsStoreManager(BasePermission):
    message = "Only Store Managers can access this resource."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "STORE_MANAGER"


class IsInventoryStaff(BasePermission):
    message = "Only Inventory Staff can access this resource."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "INVENTORY_STAFF"


class IsStoreManagerOrInventoryStaff(BasePermission):
    message = "Only Store Managers or Inventory Staff can access this resource."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["STORE_MANAGER", "INVENTORY_STAFF"]


class IsSuperAdmin(BasePermission):
    message = "Only Admin users can access this resource."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser
