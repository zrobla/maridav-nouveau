from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from crm.models import (
    Customer,
    EscalationLevelChoices,
    EscalationStatusChoices,
    InboundRequest,
    SlaEscalation,
    SupportCase,
    Task,
)

User = get_user_model()


class SLAOrchestrationPhase2Tests(TestCase):
    def setUp(self):
        super().setUp()
        self.group_l1 = Group.objects.create(name="Technicien CRM & Support IT")
        self.group_l2 = Group.objects.create(name="Directeur Commercial")
        self.group_l3 = Group.objects.create(name="Direction Générale")

        self.l1_user = User.objects.create_user(username="l1_user", password="StrongPass!234")
        self.l2_user = User.objects.create_user(username="l2_user", password="StrongPass!234")
        self.l3_user = User.objects.create_user(username="l3_user", password="StrongPass!234")
        self.group_l1.user_set.add(self.l1_user)
        self.group_l2.user_set.add(self.l2_user)
        self.group_l3.user_set.add(self.l3_user)

    def _create_overdue_inbound(self, hours: int) -> InboundRequest:
        return InboundRequest.objects.create(
            kind="lead",
            name=f"Inbound overdue {hours}h",
            first_response_due_at=timezone.now() - timedelta(hours=hours),
        )

    def test_command_creates_escalation_notification_and_task(self):
        inbound = self._create_overdue_inbound(hours=2)

        call_command("run_sla_orchestration")

        escalation = SlaEscalation.objects.get(source_type="inbound", object_id=inbound.pk)
        self.assertEqual(escalation.escalation_level, EscalationLevelChoices.LEVEL_1)
        self.assertEqual(escalation.status, EscalationStatusChoices.OPEN)
        self.assertEqual(escalation.notified_group, self.group_l1)
        self.assertEqual(escalation.assigned_to, self.l1_user)
        self.assertTrue((escalation.metadata or {}).get("notifications"))

        task = Task.objects.get(title=f"[SLA:inbound:{inbound.pk}:l1] Escalade automatique")
        self.assertEqual(task.assigned_to, self.l1_user)

        # Idempotence: relancer n'empile pas une nouvelle tâche identique.
        call_command("run_sla_orchestration")
        self.assertEqual(Task.objects.filter(title=task.title).count(), 1)

    def test_level_promotion_to_l3_closes_previous_open_level(self):
        inbound = self._create_overdue_inbound(hours=2)
        call_command("run_sla_orchestration")

        InboundRequest.objects.filter(pk=inbound.pk).update(
            first_response_due_at=timezone.now() - timedelta(hours=30)
        )
        call_command("run_sla_orchestration")

        open_escalations = SlaEscalation.objects.filter(
            source_type="inbound",
            object_id=inbound.pk,
            status__in=[EscalationStatusChoices.OPEN, EscalationStatusChoices.ACK],
        )
        self.assertEqual(open_escalations.count(), 1)
        self.assertEqual(open_escalations.first().escalation_level, EscalationLevelChoices.LEVEL_3)
        self.assertEqual(open_escalations.first().notified_group, self.group_l3)
        self.assertEqual(open_escalations.first().assigned_to, self.l3_user)

        self.assertTrue(
            SlaEscalation.objects.filter(
                source_type="inbound",
                object_id=inbound.pk,
                escalation_level=EscalationLevelChoices.LEVEL_1,
                status=EscalationStatusChoices.RESOLVED,
            ).exists()
        )

    def test_command_handles_overdue_support_without_ui_traffic(self):
        customer = Customer.objects.create(name="Client SLA", code="C-SLA")
        support = SupportCase.objects.create(
            customer=customer,
            description="Ticket de test",
            due_date=timezone.now().date() + timedelta(days=1),
        )
        # Bypass signaux pour simuler un ticket devenu overdue sans action UI.
        SupportCase.objects.filter(pk=support.pk).update(due_date=timezone.now().date() - timedelta(days=1))

        call_command("run_sla_orchestration")

        escalation = SlaEscalation.objects.get(source_type="support", object_id=support.pk)
        self.assertEqual(escalation.status, EscalationStatusChoices.OPEN)
        self.assertIsNotNone(escalation.notified_group_id)

        sla_task = Task.objects.filter(title__contains=f"SLA:support:{support.pk}:").first()
        self.assertIsNotNone(sla_task)
        self.assertEqual(sla_task.support_case_id, support.pk)
