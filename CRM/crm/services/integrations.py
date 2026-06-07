from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from crm.models import (
    ChannelChoices,
    EnterpriseConnector,
    EnterpriseConnectorAuthModeChoices,
    EnterpriseConnectorTransportChoices,
    EnterpriseDeadLetterDirectionChoices,
    EnterpriseDeadLetterEvent,
    EnterpriseFieldMapping,
    EnterpriseInboxEvent,
    EnterpriseInboxStatusChoices,
    EnterpriseIntegrationDirectionChoices,
    EnterpriseIntegrationTypeChoices,
    EnterpriseOutboxEvent,
    EnterpriseOutboxStatusChoices,
    InboundKindChoices,
    InboundPriorityChoices,
    InboundRequest,
    Invoice,
    InvoicePayment,
    InvoicePaymentMethodChoices,
    InvoicePaymentSourceChoices,
    InvoiceFNEStatusChoices,
    InvoiceStatusChoices,
    Order,
    OrderStatusChoices,
)
from crm.services.sales import validate_invoice_payment_prerequisites, validate_order_fne_delivery_gate
from crm.request_context import get_current_request

integration_logger = logging.getLogger("crm.integrations")

_INTEGRATION_RUNTIME_CONTEXT: ContextVar[bool] = ContextVar("crm_integration_runtime_context", default=False)
_MAX_BACKOFF_SECONDS = 3600


class IntegrationTransientError(Exception):
    """Error eligible for retry with backoff."""


class IntegrationPermanentError(Exception):
    """Error that must be dead-lettered without retry."""


@contextmanager
def integration_runtime_context():
    token = _INTEGRATION_RUNTIME_CONTEXT.set(True)
    try:
        yield
    finally:
        _INTEGRATION_RUNTIME_CONTEXT.reset(token)


def is_integration_runtime_active() -> bool:
    return bool(_INTEGRATION_RUNTIME_CONTEXT.get())


def _jsonable(value: Any):
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _current_request_id() -> str:
    request = get_current_request()
    if request is None:
        return ""
    return getattr(request, "request_id", "") or request.headers.get("X-Request-ID", "")


def _current_correlation_id(request_id: str = "") -> str:
    request = get_current_request()
    if request is not None:
        value = request.headers.get("X-Correlation-ID", "") or request.headers.get("X-Request-ID", "")
        if value:
            return value.strip()[:64]
    return (request_id or "")[:64]


def _sha_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_order_payload(order: Order) -> dict[str, Any]:
    items = [
        {
            "id": item.pk,
            "product_id": item.product_id,
            "quantity": int(item.quantity or 0),
            "unit_price": int(item.unit_price or 0),
            "total_price": int(item.total_price or 0),
        }
        for item in order.items.select_related("product").all()
    ]
    return {
        "id": order.pk,
        "order_number": order.order_number,
        "status": order.status,
        "customer_id": order.customer_id,
        "outlet_id": order.outlet_id,
        "delivery_date": _jsonable(order.delivery_date),
        "discount_pct": _jsonable(order.discount_pct),
        "credit_exception_requested": bool(order.credit_exception_requested),
        "total_amount": _jsonable(order.total_amount),
        "created_at": _jsonable(order.created_at),
        "updated_at": _jsonable(order.updated_at),
        "items": items,
    }


def build_invoice_payload(invoice: Invoice) -> dict[str, Any]:
    items = [
        {
            "id": item.pk,
            "product_id": item.product_id,
            "description": item.description,
            "quantity": int(item.quantity or 0),
            "unit_price": int(item.unit_price or 0),
            "discount_pct": _jsonable(item.discount_pct),
            "tax_rate_pct": _jsonable(item.tax_rate_pct),
            "line_total": int(item.total_amount or 0),
        }
        for item in invoice.items.select_related("product").all()
    ]
    payments = [
        {
            "id": payment.pk,
            "amount": int(payment.amount or 0),
            "payment_method": payment.payment_method,
            "payment_reference": payment.payment_reference,
            "paid_at": _jsonable(payment.paid_at),
            "source": payment.source,
            "source_connector": payment.source_connector,
            "source_event_id": payment.source_event_id or "",
        }
        for payment in invoice.payments.order_by("-paid_at", "-pk")[:20]
    ]
    return {
        "id": invoice.pk,
        "invoice_number": invoice.invoice_number,
        "source": invoice.source,
        "nature": invoice.nature,
        "original_invoice_id": invoice.original_invoice_id,
        "original_invoice_number": invoice.original_invoice.invoice_number if invoice.original_invoice_id else "",
        "status": invoice.status,
        "customer_id": invoice.customer_id,
        "order_id": invoice.order_id,
        "currency": invoice.currency,
        "due_date": _jsonable(invoice.due_date),
        "issued_at": _jsonable(invoice.issued_at),
        "subtotal_amount": int(invoice.subtotal_amount or 0),
        "discount_amount": int(invoice.discount_amount or 0),
        "tax_amount": int(invoice.tax_amount or 0),
        "total_amount": int(invoice.total_amount or 0),
        "paid_amount": int(invoice.paid_amount or 0),
        "payment_method": invoice.payment_method,
        "payment_reference": invoice.payment_reference,
        "cancellation_reason": invoice.cancellation_reason,
        "sales_owner_id": invoice.sales_owner_id,
        "fne_required": bool(invoice.fne_required),
        "fne_status": invoice.fne_status,
        "fne_reference": invoice.fne_reference,
        "created_at": _jsonable(invoice.created_at),
        "updated_at": _jsonable(invoice.updated_at),
        "payments_count": len(payments),
        "payments": payments,
        "items": items,
    }


