import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from crm.models import (
    ApprovalRequest,
    AuditEventChoices,
    CareerApplication,
    Contact,
    Customer,
    DataQualityIssue,
    Forecast,
    InboundRequest,
    Lead,
    NewsletterSubscription,
    Opportunity,
    Order,
    OrderItem,
    Invoice,
    InvoiceItem,
    InvoicePayment,
    InvoiceStatusChoices,
    Outlet,
    Product,
    ProductCategory,
    Promotion,
    RoleAssignment,
    RoutingRule,
    SlaEscalation,
    SupportCase,
    Task,
    Territory,
    UserSecurityProfile,
    VisitReport,
)
from crm.services.automation import ensure_inbound_defaults, ensure_lead_score, should_mark_first_response, should_mark_resolved
from crm.services.governance import (
    apply_order_approval_policy,
    create_audit_trail,
    diff_changed_fields,
    model_snapshot,
    refresh_sla_escalations,
    run_inbound_data_quality_checks,
    run_invoice_data_quality_checks,
)
from crm.services.integrations import (
    emit_inbound_outbox_event,
    emit_invoice_outbox_event,
    emit_invoice_payment_outbox_event,
    emit_order_outbox_event,
)
from crm.services.sales import (
    mark_invoice_ready_for_fne,
    recalculate_invoice_payment_snapshot,
    recalculate_invoice_totals,
    reconcile_invoice_status_from_payments,
    resolve_default_sales_owner,
    validate_invoice_issue_prerequisites,
)

User = get_user_model()
signals_logger = logging.getLogger("crm.integrations")


AUDIT_TRACKED_MODELS = (
    Customer,
    Contact,
    Lead,
    InboundRequest,
    Opportunity,
    Order,
    OrderItem,
    Invoice,
    InvoiceItem,
    InvoicePayment,
    SupportCase,
    VisitReport,
    Task,
    Product,
    ProductCategory,
    Territory,
    Outlet,
    Promotion,
    Forecast,
    RoutingRule,
    CareerApplication,
    NewsletterSubscription,
    ApprovalRequest,
    DataQualityIssue,
    SlaEscalation,
    RoleAssignment,
)


@receiver(pre_save)
def track_pre_save_state(sender, instance, **kwargs):
    if sender not in AUDIT_TRACKED_MODELS:
        return
    if not instance.pk:
        instance._audit_before_state = {}
        return
    previous = sender.objects.filter(pk=instance.pk).first()
    instance._audit_before_state = model_snapshot(previous) if previous else {}


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if sender not in AUDIT_TRACKED_MODELS:
        return
    before_state = getattr(instance, "_audit_before_state", {}) or {}
    after_state = model_snapshot(instance)
    changed_fields = diff_changed_fields(before_state, after_state)
    if not created and not changed_fields:
        return

    event = AuditEventChoices.CREATE if created else AuditEventChoices.UPDATE
    if not created and "status" in changed_fields:
        event = AuditEventChoices.STATUS_CHANGE
    create_audit_trail(
        instance=instance,
        event=event,
        before_state=before_state,
        after_state=after_state,
        changed_fields=changed_fields,
    )


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if sender not in AUDIT_TRACKED_MODELS:
        return
    before_state = getattr(instance, "_audit_before_state", None) or model_snapshot(instance)
    create_audit_trail(
        instance=instance,
        event=AuditEventChoices.DELETE,
        before_state=before_state,
        after_state={},
        changed_fields=list(before_state.keys()),
    )


@receiver(post_save, sender=User)
def ensure_user_security_profile(sender, instance, created, **kwargs):
    UserSecurityProfile.objects.get_or_create(user=instance)


@receiver(user_logged_in)
def update_security_profile_on_login(sender, request, user, **kwargs):
    profile, _ = UserSecurityProfile.objects.get_or_create(user=user)
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    login_ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
    profile.last_login_ip = login_ip or profile.last_login_ip
    profile.failed_login_count = 0
    profile.save(update_fields=["last_login_ip", "failed_login_count", "updated_at"])


