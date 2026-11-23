
from rest_framework.permissions import BasePermission


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and (
                user.is_superuser
                or user.role == "ADMIN"
                or user.role == "STORE_MANAGER"
            )
        )


class IsManagerOrStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and (
                user.is_superuser
                or user.role in [
                    "ADMIN",
                    "STORE_MANAGER",
                    "INVENTORY_STAFF",
                ]
            )
        )
