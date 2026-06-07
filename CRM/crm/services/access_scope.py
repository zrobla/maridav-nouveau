from __future__ import annotations

from collections.abc import Iterable

from django.db.models import Q, QuerySet
from django.utils import timezone

from crm.models import (
    Contact,
    Customer,
    Forecast,
    InboundRequest,
    Invoice,
    InvoiceItem,
    InvoicePayment,
    Lead,
    Opportunity,
    Order,
    OrderItem,
    Outlet,
    Promotion,
    RoleAssignment,
    RoleScopeChoices,
    SupportCase,
    Task,
    Territory,
    VisitReport,
)


PRIVILEGED_GROUPS = {
    "Direction/Propriétaire",
    "Direction Générale",
    "Administrateur Système",
    "Directeur Commercial",
    "Technicien CRM & Support IT",
    "Comptable",
    "Gouvernance & Conformité",
}


def _empty_scope() -> dict[str, set]:
    return {
        "segments": set(),
        "stages": set(),
        "objectives": set(),
        "regions": set(),
        "customer_ids": set(),
        "opportunity_ids": set(),
        "order_ids": set(),
        "support_ids": set(),
        "inbound_ids": set(),
    }


def has_global_scope(user) -> bool:
    if user.is_superuser:
        return True
    if user.has_perm("crm.manage_sales_team") or user.has_perm("crm.view_reports"):
        return True
    return user.groups.filter(name__in=PRIVILEGED_GROUPS).exists()


def active_role_assignments(user):
    now = timezone.now()
    return RoleAssignment.objects.filter(user=user, is_active=True, valid_from__lte=now).filter(
        Q(valid_to__isnull=True) | Q(valid_to__gte=now)
    )


def _parse_scope_reference_value(expected_scope: str, reference: str | None) -> str | None:
    ref = (reference or "").strip()
    if not ref:
        return None
    lowered = ref.lower()
    if "=" in lowered:
        key, value = lowered.split("=", 1)
        if key.strip() == expected_scope:
            return value.strip() or None
    return lowered


def resolve_scope(user) -> dict[str, set]:
    scope = _empty_scope()
    for assignment in active_role_assignments(user):
        if assignment.scope == RoleScopeChoices.SEGMENT:
            value = _parse_scope_reference_value("segment", assignment.scope_reference)
            if value:
                scope["segments"].add(value)
        elif assignment.scope == RoleScopeChoices.STAGE:
            value = _parse_scope_reference_value("stage", assignment.scope_reference)
            if value:
                scope["stages"].add(value)
        elif assignment.scope == RoleScopeChoices.OBJECTIVE:
            value = _parse_scope_reference_value("objective", assignment.scope_reference)
            if value:
                scope["objectives"].add(value)
        elif assignment.scope == RoleScopeChoices.REGION:
            value = _parse_scope_reference_value("region", assignment.scope_reference)
            if value:
                scope["regions"].add(value)
        elif assignment.scope == RoleScopeChoices.CUSTOMER and assignment.object_id:
            scope["customer_ids"].add(assignment.object_id)
        elif assignment.scope == RoleScopeChoices.OPPORTUNITY and assignment.object_id:
            scope["opportunity_ids"].add(assignment.object_id)
        elif assignment.scope == RoleScopeChoices.ORDER and assignment.object_id:
            scope["order_ids"].add(assignment.object_id)
        elif assignment.scope == RoleScopeChoices.SUPPORT and assignment.object_id:
            scope["support_ids"].add(assignment.object_id)
        elif assignment.scope == RoleScopeChoices.INBOUND and assignment.object_id:
            scope["inbound_ids"].add(assignment.object_id)
    return scope


def scope_badges(scope: dict[str, set], is_global_scope: bool) -> list[str]:
    if is_global_scope:
        return ["Portée globale"]

    badges: list[str] = []
    for label, key in [
        ("Segment", "segments"),
        ("Stade", "stages"),
        ("Objectif", "objectives"),
        ("Région", "regions"),
    ]:
        for value in sorted(scope[key]):
            badges.append(f"{label}: {value}")
    if scope["customer_ids"]:
        badges.append(f"Clients ciblés: {len(scope['customer_ids'])}")
    if not badges:
        badges.append("Portefeuille assigné")
    return badges


