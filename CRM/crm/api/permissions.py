from django.conf import settings
from rest_framework.permissions import BasePermission, DjangoModelPermissions


class StrictDjangoModelPermissions(DjangoModelPermissions):
    """
    Enforce Django model permissions for read operations as well.
    """

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    def has_permission(self, request, view):
        # Progressive rollout: keep legacy auth-only behaviour until strict mode is enabled.
        if not getattr(settings, "API_SECURITY_STRICT_MODE", False):
            user = getattr(request, "user", None)
            return bool(user and user.is_authenticated)
        return super().has_permission(request, view)


class DashboardOrReportingPermission(BasePermission):
    message = "Accès réservé aux profils dashboard/reporting."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return user.has_perm("crm.view_dashboard") or user.has_perm("crm.view_reports")


class ObservabilityPermission(BasePermission):
    message = "Accès observabilité réservé aux profils gouvernance/reporting."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return user.is_superuser or user.has_perm("crm.view_reports") or user.has_perm("crm.manage_sales_team")
