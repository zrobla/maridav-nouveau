"""Admin configuration for CRM models."""

from django.contrib import admin

from . import models


@admin.register(models.Territory)
class TerritoryAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "manager")
    search_fields = ("name", "region")


@admin.register(models.Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = ("name", "channel", "city", "region", "status")
    list_filter = ("channel", "status", "region")
    search_fields = ("name", "city", "region")


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "customer_type", "segment", "region", "status")
    search_fields = ("name", "code", "city", "region")
    list_filter = ("customer_type", "segment", "region", "status")


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "customer", "role", "preferred_channel")
    search_fields = ("first_name", "last_name", "customer__name")


@admin.register(models.Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "segment", "lead_score", "status", "channel", "assigned_to")
    search_fields = ("name", "company")
    list_filter = ("segment", "status", "channel")


@admin.register(models.InboundRequest)
class InboundRequestAdmin(admin.ModelAdmin):
    list_display = ("kind", "name", "email", "phone", "priority", "status", "assigned_to", "created_at")
    search_fields = ("name", "email", "phone", "company")
    list_filter = ("kind", "status", "segment", "priority")


@admin.register(models.RoutingRule)
class RoutingRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "segment", "region", "channel_preference", "priority", "assigned_to", "active")
    list_filter = ("kind", "segment", "channel_preference", "active")
    search_fields = ("name", "region")


@admin.register(models.CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "status", "created_at")
    search_fields = ("full_name", "email", "phone", "role")
    list_filter = ("status",)


@admin.register(models.NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "status", "created_at")
    search_fields = ("email",)
    list_filter = ("status",)


@admin.register(models.ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "segment", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProductPriceInline(admin.TabularInline):
    model = models.ProductPrice
    extra = 1


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "unit_price", "cost_price", "margin_amount", "status")
    search_fields = ("name", "sku")
    list_filter = ("category", "status")
    inlines = [ProductPriceInline]


@admin.register(models.ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ("product", "customer_type", "unit_price", "margin_amount")
    list_filter = ("customer_type",)
    search_fields = ("product__name", "product__sku")


@admin.register(models.Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "customer", "stage", "expected_value", "probability")
    list_filter = ("stage", "segment")


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 1


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer", "outlet", "status", "delivery_date", "total_amount")
    list_filter = ("status",)
    inlines = [OrderItemInline]


class InvoiceItemInline(admin.TabularInline):
    model = models.InvoiceItem
    extra = 1


class InvoicePaymentInline(admin.TabularInline):
    model = models.InvoicePayment
    extra = 0
    fields = ("amount", "payment_method", "payment_reference", "paid_at", "source", "recorded_by")
    readonly_fields = ("source", "recorded_by")


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "nature",
        "customer",
        "source",
        "status",
        "fne_status",
        "total_amount",
        "paid_amount",
        "sales_owner",
    )
    list_filter = ("nature", "source", "status", "fne_status", "payment_method")
    search_fields = ("invoice_number", "customer__name", "payment_reference", "fne_reference")
    inlines = [InvoiceItemInline, InvoicePaymentInline]


@admin.register(models.InvoicePayment)
class InvoicePaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "payment_method", "payment_reference", "paid_at", "source", "recorded_by")
    list_filter = ("payment_method", "source", "paid_at")
    search_fields = ("invoice__invoice_number", "payment_reference", "source_event_id", "source_connector")


@admin.register(models.SupportCase)
class SupportCaseAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer", "case_type", "status", "priority")
    list_filter = ("case_type", "status", "priority")


@admin.register(models.VisitReport)
class VisitReportAdmin(admin.ModelAdmin):
    list_display = ("customer", "outlet", "visit_date", "purpose", "species", "biosecurity_score")
    list_filter = ("purpose", "species")


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "activity_type", "due_date", "assigned_to")
    list_filter = ("status", "activity_type")


