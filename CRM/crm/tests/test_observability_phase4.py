from __future__ import annotations

from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from crm.models import (
    Customer,
    DataQualityIssue,
    DataQualitySeverityChoices,
    DataQualityStatusChoices,
    EscalationLevelChoices,
    EscalationStatusChoices,
    InboundRequest,
    Invoice,
    InvoiceItem,
    InvoiceFNEStatusChoices,
    InvoiceStatusChoices,
    Product,
    ProductCategory,
    SlaEscalation,
)
from crm.services.sales import recalculate_invoice_totals
from crm.services.observability import reset_observability_metrics

User = get_user_model()


def grant_reports_perm(user):
    perm = Permission.objects.get(content_type__app_label="crm", codename="view_reports")
    user.user_permissions.add(perm)


@override_settings(API_SECURITY_STRICT_MODE=True)
class ObservabilitySummaryPhase4Tests(APITestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        reset_observability_metrics(minutes=120)
        self.user = User.objects.create_user(username="obs_reports", password="StrongPass!234")
        grant_reports_perm(self.user)

    def test_observability_summary_endpoint_returns_api_and_sla_metrics(self):
        public = APIClient()
        public.post(
            "/api/v1/public/inbound/",
            {
                "name": "Obs Intake",
                "email": "obs-intake@example.com",
                "phone": "+22500001001",
                "region": "Bouake",
                "segment": "volailles",
            },
            format="json",
        )
        public.get("/api/v1/not-found-observability/")

        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/observability/summary/?window_minutes=5")

        self.assertEqual(response.status_code, 200)
        self.assertIn("request_id", response.data)
        self.assertIn("health", response.data)
        self.assertIn("api", response.data)
        self.assertIn("sla", response.data)
        self.assertIn("finance", response.data)
        self.assertIn("alerts", response.data)
        self.assertGreaterEqual(response.data["api"]["requests"], 2)
        self.assertGreaterEqual(response.data["api"]["status_4xx"], 1)

    @override_settings(
        OBS_ALERT_MIN_REQUESTS=1,
        OBS_ALERT_4XX_RATE_PCT=0.1,
        OBS_ALERT_P95_MS=0.1,
    )
    def test_observability_summary_raises_alerts_when_thresholds_breached(self):
        public = APIClient()
        public.get("/api/v1/observability-missing-route/")

        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/observability/summary/?window_minutes=5")
        self.assertEqual(response.status_code, 200)

        alert_codes = {item["code"] for item in response.data["alerts"]}
        self.assertIn("api_4xx_rate_high", alert_codes)
        self.assertIn("api_latency_p95_high", alert_codes)

    @override_settings(
        OBS_ALERT_FIN_DQ_OPEN=0,
        OBS_ALERT_FIN_DQ_CRITICAL=0,
        OBS_ALERT_FIN_OVERDUE_AMOUNT=1000,
        OBS_ALERT_FIN_FNE_REJECTED=0,
        OBS_ALERT_FIN_LEDGER_MISMATCH=0,
    )
    def test_observability_summary_finance_alerts(self):
        customer = Customer.objects.create(
            name="Client Observability Finance",
            code="C-OBS-FIN",
            region="Abidjan",
            tax_ncc="NCC-OBS-FIN",
            tax_ntd="NTD-OBS-FIN",
            tax_rccm="RCCM-OBS-FIN",
            tax_regime="Régime réel simplifié",
        )
        category = ProductCategory.objects.create(name="Cat Obs Fin", slug="cat-obs-fin")
        product = Product.objects.create(category=category, name="Produit Obs Fin", sku="SKU-OBS-FIN", unit_price=50000)
        invoice = Invoice.objects.create(
            customer=customer,
            status=InvoiceStatusChoices.BROUILLON,
            due_date=timezone.now().date() - timedelta(days=1),
            fne_required=True,
            fne_status=InvoiceFNEStatusChoices.REJECTED,
        )
        InvoiceItem.objects.create(invoice=invoice, product=product, quantity=1, unit_price=50000)
        recalculate_invoice_totals(invoice)
        Invoice.objects.filter(pk=invoice.pk).update(
            paid_amount=10000,
            status=InvoiceStatusChoices.EMISE,
            updated_at=timezone.now(),
        )
        invoice.refresh_from_db()
        DataQualityIssue.objects.create(
            source="invoice",
            content_type=ContentType.objects.get_for_model(Invoice),
            object_id=invoice.pk,
            issue_type="inconsistent_data",
            severity=DataQualitySeverityChoices.CRITICAL,
            status=DataQualityStatusChoices.OPEN,
            fingerprint=f"invoice:{invoice.pk}:payment_ledger_mismatch",
            message="Mismatch ledger",
            suggested_action="Fix",
        )

        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/observability/summary/?window_minutes=5")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data["finance"]["overdue_unpaid_amount_total"], 40000)
        alert_codes = {item["code"] for item in response.data["alerts"]}
        self.assertIn("finance_dq_open_high", alert_codes)
        self.assertIn("finance_dq_critical_present", alert_codes)
        self.assertIn("finance_overdue_amount_high", alert_codes)
        self.assertIn("finance_fne_rejected_present", alert_codes)
        self.assertIn("finance_payment_ledger_mismatch_open", alert_codes)


class ObservabilityCommandPhase4Tests(TestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        reset_observability_metrics(minutes=120)

    @override_settings(OBS_ALERT_SLA_OPEN=0)
    def test_command_fail_on_alert_returns_error_for_sla_backlog(self):
        inbound = InboundRequest.objects.create(
            kind="lead",
            name="Inbound Obs",
            first_response_due_at=timezone.now() - timedelta(hours=2),
        )
        SlaEscalation.objects.create(
            source_type="inbound",
            content_type=ContentType.objects.get_for_model(InboundRequest),
            object_id=inbound.pk,
            escalation_level=EscalationLevelChoices.LEVEL_1,
            status=EscalationStatusChoices.OPEN,
            due_at=timezone.now() - timedelta(hours=1),
            reason="Test alert observability",
        )

        with self.assertRaises(CommandError):
            call_command("run_observability_checks", "--fail-on-alert")

    def test_command_outputs_summary_payload(self):
        stdout = StringIO()
        call_command("run_observability_checks", stdout=stdout)
        output = stdout.getvalue()
        self.assertIn("Observability health=", output)
        self.assertIn('"api"', output)
        self.assertIn('"sla"', output)
        self.assertIn('"finance"', output)
