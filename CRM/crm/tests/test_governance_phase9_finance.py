from __future__ import annotations

from django.test import TestCase

from crm.models import (
    Customer,
    DataQualityIssue,
    DataQualityStatusChoices,
    Invoice,
    InvoiceItem,
    InvoicePayment,
    InvoicePaymentMethodChoices,
    InvoiceStatusChoices,
    Product,
    ProductCategory,
)
from crm.services.governance import run_invoice_data_quality_checks
from crm.services.sales import recalculate_invoice_totals


class GovernancePhase9FinanceTests(TestCase):
    def setUp(self):
        super().setUp()
        self.customer = Customer.objects.create(
            name="Client Governance Fin",
            code="C-GOV-FIN",
            region="Abidjan",
            tax_ncc="NCC-GOV-FIN",
            tax_ntd="NTD-GOV-FIN",
            tax_rccm="RCCM-GOV-FIN",
            tax_regime="Régime réel simplifié",
        )
        self.category = ProductCategory.objects.create(name="Cat Governance", slug="cat-governance")
        self.product = Product.objects.create(
            category=self.category,
            name="Produit Governance",
            sku="SKU-GOV-1",
            unit_price=40000,
        )

    def _make_issued_invoice(self) -> Invoice:
        invoice = Invoice.objects.create(
            customer=self.customer,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=False,
        )
        InvoiceItem.objects.create(invoice=invoice, product=self.product, quantity=1, unit_price=40000)
        recalculate_invoice_totals(invoice)
        invoice.status = InvoiceStatusChoices.EMISE
        invoice.save(update_fields=["status", "updated_at"])
        invoice.refresh_from_db()
        return invoice

    def test_payment_ledger_mismatch_issue_is_auto_resolved_when_fixed(self):
        invoice = self._make_issued_invoice()
        Invoice.objects.filter(pk=invoice.pk).update(
            paid_amount=15000,
            payment_method=InvoicePaymentMethodChoices.NON_RENSEIGNE,
        )
        invoice.refresh_from_db()

        run_invoice_data_quality_checks(invoice)
        mismatch_issue = DataQualityIssue.objects.filter(
            source="invoice",
            object_id=invoice.pk,
            fingerprint=f"invoice:{invoice.pk}:payment_ledger_mismatch",
        ).first()
        self.assertIsNotNone(mismatch_issue)
        self.assertEqual(mismatch_issue.status, DataQualityStatusChoices.OPEN)

        InvoicePayment.objects.create(
            invoice=invoice,
            amount=15000,
            payment_method=InvoicePaymentMethodChoices.MOBILE_MONEY,
            payment_reference="MM-GOV-001",
        )
        invoice.refresh_from_db()
        run_invoice_data_quality_checks(invoice)

        mismatch_issue.refresh_from_db()
        self.assertEqual(mismatch_issue.status, DataQualityStatusChoices.RESOLVED)

    def test_payment_method_missing_issue_is_detected(self):
        invoice = self._make_issued_invoice()
        Invoice.objects.filter(pk=invoice.pk).update(
            paid_amount=10000,
            payment_method=InvoicePaymentMethodChoices.NON_RENSEIGNE,
        )
        invoice.refresh_from_db()

        run_invoice_data_quality_checks(invoice)
        method_issue = DataQualityIssue.objects.filter(
            source="invoice",
            object_id=invoice.pk,
            fingerprint=f"invoice:{invoice.pk}:payment_method_missing",
        ).first()
        self.assertIsNotNone(method_issue)
        self.assertEqual(method_issue.status, DataQualityStatusChoices.OPEN)
