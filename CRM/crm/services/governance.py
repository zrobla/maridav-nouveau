from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Sum
from django.db.models.fields.files import FieldFile
from django.utils import timezone

from crm.models import (
    ApprovalPolicy,
    ApprovalRequest,
    ApprovalStatusChoices,
    ApprovalTypeChoices,
    AuditEventChoices,
    AuditSourceChoices,
    AuditTrail,
    DataQualityIssue,
    DataQualitySeverityChoices,
    DataQualityStatusChoices,
    EscalationLevelChoices,
    EscalationStatusChoices,
    Invoice,
    InvoiceNatureChoices,
    InvoicePaymentMethodChoices,
    InvoiceStatusChoices,
    InboundKindChoices,
    InboundRequest,
    InboundStatusChoices,
    Order,
    SlaEscalation,
    SupportCase,
    SupportStatusChoices,
    Task,
)
from crm.request_context import get_current_request


def _jsonable(value: Any):
    if value is None:
        return None
    if isinstance(value, FieldFile):
        return value.name or ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def model_snapshot(instance) -> dict[str, Any]:
    """Capture un snapshot stable des champs concrets pour l'audit."""
    data: dict[str, Any] = {}
    for field in instance._meta.concrete_fields:
        if field.many_to_many:
            continue
        field_name = field.name
        if field.is_relation and field_name.endswith("_ptr"):
            continue
        value = getattr(instance, f"{field_name}_id") if field.is_relation else getattr(instance, field_name)
        data[field_name] = _jsonable(value)
    return data


def diff_changed_fields(before_state: dict[str, Any], after_state: dict[str, Any]) -> list[str]:
    keys = set(before_state.keys()) | set(after_state.keys())
    changed = [key for key in keys if before_state.get(key) != after_state.get(key)]
    return sorted(changed)


def _derive_audit_source() -> str:
    request = get_current_request()
    if request is None:
        return AuditSourceChoices.SYSTEM
    if request.path.startswith("/api/"):
        return AuditSourceChoices.API
    return AuditSourceChoices.UI


def create_audit_trail(
    *,
    instance,
    event: str,
    message: str = "",
    before_state: dict[str, Any] | None = None,
    after_state: dict[str, Any] | None = None,
    changed_fields: list[str] | None = None,
) -> AuditTrail:
    request = get_current_request()
    actor = getattr(request, "user", None) if request is not None else None
    if actor is not None and getattr(actor, "is_authenticated", False) is False:
        actor = None

    before_state = before_state or {}
    after_state = after_state or {}
    changed_fields = changed_fields if changed_fields is not None else diff_changed_fields(before_state, after_state)

    request_id = ""
    ip_address = None
    user_agent = ""
    actor_display = ""

    if request is not None:
        request_id = getattr(request, "request_id", "") or request.headers.get("X-Request-ID", "")
        ip_address = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get(
            "REMOTE_ADDR"
        )
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        if actor:
            actor_display = request.user.get_username()
            try:
                actor_display = f"{actor_display} [{actor.security_profile.short_uuid}]"
            except Exception:
                pass
        else:
            actor_display = "anonymous"
    elif actor is not None:
        actor_display = actor.get_username()

    return AuditTrail.objects.create(
        event=event,
        source=_derive_audit_source(),
        content_type=ContentType.objects.get_for_model(instance.__class__),
        object_id=instance.pk,
        object_repr=str(instance)[:255],
        actor=actor,
        actor_display=actor_display,
        request_id=request_id,
        ip_address=ip_address or None,
        user_agent=user_agent[:255],
        message=message,
        changed_fields=changed_fields,
        before_state=before_state,
        after_state=after_state,
    )


def _normalize_phone(value: str) -> str:
    return re.sub(r"\D+", "", value or "")


