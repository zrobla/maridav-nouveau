from django.conf import settings
from django.contrib.auth import logout
from django.middleware.csrf import get_token
from rest_framework import permissions, response, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth_login"

    def post(self, request, *args, **kwargs):
        response_obj = super().post(request, *args, **kwargs)
        if response_obj.status_code != 200:
            return response_obj
        access = response_obj.data.get("access")
        refresh = response_obj.data.get("refresh")
        response_obj.data = {"detail": "login_ok"}
        self._set_auth_cookies(response_obj, access, refresh)
        return response_obj

    def _set_auth_cookies(self, response_obj, access, refresh):
        cookie_domain = settings.AUTH_COOKIE_DOMAIN or None
        response_obj.set_cookie(
            settings.AUTH_COOKIE_ACCESS,
            access,
            httponly=True,
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            domain=cookie_domain,
            max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        )
        response_obj.set_cookie(
            settings.AUTH_COOKIE_REFRESH,
            refresh,
            httponly=True,
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            domain=cookie_domain,
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        )
        get_token(self.request)


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth_refresh"

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        data = request.data.copy()
        if refresh:
            data["refresh"] = refresh
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data.get("access")
        refresh_out = serializer.validated_data.get("refresh")
        response_obj = response.Response({"detail": "refresh_ok"})
        self._set_auth_cookies(response_obj, access, refresh_out)
        return response_obj

    def _set_auth_cookies(self, response_obj, access, refresh):
        cookie_domain = settings.AUTH_COOKIE_DOMAIN or None
        response_obj.set_cookie(
            settings.AUTH_COOKIE_ACCESS,
            access,
            httponly=True,
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            domain=cookie_domain,
            max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        )
        if refresh:
            response_obj.set_cookie(
                settings.AUTH_COOKIE_REFRESH,
                refresh,
                httponly=True,
                secure=settings.AUTH_COOKIE_SECURE,
                samesite=settings.AUTH_COOKIE_SAMESITE,
                domain=cookie_domain,
                max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            )
        get_token(self.request)


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth_refresh"

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except Exception:
                pass
        logout(request)
        response_obj = response.Response({"detail": "logout_ok"})
        cookie_domain = settings.AUTH_COOKIE_DOMAIN or None
        response_obj.delete_cookie(settings.AUTH_COOKIE_ACCESS, domain=cookie_domain)
        response_obj.delete_cookie(settings.AUTH_COOKIE_REFRESH, domain=cookie_domain)
        return response_obj