def _or_icontains(field_name: str, values: Iterable[str]):
    query = Q()
    for value in values:
        query |= Q(**{f"{field_name}__icontains": value})
    return query


def _scope_context(user, context: tuple[bool, dict[str, set]] | None = None):
    if context is not None:
        return context
    return has_global_scope(user), resolve_scope(user)


def scoped_customers_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Customer.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = (
        Q(tasks__assigned_to=user)
        | Q(opportunities__assigned_to=user)
        | Q(support_cases__assigned_to=user)
        | Q(orders__created_by=user)
        | Q(visits__created_by=user)
    )
    if scope["customer_ids"]:
        query |= Q(pk__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(segment__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_contacts_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Contact.objects.select_related("customer").all()
    is_global_scope, _scope = _scope_context(user, context)
    if is_global_scope:
        return queryset
    customer_ids = scoped_customers_queryset(
        user,
        queryset=Customer.objects.all(),
        context=(is_global_scope, _scope),
    ).values_list("id", flat=True)
    return queryset.filter(customer_id__in=customer_ids).distinct()


def scoped_leads_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Lead.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(assigned_to=user)
    if scope["segments"]:
        query |= Q(segment__in=scope["segments"])
    if scope["stages"]:
        query |= _or_icontains("stage", scope["stages"])
    if scope["objectives"]:
        query |= _or_icontains("objective", scope["objectives"])
    if scope["regions"]:
        query |= _or_icontains("region", scope["regions"])
    if scope["inbound_ids"]:
        query |= Q(inbound_requests__id__in=scope["inbound_ids"])
    if scope["opportunity_ids"]:
        query |= Q(opportunities__id__in=scope["opportunity_ids"])
    return queryset.filter(query).distinct()


def scoped_inbound_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else InboundRequest.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(assigned_to=user) | Q(lead__assigned_to=user)
    if scope["segments"]:
        query |= Q(segment__in=scope["segments"])
    if scope["stages"]:
        query |= _or_icontains("stage", scope["stages"])
    if scope["objectives"]:
        query |= _or_icontains("objective", scope["objectives"])
    if scope["regions"]:
        query |= _or_icontains("region", scope["regions"])
    if scope["inbound_ids"]:
        query |= Q(pk__in=scope["inbound_ids"])
    return queryset.filter(query).distinct()


def scoped_opportunities_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Opportunity.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(assigned_to=user) | Q(lead__assigned_to=user)
    if scope["opportunity_ids"]:
        query |= Q(pk__in=scope["opportunity_ids"])
    if scope["customer_ids"]:
        query |= Q(customer_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(segment__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("customer__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_orders_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Order.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(created_by=user) | Q(tasks__assigned_to=user)
    if scope["order_ids"]:
        query |= Q(pk__in=scope["order_ids"])
    if scope["customer_ids"]:
        query |= Q(customer_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(customer__segment__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("customer__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_invoices_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Invoice.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(created_by=user) | Q(sales_owner=user) | Q(order__created_by=user) | Q(customer__tasks__assigned_to=user)
    if scope["order_ids"]:
        query |= Q(order_id__in=scope["order_ids"])
    if scope["customer_ids"]:
        query |= Q(customer_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(customer__segment__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("customer__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_order_items_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else OrderItem.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(order__created_by=user) | Q(order__tasks__assigned_to=user)
    if scope["order_ids"]:
        query |= Q(order_id__in=scope["order_ids"])
    if scope["customer_ids"]:
        query |= Q(order__customer_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(order__customer__segment__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("order__customer__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_invoice_items_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else InvoiceItem.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = (
        Q(invoice__created_by=user)
        | Q(invoice__sales_owner=user)
        | Q(invoice__order__created_by=user)
        | Q(invoice__customer__tasks__assigned_to=user)
    )
    if scope["order_ids"]:
        query |= Q(invoice__order_id__in=scope["order_ids"])
    if scope["customer_ids"]:
        query |= Q(invoice__customer_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(invoice__customer__segment__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("invoice__customer__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_invoice_payments_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else InvoicePayment.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = (
        Q(invoice__created_by=user)
        | Q(invoice__sales_owner=user)
        | Q(invoice__order__created_by=user)
        | Q(invoice__customer__tasks__assigned_to=user)
    )
    if scope["order_ids"]:
        query |= Q(invoice__order_id__in=scope["order_ids"])
    if scope["customer_ids"]:
        query |= Q(invoice__customer_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(invoice__customer__segment__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("invoice__customer__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_support_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else SupportCase.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(assigned_to=user) | Q(tasks__assigned_to=user)
    if scope["support_ids"]:
        query |= Q(pk__in=scope["support_ids"])
    if scope["customer_ids"]:
        query |= Q(customer_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(species__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("customer__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_tasks_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Task.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(assigned_to=user)
    if scope["customer_ids"]:
        query |= Q(customer_id__in=scope["customer_ids"])
    if scope["opportunity_ids"]:
        query |= Q(opportunity_id__in=scope["opportunity_ids"])
    if scope["order_ids"]:
        query |= Q(order_id__in=scope["order_ids"])
    if scope["support_ids"]:
        query |= Q(support_case_id__in=scope["support_ids"])
    return queryset.filter(query).distinct()


def scoped_visits_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else VisitReport.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(created_by=user)
    if scope["customer_ids"]:
        query |= Q(customer_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(species__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("customer__region", scope["regions"])
        query |= _or_icontains("outlet__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_promotions_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Promotion.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(outlets__territory__manager=user)
    if scope["regions"]:
        query |= _or_icontains("outlets__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_forecasts_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Forecast.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(customer__tasks__assigned_to=user) | Q(customer__orders__created_by=user)
    if scope["customer_ids"]:
        query |= Q(customer_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(customer__segment__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("customer__region", scope["regions"])
        query |= _or_icontains("outlet__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_territories_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Territory.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(manager=user)
    if scope["regions"]:
        query |= _or_icontains("region", scope["regions"])
        query |= _or_icontains("outlets__region", scope["regions"])
    if scope["customer_ids"]:
        query |= Q(outlets__distributor_id__in=scope["customer_ids"])
    return queryset.filter(query).distinct()


def scoped_outlets_queryset(user, queryset: QuerySet | None = None, *, context=None):
    queryset = queryset if queryset is not None else Outlet.objects.all()
    is_global_scope, scope = _scope_context(user, context)
    if is_global_scope:
        return queryset

    query = Q(territory__manager=user)
    if scope["customer_ids"]:
        query |= Q(distributor_id__in=scope["customer_ids"])
    if scope["segments"]:
        query |= Q(distributor__segment__in=scope["segments"])
    if scope["regions"]:
        query |= _or_icontains("region", scope["regions"])
        query |= _or_icontains("territory__region", scope["regions"])
    return queryset.filter(query).distinct()


def scoped_queryset_for_model(user, queryset: QuerySet, *, context=None):
    handlers = {
        Customer: scoped_customers_queryset,
        Contact: scoped_contacts_queryset,
        Lead: scoped_leads_queryset,
        InboundRequest: scoped_inbound_queryset,
        Opportunity: scoped_opportunities_queryset,
        Order: scoped_orders_queryset,
        Invoice: scoped_invoices_queryset,
        OrderItem: scoped_order_items_queryset,
        InvoiceItem: scoped_invoice_items_queryset,
        InvoicePayment: scoped_invoice_payments_queryset,
        SupportCase: scoped_support_queryset,
        Task: scoped_tasks_queryset,
        VisitReport: scoped_visits_queryset,
        Promotion: scoped_promotions_queryset,
        Forecast: scoped_forecasts_queryset,
        Territory: scoped_territories_queryset,
        Outlet: scoped_outlets_queryset,
    }
    handler = handlers.get(queryset.model)
    if handler is None:
        return queryset
    return handler(user, queryset=queryset, context=context)


def object_in_scope(user, obj, *, context=None) -> bool:
    if obj is None:
        return True
    if not getattr(obj, "pk", None):
        return False
    queryset = scoped_queryset_for_model(user, obj.__class__.objects.all(), context=context)
    return queryset.filter(pk=obj.pk).exists()