def _upsert_data_quality_issue(
    *,
    inbound: InboundRequest,
    issue_type: str,
    severity: str,
    message: str,
    suggested_action: str,
    fingerprint: str,
    metadata: dict[str, Any] | None = None,
    matched_obj=None,
) -> DataQualityIssue:
    content_type = ContentType.objects.get_for_model(InboundRequest)
    defaults = {
        "severity": severity,
        "message": message,
        "suggested_action": suggested_action,
        "metadata": metadata or {},
        "status": DataQualityStatusChoices.OPEN,
        "matched_content_type": ContentType.objects.get_for_model(matched_obj.__class__) if matched_obj else None,
        "matched_object_id": matched_obj.pk if matched_obj else None,
    }
    existing = (
        DataQualityIssue.objects.filter(
            source="inbound",
            content_type=content_type,
            object_id=inbound.pk,
            issue_type=issue_type,
            fingerprint=fingerprint,
            status__in=[DataQualityStatusChoices.OPEN, DataQualityStatusChoices.IN_REVIEW],
        )
        .order_by("-created_at")
        .first()
    )
    if existing:
        for key, value in defaults.items():
            setattr(existing, key, value)
        existing.save()
        return existing
    return DataQualityIssue.objects.create(
        source="inbound",
        content_type=content_type,
        object_id=inbound.pk,
        issue_type=issue_type,
        fingerprint=fingerprint,
        **defaults,
    )


def run_inbound_data_quality_checks(inbound: InboundRequest) -> list[DataQualityIssue]:
    """
    Contrôles de base:
    - contact minimum (email ou téléphone),
    - consentement pour flux acquisition,
    - doublon potentiel par email/téléphone sur 60 jours.
    """
    issues: list[DataQualityIssue] = []

    if not inbound.email and not inbound.phone:
        issues.append(
            _upsert_data_quality_issue(
                inbound=inbound,
                issue_type="missing_required",
                severity=DataQualitySeverityChoices.HIGH,
                message="La demande ne contient ni email ni téléphone.",
                suggested_action="Compléter un canal de contact avant qualification.",
                fingerprint=f"inbound:{inbound.pk}:missing_contact",
                metadata={"missing_fields": ["email_or_phone"]},
            )
        )

    if inbound.kind in {InboundKindChoices.LEAD, InboundKindChoices.CONTACT, InboundKindChoices.PRODUCT} and not inbound.consent:
        issues.append(
            _upsert_data_quality_issue(
                inbound=inbound,
                issue_type="consent_missing",
                severity=DataQualitySeverityChoices.MEDIUM,
                message="Consentement marketing non explicite sur une demande de conversion.",
                suggested_action="Valider le consentement avant toute campagne sortante.",
                fingerprint=f"inbound:{inbound.pk}:consent_missing",
                metadata={"kind": inbound.kind},
            )
        )

    since = timezone.now() - timedelta(days=60)
    duplicate_query = InboundRequest.objects.exclude(pk=inbound.pk).filter(created_at__gte=since)
    duplicate_match = None

    if inbound.email:
        duplicate_match = duplicate_query.filter(email__iexact=inbound.email.strip()).order_by("-created_at").first()
    if duplicate_match is None and inbound.phone:
        phone = _normalize_phone(inbound.phone)
        if phone:
            duplicate_match = next(
                (
                    item
                    for item in duplicate_query.exclude(phone="").order_by("-created_at")[:50]
                    if _normalize_phone(item.phone) == phone
                ),
                None,
            )

    if duplicate_match is not None:
        identifier = inbound.email.strip().lower() if inbound.email else _normalize_phone(inbound.phone)
        issues.append(
            _upsert_data_quality_issue(
                inbound=inbound,
                issue_type="duplicate_potential",
                severity=DataQualitySeverityChoices.HIGH,
                message=(
                    "Doublon potentiel détecté avec une demande récente "
                    f"(ID #{duplicate_match.pk})."
                ),
                suggested_action="Fusionner les fiches ou rattacher la nouvelle requête au dossier existant.",
                fingerprint=f"inbound:{identifier}:dup",
                metadata={"duplicate_id": duplicate_match.pk},
                matched_obj=duplicate_match,
            )
        )

    return issues


