from datetime import timedelta
import re

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

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
    NewsletterSubscription,
    Opportunity,
    Order,
    OrderItem,
    Product,
    ProductCategory,
    Promotion,
    RoleAssignment,
    RoutingRule,
    SlaEscalation,
    Territory,
    Outlet,
    SupportCase,
    Task,
    UserSecurityProfile,
    VisitReport,
)
from crm.services.automation import calculate_lead_score, calculate_priority

User = get_user_model()


def _normalize_text(value, max_length=255):
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:max_length]


def _normalize_email(value):
    return _normalize_text(value, max_length=254).lower()


def _normalize_phone(value):
    raw = _normalize_text(value, max_length=64)
    normalized = re.sub(r"[^\d+]", "", raw)
    return normalized[:40]


def _guard_recent_duplicate(
    *,
    kind: str,
    email: str = "",
    phone: str = "",
    name: str = "",
    ip_address=None,
    window_minutes: int = 2,
):
    since = timezone.now() - timedelta(minutes=window_minutes)
    queryset = InboundRequest.objects.filter(kind=kind, created_at__gte=since)
    if email:
        queryset = queryset.filter(email__iexact=email)
    elif phone:
        queryset = queryset.filter(phone__iexact=phone)
    elif ip_address:
        queryset = queryset.filter(ip_address=ip_address)
    if name:
        queryset = queryset.filter(name__iexact=name)
    if queryset.exists():
        raise serializers.ValidationError("Soumission trop frequente. Merci de patienter avant de recommencer.")


