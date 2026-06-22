"""Views for the CRM application."""

from __future__ import annotations

import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.views import View

from .forms import (
    CareerApplicationForm,
    ContactForm,
    CustomerForm,
    ForecastForm,
    InboundRequestForm,
    LeadForm,
    NewsletterSubscriptionForm,
    OutletForm,
    OpportunityForm,
    OrderForm,
    OrderItemFormSet,
    InvoiceForm,
    InvoiceItemFormSet,
    InvoicePaymentForm,
    ProductForm,
    ProductCategoryForm,
    ProductPriceFormSet,
    PromotionForm,
    RoleAssignmentForm,
    RoutingRuleForm,
    SalesTargetForm,
    StockLotForm,
    StockMovementForm,
    SupportCaseForm,
    TaskForm,
    TerritoryForm,
    UserRoleForm,
    UserSecurityProfileForm,
    VisitReportForm,
    WarehouseForm,
)
from .models import (
    ApprovalRequest,
    ApprovalStatusChoices,
    AuditTrail,
    CareerApplication,
    Customer,
    Contact,
    DataQualityIssue,
    DataQualityStatusChoices,
    Forecast,
    InboundRequest,
    Lead,
    NewsletterSubscription,
    Outlet,
    Opportunity,
    OpportunityStageChoices,
    Order,
    Invoice,
    InvoicePayment,
    InvoicePaymentSourceChoices,
    InvoiceNatureChoices,
    InvoiceFNEStatusChoices,
    InvoiceStatusChoices,
    Product,
    ProductCategory,
    Promotion,
    RoleAssignment,
    RoutingRule,
    SalesTarget,
    SlaEscalation,
    EscalationStatusChoices,
    StockLot,
    StockLotStatusChoices,
    StockMovement,
    StockMovementTypeChoices,
    SupportCase,
    Task,
    Territory,
    VisitReport,
    InboundStatusChoices,
    LeadStatusChoices,
    MONTH_CHOICES,
    OrderStatusChoices,
    SupportStatusChoices,
    TaskStatusChoices,
    UserSecurityProfile,
    Warehouse,
)
from .services.stock import apply_stock_movement
from .services.credit import customer_aging, receivables_overview
from .services import sales_performance
from .services.access_scope import (
    has_global_scope,
    resolve_scope,
    scope_badges,
    scoped_customers_queryset,
    scoped_forecasts_queryset,
    scoped_inbound_queryset,
    scoped_invoices_queryset,
    scoped_invoice_payments_queryset,
    scoped_leads_queryset,
    scoped_opportunities_queryset,
    scoped_orders_queryset,
    scoped_promotions_queryset,
    scoped_support_queryset,
    scoped_tasks_queryset,
    scoped_visits_queryset,
)
from .services.governance import apply_order_approval_policy, refresh_sla_escalations, run_invoice_data_quality_checks
from .services.sales import (
    mark_invoice_ready_for_fne,
    recalculate_invoice_payment_snapshot,
    recalculate_invoice_totals,
    reconcile_invoice_status_from_payments,
    resolve_default_sales_owner,
    validate_order_fne_delivery_gate,
    validate_invoice_payment_prerequisites,
    validate_invoice_issue_prerequisites,
)


class DashboardView(PermissionRequiredMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = "crm/dashboard.html"
    permission_required = "crm.view_dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        refresh_sla_escalations(now=now)

        is_global_scope = self._has_global_scope(user)
        scope = self._resolve_dashboard_scope(user)

        customers_qs = self._scoped_customers_queryset(user, is_global_scope, scope)
        leads_qs = self._scoped_leads_queryset(user, is_global_scope, scope)
        opportunities_qs = self._scoped_opportunities_queryset(user, is_global_scope, scope)
        orders_qs = self._scoped_orders_queryset(user, is_global_scope, scope)
        invoices_qs = self._scoped_invoices_queryset(user, is_global_scope, scope)
        support_qs = self._scoped_support_queryset(user, is_global_scope, scope)
        inbox_qs = self._scoped_inbox_queryset(user, is_global_scope, scope)
        tasks_qs = self._scoped_tasks_queryset(user, is_global_scope, scope)
        visits_qs = self._scoped_visits_queryset(user, is_global_scope, scope)

        lead_total = leads_qs.count()
        lead_converted = leads_qs.filter(status=LeadStatusChoices.CONVERTI).count()
        inbound_total = inbox_qs.count()
        inbound_converted = inbox_qs.filter(status=InboundStatusChoices.CONVERTI).count()

        context["is_global_dashboard_scope"] = is_global_scope
        context["dashboard_role_labels"] = list(user.groups.values_list("name", flat=True).order_by("name"))
        context["dashboard_scope_badges"] = self._scope_badges(scope, is_global_scope)

        context["customers_count"] = customers_qs.count()
        context["leads_open"] = leads_qs.exclude(status=LeadStatusChoices.CONVERTI).count()
        context["opportunities_value"] = (
            opportunities_qs.exclude(stage__in=[OpportunityStageChoices.GAGNE, OpportunityStageChoices.PERDU]).aggregate(
                Sum("expected_value")
            )["expected_value__sum"]
            or 0
        )
        context["orders_to_deliver"] = orders_qs.filter(
            status__in=[OrderStatusChoices.DEVIS, OrderStatusChoices.CONFIRME]
        ).count()
        context["invoices_emitted"] = invoices_qs.exclude(status=InvoiceStatusChoices.BROUILLON).count()
        context["invoices_fne_pending"] = invoices_qs.filter(fne_status=InvoiceFNEStatusChoices.PENDING).count()
        context["support_open"] = support_qs.exclude(status=SupportStatusChoices.CLOTURE).count()
        context["inbound_open"] = inbox_qs.exclude(status__in=[InboundStatusChoices.CONVERTI, InboundStatusChoices.CLOTURE]).count()
        context["inbound_sla_overdue"] = inbox_qs.filter(first_response_at__isnull=True, first_response_due_at__lt=now).exclude(
            status=InboundStatusChoices.CLOTURE
        ).count()
        context["careers_pending"] = CareerApplication.objects.filter(status__in=["recu", "etude", "entretien"]).count()
        context["newsletter_active"] = NewsletterSubscription.objects.filter(status="actif").count()
        context["data_quality_open"] = DataQualityIssue.objects.filter(
            status__in=[DataQualityStatusChoices.OPEN, DataQualityStatusChoices.IN_REVIEW]
        ).count()
        context["approval_pending"] = ApprovalRequest.objects.filter(status=ApprovalStatusChoices.PENDING).count()
        context["sla_escalations_open"] = SlaEscalation.objects.filter(
            status__in=[EscalationStatusChoices.OPEN, EscalationStatusChoices.ACK]
        ).count()
        context["promotions_active"] = self._scoped_promotions_queryset(user, is_global_scope, scope).filter(status="actif").count()
        context["forecast_confirmed_qty"] = (
            self._scoped_forecasts_queryset(user, is_global_scope, scope)
            .filter(status="confirme")
            .aggregate(Sum("expected_quantity"))["expected_quantity__sum"]
            or 0
        )
        context["lead_conversion_rate"] = round((lead_converted / lead_total) * 100, 1) if lead_total else 0
        context["inbound_conversion_rate"] = round((inbound_converted / inbound_total) * 100, 1) if inbound_total else 0
        context["inbound_overdue_items"] = (
            inbox_qs.filter(first_response_at__isnull=True, first_response_due_at__lt=now)
            .exclude(status=InboundStatusChoices.CLOTURE)
            .select_related("assigned_to")
            .order_by("first_response_due_at")[:5]
        )
        context["tasks_next"] = tasks_qs.exclude(status=TaskStatusChoices.TERMINE).order_by("due_date")[:5]
        context["recent_visits"] = visits_qs.select_related("customer", "outlet").order_by("-visit_date")[:5]

        context["show_lead_chart"] = user.has_perm("crm.view_lead")
        context["show_opportunity_chart"] = user.has_perm("crm.view_opportunity")
        context["show_order_chart"] = user.has_perm("crm.view_order")
        context["show_charts_panel"] = any(
            [context["show_lead_chart"], context["show_opportunity_chart"], context["show_order_chart"]]
        )

        context["lead_status_labels"], context["lead_status_data"] = self._status_distribution(
            leads_qs, "status", Lead._meta.get_field("status").choices
        )
        context["order_status_labels"], context["order_status_data"] = self._status_distribution(
            orders_qs, "status", OrderStatusChoices.choices
        )
        context["opportunity_stage_labels"], context["opportunity_stage_data"] = self._status_distribution(
            opportunities_qs, "stage", Opportunity._meta.get_field("stage").choices
        )

        context["metric_cards_primary"] = self._metric_cards_primary(user, context)
        context["metric_cards_governance"] = self._metric_cards_governance(user, context)
        context["metric_cards_secondary"] = self._metric_cards_secondary(user, context)
        context["dashboard_actions"] = self._dashboard_actions(user)
        context["show_tasks_panel"] = user.has_perm("crm.view_task")
        context["show_inbound_sla_panel"] = user.has_perm("crm.view_inboundrequest")
        context["show_visits_panel"] = user.has_perm("crm.view_visitreport")
        return context

    def _has_global_scope(self, user):
        return has_global_scope(user)

    def _resolve_dashboard_scope(self, user):
        return resolve_scope(user)

    def _scope_badges(self, scope, is_global_scope):
        return scope_badges(scope, is_global_scope)

    def _scoped_customers_queryset(self, user, is_global_scope, scope):
        return scoped_customers_queryset(user, queryset=Customer.objects.all(), context=(is_global_scope, scope))

    def _scoped_leads_queryset(self, user, is_global_scope, scope):
        return scoped_leads_queryset(user, queryset=Lead.objects.all(), context=(is_global_scope, scope))

    def _scoped_inbox_queryset(self, user, is_global_scope, scope):
        return scoped_inbound_queryset(user, queryset=InboundRequest.objects.all(), context=(is_global_scope, scope))

    def _scoped_opportunities_queryset(self, user, is_global_scope, scope):
        return scoped_opportunities_queryset(
            user,
            queryset=Opportunity.objects.all(),
            context=(is_global_scope, scope),
        )

    def _scoped_orders_queryset(self, user, is_global_scope, scope):
        return scoped_orders_queryset(user, queryset=Order.objects.all(), context=(is_global_scope, scope))

    def _scoped_invoices_queryset(self, user, is_global_scope, scope):
        return scoped_invoices_queryset(user, queryset=Invoice.objects.all(), context=(is_global_scope, scope))

    def _scoped_support_queryset(self, user, is_global_scope, scope):
        return scoped_support_queryset(user, queryset=SupportCase.objects.all(), context=(is_global_scope, scope))

    def _scoped_tasks_queryset(self, user, is_global_scope, scope):
        return scoped_tasks_queryset(user, queryset=Task.objects.all(), context=(is_global_scope, scope))

    def _scoped_visits_queryset(self, user, is_global_scope, scope):
        return scoped_visits_queryset(user, queryset=VisitReport.objects.all(), context=(is_global_scope, scope))

    def _scoped_promotions_queryset(self, user, is_global_scope, scope):
        return scoped_promotions_queryset(user, queryset=Promotion.objects.all(), context=(is_global_scope, scope))

    def _scoped_forecasts_queryset(self, user, is_global_scope, scope):
        return scoped_forecasts_queryset(user, queryset=Forecast.objects.all(), context=(is_global_scope, scope))

    def _metric_cards_primary(self, user, context):
        cards = []
        if user.has_perm("crm.view_customer"):
            cards.append(
                {
                    "title": "Clients & prospects",
                    "value": context["customers_count"],
                    "subtitle": "Présence nationale, distributeurs & éleveurs",
                    "icon": "bi bi-people",
                    "icon_class": "bg-success",
                }
            )
        if user.has_perm("crm.view_lead"):
            cards.append(
                {
                    "title": "Leads actifs",
                    "value": context["leads_open"],
                    "subtitle": "Site, WhatsApp, appels",
                    "icon": "bi bi-magnet",
                    "icon_class": "bg-warning text-dark",
                }
            )
        if user.has_perm("crm.view_opportunity"):
            cards.append(
                {
                    "title": "Pipeline (FCFA)",
                    "value": f"{context['opportunities_value']:.0f}",
                    "subtitle": "Opportunités non gagnées/perdues",
                    "icon": "bi bi-kanban",
                    "icon_class": "bg-info text-dark",
                }
            )
        if user.has_perm("crm.view_supportcase"):
            cards.append(
                {
                    "title": "Supports ouverts",
                    "value": context["support_open"],
                    "subtitle": "Tickets terrain et qualité",
                    "icon": "bi bi-life-preserver",
                    "icon_class": "bg-danger",
                }
            )
        return cards

    def _metric_cards_governance(self, user, context):
        cards = []
        if user.has_perm("crm.view_dataqualityissue"):
            cards.append(
                {
                    "title": "Data Quality ouverte",
                    "value": context["data_quality_open"],
                    "subtitle": "Voir le registre qualité",
                    "url": reverse_lazy("governance-data-quality-list"),
                    "icon": "bi bi-shield-exclamation",
                    "icon_class": "bg-danger",
                }
            )
        if user.has_perm("crm.view_slaescalation"):
            cards.append(
                {
                    "title": "Escalades SLA",
                    "value": context["sla_escalations_open"],
                    "subtitle": "Voir les escalades actives",
                    "url": reverse_lazy("governance-escalations-list"),
                    "icon": "bi bi-hourglass-split",
                    "icon_class": "bg-warning text-dark",
                }
            )
        if user.has_perm("crm.view_approvalrequest"):
            cards.append(
                {
                    "title": "Approbations en attente",
                    "value": context["approval_pending"],
                    "subtitle": "Traiter les validations",
                    "url": reverse_lazy("governance-approvals-list"),
                    "icon": "bi bi-check2-square",
                    "icon_class": "bg-primary",
                }
            )
        return cards

    def _metric_cards_secondary(self, user, context):
        cards = []
        if user.has_perm("crm.view_inboundrequest"):
            cards.append(
                {
                    "title": "Inbox ouverte",
                    "value": context["inbound_open"],
                    "subtitle": f"{context['inbound_sla_overdue']} en retard SLA",
                    "icon": "bi bi-inbox",
                    "icon_class": "bg-primary",
                }
            )
        if user.has_perm("crm.view_invoice"):
            cards.append(
                {
                    "title": "Factures émises",
                    "value": context["invoices_emitted"],
                    "subtitle": f"FNE en attente: {context['invoices_fne_pending']}",
                    "icon": "bi bi-receipt",
                    "icon_class": "bg-primary",
                }
            )
        if user.has_perm("crm.view_careerapplication"):
            cards.append(
                {
                    "title": "Candidatures actives",
                    "value": context["careers_pending"],
                    "subtitle": "Carrières à traiter",
                    "icon": "bi bi-briefcase",
                    "icon_class": "bg-secondary",
                }
            )
        if user.has_perm("crm.view_newslettersubscription"):
            cards.append(
                {
                    "title": "Newsletter active",
                    "value": context["newsletter_active"],
                    "subtitle": f"{context['promotions_active']} promotions actives",
                    "icon": "bi bi-envelope-open",
                    "icon_class": "bg-success",
                }
            )
        if user.has_perm("crm.view_lead") or user.has_perm("crm.view_forecast"):
            cards.append(
                {
                    "title": "Conversion & forecast",
                    "value": f"{context['lead_conversion_rate']}%",
                    "subtitle": (
                        f"Inbound {context['inbound_conversion_rate']}% · Forecast confirmé {context['forecast_confirmed_qty']}"
                    ),
                    "icon": "bi bi-graph-up-arrow",
                    "icon_class": "bg-warning text-dark",
                }
            )
        return cards

    def _dashboard_actions(self, user):
        actions = []
        if user.has_perm("crm.add_lead"):
            actions.append(
                {"label": "Nouveau lead", "icon": "bi bi-lightning", "url": reverse_lazy("leads-create"), "class": "btn-brand"}
            )
        if user.has_perm("crm.add_customer"):
            actions.append(
                {
                    "label": "Ajouter un client",
                    "icon": "bi bi-person-plus",
                    "url": reverse_lazy("customers-create"),
                    "class": "btn-outline-success",
                }
            )
        if user.has_perm("crm.add_order"):
            actions.append(
                {
                    "label": "Saisir une commande",
                    "icon": "bi bi-bag-check",
                    "url": reverse_lazy("orders-create"),
                    "class": "btn-outline-success",
                }
            )
        if user.has_perm("crm.add_invoice"):
            actions.append(
                {
                    "label": "Vente express",
                    "icon": "bi bi-receipt-cutoff",
                    "url": reverse_lazy("sales-create"),
                    "class": "btn-outline-success",
                }
            )
        if user.has_perm("crm.add_supportcase"):
            actions.append(
                {
                    "label": "Ouvrir un ticket",
                    "icon": "bi bi-clipboard-pulse",
                    "url": reverse_lazy("support-create"),
                    "class": "btn-outline-success",
                }
            )
        if user.has_perm("crm.add_visitreport"):
            actions.append(
                {
                    "label": "Planifier une visite",
                    "icon": "bi bi-geo-alt",
                    "url": reverse_lazy("visits-create"),
                    "class": "btn-outline-success",
                }
            )
        if user.has_perm("crm.change_approvalrequest"):
            actions.append(
                {
                    "label": "Traiter les approbations",
                    "icon": "bi bi-check2-square",
                    "url": reverse_lazy("governance-approvals-list"),
                    "class": "btn-outline-secondary",
                }
            )
        return actions

    def _status_distribution(self, queryset, field: str, choices):
        counts = queryset.values(field).annotate(total=Count("id"))
        labels = []
        data = []
        for value, label in choices:
            labels.append(label)
            match = next((c for c in counts if c[field] == value), None)
            data.append(match["total"] if match else 0)
        return labels, data


class SearchableListMixin:
    search_fields: tuple[str, ...] = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            queryset = queryset.filter(q_objects)
        return queryset


class ScopedPermissionRequiredMixin(PermissionRequiredMixin):
    """
    Permet un fallback en permission objet pour les rôles assignés par dossier/projet.
    """

    def get_permission_object(self):
        if hasattr(self, "object") and self.object is not None:
            return self.object
        if hasattr(self, "get_object"):
            try:
                return self.get_object()
            except Exception:
                return None
        return None

    def has_permission(self):
        if super().has_permission():
            return True
        obj = self.get_permission_object()
        if obj is None:
            return False
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms, obj)


class CustomerListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = Customer
    template_name = "crm/customers/list.html"
    context_object_name = "customers"
    paginate_by = 20
    search_fields = ("name", "code", "city", "region", "customer_type")
    permission_required = "crm.view_customer"

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("contacts")
        segment = self.request.GET.get("segment")
        status = self.request.GET.get("status")
        if segment:
            queryset = queryset.filter(segment=segment)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["segment_choices"] = Customer._meta.get_field("segment").choices
        context["status_choices"] = Customer._meta.get_field("status").choices
        return context


class CustomerDetailView(ScopedPermissionRequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = Customer
    template_name = "crm/customers/detail.html"
    context_object_name = "customer"
    permission_required = "crm.view_customer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        context.update(
            {
                "contacts": customer.contacts.all(),
                "orders": customer.orders.all()[:5],
                "invoices": customer.invoices.all()[:5],
                "support_cases": customer.support_cases.all()[:5],
                "visits": customer.visits.all()[:5],
                "tasks": customer.tasks.exclude(status=TaskStatusChoices.TERMINE)[:5],
                "opportunities": customer.opportunities.all()[:5],
                "credit_aging": customer_aging(customer),
            }
        )
        return context


class CustomerCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "crm/customers/form.html"
    success_url = reverse_lazy("customers-list")
    permission_required = "crm.add_customer"


