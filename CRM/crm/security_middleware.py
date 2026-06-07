from __future__ import annotations

import json
import logging
import time
import uuid

from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect

from crm.models import UserSecurityProfile
from crm.services.observability import record_api_request_sample


api_access_logger = logging.getLogger("crm.api.access")


class RequestIDMiddleware:
    """Injecte un identifiant de requête traçable sur chaque appel."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.request_id = request_id
        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response


class AccountLockMiddleware:
    """Bloque l'accès des comptes marqués verrouillés dans le profil sécurité."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            profile, _ = UserSecurityProfile.objects.get_or_create(user=user)
            if profile.is_locked and not request.path.startswith("/admin/login"):
                logout(request)
                if request.path.startswith("/api/"):
                    return JsonResponse(
                        {"detail": "Compte verrouillé. Contactez l'administrateur."},
                        status=403,
                    )
                return redirect("login")
        return self.get_response(request)


class ApiAccessLogMiddleware:
    """Journalise les accès API avec contexte sécurité exploitable."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        started = time.perf_counter()
        response = None
        try:
            response = self.get_response(request)
            return response
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
            ip_address = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
            user = getattr(request, "user", None)
            username = user.get_username() if user is not None and user.is_authenticated else "anonymous"
            payload = {
                "request_id": getattr(request, "request_id", ""),
                "method": request.method,
                "path": request.path,
                "status_code": getattr(response, "status_code", 500),
                "duration_ms": duration_ms,
                "user": username,
                "ip": ip_address or "",
            }
            api_access_logger.info(json.dumps(payload, ensure_ascii=False))
            record_api_request_sample(
                status_code=int(payload["status_code"]),
                duration_ms=duration_ms,
            )
