from rest_framework.permissions import BasePermission


class IsStaffOrAdmin(BasePermission):
    """Allow access only to admin or staff users."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("admin", "staff")
        )


class IsOwnerOrStaffOrAdmin(BasePermission):
    """
    Allow staff/admin to view/edit anything.
    Allow customers to view their own records only.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role in ("admin", "staff"):
            return True
        customer_user = getattr(obj, "customer", None)
        return customer_user == request.user
