from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, IntegerField, Q, Sum
from django.middleware.csrf import get_token
from django.utils import timezone
from rest_framework import generics, permissions, response, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView

from crm.models import (
    ApprovalPolicy,
    ApprovalRequest,
    AuditTrail,
    CareerApplication,
    Contact,
    Customer,
    DataQualityIssue,
    Forecast,
    InboundRequest,
    Invoice,
    InvoiceItem,
    InvoicePayment,
    Lead,
    LeadStatusChoices,
    NewsletterSubscription,
    Opportunity,
    OpportunityStageChoices,
    Order,
    OrderItem,
    Product,
    ProductCategory,
    Promotion,
    PromotionStatusChoices,
    RoleAssignment,
    RoutingRule,
    SlaEscalation,
    Territory,
    Outlet,
    SupportStatusChoices,
    SupportCase,
    Task,
    UserSecurityProfile,
    VisitReport,
)
from crm.services.access_scope import has_global_scope, resolve_scope, scoped_queryset_for_model
from crm.services.observability import build_observability_summary
from crm.services.sales import validate_invoice_payment_prerequisites, validate_order_fne_delivery_gate

from .serializers import (
    ApprovalPolicySerializer,
    ApprovalRequestSerializer,
    AuditTrailSerializer,
    ContactSerializer,
    CustomerSerializer,
    DataQualityIssueSerializer,
    ForecastSerializer,
    LeadSerializer,
    InboundRequestSerializer,
    InvoiceItemSerializer,
    InvoicePaymentSerializer,
    InvoiceSerializer,
    CareerApplicationSerializer,
    NewsletterSubscriptionSerializer,
    OpportunitySerializer,
    OrderSerializer,
    OrderItemSerializer,
    ProductCategorySerializer,
    ProductSerializer,
    PromotionSerializer,
    RoleAssignmentSerializer,
    RoutingRuleSerializer,
    SlaEscalationSerializer,
    TerritorySerializer,
    OutletSerializer,
    PublicLeadCreateSerializer,
    PublicCareerApplicationSerializer,
    PublicNewsletterSubscriptionSerializer,
    SupportCaseSerializer,
    TaskSerializer,
    UserSerializer,
    UserSecurityProfileSerializer,
    VisitReportSerializer,
)
from .permissions import DashboardOrReportingPermission, ObservabilityPermission, StrictDjangoModelPermissions

User = get_user_model()


class ScopedAPIViewMixin:
    def _is_scope_enforced(self) -> bool:
        return bool(getattr(settings, "API_SECURITY_STRICT_MODE", False))

    def _scope_context(self):
        if not hasattr(self, "_cached_scope_context"):
            self._cached_scope_context = (has_global_scope(self.request.user), resolve_scope(self.request.user))
        return self._cached_scope_context

    def _apply_scope(self, queryset):
        if not self._is_scope_enforced():
            return queryset
        return scoped_queryset_for_model(self.request.user, queryset, context=self._scope_context())


