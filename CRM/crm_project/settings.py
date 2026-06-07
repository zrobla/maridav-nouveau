"""Django settings for the Maridav CI CRM project."""

from pathlib import Path
import logging
import os
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-maridav-crm-secret-key-change-me",
)
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in {"true", "1", "yes"}
ALLOWED_HOSTS = [h for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h] or ["*"]
API_SECURITY_STRICT_MODE = os.getenv("API_SECURITY_STRICT_MODE", "False").lower() in {"true", "1", "yes"}
API_PUBLIC_THROTTLE_PROFILE = (os.getenv("API_PUBLIC_THROTTLE_PROFILE", "medium") or "medium").strip().lower()


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.sitemaps",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.typed_table_block",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail.api.v2",
    "modelcluster",
    "taggit",
    "website.apps.WebsiteConfig",
    "crm.apps.CrmConfig",
    "content",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "crm.security_middleware.RequestIDMiddleware",
    "crm_project.middleware.HostURLConfMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "crm.security_middleware.AccountLockMiddleware",
    "crm.middleware.RequestContextMiddleware",
    "crm.security_middleware.ApiAccessLogMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]


ROOT_URLCONF = "crm_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "crm.context_processors.current_user_security_profile",
                "crm.context_processors.crm_tenant_branding",
            ],
        },
    },
]

WSGI_APPLICATION = "crm_project.wsgi.application"
ASGI_APPLICATION = "crm_project.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

SITE_ID = 1


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


def _env_text(name: str, default: str) -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip()
    return value or default


CRM_TENANT_SLUG = _env_text("CRM_TENANT_SLUG", "maridav-ci")
CRM_TENANT_LEGAL_NAME = _env_text("CRM_TENANT_LEGAL_NAME", "Maridav CI")
CRM_TENANT_DISPLAY_NAME = _env_text("CRM_TENANT_DISPLAY_NAME", CRM_TENANT_LEGAL_NAME)
CRM_PLATFORM_NAME = _env_text("CRM_PLATFORM_NAME", f"CRM {CRM_TENANT_DISPLAY_NAME}")
CRM_PLATFORM_TAGLINE = _env_text(
    "CRM_PLATFORM_TAGLINE",
    "Performance & Excellence operationnelle",
)
CRM_BRAND_LOGO = _env_text("CRM_BRAND_LOGO", "img/logo_maridav_ci.png")
CRM_BRAND_LOGO_ALT = _env_text("CRM_BRAND_LOGO_ALT", CRM_TENANT_DISPLAY_NAME)
CRM_BRAND_SIDEBAR_SUBTITLE = _env_text("CRM_BRAND_SIDEBAR_SUBTITLE", CRM_PLATFORM_NAME.upper())

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
AUTHENTICATION_BACKENDS = [
    "crm.auth_backends.CRMModelBackend",
]

WAGTAIL_SITE_NAME = CRM_TENANT_DISPLAY_NAME
WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL", "http://localhost:8000")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("crm.authentication.CookieJWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
}

_PUBLIC_THROTTLE_PROFILES = {
    "loose": {
        "public_inbound": "120/min",
        "public_careers": "40/min",
        "public_newsletter": "120/min",
        "auth_login": "20/min",
        "auth_refresh": "60/min",
        "auth_csrf": "120/min",
    },
    "medium": {
        "public_inbound": "60/min",
        "public_careers": "20/min",
        "public_newsletter": "60/min",
        "auth_login": "10/min",
        "auth_refresh": "30/min",
        "auth_csrf": "60/min",
    },
    "strict": {
        "public_inbound": "30/min",
        "public_careers": "10/min",
        "public_newsletter": "30/min",
        "auth_login": "5/min",
        "auth_refresh": "15/min",
        "auth_csrf": "30/min",
    },
}

if API_PUBLIC_THROTTLE_PROFILE not in _PUBLIC_THROTTLE_PROFILES:
    API_PUBLIC_THROTTLE_PROFILE = "medium"

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "anon": os.getenv("DJANGO_API_ANON_RATE", "180/min"),
    "user": os.getenv("DJANGO_API_USER_RATE", "600/min"),
    **_PUBLIC_THROTTLE_PROFILES[API_PUBLIC_THROTTLE_PROFILE],
}