@receiver(user_login_failed)
def register_failed_login(sender, credentials, request, **kwargs):
    username = (credentials or {}).get("username")
    if not username:
        return
    user = User.objects.filter(username=username).first()
    if not user:
        return
    profile, _ = UserSecurityProfile.objects.get_or_create(user=user)
    profile.failed_login_count += 1
    if profile.failed_login_count >= settings.MAX_LOGIN_FAILURES:
        profile.is_locked = True
    profile.save(update_fields=["failed_login_count", "is_locked", "updated_at"])


@receiver(post_save, sender=InboundRequest)
def inbound_post_save(sender, instance, created, **kwargs):
    updates = {}
    ensure_inbound_defaults(instance)

    if instance.lead:
        ensure_lead_score(instance.lead)

    if should_mark_first_response(instance):
        updates["first_response_at"] = timezone.now()

    if should_mark_resolved(instance):
        updates["resolved_at"] = timezone.now()

    if updates:
        InboundRequest.objects.filter(pk=instance.pk).update(**updates)

    if created and instance.lead_id:
        task_exists = Task.objects.filter(lead_id=instance.lead_id, title__icontains="Qualifier").exists()
        if not task_exists:
            due_date = (instance.first_response_due_at or timezone.now()).date()
            Task.objects.create(
                title=f"Qualifier la demande: {instance.name or instance.company or 'Lead web'}",
                description="Prioriser la qualification et proposer une offre.",
                due_date=due_date,
                lead_id=instance.lead_id,
                assigned_to_id=instance.assigned_to_id,
            )

    run_inbound_data_quality_checks(instance)
    try:
        emit_inbound_outbox_event(instance, created=created)
    except Exception as exc:  # pragma: no cover - resilience guard
        signals_logger.warning("inbound_outbox_emit_failed inbound=%s reason=%s", instance.pk, exc)


@receiver(post_save, sender=SupportCase)
def support_post_save(sender, instance, created, **kwargs):
    refresh_sla_escalations()


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    apply_order_approval_policy(instance)
    try:
        emit_order_outbox_event(instance, created=created)
    except Exception as exc:  # pragma: no cover - resilience guard
        signals_logger.warning("order_outbox_emit_failed order=%s reason=%s", instance.pk, exc)


@receiver(post_save, sender=OrderItem)
def order_item_post_save(sender, instance, created, **kwargs):
    order = Order.objects.filter(pk=instance.order_id).first()
    if order:
        apply_order_approval_policy(order)


@receiver(post_delete, sender=OrderItem)
def order_item_post_delete(sender, instance, **kwargs):
    order = Order.objects.filter(pk=instance.order_id).first()
    if order:
        apply_order_approval_policy(order)


@receiver(post_save, sender=Invoice)
def invoice_post_save(sender, instance, created, **kwargs):
    owner = resolve_default_sales_owner(instance, fallback_user=instance.created_by)
    if owner and instance.sales_owner_id != owner.id:
        Invoice.objects.filter(pk=instance.pk).update(sales_owner=owner)
        instance.sales_owner = owner

    if instance.status in {
        InvoiceStatusChoices.EMISE,
        InvoiceStatusChoices.PARTIELLEMENT_PAYEE,
        InvoiceStatusChoices.PAYEE,
    } and instance.issued_at is None:
        issued_at = timezone.now()
        Invoice.objects.filter(pk=instance.pk).update(issued_at=issued_at)
        instance.issued_at = issued_at

    recalculate_invoice_payment_snapshot(instance, force=False)
    reconcile_invoice_status_from_payments(instance)
    prerequisites = validate_invoice_issue_prerequisites(instance)
    if prerequisites and instance.status in {
        InvoiceStatusChoices.EMISE,
        InvoiceStatusChoices.PARTIELLEMENT_PAYEE,
        InvoiceStatusChoices.PAYEE,
    }:
        Invoice.objects.filter(pk=instance.pk).update(status=InvoiceStatusChoices.BROUILLON)
        instance.status = InvoiceStatusChoices.BROUILLON

    if instance.status in {
        InvoiceStatusChoices.EMISE,
        InvoiceStatusChoices.PARTIELLEMENT_PAYEE,
        InvoiceStatusChoices.PAYEE,
    }:
        mark_invoice_ready_for_fne(instance)
    run_invoice_data_quality_checks(instance)
    try:
        emit_invoice_outbox_event(instance, created=created)
    except Exception as exc:  # pragma: no cover - resilience guard
        signals_logger.warning("invoice_outbox_emit_failed invoice=%s reason=%s", instance.pk, exc)