def run_invoice_data_quality_checks(invoice: Invoice) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    content_type = ContentType.objects.get_for_model(Invoice)
    active_fingerprints: set[str] = set()

    def _upsert_issue(
        *,
        issue_type: str,
        severity: str,
        message: str,
        suggested_action: str,
        fingerprint: str,
        metadata: dict[str, Any] | None = None,
    ) -> DataQualityIssue:
        defaults = {
            "severity": severity,
            "message": message,
            "suggested_action": suggested_action,
            "metadata": metadata or {},
            "status": DataQualityStatusChoices.OPEN,
        }
        existing = (
            DataQualityIssue.objects.filter(
                source="invoice",
                content_type=content_type,
                object_id=invoice.pk,
                issue_type=issue_type,
                fingerprint=fingerprint,
                status__in=[DataQualityStatusChoices.OPEN, DataQualityStatusChoices.IN_REVIEW],
            )
            .order_by("-created_at")
            .first()
        )
        if existing:
            for key, value in defaults.items():
                setattr(existing, key, value)
            existing.save()
            active_fingerprints.add(fingerprint)
            return existing
        issue = DataQualityIssue.objects.create(
            source="invoice",
            content_type=content_type,
            object_id=invoice.pk,
            issue_type=issue_type,
            fingerprint=fingerprint,
            **defaults,
        )
        active_fingerprints.add(fingerprint)
        return issue

    if invoice.items.count() == 0:
        issues.append(
            _upsert_issue(
                issue_type="missing_required",
                severity=DataQualitySeverityChoices.HIGH,
                message="La facture ne contient aucune ligne produit.",
                suggested_action="Ajouter au moins une ligne avant émission.",
                fingerprint=f"invoice:{invoice.pk}:no_items",
                metadata={"invoice_number": invoice.invoice_number},
            )
        )

    customer = invoice.customer
    missing_fiscal = [
        label
        for attr, label in [
            ("tax_ncc", "NCC"),
            ("tax_ntd", "NTD"),
            ("tax_rccm", "RCCM"),
            ("tax_regime", "Régime fiscal"),
        ]
        if not getattr(customer, attr, "")
    ]
    if missing_fiscal and invoice.status in {InvoiceStatusChoices.EMISE, InvoiceStatusChoices.PARTIELLEMENT_PAYEE, InvoiceStatusChoices.PAYEE}:
        issues.append(
            _upsert_issue(
                issue_type="missing_required",
                severity=DataQualitySeverityChoices.HIGH,
                message="Profil fiscal client incomplet pour émission conforme.",
                suggested_action="Compléter les champs fiscaux client avant certification FNE.",
                fingerprint=f"invoice:{invoice.pk}:missing_fiscal_profile",
                metadata={"missing_fields": missing_fiscal, "customer_id": customer.pk},
            )
        )

    if int(invoice.paid_amount or 0) > int(invoice.total_amount or 0):
        issues.append(
            _upsert_issue(
                issue_type="inconsistent_data",
                severity=DataQualitySeverityChoices.MEDIUM,
                message="Le montant payé dépasse le total de la facture.",
                suggested_action="Vérifier la saisie paiement ou recalculer les totaux.",
                fingerprint=f"invoice:{invoice.pk}:paid_exceeds_total",
                metadata={
                    "paid_amount": int(invoice.paid_amount or 0),
                    "total_amount": int(invoice.total_amount or 0),
                },
            )
        )

    payment_ledger_total = int(invoice.payments.aggregate(total=Sum("amount")).get("total") or 0)
    paid_amount = int(invoice.paid_amount or 0)
    if payment_ledger_total != paid_amount:
        issues.append(
            _upsert_issue(
                issue_type="inconsistent_data",
                severity=DataQualitySeverityChoices.HIGH,
                message="Incohérence entre ledger paiements et montant payé facture.",
                suggested_action="Rafraîchir la facture et corriger les écritures paiements incohérentes.",
                fingerprint=f"invoice:{invoice.pk}:payment_ledger_mismatch",
                metadata={
                    "invoice_number": invoice.invoice_number,
                    "paid_amount": paid_amount,
                    "payment_ledger_total": payment_ledger_total,
                },
            )
        )

    if paid_amount > 0 and invoice.payment_method == InvoicePaymentMethodChoices.NON_RENSEIGNE:
        issues.append(
            _upsert_issue(
                issue_type="missing_required",
                severity=DataQualitySeverityChoices.MEDIUM,
                message="Montant payé renseigné sans mode de paiement exploitable.",
                suggested_action="Enregistrer le paiement via le ledger pour fiabiliser le mode et la référence.",
                fingerprint=f"invoice:{invoice.pk}:payment_method_missing",
                metadata={
                    "invoice_number": invoice.invoice_number,
                    "paid_amount": paid_amount,
                    "payment_method": invoice.payment_method,
                },
            )
        )

    if invoice.nature == InvoiceNatureChoices.CREDIT_NOTE and not invoice.original_invoice_id:
        issues.append(
            _upsert_issue(
                issue_type="missing_required",
                severity=DataQualitySeverityChoices.HIGH,
                message="Avoir sans facture d'origine liée.",
                suggested_action="Renseigner la facture d'origine avant émission.",
                fingerprint=f"invoice:{invoice.pk}:credit_note_without_original",
                metadata={"invoice_number": invoice.invoice_number},
            )
        )

    stale_issues = DataQualityIssue.objects.filter(
        source="invoice",
        content_type=content_type,
        object_id=invoice.pk,
        status__in=[DataQualityStatusChoices.OPEN, DataQualityStatusChoices.IN_REVIEW],
        fingerprint__startswith=f"invoice:{invoice.pk}:",
    )
    if active_fingerprints:
        stale_issues = stale_issues.exclude(fingerprint__in=list(active_fingerprints))
    for stale in stale_issues:
        stale.status = DataQualityStatusChoices.RESOLVED
        stale.resolved_at = timezone.now()
        stale.save(update_fields=["status", "resolved_at", "updated_at"])

    return issues


