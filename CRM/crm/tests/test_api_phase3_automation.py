from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from crm.models import InboundRequest, RoleAssignment, RoleScopeChoices

User = get_user_model()


def grant_crm_perms(user, *codenames):
    perms = Permission.objects.filter(content_type__app_label="crm", codename__in=codenames)
    user.user_permissions.add(*perms)


class PublicIntakePhase3Tests(APITestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_public_inbound_creates_linked_inbound_and_lead(self):
        payload = {
            "kind": "lead",
            "name": "  Ferme Bouake  ",
            "email": " Prospect@Example.com ",
            "phone": " +225 07 01 02 03 04 ",
            "segment": " Volaille ",
            "intent": "support technique",
            "region": "Bouake",
            "message": "Bonjour, besoin d'accompagnement.",
            "consent": True,
        }
        response = self.client.post("/api/v1/public/inbound/", payload, format="json")
        self.assertEqual(response.status_code, 201)

        inbound = InboundRequest.objects.get(email="prospect@example.com")
        self.assertIsNotNone(inbound.lead_id)
        self.assertEqual(inbound.name, "Ferme Bouake")
        self.assertEqual(inbound.phone, "+2250701020304")
        self.assertEqual(inbound.segment, "volailles")
        self.assertEqual(inbound.lead.segment, "volailles")

    def test_public_inbound_duplicate_submission_is_blocked(self):
        payload = {
            "name": "Ferme Duplicate",
            "email": "dup@example.com",
            "phone": "+22500000001",
            "segment": "volailles",
        }
        first = self.client.post("/api/v1/public/inbound/", payload, format="json")
        second = self.client.post("/api/v1/public/inbound/", payload, format="json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)
        self.assertIn("Soumission trop frequente", str(second.data))


@override_settings(API_SECURITY_STRICT_MODE=True)
class AuthCookieFlowPhase3Tests(APITestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        self.password = "ValidPass!234"
        self.user = User.objects.create_user(username="cookie_user", password=self.password)

    def _get_csrf_token(self, client: APIClient) -> str:
        response = client.get("/api/v1/auth/csrf/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrfToken", response.data)
        return response.data["csrfToken"]

    def _login(self, client: APIClient, username: str, password: str, csrf_token: str):
        return client.post(
            "/api/v1/auth/login/",
            {"username": username, "password": password},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

    def test_login_refresh_logout_and_me_work_with_http_only_cookies(self):
        client = APIClient(enforce_csrf_checks=True)
        csrf_token = self._get_csrf_token(client)

        login = self._login(client, self.user.username, self.password, csrf_token)
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.data["detail"], "login_ok")
        self.assertIn(settings.AUTH_COOKIE_ACCESS, login.cookies)
        self.assertIn(settings.AUTH_COOKIE_REFRESH, login.cookies)

        me = client.get("/api/v1/auth/me/", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["username"], self.user.username)

        refresh = client.post("/api/v1/auth/refresh/", {}, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(refresh.status_code, 200)
        self.assertEqual(refresh.data["detail"], "refresh_ok")
        self.assertIn(settings.AUTH_COOKIE_ACCESS, refresh.cookies)

        logout = client.post("/api/v1/auth/logout/", {}, format="json", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(logout.data["detail"], "logout_ok")

        me_after_logout = client.get("/api/v1/auth/me/", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(me_after_logout.status_code, 401)

    def test_cookie_authenticated_write_requires_csrf_header(self):
        writer = User.objects.create_user(username="writer_user", password=self.password)
        grant_crm_perms(writer, "add_customer")

        client = APIClient(enforce_csrf_checks=True)
        csrf_token = self._get_csrf_token(client)
        login = self._login(client, writer.username, self.password, csrf_token)
        self.assertEqual(login.status_code, 200)

        blocked = client.post(
            "/api/v1/customers/",
            {"name": "Client CSRF", "code": "C-CSRF-1"},
            format="json",
            HTTP_X_CSRFTOKEN="invalid-token",
        )
        self.assertEqual(blocked.status_code, 403)
        self.assertIn("CSRF Failed", str(blocked.data))

        allowed = client.post(
            "/api/v1/customers/",
            {"name": "Client CSRF OK", "code": "C-CSRF-2"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(allowed.status_code, 201)


@override_settings(API_SECURITY_STRICT_MODE=True)
class EndToEndSmokePhase3Tests(APITestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        self.role_group = Group.objects.create(name="Commerciaux")
        self.user = User.objects.create_user(username="smoke_scope", password="StrongPass!234")
        grant_crm_perms(self.user, "view_dashboard")
        RoleAssignment.objects.create(
            user=self.user,
            group=self.role_group,
            scope=RoleScopeChoices.REGION,
            scope_reference="region=Bouake",
        )

    def test_public_intake_then_scoped_dashboard_read(self):
        public_client = APIClient()
        payloads = [
            {
                "name": "Ferme Bouake",
                "email": "bouake-smoke@example.com",
                "phone": "+22500000011",
                "region": "Bouake",
                "segment": "volailles",
            },
            {
                "name": "Ferme Abidjan",
                "email": "abidjan-smoke@example.com",
                "phone": "+22500000012",
                "region": "Abidjan",
                "segment": "volailles",
            },
        ]
        for payload in payloads:
            response = public_client.post("/api/v1/public/inbound/", payload, format="json")
            self.assertEqual(response.status_code, 201)

        self.client.force_authenticate(self.user)

        kpi = self.client.get("/api/v1/analytics/kpi/")
        self.assertEqual(kpi.status_code, 200)
        self.assertEqual(kpi.data["inbound"]["total"], 1)

        search = self.client.get("/api/v1/search/?q=Ferme")
        self.assertEqual(search.status_code, 200)
        lead_names = {item["name"] for item in search.data["leads"]}
        self.assertEqual(lead_names, {"Ferme Bouake"})