@receiver(post_save, sender=InvoiceItem)
def invoice_item_post_save(sender, instance, created, **kwargs):
    invoice = Invoice.objects.filter(pk=instance.invoice_id).first()
    if not invoice:
        return
    recalculate_invoice_totals(invoice)
    reconcile_invoice_status_from_payments(invoice)
    prerequisites = validate_invoice_issue_prerequisites(invoice)
    if prerequisites and invoice.status in {
        InvoiceStatusChoices.EMISE,
        InvoiceStatusChoices.PARTIELLEMENT_PAYEE,
        InvoiceStatusChoices.PAYEE,
    }:
        Invoice.objects.filter(pk=invoice.pk).update(status=InvoiceStatusChoices.BROUILLON)
        invoice.status = InvoiceStatusChoices.BROUILLON
    if invoice.status in {
        InvoiceStatusChoices.EMISE,
        InvoiceStatusChoices.PARTIELLEMENT_PAYEE,
        InvoiceStatusChoices.PAYEE,
    }:
        mark_invoice_ready_for_fne(invoice)
    run_invoice_data_quality_checks(invoice)
    try:
        emit_invoice_outbox_event(invoice, created=False)
    except Exception as exc:  # pragma: no cover - resilience guard
        signals_logger.warning("invoice_item_outbox_emit_failed invoice=%s reason=%s", invoice.pk, exc)


@receiver(post_delete, sender=InvoiceItem)
def invoice_item_post_delete(sender, instance, **kwargs):
    invoice = Invoice.objects.filter(pk=instance.invoice_id).first()
    if not invoice:
        return
    recalculate_invoice_totals(invoice)
    reconcile_invoice_status_from_payments(invoice)
    run_invoice_data_quality_checks(invoice)
    try:
        emit_invoice_outbox_event(invoice, created=False)
    except Exception as exc:  # pragma: no cover - resilience guard
        signals_logger.warning("invoice_item_delete_outbox_emit_failed invoice=%s reason=%s", invoice.pk, exc)


@receiver(post_save, sender=InvoicePayment)
def invoice_payment_post_save(sender, instance, created, **kwargs):
    invoice = Invoice.objects.filter(pk=instance.invoice_id).first()
    if not invoice:
        return
    recalculate_invoice_payment_snapshot(invoice, force=True)
    reconcile_invoice_status_from_payments(invoice)
    run_invoice_data_quality_checks(invoice)
    try:
        emit_invoice_outbox_event(invoice, created=False)
    except Exception as exc:  # pragma: no cover - resilience guard
        signals_logger.warning("invoice_payment_outbox_emit_failed invoice=%s reason=%s", invoice.pk, exc)
    try:
        emit_invoice_payment_outbox_event(
            instance,
            event_type="invoice_payment.created" if created else "invoice_payment.updated",
        )
    except Exception as exc:  # pragma: no cover - resilience guard
        signals_logger.warning("invoice_payment_event_emit_failed payment=%s reason=%s", instance.pk, exc)


@receiver(post_delete, sender=InvoicePayment)
def invoice_payment_post_delete(sender, instance, **kwargs):
    invoice = Invoice.objects.filter(pk=instance.invoice_id).first()
    if not invoice:
        return
    recalculate_invoice_payment_snapshot(invoice, force=True)
    reconcile_invoice_status_from_payments(invoice)
    run_invoice_data_quality_checks(invoice)
    try:
        emit_invoice_outbox_event(invoice, created=False)
    except Exception as exc:  # pragma: no cover - resilience guard
        signals_logger.warning("invoice_payment_delete_outbox_emit_failed invoice=%s reason=%s", invoice.pk, exc)
    try:
        emit_invoice_payment_outbox_event(instance, event_type="invoice_payment.deleted")
    except Exception as exc:  # pragma: no cover - resilience guard
        signals_logger.warning("invoice_payment_delete_event_emit_failed payment=%s reason=%s", instance.pk, exc)
