from __future__ import annotations

from django.test import TestCase

from crm.models import (
    Customer,
    Invoice,
    InvoiceFNEStatusChoices,
    InvoiceItem,
    InvoiceNatureChoices,
    InvoiceStatusChoices,
    Product,
    ProductCategory,
)
from crm.services.sales import recalculate_invoice_totals, validate_invoice_issue_prerequisites


class CreditNotePhase6Tests(TestCase):
    def setUp(self):
        super().setUp()
        self.customer = Customer.objects.create(
            name="Client Credit Note",
            code="C-CN-01",
            region="Abidjan",
            tax_ncc="NCC-12345",
            tax_ntd="NTD-12345",
            tax_rccm="RCCM-12345",
            tax_regime="Régime réel simplifié",
        )
        self.category = ProductCategory.objects.create(name="Gamme Test", slug="gamme-test")
        self.product = Product.objects.create(category=self.category, name="Produit Test", sku="PRD-CN-1", unit_price=10000)

    def _add_invoice_line(self, invoice: Invoice, *, quantity: int = 1, unit_price: int = 10000):
        InvoiceItem.objects.create(
            invoice=invoice,
            product=self.product,
            quantity=quantity,
            unit_price=unit_price,
            discount_pct=0,
            tax_rate_pct=0,
        )
        recalculate_invoice_totals(invoice)
        invoice.refresh_from_db()

    def _make_original_invoice(self, *, certified: bool) -> Invoice:
        original = Invoice.objects.create(
            customer=self.customer,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=True,
            fne_status=InvoiceFNEStatusChoices.NOT_SENT,
        )
        self._add_invoice_line(original, quantity=2, unit_price=12000)
        original.status = InvoiceStatusChoices.EMISE
        original.fne_status = (
            InvoiceFNEStatusChoices.CERTIFIED if certified else InvoiceFNEStatusChoices.PENDING
        )
        original.save(update_fields=["status", "fne_status", "updated_at"])
        original.refresh_from_db()
        return original

    def test_validate_credit_note_requires_certified_original(self):
        original = self._make_original_invoice(certified=False)
        credit_note = Invoice.objects.create(
            customer=self.customer,
            nature=InvoiceNatureChoices.CREDIT_NOTE,
            original_invoice=original,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=True,
        )
        self._add_invoice_line(credit_note, quantity=1, unit_price=12000)
        credit_note.status = InvoiceStatusChoices.EMISE
        credit_note.save(update_fields=["status", "updated_at"])
        credit_note.refresh_from_db()

        issues = validate_invoice_issue_prerequisites(credit_note)
        self.assertTrue(any("certifiée FNE" in issue for issue in issues))

    def test_credit_note_is_forced_back_to_draft_when_original_not_certified(self):
        original = self._make_original_invoice(certified=False)
        credit_note = Invoice.objects.create(
            customer=self.customer,
            nature=InvoiceNatureChoices.CREDIT_NOTE,
            original_invoice=original,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=True,
        )
        self._add_invoice_line(credit_note, quantity=1, unit_price=12000)

        credit_note.status = InvoiceStatusChoices.EMISE
        credit_note.save(update_fields=["status", "updated_at"])
        credit_note.refresh_from_db()

        self.assertEqual(credit_note.status, InvoiceStatusChoices.BROUILLON)

    def test_credit_note_can_be_issued_when_original_certified(self):
        original = self._make_original_invoice(certified=True)
        credit_note = Invoice.objects.create(
            customer=self.customer,
            nature=InvoiceNatureChoices.CREDIT_NOTE,
            original_invoice=original,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=True,
        )
        self._add_invoice_line(credit_note, quantity=1, unit_price=12000)

        credit_note.status = InvoiceStatusChoices.EMISE
        credit_note.save(update_fields=["status", "updated_at"])
        credit_note.refresh_from_db()

        self.assertEqual(credit_note.status, InvoiceStatusChoices.EMISE)
        self.assertEqual(credit_note.fne_status, InvoiceFNEStatusChoices.PENDING)
