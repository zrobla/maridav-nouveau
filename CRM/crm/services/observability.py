from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db.models import ExpressionWrapper, F, IntegerField, Sum
from django.utils import timezone

from crm.models import (
    DataQualityIssue,
    DataQualitySeverityChoices,
    DataQualityStatusChoices,
    EscalationLevelChoices,
    EscalationStatusChoices,
    Invoice,
    InvoiceFNEStatusChoices,
    InvoiceStatusChoices,
    SlaEscalation,
)

_CACHE_PREFIX = "obs:api"
_LATENCY_BUCKETS_MS = [50, 100, 200, 500, 1000, 2000, 5000]
_LATENCY_BUCKET_KEYS = [f"le_{value}" for value in _LATENCY_BUCKETS_MS] + ["gt_5000"]


def _cache_ttl_seconds() -> int:
    return int(getattr(settings, "OBS_METRICS_CACHE_TTL_SECONDS", 1800))


def _window_minutes_default() -> int:
    return int(getattr(settings, "OBS_METRICS_WINDOW_MINUTES", 5))


def _minute_bucket(now) -> str:
    return now.strftime("%Y%m%d%H%M")


def _minute_buckets(window_minutes: int, now=None) -> list[str]:
    now = now or timezone.now()
    return [_minute_bucket(now - timedelta(minutes=offset)) for offset in range(window_minutes - 1, -1, -1)]


def _cache_incr(key: str, delta: int = 1, *, timeout: int | None = None):
    timeout = timeout or _cache_ttl_seconds()
    cache.add(key, 0, timeout=timeout)
    try:
        cache.incr(key, delta)
    except ValueError:
        cache.set(key, delta, timeout=timeout)


def _cache_get_int(key: str) -> int:
    value = cache.get(key, 0)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _latency_bucket_key(duration_ms: float) -> str:
    for boundary in _LATENCY_BUCKETS_MS:
        if duration_ms <= boundary:
            return f"le_{boundary}"
    return "gt_5000"


def _histogram_key(base_key: str, bucket_key: str) -> str:
    return f"{base_key}:latency_hist:{bucket_key}"


def _estimate_p95_ms(histogram: dict[str, int], requests: int) -> float:
    if requests <= 0:
        return 0.0
    threshold = requests * 0.95
    cumulative = 0
    for bucket_key in _LATENCY_BUCKET_KEYS:
        cumulative += int(histogram.get(bucket_key, 0))
        if cumulative >= threshold:
            if bucket_key.startswith("le_"):
                return float(bucket_key.replace("le_", ""))
            return float(_LATENCY_BUCKETS_MS[-1])
    return float(_LATENCY_BUCKETS_MS[-1])


def record_api_request_sample(*, status_code: int, duration_ms: float, now=None):
    now = now or timezone.now()
    base_key = f"{_CACHE_PREFIX}:{_minute_bucket(now)}"
    ttl = _cache_ttl_seconds()

    _cache_incr(f"{base_key}:requests", timeout=ttl)
    _cache_incr(f"{base_key}:latency_sum_ms", delta=int(round(max(duration_ms, 0))), timeout=ttl)

    if 400 <= int(status_code) < 500:
        _cache_incr(f"{base_key}:status_4xx", timeout=ttl)
    elif int(status_code) >= 500:
        _cache_incr(f"{base_key}:status_5xx", timeout=ttl)

    bucket_key = _latency_bucket_key(duration_ms)
    _cache_incr(_histogram_key(base_key, bucket_key), timeout=ttl)


