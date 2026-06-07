from __future__ import annotations

from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from crm.models import (
    EnterpriseConnector,
    EnterpriseConnectorTransportChoices,
    EnterpriseDeadLetterEvent,
    EnterpriseInboxEvent,
    EnterpriseInboxStatusChoices,
    EnterpriseIntegrationDirectionChoices,
    EnterpriseIntegrationTypeChoices,
    EnterpriseOutboxEvent,
    EnterpriseOutboxStatusChoices,
    InboundKindChoices,
    InboundRequest,
    Invoice,
    InvoiceFNEStatusChoices,
    InvoiceItem,
    InvoicePayment,
    InvoiceStatusChoices,
    Order,
    Customer,
    Product,
    ProductCategory,
)
from crm.services.integrations import (
    emit_invoice_outbox_event,
    emit_invoice_payment_outbox_event,
    emit_order_outbox_event,
    enqueue_outbox_event,
    ingest_inbox_event,
    process_inbox_events,
    process_outbox_events,
)
from crm.services.sales import recalculate_invoice_totals


class EnterpriseConnectorsPhase5Tests(TestCase):
    def make_connector(
        self,
        *,
        code: str,
        integration_type: str = EnterpriseIntegrationTypeChoices.ERP_COMPTA,
        direction: str = EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
        transport: str = EnterpriseConnectorTransportChoices.MOCK,
        max_retries: int = 5,
        dlq_after_attempts: int = 5,
    ) -> EnterpriseConnector:
        return EnterpriseConnector.objects.create(
            code=code,
            name=code,
            integration_type=integration_type,
            direction=direction,
            active=True,
            transport=transport,
            max_retries=max_retries,
            dlq_after_attempts=dlq_after_attempts,
            retry_backoff_seconds=1,
        )

    def test_enqueue_outbox_event_is_idempotent_per_connector(self):
        connector = self.make_connector(code="erp-idempotent")
        event, created = enqueue_outbox_event(
            connector=connector,
            entity_type="order",
            entity_id=10,
            event_type="order.updated",
            payload={"order_number": "CMD-100"},
            idempotency_key="order:10:stable-key",
        )
        self.assertTrue(created)
        self.assertEqual(event.status, EnterpriseOutboxStatusChoices.PENDING)

        duplicated, created_again = enqueue_outbox_event(
            connector=connector,
            entity_type="order",
            entity_id=10,
            event_type="order.updated",
            payload={"order_number": "CMD-100"},
            idempotency_key="order:10:stable-key",
        )
        self.assertFalse(created_again)
        self.assertEqual(event.pk, duplicated.pk)
        self.assertEqual(EnterpriseOutboxEvent.objects.count(), 1)

    def test_emit_order_outbox_event_creates_once_for_same_version(self):
        connector = self.make_connector(code="erp-order", integration_type=EnterpriseIntegrationTypeChoices.ERP_COMPTA)
        customer = Customer.objects.create(name="Client ERP", code="C-ERP-01", region="Abidjan")
        order = Order.objects.create(customer=customer)
        before_count = EnterpriseOutboxEvent.objects.filter(connector=connector).count()

        first = emit_order_outbox_event(order, created=True)
        second = emit_order_outbox_event(order, created=True)
        after_count = EnterpriseOutboxEvent.objects.filter(connector=connector).count()

        self.assertEqual(first["selected"], 1)
        self.assertEqual(after_count, before_count)
        self.assertEqual(second["existing"], 1)
        self.assertEqual(after_count, 1)

    def test_emit_invoice_outbox_event_targets_fne_when_issued(self):
        erp = self.make_connector(code="erp-invoice", integration_type=EnterpriseIntegrationTypeChoices.ERP_COMPTA)
        bi = self.make_connector(code="bi-invoice", integration_type=EnterpriseIntegrationTypeChoices.BI_ANALYTICS)
        fne = self.make_connector(code="fne-invoice", integration_type=EnterpriseIntegrationTypeChoices.FNE_DGI)
        customer = Customer.objects.create(
            name="Client FNE",
            code="C-FNE-01",
            region="Abidjan",
            tax_ncc="NCC-001",
            tax_ntd="NTD-001",
            tax_rccm="RCCM-001",
            tax_regime="Régime réel simplifié",
        )
        category = ProductCategory.objects.create(name="Cat FNE", slug="cat-fne")
        product = Product.objects.create(category=category, name="Produit FNE", sku="SKU-FNE-1", unit_price=150000)
        invoice = Invoice.objects.create(
            customer=customer,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=True,
        )
        InvoiceItem.objects.create(invoice=invoice, product=product, quantity=1, unit_price=150000)
        recalculate_invoice_totals(invoice)
        invoice.status = InvoiceStatusChoices.EMISE
        invoice.save(update_fields=["status", "updated_at"])
        invoice.refresh_from_db()

        before_count = EnterpriseOutboxEvent.objects.filter(entity_type="invoice", entity_id=invoice.pk).count()
        metrics = emit_invoice_outbox_event(invoice, created=True)
        self.assertEqual(metrics["selected"], 3)
        after_count = EnterpriseOutboxEvent.objects.filter(entity_type="invoice", entity_id=invoice.pk).count()
        self.assertGreaterEqual(after_count, before_count)
        self.assertTrue(
            EnterpriseOutboxEvent.objects.filter(
                connector=erp,
                entity_type="invoice",
                entity_id=invoice.pk,
            ).exists()
        )
        self.assertTrue(
            EnterpriseOutboxEvent.objects.filter(
                connector=bi,
                entity_type="invoice",
                entity_id=invoice.pk,
            ).exists()
        )
        self.assertTrue(
            EnterpriseOutboxEvent.objects.filter(
                connector=fne,
                entity_type="invoice",
                entity_id=invoice.pk,
            ).exists()
        )

    def test_emit_invoice_payment_outbox_event_targets_erp_and_bi(self):
        erp = self.make_connector(code="erp-payment-out", integration_type=EnterpriseIntegrationTypeChoices.ERP_COMPTA)
        bi = self.make_connector(code="bi-payment-out", integration_type=EnterpriseIntegrationTypeChoices.BI_ANALYTICS)
        self.make_connector(code="fne-payment-out", integration_type=EnterpriseIntegrationTypeChoices.FNE_DGI)
        customer = Customer.objects.create(
            name="Client Payment Out",
            code="C-PAY-OUT",
            region="Abidjan",
            tax_ncc="NCC-PAY-OUT",
            tax_ntd="NTD-PAY-OUT",
            tax_rccm="RCCM-PAY-OUT",
            tax_regime="Régime réel simplifié",
        )
        category = ProductCategory.objects.create(name="Cat Pay Out", slug="cat-pay-out")
        product = Product.objects.create(category=category, name="Produit Pay Out", sku="SKU-PAY-OUT", unit_price=120000)
        invoice = Invoice.objects.create(
            customer=customer,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=False,
        )
        InvoiceItem.objects.create(invoice=invoice, product=product, quantity=1, unit_price=120000)
        recalculate_invoice_totals(invoice)
        invoice.status = InvoiceStatusChoices.EMISE
        invoice.save(update_fields=["status", "updated_at"])
        payment = InvoicePayment.objects.create(
            invoice=invoice,
            amount=40000,
            payment_method="mobile_money",
            payment_reference="MM-OUT-001",
        )

        metrics = emit_invoice_payment_outbox_event(payment, event_type="invoice_payment.created")
        self.assertEqual(metrics["selected"], 2)
        self.assertTrue(
            EnterpriseOutboxEvent.objects.filter(
                connector=erp,
                entity_type="invoice_payment",
                entity_id=payment.pk,
            ).exists()
        )
        self.assertTrue(
            EnterpriseOutboxEvent.objects.filter(
                connector=bi,
                entity_type="invoice_payment",
                entity_id=payment.pk,
            ).exists()
        )

    def test_process_outbox_delivers_event_with_mock_transport(self):
        connector = self.make_connector(code="erp-deliver")
        event = EnterpriseOutboxEvent.objects.create(
            connector=connector,
            entity_type="order",
            entity_id=11,
            event_type="order.updated",
            idempotency_key="order:11:deliver",
            payload={"order_number": "CMD-DELIVER"},
        )

        metrics = process_outbox_events(limit=10)
        event.refresh_from_db()

        self.assertEqual(metrics["delivered"], 1)
        self.assertEqual(event.status, EnterpriseOutboxStatusChoices.DELIVERED)
        self.assertEqual(event.attempt_count, 1)
        self.assertIsNotNone(event.delivered_at)
        self.assertIn("mock-", event.external_reference)

    def test_process_outbox_retries_then_moves_to_dead_letter(self):
        connector = self.make_connector(code="erp-retry", max_retries=2, dlq_after_attempts=2)
        event = EnterpriseOutboxEvent.objects.create(
            connector=connector,
            entity_type="order",
            entity_id=12,
            event_type="order.updated",
            idempotency_key="order:12:retry",
            payload={"_force_result": "transient"},
        )

        first_metrics = process_outbox_events(limit=10, now=timezone.now())
        event.refresh_from_db()
        self.assertEqual(first_metrics["failed"], 1)
        self.assertEqual(event.status, EnterpriseOutboxStatusChoices.FAILED)
        self.assertEqual(event.attempt_count, 1)
        self.assertIsNotNone(event.next_retry_at)

        event.next_retry_at = timezone.now() - timedelta(seconds=1)
        event.save(update_fields=["next_retry_at", "updated_at"])

        second_metrics = process_outbox_events(limit=10, now=timezone.now())
        event.refresh_from_db()
        self.assertEqual(second_metrics["dead"], 1)
        self.assertEqual(event.status, EnterpriseOutboxStatusChoices.DEAD)
        self.assertEqual(event.attempt_count, 2)
        self.assertEqual(
            EnterpriseDeadLetterEvent.objects.filter(related_outbox=event).count(),
            1,
        )

    def test_ingest_inbox_event_deduplicates_external_event_id(self):
        self.make_connector(
            code="tel-ingest",
            integration_type=EnterpriseIntegrationTypeChoices.TELEPHONY_WHATSAPP,
            direction=EnterpriseIntegrationDirectionChoices.INBOUND,
        )

        event, created = ingest_inbox_event(
            connector_code="tel-ingest",
            external_event_id="ext-100",
            event_type="whatsapp.message",
            payload={"from": "+22501020304", "body": "Bonjour"},
        )
        self.assertTrue(created)
        self.assertEqual(event.status, EnterpriseInboxStatusChoices.PENDING)

        duplicated, created_again = ingest_inbox_event(
            connector_code="tel-ingest",
            external_event_id="ext-100",
            event_type="whatsapp.message",
            payload={"from": "+22501020304", "body": "Bonjour"},
        )
        self.assertFalse(created_again)
        self.assertEqual(event.pk, duplicated.pk)
        self.assertEqual(EnterpriseInboxEvent.objects.count(), 1)

    def test_process_inbox_telephony_creates_inbound_request(self):
        self.make_connector(
            code="tel-process",
            integration_type=EnterpriseIntegrationTypeChoices.TELEPHONY_WHATSAPP,
            direction=EnterpriseIntegrationDirectionChoices.INBOUND,
        )
        inbox_event, _ = ingest_inbox_event(
            connector_code="tel-process",
            external_event_id="ext-200",
            event_type="whatsapp.message",
            payload={"from": "+22502030405", "body": "Besoin info", "contact_name": "Client WA"},
        )

        metrics = process_inbox_events(limit=10)
        inbox_event.refresh_from_db()
        self.assertEqual(metrics["handled"], 1)
        self.assertEqual(inbox_event.status, EnterpriseInboxStatusChoices.PROCESSED)

        inbound = InboundRequest.objects.get()
        self.assertEqual(inbound.kind, InboundKindChoices.CONTACT)
        self.assertEqual(inbound.phone, "+22502030405")
        self.assertIn("connector_code", inbound.raw_data)
        self.assertEqual(inbound.raw_data["connector_code"], "tel-process")

    def test_process_inbox_marks_duplicate_dedup_key_as_ignored(self):
        self.make_connector(
            code="tel-dedup",
            integration_type=EnterpriseIntegrationTypeChoices.TELEPHONY_WHATSAPP,
            direction=EnterpriseIntegrationDirectionChoices.INBOUND,
        )
        first, _ = ingest_inbox_event(
            connector_code="tel-dedup",
            external_event_id="ext-301",
            event_type="whatsapp.message",
            dedup_key="session-xyz",
            payload={"from": "+22509080706", "body": "Message 1"},
        )
        second, _ = ingest_inbox_event(
            connector_code="tel-dedup",
            external_event_id="ext-302",
            event_type="whatsapp.message",
            dedup_key="session-xyz",
            payload={"from": "+22509080706", "body": "Message 2"},
        )

        process_inbox_events(limit=1)
        process_inbox_events(limit=1)

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.status, EnterpriseInboxStatusChoices.PROCESSED)
        self.assertEqual(second.status, EnterpriseInboxStatusChoices.IGNORED)
        self.assertEqual(InboundRequest.objects.count(), 1)

    def test_process_inbox_order_delivery_blocked_when_invoice_not_fne_certified(self):
        self.make_connector(
            code="erp-order-inbound",
            integration_type=EnterpriseIntegrationTypeChoices.ERP_COMPTA,
            direction=EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
        )
        customer = Customer.objects.create(name="Client Gate Inbound", code="C-GATE-IN", region="Abidjan")
        order = Order.objects.create(customer=customer, status="confirme")
        Invoice.objects.create(
            customer=customer,
            order=order,
            status=InvoiceStatusChoices.EMISE,
            fne_required=True,
            fne_status=InvoiceFNEStatusChoices.PENDING,
            total_amount=120000,
        )
        inbox_event, _ = ingest_inbox_event(
            connector_code="erp-order-inbound",
            external_event_id="ext-order-delivered",
            event_type="order.sync",
            payload={"order_id": order.id, "status": "delivered"},
        )

        metrics = process_inbox_events(limit=10)
        inbox_event.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(metrics["dead"], 1)
        self.assertEqual(inbox_event.status, EnterpriseInboxStatusChoices.DEAD)
        self.assertEqual(order.status, "confirme")

    def test_process_inbox_payment_sync_creates_payment_and_reconciles_invoice(self):
        self.make_connector(
            code="erp-payment-inbound",
            integration_type=EnterpriseIntegrationTypeChoices.ERP_COMPTA,
            direction=EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
        )
        customer = Customer.objects.create(
            name="Client Paiement Inbound",
            code="C-PAY-IN",
            region="Abidjan",
            tax_ncc="NCC-PAY-IN",
            tax_ntd="NTD-PAY-IN",
            tax_rccm="RCCM-PAY-IN",
            tax_regime="Régime réel simplifié",
        )
        category = ProductCategory.objects.create(name="Cat Pay In", slug="cat-pay-in")
        product = Product.objects.create(category=category, name="Produit Pay In", sku="SKU-PAY-IN", unit_price=50000)
        invoice = Invoice.objects.create(
            customer=customer,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=False,
        )
        InvoiceItem.objects.create(invoice=invoice, product=product, quantity=1, unit_price=50000)
        recalculate_invoice_totals(invoice)
        invoice.status = InvoiceStatusChoices.EMISE
        invoice.save(update_fields=["status", "updated_at"])
        invoice.refresh_from_db()

        inbox_event, _ = ingest_inbox_event(
            connector_code="erp-payment-inbound",
            external_event_id="ext-payment-001",
            event_type="payment.sync",
            payload={
                "invoice_id": invoice.id,
                "amount": 20000,
                "payment_method": "mobile_money",
                "payment_reference": "MM-INT-001",
                "payment_id": "PAY-EVT-001",
            },
        )

        metrics = process_inbox_events(limit=10)
        inbox_event.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(metrics["handled"], 1)
        self.assertEqual(inbox_event.status, EnterpriseInboxStatusChoices.PROCESSED)
        self.assertEqual(invoice.status, InvoiceStatusChoices.PARTIELLEMENT_PAYEE)
        self.assertEqual(invoice.paid_amount, 20000)
        self.assertEqual(InvoicePayment.objects.filter(invoice=invoice).count(), 1)

    def test_process_inbox_payment_sync_is_idempotent_on_source_event(self):
        self.make_connector(
            code="erp-payment-idempotent",
            integration_type=EnterpriseIntegrationTypeChoices.ERP_COMPTA,
            direction=EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
        )
        customer = Customer.objects.create(
            name="Client Paiement Idem",
            code="C-PAY-IDEM",
            region="Abidjan",
            tax_ncc="NCC-PAY-IDEM",
            tax_ntd="NTD-PAY-IDEM",
            tax_rccm="RCCM-PAY-IDEM",
            tax_regime="Régime réel simplifié",
        )
        category = ProductCategory.objects.create(name="Cat Pay Idem", slug="cat-pay-idem")
        product = Product.objects.create(category=category, name="Produit Pay Idem", sku="SKU-PAY-IDEM", unit_price=30000)
        invoice = Invoice.objects.create(
            customer=customer,
            status=InvoiceStatusChoices.BROUILLON,
            fne_required=False,
        )
        InvoiceItem.objects.create(invoice=invoice, product=product, quantity=1, unit_price=30000)
        recalculate_invoice_totals(invoice)
        invoice.status = InvoiceStatusChoices.EMISE
        invoice.save(update_fields=["status", "updated_at"])
        invoice.refresh_from_db()

        ingest_inbox_event(
            connector_code="erp-payment-idempotent",
            external_event_id="ext-payment-201",
            event_type="payment.sync",
            payload={
                "invoice_id": invoice.id,
                "amount": 10000,
                "payment_id": "PAY-SAME-001",
            },
        )
        ingest_inbox_event(
            connector_code="erp-payment-idempotent",
            external_event_id="ext-payment-202",
            event_type="payment.sync",
            payload={
                "invoice_id": invoice.id,
                "amount": 10000,
                "payment_id": "PAY-SAME-001",
            },
        )

        first_metrics = process_inbox_events(limit=1)
        second_metrics = process_inbox_events(limit=1)
        invoice.refresh_from_db()
        self.assertEqual(first_metrics["handled"], 1)
        self.assertEqual(second_metrics["handled"], 1)
        self.assertEqual(InvoicePayment.objects.filter(invoice=invoice).count(), 1)
        self.assertEqual(invoice.paid_amount, 10000)


