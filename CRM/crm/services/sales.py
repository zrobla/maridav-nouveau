from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Sum

from crm.models import (
    Invoice,
    InvoiceFNEStatusChoices,
    InvoiceNatureChoices,
    InvoicePaymentMethodChoices,
    InvoiceStatusChoices,
    Order,
    OrderStatusChoices,
)

User = get_user_model()


def resolve_default_sales_owner(invoice: Invoice, *, fallback_user=None):
    """Resolve the accountable sales owner with deterministic fallback rules."""
    if invoice.sales_owner_id:
        return invoice.sales_owner

    if fallback_user is not None and getattr(fallback_user, "is_authenticated", False):
        return fallback_user

    if invoice.created_by_id:
        return invoice.created_by

    if invoice.order_id and invoice.order and invoice.order.created_by_id:
        return invoice.order.created_by

    customer = invoice.customer
    if customer:
        opp = customer.opportunities.filter(assigned_to__isnull=False).order_by("-updated_at").first()
        if opp and opp.assigned_to_id:
            return opp.assigned_to
        task = customer.tasks.filter(assigned_to__isnull=False).order_by("-updated_at").first()
        if task and task.assigned_to_id:
            return task.assigned_to

    # "Maridav par défaut": first active member in core sales groups.
    fallback_groups = [
        "Commerciaux",
        "Technico-Commerciaux",
        "Directeur Commercial",
        "Direction Générale",
    ]
    for group_name in fallback_groups:
        group = Group.objects.filter(name=group_name).first()
        if not group:
            continue
        user = group.user_set.filter(is_active=True).order_by("id").first()
        if user:
            return user

    # Last fallback: first active superuser.
    return User.objects.filter(is_active=True, is_superuser=True).order_by("id").first()


def recalculate_invoice_totals(invoice: Invoice) -> dict[str, int]:
    if not invoice.pk:
        return {"subtotal_amount": 0, "discount_amount": 0, "tax_amount": 0, "total_amount": 0}

    subtotal = 0
    discount = 0
    tax = 0
    for item in invoice.items.all():
        subtotal += int(item.subtotal_amount)
        discount += int(item.discount_amount)
        tax += int(item.tax_amount)
    total = max(0, int(subtotal - discount + tax))

    updates: dict[str, Any] = {
        "subtotal_amount": subtotal,
        "discount_amount": discount,
        "tax_amount": tax,
        "total_amount": total,
    }
    for field, value in updates.items():
        setattr(invoice, field, value)
    Invoice.objects.filter(pk=invoice.pk).update(**updates)
    return updates


def validate_invoice_issue_prerequisites(invoice: Invoice) -> list[str]:
    issues: list[str] = []
    customer = invoice.customer

    if invoice.items.count() == 0:
        issues.append("La facture ne contient aucune ligne produit.")

    if int(invoice.total_amount or 0) <= 0:
        issues.append("Le total de facture doit être strictement positif.")

    if customer:
        missing_fiscal = []
        for field_name, label in [
            ("tax_ncc", "NCC"),
            ("tax_ntd", "NTD"),
            ("tax_rccm", "RCCM"),
            ("tax_regime", "Régime fiscal"),
        ]:
            if not getattr(customer, field_name, ""):
                missing_fiscal.append(label)
        if missing_fiscal:
            issues.append(
                "Profil fiscal client incomplet ("
                + ", ".join(missing_fiscal)
                + ")."
            )

    if invoice.nature == InvoiceNatureChoices.CREDIT_NOTE:
        if not invoice.original_invoice_id:
            issues.append("Un avoir doit obligatoirement référencer une facture d'origine.")
        else:
            original = invoice.original_invoice
            if original.nature == InvoiceNatureChoices.CREDIT_NOTE:
                issues.append("Un avoir ne peut pas référencer un autre avoir.")
            if original.status == InvoiceStatusChoices.BROUILLON:
                issues.append("La facture d'origine doit être émise avant création d'un avoir.")
            if original.fne_required and original.fne_status != InvoiceFNEStatusChoices.CERTIFIED:
                issues.append(
                    "La facture d'origine doit être certifiée FNE avant émission d'un avoir."
                )
    return issues


