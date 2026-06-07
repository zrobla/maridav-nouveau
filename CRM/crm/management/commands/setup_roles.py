"""Initialise les rôles et permissions CRM."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from crm import models


def perms_for(model, *actions):
    codenames = [f"{action}_{model._meta.model_name}" for action in actions]
    return list(Permission.objects.filter(codename__in=codenames))


def perms_by_codename(*codenames):
    return list(Permission.objects.filter(codename__in=codenames))


class Command(BaseCommand):
    help = "Crée les groupes premium CRM + gouvernance IAM avec permissions alignées corporate."

    def handle(self, *args, **options):
        User = get_user_model()
        direction_proprietaire, _ = Group.objects.get_or_create(name="Direction/Propriétaire")
        direction_generale, _ = Group.objects.get_or_create(name="Direction Générale")
        administrateur_systeme, _ = Group.objects.get_or_create(name="Administrateur Système")
        directeur_commercial, _ = Group.objects.get_or_create(name="Directeur Commercial")
        commerciaux, _ = Group.objects.get_or_create(name="Commerciaux")
        technico_commerciaux, _ = Group.objects.get_or_create(name="Technico-Commerciaux")
        experts_metier, _ = Group.objects.get_or_create(name="Experts Métier")
        technicien_crm, _ = Group.objects.get_or_create(name="Technicien CRM & Support IT")
        support, _ = Group.objects.get_or_create(name="Support Technique")
        caissiere, _ = Group.objects.get_or_create(name="Caissière")
        comptable, _ = Group.objects.get_or_create(name="Comptable")
        gouvernance, _ = Group.objects.get_or_create(name="Gouvernance & Conformité")

        crm_all = list(Permission.objects.filter(content_type__app_label="crm"))
        auth_admin = perms_by_codename(
            "view_user",
            "add_user",
            "change_user",
            "delete_user",
            "view_group",
            "add_group",
            "change_group",
            "delete_group",
        )

        # Direction/Propriétaire + Direction Générale: contrôle global
        direction_proprietaire.permissions.set(crm_all + auth_admin)
        direction_generale.permissions.set(crm_all + auth_admin)

        # Administrateur système : exploitation plateforme + IAM
        admin_perms = []
        admin_perms += crm_all
        admin_perms += auth_admin
        administrateur_systeme.permissions.set(admin_perms)

        # Directeur Commercial : pilotage des équipes et pipeline
        dc_perms = []
        dc_perms += perms_by_codename("view_dashboard", "view_reports", "manage_sales_team")
        dc_perms += perms_for(models.InboundRequest, "view", "change")
        dc_perms += perms_for(models.Customer, "view", "add", "change")
        dc_perms += perms_for(models.Contact, "view", "add", "change")
        dc_perms += perms_for(models.Lead, "view", "add", "change")
        dc_perms += perms_for(models.Opportunity, "view", "add", "change")
        dc_perms += perms_for(models.Order, "view", "add", "change")
        dc_perms += perms_for(models.OrderItem, "view", "add", "change")
        dc_perms += perms_for(models.Invoice, "view", "add", "change")
        dc_perms += perms_for(models.InvoiceItem, "view", "add", "change")
        dc_perms += perms_for(models.Task, "view", "add", "change")
        dc_perms += perms_for(models.VisitReport, "view", "add", "change")
        dc_perms += perms_for(models.SupportCase, "view", "add", "change")
        dc_perms += perms_for(models.Product, "view", "add", "change")
        dc_perms += perms_for(models.ProductCategory, "view", "add", "change")
        dc_perms += perms_for(models.Forecast, "view", "add", "change")
        dc_perms += perms_for(models.Promotion, "view", "add", "change")
        dc_perms += perms_for(models.ApprovalRequest, "view", "change")
        dc_perms += perms_for(models.ApprovalPolicy, "view")
        dc_perms += perms_for(models.DataQualityIssue, "view", "change")
        dc_perms += perms_for(models.SlaEscalation, "view", "change")
        dc_perms += perms_for(models.AuditTrail, "view")
        dc_perms += perms_for(models.EnterpriseOutboxEvent, "view")
        dc_perms += perms_for(models.EnterpriseInboxEvent, "view")
        directeur_commercial.permissions.set(dc_perms)

        # Commerciaux : gestion portefeuille + conversion
        sales_perms = []
        sales_perms += perms_by_codename("view_dashboard")
        sales_perms += perms_for(models.InboundRequest, "view", "add", "change")
        sales_perms += perms_for(models.Customer, "view")
        sales_perms += perms_for(models.Contact, "view", "add", "change")
        sales_perms += perms_for(models.Lead, "view", "add", "change")
        sales_perms += perms_for(models.Opportunity, "view", "add", "change")
        sales_perms += perms_for(models.Order, "view", "add", "change")
        sales_perms += perms_for(models.OrderItem, "view", "add", "change")
        sales_perms += perms_for(models.Invoice, "view", "add", "change")
        sales_perms += perms_for(models.InvoiceItem, "view", "add", "change")
        sales_perms += perms_for(models.Task, "view", "add", "change")
        sales_perms += perms_for(models.VisitReport, "view", "add")
        sales_perms += perms_for(models.SupportCase, "view", "add", "change")
        sales_perms += perms_for(models.Product, "view")
        sales_perms += perms_for(models.ProductCategory, "view")
        sales_perms += perms_for(models.ApprovalRequest, "view")
        sales_perms += perms_for(models.DataQualityIssue, "view")
        sales_perms += perms_for(models.SlaEscalation, "view")
        commerciaux.permissions.set(sales_perms)

        # Technico-commerciaux : conversion + expertise terrain + suivi technique.
        tech_sales_perms = []
        tech_sales_perms += perms_by_codename("view_dashboard")
        tech_sales_perms += perms_for(models.InboundRequest, "view", "add", "change")
        tech_sales_perms += perms_for(models.Customer, "view", "add", "change")
        tech_sales_perms += perms_for(models.Contact, "view", "add", "change")
        tech_sales_perms += perms_for(models.Lead, "view", "add", "change")
        tech_sales_perms += perms_for(models.Opportunity, "view", "add", "change")
        tech_sales_perms += perms_for(models.Order, "view", "add", "change")
        tech_sales_perms += perms_for(models.OrderItem, "view", "add", "change")
        tech_sales_perms += perms_for(models.Invoice, "view", "add", "change")
        tech_sales_perms += perms_for(models.InvoiceItem, "view", "add", "change")
        tech_sales_perms += perms_for(models.SupportCase, "view", "add", "change")
        tech_sales_perms += perms_for(models.VisitReport, "view", "add", "change")
        tech_sales_perms += perms_for(models.Task, "view", "add", "change")
        tech_sales_perms += perms_for(models.Product, "view")
        tech_sales_perms += perms_for(models.ProductCategory, "view")
        tech_sales_perms += perms_for(models.Territory, "view")
        tech_sales_perms += perms_for(models.Outlet, "view")
        tech_sales_perms += perms_for(models.Forecast, "view")
        tech_sales_perms += perms_for(models.Promotion, "view")
        tech_sales_perms += perms_for(models.ApprovalRequest, "view")
        tech_sales_perms += perms_for(models.DataQualityIssue, "view")
        tech_sales_perms += perms_for(models.SlaEscalation, "view")
        technico_commerciaux.permissions.set(tech_sales_perms)

        # Experts metier : expertise par espece/stade/objectif/region + support.
        expert_perms = []
        expert_perms += perms_by_codename("view_dashboard", "view_reports")
        expert_perms += perms_for(models.InboundRequest, "view", "change")
        expert_perms += perms_for(models.Customer, "view")
        expert_perms += perms_for(models.Contact, "view")
        expert_perms += perms_for(models.Lead, "view", "change")
        expert_perms += perms_for(models.Opportunity, "view", "change")
        expert_perms += perms_for(models.Order, "view")
        expert_perms += perms_for(models.OrderItem, "view")
        expert_perms += perms_for(models.Invoice, "view")
        expert_perms += perms_for(models.InvoiceItem, "view")
        expert_perms += perms_for(models.SupportCase, "view", "add", "change")
        expert_perms += perms_for(models.VisitReport, "view", "add", "change")
        expert_perms += perms_for(models.Task, "view", "add", "change")
        expert_perms += perms_for(models.Product, "view")
        expert_perms += perms_for(models.ProductCategory, "view")
        expert_perms += perms_for(models.Territory, "view")
        expert_perms += perms_for(models.Outlet, "view")
        expert_perms += perms_for(models.Forecast, "view")
        expert_perms += perms_for(models.Promotion, "view")
        expert_perms += perms_for(models.DataQualityIssue, "view")
        expert_perms += perms_for(models.SlaEscalation, "view")
        experts_metier.permissions.set(expert_perms)

        # Technicien CRM & Support IT : exploitation quotidienne + support plateforme
        it_perms = []
        it_perms += perms_by_codename("view_dashboard")
        it_perms += perms_for(models.Customer, "view")
        it_perms += perms_for(models.Contact, "view")
        it_perms += perms_for(models.InboundRequest, "view", "change")
        it_perms += perms_for(models.Invoice, "view", "add", "change")
        it_perms += perms_for(models.InvoiceItem, "view", "add", "change")
        it_perms += perms_for(models.SupportCase, "view", "add", "change")
        it_perms += perms_for(models.VisitReport, "view", "add", "change")
        it_perms += perms_for(models.Task, "view", "add", "change")
        it_perms += perms_for(models.RoutingRule, "view", "add", "change")
        it_perms += perms_for(models.CareerApplication, "view", "change")
        it_perms += perms_for(models.NewsletterSubscription, "view", "change")
        it_perms += perms_for(models.DataQualityIssue, "view", "change")
        it_perms += perms_for(models.SlaEscalation, "view", "change")
        it_perms += perms_for(models.AuditTrail, "view")
        it_perms += perms_for(models.RoleAssignment, "view", "add", "change")
        it_perms += perms_for(models.UserSecurityProfile, "view", "change")
        it_perms += perms_for(models.EnterpriseConnector, "view", "add", "change")
        it_perms += perms_for(models.EnterpriseFieldMapping, "view", "add", "change")
        it_perms += perms_for(models.EnterpriseOutboxEvent, "view", "change")
        it_perms += perms_for(models.EnterpriseInboxEvent, "view", "change")
        it_perms += perms_for(models.EnterpriseDeadLetterEvent, "view")
        technicien_crm.permissions.set(it_perms)
        support.permissions.set(it_perms)

        # Caissière : exécution commandes/encaissement
        cashier_perms = []
        cashier_perms += perms_by_codename("view_dashboard")
        cashier_perms += perms_for(models.Customer, "view")
        cashier_perms += perms_for(models.Contact, "view")
        cashier_perms += perms_for(models.Product, "view")
        cashier_perms += perms_for(models.Outlet, "view")
        cashier_perms += perms_for(models.Order, "view", "add", "change")
        cashier_perms += perms_for(models.OrderItem, "view", "add", "change")
        cashier_perms += perms_for(models.Invoice, "view", "add", "change")
        cashier_perms += perms_for(models.InvoiceItem, "view", "add", "change")
        cashier_perms += perms_for(models.Task, "view", "add")
        cashier_perms += perms_for(models.ApprovalRequest, "view")
        caissiere.permissions.set(cashier_perms)

        # Comptable : visibilité financière et conformité
        accounting_perms = []
        accounting_perms += perms_by_codename("view_dashboard", "view_reports")
        accounting_perms += perms_for(models.Customer, "view")
        accounting_perms += perms_for(models.Outlet, "view")
        accounting_perms += perms_for(models.Order, "view", "change")
        accounting_perms += perms_for(models.OrderItem, "view")
        accounting_perms += perms_for(models.Invoice, "view", "change")
        accounting_perms += perms_for(models.InvoiceItem, "view")
        accounting_perms += perms_for(models.Opportunity, "view")
        accounting_perms += perms_for(models.Forecast, "view", "change")
        accounting_perms += perms_for(models.Promotion, "view")
        accounting_perms += perms_for(models.ApprovalRequest, "view", "change")
        accounting_perms += perms_for(models.AuditTrail, "view")
        accounting_perms += perms_for(models.EnterpriseOutboxEvent, "view")
        accounting_perms += perms_for(models.EnterpriseInboxEvent, "view")
        comptable.permissions.set(accounting_perms)

        # Gouvernance & conformité
        governance_perms = []
        governance_perms += perms_by_codename("view_dashboard", "view_reports")
        governance_perms += perms_for(models.ApprovalPolicy, "view", "add", "change")
        governance_perms += perms_for(models.ApprovalRequest, "view", "change")
        governance_perms += perms_for(models.Invoice, "view", "change")
        governance_perms += perms_for(models.InvoiceItem, "view")
        governance_perms += perms_for(models.DataQualityIssue, "view", "change")
        governance_perms += perms_for(models.SlaEscalation, "view", "change")
        governance_perms += perms_for(models.RoleAssignment, "view", "add", "change")
        governance_perms += perms_for(models.UserSecurityProfile, "view", "change")
        governance_perms += perms_for(models.AuditTrail, "view")
        governance_perms += perms_for(models.EnterpriseConnector, "view", "add", "change")
        governance_perms += perms_for(models.EnterpriseFieldMapping, "view", "add", "change")
        governance_perms += perms_for(models.EnterpriseOutboxEvent, "view", "change")
        governance_perms += perms_for(models.EnterpriseInboxEvent, "view", "change")
        governance_perms += perms_for(models.EnterpriseDeadLetterEvent, "view")
        gouvernance.permissions.set(governance_perms)

        models.ApprovalPolicy.objects.get_or_create(
            name="Corporate - Remise >= 8% ou Exception crédit",
            defaults={
                "active": True,
                "min_order_total": 250000,
                "min_discount_pct": 8,
                "require_credit_exception": True,
                "approver_group": directeur_commercial,
                "notes": "Politique par défaut alignée gouvernance-first.",
            },
        )

        for user in User.objects.all():
            models.UserSecurityProfile.objects.get_or_create(user=user)

        self.stdout.write(
            self.style.SUCCESS(
                "Groupes et permissions CRM configurés (Direction, Admin Système, Commercial, Technico-commercial, Experts, IT, Caissière, Comptable, Gouvernance)."
            )
        )
