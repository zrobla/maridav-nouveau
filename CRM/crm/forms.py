"""Forms for the CRM app."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import inlineformset_factory

from .models import (
    ApprovalPolicy,
    ApprovalRequest,
    AuditTrail,
    CareerApplication,
    Customer,
    Contact,
    DataQualityIssue,
    Forecast,
    InboundRequest,
    Lead,
    NewsletterSubscription,
    Outlet,
    Opportunity,
    Order,
    OrderItem,
    Invoice,
    InvoiceItem,
    InvoicePayment,
    Product,
    ProductCategory,
    ProductPrice,
    Promotion,
    RoleAssignment,
    RoleAssignmentTypeChoices,
    RoleScopeChoices,
    RoutingRule,
    SalesTarget,
    SlaEscalation,
    StockLot,
    StockMovement,
    SupportCase,
    Task,
    Territory,
    UserSecurityProfile,
    VisitReport,
    Warehouse,
)

User = get_user_model()


class DateInput(forms.DateInput):
    """Date picker en format français jj/mm/aaaa."""

    input_type = "text"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", "%d/%m/%Y")
        attrs = kwargs.setdefault("attrs", {})
        attrs.setdefault("placeholder", "jj/mm/aaaa")
        attrs.setdefault("pattern", "\\d{2}/\\d{2}/\\d{4}")
        super().__init__(*args, **kwargs)


class DateTimeInput(forms.DateTimeInput):
    """Date time picker en format français jj/mm/aaaa hh:mm."""

    input_type = "text"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", "%d/%m/%Y %H:%M")
        attrs = kwargs.setdefault("attrs", {})
        attrs.setdefault("placeholder", "jj/mm/aaaa hh:mm")
        super().__init__(*args, **kwargs)


class StyledModelForm(forms.ModelForm):
    """Add Bootstrap classes automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")
            if isinstance(field, forms.DateField):
                field.input_formats = ["%d/%m/%Y", "%Y-%m-%d"]
                if not isinstance(field.widget, DateInput):
                    field.widget = DateInput()
                field.widget.attrs.setdefault("placeholder", "jj/mm/aaaa")
            if isinstance(field, forms.DateTimeField):
                field.input_formats = ["%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]
                if not isinstance(field.widget, DateTimeInput):
                    field.widget = DateTimeInput()
                field.widget.attrs.setdefault("placeholder", "jj/mm/aaaa hh:mm")


class CustomerForm(StyledModelForm):
    class Meta:
        model = Customer
        fields = [
            "name",
            "code",
            "customer_type",
            "segment",
            "size",
            "city",
            "region",
            "address",
            "country",
            "phone",
            "whatsapp",
            "email",
            "tax_ncc",
            "tax_ntd",
            "tax_rccm",
            "tax_regime",
            "status",
            "credit_limit",
            "payment_terms_days",
            "credit_hold",
            "notes",
        ]


class ContactForm(StyledModelForm):
    class Meta:
        model = Contact
        fields = [
            "customer",
            "first_name",
            "last_name",
            "role",
            "phone",
            "whatsapp",
            "email",
            "preferred_channel",
            "is_primary",
        ]


class LeadForm(StyledModelForm):
    class Meta:
        model = Lead
        fields = [
            "name",
            "company",
            "phone",
            "email",
            "lead_score",
            "channel",
            "preferred_channel",
            "segment",
            "stage",
            "need_type",
            "expected_volume",
            "product_interest",
            "objective",
            "region",
            "status",
            "assigned_to",
            "next_step_date",
            "notes",
        ]
        widgets = {"next_step_date": DateInput()}


class ProductCategoryForm(StyledModelForm):
    class Meta:
        model = ProductCategory
        fields = ["name", "slug", "segment", "description"]


class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "sku",
            "packaging",
            "unit_price",
            "cost_price",
            "min_stock_alert",
            "status",
            "usage_notes",
        ]


class ProductPriceForm(StyledModelForm):
    class Meta:
        model = ProductPrice
        fields = ["customer_type", "unit_price"]


ProductPriceFormSet = inlineformset_factory(
    Product,
    ProductPrice,
    form=ProductPriceForm,
    extra=1,
    can_delete=True,
)


class SalesTargetForm(StyledModelForm):
    class Meta:
        model = SalesTarget
        fields = [
            "owner",
            "territory",
            "segment",
            "period_year",
            "period_month",
            "target_amount",
            "target_quantity",
            "commission_rate_pct",
            "status",
            "notes",
        ]


