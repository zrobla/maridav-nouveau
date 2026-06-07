from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from crm.models import (
    ChannelChoices,
    InboundPriorityChoices,
    InboundRequest,
    InboundStatusChoices,
    Lead,
    RoutingRule,
    SpeciesChoices,
)

User = get_user_model()


@dataclass
class SlaWindow:
    first_response_hours: int
    resolution_hours: int


SLA_WINDOWS = {
    InboundPriorityChoices.URGENT: SlaWindow(first_response_hours=2, resolution_hours=24),
    InboundPriorityChoices.ELEVE: SlaWindow(first_response_hours=4, resolution_hours=48),
    InboundPriorityChoices.NORMAL: SlaWindow(first_response_hours=12, resolution_hours=72),
    InboundPriorityChoices.FAIBLE: SlaWindow(first_response_hours=24, resolution_hours=120),
}


def _extract_volume_score(value: str) -> int:
    if not value:
        return 0
    matches = re.findall(r"\d+", str(value))
    if not matches:
        return 0
    number = int(matches[0])
    if number >= 1000:
        return 20
    if number >= 500:
        return 15
    if number >= 100:
        return 10
    return 5


def calculate_lead_score(payload: dict) -> int:
    score = 10
    if payload.get("company"):
        score += 15
    if payload.get("phone") and payload.get("email"):
        score += 10
    elif payload.get("phone") or payload.get("email"):
        score += 5

    score += _extract_volume_score(payload.get("volume") or payload.get("expected_volume") or "")

    intent = (payload.get("intent") or payload.get("objective") or "").lower()
    if any(word in intent for word in ["devis", "commande", "achat", "prix"]):
        score += 10

    product = (payload.get("product") or payload.get("product_interest") or "").lower()
    if product:
        score += 5

    channel = (payload.get("channel_preference") or payload.get("preferred_channel") or "").lower()
    if channel in {ChannelChoices.WHATSAPP, ChannelChoices.APPEL}:
        score += 5

    segment = (payload.get("segment") or "").lower()
    if segment == SpeciesChoices.MULTI:
        score += 5

    return min(score, 100)


def calculate_priority(payload: dict) -> str:
    segment = (payload.get("segment") or "").lower()
    intent = (payload.get("intent") or payload.get("objective") or "").lower()
    channel = (payload.get("channel_preference") or payload.get("preferred_channel") or "").lower()
    has_volume = bool(payload.get("volume") or payload.get("expected_volume"))

    if "urgence" in intent or segment == SpeciesChoices.BIOSECURITE:
        return InboundPriorityChoices.URGENT
    if channel in {ChannelChoices.WHATSAPP, ChannelChoices.APPEL} and has_volume:
        return InboundPriorityChoices.ELEVE
    if not payload.get("phone") and payload.get("email") and not has_volume:
        return InboundPriorityChoices.FAIBLE
    return InboundPriorityChoices.NORMAL


def get_sla_deadlines(priority: str, created_at=None):
    created_at = created_at or timezone.now()
    window = SLA_WINDOWS.get(priority, SLA_WINDOWS[InboundPriorityChoices.NORMAL])
    first_response_due = created_at + timedelta(hours=window.first_response_hours)
    resolution_due = created_at + timedelta(hours=window.resolution_hours)
    return first_response_due, resolution_due


def find_routing_rule(inbound: InboundRequest):
    rules = RoutingRule.objects.filter(active=True).order_by("priority", "id")
    for rule in rules:
        if rule.kind and rule.kind != inbound.kind:
            continue
        if rule.segment and rule.segment != inbound.segment:
            continue
        if rule.channel_preference and rule.channel_preference != inbound.channel_preference:
            continue
        if rule.region:
            region = (inbound.region or "").lower()
            if rule.region.lower() not in region:
                continue
        return rule
    return None


def ensure_inbound_defaults(inbound: InboundRequest):
    updates = {}
    if not inbound.priority:
        updates["priority"] = calculate_priority(
            {
                "segment": inbound.segment,
                "intent": inbound.intent,
                "objective": inbound.objective,
                "channel_preference": inbound.channel_preference,
                "volume": inbound.volume,
                "phone": inbound.phone,
                "email": inbound.email,
            }
        )

    priority = updates.get("priority") or inbound.priority
    if not inbound.first_response_due_at or not inbound.resolution_due_at:
        first_due, resolution_due = get_sla_deadlines(priority, inbound.created_at)
        if not inbound.first_response_due_at:
            updates["first_response_due_at"] = first_due
        if not inbound.resolution_due_at:
            updates["resolution_due_at"] = resolution_due

    if inbound.assigned_to_id is None:
        rule = find_routing_rule(inbound)
        if rule and rule.assigned_to_id:
            updates["assigned_to"] = rule.assigned_to

    if updates:
        InboundRequest.objects.filter(pk=inbound.pk).update(**updates)
        for key, value in updates.items():
            setattr(inbound, key, value)
    return updates


def ensure_lead_score(lead: Lead, payload: dict | None = None) -> int:
    if lead.lead_score:
        return lead.lead_score
    data = payload or {
        "company": lead.company,
        "phone": lead.phone,
        "email": lead.email,
        "segment": lead.segment,
        "expected_volume": lead.expected_volume,
        "product_interest": lead.product_interest,
        "objective": lead.objective,
        "preferred_channel": lead.preferred_channel,
    }
    score = calculate_lead_score(data)
    Lead.objects.filter(pk=lead.pk).update(lead_score=score)
    lead.lead_score = score
    return score


def should_mark_first_response(inbound: InboundRequest) -> bool:
    if inbound.first_response_at:
        return False
    return inbound.status != InboundStatusChoices.NOUVEAU


def should_mark_resolved(inbound: InboundRequest) -> bool:
    if inbound.resolved_at:
        return False
    return inbound.status in {InboundStatusChoices.CONVERTI, InboundStatusChoices.CLOTURE}