@admin.register(models.Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("name",)


@admin.register(models.Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ("customer", "product", "period", "expected_quantity", "status")
    list_filter = ("status",)


@admin.register(models.ApprovalPolicy)
class ApprovalPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "min_order_total", "min_discount_pct", "require_credit_exception", "approver_group")
    list_filter = ("active", "require_credit_exception")


@admin.register(models.ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "entity_type",
        "request_type",
        "status",
        "object_id",
        "amount_fcfa",
        "discount_pct",
        "requested_by",
        "assigned_to",
        "requested_at",
    )
    list_filter = ("entity_type", "request_type", "status")
    search_fields = ("reason", "decision_note")


@admin.register(models.DataQualityIssue)
class DataQualityIssueAdmin(admin.ModelAdmin):
    list_display = ("source", "issue_type", "severity", "status", "object_id", "created_at", "assigned_to")
    list_filter = ("source", "issue_type", "severity", "status")
    search_fields = ("message", "fingerprint")


@admin.register(models.SlaEscalation)
class SlaEscalationAdmin(admin.ModelAdmin):
    list_display = ("source_type", "escalation_level", "status", "object_id", "due_at", "assigned_to")
    list_filter = ("source_type", "escalation_level", "status")
    search_fields = ("reason",)


@admin.register(models.AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ("created_at", "event", "source", "content_type", "object_id", "actor_display")
    list_filter = ("event", "source", "content_type")
    search_fields = ("message", "actor_display", "object_repr")


@admin.register(models.UserSecurityProfile)
class UserSecurityProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "public_uuid", "mfa_required", "is_locked", "last_password_rotation_at")
    search_fields = ("user__username", "user__email", "public_uuid")
    list_filter = ("mfa_required", "is_locked")


@admin.register(models.RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "assignment_type", "scope", "is_active", "valid_from", "valid_to")
    list_filter = ("assignment_type", "scope", "is_active", "group")
    search_fields = ("user__username", "scope_reference", "reason")


@admin.register(models.EnterpriseConnector)
class EnterpriseConnectorAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "integration_type", "direction", "transport", "active")
    list_filter = ("integration_type", "direction", "transport", "active")
    search_fields = ("code", "name")


@admin.register(models.EnterpriseFieldMapping)
class EnterpriseFieldMappingAdmin(admin.ModelAdmin):
    list_display = ("connector", "entity_type", "source_field", "target_field", "version", "active")
    list_filter = ("entity_type", "version", "active", "connector")
    search_fields = ("connector__code", "source_field", "target_field")


@admin.register(models.EnterpriseOutboxEvent)
class EnterpriseOutboxEventAdmin(admin.ModelAdmin):
    list_display = ("connector", "event_type", "entity_type", "status", "attempt_count", "created_at", "delivered_at")
    list_filter = ("status", "connector", "entity_type")
    search_fields = ("event_type", "idempotency_key", "external_reference")
    readonly_fields = ("created_at", "updated_at", "delivered_at")


@admin.register(models.EnterpriseInboxEvent)
class EnterpriseInboxEventAdmin(admin.ModelAdmin):
    list_display = ("connector", "external_event_id", "event_type", "status", "attempt_count", "created_at", "processed_at")
    list_filter = ("status", "connector", "event_type")
    search_fields = ("external_event_id", "event_type", "dedup_key")
    readonly_fields = ("created_at", "updated_at", "processed_at")


@admin.register(models.EnterpriseDeadLetterEvent)
class EnterpriseDeadLetterEventAdmin(admin.ModelAdmin):
    list_display = ("connector", "direction", "event_type", "attempt_count", "created_at")
    list_filter = ("direction", "connector", "event_type")
    search_fields = ("event_type", "reason")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.SalesTarget)
class SalesTargetAdmin(admin.ModelAdmin):
    list_display = ("owner", "period_month", "period_year", "segment", "target_amount", "commission_rate_pct", "status")
    list_filter = ("period_year", "period_month", "status", "segment")
    search_fields = ("owner__username", "owner__first_name", "owner__last_name")


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "warehouse_type", "city", "region", "is_active")
    list_filter = ("warehouse_type", "region", "is_active")
    search_fields = ("name", "code", "city")


class StockMovementInline(admin.TabularInline):
    model = models.StockMovement
    extra = 0
    fields = ("movement_type", "quantity", "balance_after", "reason", "occurred_at", "recorded_by")
    readonly_fields = ("balance_after",)


@admin.register(models.StockLot)
class StockLotAdmin(admin.ModelAdmin):
    list_display = ("lot_code", "product", "warehouse", "quantity_on_hand", "unit", "expiry_date", "status")
    list_filter = ("status", "warehouse", "unit")
    search_fields = ("lot_code", "product__name", "product__sku", "supplier_reference")
    inlines = [StockMovementInline]


@admin.register(models.StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("occurred_at", "movement_type", "lot", "quantity", "balance_after", "recorded_by")
    list_filter = ("movement_type", "occurred_at")
    search_fields = ("lot__lot_code", "lot__product__name", "reason")
    readonly_fields = ("balance_after",)