class OpportunityForm(StyledModelForm):
    class Meta:
        model = Opportunity
        fields = [
            "title",
            "customer",
            "lead",
            "stage",
            "expected_value",
            "probability",
            "expected_close_date",
            "segment",
            "assigned_to",
            "notes",
        ]
        widgets = {"expected_close_date": DateInput()}


class OrderForm(StyledModelForm):
    class Meta:
        model = Order
        fields = [
            "order_number",
            "customer",
            "outlet",
            "status",
            "delivery_date",
            "billing_contact",
            "discount_pct",
            "credit_exception_requested",
            "notes",
        ]
        widgets = {"delivery_date": DateInput()}


class OrderItemForm(StyledModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "unit_price"]


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    fields=["product", "quantity", "unit_price"],
    extra=1,
    can_delete=True,
)


class InvoiceForm(StyledModelForm):
    class Meta:
        model = Invoice
        fields = [
            "invoice_number",
            "source",
            "nature",
            "customer",
            "order",
            "original_invoice",
            "status",
            "due_date",
            "currency",
            "sales_owner",
            "fne_required",
            "cancellation_reason",
            "notes",
        ]
        widgets = {"due_date": DateInput()}


class InvoiceItemForm(StyledModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["product", "description", "quantity", "unit_price", "discount_pct", "tax_rate_pct"]


InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    fields=["product", "description", "quantity", "unit_price", "discount_pct", "tax_rate_pct"],
    extra=1,
    can_delete=True,
)


class InvoicePaymentForm(StyledModelForm):
    class Meta:
        model = InvoicePayment
        fields = [
            "amount",
            "payment_method",
            "payment_reference",
            "paid_at",
            "notes",
        ]
        widgets = {"paid_at": DateTimeInput()}


class SupportCaseForm(StyledModelForm):
    class Meta:
        model = SupportCase
        fields = [
            "reference",
            "customer",
            "contact",
            "case_type",
            "status",
            "priority",
            "species",
            "channel",
            "description",
            "due_date",
            "assigned_to",
            "resolution",
        ]
        widgets = {"due_date": DateInput()}


class VisitReportForm(StyledModelForm):
    class Meta:
        model = VisitReport
        fields = [
            "customer",
            "outlet",
            "contact",
            "visit_date",
            "species",
            "purpose",
            "observations",
            "actions",
            "follow_up_date",
            "biosecurity_score",
        ]
        widgets = {"visit_date": DateInput(), "follow_up_date": DateInput()}


class TaskForm(StyledModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "due_date",
            "status",
            "activity_type",
            "customer",
            "lead",
            "opportunity",
            "support_case",
            "order",
            "assigned_to",
        ]
        widgets = {"due_date": DateInput()}


class InboundRequestForm(StyledModelForm):
    class Meta:
        model = InboundRequest
        fields = [
            "kind",
            "status",
            "priority",
            "name",
            "company",
            "phone",
            "email",
            "segment",
            "stage",
            "intent",
            "channel_preference",
            "volume",
            "product",
            "objective",
            "message",
            "region",
            "preferred_time",
            "consent",
            "lead",
            "assigned_to",
        ]


class CareerApplicationForm(StyledModelForm):
    class Meta:
        model = CareerApplication
        fields = [
            "inbound_request",
            "full_name",
            "email",
            "phone",
            "role",
            "experience",
            "location",
            "availability",
            "mobility",
            "message",
            "consent",
            "status",
            "cv",
        ]


class NewsletterSubscriptionForm(StyledModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ["inbound_request", "email", "status"]


class TerritoryForm(StyledModelForm):
    class Meta:
        model = Territory
        fields = ["name", "region", "manager", "notes"]


class OutletForm(StyledModelForm):
    class Meta:
        model = Outlet
        fields = [
            "name",
            "territory",
            "distributor",
            "channel",
            "city",
            "region",
            "address",
            "gps_lat",
            "gps_lng",
            "status",
            "notes",
        ]


class PromotionForm(StyledModelForm):
    class Meta:
        model = Promotion
        fields = [
            "name",
            "product",
            "start_date",
            "end_date",
            "budget",
            "status",
            "outlets",
            "notes",
        ]
        widgets = {
            "start_date": DateInput(),
            "end_date": DateInput(),
            "outlets": forms.SelectMultiple(attrs={"class": "form-select", "size": 8}),
        }


class ForecastForm(StyledModelForm):
    class Meta:
        model = Forecast
        fields = [
            "customer",
            "outlet",
            "product",
            "period",
            "expected_quantity",
            "status",
            "notes",
        ]


class UserRoleForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 10}),
        label="Rôles permanents",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff", "groups"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["username", "first_name", "last_name", "email"]:
            self.fields[field_name].required = False


