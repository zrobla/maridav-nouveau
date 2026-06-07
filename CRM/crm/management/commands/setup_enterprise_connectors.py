"""Seed baseline enterprise connectors and field mappings."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from crm.models import (
    EnterpriseConnector,
    EnterpriseConnectorTransportChoices,
    EnterpriseFieldMapping,
    EnterpriseIntegrationDirectionChoices,
    EnterpriseIntegrationTypeChoices,
)


DEFAULT_CONNECTORS = [
    {
        "code": "erp_compta_main",
        "name": "ERP/Compta Main",
        "integration_type": EnterpriseIntegrationTypeChoices.ERP_COMPTA,
        "direction": EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
    },
    {
        "code": "telephony_whatsapp_main",
        "name": "Telephony/WhatsApp Main",
        "integration_type": EnterpriseIntegrationTypeChoices.TELEPHONY_WHATSAPP,
        "direction": EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
    },
    {
        "code": "bi_analytics_main",
        "name": "BI/Analytics Main",
        "integration_type": EnterpriseIntegrationTypeChoices.BI_ANALYTICS,
        "direction": EnterpriseIntegrationDirectionChoices.OUTBOUND,
    },
    {
        "code": "logistics_stock_main",
        "name": "Logistics/Stock Main",
        "integration_type": EnterpriseIntegrationTypeChoices.LOGISTICS_STOCK,
        "direction": EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
    },
    {
        "code": "fne_dgi_main",
        "name": "FNE/DGI Main",
        "integration_type": EnterpriseIntegrationTypeChoices.FNE_DGI,
        "direction": EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
    },
]


def _upsert_mapping(*, connector: EnterpriseConnector, entity_type: str, source_field: str, target_field: str, required: bool = False):
    EnterpriseFieldMapping.objects.update_or_create(
        connector=connector,
        entity_type=entity_type,
        source_field=source_field,
        version=1,
        defaults={
            "target_field": target_field,
            "transform_rule": "",
            "is_required": required,
            "default_value": "",
            "active": True,
        },
    )


class Command(BaseCommand):
    help = "Initialise les connecteurs enterprise par défaut (ERP, telephony, BI, logistics, FNE)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--activate",
            action="store_true",
            help="Active les connecteurs créés/actualisés.",
        )
        parser.add_argument(
            "--transport",
            default=EnterpriseConnectorTransportChoices.MOCK,
            choices=[EnterpriseConnectorTransportChoices.MOCK, EnterpriseConnectorTransportChoices.HTTP],
            help="Transport par défaut des connecteurs seedés.",
        )
        parser.add_argument(
            "--overwrite-existing",
            action="store_true",
            help="Ecrase les paramètres principaux des connecteurs déjà présents.",
        )

    def handle(self, *args, **options):
        activate = bool(options.get("activate"))
        transport = options.get("transport") or EnterpriseConnectorTransportChoices.MOCK
        overwrite_existing = bool(options.get("overwrite_existing"))

        created_count = 0
        updated_count = 0
        mapping_count = 0

        for item in DEFAULT_CONNECTORS:
            defaults = {
                "name": item["name"],
                "integration_type": item["integration_type"],
                "direction": item["direction"],
                "active": activate,
                "transport": transport,
                "timeout_seconds": 10,
                "max_retries": 5,
                "retry_backoff_seconds": 30,
                "dlq_after_attempts": 5,
                "metadata": {},
            }
            connector, created = EnterpriseConnector.objects.get_or_create(code=item["code"], defaults=defaults)
            if created:
                created_count += 1
            elif overwrite_existing:
                for key, value in defaults.items():
                    setattr(connector, key, value)
                connector.save()
                updated_count += 1

            if connector.integration_type in {
                EnterpriseIntegrationTypeChoices.ERP_COMPTA,
                EnterpriseIntegrationTypeChoices.LOGISTICS_STOCK,
            }:
                _upsert_mapping(connector=connector, entity_type="order", source_field="order_number", target_field="order_number", required=True)
                _upsert_mapping(connector=connector, entity_type="order", source_field="status", target_field="status")
                _upsert_mapping(connector=connector, entity_type="order", source_field="total_amount", target_field="total_amount")
                _upsert_mapping(
                    connector=connector,
                    entity_type="inbox:payment.sync",
                    source_field="invoice_id",
                    target_field="invoice_id",
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="inbox:payment.sync",
                    source_field="invoice_number",
                    target_field="invoice_number",
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="inbox:payment.sync",
                    source_field="amount",
                    target_field="amount",
                    required=True,
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="inbox:payment.sync",
                    source_field="payment_method",
                    target_field="payment_method",
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="inbox:payment.sync",
                    source_field="payment_reference",
                    target_field="payment_reference",
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="inbox:payment.sync",
                    source_field="payment_id",
                    target_field="payment_id",
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="inbox:payment.sync",
                    source_field="paid_at",
                    target_field="paid_at",
                )
                mapping_count += 10

            if connector.integration_type in {
                EnterpriseIntegrationTypeChoices.ERP_COMPTA,
                EnterpriseIntegrationTypeChoices.BI_ANALYTICS,
            }:
                _upsert_mapping(
                    connector=connector,
                    entity_type="invoice_payment",
                    source_field="invoice_number",
                    target_field="invoice_number",
                    required=True,
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="invoice_payment",
                    source_field="amount",
                    target_field="amount",
                    required=True,
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="invoice_payment",
                    source_field="payment_method",
                    target_field="payment_method",
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="invoice_payment",
                    source_field="payment_reference",
                    target_field="payment_reference",
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="invoice_payment",
                    source_field="paid_at",
                    target_field="paid_at",
                )
                _upsert_mapping(
                    connector=connector,
                    entity_type="invoice_payment",
                    source_field="source",
                    target_field="source",
                )
                mapping_count += 6

            if connector.integration_type == EnterpriseIntegrationTypeChoices.TELEPHONY_WHATSAPP:
                _upsert_mapping(connector=connector, entity_type="inbox", source_field="from", target_field="phone")
                _upsert_mapping(connector=connector, entity_type="inbox", source_field="body", target_field="message")
                _upsert_mapping(connector=connector, entity_type="inbox", source_field="contact_name", target_field="name")
                mapping_count += 3

            if connector.integration_type == EnterpriseIntegrationTypeChoices.FNE_DGI:
                _upsert_mapping(
                    connector=connector,
                    entity_type="invoice",
                    source_field="invoice_number",
                    target_field="invoice_number",
                    required=True,
                )
                _upsert_mapping(connector=connector, entity_type="invoice", source_field="nature", target_field="nature")
                _upsert_mapping(
                    connector=connector,
                    entity_type="invoice",
                    source_field="original_invoice_number",
                    target_field="original_invoice_number",
                )
                _upsert_mapping(connector=connector, entity_type="invoice", source_field="total_amount", target_field="amount_ttc")
                _upsert_mapping(connector=connector, entity_type="invoice", source_field="issued_at", target_field="issue_datetime")
                _upsert_mapping(connector=connector, entity_type="invoice", source_field="customer_id", target_field="customer_id")
                _upsert_mapping(connector=connector, entity_type="inbox", source_field="invoice_id", target_field="invoice_id")
                _upsert_mapping(connector=connector, entity_type="inbox", source_field="invoice_number", target_field="invoice_number")
                _upsert_mapping(connector=connector, entity_type="inbox", source_field="status", target_field="fne_status")
                _upsert_mapping(connector=connector, entity_type="inbox", source_field="reference", target_field="fne_reference")
                _upsert_mapping(connector=connector, entity_type="inbox", source_field="error_message", target_field="error_message")
                mapping_count += 11

        self.stdout.write(
            self.style.SUCCESS(
                "Enterprise connectors seeded "
                f"(created={created_count}, updated={updated_count}, mappings_upserted={mapping_count})."
            )
        )
