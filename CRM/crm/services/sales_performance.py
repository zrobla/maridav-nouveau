"""Services de pilotage commercial & financier (Phase 4).

Calcule le chiffre d'affaires réalisé (à partir des factures émises), confronte les
objectifs commerciaux au réalisé, et alimente le tableau de bord financier
(CA par commercial, par espèce, top produits, série mensuelle).

Le CA d'une période retient les factures « réelles » (émises / partiellement payées /
payées), datées par leur date d'émission si renseignée, sinon par leur date de création.
"""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Q, Sum
from django.utils import timezone

from crm.models import (
    Invoice,
    InvoiceItem,
    InvoiceStatusChoices,
    SalesTarget,
)


REALIZED_STATUSES = [
    InvoiceStatusChoices.EMISE,
    InvoiceStatusChoices.PARTIELLEMENT_PAYEE,
    InvoiceStatusChoices.PAYEE,
]


def _period_q(year: int, month: int) -> Q:
    """Factures dont la date effective (émission, sinon création) tombe dans la période."""
    return Q(issued_at__year=year, issued_at__month=month) | Q(
        issued_at__isnull=True, created_at__year=year, created_at__month=month
    )


def realized_invoices(year: int, month: int, owner=None):
    qs = Invoice.objects.filter(status__in=REALIZED_STATUSES).filter(_period_q(year, month))
    if owner is not None:
        qs = qs.filter(sales_owner=owner)
    return qs


def realized_amount(year: int, month: int, owner=None, segment: str | None = None) -> int:
    """CA réalisé d'une période, éventuellement filtré par commercial et/ou espèce."""
    invoices = realized_invoices(year, month, owner=owner)
    if not segment:
        return int(invoices.aggregate(t=Sum("total_amount"))["t"] or 0)
    items = InvoiceItem.objects.filter(
        invoice__in=invoices, product__category__segment=segment
    ).select_related("product")
    return sum(it.total_amount for it in items)


def target_summary(target: SalesTarget) -> dict:
    """Réalisé vs objectif d'un commercial + commission estimée."""
    realized = realized_amount(
        target.period_year, target.period_month, owner=target.owner, segment=target.segment or None
    )
    target_amount = int(target.target_amount or 0)
    achievement = round(realized / target_amount * 100, 1) if target_amount else None
    commission = int(realized * Decimal(target.commission_rate_pct or 0) / Decimal("100"))
    return {
        "realized": realized,
        "target": target_amount,
        "achievement_pct": achievement,
        "gap": realized - target_amount,
        "commission": commission,
    }


def ca_by_commercial(year: int, month: int) -> list[dict]:
    rows = (
        realized_invoices(year, month)
        .values("sales_owner__username", "sales_owner__first_name", "sales_owner__last_name")
        .annotate(ca=Sum("total_amount"))
        .order_by("-ca")
    )
    result = []
    for r in rows:
        name = (f"{r['sales_owner__first_name'] or ''} {r['sales_owner__last_name'] or ''}").strip()
        result.append({"name": name or r["sales_owner__username"] or "Non attribué", "ca": int(r["ca"] or 0)})
    return result


def ca_by_species(year: int, month: int) -> list[dict]:
    invoices = realized_invoices(year, month)
    # Le total d'une ligne tient compte des remises/taxes -> on agrège via la propriété.
    buckets: dict[str, int] = {}
    for it in InvoiceItem.objects.filter(invoice__in=invoices).select_related("product__category"):
        seg = it.product.category.get_segment_display() if it.product.category else "—"
        buckets[seg] = buckets.get(seg, 0) + it.total_amount
    return sorted(
        [{"segment": k, "ca": v} for k, v in buckets.items()], key=lambda x: x["ca"], reverse=True
    )


def top_products(year: int, month: int, limit: int = 10) -> list[dict]:
    invoices = realized_invoices(year, month)
    buckets: dict[int, dict] = {}
    for it in InvoiceItem.objects.filter(invoice__in=invoices).select_related("product"):
        b = buckets.setdefault(it.product_id, {"name": it.product.name, "qty": 0, "ca": 0})
        b["qty"] += int(it.quantity or 0)
        b["ca"] += it.total_amount
    return sorted(buckets.values(), key=lambda x: x["ca"], reverse=True)[:limit]


def monthly_ca_series(year: int) -> list[int]:
    """CA mensuel (12 valeurs) de l'année, pour un graphe d'évolution."""
    series = []
    for month in range(1, 13):
        series.append(realized_amount(year, month))
    return series


def finance_overview(year: int, month: int) -> dict:
    month_ca = realized_amount(year, month)
    year_ca = sum(realized_amount(year, m) for m in range(1, 13))
    invoices_count = realized_invoices(year, month).count()
    return {
        "month_ca": month_ca,
        "year_ca": year_ca,
        "invoices_count": invoices_count,
    }
