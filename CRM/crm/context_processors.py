from __future__ import annotations

from crm.models import UserSecurityProfile
from crm.services.tenant import resolve_tenant_branding


def current_user_security_profile(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {}
    profile, _ = UserSecurityProfile.objects.get_or_create(user=user)
    return {"current_user_security_profile": profile}


def crm_tenant_branding(request):
    return {"crm_branding": resolve_tenant_branding()}