class EnterpriseConnectorCommandsPhase5Tests(TestCase):
    def test_setup_enterprise_connectors_creates_default_set(self):
        call_command("setup_enterprise_connectors", "--activate")
        self.assertEqual(EnterpriseConnector.objects.count(), 5)
        self.assertTrue(
            EnterpriseConnector.objects.filter(integration_type=EnterpriseIntegrationTypeChoices.FNE_DGI).exists()
        )
        self.assertGreater(EnterpriseConnector.objects.filter(active=True).count(), 0)

    def test_run_enterprise_connectors_command_outputs_metrics(self):
        connector = EnterpriseConnector.objects.create(
            code="erp-command",
            name="ERP Command",
            integration_type=EnterpriseIntegrationTypeChoices.ERP_COMPTA,
            direction=EnterpriseIntegrationDirectionChoices.OUTBOUND,
            active=True,
            transport=EnterpriseConnectorTransportChoices.MOCK,
        )
        EnterpriseOutboxEvent.objects.create(
            connector=connector,
            entity_type="order",
            entity_id=50,
            event_type="order.updated",
            idempotency_key="order:50:command",
            payload={"order_number": "CMD-50"},
        )
        stdout = StringIO()
        call_command("run_enterprise_connectors", "--outbox-only", stdout=stdout)
        output = stdout.getvalue()
        self.assertIn("Enterprise connector cycle OK", output)
        self.assertIn('"outbox"', output)
