from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from crm.models import (
    ApprovalPolicy,
    ApprovalRequest,
    ApprovalStatusChoices,
    ApprovalTypeChoices,
    Customer,
    Order,
    OrderItem,
    Product,
    ProductCategory,
)

User = get_user_model()


class OrderApprovalWorkflowPhase3Tests(TestCase):
    def setUp(self):
        super().setUp()
        self.approver_group = Group.objects.create(name="Finance Approbation")
        self.approver = User.objects.create_user(username="approver_finance", password="StrongPass!234")
        self.approver_group.user_set.add(self.approver)

        self.customer = Customer.objects.create(
            name="Client Workflow",
            code="C-WORKFLOW",
            region="Bouake",
        )
        self.category = ProductCategory.objects.create(name="Aliments", slug="aliments")
        self.product = Product.objects.create(
            category=self.category,
            name="Granules Test",
            sku="SKU-WORK-001",
            unit_price=25000,
        )

    def test_order_item_threshold_creates_and_updates_single_pending_approval(self):
        ApprovalPolicy.objects.create(
            name="Policy seuil commande",
            active=True,
            min_order_total=100000,
            min_discount_pct=0,
            approver_group=self.approver_group,
        )
        order = Order.objects.create(customer=self.customer)
        self.assertFalse(ApprovalRequest.objects.filter(entity_type="order", object_id=order.pk).exists())

        OrderItem.objects.create(order=order, product=self.product, quantity=5, unit_price=25000)

        approval = ApprovalRequest.objects.get(entity_type="order", object_id=order.pk, status=ApprovalStatusChoices.PENDING)
        self.assertEqual(approval.request_type, ApprovalTypeChoices.DISCOUNT)
        self.assertEqual(approval.assigned_to, self.approver)
        self.assertEqual(approval.amount_fcfa, 125000)
        self.assertEqual((approval.metadata or {}).get("policy"), "Policy seuil commande")

        # Deuxième ligne: mise à jour de la demande existante, pas de duplication.
        OrderItem.objects.create(order=order, product=self.product, quantity=1, unit_price=5000)
        self.assertEqual(
            ApprovalRequest.objects.filter(entity_type="order", object_id=order.pk, status=ApprovalStatusChoices.PENDING).count(),
            1,
        )
        approval.refresh_from_db()
        self.assertEqual(approval.amount_fcfa, 130000)

    def test_credit_exception_creates_credit_request_and_remains_idempotent(self):
        ApprovalPolicy.objects.create(
            name="Policy exception credit",
            active=True,
            min_order_total=0,
            min_discount_pct=99,
            require_credit_exception=True,
            default_approver=self.approver,
        )

        order = Order.objects.create(
            customer=self.customer,
            credit_exception_requested=True,
            discount_pct=0,
        )

        approval = ApprovalRequest.objects.get(entity_type="order", object_id=order.pk, status=ApprovalStatusChoices.PENDING)
        self.assertEqual(approval.request_type, ApprovalTypeChoices.CREDIT)
        self.assertEqual(approval.assigned_to, self.approver)
        self.assertTrue((approval.metadata or {}).get("credit_exception_requested"))

        # Nouveau save de commande: toujours une seule demande pending.
        order.notes = "Mise à jour dossier"
        order.save()
        self.assertEqual(
            ApprovalRequest.objects.filter(entity_type="order", object_id=order.pk, status=ApprovalStatusChoices.PENDING).count(),
            1,
        )
