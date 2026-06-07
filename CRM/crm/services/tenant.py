from __future__ import annotations

from django.conf import settings
from django.templatetags.static import static


DEFAULT_TENANT_SLUG = "maridav-ci"
DEFAULT_TENANT_LEGAL_NAME = "Maridav CI"
DEFAULT_TENANT_TAGLINE = "Performance & Excellence operationnelle"
DEFAULT_TENANT_LOGO = "img/logo_maridav_ci.png"


def _coalesce(value: object, fallback: str) -> str:
    candidate = str(value or "").strip()
    return candidate or fallback


def _resolve_logo_url(logo_path: str) -> str:
    if logo_path.startswith(("http://", "https://", "/")):
        return logo_path
    return static(logo_path)


def resolve_tenant_branding() -> dict[str, str]:
    tenant_slug = _coalesce(getattr(settings, "CRM_TENANT_SLUG", DEFAULT_TENANT_SLUG), DEFAULT_TENANT_SLUG)
    legal_name = _coalesce(
        getattr(settings, "CRM_TENANT_LEGAL_NAME", DEFAULT_TENANT_LEGAL_NAME),
        DEFAULT_TENANT_LEGAL_NAME,
    )
    display_name = _coalesce(getattr(settings, "CRM_TENANT_DISPLAY_NAME", legal_name), legal_name)
    crm_name = _coalesce(getattr(settings, "CRM_PLATFORM_NAME", f"CRM {display_name}"), f"CRM {display_name}")
    tagline = _coalesce(getattr(settings, "CRM_PLATFORM_TAGLINE", DEFAULT_TENANT_TAGLINE), DEFAULT_TENANT_TAGLINE)
    sidebar_subtitle = _coalesce(getattr(settings, "CRM_BRAND_SIDEBAR_SUBTITLE", crm_name.upper()), crm_name.upper())
    logo_path = _coalesce(getattr(settings, "CRM_BRAND_LOGO", DEFAULT_TENANT_LOGO), DEFAULT_TENANT_LOGO)
    logo_alt = _coalesce(getattr(settings, "CRM_BRAND_LOGO_ALT", display_name), display_name)

    return {
        "tenant_slug": tenant_slug,
        "legal_name": legal_name,
        "display_name": display_name,
        "crm_name": crm_name,
        "tagline": tagline,
        "sidebar_subtitle": sidebar_subtitle,
        "logo_path": logo_path,
        "logo_url": _resolve_logo_url(logo_path),
        "logo_alt": logo_alt,
    }