class UserSerializer(serializers.ModelSerializer):
    user_uuid = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "is_active", "is_staff", "user_uuid"]

    def get_user_uuid(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        if request is None or not request.user.is_authenticated:
            return None
        if not request.user.has_perm("crm.view_usersecurityprofile"):
            return None
        try:
            return str(obj.security_profile.public_uuid)
        except Exception:
            return None


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Territory
        fields = "__all__"


class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = "__all__"


class RoutingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutingRule
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"


class InboundRequestSerializer(serializers.ModelSerializer):
    sla_status = serializers.SerializerMethodField()

    class Meta:
        model = InboundRequest
        fields = "__all__"

    def get_sla_status(self, obj):
        from django.utils import timezone

        now = timezone.now()
        if obj.resolved_at:
            return "resolu"
        if obj.first_response_at is None:
            if obj.first_response_due_at and obj.first_response_due_at < now:
                return "en_retard"
            return "en_cours"
        if obj.resolution_due_at and obj.resolution_due_at < now:
            return "en_retard"
        return "ok"


class CareerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerApplication
        fields = "__all__"


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = "__all__"


class ApprovalPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalPolicy
        fields = "__all__"


class ApprovalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequest
        fields = "__all__"


class DataQualityIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataQualityIssue
        fields = "__all__"


class SlaEscalationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlaEscalation
        fields = "__all__"


class AuditTrailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditTrail
        fields = "__all__"


class UserSecurityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSecurityProfile
        fields = "__all__"


class RoleAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleAssignment
        fields = "__all__"


class PublicLeadCreateSerializer(serializers.Serializer):
    kind = serializers.CharField(required=False, default="lead")
    name = serializers.CharField()
    company = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    segment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    stage = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    intent = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    channel_preference = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    volume = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    product = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    objective = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    region = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    preferred_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    interests = serializers.ListField(child=serializers.CharField(), required=False)
    consent = serializers.BooleanField(required=False, default=False)
    source_page = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    referrer = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_source = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_medium = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_campaign = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_term = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ip_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    user_agent = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    honeypot = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    raw_data = serializers.JSONField(required=False)

    def _normalize_segment(self, value):
        if not value:
            return None
        value = value.strip().lower()
        if "vol" in value:
            return "volailles"
        if "porc" in value:
            return "porcins"
        if "poiss" in value or "tilapia" in value:
            return "poissons"
        if "bio" in value:
            return "biosecurite"
        return value

    def _normalize_channel(self, value):
        if not value:
            return ""
        value = value.lower()
        if "what" in value:
            return "whatsapp"
        if "mail" in value or "email" in value:
            return "email"
        if "tel" in value or "phone" in value:
            return "appel"
        return ""

    def _resolve_need_type(self, interests, intent):
        if interests:
            first = interests[0].lower()
            if "additif" in first:
                return "additifs"
            if "bio" in first:
                return "biosecurite"
            if "conseil" in first:
                return "formation"
            return "aliments"
        if intent:
            intent = intent.lower()
            if "support" in intent:
                return "formation"
            if "distributeur" in intent:
                return "logistique"
            return "aliments"
        return "aliments"

    def create(self, validated_data):
        if validated_data.get("honeypot"):
            raise serializers.ValidationError("Spam detected.")
        snapshot = dict(validated_data)
        snapshot.pop("honeypot", None)
        name = _normalize_text(validated_data.get("name"), max_length=255)
        company = _normalize_text(validated_data.get("company"), max_length=255)
        phone = _normalize_phone(validated_data.get("phone"))
        email = _normalize_email(validated_data.get("email"))
        stage = _normalize_text(validated_data.get("stage"), max_length=120)
        intent = _normalize_text(validated_data.get("intent"), max_length=120)
        volume = _normalize_text(validated_data.get("volume"), max_length=120)
        product = _normalize_text(validated_data.get("product"), max_length=255)
        objective = _normalize_text(validated_data.get("objective"), max_length=255)
        message = _normalize_text(validated_data.get("message"), max_length=2000)
        region = _normalize_text(validated_data.get("region"), max_length=120)
        preferred_time = _normalize_text(validated_data.get("preferred_time"), max_length=120)
        interests = [_normalize_text(item, max_length=120) for item in (validated_data.get("interests") or []) if item]
        interests = [item for item in interests if item]
        segment = self._normalize_segment(validated_data.get("segment"))
        channel_preference = self._normalize_channel(validated_data.get("channel_preference"))
        kind = (validated_data.get("kind") or "lead").lower()
        ip_address = validated_data.get("ip_address")

        _guard_recent_duplicate(
            kind=kind,
            email=email,
            phone=phone,
            name=name,
            ip_address=ip_address,
        )

        priority = calculate_priority(
            {
                "segment": segment,
                "intent": intent,
                "objective": objective,
                "channel_preference": channel_preference,
                "volume": volume,
                "phone": phone,
                "email": email,
            }
        )

        inbound = InboundRequest.objects.create(
            kind=kind,
            priority=priority,
            name=name,
            company=company,
            phone=phone,
            email=email,
            segment=segment or "",
            stage=stage,
            intent=intent,
            channel_preference=channel_preference,
            volume=volume,
            product=product,
            objective=objective,
            message=message,
            region=region,
            preferred_time=preferred_time,
            interests=interests,
            consent=validated_data.get("consent", False),
            source_page=validated_data.get("source_page") or "",
            referrer=validated_data.get("referrer") or "",
            utm_source=validated_data.get("utm_source") or "",
            utm_medium=validated_data.get("utm_medium") or "",
            utm_campaign=validated_data.get("utm_campaign") or "",
            utm_content=validated_data.get("utm_content") or "",
            utm_term=validated_data.get("utm_term") or "",
            ip_address=ip_address,
            user_agent=validated_data.get("user_agent") or "",
            raw_data=validated_data.get("raw_data") or snapshot,
        )

        lead_score = calculate_lead_score(
            {
                "company": company,
                "phone": phone,
                "email": email,
                "segment": segment,
                "expected_volume": volume,
                "product_interest": product,
                "objective": objective,
                "preferred_channel": channel_preference,
                "intent": intent,
            }
        )

        lead = Lead.objects.create(
            name=name,
            company=company,
            phone=phone,
            email=email,
            lead_score=lead_score,
            channel="site",
            preferred_channel=channel_preference,
            segment=segment or "volailles",
            stage=stage,
            need_type=self._resolve_need_type(interests, intent),
            expected_volume=volume,
            product_interest=product,
            objective=objective,
            interests=interests,
            region=region,
            notes="\\n".join(
                [
                    part
                    for part in [
                        message,
                        f"Intention: {intent}" if intent else "",
                        f"Canal prefere: {channel_preference}" if channel_preference else "",
                        f"Creneau: {preferred_time}" if preferred_time else "",
                    ]
                    if part
                ]
            ),
            source_page=validated_data.get("source_page") or "",
            referrer=validated_data.get("referrer") or "",
            utm_source=validated_data.get("utm_source") or "",
            utm_medium=validated_data.get("utm_medium") or "",
            utm_campaign=validated_data.get("utm_campaign") or "",
            utm_content=validated_data.get("utm_content") or "",
            utm_term=validated_data.get("utm_term") or "",
            ip_address=ip_address,
            user_agent=validated_data.get("user_agent") or "",
        )
        inbound.lead = lead
        inbound.save(update_fields=["lead"])
        return inbound


class PublicCareerApplicationSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    role = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    experience = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    availability = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mobility = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    specialites = serializers.ListField(child=serializers.CharField(), required=False)
    consent = serializers.BooleanField(required=False, default=False)
    cv = serializers.FileField(required=False, allow_null=True)
    source_page = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    referrer = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_source = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_medium = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_campaign = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_term = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ip_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    user_agent = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    honeypot = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)

    def to_internal_value(self, data):
        if hasattr(data, "getlist") and not data.get("specialites"):
            specialites = data.getlist("specialites")
            data = data.copy()
            if specialites:
                data.setlist("specialites", specialites)
        return super().to_internal_value(data)

    def create(self, validated_data):
        if validated_data.get("honeypot"):
            raise serializers.ValidationError("Spam detected.")
        snapshot = dict(validated_data)
        snapshot.pop("honeypot", None)
        full_name = _normalize_text(validated_data.get("full_name"), max_length=255)
        email = _normalize_email(validated_data.get("email"))
        phone = _normalize_phone(validated_data.get("phone"))
        message = _normalize_text(validated_data.get("message"), max_length=2000)
        ip_address = validated_data.get("ip_address")

        _guard_recent_duplicate(
            kind="career",
            email=email,
            phone=phone,
            name=full_name,
            ip_address=ip_address,
        )

        inbound = InboundRequest.objects.create(
            kind="career",
            name=full_name,
            email=email,
            phone=phone,
            message=message,
            consent=validated_data.get("consent", False),
            source_page=validated_data.get("source_page") or "",
            referrer=validated_data.get("referrer") or "",
            utm_source=validated_data.get("utm_source") or "",
            utm_medium=validated_data.get("utm_medium") or "",
            utm_campaign=validated_data.get("utm_campaign") or "",
            utm_content=validated_data.get("utm_content") or "",
            utm_term=validated_data.get("utm_term") or "",
            ip_address=ip_address,
            user_agent=validated_data.get("user_agent") or "",
            raw_data=validated_data.get("raw_data") or {k: v for k, v in snapshot.items() if k not in {"cv"}},
        )
        application = CareerApplication.objects.create(
            inbound_request=inbound,
            full_name=full_name,
            email=email,
            phone=phone,
            role=_normalize_text(validated_data.get("role"), max_length=120),
            experience=_normalize_text(validated_data.get("experience"), max_length=120),
            location=_normalize_text(validated_data.get("location"), max_length=120),
            availability=_normalize_text(validated_data.get("availability"), max_length=120),
            mobility=_normalize_text(validated_data.get("mobility"), max_length=120),
            message=message,
            specialites=[_normalize_text(item, max_length=120) for item in (validated_data.get("specialites") or []) if item],
            consent=validated_data.get("consent", False),
            cv=validated_data.get("cv"),
            source_page=validated_data.get("source_page") or "",
            referrer=validated_data.get("referrer") or "",
            utm_source=validated_data.get("utm_source") or "",
            utm_medium=validated_data.get("utm_medium") or "",
            utm_campaign=validated_data.get("utm_campaign") or "",
            utm_content=validated_data.get("utm_content") or "",
            utm_term=validated_data.get("utm_term") or "",
            ip_address=ip_address,
            user_agent=validated_data.get("user_agent") or "",
        )
        inbound.save(update_fields=["updated_at"])
        return application


class PublicNewsletterSubscriptionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    source_page = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    referrer = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_source = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_medium = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_campaign = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utm_term = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ip_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    user_agent = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    honeypot = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)

    def create(self, validated_data):
        if validated_data.get("honeypot"):
            raise serializers.ValidationError("Spam detected.")
        snapshot = dict(validated_data)
        snapshot.pop("honeypot", None)
        email = _normalize_email(validated_data.get("email"))
        ip_address = validated_data.get("ip_address")

        _guard_recent_duplicate(
            kind="newsletter",
            email=email,
            ip_address=ip_address,
            window_minutes=1,
        )

        inbound = InboundRequest.objects.create(
            kind="newsletter",
            email=email,
            source_page=validated_data.get("source_page") or "",
            referrer=validated_data.get("referrer") or "",
            utm_source=validated_data.get("utm_source") or "",
            utm_medium=validated_data.get("utm_medium") or "",
            utm_campaign=validated_data.get("utm_campaign") or "",
            utm_content=validated_data.get("utm_content") or "",
            utm_term=validated_data.get("utm_term") or "",
            ip_address=ip_address,
            user_agent=validated_data.get("user_agent") or "",
            raw_data=validated_data.get("raw_data") or snapshot,
        )
        subscription, _ = NewsletterSubscription.objects.update_or_create(
            email=email,
            defaults={
                "status": "actif",
                "inbound_request": inbound,
                "source_page": validated_data.get("source_page") or "",
                "referrer": validated_data.get("referrer") or "",
                "utm_source": validated_data.get("utm_source") or "",
                "utm_medium": validated_data.get("utm_medium") or "",
                "utm_campaign": validated_data.get("utm_campaign") or "",
                "utm_content": validated_data.get("utm_content") or "",
                "utm_term": validated_data.get("utm_term") or "",
                "ip_address": ip_address,
                "user_agent": validated_data.get("user_agent") or "",
            },
        )
        inbound.save(update_fields=["updated_at"])
        return subscription


class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"


class PromotionSerializer(serializers.ModelSerializer):
    outlet_count = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = "__all__"

    def get_outlet_count(self, obj):
        return obj.outlets.count()


class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = "__all__"


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.FloatField(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class InvoiceItemSerializer(serializers.ModelSerializer):
    line_subtotal = serializers.IntegerField(source="subtotal_amount", read_only=True)
    line_discount = serializers.IntegerField(source="discount_amount", read_only=True)
    line_tax = serializers.IntegerField(source="tax_amount", read_only=True)
    line_total = serializers.IntegerField(source="total_amount", read_only=True)

    class Meta:
        model = InvoiceItem
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    balance_due = serializers.IntegerField(read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"


class SupportCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportCase
        fields = "__all__"


class VisitReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitReport
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class InvoicePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoicePayment
        fields = "__all__"