def validate_invoice_payment_prerequisites(invoice: Invoice, *, amount: int) -> list[str]:
    issues: list[str] = []
    payment_amount = int(amount or 0)
    total_amount = int(invoice.total_amount or 0)

    if payment_amount <= 0:
        issues.append("Le montant du paiement doit être strictement positif.")

    if invoice.status == InvoiceStatusChoices.BROUILLON:
        issues.append("La facture doit être émise avant enregistrement d'un paiement.")

    if invoice.status == InvoiceStatusChoices.ANNULEE:
        issues.append("Aucun paiement n'est autorisé sur une facture annulée.")

    if invoice.nature == InvoiceNatureChoices.CREDIT_NOTE:
        issues.append("Un paiement ne peut pas être enregistré sur un avoir.")

    if total_amount <= 0:
        issues.append("Le total de la facture doit être strictement positif.")

    aggregated_paid = 0
    if invoice.pk:
        aggregated_paid = int(invoice.payments.aggregate(total=Sum("amount")).get("total") or 0)
    current_paid = max(aggregated_paid, int(invoice.paid_amount or 0))
    balance_due = max(0, total_amount - current_paid)
    if payment_amount > balance_due:
        issues.append(
            "Le montant du paiement dépasse le reste à payer "
            f"({balance_due} FCFA)."
        )

    return issues


def recalculate_invoice_payment_snapshot(invoice: Invoice, *, force: bool = False) -> dict[str, Any]:
    if not invoice.pk:
        return {
            "paid_amount": int(invoice.paid_amount or 0),
            "payment_method": invoice.payment_method,
            "payment_reference": invoice.payment_reference,
        }

    payments_qs = invoice.payments.all()
    paid_amount = int(payments_qs.aggregate(total=Sum("amount")).get("total") or 0)
    if not force and paid_amount == 0:
        return {
            "paid_amount": int(invoice.paid_amount or 0),
            "payment_method": invoice.payment_method,
            "payment_reference": invoice.payment_reference,
        }

    latest_payment = payments_qs.order_by("-paid_at", "-pk").first()
    updates: dict[str, Any] = {
        "paid_amount": paid_amount,
        "payment_method": (
            latest_payment.payment_method
            if latest_payment
            else InvoicePaymentMethodChoices.NON_RENSEIGNE
        ),
        "payment_reference": latest_payment.payment_reference if latest_payment else "",
    }

    for field, value in updates.items():
        setattr(invoice, field, value)
    Invoice.objects.filter(pk=invoice.pk).update(**updates)
    return updates


def reconcile_invoice_status_from_payments(invoice: Invoice):
    total = int(invoice.total_amount or 0)
    paid = int(invoice.paid_amount or 0)

    new_status = invoice.status
    if invoice.status not in {InvoiceStatusChoices.ANNULEE, InvoiceStatusChoices.BROUILLON}:
        if paid <= 0:
            new_status = InvoiceStatusChoices.EMISE
        elif paid < total:
            new_status = InvoiceStatusChoices.PARTIELLEMENT_PAYEE
        else:
            new_status = InvoiceStatusChoices.PAYEE

    if new_status != invoice.status:
        invoice.status = new_status
        Invoice.objects.filter(pk=invoice.pk).update(status=new_status)


def mark_invoice_ready_for_fne(invoice: Invoice):
    if not invoice.fne_required:
        if invoice.fne_status != InvoiceFNEStatusChoices.NOT_REQUIRED:
            invoice.fne_status = InvoiceFNEStatusChoices.NOT_REQUIRED
            Invoice.objects.filter(pk=invoice.pk).update(fne_status=InvoiceFNEStatusChoices.NOT_REQUIRED)
        return

    if invoice.fne_status in {InvoiceFNEStatusChoices.CERTIFIED, InvoiceFNEStatusChoices.REJECTED}:
        return

    if invoice.fne_status != InvoiceFNEStatusChoices.PENDING:
        invoice.fne_status = InvoiceFNEStatusChoices.PENDING
        Invoice.objects.filter(pk=invoice.pk).update(fne_status=InvoiceFNEStatusChoices.PENDING)


def validate_order_fne_delivery_gate(order: Order, *, target_status: str | None = None) -> list[str]:
    """
    Bloque les operations aval de livraison tant que la commande n'est pas couverte
    par une facture certifiee FNE.
    """
    target = target_status or order.status
    if target != OrderStatusChoices.LIVRE:
        return []

    if not order.pk:
        return ["La livraison est bloquée: aucune facture certifiée FNE liée à la commande."]

    invoices = order.invoices.exclude(status=InvoiceStatusChoices.ANNULEE)
    if not invoices.exists():
        return ["La livraison est bloquée: aucune facture liée à la commande."]

    required_invoices = invoices.filter(fne_required=True)
    if required_invoices.exists():
        not_certified = required_invoices.exclude(fne_status=InvoiceFNEStatusChoices.CERTIFIED)
        if not_certified.exists():
            refs = ", ".join(list(not_certified.values_list("invoice_number", flat=True)[:5]))
            if refs:
                return [f"La livraison est bloquée: factures non certifiées FNE ({refs})."]
            return ["La livraison est bloquée: des factures liées ne sont pas certifiées FNE."]
        return []

    issued = invoices.exclude(status=InvoiceStatusChoices.BROUILLON)
    if not issued.exists():
        return ["La livraison est bloquée: aucune facture émise pour la commande."]
    return []