def _resolve_default_approver(policy: ApprovalPolicy):
    if policy.default_approver_id:
        return policy.default_approver
    if policy.approver_group_id:
        user = policy.approver_group.user_set.filter(is_active=True).order_by("id").first()
        if user:
            return user
    return None


def apply_order_approval_policy(order: Order, requested_by=None) -> tuple[ApprovalRequest | None, bool]:
    """Crée (ou met à jour) une demande d'approbation si la commande dépasse la politique."""
    order_total = int(order.total_amount or 0)
    discount_pct = float(order.discount_pct or 0)
    needs_credit = bool(order.credit_exception_requested)

    policies = ApprovalPolicy.objects.filter(active=True).order_by("-min_order_total", "-min_discount_pct", "id")
    policy = next(
        (item for item in policies if item.applies_to_order(order_total, discount_pct, needs_credit)),
        None,
    )
    if policy is None:
        return None, False

    request_type = ApprovalTypeChoices.CREDIT if needs_credit else ApprovalTypeChoices.DISCOUNT
    if request_type == ApprovalTypeChoices.DISCOUNT and discount_pct < float(policy.min_discount_pct or 0):
        request_type = ApprovalTypeChoices.PRICING

    content_type = ContentType.objects.get_for_model(Order)
    defaults = {
        "request_type": request_type,
        "status": ApprovalStatusChoices.PENDING,
        "reason": (
            f"Commande {order.order_number}: validation requise (total={order_total} FCFA, remise={discount_pct}%)."
        ),
        "requested_by": requested_by,
        "assigned_to": _resolve_default_approver(policy),
        "amount_fcfa": order_total,
        "discount_pct": Decimal(str(discount_pct)),
        "metadata": {
            "policy": policy.name,
            "policy_id": policy.id,
            "credit_exception_requested": needs_credit,
        },
    }

    pending = ApprovalRequest.objects.filter(
        entity_type="order",
        content_type=content_type,
        object_id=order.pk,
        status=ApprovalStatusChoices.PENDING,
    ).first()
    if pending:
        for key, value in defaults.items():
            setattr(pending, key, value)
        pending.save()
        return pending, False

    approval = ApprovalRequest.objects.create(
        entity_type="order",
        content_type=content_type,
        object_id=order.pk,
        **defaults,
    )
    return approval, True


def _escalation_level_from_overdue_hours(hours: float) -> str:
    if hours >= 24:
        return EscalationLevelChoices.LEVEL_3
    if hours >= 8:
        return EscalationLevelChoices.LEVEL_2
    return EscalationLevelChoices.LEVEL_1


def _create_or_get_escalation(
    *,
    source_type: str,
    obj,
    due_at: datetime,
    reason: str,
    level: str,
    assigned_to=None,
):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    escalation = (
        SlaEscalation.objects.filter(
            source_type=source_type,
            content_type=content_type,
            object_id=obj.pk,
            escalation_level=level,
            status__in=[EscalationStatusChoices.OPEN, EscalationStatusChoices.ACK],
        )
        .order_by("-escalated_at")
        .first()
    )
    if escalation:
        changed_fields = []
        if escalation.due_at != due_at:
            escalation.due_at = due_at
            changed_fields.append("due_at")
        if escalation.reason != reason:
            escalation.reason = reason
            changed_fields.append("reason")
        if assigned_to and escalation.assigned_to_id != assigned_to.id:
            escalation.assigned_to = assigned_to
            changed_fields.append("assigned_to")
        if changed_fields:
            changed_fields.append("updated_at")
            escalation.save(update_fields=changed_fields)
        return escalation, False

    escalation = SlaEscalation.objects.create(
        source_type=source_type,
        content_type=content_type,
        object_id=obj.pk,
        escalation_level=level,
        status=EscalationStatusChoices.OPEN,
        due_at=due_at,
        reason=reason,
        assigned_to=assigned_to,
    )
    return escalation, True


