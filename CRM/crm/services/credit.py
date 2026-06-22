"""Services de gestion du crédit client et des créances âgées (Phase 2).

Calcule l'encours d'un client et la balance âgée (0-30 / 31-60 / 61-90 / 90+ jours)
à partir des factures émises non soldées. Une facture sans échéance est considérée
« courante » (non échue).
"""

from __future__ import annotations

from django.utils import timezone

from crm.models import Customer, Invoice, InvoiceStatusChoices


RECEIVABLE_STATUSES = [
    InvoiceStatusChoices.EMISE,
    InvoiceStatusChoices.PARTIELLEMENT_PAYEE,
]


def receivable_invoices(customer: Customer | None = None):
    qs = Invoice.objects.filter(status__in=RECEIVABLE_STATUSES).select_related("customer")
    if customer is not None:
        qs = qs.filter(customer=customer)
    return qs


def _bucket_for(due_date, today):
    """Retourne la clé de tranche d'ancienneté pour une échéance donnée."""
    if not due_date or due_date >= today:
        return "current"
    overdue_days = (today - due_date).days
    if overdue_days <= 30:
        return "d1_30"
    if overdue_days <= 60:
        return "d31_60"
    if overdue_days <= 90:
        return "d61_90"
    return "d90_plus"


def customer_aging(customer: Customer, today=None) -> dict:
    """Balance âgée d'un client : montants par tranche + total + retard."""
    today = today or timezone.localdate()
    buckets = {"current": 0, "d1_30": 0, "d31_60": 0, "d61_90": 0, "d90_plus": 0}
    for inv in receivable_invoices(customer):
        balance = max(0, int(inv.total_amount or 0) - int(inv.paid_amount or 0))
        if balance <= 0:
            continue
        buckets[_bucket_for(inv.due_date, today)] += balance
    total = sum(buckets.values())
    overdue = total - buckets["current"]
    return {**buckets, "total": total, "overdue": overdue}


def receivables_overview(customers_qs=None, today=None) -> dict:
    """Vue consolidée des créances : lignes par client + totaux globaux.

    Ne retient que les clients ayant un encours strictement positif.
    """
    today = today or timezone.localdate()
    if customers_qs is None:
        customers_qs = Customer.objects.all()
    rows = []
    totals = {"current": 0, "d1_30": 0, "d31_60": 0, "d61_90": 0, "d90_plus": 0, "total": 0, "overdue": 0}
    for customer in customers_qs.prefetch_related("invoices"):
        aging = customer_aging(customer, today=today)
        if aging["total"] <= 0:
            continue
        rows.append(
            {
                "customer": customer,
                "aging": aging,
                "credit_limit": int(customer.credit_limit or 0),
                "available": int(customer.credit_limit or 0) - aging["total"],
                "over_limit": bool(customer.credit_limit) and aging["total"] > customer.credit_limit,
                "credit_hold": customer.credit_hold,
            }
        )
        for key in totals:
            totals[key] += aging[key]
    rows.sort(key=lambda r: r["aging"]["overdue"], reverse=True)
    return {"rows": rows, "totals": totals}
