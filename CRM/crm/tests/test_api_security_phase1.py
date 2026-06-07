from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from crm.models import (
    Customer,
    InboundRequest,
    Invoice,
    InvoicePayment,
    InvoiceFNEStatusChoices,
    InvoiceStatusChoices,
    Lead,
    Opportunity,
    Order,
    RoleAssignment,
    RoleScopeChoices,
    UserSecurityProfile,
)

User = get_user_model()


@override_settings(API_SECURITY_STRICT_MODE=True)
class APISecurityPhase1Tests(APITestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        self.role_group = Group.objects.create(name="Commerciaux")

    def grant_crm_perms(self, user, *codenames):
        perms = Permission.objects.filter(content_type__app_label="crm", codename__in=codenames)
        user.user_permissions.add(*perms)

    def make_scoped_user(self, username: str, region: str = "Bouake"):
        user = User.objects.create_user(username=username, password="StrongPass!234", email=f"{username}@example.com")
        RoleAssignment.objects.create(
            user=user,
            group=self.role_group,
            scope=RoleScopeChoices.REGION,
            scope_reference=f"region={region}",
        )
        return user

    def test_scoped_user_sees_only_scoped_leads_inbound_opportunities(self):
        scoped_user = self.make_scoped_user("scoped_sales")
        self.grant_crm_perms(scoped_user, "view_lead", "view_inboundrequest", "view_opportunity")

        customer_scoped = Customer.objects.create(name="Client Bouake", code="C-SCOPE", region="Bouake")
        customer_other = Customer.objects.create(name="Client Abidjan", code="C-OTHER", region="Abidjan")

        lead_scoped = Lead.objects.create(name="Lead Bouake", region="Bouake")
        Lead.objects.create(name="Lead Abidjan", region="Abidjan")

        inbound_scoped = InboundRequest.objects.create(kind="lead", name="Inbound Bouake", region="Bouake")
        InboundRequest.objects.create(kind="lead", name="Inbound Abidjan", region="Abidjan")

        opportunity_scoped = Opportunity.objects.create(title="Opp Bouake", customer=customer_scoped)
        Opportunity.objects.create(title="Opp Abidjan", customer=customer_other)

        self.client.force_authenticate(scoped_user)

        leads_response = self.client.get("/api/v1/leads/")
        self.assertEqual(leads_response.status_code, 200)
        self.assertEqual({item["id"] for item in leads_response.data}, {lead_scoped.id})

        inbound_response = self.client.get("/api/v1/inbound/")
        self.assertEqual(inbound_response.status_code, 200)
        self.assertEqual({item["id"] for item in inbound_response.data}, {inbound_scoped.id})

        opportunities_response = self.client.get("/api/v1/opportunities/")
        self.assertEqual(opportunities_response.status_code, 200)
        self.assertEqual({item["id"] for item in opportunities_response.data}, {opportunity_scoped.id})

    def test_user_without_view_order_permission_cannot_read_orders(self):
        user = User.objects.create_user(username="no_order_perm", password="StrongPass!234")
        self.client.force_authenticate(user)
        response = self.client.get("/api/v1/orders/")
        self.assertEqual(response.status_code, 403)

    def test_post_order_outside_scope_is_blocked(self):
        scoped_user = self.make_scoped_user("order_scope")
        self.grant_crm_perms(scoped_user, "view_order", "add_order")
        customer_scoped = Customer.objects.create(name="Client In Scope", code="C-IN", region="Bouake")
        customer_out = Customer.objects.create(name="Client Out Scope", code="C-OUT", region="Abidjan")

        self.client.force_authenticate(scoped_user)

        forbidden = self.client.post("/api/v1/orders/", {"customer": customer_out.id}, format="json")
        self.assertEqual(forbidden.status_code, 403)

        allowed = self.client.post("/api/v1/orders/", {"customer": customer_scoped.id}, format="json")
        self.assertEqual(allowed.status_code, 201)

    def test_order_delivery_is_blocked_until_fne_certification(self):
        scoped_user = self.make_scoped_user("order_gate")
        self.grant_crm_perms(scoped_user, "view_order", "add_order", "change_order")
        customer = Customer.objects.create(name="Client Gate", code="C-GATE", region="Bouake")
        order = Order.objects.create(customer=customer, status="confirme")
        invoice = Invoice.objects.create(
            customer=customer,
            order=order,
            status=InvoiceStatusChoices.EMISE,
            fne_required=True,
            fne_status=InvoiceFNEStatusChoices.PENDING,
            total_amount=100000,
        )

        self.client.force_authenticate(scoped_user)
        blocked = self.client.patch(f"/api/v1/orders/{order.id}/", {"status": "livre"}, format="json")
        self.assertEqual(blocked.status_code, 400)
        self.assertIn("certifi", str(blocked.data).lower())

        invoice.fne_status = InvoiceFNEStatusChoices.CERTIFIED
        invoice.save(update_fields=["fne_status", "updated_at"])

        allowed = self.client.patch(f"/api/v1/orders/{order.id}/", {"status": "livre"}, format="json")
        self.assertEqual(allowed.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, "livre")

    def test_post_invoice_payment_outside_scope_is_blocked(self):
        scoped_user = self.make_scoped_user("payment_scope")
        self.grant_crm_perms(
            scoped_user,
            "view_invoice",
            "view_invoicepayment",
            "add_invoicepayment",
        )
        customer_scoped = Customer.objects.create(name="Client Scope Pay", code="C-S-PAY", region="Bouake")
        customer_out = Customer.objects.create(name="Client Out Pay", code="C-O-PAY", region="Abidjan")

        invoice_scoped = Invoice.objects.create(customer=customer_scoped, status=InvoiceStatusChoices.BROUILLON, fne_required=False)
        invoice_out = Invoice.objects.create(customer=customer_out, status=InvoiceStatusChoices.BROUILLON, fne_required=False)
        Invoice.objects.filter(pk=invoice_scoped.pk).update(status=InvoiceStatusChoices.EMISE, total_amount=50000)
        Invoice.objects.filter(pk=invoice_out.pk).update(status=InvoiceStatusChoices.EMISE, total_amount=50000)

        self.client.force_authenticate(scoped_user)

        forbidden = self.client.post(
            "/api/v1/invoice-payments/",
            {"invoice": invoice_out.id, "amount": 10000, "payment_method": "especes"},
            format="json",
        )
        self.assertEqual(forbidden.status_code, 403)

        allowed = self.client.post(
            "/api/v1/invoice-payments/",
            {"invoice": invoice_scoped.id, "amount": 10000, "payment_method": "mobile_money"},
            format="json",
        )
        self.assertEqual(allowed.status_code, 201)
        self.assertEqual(InvoicePayment.objects.filter(invoice_id=invoice_scoped.id).count(), 1)

    def test_public_newsletter_throttle_returns_429(self):
        cache.clear()
        client = APIClient()
        statuses = []
        for index in range(65):
            response = client.post(
                "/api/v1/public/newsletter/",
                {"email": f"throttle-{index}@example.com"},
                format="json",
            )
            statuses.append(response.status_code)

        self.assertEqual(statuses[0], 201)
        self.assertIn(429, statuses)

    @override_settings(MAX_LOGIN_FAILURES=2)
    def test_login_bruteforce_is_throttled_and_lock_policy_still_applies(self):
        cache.clear()
        user = User.objects.create_user(username="login_target", password="ValidPass!234")
        client = APIClient()

        statuses = []
        for _ in range(12):
            response = client.post("/api/v1/auth/login/", {"username": user.username, "password": "wrong"}, format="json")
            statuses.append(response.status_code)

        self.assertIn(401, statuses)
        self.assertIn(429, statuses)

        profile = UserSecurityProfile.objects.get(user=user)
        self.assertTrue(profile.is_locked)

    def test_analytics_and_search_are_scoped(self):
        scoped_user = self.make_scoped_user("analytics_scope")
        self.grant_crm_perms(scoped_user, "view_dashboard")

        customer_scoped = Customer.objects.create(name="Client Scope", code="C-AN-1", region="Bouake")
        customer_other = Customer.objects.create(name="Client Other", code="C-AN-2", region="Abidjan")
        Lead.objects.create(name="Lead Scope", region="Bouake")
        Lead.objects.create(name="Lead Other", region="Abidjan")
        InboundRequest.objects.create(kind="lead", name="Inbound Scope", region="Bouake")
        InboundRequest.objects.create(kind="lead", name="Inbound Other", region="Abidjan")
        Opportunity.objects.create(title="Opp Scope", customer=customer_scoped)
        Opportunity.objects.create(title="Opp Other", customer=customer_other)

        self.client.force_authenticate(scoped_user)

        kpi_response = self.client.get("/api/v1/analytics/kpi/")
        self.assertEqual(kpi_response.status_code, 200)
        self.assertEqual(kpi_response.data["inbound"]["total"], 1)

        search_response = self.client.get("/api/v1/search/?q=Client")
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual({item["id"] for item in search_response.data["customers"]}, {customer_scoped.id})

    def test_api_access_logs_include_request_id_and_path(self):
        with self.assertLogs("crm.api.access", level="INFO") as captured:
            response = self.client.post("/api/v1/public/newsletter/", {"email": "log@example.com"}, format="json")
        self.assertEqual(response.status_code, 201)
        output = "\n".join(captured.output)
        self.assertIn('"request_id"', output)
        self.assertIn('"/api/v1/public/newsletter/"', output)