def _resolve_notified_group(level: str) -> Group | None:
    group_candidates = {
        EscalationLevelChoices.LEVEL_1: ["Technicien CRM & Support IT", "Support Technique"],
        EscalationLevelChoices.LEVEL_2: ["Directeur Commercial", "Gouvernance & Conformité"],
        EscalationLevelChoices.LEVEL_3: ["Direction Générale", "Direction/Propriétaire", "Administrateur Système"],
    }
    for group_name in group_candidates.get(level, []):
        group = Group.objects.filter(name=group_name).first()
        if group:
            return group
    return Group.objects.filter(name="Gouvernance & Conformité").first()


def _resolve_assigned_user(escalation: SlaEscalation):
    if escalation.assigned_to_id:
        return escalation.assigned_to
    if escalation.notified_group_id:
        return escalation.notified_group.user_set.filter(is_active=True).order_by("id").first()
    return None


def _build_escalation_reference(escalation: SlaEscalation) -> str:
    return f"SLA:{escalation.source_type}:{escalation.object_id}:{escalation.escalation_level}"


def _ensure_escalation_task(escalation: SlaEscalation, source_obj, now: datetime) -> tuple[Task | None, bool]:
    reference = _build_escalation_reference(escalation)
    title = f"[{reference}] Escalade automatique"
    existing = Task.objects.filter(title=title).first()
    if existing:
        return existing, False

    task_kwargs = {
        "title": title,
        "description": (
            f"Escalade {escalation.get_escalation_level_display()} sur {escalation.get_source_type_display()} "
            f"(objet #{escalation.object_id}). Motif: {escalation.reason}"
        ),
        "due_date": now.date(),
        "assigned_to": _resolve_assigned_user(escalation),
    }

    if escalation.source_type == "support":
        task_kwargs["support_case"] = source_obj
        task_kwargs["customer"] = getattr(source_obj, "customer", None)
    elif escalation.source_type == "inbound":
        lead = getattr(source_obj, "lead", None)
        if lead:
            task_kwargs["lead"] = lead

    task = Task.objects.create(**task_kwargs)
    return task, True


def _apply_escalation_automation(
    escalation: SlaEscalation,
    *,
    source_obj,
    now: datetime,
    created: bool,
) -> dict[str, int]:
    updates = []
    notification_count = 0
    task_created_count = 0

    notified_group = _resolve_notified_group(escalation.escalation_level)
    if notified_group and escalation.notified_group_id != notified_group.id:
        escalation.notified_group = notified_group
        updates.append("notified_group")

    if not escalation.assigned_to_id:
        assigned_user = _resolve_assigned_user(escalation)
        if assigned_user and escalation.assigned_to_id != assigned_user.id:
            escalation.assigned_to = assigned_user
            updates.append("assigned_to")

    metadata = dict(escalation.metadata or {})
    notifications = list(metadata.get("notifications", []))
    notification_key = f"{escalation.escalation_level}:{escalation.status}"
    if created or notification_key not in {item.get("key") for item in notifications}:
        notifications.append(
            {
                "key": notification_key,
                "notified_at": now.isoformat(),
                "group": escalation.notified_group.name if escalation.notified_group_id else "",
            }
        )
        metadata["notifications"] = notifications
        escalation.metadata = metadata
        updates.append("metadata")
        notification_count += 1

    task, task_created = _ensure_escalation_task(escalation, source_obj, now)
    if task_created:
        task_created_count += 1
        create_audit_trail(
            instance=escalation,
            event=AuditEventChoices.SLA,
            message=(
                f"Escalade {escalation.escalation_level} notifiée au groupe "
                f"{escalation.notified_group.name if escalation.notified_group_id else 'N/A'}; "
                f"task automatique #{task.pk} créée."
            ),
        )

    if updates:
        updates.append("updated_at")
        escalation.save(update_fields=updates)

    return {
        "notifications": notification_count,
        "tasks_created": task_created_count,
    }