class CustomerUpdateView(ScopedPermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "crm/customers/form.html"
    success_url = reverse_lazy("customers-list")
    permission_required = "crm.change_customer"


class ContactCreateView(ScopedPermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "crm/contacts/form.html"
    permission_required = "crm.add_contact"

    def get_initial(self):
        initial = super().get_initial()
        customer_id = self.kwargs.get("customer_id")
        if customer_id:
            initial["customer"] = customer_id
        return initial

    def get_success_url(self):
        customer = self.object.customer
        messages.success(self.request, "Contact enregistré")
        return customer.get_absolute_url()

    def get_permission_object(self):
        customer_id = self.kwargs.get("customer_id") or self.request.POST.get("customer")
        if not customer_id:
            return None
        return Customer.objects.filter(pk=customer_id).first()


class LeadListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = Lead
    template_name = "crm/leads/list.html"
    context_object_name = "leads"
    paginate_by = 20
    search_fields = ("name", "company", "phone", "email")
    permission_required = "crm.view_lead"

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get("status")
        segment = self.request.GET.get("segment")
        if status:
            queryset = queryset.filter(status=status)
        if segment:
            queryset = queryset.filter(segment=segment)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Lead._meta.get_field("status").choices
        context["segment_choices"] = Lead._meta.get_field("segment").choices
        return context


class LeadCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Lead
    form_class = LeadForm
    template_name = "crm/leads/form.html"
    success_url = reverse_lazy("leads-list")
    permission_required = "crm.add_lead"


class LeadUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = "crm/leads/form.html"
    success_url = reverse_lazy("leads-list")
    permission_required = "crm.change_lead"


class OpportunityListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Opportunity
    template_name = "crm/opportunities/list.html"
    context_object_name = "opportunities"
    paginate_by = 20
    permission_required = "crm.view_opportunity"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer")
        stage = self.request.GET.get("stage")
        assigned = self.request.GET.get("assigned")
        if stage:
            queryset = queryset.filter(stage=stage)
        if assigned:
            queryset = queryset.filter(assigned_to_id=assigned)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = get_user_model().objects.all()
        context["stage_choices"] = Opportunity._meta.get_field("stage").choices
        return context


class OpportunityCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = "crm/opportunities/form.html"
    success_url = reverse_lazy("opportunities-list")
    permission_required = "crm.add_opportunity"


class OpportunityUpdateView(ScopedPermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = "crm/opportunities/form.html"
    success_url = reverse_lazy("opportunities-list")
    permission_required = "crm.change_opportunity"


class ProductCategoryListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = ProductCategory
    template_name = "crm/products/categories.html"
    context_object_name = "categories"
    permission_required = "crm.view_productcategory"


class ProductCategoryCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = "crm/products/category_form.html"
    success_url = reverse_lazy("products-categories")
    permission_required = "crm.add_productcategory"


class ProductListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = Product
    template_name = "crm/products/list.html"
    context_object_name = "products"
    paginate_by = 25
    search_fields = ("name", "sku")
    permission_required = "crm.view_product"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category")
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ProductCategory.objects.all()
        return context


class ProductCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Product
    form_class = ProductForm
    template_name = "crm/products/form.html"
    success_url = reverse_lazy("products-list")
    permission_required = "crm.add_product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["prices_formset"] = ProductPriceFormSet(self.request.POST)
        else:
            context["prices_formset"] = ProductPriceFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        prices_formset = context["prices_formset"]
        if prices_formset.is_valid():
            response = super().form_valid(form)
            prices_formset.instance = self.object
            prices_formset.save()
            return response
        return self.form_invalid(form)


class ProductUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "crm/products/form.html"
    success_url = reverse_lazy("products-list")
    permission_required = "crm.change_product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["prices_formset"] = ProductPriceFormSet(self.request.POST, instance=self.object)
        else:
            context["prices_formset"] = ProductPriceFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        prices_formset = context["prices_formset"]
        if prices_formset.is_valid():
            response = super().form_valid(form)
            prices_formset.instance = self.object
            prices_formset.save()
            return response
        return self.form_invalid(form)


class MarginReportView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = Product
    template_name = "crm/products/margin_report.html"
    context_object_name = "products"
    paginate_by = 40
    search_fields = ("name", "sku")
    permission_required = "crm.view_product"

    def get_queryset(self):
        qs = super().get_queryset().filter(status="actif").select_related("category").prefetch_related("segment_prices")
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ProductCategory.objects.all()
        all_products = Product.objects.filter(status="actif")
        priced = [p for p in all_products if p.unit_price]
        context["products_priced"] = len(priced)
        context["products_no_cost"] = sum(1 for p in priced if not p.cost_price)
        margins = [p.margin_pct for p in priced if p.cost_price and p.margin_pct is not None]
        context["avg_margin_pct"] = round(sum(margins) / len(margins), 1) if margins else None
        return context


class OrderListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = "crm/orders/list.html"
    context_object_name = "orders"
    paginate_by = 20
    permission_required = "crm.view_order"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class OrderCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Order
    form_class = OrderForm
    template_name = "crm/orders/form.html"
    success_url = reverse_lazy("orders-list")
    permission_required = "crm.add_order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = OrderItemFormSet(self.request.POST)
        else:
            context["items_formset"] = OrderItemFormSet()
        return context

    def form_valid(self, form):
        blockers = validate_order_fne_delivery_gate(form.instance, target_status=form.cleaned_data.get("status"))
        if blockers:
            form.add_error("status", blockers[0])
            messages.error(self.request, blockers[0])
            return self.form_invalid(form)

        form.instance.created_by = self.request.user
        context = self.get_context_data()
        items_formset = context["items_formset"]
        if items_formset.is_valid():
            response = super().form_valid(form)
            items_formset.instance = self.object
            items_formset.save()
            approval_request, created = apply_order_approval_policy(self.object, requested_by=self.request.user)
            if approval_request:
                if created:
                    messages.warning(
                        self.request,
                        "Commande enregistrée avec demande d'approbation corporate en attente.",
                    )
                else:
                    messages.info(
                        self.request,
                        "Commande soumise au workflow d'approbation corporate.",
                    )
            return response
        return self.form_invalid(form)


class OrderUpdateView(ScopedPermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "crm/orders/form.html"
    success_url = reverse_lazy("orders-list")
    permission_required = "crm.change_order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = OrderItemFormSet(self.request.POST, instance=self.object)
        else:
            context["items_formset"] = OrderItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        blockers = validate_order_fne_delivery_gate(form.instance, target_status=form.cleaned_data.get("status"))
        if blockers:
            form.add_error("status", blockers[0])
            messages.error(self.request, blockers[0])
            return self.form_invalid(form)

        context = self.get_context_data()
        items_formset = context["items_formset"]
        if items_formset.is_valid():
            response = super().form_valid(form)
            items_formset.instance = self.object
            items_formset.save()
            approval_request, created = apply_order_approval_policy(self.object, requested_by=self.request.user)
            if approval_request and created:
                messages.warning(
                    self.request,
                    "Mise à jour enregistrée et validation manager requise avant confirmation finale.",
                )
            return response
        return self.form_invalid(form)


class SalesInvoiceListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Invoice
    template_name = "crm/sales/list.html"
    context_object_name = "invoices"
    paginate_by = 25
    permission_required = "crm.view_invoice"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer", "sales_owner", "created_by", "order")
        queryset = scoped_invoices_queryset(
            self.request.user,
            queryset=queryset,
            context=(has_global_scope(self.request.user), resolve_scope(self.request.user)),
        )
        nature = (self.request.GET.get("nature") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        fne_status = (self.request.GET.get("fne_status") or "").strip()
        if nature:
            queryset = queryset.filter(nature=nature)
        if status:
            queryset = queryset.filter(status=status)
        if fne_status:
            queryset = queryset.filter(fne_status=fne_status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nature_choices"] = InvoiceNatureChoices.choices
        context["status_choices"] = InvoiceStatusChoices.choices
        context["fne_status_choices"] = InvoiceFNEStatusChoices.choices
        return context


class SalesInvoiceCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "crm/sales/form.html"
    success_url = reverse_lazy("sales-list")
    permission_required = "crm.add_invoice"

    def _credit_source_invoice(self):
        raw = self.request.GET.get("credit_from") or self.request.POST.get("credit_from")
        if not raw or not str(raw).isdigit():
            return None
        return (
            Invoice.objects.filter(pk=int(raw))
            .select_related("customer", "order", "sales_owner")
            .prefetch_related("items")
            .first()
        )

    def get_initial(self):
        initial = super().get_initial()
        order_id = self.request.GET.get("order")
        if order_id and order_id.isdigit():
            order = Order.objects.filter(pk=int(order_id)).select_related("customer").first()
            if order:
                initial["order"] = order.pk
                initial["customer"] = order.customer_id
                initial["source"] = "order"
        credit_source = self._credit_source_invoice()
        if credit_source:
            initial["source"] = credit_source.source
            initial["nature"] = InvoiceNatureChoices.CREDIT_NOTE
            initial["customer"] = credit_source.customer_id
            initial["order"] = credit_source.order_id
            initial["original_invoice"] = credit_source.pk
            initial["status"] = InvoiceStatusChoices.EMISE
            initial["fne_required"] = credit_source.fne_required
            initial["cancellation_reason"] = "Avoir émis depuis la facture d'origine."
            initial["notes"] = f"Avoir lié à {credit_source.invoice_number}."
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = InvoiceItemFormSet(self.request.POST)
        else:
            credit_source = self._credit_source_invoice()
            if credit_source:
                initial_items = [
                    {
                        "product": item.product_id,
                        "description": item.description,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "discount_pct": item.discount_pct,
                        "tax_rate_pct": item.tax_rate_pct,
                    }
                    for item in credit_source.items.all()
                ]
                context["items_formset"] = InvoiceItemFormSet(initial=initial_items)
                context["credit_source_invoice"] = credit_source
            else:
                context["items_formset"] = InvoiceItemFormSet()
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if form.instance.order_id and form.instance.source != "order":
            form.instance.source = "order"
        if form.instance.nature == InvoiceNatureChoices.CREDIT_NOTE and not form.instance.original_invoice_id:
            credit_source = self._credit_source_invoice()
            if credit_source:
                form.instance.original_invoice = credit_source
                if not form.instance.customer_id:
                    form.instance.customer = credit_source.customer
                if not form.instance.order_id:
                    form.instance.order = credit_source.order
        context = self.get_context_data()
        items_formset = context["items_formset"]
        if not items_formset.is_valid():
            return self.form_invalid(form)

        response = super().form_valid(form)
        items_formset.instance = self.object
        items_formset.save()

        owner = resolve_default_sales_owner(self.object, fallback_user=self.request.user)
        if owner and self.object.sales_owner_id != owner.id:
            self.object.sales_owner = owner
            self.object.save(update_fields=["sales_owner", "updated_at"])

        recalculate_invoice_totals(self.object)
        recalculate_invoice_payment_snapshot(self.object, force=False)
        run_invoice_data_quality_checks(self.object)
        reconcile_invoice_status_from_payments(self.object)

        if self.object.status == InvoiceStatusChoices.EMISE:
            prerequisites = validate_invoice_issue_prerequisites(self.object)
            if prerequisites:
                self.object.status = InvoiceStatusChoices.BROUILLON
                self.object.save(update_fields=["status", "updated_at"])
                messages.warning(
                    self.request,
                    "Facture enregistrée en brouillon: " + " ".join(prerequisites),
                )
            else:
                mark_invoice_ready_for_fne(self.object)
                if (
                    self.object.nature == InvoiceNatureChoices.CREDIT_NOTE
                    and self.object.original_invoice_id
                    and int(self.object.total_amount or 0) == int(self.object.original_invoice.total_amount or 0)
                ):
                    Invoice.objects.filter(pk=self.object.original_invoice_id).update(
                        status=InvoiceStatusChoices.ANNULEE
                    )
                    messages.success(
                        self.request,
                        "Avoir émis et facture d'origine marquée annulée.",
                    )
                else:
                    messages.success(self.request, "Facture émise avec succès.")
        else:
            messages.success(self.request, "Facture enregistrée en brouillon.")
        return response


class SalesInvoiceUpdateView(ScopedPermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "crm/sales/form.html"
    success_url = reverse_lazy("sales-list")
    permission_required = "crm.change_invoice"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = InvoiceItemFormSet(self.request.POST, instance=self.object)
        else:
            context["items_formset"] = InvoiceItemFormSet(instance=self.object)
        context["payments"] = (
            scoped_invoice_payments_queryset(
                self.request.user,
                queryset=InvoicePayment.objects.select_related("recorded_by").filter(invoice=self.object),
                context=(has_global_scope(self.request.user), resolve_scope(self.request.user)),
            )
            .order_by("-paid_at", "-pk")
        )
        context["can_add_payment"] = self.request.user.has_perm("crm.add_invoicepayment")
        context["can_delete_payment"] = self.request.user.has_perm("crm.delete_invoicepayment")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context["items_formset"]
        if not items_formset.is_valid():
            return self.form_invalid(form)

        response = super().form_valid(form)
        items_formset.instance = self.object
        items_formset.save()

        owner = resolve_default_sales_owner(self.object, fallback_user=self.request.user)
        if owner and self.object.sales_owner_id != owner.id:
            self.object.sales_owner = owner
            self.object.save(update_fields=["sales_owner", "updated_at"])

        recalculate_invoice_totals(self.object)
        recalculate_invoice_payment_snapshot(self.object, force=False)
        run_invoice_data_quality_checks(self.object)
        reconcile_invoice_status_from_payments(self.object)

        if self.object.status == InvoiceStatusChoices.EMISE:
            prerequisites = validate_invoice_issue_prerequisites(self.object)
            if prerequisites:
                self.object.status = InvoiceStatusChoices.BROUILLON
                self.object.save(update_fields=["status", "updated_at"])
                messages.warning(
                    self.request,
                    "Facture conservée en brouillon: " + " ".join(prerequisites),
                )
            else:
                mark_invoice_ready_for_fne(self.object)
                if (
                    self.object.nature == InvoiceNatureChoices.CREDIT_NOTE
                    and self.object.original_invoice_id
                    and int(self.object.total_amount or 0) == int(self.object.original_invoice.total_amount or 0)
                ):
                    Invoice.objects.filter(pk=self.object.original_invoice_id).update(
                        status=InvoiceStatusChoices.ANNULEE
                    )
                    messages.success(
                        self.request,
                        "Avoir mis à jour et facture d'origine marquée annulée.",
                    )
                else:
                    messages.success(self.request, "Facture mise à jour et émise.")
        else:
            messages.success(self.request, "Facture mise à jour.")
        return response


class SalesInvoicePrintView(ScopedPermissionRequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = Invoice
    template_name = "crm/sales/print.html"
    context_object_name = "invoice"
    permission_required = "crm.view_invoice"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payments"] = self.object.payments.select_related("recorded_by").order_by("-paid_at", "-pk")
        return context


class SalesInvoicePaymentCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = InvoicePayment
    form_class = InvoicePaymentForm
    template_name = "crm/sales/payment_form.html"
    permission_required = "crm.add_invoicepayment"

    def dispatch(self, request, *args, **kwargs):
        self.invoice = get_object_or_404(
            scoped_invoices_queryset(
                request.user,
                queryset=Invoice.objects.select_related("customer").all(),
                context=(has_global_scope(request.user), resolve_scope(request.user)),
            ),
            pk=kwargs.get("invoice_id"),
        )
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.invoice.payment_method:
            initial["payment_method"] = self.invoice.payment_method
        if self.invoice.balance_due:
            initial["amount"] = self.invoice.balance_due
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invoice"] = self.invoice
        context["payments"] = (
            scoped_invoice_payments_queryset(
                self.request.user,
                queryset=InvoicePayment.objects.select_related("recorded_by").filter(invoice=self.invoice),
                context=(has_global_scope(self.request.user), resolve_scope(self.request.user)),
            )
            .order_by("-paid_at", "-pk")
        )
        return context

    def form_valid(self, form):
        issues = validate_invoice_payment_prerequisites(
            self.invoice,
            amount=int(form.cleaned_data.get("amount") or 0),
        )
        if issues:
            form.add_error("amount", issues[0])
            messages.error(self.request, issues[0])
            return self.form_invalid(form)

        form.instance.invoice = self.invoice
        form.instance.recorded_by = self.request.user
        form.instance.source = InvoicePaymentSourceChoices.MANUAL
        response = super().form_valid(form)
        messages.success(self.request, "Paiement enregistré et facture réconciliée.")
        return response

    def get_success_url(self):
        return reverse_lazy("sales-update", kwargs={"pk": self.invoice.pk})


class SalesInvoicePaymentDeleteView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "crm.delete_invoicepayment"

    def post(self, request, invoice_id: int, payment_id: int, *args, **kwargs):
        scope_context = (has_global_scope(request.user), resolve_scope(request.user))
        invoice = get_object_or_404(
            scoped_invoices_queryset(
                request.user,
                queryset=Invoice.objects.all(),
                context=scope_context,
            ),
            pk=invoice_id,
        )
        payment = get_object_or_404(
            scoped_invoice_payments_queryset(
                request.user,
                queryset=InvoicePayment.objects.filter(invoice=invoice),
                context=scope_context,
            ),
            pk=payment_id,
        )
        payment.delete()
        messages.success(request, "Paiement supprimé et facture réconciliée.")
        return redirect("sales-update", pk=invoice.pk)


class SupportCaseListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = SupportCase
    template_name = "crm/support/list.html"
    context_object_name = "support_cases"
    paginate_by = 20
    permission_required = "crm.view_supportcase"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class SupportCaseCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = SupportCase
    form_class = SupportCaseForm
    template_name = "crm/support/form.html"
    success_url = reverse_lazy("support-list")
    permission_required = "crm.add_supportcase"


class SupportCaseUpdateView(ScopedPermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = SupportCase
    form_class = SupportCaseForm
    template_name = "crm/support/form.html"
    success_url = reverse_lazy("support-list")
    permission_required = "crm.change_supportcase"


class VisitReportListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = VisitReport
    template_name = "crm/visits/list.html"
    context_object_name = "visits"
    paginate_by = 20
    permission_required = "crm.view_visitreport"


class VisitReportCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = VisitReport
    form_class = VisitReportForm
    template_name = "crm/visits/form.html"
    success_url = reverse_lazy("visits-list")
    permission_required = "crm.add_visitreport"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Rapport de visite enregistré")
        return super().form_valid(form)


class TaskListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "crm/tasks/list.html"
    context_object_name = "tasks"
    paginate_by = 25
    permission_required = "crm.view_task"

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get("status")
        assigned = self.request.GET.get("assigned")
        if status:
            queryset = queryset.filter(status=status)
        if assigned:
            queryset = queryset.filter(assigned_to_id=assigned)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = get_user_model().objects.all()
        context["today"] = timezone.now().date()
        context["status_choices"] = Task._meta.get_field("status").choices
        return context


class TaskCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "crm/tasks/form.html"
    success_url = reverse_lazy("tasks-list")
    permission_required = "crm.add_task"


class TaskUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "crm/tasks/form.html"
    success_url = reverse_lazy("tasks-list")
    permission_required = "crm.change_task"


class InboundRequestListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = InboundRequest
    template_name = "crm/inbox/list.html"
    context_object_name = "inbound_requests"
    paginate_by = 25
    search_fields = ("name", "company", "email", "phone", "intent", "product")
    permission_required = "crm.view_inboundrequest"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("lead", "assigned_to")
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        kind = self.request.GET.get("kind")
        segment = self.request.GET.get("segment")
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if kind:
            queryset = queryset.filter(kind=kind)
        if segment:
            queryset = queryset.filter(segment=segment)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = InboundRequest._meta.get_field("status").choices
        context["priority_choices"] = InboundRequest._meta.get_field("priority").choices
        context["kind_choices"] = InboundRequest._meta.get_field("kind").choices
        context["segment_choices"] = Lead._meta.get_field("segment").choices
        return context


class InboundRequestCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = InboundRequest
    form_class = InboundRequestForm
    template_name = "crm/inbox/form.html"
    success_url = reverse_lazy("inbox-list")
    permission_required = "crm.add_inboundrequest"


class InboundRequestUpdateView(ScopedPermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = InboundRequest
    form_class = InboundRequestForm
    template_name = "crm/inbox/form.html"
    success_url = reverse_lazy("inbox-list")
    permission_required = "crm.change_inboundrequest"


class CareerApplicationListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = CareerApplication
    template_name = "crm/careers/list.html"
    context_object_name = "applications"
    paginate_by = 25
    search_fields = ("full_name", "email", "phone", "role")
    permission_required = "crm.view_careerapplication"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("inbound_request")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = CareerApplication._meta.get_field("status").choices
        return context


class CareerApplicationCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = CareerApplication
    form_class = CareerApplicationForm
    template_name = "crm/careers/form.html"
    success_url = reverse_lazy("careers-list")
    permission_required = "crm.add_careerapplication"


class CareerApplicationUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = CareerApplication
    form_class = CareerApplicationForm
    template_name = "crm/careers/form.html"
    success_url = reverse_lazy("careers-list")
    permission_required = "crm.change_careerapplication"


class NewsletterSubscriptionListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = NewsletterSubscription
    template_name = "crm/newsletter/list.html"
    context_object_name = "subscriptions"
    paginate_by = 25
    search_fields = ("email",)
    permission_required = "crm.view_newslettersubscription"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("inbound_request")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = NewsletterSubscription._meta.get_field("status").choices
        return context


class NewsletterSubscriptionCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = NewsletterSubscription
    form_class = NewsletterSubscriptionForm
    template_name = "crm/newsletter/form.html"
    success_url = reverse_lazy("newsletter-list")
    permission_required = "crm.add_newslettersubscription"


class NewsletterSubscriptionUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = NewsletterSubscription
    form_class = NewsletterSubscriptionForm
    template_name = "crm/newsletter/form.html"
    success_url = reverse_lazy("newsletter-list")
    permission_required = "crm.change_newslettersubscription"


class TerritoryListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = Territory
    template_name = "crm/territories/list.html"
    context_object_name = "territories"
    paginate_by = 25
    search_fields = ("name", "region")
    permission_required = "crm.view_territory"


class TerritoryCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Territory
    form_class = TerritoryForm
    template_name = "crm/territories/form.html"
    success_url = reverse_lazy("territories-list")
    permission_required = "crm.add_territory"


class TerritoryUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Territory
    form_class = TerritoryForm
    template_name = "crm/territories/form.html"
    success_url = reverse_lazy("territories-list")
    permission_required = "crm.change_territory"


class OutletListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = Outlet
    template_name = "crm/outlets/list.html"
    context_object_name = "outlets"
    paginate_by = 25
    search_fields = ("name", "city", "region", "address")
    permission_required = "crm.view_outlet"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("territory", "distributor")
        channel = self.request.GET.get("channel")
        status = self.request.GET.get("status")
        territory = self.request.GET.get("territory")
        if channel:
            queryset = queryset.filter(channel=channel)
        if status:
            queryset = queryset.filter(status=status)
        if territory:
            queryset = queryset.filter(territory_id=territory)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["channel_choices"] = Outlet._meta.get_field("channel").choices
        context["status_choices"] = Outlet._meta.get_field("status").choices
        context["territories"] = Territory.objects.all()
        return context


class OutletCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Outlet
    form_class = OutletForm
    template_name = "crm/outlets/form.html"
    success_url = reverse_lazy("outlets-list")
    permission_required = "crm.add_outlet"


class OutletUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Outlet
    form_class = OutletForm
    template_name = "crm/outlets/form.html"
    success_url = reverse_lazy("outlets-list")
    permission_required = "crm.change_outlet"


class PromotionListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = Promotion
    template_name = "crm/promotions/list.html"
    context_object_name = "promotions"
    paginate_by = 25
    search_fields = ("name",)
    permission_required = "crm.view_promotion"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("product").prefetch_related("outlets")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Promotion._meta.get_field("status").choices
        return context


class PromotionCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Promotion
    form_class = PromotionForm
    template_name = "crm/promotions/form.html"
    success_url = reverse_lazy("promotions-list")
    permission_required = "crm.add_promotion"


class PromotionUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Promotion
    form_class = PromotionForm
    template_name = "crm/promotions/form.html"
    success_url = reverse_lazy("promotions-list")
    permission_required = "crm.change_promotion"


class ForecastListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Forecast
    template_name = "crm/forecasts/list.html"
    context_object_name = "forecasts"
    paginate_by = 25
    permission_required = "crm.view_forecast"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer", "product", "outlet")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Forecast._meta.get_field("status").choices
        return context


class ForecastCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Forecast
    form_class = ForecastForm
    template_name = "crm/forecasts/form.html"
    success_url = reverse_lazy("forecasts-list")
    permission_required = "crm.add_forecast"


class ForecastUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Forecast
    form_class = ForecastForm
    template_name = "crm/forecasts/form.html"
    success_url = reverse_lazy("forecasts-list")
    permission_required = "crm.change_forecast"


class RoutingRuleListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = RoutingRule
    template_name = "crm/routing_rules/list.html"
    context_object_name = "routing_rules"
    paginate_by = 25
    search_fields = ("name", "region")
    permission_required = "crm.view_routingrule"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("assigned_to")
        active = self.request.GET.get("active")
        if active == "1":
            queryset = queryset.filter(active=True)
        elif active == "0":
            queryset = queryset.filter(active=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["kind_choices"] = RoutingRule._meta.get_field("kind").choices
        context["segment_choices"] = RoutingRule._meta.get_field("segment").choices
        context["channel_choices"] = RoutingRule._meta.get_field("channel_preference").choices
        return context


class RoutingRuleCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = RoutingRule
    form_class = RoutingRuleForm
    template_name = "crm/routing_rules/form.html"
    success_url = reverse_lazy("routing-rules-list")
    permission_required = "crm.add_routingrule"


class RoutingRuleUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = RoutingRule
    form_class = RoutingRuleForm
    template_name = "crm/routing_rules/form.html"
    success_url = reverse_lazy("routing-rules-list")
    permission_required = "crm.change_routingrule"


class GlobalSearchView(PermissionRequiredMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = "crm/search.html"
    permission_required = "crm.view_customer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query
        if query:
            context["customers"] = Customer.objects.filter(
                Q(name__icontains=query) | Q(code__icontains=query) | Q(city__icontains=query)
            )[:5]
            context["leads"] = Lead.objects.filter(
                Q(name__icontains=query) | Q(company__icontains=query) | Q(phone__icontains=query)
            )[:5]
            context["opportunities"] = Opportunity.objects.filter(Q(title__icontains=query))[:5]
            context["support_cases"] = SupportCase.objects.filter(
                Q(reference__icontains=query) | Q(description__icontains=query)
            )[:5]
            context["inbound_requests"] = InboundRequest.objects.filter(
                Q(name__icontains=query)
                | Q(company__icontains=query)
                | Q(phone__icontains=query)
                | Q(email__icontains=query)
                | Q(product__icontains=query)
            )[:5]
            context["career_applications"] = CareerApplication.objects.filter(
                Q(full_name__icontains=query) | Q(email__icontains=query) | Q(role__icontains=query)
            )[:5]
            context["newsletter_subscriptions"] = NewsletterSubscription.objects.filter(email__icontains=query)[:5]
            context["territories"] = Territory.objects.filter(Q(name__icontains=query) | Q(region__icontains=query))[:5]
            context["outlets"] = Outlet.objects.filter(
                Q(name__icontains=query) | Q(city__icontains=query) | Q(region__icontains=query)
            )[:5]
            context["promotions"] = Promotion.objects.filter(Q(name__icontains=query))[:5]
        return context


class AccessUserListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = get_user_model()
    template_name = "crm/access/users_list.html"
    context_object_name = "users"
    paginate_by = 40
    search_fields = ("username", "first_name", "last_name", "email")
    permission_required = "auth.view_user"

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("security_profile")
            .prefetch_related("groups")
            .order_by("username")
        )
        for user in queryset:
            UserSecurityProfile.objects.get_or_create(user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role_catalog"] = [
            {
                "name": "Direction/Propriétaire",
                "focus": "Pilotage global, gouvernance, décision stratégique",
            },
            {
                "name": "Administrateur Système",
                "focus": "Administration plateforme, sécurité, comptes et rôles",
            },
            {
                "name": "Directeur Commercial",
                "focus": "Pipeline, conversion, approbations commerciales",
            },
            {
                "name": "Commerciaux",
                "focus": "Prospection, qualification, opportunités, commandes",
            },
            {
                "name": "Technico-Commerciaux",
                "focus": "Conversion commerciale + expertise technique + visites terrain",
            },
            {
                "name": "Experts Métier",
                "focus": "Expertise par espèce/stade/objectif/région, support et recommandations",
            },
            {
                "name": "Technicien CRM & Support IT",
                "focus": "Exploitation CRM, support IT, qualité de données, SLA",
            },
            {
                "name": "Caissière",
                "focus": "Exécution commande/facturation opérationnelle",
            },
            {
                "name": "Comptable",
                "focus": "Contrôle financier, suivi commande/forecast et audit",
            },
            {
                "name": "Gouvernance & Conformité",
                "focus": "Audit trail, escalades, règles de validation",
            },
        ]
        return context


class AccessUserUpdateView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "auth.change_user"
    template_name = "crm/access/user_form.html"

    def _target(self, pk):
        user = get_object_or_404(get_user_model(), pk=pk)
        profile, _ = UserSecurityProfile.objects.get_or_create(user=user)
        return user, profile

    def get(self, request, pk):
        user, profile = self._target(pk)
        user_form = UserRoleForm(instance=user)
        profile_form = UserSecurityProfileForm(instance=profile)
        assignments = RoleAssignment.objects.filter(user=user).select_related("group", "granted_by").order_by("-created_at")[:20]
        return self._render(request, user, profile, user_form, profile_form, assignments)

    def post(self, request, pk):
        user, profile = self._target(pk)
        user_form = UserRoleForm(request.POST, instance=user)
        profile_form = UserSecurityProfileForm(request.POST, instance=profile)
        assignments = RoleAssignment.objects.filter(user=user).select_related("group", "granted_by").order_by("-created_at")[:20]
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Accès utilisateur mis à jour.")
            return redirect("access-user-update", pk=user.pk)
        return self._render(request, user, profile, user_form, profile_form, assignments)

    def _render(self, request, user, profile, user_form, profile_form, assignments):
        return render(
            request,
            self.template_name,
            {
                "user_target": user,
                "profile": profile,
                "user_form": user_form,
                "profile_form": profile_form,
                "assignments": assignments,
            },
        )


class RoleAssignmentListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = RoleAssignment
    template_name = "crm/access/assignments_list.html"
    context_object_name = "assignments"
    paginate_by = 40
    permission_required = "crm.view_roleassignment"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user", "user__security_profile", "group", "granted_by", "revoked_by")
        is_active = self.request.GET.get("active")
        scope = self.request.GET.get("scope")
        user_id = self.request.GET.get("user")
        if is_active == "1":
            queryset = queryset.filter(is_active=True)
        elif is_active == "0":
            queryset = queryset.filter(is_active=False)
        if scope:
            queryset = queryset.filter(scope=scope)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scope_choices"] = RoleAssignment._meta.get_field("scope").choices
        context["users"] = get_user_model().objects.order_by("username")
        return context


class RoleAssignmentCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = RoleAssignment
    form_class = RoleAssignmentForm
    template_name = "crm/access/assignment_form.html"
    success_url = reverse_lazy("access-assignments-list")
    permission_required = "crm.add_roleassignment"

    def form_valid(self, form):
        if not form.instance.granted_by_id:
            form.instance.granted_by = self.request.user
        messages.success(self.request, "Assignation de rôle créée.")
        return super().form_valid(form)


class RoleAssignmentUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = RoleAssignment
    form_class = RoleAssignmentForm
    template_name = "crm/access/assignment_form.html"
    success_url = reverse_lazy("access-assignments-list")
    permission_required = "crm.change_roleassignment"

    def form_valid(self, form):
        if not form.instance.granted_by_id:
            form.instance.granted_by = self.request.user
        messages.success(self.request, "Assignation de rôle mise à jour.")
        return super().form_valid(form)


class RoleAssignmentRevokeView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "crm.change_roleassignment"

    def post(self, request, pk):
        assignment = get_object_or_404(RoleAssignment, pk=pk)
        assignment.is_active = False
        assignment.revoked_by = request.user
        assignment.revoked_at = timezone.now()
        assignment.save(update_fields=["is_active", "revoked_by", "revoked_at", "updated_at"])
        messages.info(request, "Assignation révoquée.")
        return redirect("access-assignments-list")


class GovernanceAuditTrailListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = AuditTrail
    template_name = "crm/governance/audit_list.html"
    context_object_name = "events"
    paginate_by = 50
    permission_required = "crm.view_audittrail"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("actor", "content_type")
        event = self.request.GET.get("event")
        source = self.request.GET.get("source")
        if event:
            queryset = queryset.filter(event=event)
        if source:
            queryset = queryset.filter(source=source)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_choices"] = AuditTrail._meta.get_field("event").choices
        context["source_choices"] = AuditTrail._meta.get_field("source").choices
        return context


class GovernanceDataQualityListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = DataQualityIssue
    template_name = "crm/governance/data_quality_list.html"
    context_object_name = "issues"
    paginate_by = 50
    permission_required = "crm.view_dataqualityissue"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("assigned_to", "resolved_by", "content_type")
        status = self.request.GET.get("status")
        severity = self.request.GET.get("severity")
        issue_type = self.request.GET.get("issue_type")
        if status:
            queryset = queryset.filter(status=status)
        if severity:
            queryset = queryset.filter(severity=severity)
        if issue_type:
            queryset = queryset.filter(issue_type=issue_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = DataQualityIssue._meta.get_field("status").choices
        context["severity_choices"] = DataQualityIssue._meta.get_field("severity").choices
        context["type_choices"] = DataQualityIssue._meta.get_field("issue_type").choices
        return context


class GovernanceDataQualityActionView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "crm.change_dataqualityissue"

    def post(self, request, pk):
        issue = get_object_or_404(DataQualityIssue, pk=pk)
        action = request.POST.get("action")
        if action == "resolve":
            issue.status = DataQualityStatusChoices.RESOLVED
            issue.resolved_by = request.user
            issue.resolved_at = timezone.now()
            issue.save(update_fields=["status", "resolved_by", "resolved_at", "updated_at"])
            messages.success(request, f"Issue #{issue.pk} marquée comme résolue.")
        elif action == "ignore":
            issue.status = DataQualityStatusChoices.IGNORED
            issue.resolved_by = request.user
            issue.resolved_at = timezone.now()
            issue.save(update_fields=["status", "resolved_by", "resolved_at", "updated_at"])
            messages.info(request, f"Issue #{issue.pk} ignorée.")
        else:
            issue.status = DataQualityStatusChoices.IN_REVIEW
            issue.assigned_to = request.user
            issue.save(update_fields=["status", "assigned_to", "updated_at"])
            messages.info(request, f"Issue #{issue.pk} passée en revue.")
        return redirect("governance-data-quality-list")


class GovernanceEscalationListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = SlaEscalation
    template_name = "crm/governance/escalations_list.html"
    context_object_name = "escalations"
    paginate_by = 50
    permission_required = "crm.view_slaescalation"

    def get_queryset(self):
        refresh_sla_escalations()
        queryset = super().get_queryset().select_related("assigned_to", "content_type")
        status = self.request.GET.get("status")
        source_type = self.request.GET.get("source_type")
        if status:
            queryset = queryset.filter(status=status)
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = SlaEscalation._meta.get_field("status").choices
        context["source_choices"] = SlaEscalation._meta.get_field("source_type").choices
        context["level_choices"] = SlaEscalation._meta.get_field("escalation_level").choices
        return context


class GovernanceEscalationActionView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "crm.change_slaescalation"

    def post(self, request, pk):
        escalation = get_object_or_404(SlaEscalation, pk=pk)
        action = request.POST.get("action")
        if action == "ack":
            escalation.status = EscalationStatusChoices.ACK
            escalation.assigned_to = request.user
            escalation.save(update_fields=["status", "assigned_to", "updated_at"])
            messages.info(request, f"Escalade #{escalation.pk} prise en charge.")
        else:
            escalation.status = EscalationStatusChoices.RESOLVED
            escalation.resolved_at = timezone.now()
            escalation.assigned_to = request.user
            escalation.save(update_fields=["status", "resolved_at", "assigned_to", "updated_at"])
            messages.success(request, f"Escalade #{escalation.pk} clôturée.")
        return redirect("governance-escalations-list")


class GovernanceApprovalListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = ApprovalRequest
    template_name = "crm/governance/approvals_list.html"
    context_object_name = "approvals"
    paginate_by = 50
    permission_required = "crm.view_approvalrequest"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("requested_by", "assigned_to", "decided_by", "content_type")
        status = self.request.GET.get("status")
        entity_type = self.request.GET.get("entity_type")
        if status:
            queryset = queryset.filter(status=status)
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = ApprovalRequest._meta.get_field("status").choices
        context["entity_choices"] = ApprovalRequest._meta.get_field("entity_type").choices
        return context


class GovernanceApprovalActionView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "crm.change_approvalrequest"

    def post(self, request, pk):
        approval = get_object_or_404(ApprovalRequest, pk=pk)
        action = request.POST.get("action")
        note = (request.POST.get("decision_note") or "").strip()

        if action == "approve":
            approval.status = ApprovalStatusChoices.APPROVED
            messages.success(request, f"Demande #{approval.pk} approuvée.")
        elif action == "reject":
            approval.status = ApprovalStatusChoices.REJECTED
            messages.warning(request, f"Demande #{approval.pk} refusée.")
        else:
            approval.status = ApprovalStatusChoices.CANCELLED
            messages.info(request, f"Demande #{approval.pk} annulée.")

        approval.decided_by = request.user
        approval.decided_at = timezone.now()
        approval.decision_note = note
        approval.save(update_fields=["status", "decided_by", "decided_at", "decision_note", "updated_at"])

        if approval.entity_type == "order" and approval.content_object:
            order = approval.content_object
            if action == "approve" and order.status == OrderStatusChoices.DEVIS:
                order.status = OrderStatusChoices.CONFIRME
                order.save(update_fields=["status", "updated_at"])
            if action == "reject" and order.status == OrderStatusChoices.CONFIRME:
                order.status = OrderStatusChoices.DEVIS
                order.save(update_fields=["status", "updated_at"])

        return redirect("governance-approvals-list")


class SOPStudioView(PermissionRequiredMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = "crm/sop/studio.html"
    permission_required = "crm.view_dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scan_items"] = [
            {
                "domain": "Intake Omnicanal",
                "score": 5,
                "current": "5/5",
                "status": "Fort",
                "details": "Formulaires publics connectes a l'API CRM (inbound, carriere, newsletter) avec journalisation et priorisation.",
            },
            {
                "domain": "SLA et Routage",
                "score": 4,
                "current": "4/5",
                "status": "Fort",
                "details": "Priorite + SLA + routing rules en place avec moteur d'escalades et centre d'actions gouvernance.",
            },
            {
                "domain": "Qualification et Conversion",
                "score": 4,
                "current": "4/5",
                "status": "Fort",
                "details": "Lead scoring, pipeline, commandes et guardrails d'approbation (remise/credit) actifs.",
            },
            {
                "domain": "Service et Terrain",
                "score": 4,
                "current": "4/5",
                "status": "Fort",
                "details": "Support, visites et taches operationnels avec vues rolees (technico-commerciaux/experts).",
            },
            {
                "domain": "FMCG Distribution",
                "score": 4,
                "current": "4/5",
                "status": "Fort",
                "details": "Territoires, outlets, promotions et forecasts operationnels.",
            },
            {
                "domain": "Gouvernance et Audit",
                "score": 4,
                "current": "4/5",
                "status": "Fort",
                "details": "Audit trail, data quality, escalades SLA, approvals et segregation des roles implémentes.",
            },
            {
                "domain": "IAM & Securite",
                "score": 4,
                "current": "4/5",
                "status": "Fort",
                "details": "RBAC et roles scopes, UUID utilisateur, lock policy, request-id et menus dynamiques.",
            },
            {
                "domain": "Integrations Enterprise",
                "score": 2,
                "current": "2/5",
                "status": "Gap",
                "details": "Connecteurs ERP/compta, telephonie, WhatsApp Business, BI corporate a integrer.",
            },
            {
                "domain": "Analytics Executive",
                "score": 4,
                "current": "4/5",
                "status": "Fort",
                "details": "KPI, alertes et dashboard role-aware actifs; BI executive avancee reste a industrialiser.",
            },
        ]

        context["sop_steps"] = [
            {
                "id": "intake-unifie",
                "step": "1. Intake unifie",
                "owner": "Marketing Ops",
                "sla": "Temps reel",
                "deliverable": "Inbound horodate + source + consentement",
                "context": (
                    "Toutes les demandes web doivent entrer dans une file unique CRM afin d'eviter les pertes"
                    " entre marketing, ventes, support et RH."
                ),
                "use_case": (
                    "Un eleveur remplit le formulaire technique sur maridav.ci. Le CRM cree la requete avec"
                    " source Web, espece Poissons, et niveau de priorite."
                ),
            },
            {
                "id": "data-quality-gate",
                "step": "2. Data quality gate",
                "owner": "CRM Ops",
                "sla": "< 5 min",
                "deliverable": "Validation schema + dedoublonnage initial",
                "context": (
                    "Le CRM doit bloquer les fiches incompletes et fusionner les doublons pour proteger la qualite"
                    " des KPIs et du pipeline commercial."
                ),
                "use_case": (
                    "Un meme distributeur soumet deux formulaires avec emails differents. Le moteur rapproche les"
                    " identites et ouvre un seul dossier client."
                ),
            },
            {
                "id": "qualification-auto",
                "step": "3. Qualification automatique",
                "owner": "CRM Engine",
                "sla": "< 5 min",
                "deliverable": "Segment, priorite, lead score, route proposee",
                "context": (
                    "Chaque requete doit etre classee selon l'activite Maridav (volailles, porcins, poissons,"
                    " biosecurite) pour orienter la bonne equipe et accelerer la conversion."
                ),
                "use_case": (
                    "Une demande mentionne 'aliment tilapia'. Le CRM affecte le segment Poissons, attribue un score"
                    " eleve et propose un routage vers l'equipe aquaculture."
                ),
            },
            {
                "id": "assignation-routage",
                "step": "4. Assignation/Routage",
                "owner": "Sales Manager",
                "sla": "< 15 min",
                "deliverable": "Proprietaire assigne + file d'attente",
                "context": (
                    "Le routage doit tenir compte du territoire, de la charge et de l'expertise espece pour limiter"
                    " les retards et les transferts inutiles."
                ),
                "use_case": (
                    "Une demande venant de Bouake est assignee automatiquement au commercial de zone ayant le meilleur"
                    " taux de traitement sur la filiere Volailles."
                ),
            },
            {
                "id": "first-response",
                "step": "5. First response",
                "owner": "Commercial/Support",
                "sla": "1h-24h selon priorite",
                "deliverable": "Contact initial trace + statut mis a jour",
                "context": (
                    "La premiere reponse est critique pour la confiance client et le taux de conversion. Le CRM doit"
                    " tracer l'heure, le canal et le resultat du premier contact."
                ),
                "use_case": (
                    "Le commercial appelle un prospect dans le SLA, journalise l'echange dans la timeline et change le"
                    " statut de 'Nouveau' a 'En qualification'."
                ),
            },
            {
                "id": "traitement-metier",
                "step": "6. Traitement metier",
                "owner": "Sales/Support/RH",
                "sla": "Selon process",
                "deliverable": "Lead/Opportunity/Case/Application crees",
                "context": (
                    "Apres qualification, la requete doit suivre le bon flux metier: vente (lead/opportunite),"
                    " support (case), ou recrutement (application)."
                ),
                "use_case": (
                    "Un formulaire Carriere cree automatiquement une candidature RH alors qu'une demande de devis cree"
                    " un lead commercial relie au client."
                ),
            },
            {
                "id": "execution-terrain",
                "step": "7. Execution terrain",
                "owner": "Equipe technique",
                "sla": "< 72h",
                "deliverable": "Visit report + actions + checklist espece",
                "context": (
                    "Pour Maridav, la valeur se concretise sur le terrain. Les visites techniques doivent etre"
                    " standardisees par espece pour garantir un suivi homogène."
                ),
                "use_case": (
                    "Un technicien visite un elevage porcin, complete la checklist biosécurite et ajoute un plan"
                    " d'actions avec date de suivi."
                ),
            },
            {
                "id": "approvals-corporate",
                "step": "8. Approvals corporate",
                "owner": "Direction commerciale",
                "sla": "< 24h",
                "deliverable": "Decision remise/prix/credit journalisee",
                "context": (
                    "Les exceptions prix, remises ou credit doivent passer par une validation tracable pour proteger"
                    " la marge et la gouvernance corporate."
                ),
                "use_case": (
                    "Une remise de 10% sur une commande grossiste declenche une approbation manager avant confirmation"
                    " de l'offre au client."
                ),
            },
            {
                "id": "conversion-commande",
                "step": "9. Conversion commande",
                "owner": "Sales Ops",
                "sla": "< 48h",
                "deliverable": "Order + order items + outlet + statut",
                "context": (
                    "La conversion doit produire une commande complete avec lignes produit, point de vente et statut"
                    " logistique pour eviter les ecarts de livraison."
                ),
                "use_case": (
                    "Une opportunite gagnee est convertie en commande avec 3 lignes produits, rattachee a un outlet,"
                    " puis transmise a la preparation."
                ),
            },
            {
                "id": "cloture-documentee",
                "step": "10. Cloture documentee",
                "owner": "Owner dossier",
                "sla": "< 24h post action",
                "deliverable": "Motif + resultat + next action",
                "context": (
                    "Chaque dossier doit se fermer avec une trace exploitable pour l'audit et pour la reactivation"
                    " future des comptes."
                ),
                "use_case": (
                    "Le dossier est cloture avec motif 'devis refuse - prix', resultat 'perdu', et prochaine action"
                    " planifiee a 30 jours."
                ),
            },
            {
                "id": "csat-nps",
                "step": "11. CSAT/NPS",
                "owner": "Customer Success",
                "sla": "< 48h post cloture",
                "deliverable": "Score satisfaction collecte",
                "context": (
                    "La satisfaction apres traitement permet d'identifier les irritants operationnels et de prioriser"
                    " les plans d'amelioration."
                ),
                "use_case": (
                    "Apres resolution d'un ticket support, le client recoit une enquete CSAT. Le score alimente le"
                    " dashboard qualite mensuel."
                ),
            },
            {
                "id": "revue-continue",
                "step": "12. Revue continue",
                "owner": "Direction + Ops",
                "sla": "Hebdo/Mensuel",
                "deliverable": "CAPA, ajustements SLA, KPI et playbooks",
                "context": (
                    "La gouvernance 10/10 exige une revue reguliere des KPIs, ecarts SLA, et actions CAPA pour faire"
                    " evoluer les regles et playbooks."
                ),
                "use_case": (
                    "En comite mensuel, la direction voit une chute de conversion sur la filiere Poissons et decide"
                    " un plan CAPA avec nouveaux scripts commerciaux."
                ),
            },
        ]

        context["decision_blueprint"] = [
            {
                "key": "governance_model",
                "label": "Modele de gouvernance",
                "help": "Definit la profondeur de controle corporate (RACI, validation, audit).",
                "options": [
                    {"value": "enterprise", "label": "Enterprise (recommande)", "score": 12},
                    {"value": "balanced", "label": "Balanced", "score": 8},
                    {"value": "light", "label": "Light", "score": 4},
                ],
            },
            {
                "key": "sla_profile",
                "label": "Profil SLA",
                "help": "Cadence de reponse et resolution sur Inbox/Support.",
                "options": [
                    {"value": "premium", "label": "Premium 24/7 (recommande)", "score": 12},
                    {"value": "aggressive", "label": "Agressif heures ouvrables", "score": 8},
                    {"value": "standard", "label": "Standard", "score": 4},
                ],
            },
            {
                "key": "identity_resolution",
                "label": "Resolution d'identite",
                "help": "Niveau de dedoublonnage client/contact/lead.",
                "options": [
                    {"value": "mdm", "label": "MDM + fuzzy matching (recommande)", "score": 10},
                    {"value": "hybrid", "label": "Hybrid exact + manuel", "score": 6},
                    {"value": "basic", "label": "Exact match simple", "score": 3},
                ],
            },
            {
                "key": "approval_matrix",
                "label": "Matrice d'approbation",
                "help": "Validation de remises, credit, exceptions tarifaires.",
                "options": [
                    {"value": "full", "label": "Complete corporate (recommande)", "score": 12},
                    {"value": "discount_only", "label": "Remises uniquement", "score": 7},
                    {"value": "none", "label": "Sans approbation formelle", "score": 2},
                ],
            },
            {
                "key": "integration_strategy",
                "label": "Strategie d'integration externe",
                "help": "Connexion ERP/compta/BI/telephonie.",
                "options": [
                    {"value": "api_bus", "label": "API bus enterprise (recommande)", "score": 12},
                    {"value": "point_to_point", "label": "Connecteurs point a point", "score": 7},
                    {"value": "internal_only", "label": "Interne uniquement", "score": 2},
                ],
            },
            {
                "key": "analytics_tier",
                "label": "Niveau analytics",
                "help": "Maturite du pilotage de conversion et performance.",
                "options": [
                    {"value": "executive", "label": "Executive BI + cohortes (recommande)", "score": 10},
                    {"value": "enhanced", "label": "Dashboard etendu", "score": 6},
                    {"value": "basic", "label": "KPI de base", "score": 3},
                ],
            },
        ]

        context["feature_flags"] = [
            {
                "key": "audit_trail",
                "label": "Journal d'audit immutable",
                "impact": "Traçabilite corporate et conformité.",
                "score": 6,
            },
            {
                "key": "escalation_engine",
                "label": "Moteur d'escalade SLA multi-niveaux",
                "impact": "Reduction des retards critiques.",
                "score": 6,
            },
            {
                "key": "playbooks_species",
                "label": "Playbooks SOP par espece",
                "impact": "Execution homogène terrain par filiere.",
                "score": 5,
            },
            {
                "key": "price_guardrails",
                "label": "Guardrails prix/marge",
                "impact": "Controle de rentabilite commerciale.",
                "score": 5,
            },
            {
                "key": "customer_360_timeline",
                "label": "Timeline client 360 (inbound->vente->support)",
                "impact": "Vision complete pour decision rapide.",
                "score": 4,
            },
            {
                "key": "forecast_accuracy",
                "label": "Mesure Forecast Accuracy (MAPE/Bias)",
                "impact": "Pilotage S&OP plus fiable.",
                "score": 4,
            },
            {
                "key": "csat_nps",
                "label": "CSAT/NPS post-traitement",
                "impact": "Mesure satisfaction et qualite percue.",
                "score": 3,
            },
        ]

        context["role_dashboard_matrix"] = [
            {
                "slug": "direction",
                "role": "Direction/Proprietaire + Direction Generale",
                "scope": "Global corporate",
                "widgets": "KPI globaux, conversion, pipeline, gouvernance, forecast",
                "charts": "Leads + Opportunites + Commandes",
                "actions": "Validation strategique, arbitrage CAPA, pilotage priorites",
                "approvals": "Niveau final (exceptions critiques)",
                "assignment": "Vue transversale, aucun filtre restrictif",
                "context": "Decision executive et gouvernance globale de la performance CRM.",
                "use_case": "Le DG suit conversion nationale et approuve une exception de remise strategique.",
                "default_phase": "phase_1",
            },
            {
                "slug": "directeur_commercial",
                "role": "Directeur Commercial",
                "scope": "Global commercial + equipe",
                "widgets": "Pipeline, leads ouverts, SLA inbox, approbations commerciales",
                "charts": "Leads + Opportunites + Commandes",
                "actions": "Affectation, coaching equipe, validation remises/credit",
                "approvals": "Niveau manager",
                "assignment": "Pilotage portefeuille + charge equipe",
                "context": "Chef d'orchestre des conversions et de la discipline commerciale.",
                "use_case": "Valide une commande avec remise > 8% et reaffecte les leads en retard SLA.",
                "default_phase": "phase_1",
            },
            {
                "slug": "commerciaux",
                "role": "Commerciaux",
                "scope": "Portefeuille assigne + assignations actives",
                "widgets": "Leads actifs, inbox ouverte, taches, commandes en cours",
                "charts": "Leads + Opportunites",
                "actions": "Qualification, relance, creation commandes, suivi client",
                "approvals": "Consultation demandes en attente",
                "assignment": "Affectation utilisateur + scopes segment/region/client",
                "context": "Execution quotidienne du cycle conversion -> vente.",
                "use_case": "Traite un lead region Bouake, cree une opportunite puis une commande.",
                "default_phase": "phase_1",
            },
            {
                "slug": "technico_commerciaux",
                "role": "Technico-Commerciaux",
                "scope": "Portefeuille assigne + terrain",
                "widgets": "Leads, support, visites, taches terrain, SLA",
                "charts": "Leads + Opportunites",
                "actions": "Diagnostic, proposition technique, conversion et suivi terrain",
                "approvals": "Consultation + contribution dossier",
                "assignment": "Scopes segment/stage/objective/region + client/projet",
                "context": "Pont entre argumentaire commercial et preuve technique terrain.",
                "use_case": "Apres visite volaille, propose plan d'action et convertit la demande en commande.",
                "default_phase": "phase_1",
            },
            {
                "slug": "experts_metier",
                "role": "Experts Metier",
                "scope": "Scopes expertise (segment/stage/objective/region)",
                "widgets": "Support, visites, data quality metier, SLA technique",
                "charts": "Leads (scope) + support indicateurs",
                "actions": "Recommandation experte, playbook, controle execution",
                "approvals": "Avis technique pre-approbation",
                "assignment": "RoleAssignment scoping fin par filiere ou objectif",
                "context": "Garants de la qualite technique par espece et stade de production.",
                "use_case": "Expert poisson prend en charge les dossiers tilapia a fort impact.",
                "default_phase": "phase_1",
            },
            {
                "slug": "technicien_crm",
                "role": "Technicien CRM & Support IT",
                "scope": "Global exploitation plateforme",
                "widgets": "SLA, data quality, incidents support, integrite des flux",
                "charts": "Operations (focus SLA/qualite)",
                "actions": "Parametrage, correction, support utilisateurs, routing",
                "approvals": "Execution controlee (pas decision metier finale)",
                "assignment": "Global operationnel + backlog correctif",
                "context": "Assure la continuite de service et la fiabilite CRM.",
                "use_case": "Corrige une regle de routage et resorbe les escalades SLA.",
                "default_phase": "phase_1",
            },
            {
                "slug": "caissiere_comptable",
                "role": "Caissiere + Comptable",
                "scope": "Commandes/finances + controle",
                "widgets": "Commandes a traiter, exceptions credit, suivi financier",
                "charts": "Commandes (et forecast pour comptable)",
                "actions": "Execution commande, controle financier, reconciliation",
                "approvals": "Entrent dans les circuits de validation commerciale/finance",
                "assignment": "Portee operationnelle finance et execution",
                "context": "Securisent la transformation commerciale en revenu controle.",
                "use_case": "Verifie commande en attente d'approbation credit avant traitement.",
                "default_phase": "phase_2",
            },
            {
                "slug": "gouvernance_admin",
                "role": "Gouvernance & Conformite + Admin Systeme",
                "scope": "Global controle et securite",
                "widgets": "Audit trail, role assignment, data quality, escalades",
                "charts": "KPI conformite + tendances ecarts",
                "actions": "Revue controle interne, segregation des taches, hardening",
                "approvals": "Cadre et supervision des regles",
                "assignment": "Global avec habilitations critiques",
                "context": "Garantit la conformite, la traçabilite et la gouvernance IAM.",
                "use_case": "Detecte une anomalie d'acces et ajuste la matrice de permissions.",
                "default_phase": "phase_1",
            },
        ]

        context["role_phase_options"] = [
            {"value": "phase_1", "label": "Phase 1 - Critique (governance first)"},
            {"value": "phase_2", "label": "Phase 2 - Balanced (metier & UX)"},
            {"value": "phase_3", "label": "Phase 3 - Optimisation avancee"},
        ]

        context["enterprise_onboarding_template"] = {
            "meta": {
                "client": "",
                "project_code": "",
                "integration_type": "erp_compta",
                "source_system": "",
                "target_system": "crm_django",
                "owner_business": "",
                "owner_technical": "",
                "go_live_target": "",
            },
            "raci": {
                "direction_owner": "",
                "sales_director": "",
                "finance_owner": "",
                "crm_it_owner": "",
                "system_admin": "",
                "governance_owner": "",
                "integrator_owner": "",
            },
            "phase_gates": {
                "phase_0_discovery_done": False,
                "phase_1_contracts_done": False,
                "phase_2_build_done": False,
                "phase_3_validation_done": False,
                "phase_4_go_live_done": False,
            },
            "scorecard": {
                "governance": None,
                "contracts": None,
                "security": None,
                "build": None,
                "tests": None,
                "ops": None,
            },
            "notes": "",
        }

        output_path = settings.BASE_DIR.parent / "markdown" / "sop_studio_choices.json"
        saved_payload = {}
        if output_path.exists():
            try:
                saved_envelope = json.loads(output_path.read_text(encoding="utf-8"))
                if isinstance(saved_envelope, dict):
                    saved_payload = saved_envelope.get("payload") or {}
            except (json.JSONDecodeError, OSError):
                saved_payload = {}
        context["saved_sop_choices"] = saved_payload

        scan_scores = [item["score"] for item in context["scan_items"]]
        context["baseline_score"] = round((sum(scan_scores) / (len(scan_scores) * 5)) * 100) if scan_scores else 0
        return context


class SOPDiagnosticView(PermissionRequiredMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = "crm/sop/diagnostic.html"
    permission_required = "crm.view_dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        diagnostic_path = settings.BASE_DIR.parent / "markdown" / "diagnostic_site_crm_optimisations.md"
        markdown_content = ""
        if diagnostic_path.exists():
            try:
                markdown_content = diagnostic_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                markdown_content = diagnostic_path.read_text(encoding="latin-1")

        if not markdown_content:
            markdown_content = (
                "# Diagnostic indisponible\n\n"
                "Le fichier `markdown/diagnostic_site_crm_optimisations.md` est introuvable."
            )

        try:
            relative_path = diagnostic_path.relative_to(settings.BASE_DIR.parent)
        except ValueError:
            relative_path = diagnostic_path

        context["diagnostic_markdown"] = markdown_content
        context["diagnostic_source_file"] = str(relative_path)
        return context


class SOPStudioSaveView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "crm.view_dashboard"

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"ok": False, "error": "Payload JSON invalide."}, status=400)

        enterprise_checklist = payload.get("enterprise_checklist")
        if enterprise_checklist is not None and not isinstance(enterprise_checklist, dict):
            return JsonResponse({"ok": False, "error": "enterprise_checklist doit etre un objet JSON."}, status=400)

        if isinstance(enterprise_checklist, dict):
            scorecard = enterprise_checklist.get("scorecard") or {}
            keys = ["governance", "contracts", "security", "build", "tests", "ops"]
            values = []
            valid = True
            for key in keys:
                value = scorecard.get(key)
                if value is None:
                    valid = False
                    break
                try:
                    numeric = float(value)
                except (TypeError, ValueError):
                    valid = False
                    break
                values.append(max(0.0, min(5.0, numeric)))
            if valid:
                readiness_score = round((sum(values) / 30.0) * 100)
                payload["enterprise_readiness_server"] = {
                    "score": readiness_score,
                    "decision": "GO enterprise" if readiness_score >= 85 else "GO conditionnel" if readiness_score >= 70 else "NO GO",
                }

        output_path = settings.BASE_DIR.parent / "markdown" / "sop_studio_choices.json"
        history = []
        if output_path.exists():
            try:
                previous = json.loads(output_path.read_text(encoding="utf-8"))
                if isinstance(previous, dict):
                    history = previous.get("history") or []
            except (json.JSONDecodeError, OSError):
                history = []

        history.append(
            {
                "saved_at": timezone.now().isoformat(),
                "saved_by": request.user.username,
                "projected_score": payload.get("projected_score"),
                "delivery_mode": payload.get("delivery_mode"),
                "business_focus": payload.get("business_focus"),
            }
        )

        envelope = {
            "saved_at": timezone.now().isoformat(),
            "saved_by": request.user.username,
            "payload": payload,
            "history": history[-50:],
        }
        output_path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")

        return JsonResponse(
            {
                "ok": True,
                "message": "Choix SOP enregistrés.",
                "saved_to": "markdown/sop_studio_choices.json",
            }
        )


# ---------------------------------------------------------------------------
# Phase 1 — Stock, lots & péremption
# ---------------------------------------------------------------------------


class WarehouseListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = Warehouse
    template_name = "crm/stock/warehouses_list.html"
    context_object_name = "warehouses"
    paginate_by = 25
    search_fields = ("name", "code", "city", "region")
    permission_required = "crm.view_warehouse"

    def get_queryset(self):
        return super().get_queryset().select_related("territory", "manager")


class WarehouseCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = "crm/stock/warehouse_form.html"
    success_url = reverse_lazy("warehouses-list")
    permission_required = "crm.add_warehouse"


class WarehouseUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = "crm/stock/warehouse_form.html"
    success_url = reverse_lazy("warehouses-list")
    permission_required = "crm.change_warehouse"


class StockLotListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = StockLot
    template_name = "crm/stock/lots_list.html"
    context_object_name = "lots"
    paginate_by = 30
    search_fields = ("lot_code", "product__name", "product__sku", "supplier_reference")
    permission_required = "crm.view_stocklot"

    def get_queryset(self):
        qs = super().get_queryset().select_related("product", "warehouse")
        warehouse = self.request.GET.get("warehouse")
        status = self.request.GET.get("status")
        alert = self.request.GET.get("alert")
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        if status:
            qs = qs.filter(status=status)
        today = timezone.localdate()
        if alert == "expired":
            qs = qs.filter(expiry_date__lt=today)
        elif alert == "near":
            qs = qs.filter(expiry_date__gte=today, expiry_date__lte=today + timezone.timedelta(days=30))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["warehouses"] = Warehouse.objects.filter(is_active=True)
        context["status_choices"] = StockLotStatusChoices.choices
        return context


class StockLotCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = StockLot
    form_class = StockLotForm
    template_name = "crm/stock/lot_form.html"
    success_url = reverse_lazy("stock-lots-list")
    permission_required = "crm.add_stocklot"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.quantity_on_hand = 0
        self.object.save()
        initial = self.object.quantity_initial or 0
        if initial and initial > 0:
            movement = StockMovement(
                lot=self.object,
                movement_type=StockMovementTypeChoices.ENTREE,
                quantity=initial,
                reason="Réception initiale du lot",
                occurred_at=timezone.now(),
                recorded_by=self.request.user,
            )
            apply_stock_movement(movement)
        messages.success(self.request, "Lot créé et entrée en stock enregistrée.")
        return redirect(self.success_url)


class StockLotUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = StockLot
    form_class = StockLotForm
    template_name = "crm/stock/lot_form.html"
    success_url = reverse_lazy("stock-lots-list")
    permission_required = "crm.change_stocklot"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movements"] = self.object.movements.select_related("order", "invoice")[:30]
        return context


class StockMovementListView(PermissionRequiredMixin, LoginRequiredMixin, SearchableListMixin, generic.ListView):
    model = StockMovement
    template_name = "crm/stock/movements_list.html"
    context_object_name = "movements"
    paginate_by = 40
    search_fields = ("lot__lot_code", "lot__product__name", "reason")
    permission_required = "crm.view_stockmovement"

    def get_queryset(self):
        qs = super().get_queryset().select_related("lot", "lot__product", "lot__warehouse", "recorded_by")
        mtype = self.request.GET.get("type")
        if mtype:
            qs = qs.filter(movement_type=mtype)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type_choices"] = StockMovementTypeChoices.choices
        return context


class StockMovementCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = "crm/stock/movement_form.html"
    success_url = reverse_lazy("stock-movements-list")
    permission_required = "crm.add_stockmovement"

    def get_initial(self):
        initial = super().get_initial()
        lot_id = self.request.GET.get("lot")
        if lot_id:
            initial["lot"] = lot_id
        return initial

    def form_valid(self, form):
        from django.core.exceptions import ValidationError

        movement = form.save(commit=False)
        movement.recorded_by = self.request.user
        try:
            apply_stock_movement(movement)
        except ValidationError as exc:
            for message in getattr(exc, "messages", [str(exc)]):
                form.add_error(None, message)
            return self.form_invalid(form)
        messages.success(self.request, "Mouvement de stock enregistré.")
        return redirect(self.success_url)


class StockDashboardView(PermissionRequiredMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = "crm/stock/dashboard.html"
    permission_required = "crm.view_stocklot"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        active_lots = StockLot.objects.filter(
            status__in=[StockLotStatusChoices.DISPONIBLE, StockLotStatusChoices.RESERVE]
        ).select_related("product", "warehouse")

        context["lots_total"] = StockLot.objects.count()
        context["stock_value"] = sum(
            int(lot.quantity_on_hand or 0) * int(lot.unit_cost or 0) for lot in active_lots
        )
        expired = StockLot.objects.filter(
            expiry_date__lt=today
        ).exclude(status=StockLotStatusChoices.EPUISE).select_related("product", "warehouse")
        near = StockLot.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timezone.timedelta(days=30),
        ).exclude(status=StockLotStatusChoices.EPUISE).select_related("product", "warehouse")
        context["expired_lots"] = expired[:20]
        context["expired_count"] = expired.count()
        context["near_expiry_lots"] = near.order_by("expiry_date")[:20]
        context["near_expiry_count"] = near.count()

        low_products = [p for p in Product.objects.filter(status="actif") if p.is_stock_low]
        context["low_stock_products"] = low_products[:20]
        context["low_stock_count"] = len(low_products)

        context["recent_movements"] = (
            StockMovement.objects.select_related("lot", "lot__product", "recorded_by")
            .order_by("-occurred_at")[:10]
        )
        return context


# ---------------------------------------------------------------------------
# Phase 2 — Encours crédit & créances âgées
# ---------------------------------------------------------------------------


class ReceivablesView(PermissionRequiredMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = "crm/finance/receivables.html"
    permission_required = "crm.view_invoice"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Portée : les profils de direction/reporting voient l'encours global ;
        # les commerciaux / technico-commerciaux ne voient QUE leur portefeuille
        # (clients qui leur sont liés). Le cloisonnement est appliqué par
        # scoped_customers_queryset ; on l'expose pour l'afficher clairement.
        is_global_scope = has_global_scope(self.request.user)
        customers_qs = scoped_customers_queryset(self.request.user)
        overview = receivables_overview(customers_qs)
        rows = overview["rows"]

        only = self.request.GET.get("filter")
        if only == "overdue":
            rows = [r for r in rows if r["aging"]["overdue"] > 0]
        elif only == "over_limit":
            rows = [r for r in rows if r["over_limit"] or r["credit_hold"]]

        context["rows"] = rows
        context["totals"] = overview["totals"]
        context["filter"] = only or ""
        context["customers_with_balance"] = len(overview["rows"])
        context["is_global_scope"] = is_global_scope
        return context


# ---------------------------------------------------------------------------
# Phase 4 — Objectifs commerciaux & tableau de bord financier
# ---------------------------------------------------------------------------


class SalesTargetListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    model = SalesTarget
    template_name = "crm/targets/list.html"
    context_object_name = "targets"
    paginate_by = 30
    permission_required = "crm.view_salestarget"

    def get_queryset(self):
        qs = super().get_queryset().select_related("owner", "territory")
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")
        if year:
            qs = qs.filter(period_year=year)
        if month:
            qs = qs.filter(period_month=month)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = []
        for target in context["targets"]:
            rows.append({"target": target, "summary": sales_performance.target_summary(target)})
        context["rows"] = rows
        context["months"] = MONTH_CHOICES
        context["current_year"] = timezone.localdate().year
        return context


class SalesTargetCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = SalesTarget
    form_class = SalesTargetForm
    template_name = "crm/targets/form.html"
    success_url = reverse_lazy("targets-list")
    permission_required = "crm.add_salestarget"

    def get_initial(self):
        initial = super().get_initial()
        today = timezone.localdate()
        initial.setdefault("period_year", today.year)
        initial.setdefault("period_month", today.month)
        return initial


class SalesTargetUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = SalesTarget
    form_class = SalesTargetForm
    template_name = "crm/targets/form.html"
    success_url = reverse_lazy("targets-list")
    permission_required = "crm.change_salestarget"


class SalesPerformanceView(PermissionRequiredMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = "crm/finance/performance.html"
    # Pilotage financier consolidé (CA global, commissions) : réservé aux profils
    # de direction / reporting via view_reports, et non à tout compte connecté.
    permission_required = "crm.view_reports"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        try:
            year = int(self.request.GET.get("year", today.year))
            month = int(self.request.GET.get("month", today.month))
        except (TypeError, ValueError):
            year, month = today.year, today.month

        overview = sales_performance.finance_overview(year, month)
        receivables = receivables_overview(scoped_customers_queryset(self.request.user))

        targets = SalesTarget.objects.filter(
            period_year=year, period_month=month
        ).select_related("owner", "territory")
        target_rows = [
            {"target": t, "summary": sales_performance.target_summary(t)} for t in targets
        ]
        target_rows.sort(key=lambda r: r["summary"]["achievement_pct"] or 0, reverse=True)

        context.update(
            {
                "year": year,
                "month": month,
                "months": MONTH_CHOICES,
                "month_label": dict(MONTH_CHOICES).get(month, ""),
                "month_ca": overview["month_ca"],
                "year_ca": overview["year_ca"],
                "invoices_count": overview["invoices_count"],
                "outstanding_total": receivables["totals"]["total"],
                "overdue_total": receivables["totals"]["overdue"],
                "target_rows": target_rows,
                "ca_by_commercial": sales_performance.ca_by_commercial(year, month),
                "ca_by_species": sales_performance.ca_by_species(year, month),
                "top_products": sales_performance.top_products(year, month),
                "monthly_series": sales_performance.monthly_ca_series(year),
                "year_options": list(range(today.year - 3, today.year + 1)),
            }
        )
        return context
