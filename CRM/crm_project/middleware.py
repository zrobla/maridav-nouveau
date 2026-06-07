from django.conf import settings


class HostURLConfMiddleware:
    """Switch URL configuration by requested hostname.

    - public site hosts -> ``crm_project.urls_site``
    - crm hosts         -> ``crm_project.urls_crm``
    - others            -> default ROOT_URLCONF (local mixed)
    """

    public_urlconf = "crm_project.urls_site"
    crm_urlconf = "crm_project.urls_crm"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = self._extract_host(request)
        public_hosts = {h.lower() for h in getattr(settings, "SITE_PUBLIC_HOSTS", [])}
        crm_hosts = {h.lower() for h in getattr(settings, "SITE_CRM_HOSTS", [])}

        if host and host in crm_hosts:
            request.urlconf = self.crm_urlconf
        elif host and host in public_hosts:
            request.urlconf = self.public_urlconf

        return self.get_response(request)

    @staticmethod
    def _extract_host(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_HOST")
        raw_host = forwarded or request.META.get("HTTP_HOST", "")
        if not raw_host:
            return ""
        host = raw_host.split(",", 1)[0].strip().lower()
        return host.split(":", 1)[0]