SPECTACULAR_SETTINGS = {
    "TITLE": f"{CRM_TENANT_DISPLAY_NAME} API",
    "DESCRIPTION": f"API CRM + CMS headless pour {CRM_TENANT_DISPLAY_NAME}.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

AUTH_COOKIE_ACCESS = os.getenv("AUTH_COOKIE_ACCESS", "maridav_access")
AUTH_COOKIE_REFRESH = os.getenv("AUTH_COOKIE_REFRESH", "maridav_refresh")
AUTH_COOKIE_SECURE = os.getenv(
    "DJANGO_COOKIE_SECURE",
    "True" if not DEBUG else "False",
).lower() in {"true", "1", "yes"}
SESSION_COOKIE_SAMESITE = os.getenv("DJANGO_SESSION_COOKIE_SAMESITE", "Lax")
AUTH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", SESSION_COOKIE_SAMESITE)
AUTH_COOKIE_DOMAIN = os.getenv("AUTH_COOKIE_DOMAIN", "")
SESSION_COOKIE_SECURE = AUTH_COOKIE_SECURE
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_NAME = os.getenv("CSRF_COOKIE_NAME", "maridav_csrf")
CSRF_COOKIE_SECURE = AUTH_COOKIE_SECURE
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = os.getenv("DJANGO_CSRF_COOKIE_SAMESITE", "Lax")
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://localhost:8000,https://maridav.ci,https://crm.maridav.ci",
    ).split(",")
    if origin.strip()
]

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "DJANGO_CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://localhost:8000,https://maridav.ci,https://crm.maridav.ci",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv(
    "DJANGO_SECURE_SSL_REDIRECT",
    "True" if not DEBUG else "False",
).lower() in {"true", "1", "yes"}
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True

SITE_PUBLIC_HOSTS = [
    host.strip().lower()
    for host in os.getenv("DJANGO_SITE_PUBLIC_HOSTS", "maridav.ci,www.maridav.ci").split(",")
    if host.strip()
]
SITE_CRM_HOSTS = [
    host.strip().lower()
    for host in os.getenv("DJANGO_SITE_CRM_HOSTS", "crm.maridav.ci").split(",")
    if host.strip()
]

WEBSITE_TEMPLATE = (os.getenv("DJANGO_WEBSITE_TEMPLATE", "template_01") or "template_01").strip()
MAX_LOGIN_FAILURES = int(os.getenv("DJANGO_MAX_LOGIN_FAILURES", "5"))

OBS_METRICS_WINDOW_MINUTES = int(os.getenv("OBS_METRICS_WINDOW_MINUTES", "5"))
OBS_METRICS_CACHE_TTL_SECONDS = int(os.getenv("OBS_METRICS_CACHE_TTL_SECONDS", "1800"))
OBS_ALERT_MIN_REQUESTS = int(os.getenv("OBS_ALERT_MIN_REQUESTS", "20"))
OBS_ALERT_4XX_RATE_PCT = _env_float("OBS_ALERT_4XX_RATE_PCT", 30.0)
OBS_ALERT_5XX_RATE_PCT = _env_float("OBS_ALERT_5XX_RATE_PCT", 5.0)
OBS_ALERT_P95_MS = _env_float("OBS_ALERT_P95_MS", 1200.0)
OBS_ALERT_SLA_OPEN = int(os.getenv("OBS_ALERT_SLA_OPEN", "15"))
OBS_ALERT_SLA_L3_OPEN = int(os.getenv("OBS_ALERT_SLA_L3_OPEN", "0"))
OBS_ALERT_SLA_OLDEST_OVERDUE_MINUTES = int(os.getenv("OBS_ALERT_SLA_OLDEST_OVERDUE_MINUTES", "120"))

SENTRY_DSN = os.getenv("SENTRY_DSN", "").strip()
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "development" if DEBUG else "production")
SENTRY_RELEASE = os.getenv("SENTRY_RELEASE", "").strip()
SENTRY_TRACES_SAMPLE_RATE = _env_float("SENTRY_TRACES_SAMPLE_RATE", 0.0)
SENTRY_PROFILES_SAMPLE_RATE = _env_float("SENTRY_PROFILES_SAMPLE_RATE", 0.0)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "crm.api.access": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_API_ACCESS_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "crm.observability": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_OBSERVABILITY_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "crm.observability.alerts": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_OBSERVABILITY_ALERT_LOG_LEVEL", "WARNING"),
            "propagate": False,
        },
        "crm.integrations": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_ENTERPRISE_CONNECTORS_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
            environment=SENTRY_ENVIRONMENT,
            release=SENTRY_RELEASE or None,
            send_default_pii=False,
        )
        logging.getLogger("crm.observability").info("Sentry SDK initialized.")
    except Exception as exc:  # pragma: no cover - optional dependency path
        logging.getLogger("crm.observability").warning(
            "Sentry SDK not initialized (%s).", exc
        )