class UserSecurityProfileForm(StyledModelForm):
    class Meta:
        model = UserSecurityProfile
        fields = [
            "mfa_required",
            "force_password_reset",
            "is_locked",
            "failed_login_count",
            "last_password_rotation_at",
            "last_login_ip",
            "notes",
        ]
        widgets = {
            "last_password_rotation_at": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "last_login_ip": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
        }


class RoleAssignmentForm(StyledModelForm):
    class Meta:
        model = RoleAssignment
        fields = [
            "user",
            "group",
            "assignment_type",
            "scope",
            "scope_reference",
            "content_type",
            "object_id",
            "valid_from",
            "valid_to",
            "is_active",
            "reason",
        ]
        widgets = {
            "valid_from": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "valid_to": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def clean(self):
        cleaned = super().clean()
        assignment_type = cleaned.get("assignment_type")
        scope = cleaned.get("scope")
        content_type = cleaned.get("content_type")
        object_id = cleaned.get("object_id")
        valid_from = cleaned.get("valid_from")
        valid_to = cleaned.get("valid_to")

        if assignment_type in {RoleAssignmentTypeChoices.TEMPORARY, RoleAssignmentTypeChoices.SCOPED} and not valid_to:
            self.add_error("valid_to", "La date de fin est obligatoire pour un rôle temporaire/scopé.")
        if valid_from and valid_to and valid_from > valid_to:
            self.add_error("valid_to", "La date de fin doit être postérieure à la date de début.")

        if scope != RoleScopeChoices.GLOBAL and not (content_type and object_id):
            if not cleaned.get("scope_reference"):
                self.add_error("scope_reference", "Indique une référence de dossier/projet ou renseigne une entité liée.")

        if scope == RoleScopeChoices.GLOBAL:
            cleaned["content_type"] = None
            cleaned["object_id"] = None
            if not cleaned.get("scope_reference"):
                cleaned["scope_reference"] = "Global"
        return cleaned


class RoutingRuleForm(StyledModelForm):
    class Meta:
        model = RoutingRule
        fields = [
            "name",
            "kind",
            "segment",
            "region",
            "channel_preference",
            "priority",
            "assigned_to",
            "active",
            "notes",
        ]


# --- Phase 1 : Stock, lots & péremption ---------------------------------------


class WarehouseForm(StyledModelForm):
    class Meta:
        model = Warehouse
        fields = [
            "name",
            "code",
            "warehouse_type",
            "territory",
            "city",
            "region",
            "address",
            "manager",
            "is_active",
            "notes",
        ]


class StockLotForm(StyledModelForm):
    """Création/édition d'un lot. La quantité 'reçue' alimente le solde initial ;
    par la suite, le solde n'évolue que via les mouvements de stock."""

    class Meta:
        model = StockLot
        fields = [
            "product",
            "warehouse",
            "lot_code",
            "unit",
            "quantity_initial",
            "unit_cost",
            "production_date",
            "expiry_date",
            "status",
            "supplier_reference",
            "notes",
        ]
        widgets = {
            "production_date": DateInput(),
            "expiry_date": DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["quantity_initial"].label = "Quantité reçue"
        if self.instance and self.instance.pk:
            # En édition, la quantité initiale est figée (le solde suit les mouvements).
            self.fields["quantity_initial"].disabled = True
            self.fields["quantity_initial"].help_text = (
                "Quantité d'origine du lot. Le stock courant évolue via les mouvements."
            )


class StockMovementForm(StyledModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "lot",
            "movement_type",
            "quantity",
            "reason",
            "order",
            "invoice",
            "counterpart_warehouse",
            "occurred_at",
            "notes",
        ]
        widgets = {"occurred_at": DateTimeInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lot"].queryset = StockLot.objects.select_related(
            "product", "warehouse"
        ).order_by("product__name", "lot_code")
        self.fields["order"].required = False
        self.fields["invoice"].required = False
        self.fields["counterpart_warehouse"].required = False
        self.fields["quantity"].help_text = (
            "Pour un ajustement, saisir la quantité réellement comptée (le solde sera fixé à cette valeur)."
        )
