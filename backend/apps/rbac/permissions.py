from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import RolePermission

class NotExclusion(permissions.BasePermission):
    message = "Доступ ограничен. Обратитесь в отдел HR для уточнения статуса учетной записи."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'exclusion':
            # Exclusion can only access support tickets and exclusion info
            if view.__class__.__name__ in ('SupportTicketViewSet', 'ExclusionInfoView', 'UserMeView'):
                return True
            raise PermissionDenied(detail=self.message)
        return True

class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser))

class IsHRorAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ('admin', 'hr') or request.user.is_superuser)

class HasRolePermission(permissions.BasePermission):
    def __init__(self, permission_key: str):
        self.permission_key = permission_key

    def __call__(self):
        return self

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
        rule = RolePermission.objects.filter(role=request.user.role, permission_key=self.permission_key).first()
        if rule:
            return rule.is_allowed
        # Default policy: HR has broad access, regular employee has portal access
        if request.user.role == 'hr' and not self.permission_key.startswith('settings.platform'):
            return True
        return False