def build_invoice_payment_payload(payment: InvoicePayment) -> dict[str, Any]:
    invoice = payment.invoice
    return {
        "id": payment.pk,
        "invoice_id": payment.invoice_id,
        "invoice_number": invoice.invoice_number if invoice else "",
        "customer_id": invoice.customer_id if invoice else None,
        "amount": int(payment.amount or 0),
        "payment_method": payment.payment_method,
        "payment_reference": payment.payment_reference,
        "paid_at": _jsonable(payment.paid_at),
        "source": payment.source,
        "source_connector": payment.source_connector,
        "source_event_id": payment.source_event_id or "",
        "recorded_by_id": payment.recorded_by_id,
        "created_at": _jsonable(payment.created_at),
        "updated_at": _jsonable(payment.updated_at),
    }


def build_inbound_payload(inbound: InboundRequest) -> dict[str, Any]:
    return {
        "id": inbound.pk,
        "kind": inbound.kind,
        "status": inbound.status,
        "priority": inbound.priority,
        "name": inbound.name,
        "company": inbound.company,
        "phone": inbound.phone,
        "email": inbound.email,
        "segment": inbound.segment,
        "stage": inbound.stage,
        "intent": inbound.intent,
        "channel_preference": inbound.channel_preference,
        "volume": inbound.volume,
        "product": inbound.product,
        "objective": inbound.objective,
        "message": inbound.message,
        "region": inbound.region,
        "preferred_time": inbound.preferred_time,
        "interests": list(inbound.interests or []),
        "consent": bool(inbound.consent),
        "first_response_due_at": _jsonable(inbound.first_response_due_at),
        "resolution_due_at": _jsonable(inbound.resolution_due_at),
        "first_response_at": _jsonable(inbound.first_response_at),
        "resolved_at": _jsonable(inbound.resolved_at),
        "assigned_to_id": inbound.assigned_to_id,
        "lead_id": inbound.lead_id,
        "created_at": _jsonable(inbound.created_at),
        "updated_at": _jsonable(inbound.updated_at),
    }


def build_idempotency_key(
    *,
    connector_code: str,
    entity_type: str,
    entity_id: int,
    event_type: str,
    version_hint: str = "",
) -> str:
    seed = f"{connector_code}|{entity_type}|{entity_id}|{event_type}|{version_hint}"
    digest = _sha_digest(seed)[:24]
    return f"{entity_type}:{entity_id}:{event_type}:{digest}"[:180]


def _serialize_connector_filter(
    *,
    integration_types: list[str] | tuple[str, ...] | None = None,
    direction: str | None = None,
    connector_codes: list[str] | tuple[str, ...] | None = None,
):
    queryset = EnterpriseConnector.objects.filter(active=True)
    if integration_types:
        queryset = queryset.filter(integration_type__in=list(integration_types))
    if direction == "outbound":
        queryset = queryset.filter(
            direction__in=[
                EnterpriseIntegrationDirectionChoices.OUTBOUND,
                EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
            ]
        )
    elif direction == "inbound":
        queryset = queryset.filter(
            direction__in=[
                EnterpriseIntegrationDirectionChoices.INBOUND,
                EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
            ]
        )
    if connector_codes:
        queryset = queryset.filter(code__in=[code.strip() for code in connector_codes if code.strip()])
    return queryset.order_by("code")


def enqueue_outbox_event(
    *,
    connector: EnterpriseConnector,
    entity_type: str,
    entity_id: int,
    event_type: str,
    payload: dict[str, Any],
    idempotency_key: str,
    request_id: str = "",
    correlation_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> tuple[EnterpriseOutboxEvent, bool]:
    payload = _jsonable(payload) or {}
    defaults = {
        "payload": payload,
        "status": EnterpriseOutboxStatusChoices.PENDING,
        "request_id": (request_id or "")[:64],
        "correlation_id": (correlation_id or "")[:64],
        "metadata": _jsonable(metadata) or {},
    }
    try:
        event, created = EnterpriseOutboxEvent.objects.get_or_create(
            connector=connector,
            idempotency_key=idempotency_key,
            defaults={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "event_type": event_type,
                **defaults,
            },
        )
    except IntegrityError:
        event = EnterpriseOutboxEvent.objects.get(connector=connector, idempotency_key=idempotency_key)
        created = False
    return event, created


def _latest_mapping_set(connector: EnterpriseConnector, entity_type: str) -> list[EnterpriseFieldMapping]:
    mappings = list(
        EnterpriseFieldMapping.objects.filter(
            connector=connector,
            entity_type=entity_type,
            active=True,
        ).order_by("-version", "source_field")
    )
    if not mappings:
        return []
    target_version = mappings[0].version
    return [mapping for mapping in mappings if mapping.version == target_version]


def _apply_transform_rule(value: Any, transform_rule: str) -> Any:
    rule = (transform_rule or "").strip().lower()
    if not rule:
        return value
    if value is None:
        return None
    if rule == "lower":
        return str(value).lower()
    if rule == "upper":
        return str(value).upper()
    if rule == "strip":
        return str(value).strip()
    if rule == "int":
        return int(value)
    if rule == "float":
        return float(value)
    if rule == "bool":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}
    if rule == "iso_datetime":
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
    return value