def get_api_window_metrics(*, window_minutes: int | None = None, now=None) -> dict[str, Any]:
    now = now or timezone.now()
    window_minutes = int(window_minutes or _window_minutes_default())

    requests = 0
    status_4xx = 0
    status_5xx = 0
    latency_sum_ms = 0
    histogram = {key: 0 for key in _LATENCY_BUCKET_KEYS}

    for bucket in _minute_buckets(window_minutes, now=now):
        base_key = f"{_CACHE_PREFIX}:{bucket}"
        requests += _cache_get_int(f"{base_key}:requests")
        status_4xx += _cache_get_int(f"{base_key}:status_4xx")
        status_5xx += _cache_get_int(f"{base_key}:status_5xx")
        latency_sum_ms += _cache_get_int(f"{base_key}:latency_sum_ms")
        for bucket_key in _LATENCY_BUCKET_KEYS:
            histogram[bucket_key] += _cache_get_int(_histogram_key(base_key, bucket_key))

    latency_avg_ms = round((latency_sum_ms / requests), 2) if requests else 0.0
    rate_4xx_pct = round((status_4xx / requests) * 100, 2) if requests else 0.0
    rate_5xx_pct = round((status_5xx / requests) * 100, 2) if requests else 0.0
    latency_p95_ms = _estimate_p95_ms(histogram, requests)

    return {
        "window_minutes": window_minutes,
        "requests": requests,
        "status_4xx": status_4xx,
        "status_5xx": status_5xx,
        "error_rate_4xx_pct": rate_4xx_pct,
        "error_rate_5xx_pct": rate_5xx_pct,
        "latency_avg_ms": latency_avg_ms,
        "latency_p95_ms": latency_p95_ms,
        "latency_histogram": histogram,
    }