def _close_previous_open_levels(escalation: SlaEscalation, now: datetime) -> int:
    closed_count = 0
    previous = (
        SlaEscalation.objects.filter(
            source_type=escalation.source_type,
            content_type=escalation.content_type,
            object_id=escalation.object_id,
            status__in=[EscalationStatusChoices.OPEN, EscalationStatusChoices.ACK],
        )
        .exclude(pk=escalation.pk)
    )
    for item in previous:
        item.status = EscalationStatusChoices.RESOLVED
        item.resolved_at = now
        item.save(update_fields=["status", "resolved_at", "updated_at"])
        closed_count += 1
    return closed_count


def refresh_sla_escalations(now: datetime | None = None) -> dict[str, int]:
    """Rafraîchit les escalades SLA ouvertes pour Inbox et Support."""
    now = now or timezone.now()
    created_count = 0
    resolved_count = 0
    notifications_count = 0
    tasks_created_count = 0

    overdue_inbound = InboundRequest.objects.filter(
        first_response_at__isnull=True,
        first_response_due_at__lt=now,
    ).exclude(status=InboundStatusChoices.CLOTURE)
    tracked_inbound_ids = set()

    for inbound in overdue_inbound:
        due_at = inbound.first_response_due_at
        if due_at is None:
            continue
        overdue_hours = max(0.0, (now - due_at).total_seconds() / 3600)
        level = _escalation_level_from_overdue_hours(overdue_hours)
        escalation, created = _create_or_get_escalation(
            source_type="inbound",
            obj=inbound,
            due_at=due_at,
            reason="SLA première réponse dépassé.",
            level=level,
            assigned_to=inbound.assigned_to,
        )
        tracked_inbound_ids.add(inbound.pk)
        if created:
            created_count += 1
        resolved_count += _close_previous_open_levels(escalation, now)
        automation_metrics = _apply_escalation_automation(
            escalation,
            source_obj=inbound,
            now=now,
            created=created,
        )
        notifications_count += automation_metrics["notifications"]
        tasks_created_count += automation_metrics["tasks_created"]

    open_inbound_escalations = SlaEscalation.objects.filter(
        source_type="inbound",
        status__in=[EscalationStatusChoices.OPEN, EscalationStatusChoices.ACK],
    ).exclude(object_id__in=tracked_inbound_ids)
    for escalation in open_inbound_escalations:
        escalation.status = EscalationStatusChoices.RESOLVED
        escalation.resolved_at = now
        escalation.save(update_fields=["status", "resolved_at", "updated_at"])
        resolved_count += 1

    overdue_support = SupportCase.objects.filter(
        due_date__isnull=False,
        due_date__lt=now.date(),
        status__in=[SupportStatusChoices.OUVERT, SupportStatusChoices.EN_COURS, SupportStatusChoices.EN_ATTENTE],
    )
    tracked_support_ids = set()
    for case in overdue_support:
        due_at = timezone.make_aware(datetime.combine(case.due_date, time(23, 59)))
        overdue_hours = max(0.0, (now - due_at).total_seconds() / 3600)
        level = _escalation_level_from_overdue_hours(overdue_hours)
        escalation, created = _create_or_get_escalation(
            source_type="support",
            obj=case,
            due_at=due_at,
            reason="Ticket support en dépassement d'échéance.",
            level=level,
            assigned_to=case.assigned_to,
        )
        tracked_support_ids.add(case.pk)
        if created:
            created_count += 1
        resolved_count += _close_previous_open_levels(escalation, now)
        automation_metrics = _apply_escalation_automation(
            escalation,
            source_obj=case,
            now=now,
            created=created,
        )
        notifications_count += automation_metrics["notifications"]
        tasks_created_count += automation_metrics["tasks_created"]

    open_support_escalations = SlaEscalation.objects.filter(
        source_type="support",
        status__in=[EscalationStatusChoices.OPEN, EscalationStatusChoices.ACK],
    ).exclude(object_id__in=tracked_support_ids)
    for escalation in open_support_escalations:
        escalation.status = EscalationStatusChoices.RESOLVED
        escalation.resolved_at = now
        escalation.save(update_fields=["status", "resolved_at", "updated_at"])
        resolved_count += 1

    return {
        "created": created_count,
        "resolved": resolved_count,
        "notifications": notifications_count,
        "tasks_created": tasks_created_count,
    }