class ScopedReadOnlyModelViewSet(ScopedAPIViewMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [StrictDjangoModelPermissions]

    def get_queryset(self):
        return self._apply_scope(super().get_queryset())


class ScopedModelViewSet(ScopedAPIViewMixin, viewsets.ModelViewSet):
    permission_classes = [StrictDjangoModelPermissions]
    scoped_related_fields: dict[str, type] = {}

    def get_queryset(self):
        return self._apply_scope(super().get_queryset())

    def _validate_related_scope(self, validated_data):
        if not self._is_scope_enforced():
            return
        for field, model_cls in self.scoped_related_fields.items():
            if field not in validated_data:
                continue
            value = validated_data.get(field)
            if value is None:
                continue
            if hasattr(value, "__iter__") and not hasattr(value, "pk"):
                values = list(value)
            else:
                values = [value]
            allowed_queryset = self._apply_scope(model_cls.objects.all())
            for candidate in values:
                if candidate is None:
                    continue
                if not allowed_queryset.filter(pk=candidate.pk).exists():
                    raise PermissionDenied(f"Scope insuffisant pour le champ `{field}`.")

    def perform_create(self, serializer):
        self._validate_related_scope(serializer.validated_data)
        serializer.save()

    def perform_update(self, serializer):
        self._validate_related_scope(serializer.validated_data)
        serializer.save()


class CsrfTokenView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth_csrf"

    def get(self, request, *args, **kwargs):
        return response.Response({"csrfToken": get_token(request)})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return response.Response(UserSerializer(request.user, context={"request": request}).data)


class KpiSummaryView(ScopedAPIViewMixin, APIView):
    permission_classes = [DashboardOrReportingPermission]

    def get(self, request, *args, **kwargs):
        now = timezone.now()
        start = now - timedelta(days=7)
        prev_start = now - timedelta(days=14)

        inbound_queryset = self._apply_scope(InboundRequest.objects.all())
        leads_queryset = self._apply_scope(Lead.objects.all())
        opportunities_queryset = self._apply_scope(Opportunity.objects.all())
        support_queryset = self._apply_scope(SupportCase.objects.all())
        outlets_queryset = self._apply_scope(Outlet.objects.all())
        promotions_queryset = self._apply_scope(Promotion.objects.all())
        forecasts_queryset = self._apply_scope(Forecast.objects.all())
        orders_queryset = self._apply_scope(Order.objects.all())
        order_items_queryset = self._apply_scope(OrderItem.objects.select_related("order").all())
        approvals_queryset = self._apply_scope(ApprovalRequest.objects.all())
        data_quality_queryset = self._apply_scope(DataQualityIssue.objects.all())
        escalations_queryset = self._apply_scope(SlaEscalation.objects.all())
        audit_queryset = self._apply_scope(AuditTrail.objects.all())
        invoices_queryset = self._apply_scope(Invoice.objects.all())

        inbound_total = inbound_queryset.count()
        inbound_week = inbound_queryset.filter(created_at__gte=start).count()
        inbound_prev = inbound_queryset.filter(created_at__gte=prev_start, created_at__lt=start).count()
        inbound_change = None
        if inbound_prev:
            inbound_change = round(((inbound_week - inbound_prev) / inbound_prev) * 100, 1)

        leads_total = leads_queryset.count()
        leads_converted = leads_queryset.filter(status=LeadStatusChoices.CONVERTI).count()
        conversion_rate = round((leads_converted / leads_total) * 100, 1) if leads_total else 0.0

        pipeline_value = (
            opportunities_queryset.exclude(stage=OpportunityStageChoices.PERDU).aggregate(total=Sum("expected_value"))["total"]
            or 0
        )

        support_open = support_queryset.filter(
            status__in=[SupportStatusChoices.OUVERT, SupportStatusChoices.EN_COURS]
        ).count()

        response_avg = (
            leads_queryset.exclude(status=LeadStatusChoices.NOUVEAU)
            .annotate(
                delta=ExpressionWrapper(F("updated_at") - F("created_at"), output_field=DurationField())
            )
            .aggregate(avg=Avg("delta"))
            .get("avg")
        )
        response_hours = round(response_avg.total_seconds() / 3600, 1) if response_avg else 0.0

        inbound_by_kind = list(inbound_queryset.values("kind").annotate(count=Count("id")).order_by("-count"))
        inbound_by_segment = list(inbound_queryset.values("segment").annotate(count=Count("id")).order_by("-count"))
        inbound_by_channel = list(
            inbound_queryset.values("channel_preference").annotate(count=Count("id")).order_by("-count")
        )

        leads_by_status = list(leads_queryset.values("status").annotate(count=Count("id")).order_by("-count"))
        leads_by_segment = list(
            leads_queryset.values("segment").annotate(
                total=Count("id"),
                converted=Count("id", filter=Q(status=LeadStatusChoices.CONVERTI)),
            )
        )
        conversion_by_segment = [
            {
                "segment": row["segment"] or "non_specifie",
                "total": row["total"],
                "converted": row["converted"],
                "conversion_rate": round((row["converted"] / row["total"]) * 100, 1) if row["total"] else 0.0,
            }
            for row in leads_by_segment
        ]

        pipeline_by_stage = list(
            opportunities_queryset.values("stage")
            .annotate(count=Count("id"), value=Sum("expected_value"))
            .order_by("-count")
        )

        active_outlets = outlets_queryset.filter(status="actif").count()
        total_outlets = outlets_queryset.count()
        targeted_outlets = outlets_queryset.filter(promotions__status=PromotionStatusChoices.ACTIF).distinct().count()
        promotion_coverage_pct = round((targeted_outlets / total_outlets) * 100, 1) if total_outlets else 0.0
        active_promotions = promotions_queryset.filter(status=PromotionStatusChoices.ACTIF).count()
        forecasts_month = forecasts_queryset.filter(period__month=now.month, period__year=now.year).count()
        forecasts_quantity = (
            forecasts_queryset.filter(period__month=now.month, period__year=now.year).aggregate(total=Sum("expected_quantity"))["total"]
            or 0
        )

        territory_coverage = [
            {"territory": row["territory__name"] or "Non assigne", "count": row["count"]}
            for row in outlets_queryset.values("territory__name").annotate(count=Count("id")).order_by("-count")
        ]

        order_revenue = (
            order_items_queryset.aggregate(
                total=Sum(ExpressionWrapper(F("quantity") * F("unit_price"), output_field=IntegerField()))
            )["total"]
            or 0
        )
        orders_total = orders_queryset.count()
        orders_delivered = orders_queryset.filter(status="livre").count()
        invoices_total = invoices_queryset.count()
        invoices_emitted = invoices_queryset.exclude(status="brouillon").count()
        invoices_fne_pending = invoices_queryset.filter(fne_status="pending").count()
        approvals_pending = approvals_queryset.filter(status="pending").count()
        data_quality_open = data_quality_queryset.filter(status__in=["open", "in_review"]).count()
        escalations_open = escalations_queryset.filter(status__in=["open", "ack"]).count()
        audit_events_24h = audit_queryset.filter(created_at__gte=now - timedelta(hours=24)).count()

        return response.Response(
            {
                "inbound": {
                    "total": inbound_total,
                    "week": inbound_week,
                    "change_pct": inbound_change,
                },
                "conversion_rate": conversion_rate,
                "pipeline_value": pipeline_value,
                "support_open": support_open,
                "response_hours": response_hours,
                "inbound_by_kind": inbound_by_kind,
                "inbound_by_segment": inbound_by_segment,
                "inbound_by_channel": inbound_by_channel,
                "leads_by_status": leads_by_status,
                "conversion_by_segment": conversion_by_segment,
                "pipeline_by_stage": pipeline_by_stage,
                "outlets": {"total": total_outlets, "active": active_outlets},
                "territory_coverage": territory_coverage,
                "promotions_active": active_promotions,
                "promotions_coverage_pct": promotion_coverage_pct,
                "forecasts_month": forecasts_month,
                "forecasts_quantity": forecasts_quantity,
                "orders_total": orders_total,
                "orders_delivered": orders_delivered,
                "orders_revenue": order_revenue,
                "invoices_total": invoices_total,
                "invoices_emitted": invoices_emitted,
                "invoices_fne_pending": invoices_fne_pending,
                "approvals_pending": approvals_pending,
                "data_quality_open": data_quality_open,
                "escalations_open": escalations_open,
                "audit_events_24h": audit_events_24h,
            }
        )


class AlertsSummaryView(ScopedAPIViewMixin, APIView):
    permission_classes = [DashboardOrReportingPermission]

    def get(self, request, *args, **kwargs):
        now = timezone.now()
        alerts = []

        overdue_inbound = self._apply_scope(
            InboundRequest.objects.filter(
                first_response_at__isnull=True,
                first_response_due_at__lt=now,
            )
        ).order_by("first_response_due_at")[:10]
        for inbound in overdue_inbound:
            alerts.append(
                {
                    "type": "sla_inbound",
                    "severity": "high",
                    "message": f"Demande en retard: {inbound.name or inbound.email or 'Demande web'}",
                    "entity_id": inbound.id,
                    "due_at": inbound.first_response_due_at,
                }
            )

        overdue_support = self._apply_scope(
            SupportCase.objects.filter(
                status__in=[SupportStatusChoices.OUVERT, SupportStatusChoices.EN_COURS],
                due_date__isnull=False,
                due_date__lt=now.date(),
            )
        ).order_by("due_date")[:10]
        for case in overdue_support:
            alerts.append(
                {
                    "type": "sla_support",
                    "severity": "high",
                    "message": f"Ticket support en retard: {case.reference}",
                    "entity_id": case.id,
                    "due_at": case.due_date,
                }
            )

        promotions_ending = self._apply_scope(
            Promotion.objects.filter(
                status=PromotionStatusChoices.ACTIF,
                end_date__isnull=False,
                end_date__lte=now.date() + timedelta(days=7),
            )
        ).order_by("end_date")[:10]
        for promo in promotions_ending:
            alerts.append(
                {
                    "type": "promo_ending",
                    "severity": "medium",
                    "message": f"Promotion se termine bientot: {promo.name}",
                    "entity_id": promo.id,
                    "due_at": promo.end_date,
                }
            )

        pending_approvals = self._apply_scope(ApprovalRequest.objects.filter(status="pending")).order_by("-requested_at")[:10]
        for item in pending_approvals:
            alerts.append(
                {
                    "type": "approval_pending",
                    "severity": "medium",
                    "message": f"Approbation en attente: {item.get_entity_type_display()} #{item.object_id}",
                    "entity_id": item.id,
                    "due_at": item.requested_at,
                }
            )

        critical_quality = self._apply_scope(
            DataQualityIssue.objects.filter(
                status__in=["open", "in_review"], severity__in=["high", "critical"]
            )
        ).order_by("-created_at")[:10]
        for item in critical_quality:
            alerts.append(
                {
                    "type": "data_quality",
                    "severity": "high",
                    "message": item.message,
                    "entity_id": item.id,
                    "due_at": item.created_at,
                }
            )

        return response.Response({"alerts": alerts})


class GlobalSearchAPIView(ScopedAPIViewMixin, APIView):
    permission_classes = [DashboardOrReportingPermission]

    def get(self, request, *args, **kwargs):
        query = (request.GET.get("q") or "").strip()
        if not query:
            return response.Response(
                {
                    "query": query,
                    "customers": [],
                    "leads": [],
                    "opportunities": [],
                    "support_cases": [],
                    "tasks": [],
                    "products": [],
                }
            )

        customers_qs = self._apply_scope(Customer.objects.all())
        leads_qs = self._apply_scope(Lead.objects.all())
        opportunities_qs = self._apply_scope(Opportunity.objects.all())
        support_qs = self._apply_scope(SupportCase.objects.all())
        tasks_qs = self._apply_scope(Task.objects.all())
        products_qs = self._apply_scope(Product.objects.all())

        customers = list(
            customers_qs.filter(
                Q(name__icontains=query) | Q(code__icontains=query) | Q(city__icontains=query)
            )
            .values("id", "name", "code", "city", "region")[:8]
        )
        leads = list(
            leads_qs.filter(
                Q(name__icontains=query) | Q(company__icontains=query) | Q(phone__icontains=query)
            )
            .values("id", "name", "company", "phone", "status")[:8]
        )
        opportunities = list(
            opportunities_qs.filter(Q(title__icontains=query))
            .values("id", "title", "stage", "expected_value", "customer_id")[:8]
        )
        support_cases = list(
            support_qs.filter(
                Q(reference__icontains=query) | Q(description__icontains=query)
            )
            .values("id", "reference", "status", "priority", "customer_id")[:8]
        )
        tasks = list(
            tasks_qs.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
            .values("id", "title", "status", "due_date", "assigned_to_id")[:8]
        )
        products = list(
            products_qs.filter(Q(name__icontains=query) | Q(sku__icontains=query))
            .values("id", "name", "sku", "status", "category_id")[:8]
        )
        return response.Response(
            {
                "query": query,
                "customers": customers,
                "leads": leads,
                "opportunities": opportunities,
                "support_cases": support_cases,
                "tasks": tasks,
                "products": products,
            }
        )


class ObservabilitySummaryView(APIView):
    permission_classes = [ObservabilityPermission]

    def get(self, request, *args, **kwargs):
        raw_window = request.query_params.get("window_minutes")
        window_minutes = None
        if raw_window:
            try:
                window_minutes = int(raw_window)
            except ValueError as exc:
                raise ValidationError({"window_minutes": "Valeur entière attendue."}) from exc
            if window_minutes < 1 or window_minutes > 120:
                raise ValidationError({"window_minutes": "La fenêtre doit être comprise entre 1 et 120 minutes."})

        summary = build_observability_summary(window_minutes=window_minutes)
        summary["request_id"] = getattr(request, "request_id", "")
        return response.Response(summary)


class PublicLeadCreateAPIView(generics.CreateAPIView):
    serializer_class = PublicLeadCreateSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "public_inbound"

    def get_client_ip(self):
        forwarded = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.request.META.get("REMOTE_ADDR")

    def perform_create(self, serializer):
        serializer.save(
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )


class PublicCareerCreateAPIView(generics.CreateAPIView):
    serializer_class = PublicCareerApplicationSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    throttle_scope = "public_careers"

    def get_client_ip(self):
        forwarded = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.request.META.get("REMOTE_ADDR")

    def perform_create(self, serializer):
        serializer.save(
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )


class PublicNewsletterCreateAPIView(generics.CreateAPIView):
    serializer_class = PublicNewsletterSubscriptionSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "public_newsletter"

    def get_client_ip(self):
        forwarded = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.request.META.get("REMOTE_ADDR")

    def perform_create(self, serializer):
        serializer.save(
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )


class CustomerViewSet(ScopedModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class UserViewSet(ScopedReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True).order_by("first_name", "last_name", "username")
    serializer_class = UserSerializer


class UserSecurityProfileViewSet(ScopedModelViewSet):
    queryset = UserSecurityProfile.objects.select_related("user").all()
    serializer_class = UserSecurityProfileSerializer


class RoleAssignmentViewSet(ScopedModelViewSet):
    queryset = RoleAssignment.objects.select_related("user", "group", "granted_by", "revoked_by").all()
    serializer_class = RoleAssignmentSerializer


class TerritoryViewSet(ScopedModelViewSet):
    queryset = Territory.objects.all()
    serializer_class = TerritorySerializer


class OutletViewSet(ScopedModelViewSet):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    scoped_related_fields = {
        "territory": Territory,
        "distributor": Customer,
    }


class ContactViewSet(ScopedModelViewSet):
    serializer_class = ContactSerializer
    scoped_related_fields = {"customer": Customer}

    def get_queryset(self):
        queryset = self._apply_scope(Contact.objects.select_related("customer").all())
        customer = self.request.query_params.get("customer")
        if customer:
            queryset = queryset.filter(customer_id=customer)
        return queryset


class LeadViewSet(ScopedModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class InboundRequestViewSet(ScopedModelViewSet):
    queryset = InboundRequest.objects.all()
    serializer_class = InboundRequestSerializer
    scoped_related_fields = {"lead": Lead}


class CareerApplicationViewSet(ScopedModelViewSet):
    queryset = CareerApplication.objects.all()
    serializer_class = CareerApplicationSerializer
    scoped_related_fields = {"inbound_request": InboundRequest}


class NewsletterSubscriptionViewSet(ScopedModelViewSet):
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    scoped_related_fields = {"inbound_request": InboundRequest}


class ApprovalPolicyViewSet(ScopedModelViewSet):
    queryset = ApprovalPolicy.objects.all()
    serializer_class = ApprovalPolicySerializer


class ApprovalRequestViewSet(ScopedModelViewSet):
    queryset = ApprovalRequest.objects.all()
    serializer_class = ApprovalRequestSerializer


class DataQualityIssueViewSet(ScopedModelViewSet):
    queryset = DataQualityIssue.objects.all()
    serializer_class = DataQualityIssueSerializer


class SlaEscalationViewSet(ScopedModelViewSet):
    queryset = SlaEscalation.objects.all()
    serializer_class = SlaEscalationSerializer


class AuditTrailViewSet(ScopedReadOnlyModelViewSet):
    queryset = AuditTrail.objects.all()
    serializer_class = AuditTrailSerializer


class OpportunityViewSet(ScopedModelViewSet):
    serializer_class = OpportunitySerializer
    scoped_related_fields = {
        "customer": Customer,
        "lead": Lead,
    }

    def get_queryset(self):
        queryset = self._apply_scope(Opportunity.objects.select_related("customer", "lead").all())
        customer = self.request.query_params.get("customer")
        stage = self.request.query_params.get("stage")
        assigned_to = self.request.query_params.get("assigned_to")
        if customer:
            queryset = queryset.filter(customer_id=customer)
        if stage:
            queryset = queryset.filter(stage=stage)
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        return queryset


class PromotionViewSet(ScopedModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    scoped_related_fields = {"outlets": Outlet}


class ForecastViewSet(ScopedModelViewSet):
    queryset = Forecast.objects.all()
    serializer_class = ForecastSerializer
    scoped_related_fields = {
        "customer": Customer,
        "outlet": Outlet,
    }


class RoutingRuleViewSet(ScopedModelViewSet):
    queryset = RoutingRule.objects.all()
    serializer_class = RoutingRuleSerializer


class ProductCategoryViewSet(ScopedModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductViewSet(ScopedModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(ScopedModelViewSet):
    serializer_class = OrderSerializer
    scoped_related_fields = {
        "customer": Customer,
        "outlet": Outlet,
    }

    def get_queryset(self):
        queryset = self._apply_scope(Order.objects.select_related("customer", "outlet").prefetch_related("items").all())
        customer = self.request.query_params.get("customer")
        status = self.request.query_params.get("status")
        if customer:
            queryset = queryset.filter(customer_id=customer)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        self._validate_related_scope(serializer.validated_data)
        draft_order = Order(status=serializer.validated_data.get("status"))
        blockers = validate_order_fne_delivery_gate(draft_order, target_status=draft_order.status)
        if blockers:
            raise ValidationError({"status": blockers})
        serializer.save()

    def perform_update(self, serializer):
        self._validate_related_scope(serializer.validated_data)
        instance = self.get_object()
        target_status = serializer.validated_data.get("status", instance.status)
        blockers = validate_order_fne_delivery_gate(instance, target_status=target_status)
        if blockers:
            raise ValidationError({"status": blockers})
        serializer.save()


class OrderItemViewSet(ScopedModelViewSet):
    serializer_class = OrderItemSerializer
    scoped_related_fields = {"order": Order}

    def get_queryset(self):
        queryset = self._apply_scope(OrderItem.objects.select_related("order", "product").all())
        order = self.request.query_params.get("order")
        if order:
            queryset = queryset.filter(order_id=order)
        return queryset


class InvoiceViewSet(ScopedModelViewSet):
    serializer_class = InvoiceSerializer
    scoped_related_fields = {
        "customer": Customer,
        "order": Order,
        "original_invoice": Invoice,
    }

    def get_queryset(self):
        queryset = self._apply_scope(
            Invoice.objects.select_related("customer", "order", "sales_owner", "created_by").prefetch_related("items").all()
        )
        customer = self.request.query_params.get("customer")
        nature = self.request.query_params.get("nature")
        status = self.request.query_params.get("status")
        fne_status = self.request.query_params.get("fne_status")
        sales_owner = self.request.query_params.get("sales_owner")
        original_invoice = self.request.query_params.get("original_invoice")
        if customer:
            queryset = queryset.filter(customer_id=customer)
        if nature:
            queryset = queryset.filter(nature=nature)
        if status:
            queryset = queryset.filter(status=status)
        if fne_status:
            queryset = queryset.filter(fne_status=fne_status)
        if sales_owner:
            queryset = queryset.filter(sales_owner_id=sales_owner)
        if original_invoice:
            queryset = queryset.filter(original_invoice_id=original_invoice)
        return queryset

    def perform_create(self, serializer):
        self._validate_related_scope(serializer.validated_data)
        serializer.save(created_by=self.request.user)


class InvoiceItemViewSet(ScopedModelViewSet):
    serializer_class = InvoiceItemSerializer
    scoped_related_fields = {
        "invoice": Invoice,
        "product": Product,
    }

    def get_queryset(self):
        queryset = self._apply_scope(InvoiceItem.objects.select_related("invoice", "product").all())
        invoice = self.request.query_params.get("invoice")
        if invoice:
            queryset = queryset.filter(invoice_id=invoice)
        return queryset


class InvoicePaymentViewSet(ScopedModelViewSet):
    serializer_class = InvoicePaymentSerializer
    scoped_related_fields = {"invoice": Invoice}

    def get_queryset(self):
        queryset = self._apply_scope(InvoicePayment.objects.select_related("invoice", "recorded_by").all())
        invoice = self.request.query_params.get("invoice")
        payment_method = self.request.query_params.get("payment_method")
        source = self.request.query_params.get("source")
        if invoice:
            queryset = queryset.filter(invoice_id=invoice)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        if source:
            queryset = queryset.filter(source=source)
        return queryset

    def perform_create(self, serializer):
        self._validate_related_scope(serializer.validated_data)
        invoice = serializer.validated_data.get("invoice")
        amount = int(serializer.validated_data.get("amount") or 0)
        issues = validate_invoice_payment_prerequisites(invoice, amount=amount)
        if issues:
            raise ValidationError({"amount": issues})
        serializer.save(recorded_by=self.request.user)


class SupportCaseViewSet(ScopedModelViewSet):
    serializer_class = SupportCaseSerializer
    scoped_related_fields = {
        "customer": Customer,
        "contact": Contact,
    }

    def get_queryset(self):
        queryset = self._apply_scope(SupportCase.objects.select_related("customer", "contact").all())
        customer = self.request.query_params.get("customer")
        status = self.request.query_params.get("status")
        if customer:
            queryset = queryset.filter(customer_id=customer)
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class VisitReportViewSet(ScopedModelViewSet):
    serializer_class = VisitReportSerializer
    scoped_related_fields = {
        "customer": Customer,
        "contact": Contact,
        "outlet": Outlet,
    }

    def get_queryset(self):
        queryset = self._apply_scope(VisitReport.objects.select_related("customer", "contact", "outlet").all())
        customer = self.request.query_params.get("customer")
        if customer:
            queryset = queryset.filter(customer_id=customer)
        return queryset


class TaskViewSet(ScopedModelViewSet):
    serializer_class = TaskSerializer
    scoped_related_fields = {
        "customer": Customer,
        "lead": Lead,
        "opportunity": Opportunity,
        "support_case": SupportCase,
        "order": Order,
    }

    def get_queryset(self):
        queryset = self._apply_scope(Task.objects.select_related(
            "customer",
            "lead",
            "opportunity",
            "support_case",
            "order",
            "assigned_to",
        ).all())
        customer = self.request.query_params.get("customer")
        lead = self.request.query_params.get("lead")
        opportunity = self.request.query_params.get("opportunity")
        support_case = self.request.query_params.get("support_case")
        order = self.request.query_params.get("order")
        assigned_to = self.request.query_params.get("assigned_to")
        status = self.request.query_params.get("status")
        if customer:
            queryset = queryset.filter(customer_id=customer)
        if lead:
            queryset = queryset.filter(lead_id=lead)
        if opportunity:
            queryset = queryset.filter(opportunity_id=opportunity)
        if support_case:
            queryset = queryset.filter(support_case_id=support_case)
        if order:
            queryset = queryset.filter(order_id=order)
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        if status:
            queryset = queryset.filter(status=status)
        return queryset
