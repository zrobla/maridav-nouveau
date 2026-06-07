from __future__ import annotations

from django.test import TestCase

from crm.models import (
    Customer,
    Invoice,
    InvoiceItem,
    InvoicePayment,
    InvoicePaymentMethodChoices,
    InvoiceStatusChoices,
    Product,
    ProductCategory,
)
from crm.services.sales import recalculate_invoice_totals, validate_invoice_payment_prerequisites


class InvoicePaymentsPhase7Tests(TestCase):
    def setUp(self):
        super().setUp()
        self.customer = Customer.objects.create(
            name="Client Paiements",
            code="C-PAY-01",
            region="Abidjan",
            tax_ncc="NCC-PAY-01",
            tax_ntd="NTD-PAY-01",
            tax_rccm="RCCM-PAY-01",
            tax_regime="Régime réel simplifié",
        )
        self.category = ProductCategory.objects.create(name="Cat Paiements", slug="cat-paiements")
        self.product = Product.objects.create(
            category=self.category,
            name="Produit Paiement",
            sku="SKU-PAY-1",
            unit_price=25000,
        )

    def _make_issued_invoice(self, *, quantity: int = 2, unit_price: int = 25000) -> Invoice:
        invoice = Invoice.objects.create(
            customer=self.customer,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=False,
        )
        InvoiceItem.objects.create(invoice=invoice, product=self.product, quantity=quantity, unit_price=unit_price)
        recalculate_invoice_totals(invoice)
        invoice.status = InvoiceStatusChoices.EMISE
        invoice.save(update_fields=["status", "updated_at"])
        invoice.refresh_from_db()
        return invoice

    def test_manual_payments_reconcile_invoice_to_partial_then_paid(self):
        invoice = self._make_issued_invoice(quantity=2, unit_price=30000)
        self.assertEqual(invoice.total_amount, 60000)

        InvoicePayment.objects.create(
            invoice=invoice,
            amount=20000,
            payment_method=InvoicePaymentMethodChoices.MOBILE_MONEY,
            payment_reference="MM-001",
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.paid_amount, 20000)
        self.assertEqual(invoice.status, InvoiceStatusChoices.PARTIELLEMENT_PAYEE)
        self.assertEqual(invoice.balance_due, 40000)

        InvoicePayment.objects.create(
            invoice=invoice,
            amount=40000,
            payment_method=InvoicePaymentMethodChoices.VIREMENT,
            payment_reference="VIR-001",
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.paid_amount, 60000)
        self.assertEqual(invoice.status, InvoiceStatusChoices.PAYEE)
        self.assertEqual(invoice.balance_due, 0)
        self.assertEqual(invoice.payment_method, InvoicePaymentMethodChoices.VIREMENT)
        self.assertEqual(invoice.payment_reference, "VIR-001")

    def test_validate_payment_rejects_amount_above_balance(self):
        invoice = self._make_issued_invoice(quantity=1, unit_price=30000)
        InvoicePayment.objects.create(
            invoice=invoice,
            amount=10000,
            payment_method=InvoicePaymentMethodChoices.ESPECES,
        )
        invoice.refresh_from_db()
        issues = validate_invoice_payment_prerequisites(invoice, amount=25000)
        self.assertTrue(any("reste à payer" in issue for issue in issues))

    def test_deleting_payment_reconciles_back_to_emitted(self):
        invoice = self._make_issued_invoice(quantity=1, unit_price=20000)
        payment = InvoicePayment.objects.create(
            invoice=invoice,
            amount=20000,
            payment_method=InvoicePaymentMethodChoices.CHEQUE,
            payment_reference="CHQ-001",
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, InvoiceStatusChoices.PAYEE)
        self.assertEqual(invoice.paid_amount, 20000)

        payment.delete()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, InvoiceStatusChoices.EMISE)
        self.assertEqual(invoice.paid_amount, 0)
        self.assertEqual(invoice.balance_due, 20000)