def apply_field_mappings(connector: EnterpriseConnector, *, entity_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    mapping_set = _latest_mapping_set(connector, entity_type)
    if not mapping_set:
        return payload

    transformed: dict[str, Any] = {}
    for mapping in mapping_set:
        value = payload.get(mapping.source_field, mapping.default_value or None)
        value = _apply_transform_rule(value, mapping.transform_rule)
        if mapping.is_required and (value is None or value == ""):
            raise IntegrationPermanentError(
                f"Field mapping required value missing: {mapping.source_field} -> {mapping.target_field}"
            )
        transformed[mapping.target_field] = value
    return transformed


def emit_entity_outbox_events(
    *,
    entity_type: str,
    entity_id: int,
    event_type: str,
    payload: dict[str, Any],
    integration_types: list[str] | tuple[str, ...],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if is_integration_runtime_active():
        return {"selected": 0, "created": 0, "existing": 0}

    request_id = _current_request_id()
    correlation_id = _current_correlation_id(request_id=request_id)
    version_hint = str(payload.get("updated_at") or payload.get("created_at") or "")

    connectors = _serialize_connector_filter(
        integration_types=integration_types,
        direction="outbound",
    )
    metrics = {"selected": 0, "created": 0, "existing": 0}

    for connector in connectors:
        metrics["selected"] += 1
        idempotency_key = build_idempotency_key(
            connector_code=connector.code,
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            version_hint=version_hint,
        )
        _, created = enqueue_outbox_event(
            connector=connector,
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            payload=payload,
            idempotency_key=idempotency_key,
            request_id=request_id,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        metrics["created" if created else "existing"] += 1
    return metrics


def emit_order_outbox_event(order: Order, *, created: bool) -> dict[str, Any]:
    payload = build_order_payload(order)
    event_type = "order.created" if created else "order.updated"
    return emit_entity_outbox_events(
        entity_type="order",
        entity_id=order.pk,
        event_type=event_type,
        payload=payload,
        integration_types=(
            EnterpriseIntegrationTypeChoices.ERP_COMPTA,
            EnterpriseIntegrationTypeChoices.LOGISTICS_STOCK,
            EnterpriseIntegrationTypeChoices.BI_ANALYTICS,
        ),
    )


def emit_invoice_outbox_event(invoice: Invoice, *, created: bool) -> dict[str, Any]:
    payload = build_invoice_payload(invoice)
    event_type = "invoice.created" if created else "invoice.updated"
    integration_types = [
        EnterpriseIntegrationTypeChoices.ERP_COMPTA,
        EnterpriseIntegrationTypeChoices.BI_ANALYTICS,
    ]
    if invoice.status in {
        InvoiceStatusChoices.EMISE,
        InvoiceStatusChoices.PARTIELLEMENT_PAYEE,
        InvoiceStatusChoices.PAYEE,
    } and bool(invoice.fne_required):
        integration_types.append(EnterpriseIntegrationTypeChoices.FNE_DGI)
    return emit_entity_outbox_events(
        entity_type="invoice",
        entity_id=invoice.pk,
        event_type=event_type,
        payload=payload,
        integration_types=tuple(integration_types),
    )


def emit_invoice_payment_outbox_event(payment: InvoicePayment, *, event_type: str = "") -> dict[str, Any]:
    payload = build_invoice_payment_payload(payment)
    resolved_event_type = event_type or "invoice_payment.updated"
    return emit_entity_outbox_events(
        entity_type="invoice_payment",
        entity_id=payment.pk,
        event_type=resolved_event_type,
        payload=payload,
        integration_types=(
            EnterpriseIntegrationTypeChoices.ERP_COMPTA,
            EnterpriseIntegrationTypeChoices.BI_ANALYTICS,
        ),
    )


def emit_inbound_outbox_event(inbound: InboundRequest, *, created: bool) -> dict[str, Any]:
    payload = build_inbound_payload(inbound)
    event_type = "inbound.created" if created else "inbound.updated"
    return emit_entity_outbox_events(
        entity_type="inbound",
        entity_id=inbound.pk,
        event_type=event_type,
        payload=payload,
        integration_types=(
            EnterpriseIntegrationTypeChoices.TELEPHONY_WHATSAPP,
            EnterpriseIntegrationTypeChoices.BI_ANALYTICS,
        ),
    )


def _resolve_auth_secret(connector: EnterpriseConnector) -> str:
    key_name = (connector.auth_secret_id or "").strip()
    if not key_name:
        return ""
    return os.getenv(key_name, "").strip()


def _build_http_headers(
    *,
    connector: EnterpriseConnector,
    payload_bytes: bytes,
    idempotency_key: str,
    correlation_id: str,
) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "X-Idempotency-Key": idempotency_key,
    }
    if correlation_id:
        headers["X-Correlation-ID"] = correlation_id

    if connector.auth_mode == EnterpriseConnectorAuthModeChoices.NONE:
        return headers

    secret = _resolve_auth_secret(connector)
    if not secret:
        raise IntegrationPermanentError(f"Missing auth secret env var for connector `{connector.code}`.")

    if connector.auth_mode == EnterpriseConnectorAuthModeChoices.API_KEY:
        header_name = str(connector.metadata.get("api_key_header") or "X-API-Key")
        headers[header_name] = secret
        return headers

    if connector.auth_mode == EnterpriseConnectorAuthModeChoices.BEARER:
        headers["Authorization"] = f"Bearer {secret}"
        return headers

    if connector.auth_mode == EnterpriseConnectorAuthModeChoices.HMAC:
        signature = hmac.new(secret.encode("utf-8"), payload_bytes, digestmod=hashlib.sha256).hexdigest()
        header_name = str(connector.metadata.get("hmac_header") or "X-Signature")
        headers[header_name] = signature
        return headers

    return headers


def _deliver_mock_outbox_event(event: EnterpriseOutboxEvent, payload: dict[str, Any]) -> dict[str, Any]:
    forced = str(payload.get("_force_result") or "").strip().lower()
    if forced == "transient":
        raise IntegrationTransientError("Forced transient error from mock connector.")
    if forced == "permanent":
        raise IntegrationPermanentError("Forced permanent error from mock connector.")

    external_reference = f"mock-{event.connector.code}-{event.pk}-{event.attempt_count}"
    return {
        "status_code": 200,
        "external_reference": external_reference,
        "response": {"ok": True, "reference": external_reference},
    }


def _deliver_http_outbox_event(event: EnterpriseOutboxEvent, payload: dict[str, Any]) -> dict[str, Any]:
    connector = event.connector
    base_url = (connector.base_url or "").strip()
    if not base_url:
        raise IntegrationPermanentError(f"Connector `{connector.code}` has no base_url configured.")

    outbox_path = str(connector.metadata.get("outbox_path") or "/api/events")
    final_url = urllib_parse.urljoin(base_url if base_url.endswith("/") else f"{base_url}/", outbox_path.lstrip("/"))
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = _build_http_headers(
        connector=connector,
        payload_bytes=payload_bytes,
        idempotency_key=event.idempotency_key,
        correlation_id=event.correlation_id or event.request_id,
    )
    req = urllib_request.Request(url=final_url, data=payload_bytes, headers=headers, method="POST")

    try:
        with urllib_request.urlopen(req, timeout=max(1, int(connector.timeout_seconds or 10))) as resp:
            status_code = int(resp.getcode() or 200)
            body = resp.read().decode("utf-8", errors="replace")
    except urllib_error.HTTPError as exc:
        status_code = int(exc.code or 500)
        body = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else str(exc)
        if 400 <= status_code < 500 and status_code != 429:
            raise IntegrationPermanentError(f"HTTP {status_code}: {body}") from exc
        raise IntegrationTransientError(f"HTTP {status_code}: {body}") from exc
    except (urllib_error.URLError, TimeoutError) as exc:
        raise IntegrationTransientError(str(exc)) from exc

    if 200 <= status_code < 300:
        return {"status_code": status_code, "external_reference": "", "response": body}
    if 400 <= status_code < 500 and status_code != 429:
        raise IntegrationPermanentError(f"HTTP {status_code}: {body}")
    raise IntegrationTransientError(f"HTTP {status_code}: {body}")


def _effective_retry_limit(connector: EnterpriseConnector) -> int:
    candidates = [int(connector.max_retries or 0), int(connector.dlq_after_attempts or 0)]
    positive = [value for value in candidates if value > 0]
    return min(positive) if positive else 1


def _next_retry_at(connector: EnterpriseConnector, *, attempt_count: int, now=None):
    now = now or timezone.now()
    backoff = max(1, int(connector.retry_backoff_seconds or 1))
    delay_seconds = min(_MAX_BACKOFF_SECONDS, backoff * (2 ** max(0, attempt_count - 1)))
    return now + timedelta(seconds=delay_seconds)


def _dead_letter_outbox(event: EnterpriseOutboxEvent, *, reason: str):
    EnterpriseDeadLetterEvent.objects.create(
        connector=event.connector,
        direction=EnterpriseDeadLetterDirectionChoices.OUTBOX,
        event_type=event.event_type,
        payload=_jsonable(event.payload) or {},
        reason=reason[:2000],
        attempt_count=int(event.attempt_count or 0),
        related_outbox=event,
        metadata={"idempotency_key": event.idempotency_key},
    )


def _dead_letter_inbox(event: EnterpriseInboxEvent, *, reason: str):
    EnterpriseDeadLetterEvent.objects.create(
        connector=event.connector,
        direction=EnterpriseDeadLetterDirectionChoices.INBOX,
        event_type=event.event_type,
        payload=_jsonable(event.payload) or {},
        reason=reason[:2000],
        attempt_count=int(event.attempt_count or 0),
        related_inbox=event,
        metadata={"external_event_id": event.external_event_id},
    )


def _outbox_deliver(event: EnterpriseOutboxEvent, payload: dict[str, Any]) -> dict[str, Any]:
    transport = event.connector.transport
    if transport == EnterpriseConnectorTransportChoices.MOCK:
        return _deliver_mock_outbox_event(event, payload)
    if transport == EnterpriseConnectorTransportChoices.HTTP:
        return _deliver_http_outbox_event(event, payload)
    raise IntegrationPermanentError(f"Unsupported transport `{transport}` for connector `{event.connector.code}`.")


def process_outbox_events(
    *,
    limit: int = 100,
    connector_codes: list[str] | tuple[str, ...] | None = None,
    now=None,
) -> dict[str, int]:
    now = now or timezone.now()
    qs = EnterpriseOutboxEvent.objects.select_related("connector").filter(
        status__in=[EnterpriseOutboxStatusChoices.PENDING, EnterpriseOutboxStatusChoices.FAILED],
        connector__active=True,
        connector__direction__in=[
            EnterpriseIntegrationDirectionChoices.OUTBOUND,
            EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
        ],
    )
    qs = qs.filter(Q(next_retry_at__isnull=True) | Q(next_retry_at__lte=now))
    if connector_codes:
        qs = qs.filter(connector__code__in=[code.strip() for code in connector_codes if code.strip()])
    events = list(qs.order_by("created_at")[: max(1, int(limit or 1))])

    metrics = {
        "selected": len(events),
        "processed": 0,
        "delivered": 0,
        "failed": 0,
        "retried": 0,
        "dead": 0,
        "errors": 0,
    }

    for event in events:
        metrics["processed"] += 1
        event.attempt_count = int(event.attempt_count or 0) + 1
        event.status = EnterpriseOutboxStatusChoices.PROCESSING
        event.next_retry_at = None
        event.save(update_fields=["attempt_count", "status", "next_retry_at", "updated_at"])

        try:
            mapped_payload = apply_field_mappings(
                event.connector,
                entity_type=event.entity_type,
                payload=_jsonable(event.payload) or {},
            )
            response_payload = _outbox_deliver(event, mapped_payload)
        except IntegrationPermanentError as exc:
            event.status = EnterpriseOutboxStatusChoices.DEAD
            event.last_error = str(exc)[:2000]
            event.next_retry_at = None
            event.save(update_fields=["status", "last_error", "next_retry_at", "updated_at"])
            _dead_letter_outbox(event, reason=str(exc))
            metrics["dead"] += 1
            integration_logger.error(
                "outbox_dead connector=%s event=%s reason=%s",
                event.connector.code,
                event.pk,
                str(exc),
            )
            continue
        except IntegrationTransientError as exc:
            retry_limit = _effective_retry_limit(event.connector)
            if event.attempt_count >= retry_limit:
                event.status = EnterpriseOutboxStatusChoices.DEAD
                event.last_error = str(exc)[:2000]
                event.next_retry_at = None
                event.save(update_fields=["status", "last_error", "next_retry_at", "updated_at"])
                _dead_letter_outbox(event, reason=str(exc))
                metrics["dead"] += 1
                integration_logger.error(
                    "outbox_dead connector=%s event=%s attempts=%s reason=%s",
                    event.connector.code,
                    event.pk,
                    event.attempt_count,
                    str(exc),
                )
            else:
                event.status = EnterpriseOutboxStatusChoices.FAILED
                event.last_error = str(exc)[:2000]
                event.next_retry_at = _next_retry_at(event.connector, attempt_count=event.attempt_count, now=now)
                event.save(update_fields=["status", "last_error", "next_retry_at", "updated_at"])
                metrics["failed"] += 1
                metrics["retried"] += 1
            continue
        except Exception as exc:  # pragma: no cover - defensive path
            metrics["errors"] += 1
            retry_limit = _effective_retry_limit(event.connector)
            if event.attempt_count >= retry_limit:
                event.status = EnterpriseOutboxStatusChoices.DEAD
                event.last_error = str(exc)[:2000]
                event.next_retry_at = None
                event.save(update_fields=["status", "last_error", "next_retry_at", "updated_at"])
                _dead_letter_outbox(event, reason=str(exc))
                metrics["dead"] += 1
            else:
                event.status = EnterpriseOutboxStatusChoices.FAILED
                event.last_error = str(exc)[:2000]
                event.next_retry_at = _next_retry_at(event.connector, attempt_count=event.attempt_count, now=now)
                event.save(update_fields=["status", "last_error", "next_retry_at", "updated_at"])
                metrics["failed"] += 1
                metrics["retried"] += 1
            integration_logger.exception("outbox_unexpected_error event=%s", event.pk)
            continue

        metadata = dict(event.metadata or {})
        metadata["last_response"] = _jsonable(response_payload)
        event.status = EnterpriseOutboxStatusChoices.DELIVERED
        event.delivered_at = now
        event.last_error = ""
        event.external_reference = str(response_payload.get("external_reference") or "")[:255]
        event.metadata = metadata
        event.save(
            update_fields=[
                "status",
                "delivered_at",
                "last_error",
                "external_reference",
                "metadata",
                "updated_at",
            ]
        )
        metrics["delivered"] += 1

    return metrics


def enqueue_inbox_event(
    *,
    connector: EnterpriseConnector,
    external_event_id: str,
    event_type: str,
    payload: dict[str, Any],
    dedup_key: str = "",
    correlation_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> tuple[EnterpriseInboxEvent, bool]:
    defaults = {
        "event_type": event_type,
        "payload": _jsonable(payload) or {},
        "status": EnterpriseInboxStatusChoices.PENDING,
        "dedup_key": dedup_key[:180],
        "correlation_id": correlation_id[:64],
        "metadata": _jsonable(metadata) or {},
    }
    try:
        event, created = EnterpriseInboxEvent.objects.get_or_create(
            connector=connector,
            external_event_id=external_event_id[:180],
            defaults=defaults,
        )
    except IntegrityError:
        event = EnterpriseInboxEvent.objects.get(
            connector=connector,
            external_event_id=external_event_id[:180],
        )
        created = False
    return event, created


def ingest_inbox_event(
    *,
    connector_code: str,
    external_event_id: str,
    event_type: str,
    payload: dict[str, Any],
    dedup_key: str = "",
    correlation_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> tuple[EnterpriseInboxEvent, bool]:
    connector = EnterpriseConnector.objects.filter(code=connector_code).first()
    if connector is None:
        raise IntegrationPermanentError(f"Connector `{connector_code}` introuvable.")
    if not external_event_id:
        raise IntegrationPermanentError("external_event_id is required.")
    if not event_type:
        raise IntegrationPermanentError("event_type is required.")
    return enqueue_inbox_event(
        connector=connector,
        external_event_id=external_event_id,
        event_type=event_type,
        payload=payload,
        dedup_key=dedup_key,
        correlation_id=correlation_id,
        metadata=metadata,
    )


def _map_external_order_status(value: str) -> str:
    status_map = {
        "draft": OrderStatusChoices.BROUILLON,
        "quote": OrderStatusChoices.DEVIS,
        "quotation": OrderStatusChoices.DEVIS,
        "confirmed": OrderStatusChoices.CONFIRME,
        "delivered": OrderStatusChoices.LIVRE,
        "cancelled": OrderStatusChoices.ANNULE,
        "canceled": OrderStatusChoices.ANNULE,
    }
    return status_map.get((value or "").strip().lower(), "")


def _resolve_inbox_payload(event: EnterpriseInboxEvent) -> dict[str, Any]:
    payload = _jsonable(event.payload) or {}
    mapped = apply_field_mappings(
        event.connector,
        entity_type=f"inbox:{event.event_type}",
        payload=payload,
    )
    if mapped is payload:
        mapped = apply_field_mappings(
            event.connector,
            entity_type="inbox",
            payload=payload,
        )
    return _jsonable(mapped) or {}


def _handle_telephony_inbox_event(event: EnterpriseInboxEvent) -> dict[str, Any]:
    payload = _resolve_inbox_payload(event)
    phone = str(payload.get("phone") or payload.get("from") or "").strip()[:40]
    email = str(payload.get("email") or "").strip()[:254]
    name = str(payload.get("name") or payload.get("contact_name") or "").strip()[:255]
    message = str(payload.get("message") or payload.get("body") or "").strip()[:2000]
    company = str(payload.get("company") or "").strip()[:255]
    region = str(payload.get("region") or "").strip()[:120]
    channel_hint = str(payload.get("channel") or event.event_type).lower()

    if not phone and not email:
        raise IntegrationPermanentError("Telephony/WhatsApp inbox event missing phone/email.")

    channel = ChannelChoices.WHATSAPP if "what" in channel_hint else ChannelChoices.APPEL
    inbound = InboundRequest.objects.create(
        kind=InboundKindChoices.CONTACT,
        priority=InboundPriorityChoices.NORMAL,
        name=name,
        company=company,
        phone=phone,
        email=email,
        channel_preference=channel,
        message=message,
        region=region,
        raw_data={
            "source": "enterprise_connector",
            "connector_code": event.connector.code,
            "external_event_id": event.external_event_id,
            "event_type": event.event_type,
            "payload": payload,
        },
    )
    return {"action": "inbound_created", "inbound_id": inbound.pk}


def _handle_order_sync_inbox_event(event: EnterpriseInboxEvent) -> dict[str, Any]:
    payload = _resolve_inbox_payload(event)
    order_id = payload.get("order_id")
    order_number = str(payload.get("order_number") or "").strip()

    queryset = Order.objects.all()
    if order_id:
        queryset = queryset.filter(pk=order_id)
    elif order_number:
        queryset = queryset.filter(order_number=order_number)
    else:
        raise IntegrationPermanentError("Order sync event missing `order_id` or `order_number`.")

    order = queryset.first()
    if order is None:
        raise IntegrationPermanentError("Order not found for enterprise inbound sync event.")

    external_status = str(payload.get("status") or payload.get("order_status") or "").strip()
    mapped_status = _map_external_order_status(external_status)
    if mapped_status and mapped_status != order.status:
        blockers = validate_order_fne_delivery_gate(order, target_status=mapped_status)
        if blockers:
            raise IntegrationPermanentError(blockers[0])
        order.status = mapped_status
        order.save(update_fields=["status", "updated_at"])

    return {"action": "order_synced", "order_id": order.pk, "order_status": order.status}


def _map_external_payment_method(value: str) -> str:
    normalized = (value or "").strip().lower()
    mapping = {
        "cash": InvoicePaymentMethodChoices.ESPECES,
        "especes": InvoicePaymentMethodChoices.ESPECES,
        "espèces": InvoicePaymentMethodChoices.ESPECES,
        "mobile_money": InvoicePaymentMethodChoices.MOBILE_MONEY,
        "mobilemoney": InvoicePaymentMethodChoices.MOBILE_MONEY,
        "om": InvoicePaymentMethodChoices.MOBILE_MONEY,
        "momo": InvoicePaymentMethodChoices.MOBILE_MONEY,
        "virement": InvoicePaymentMethodChoices.VIREMENT,
        "bank_transfer": InvoicePaymentMethodChoices.VIREMENT,
        "wire": InvoicePaymentMethodChoices.VIREMENT,
        "cheque": InvoicePaymentMethodChoices.CHEQUE,
        "chèque": InvoicePaymentMethodChoices.CHEQUE,
        "credit": InvoicePaymentMethodChoices.CREDIT,
    }
    return mapping.get(normalized, InvoicePaymentMethodChoices.NON_RENSEIGNE)


def _is_payment_sync_event(event: EnterpriseInboxEvent) -> bool:
    event_type = str(event.event_type or "").strip().lower()
    if "payment" in event_type or "paiement" in event_type:
        return True
    payload = _jsonable(event.payload) or {}
    if payload.get("payment_id") or payload.get("transaction_id"):
        return bool(payload.get("invoice_id") or payload.get("invoice_number"))
    if payload.get("amount") is not None and (payload.get("invoice_id") or payload.get("invoice_number")):
        return True
    return False


def _handle_invoice_payment_inbox_event(event: EnterpriseInboxEvent) -> dict[str, Any]:
    payload = _resolve_inbox_payload(event)
    invoice_id = payload.get("invoice_id")
    invoice_number = str(payload.get("invoice_number") or "").strip()

    queryset = Invoice.objects.all()
    if invoice_id:
        queryset = queryset.filter(pk=invoice_id)
    elif invoice_number:
        queryset = queryset.filter(invoice_number=invoice_number)
    else:
        raise IntegrationPermanentError("Payment sync event missing `invoice_id` or `invoice_number`.")

    invoice = queryset.first()
    if invoice is None:
        raise IntegrationPermanentError("Invoice not found for payment sync event.")

    amount_raw = payload.get("amount", payload.get("payment_amount"))
    try:
        amount = int(float(amount_raw))
    except (TypeError, ValueError):
        raise IntegrationPermanentError("Payment sync event has invalid `amount`.") from None
    if amount <= 0:
        raise IntegrationPermanentError("Payment sync event has non-positive `amount`.")

    source_event_id = str(
        payload.get("payment_id")
        or payload.get("transaction_id")
        or payload.get("source_event_id")
        or event.external_event_id
        or ""
    ).strip()[:180]
    if source_event_id:
        existing = InvoicePayment.objects.filter(
            source=InvoicePaymentSourceChoices.INTEGRATION,
            source_connector=event.connector.code,
            source_event_id=source_event_id,
        ).first()
        if existing is not None:
            return {
                "action": "invoice_payment_ignored_duplicate",
                "invoice_id": invoice.pk,
                "payment_id": existing.pk,
            }

    issues = validate_invoice_payment_prerequisites(invoice, amount=amount)
    if issues:
        raise IntegrationPermanentError(issues[0])

    paid_at = timezone.now()
    paid_at_raw = payload.get("paid_at")
    if isinstance(paid_at_raw, datetime):
        paid_at = paid_at_raw
    elif paid_at_raw:
        parsed_paid_at = parse_datetime(str(paid_at_raw))
        if parsed_paid_at is not None:
            if timezone.is_naive(parsed_paid_at):
                parsed_paid_at = timezone.make_aware(parsed_paid_at, timezone.get_current_timezone())
            paid_at = parsed_paid_at

    payment = InvoicePayment.objects.create(
        invoice=invoice,
        amount=amount,
        payment_method=_map_external_payment_method(str(payload.get("payment_method") or payload.get("method") or "")),
        payment_reference=str(
            payload.get("payment_reference")
            or payload.get("reference")
            or payload.get("transaction_id")
            or ""
        )[:255],
        paid_at=paid_at,
        source=InvoicePaymentSourceChoices.INTEGRATION,
        source_connector=event.connector.code,
        source_event_id=source_event_id or None,
        notes=str(payload.get("notes") or "Paiement enregistré via connecteur entreprise.")[:2000],
    )
    return {"action": "invoice_payment_synced", "invoice_id": invoice.pk, "payment_id": payment.pk}


def _map_external_fne_status(value: str) -> str:
    normalized = (value or "").strip().lower()
    mapping = {
        "pending": InvoiceFNEStatusChoices.PENDING,
        "processing": InvoiceFNEStatusChoices.PENDING,
        "certified": InvoiceFNEStatusChoices.CERTIFIED,
        "approved": InvoiceFNEStatusChoices.CERTIFIED,
        "ok": InvoiceFNEStatusChoices.CERTIFIED,
        "rejected": InvoiceFNEStatusChoices.REJECTED,
        "error": InvoiceFNEStatusChoices.REJECTED,
        "failed": InvoiceFNEStatusChoices.REJECTED,
    }
    return mapping.get(normalized, "")


def _handle_fne_dgi_inbox_event(event: EnterpriseInboxEvent) -> dict[str, Any]:
    payload = _resolve_inbox_payload(event)
    invoice_id = payload.get("invoice_id")
    invoice_number = str(payload.get("invoice_number") or "").strip()

    queryset = Invoice.objects.all()
    if invoice_id:
        queryset = queryset.filter(pk=invoice_id)
    elif invoice_number:
        queryset = queryset.filter(invoice_number=invoice_number)
    else:
        raise IntegrationPermanentError("FNE inbox event missing `invoice_id` or `invoice_number`.")

    invoice = queryset.first()
    if invoice is None:
        raise IntegrationPermanentError("Invoice not found for FNE inbound sync event.")

    external_status = str(payload.get("fne_status") or payload.get("status") or "").strip()
    mapped_status = _map_external_fne_status(external_status)
    updates: dict[str, Any] = {}
    if mapped_status and mapped_status != invoice.fne_status:
        updates["fne_status"] = mapped_status
        if mapped_status == InvoiceFNEStatusChoices.CERTIFIED:
            updates["fne_certified_at"] = timezone.now()
            updates["fne_last_error"] = ""
    if payload.get("fne_reference"):
        updates["fne_reference"] = str(payload.get("fne_reference"))[:255]
    if payload.get("error_message"):
        updates["fne_last_error"] = str(payload.get("error_message"))[:2000]
    if payload.get("error_code"):
        current_error = str(updates.get("fne_last_error") or invoice.fne_last_error or "")
        updates["fne_last_error"] = (f"[{payload.get('error_code')}] {current_error}".strip())[:2000]

    if updates:
        Invoice.objects.filter(pk=invoice.pk).update(**updates)
        for key, value in updates.items():
            setattr(invoice, key, value)

    return {"action": "invoice_fne_synced", "invoice_id": invoice.pk, "fne_status": invoice.fne_status}


def _route_inbox_event(event: EnterpriseInboxEvent) -> dict[str, Any]:
    integration_type = event.connector.integration_type
    if integration_type == EnterpriseIntegrationTypeChoices.TELEPHONY_WHATSAPP:
        return _handle_telephony_inbox_event(event)
    if integration_type in {
        EnterpriseIntegrationTypeChoices.ERP_COMPTA,
        EnterpriseIntegrationTypeChoices.LOGISTICS_STOCK,
    }:
        if _is_payment_sync_event(event):
            return _handle_invoice_payment_inbox_event(event)
        return _handle_order_sync_inbox_event(event)
    if integration_type == EnterpriseIntegrationTypeChoices.FNE_DGI:
        return _handle_fne_dgi_inbox_event(event)
    return {"action": "ignored", "reason": "integration_type_not_implemented"}


def process_inbox_events(
    *,
    limit: int = 100,
    connector_codes: list[str] | tuple[str, ...] | None = None,
    now=None,
) -> dict[str, int]:
    now = now or timezone.now()
    qs = EnterpriseInboxEvent.objects.select_related("connector").filter(
        status__in=[EnterpriseInboxStatusChoices.PENDING, EnterpriseInboxStatusChoices.FAILED],
        connector__active=True,
    )
    qs = qs.filter(
        connector__direction__in=[
            EnterpriseIntegrationDirectionChoices.INBOUND,
            EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
        ]
    )
    if connector_codes:
        qs = qs.filter(connector__code__in=[code.strip() for code in connector_codes if code.strip()])
    events = list(qs.order_by("created_at")[: max(1, int(limit or 1))])

    metrics = {
        "selected": len(events),
        "processed": 0,
        "handled": 0,
        "ignored": 0,
        "failed": 0,
        "dead": 0,
        "errors": 0,
    }

    for event in events:
        metrics["processed"] += 1
        event.attempt_count = int(event.attempt_count or 0) + 1

        if event.dedup_key:
            duplicate_exists = EnterpriseInboxEvent.objects.filter(
                connector=event.connector,
                dedup_key=event.dedup_key,
                status__in=[EnterpriseInboxStatusChoices.PROCESSED, EnterpriseInboxStatusChoices.IGNORED],
            ).exclude(pk=event.pk).exists()
            if duplicate_exists:
                event.status = EnterpriseInboxStatusChoices.IGNORED
                event.processed_at = now
                event.last_error = ""
                event.save(update_fields=["attempt_count", "status", "processed_at", "last_error", "updated_at"])
                metrics["ignored"] += 1
                continue

        try:
            with integration_runtime_context():
                outcome = _route_inbox_event(event)
        except IntegrationPermanentError as exc:
            event.status = EnterpriseInboxStatusChoices.DEAD
            event.last_error = str(exc)[:2000]
            event.save(update_fields=["attempt_count", "status", "last_error", "updated_at"])
            _dead_letter_inbox(event, reason=str(exc))
            metrics["dead"] += 1
            continue
        except IntegrationTransientError as exc:
            retry_limit = _effective_retry_limit(event.connector)
            if event.attempt_count >= retry_limit:
                event.status = EnterpriseInboxStatusChoices.DEAD
                event.last_error = str(exc)[:2000]
                event.save(update_fields=["attempt_count", "status", "last_error", "updated_at"])
                _dead_letter_inbox(event, reason=str(exc))
                metrics["dead"] += 1
            else:
                event.status = EnterpriseInboxStatusChoices.FAILED
                event.last_error = str(exc)[:2000]
                event.save(update_fields=["attempt_count", "status", "last_error", "updated_at"])
                metrics["failed"] += 1
            continue
        except Exception as exc:  # pragma: no cover - defensive path
            metrics["errors"] += 1
            retry_limit = _effective_retry_limit(event.connector)
            if event.attempt_count >= retry_limit:
                event.status = EnterpriseInboxStatusChoices.DEAD
                event.last_error = str(exc)[:2000]
                event.save(update_fields=["attempt_count", "status", "last_error", "updated_at"])
                _dead_letter_inbox(event, reason=str(exc))
                metrics["dead"] += 1
            else:
                event.status = EnterpriseInboxStatusChoices.FAILED
                event.last_error = str(exc)[:2000]
                event.save(update_fields=["attempt_count", "status", "last_error", "updated_at"])
                metrics["failed"] += 1
            integration_logger.exception("inbox_unexpected_error event=%s", event.pk)
            continue

        metadata = dict(event.metadata or {})
        metadata["outcome"] = _jsonable(outcome)
        action = str((outcome or {}).get("action") or "").strip().lower()
        if action == "ignored":
            event.status = EnterpriseInboxStatusChoices.IGNORED
            metrics["ignored"] += 1
        else:
            event.status = EnterpriseInboxStatusChoices.PROCESSED
            metrics["handled"] += 1
        event.processed_at = now
        event.last_error = ""
        event.metadata = metadata
        event.save(update_fields=["attempt_count", "status", "processed_at", "last_error", "metadata", "updated_at"])

    return metrics