def get_sla_backlog_metrics(*, now=None) -> dict[str, Any]:
    now = now or timezone.now()
    open_qs = SlaEscalation.objects.filter(status__in=[EscalationStatusChoices.OPEN, EscalationStatusChoices.ACK])

    oldest_due_at = open_qs.order_by("due_at").values_list("due_at", flat=True).first()
    oldest_overdue_minutes = 0
    if oldest_due_at and oldest_due_at < now:
        oldest_overdue_minutes = int((now - oldest_due_at).total_seconds() // 60)

    return {
        "open_total": open_qs.count(),
        "open_l1": open_qs.filter(escalation_level=EscalationLevelChoices.LEVEL_1).count(),
        "open_l2": open_qs.filter(escalation_level=EscalationLevelChoices.LEVEL_2).count(),
        "open_l3": open_qs.filter(escalation_level=EscalationLevelChoices.LEVEL_3).count(),
        "overdue_total": open_qs.filter(due_at__lt=now).count(),
        "oldest_overdue_minutes": oldest_overdue_minutes,
    }


def get_finance_risk_metrics(*, now=None) -> dict[str, Any]:
    now = now or timezone.now()
    today = now.date()

    invoice_dq_open = DataQualityIssue.objects.filter(
        source="invoice",
        status__in=[DataQualityStatusChoices.OPEN, DataQualityStatusChoices.IN_REVIEW],
    )
    overdue_invoices_qs = Invoice.objects.exclude(
        status__in=[InvoiceStatusChoices.BROUILLON, InvoiceStatusChoices.ANNULEE],
    ).filter(
        due_date__isnull=False,
        due_date__lt=today,
        total_amount__gt=F("paid_amount"),
    )
    overdue_amount_total = int(
        overdue_invoices_qs.annotate(
            overdue_balance=ExpressionWrapper(
                F("total_amount") - F("paid_amount"),
                output_field=IntegerField(),
            )
        ).aggregate(total=Sum("overdue_balance")).get("total")
        or 0
    )

    return {
        "invoice_data_quality_open": invoice_dq_open.count(),
        "invoice_data_quality_critical_open": invoice_dq_open.filter(
            severity=DataQualitySeverityChoices.CRITICAL
        ).count(),
        "payment_ledger_mismatch_open": invoice_dq_open.filter(
            fingerprint__icontains="payment_ledger_mismatch",
        ).count(),
        "overdue_unpaid_invoices_total": overdue_invoices_qs.count(),
        "overdue_unpaid_amount_total": overdue_amount_total,
        "fne_rejected_invoices_total": Invoice.objects.filter(
            fne_required=True,
            fne_status=InvoiceFNEStatusChoices.REJECTED,
        ).exclude(status=InvoiceStatusChoices.ANNULEE).count(),
    }


def evaluate_observability_alerts(
    *,
    api_metrics: dict[str, Any],
    sla_metrics: dict[str, Any],
    finance_metrics: dict[str, Any],
) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []

    min_requests = int(getattr(settings, "OBS_ALERT_MIN_REQUESTS", 20))
    alert_4xx_pct = float(getattr(settings, "OBS_ALERT_4XX_RATE_PCT", 30.0))
    alert_5xx_pct = float(getattr(settings, "OBS_ALERT_5XX_RATE_PCT", 5.0))
    alert_p95_ms = float(getattr(settings, "OBS_ALERT_P95_MS", 1200.0))
    alert_sla_open = int(getattr(settings, "OBS_ALERT_SLA_OPEN", 15))
    alert_sla_l3_open = int(getattr(settings, "OBS_ALERT_SLA_L3_OPEN", 0))
    alert_sla_oldest_overdue_min = int(getattr(settings, "OBS_ALERT_SLA_OLDEST_OVERDUE_MINUTES", 120))
    alert_fin_dq_open = int(getattr(settings, "OBS_ALERT_FIN_DQ_OPEN", 20))
    alert_fin_dq_critical = int(getattr(settings, "OBS_ALERT_FIN_DQ_CRITICAL", 0))
    alert_fin_ledger_mismatch = int(getattr(settings, "OBS_ALERT_FIN_LEDGER_MISMATCH", 0))
    alert_fin_overdue_amount = int(getattr(settings, "OBS_ALERT_FIN_OVERDUE_AMOUNT", 2_000_000))
    alert_fin_fne_rejected = int(getattr(settings, "OBS_ALERT_FIN_FNE_REJECTED", 0))

    requests = int(api_metrics.get("requests", 0))
    if requests >= min_requests and float(api_metrics.get("error_rate_5xx_pct", 0.0)) >= alert_5xx_pct:
        alerts.append(
            {
                "severity": "critical",
                "code": "api_5xx_rate_high",
                "message": "Taux 5xx API au-dessus du seuil.",
                "value": float(api_metrics.get("error_rate_5xx_pct", 0.0)),
                "threshold": alert_5xx_pct,
            }
        )
    if requests >= min_requests and float(api_metrics.get("error_rate_4xx_pct", 0.0)) >= alert_4xx_pct:
        alerts.append(
            {
                "severity": "warning",
                "code": "api_4xx_rate_high",
                "message": "Taux 4xx API au-dessus du seuil.",
                "value": float(api_metrics.get("error_rate_4xx_pct", 0.0)),
                "threshold": alert_4xx_pct,
            }
        )
    if requests >= min_requests and float(api_metrics.get("latency_p95_ms", 0.0)) >= alert_p95_ms:
        alerts.append(
            {
                "severity": "warning",
                "code": "api_latency_p95_high",
                "message": "Latence p95 API au-dessus du seuil.",
                "value": float(api_metrics.get("latency_p95_ms", 0.0)),
                "threshold": alert_p95_ms,
            }
        )

    open_total = int(sla_metrics.get("open_total", 0))
    if open_total > alert_sla_open:
        alerts.append(
            {
                "severity": "warning",
                "code": "sla_open_backlog_high",
                "message": "Volume d'escalades SLA ouvertes au-dessus du seuil.",
                "value": open_total,
                "threshold": alert_sla_open,
            }
        )

    l3_open = int(sla_metrics.get("open_l3", 0))
    if l3_open > alert_sla_l3_open:
        alerts.append(
            {
                "severity": "critical",
                "code": "sla_l3_open_present",
                "message": "Escalade SLA niveau 3 détectée.",
                "value": l3_open,
                "threshold": alert_sla_l3_open,
            }
        )

    oldest_overdue = int(sla_metrics.get("oldest_overdue_minutes", 0))
    if oldest_overdue > alert_sla_oldest_overdue_min:
        alerts.append(
            {
                "severity": "critical",
                "code": "sla_oldest_overdue_too_old",
                "message": "Ancienneté de l'escalade SLA la plus en retard au-dessus du seuil.",
                "value": oldest_overdue,
                "threshold": alert_sla_oldest_overdue_min,
            }
        )

    fin_dq_open = int(finance_metrics.get("invoice_data_quality_open", 0))
    if fin_dq_open > alert_fin_dq_open:
        alerts.append(
            {
                "severity": "warning",
                "code": "finance_dq_open_high",
                "message": "Volume d'anomalies data quality facture au-dessus du seuil.",
                "value": fin_dq_open,
                "threshold": alert_fin_dq_open,
            }
        )

    fin_dq_critical = int(finance_metrics.get("invoice_data_quality_critical_open", 0))
    if fin_dq_critical > alert_fin_dq_critical:
        alerts.append(
            {
                "severity": "critical",
                "code": "finance_dq_critical_present",
                "message": "Anomalie data quality facture critique active.",
                "value": fin_dq_critical,
                "threshold": alert_fin_dq_critical,
            }
        )

    ledger_mismatch_open = int(finance_metrics.get("payment_ledger_mismatch_open", 0))
    if ledger_mismatch_open > alert_fin_ledger_mismatch:
        alerts.append(
            {
                "severity": "warning",
                "code": "finance_payment_ledger_mismatch_open",
                "message": "Incohérences ledger paiements/factures détectées.",
                "value": ledger_mismatch_open,
                "threshold": alert_fin_ledger_mismatch,
            }
        )

    overdue_amount = int(finance_metrics.get("overdue_unpaid_amount_total", 0))
    if overdue_amount > alert_fin_overdue_amount:
        alerts.append(
            {
                "severity": "warning",
                "code": "finance_overdue_amount_high",
                "message": "Montant total des factures échues non soldées au-dessus du seuil.",
                "value": overdue_amount,
                "threshold": alert_fin_overdue_amount,
            }
        )

    fne_rejected = int(finance_metrics.get("fne_rejected_invoices_total", 0))
    if fne_rejected > alert_fin_fne_rejected:
        alerts.append(
            {
                "severity": "critical",
                "code": "finance_fne_rejected_present",
                "message": "Facture(s) rejetée(s) FNE active(s).",
                "value": fne_rejected,
                "threshold": alert_fin_fne_rejected,
            }
        )

    return alerts


def build_observability_summary(*, window_minutes: int | None = None, now=None) -> dict[str, Any]:
    now = now or timezone.now()
    api_metrics = get_api_window_metrics(window_minutes=window_minutes, now=now)
    sla_metrics = get_sla_backlog_metrics(now=now)
    finance_metrics = get_finance_risk_metrics(now=now)
    alerts = evaluate_observability_alerts(
        api_metrics=api_metrics,
        sla_metrics=sla_metrics,
        finance_metrics=finance_metrics,
    )

    health = "ok"
    if any(alert["severity"] == "critical" for alert in alerts):
        health = "critical"
    elif alerts:
        health = "warning"

    return {
        "generated_at": now.isoformat(),
        "health": health,
        "api": api_metrics,
        "sla": sla_metrics,
        "finance": finance_metrics,
        "alerts": alerts,
    }


def reset_observability_metrics(*, minutes: int = 60, now=None):
    """Utility de test pour nettoyer les buckets observabilité récents."""
    now = now or timezone.now()
    keys: list[str] = []
    for bucket in _minute_buckets(minutes, now=now):
        base_key = f"{_CACHE_PREFIX}:{bucket}"
        keys.extend(
            [
                f"{base_key}:requests",
                f"{base_key}:status_4xx",
                f"{base_key}:status_5xx",
                f"{base_key}:latency_sum_ms",
            ]
        )
        keys.extend([_histogram_key(base_key, bucket_key) for bucket_key in _LATENCY_BUCKET_KEYS])
    if keys:
        cache.delete_many(keys)
