"""Data models for the CRM core."""

from __future__ import annotations

import uuid
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone


REGION_CHOICES = [
    ("Abidjan", "Abidjan"),
    ("Bouaké", "Bouaké"),
    ("Yamoussoukro", "Yamoussoukro"),
    ("San-Pédro", "San-Pédro"),
    ("Korhogo", "Korhogo"),
    ("Daloa", "Daloa"),
    ("Man", "Man"),
    ("Gagnoa", "Gagnoa"),
    ("Autre", "Autre"),
]


class TimeStampedModel(models.Model):
    """Abstract base model with timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SpeciesChoices(models.TextChoices):
    VOLAILLES = "volailles", "Volailles"
    PORCINS = "porcins", "Porcs"
    POISSONS = "poissons", "Poissons"
    BIOSECURITE = "biosecurite", "Biosécurité"
    MULTI = "multi", "Multi-espèces"


class CustomerTypeChoices(models.TextChoices):
    ELEVEUR = "eleveur", "Éleveur"
    DISTRIBUTEUR = "distributeur", "Distributeur"
    INTEGRATEUR = "integrateur", "Intégrateur"
    VETERINAIRE = "veterinaire", "Vétérinaire"
    REVENDEUR = "revendeur", "Revendeur"
    INDUSTRIE = "industrie", "Industrie/Transformateur"
    AUTRE = "autre", "Autre"


class ChannelChoices(models.TextChoices):
    APPEL = "appel", "Appel"
    WHATSAPP = "whatsapp", "WhatsApp"
    EMAIL = "email", "E-mail"
    VISITE = "visite", "Visite terrain"
    SITE_WEB = "site", "Site web"
    REFERENT = "referent", "Référent/Partenaire"


class OutletChannelChoices(models.TextChoices):
    GROSSISTE = "grossiste", "Grossiste"
    DETAIL = "detail", "Détaillant"
    FERME = "ferme", "Ferme"
    INSTITUTION = "institution", "Institution"
    AUTRE = "autre", "Autre"


class LeadStatusChoices(models.TextChoices):
    NOUVEAU = "nouveau", "Nouveau"
    CONTACTE = "contacte", "Contacté"
    QUALIFIE = "qualifie", "Qualifié"
    PROPOSITION = "proposition", "Proposition"
    PERDU = "perdu", "Perdu"
    CONVERTI = "converti", "Converti"


class InboundStatusChoices(models.TextChoices):
    NOUVEAU = "nouveau", "Nouveau"
    A_QUALIFIER = "a_qualifier", "À qualifier"
    ASSIGNE = "assigne", "Assigné"
    CONVERTI = "converti", "Converti"
    CLOTURE = "cloture", "Clôturé"


class InboundKindChoices(models.TextChoices):
    LEAD = "lead", "Lead web"
    CONTACT = "contact", "Contact/Devis"
    PRODUCT = "product", "Produit"
    CAREER = "career", "Carrière"
    NEWSLETTER = "newsletter", "Newsletter"


class InboundPriorityChoices(models.TextChoices):
    FAIBLE = "faible", "Faible"
    NORMAL = "normal", "Normal"
    ELEVE = "eleve", "Élevé"
    URGENT = "urgent", "Urgent"


class CareerStatusChoices(models.TextChoices):
    RECU = "recu", "Reçu"
    ETUDE = "etude", "En étude"
    ENTRETIEN = "entretien", "Entretien"
    REFUSE = "refuse", "Refusé"
    RETENU = "retenu", "Retenu"


class NewsletterStatusChoices(models.TextChoices):
    ACTIF = "actif", "Actif"
    DESABONNE = "desabonne", "Désabonné"


class OpportunityStageChoices(models.TextChoices):
    DISCOVERY = "diagnostic", "Diagnostic"
    OFFRE = "offre", "Offre/Devis"
    NEGOCIATION = "negociation", "Négociation"
    GAGNE = "gagne", "Gagné"
    PERDU = "perdu", "Perdu"


class OrderStatusChoices(models.TextChoices):
    BROUILLON = "brouillon", "Brouillon"
    DEVIS = "devis", "Devis"
    CONFIRME = "confirme", "Confirmé"
    LIVRE = "livre", "Livré"
    ANNULE = "annule", "Annulé"


class InvoiceSourceChoices(models.TextChoices):
    EXPRESS = "express", "Vente express"
    ORDER = "order", "Depuis commande"


class InvoiceNatureChoices(models.TextChoices):
    STANDARD = "standard", "Facture"
    CREDIT_NOTE = "credit_note", "Avoir"


class InvoiceStatusChoices(models.TextChoices):
    BROUILLON = "brouillon", "Brouillon"
    EMISE = "emise", "Émise"
    PARTIELLEMENT_PAYEE = "partiellement_payee", "Partiellement payée"
    PAYEE = "payee", "Payée"
    ANNULEE = "annulee", "Annulée"


class InvoicePaymentMethodChoices(models.TextChoices):
    NON_RENSEIGNE = "non_renseigne", "Non renseigné"
    ESPECES = "especes", "Espèces"
    MOBILE_MONEY = "mobile_money", "Mobile Money"
    VIREMENT = "virement", "Virement"
    CHEQUE = "cheque", "Chèque"
    CREDIT = "credit", "Crédit"


class InvoicePaymentSourceChoices(models.TextChoices):
    MANUAL = "manual", "Saisie manuelle"
    INTEGRATION = "integration", "Flux integration"


class InvoiceFNEStatusChoices(models.TextChoices):
    NOT_SENT = "not_sent", "Non envoyé"
    PENDING = "pending", "En attente"
    CERTIFIED = "certified", "Certifiée"
    REJECTED = "rejected", "Rejetée"
    NOT_REQUIRED = "not_required", "Non requis"


class SupportStatusChoices(models.TextChoices):
    OUVERT = "ouvert", "Ouvert"
    EN_COURS = "en_cours", "En cours"
    EN_ATTENTE = "en_attente", "En attente client"
    CLOTURE = "cloture", "Clôturé"


class SupportTypeChoices(models.TextChoices):
    VISITE_TECHNIQUE = "visite_technique", "Visite technique"
    BIOSCURITE = "biosecurite", "Biosécurité"
    QUALITE = "qualite", "Réclamation qualité"
    FORMATION = "formation", "Formation"
    LOGISTIQUE = "logistique", "Logistique/Stock"


class PromotionStatusChoices(models.TextChoices):
    PLANIFIE = "planifie", "Planifié"
    ACTIF = "actif", "Actif"
    TERMINE = "termine", "Terminé"


class ForecastStatusChoices(models.TextChoices):
    BROUILLON = "brouillon", "Brouillon"
    CONFIRME = "confirme", "Confirmé"


class TaskStatusChoices(models.TextChoices):
    A_FAIRE = "a_faire", "À faire"
    EN_COURS = "en_cours", "En cours"
    TERMINE = "termine", "Terminé"


class TaskTypeChoices(models.TextChoices):
    APPEL = "appel", "Appel"
    VISITE = "visite", "Visite"
    EMAIL = "email", "E-mail"
    RELANCE = "relance", "Relance"
    DEVIS = "devis", "Devis"
    LIVRAISON = "livraison", "Livraison"
    FORMATION = "formation", "Formation"


class ApprovalStatusChoices(models.TextChoices):
    PENDING = "pending", "En attente"
    APPROVED = "approved", "Approuvé"
    REJECTED = "rejected", "Refusé"
    CANCELLED = "cancelled", "Annulé"


class ApprovalTypeChoices(models.TextChoices):
    DISCOUNT = "discount", "Remise"
    CREDIT = "credit", "Exception crédit"
    PRICING = "pricing", "Exception tarifaire"
    MANUAL = "manual", "Validation manuelle"


class DataQualitySeverityChoices(models.TextChoices):
    LOW = "low", "Faible"
    MEDIUM = "medium", "Moyenne"
    HIGH = "high", "Élevée"
    CRITICAL = "critical", "Critique"


class DataQualityStatusChoices(models.TextChoices):
    OPEN = "open", "Ouvert"
    IN_REVIEW = "in_review", "En revue"
    RESOLVED = "resolved", "Résolu"
    IGNORED = "ignored", "Ignoré"


class EscalationLevelChoices(models.TextChoices):
    LEVEL_1 = "l1", "Niveau 1"
    LEVEL_2 = "l2", "Niveau 2"
    LEVEL_3 = "l3", "Niveau 3"


class EscalationStatusChoices(models.TextChoices):
    OPEN = "open", "Ouvert"
    ACK = "ack", "Pris en charge"
    RESOLVED = "resolved", "Résolu"


class AuditEventChoices(models.TextChoices):
    CREATE = "create", "Création"
    UPDATE = "update", "Mise à jour"
    DELETE = "delete", "Suppression"
    STATUS_CHANGE = "status_change", "Changement de statut"
    APPROVAL = "approval", "Validation"
    SLA = "sla", "SLA/Escalade"


class AuditSourceChoices(models.TextChoices):
    UI = "ui", "Interface CRM"
    API = "api", "API"
    SYSTEM = "system", "Système"


class EnterpriseIntegrationTypeChoices(models.TextChoices):
    ERP_COMPTA = "erp_compta", "ERP/Compta"
    TELEPHONY_WHATSAPP = "telephony_whatsapp", "Telephony/WhatsApp"
    BI_ANALYTICS = "bi_analytics", "BI/Analytics"
    LOGISTICS_STOCK = "logistics_stock", "Logistique/Stock"
    FNE_DGI = "fne_dgi", "FNE/DGI"


class EnterpriseIntegrationDirectionChoices(models.TextChoices):
    OUTBOUND = "outbound", "Outbound"
    INBOUND = "inbound", "Inbound"
    BIDIRECTIONAL = "bidirectional", "Bidirectional"


class EnterpriseConnectorTransportChoices(models.TextChoices):
    MOCK = "mock", "Mock"
    HTTP = "http", "HTTP"


class EnterpriseConnectorAuthModeChoices(models.TextChoices):
    NONE = "none", "None"
    API_KEY = "api_key", "API Key"
    BEARER = "bearer", "Bearer"
    HMAC = "hmac", "HMAC"


class EnterpriseOutboxStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"
    DEAD = "dead", "Dead letter"


class EnterpriseInboxStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSED = "processed", "Processed"
    IGNORED = "ignored", "Ignored"
    FAILED = "failed", "Failed"
    DEAD = "dead", "Dead letter"


class EnterpriseDeadLetterDirectionChoices(models.TextChoices):
    OUTBOX = "outbox", "Outbox"
    INBOX = "inbox", "Inbox"


class RoleAssignmentTypeChoices(models.TextChoices):
    PERMANENT = "permanent", "Permanent"
    TEMPORARY = "temporary", "Temporaire"
    SCOPED = "scoped", "Par dossier/projet"


class RoleScopeChoices(models.TextChoices):
    GLOBAL = "global", "Global"
    SEGMENT = "segment", "Segment (espece)"
    STAGE = "stage", "Stade"
    OBJECTIVE = "objective", "Objectif"
    REGION = "region", "Region"
    CUSTOMER = "customer", "Client"
    OPPORTUNITY = "opportunity", "Opportunité"
    ORDER = "order", "Commande"
    SUPPORT = "support", "Support"
    INBOUND = "inbound", "Inbox"
    PROJECT = "project", "Projet"
    CUSTOM = "custom", "Autre"


def default_order_number() -> str:
    return f"CMD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def default_invoice_number() -> str:
    return f"FCT-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def default_support_ref() -> str:
    return f"SUP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


class Customer(TimeStampedModel):
    """Client ou prospect de Maridav CI."""

    name = models.CharField("Nom", max_length=255)
    code = models.CharField("Code client", max_length=32, unique=True)
    customer_type = models.CharField(
        "Type de client",
        max_length=32,
        choices=CustomerTypeChoices.choices,
        default=CustomerTypeChoices.ELEVEUR,
    )
    segment = models.CharField(
        "Espèce principale",
        max_length=24,
        choices=SpeciesChoices.choices,
        default=SpeciesChoices.VOLAILLES,
    )
    size = models.CharField("Taille/Capacité", max_length=120, blank=True)
    city = models.CharField("Ville", max_length=120, blank=True)
    region = models.CharField("Région", max_length=120, blank=True, choices=REGION_CHOICES)
    address = models.CharField("Adresse", max_length=255, blank=True)
    country = models.CharField(max_length=80, default="Côte d'Ivoire")
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=40, blank=True)
    email = models.EmailField("E-mail", blank=True)
    tax_ncc = models.CharField("NCC", max_length=64, blank=True)
    tax_ntd = models.CharField("NTD", max_length=64, blank=True)
    tax_rccm = models.CharField("RCCM", max_length=64, blank=True)
    tax_regime = models.CharField("Régime fiscal", max_length=120, blank=True)
    status = models.CharField(
        max_length=24,
        choices=[
            ("prospect", "Prospect"),
            ("actif", "Actif"),
            ("dormant", "Dormant"),
        ],
        default="prospect",
    )
    credit_limit = models.PositiveIntegerField(
        "Plafond de crédit (FCFA)",
        default=0,
        help_text="Montant maximum d'encours autorisé pour ce client. 0 = pas de crédit accordé.",
    )
    payment_terms_days = models.PositiveIntegerField(
        "Délai de paiement (jours)",
        default=0,
        help_text="Délai accordé pour régler une facture (ex. 30 jours). 0 = paiement comptant.",
    )
    credit_hold = models.BooleanField(
        "Compte bloqué (crédit)",
        default=False,
        help_text="Si coché, le client est signalé en blocage : ne plus livrer à crédit.",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        permissions = [
            ("view_dashboard", "Peut voir le tableau de bord CRM"),
            ("view_reports", "Peut consulter les rapports CRM"),
            ("manage_sales_team", "Peut gérer l'équipe commerciale"),
        ]

    def __str__(self) -> str:  # pragma: no cover - display
        return f"{self.name} ({self.get_customer_type_display()})"

    def get_absolute_url(self):
        return reverse("customers-detail", args=[self.pk])

    @property
    def outstanding_balance(self) -> int:
        """Encours = somme des soldes dus sur les factures émises non soldées."""
        agg = self.invoices.filter(
            status__in=[
                InvoiceStatusChoices.EMISE,
                InvoiceStatusChoices.PARTIELLEMENT_PAYEE,
            ]
        ).aggregate(
            total=models.Sum("total_amount"),
            paid=models.Sum("paid_amount"),
        )
        total = agg["total"] or 0
        paid = agg["paid"] or 0
        return max(0, int(total) - int(paid))

    @property
    def available_credit(self) -> int:
        """Crédit encore disponible avant d'atteindre le plafond (peut être négatif)."""
        return int(self.credit_limit or 0) - self.outstanding_balance

    @property
    def is_over_credit_limit(self) -> bool:
        if not self.credit_limit:
            return self.outstanding_balance > 0 if self.credit_hold else False
        return self.outstanding_balance > self.credit_limit


class Territory(TimeStampedModel):
    name = models.CharField("Territoire", max_length=120)
    region = models.CharField("Région", max_length=120, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Responsable",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="territories",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - display
        return self.name


class Outlet(TimeStampedModel):
    name = models.CharField("Point de vente", max_length=255)
    territory = models.ForeignKey(
        Territory,
        verbose_name="Territoire",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outlets",
    )
    distributor = models.ForeignKey(
        Customer,
        verbose_name="Distributeur",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outlets",
    )
    channel = models.CharField(
        "Canal",
        max_length=24,
        choices=OutletChannelChoices.choices,
        default=OutletChannelChoices.DETAIL,
    )
    city = models.CharField("Ville", max_length=120, blank=True)
    region = models.CharField("Région", max_length=120, blank=True)
    address = models.CharField("Adresse", max_length=255, blank=True)
    gps_lat = models.DecimalField("Latitude", max_digits=9, decimal_places=6, null=True, blank=True)
    gps_lng = models.DecimalField("Longitude", max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(
        "Statut",
        max_length=16,
        choices=[("actif", "Actif"), ("inactif", "Inactif")],
        default="actif",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - display
        return self.name


class Contact(TimeStampedModel):
    customer = models.ForeignKey(Customer, verbose_name="Client", related_name="contacts", on_delete=models.CASCADE)
    first_name = models.CharField("Prénom", max_length=120)
    last_name = models.CharField("Nom", max_length=120, blank=True)
    role = models.CharField("Fonction", max_length=120, blank=True)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=40, blank=True)
    email = models.EmailField("E-mail", blank=True)
    preferred_channel = models.CharField(
        "Canal préféré",
        max_length=24,
        choices=ChannelChoices.choices,
        default=ChannelChoices.WHATSAPP,
    )
    is_primary = models.BooleanField("Contact principal", default=False)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:  # pragma: no cover - display
        return f"{self.first_name} {self.last_name}".strip()


class Lead(TimeStampedModel):
    name = models.CharField("Nom du contact", max_length=255)
    company = models.CharField("Structure", max_length=255, blank=True)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    email = models.EmailField("E-mail", blank=True)
    lead_score = models.PositiveIntegerField("Score", default=0)
    channel = models.CharField("Canal", max_length=24, choices=ChannelChoices.choices, default=ChannelChoices.SITE_WEB)
    preferred_channel = models.CharField(
        "Canal préféré",
        max_length=24,
        choices=ChannelChoices.choices,
        blank=True,
    )
    segment = models.CharField("Espèce", max_length=24, choices=SpeciesChoices.choices, default=SpeciesChoices.VOLAILLES)
    stage = models.CharField("Stade/Objectif", max_length=120, blank=True)
    need_type = models.CharField(
        "Besoin", max_length=32, choices=[
            ("aliments", "Aliments complets"),
            ("additifs", "Additifs/Correcteurs"),
            ("biosecurite", "Biosécurité"),
            ("formation", "Formation/Atelier"),
            ("logistique", "Logistique/Disponibilité"),
        ], default="aliments"
    )
    expected_volume = models.CharField("Volume/Capacité", max_length=120, blank=True)
    product_interest = models.CharField("Produit/Gamme", max_length=255, blank=True)
    objective = models.CharField("Objectif", max_length=255, blank=True)
    interests = models.JSONField("Intérêts", default=list, blank=True)
    region = models.CharField("Région/Ville", max_length=120, blank=True)
    status = models.CharField(max_length=24, choices=LeadStatusChoices.choices, default=LeadStatusChoices.NOUVEAU)
    source_page = models.URLField("Page source", blank=True)
    referrer = models.URLField("Référent", blank=True)
    utm_source = models.CharField("UTM source", max_length=120, blank=True)
    utm_medium = models.CharField("UTM medium", max_length=120, blank=True)
    utm_campaign = models.CharField("UTM campaign", max_length=120, blank=True)
    utm_content = models.CharField("UTM content", max_length=120, blank=True)
    utm_term = models.CharField("UTM term", max_length=120, blank=True)
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("User agent", max_length=255, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Assigné à",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    next_step_date = models.DateField("Prochaine action", null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]


class InboundRequest(TimeStampedModel):
    kind = models.CharField("Type", max_length=24, choices=InboundKindChoices.choices)
    status = models.CharField(
        "Statut",
        max_length=24,
        choices=InboundStatusChoices.choices,
        default=InboundStatusChoices.NOUVEAU,
    )
    priority = models.CharField(
        "Priorité",
        max_length=16,
        choices=InboundPriorityChoices.choices,
        default=InboundPriorityChoices.NORMAL,
    )
    name = models.CharField("Nom", max_length=255, blank=True)
    company = models.CharField("Structure", max_length=255, blank=True)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    email = models.EmailField("E-mail", blank=True)
    segment = models.CharField("Espèce", max_length=24, choices=SpeciesChoices.choices, blank=True)
    stage = models.CharField("Stade/Objectif", max_length=120, blank=True)
    intent = models.CharField("Intention", max_length=120, blank=True)
    channel_preference = models.CharField(
        "Canal préféré",
        max_length=24,
        choices=ChannelChoices.choices,
        blank=True,
    )
    volume = models.CharField("Volume/Capacité", max_length=120, blank=True)
    product = models.CharField("Produit/Gamme", max_length=255, blank=True)
    objective = models.CharField("Objectif", max_length=255, blank=True)
    message = models.TextField("Message", blank=True)
    region = models.CharField("Région/Ville", max_length=120, blank=True)
    preferred_time = models.CharField("Créneau préféré", max_length=120, blank=True)
    interests = models.JSONField("Intérêts", default=list, blank=True)
    consent = models.BooleanField("Consentement", default=False)
    source_page = models.URLField("Page source", blank=True)
    referrer = models.URLField("Référent", blank=True)
    utm_source = models.CharField("UTM source", max_length=120, blank=True)
    utm_medium = models.CharField("UTM medium", max_length=120, blank=True)
    utm_campaign = models.CharField("UTM campaign", max_length=120, blank=True)
    utm_content = models.CharField("UTM content", max_length=120, blank=True)
    utm_term = models.CharField("UTM term", max_length=120, blank=True)
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("User agent", max_length=255, blank=True)
    raw_data = models.JSONField("Données brutes", default=dict, blank=True)
    first_response_due_at = models.DateTimeField("SLA première réponse", null=True, blank=True)
    resolution_due_at = models.DateTimeField("SLA résolution", null=True, blank=True)
    first_response_at = models.DateTimeField("Première réponse", null=True, blank=True)
    resolved_at = models.DateTimeField("Résolu le", null=True, blank=True)
    lead = models.ForeignKey(
        "Lead",
        related_name="inbound_requests",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Assigné à",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inbound_requests",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display
        return f"{self.get_kind_display()} - {self.name or self.email or self.phone}"


class RoutingRule(TimeStampedModel):
    name = models.CharField("Nom", max_length=120)
    kind = models.CharField(
        "Type de demande",
        max_length=24,
        choices=InboundKindChoices.choices,
        blank=True,
    )
    segment = models.CharField(
        "Segment",
        max_length=24,
        choices=SpeciesChoices.choices,
        blank=True,
    )
    region = models.CharField("Région/Ville", max_length=120, blank=True)
    channel_preference = models.CharField(
        "Canal",
        max_length=24,
        choices=ChannelChoices.choices,
        blank=True,
    )
    priority = models.PositiveIntegerField("Priorité", default=100)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Assigné à",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routing_rules",
    )
    active = models.BooleanField("Actif", default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["priority", "name"]

    def __str__(self) -> str:  # pragma: no cover - display
        return self.name


class CareerApplication(TimeStampedModel):
    inbound_request = models.OneToOneField(
        InboundRequest,
        related_name="career_application",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    full_name = models.CharField("Nom & prénom", max_length=255)
    email = models.EmailField("E-mail")
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    role = models.CharField("Poste visé", max_length=120, blank=True)
    experience = models.CharField("Expérience", max_length=120, blank=True)
    location = models.CharField("Ville de résidence", max_length=120, blank=True)
    availability = models.CharField("Disponibilité", max_length=120, blank=True)
    mobility = models.CharField("Mobilité", max_length=120, blank=True)
    message = models.TextField("Motivations", blank=True)
    specialites = models.JSONField("Spécialités", default=list, blank=True)
    cv = models.FileField("CV", upload_to="careers/", null=True, blank=True)
    consent = models.BooleanField("Consentement", default=False)
    status = models.CharField(
        "Statut",
        max_length=24,
        choices=CareerStatusChoices.choices,
        default=CareerStatusChoices.RECU,
    )
    source_page = models.URLField("Page source", blank=True)
    referrer = models.URLField("Référent", blank=True)
    utm_source = models.CharField("UTM source", max_length=120, blank=True)
    utm_medium = models.CharField("UTM medium", max_length=120, blank=True)
    utm_campaign = models.CharField("UTM campaign", max_length=120, blank=True)
    utm_content = models.CharField("UTM content", max_length=120, blank=True)
    utm_term = models.CharField("UTM term", max_length=120, blank=True)
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("User agent", max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display
        return self.full_name


class NewsletterSubscription(TimeStampedModel):
    inbound_request = models.OneToOneField(
        InboundRequest,
        related_name="newsletter_subscription",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    email = models.EmailField("E-mail", unique=True)
    status = models.CharField(
        "Statut",
        max_length=24,
        choices=NewsletterStatusChoices.choices,
        default=NewsletterStatusChoices.ACTIF,
    )
    source_page = models.URLField("Page source", blank=True)
    referrer = models.URLField("Référent", blank=True)
    utm_source = models.CharField("UTM source", max_length=120, blank=True)
    utm_medium = models.CharField("UTM medium", max_length=120, blank=True)
    utm_campaign = models.CharField("UTM campaign", max_length=120, blank=True)
    utm_content = models.CharField("UTM content", max_length=120, blank=True)
    utm_term = models.CharField("UTM term", max_length=120, blank=True)
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("User agent", max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display
        return self.email


class ProductCategory(TimeStampedModel):
    name = models.CharField("Nom", max_length=120)
    slug = models.SlugField("Code URL", unique=True)
    segment = models.CharField("Espèce", max_length=24, choices=SpeciesChoices.choices, default=SpeciesChoices.MULTI)
    description = models.TextField("Description", blank=True)

    class Meta:
        verbose_name_plural = "Catégories"
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(ProductCategory, verbose_name="Catégorie", on_delete=models.CASCADE, related_name="products")
    name = models.CharField("Nom", max_length=255)
    sku = models.CharField("Référence", max_length=64, unique=True)
    packaging = models.CharField("Conditionnement", max_length=120, blank=True)
    unit_price = models.PositiveIntegerField("Prix de vente de référence (FCFA)", default=0)
    cost_price = models.PositiveIntegerField(
        "Coût de revient (FCFA)",
        default=0,
        help_text="Coût d'achat/production unitaire. Sert au calcul de la marge.",
    )
    min_stock_alert = models.PositiveIntegerField(
        "Seuil d'alerte stock",
        default=0,
        help_text="En dessous de ce stock disponible, le produit est signalé en rupture/alerte. 0 = pas d'alerte.",
    )
    status = models.CharField(
        "Statut",
        max_length=24,
        choices=[("actif", "Actif"), ("archive", "Archivé")],
        default="actif",
    )
    usage_notes = models.TextField("Notes d'usage", blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.sku})"

    @property
    def stock_on_hand(self) -> Decimal:
        """Stock physique disponible, agrégé sur tous les lots disponibles/réservés."""
        agg = self.lots.filter(
            status__in=[StockLotStatusChoices.DISPONIBLE, StockLotStatusChoices.RESERVE]
        ).aggregate(total=models.Sum("quantity_on_hand"))
        return agg["total"] or Decimal("0")

    @property
    def is_stock_low(self) -> bool:
        if not self.min_stock_alert:
            return False
        return self.stock_on_hand < self.min_stock_alert

    @property
    def margin_amount(self) -> int:
        """Marge unitaire = prix de référence − coût de revient."""
        return int(self.unit_price or 0) - int(self.cost_price or 0)

    @property
    def margin_pct(self):
        """Taux de marge sur le prix de vente (%). None si prix nul."""
        if not self.unit_price:
            return None
        return round(self.margin_amount / int(self.unit_price) * 100, 1)

    def price_for(self, customer_type: str | None) -> int:
        """Prix applicable à un type de client : tarif dédié s'il existe, sinon référence."""
        if customer_type:
            tier = self.segment_prices.filter(customer_type=customer_type).first()
            if tier:
                return int(tier.unit_price)
        return int(self.unit_price or 0)


class Opportunity(TimeStampedModel):
    title = models.CharField("Titre", max_length=255)
    customer = models.ForeignKey(Customer, verbose_name="Client", on_delete=models.CASCADE, related_name="opportunities")
    lead = models.ForeignKey(Lead, verbose_name="Lead", null=True, blank=True, on_delete=models.SET_NULL, related_name="opportunities")
    stage = models.CharField("Étape", max_length=24, choices=OpportunityStageChoices.choices, default=OpportunityStageChoices.DISCOVERY)
    expected_value = models.PositiveIntegerField("Valeur attendue (FCFA)", default=0)
    probability = models.PositiveIntegerField("Probabilité (%)", default=30)
    expected_close_date = models.DateField("Date de clôture", null=True, blank=True)
    segment = models.CharField("Espèce", max_length=24, choices=SpeciesChoices.choices, default=SpeciesChoices.VOLAILLES)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Assigné à",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )
    notes = models.TextField("Notes", blank=True)

    class Meta:
        ordering = ["expected_close_date", "title"]

    def __str__(self) -> str:  # pragma: no cover
        return self.title

    def get_absolute_url(self):
        return reverse("opportunities-list")


class Order(TimeStampedModel):
    order_number = models.CharField("Numéro de commande", max_length=32, unique=True, default=default_order_number)
    customer = models.ForeignKey(Customer, verbose_name="Client", on_delete=models.CASCADE, related_name="orders")
    outlet = models.ForeignKey(
        Outlet,
        verbose_name="Point de vente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    status = models.CharField("Statut", max_length=16, choices=OrderStatusChoices.choices, default=OrderStatusChoices.BROUILLON)
    delivery_date = models.DateField("Date de livraison", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Créé par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    billing_contact = models.CharField("Contact facturation", max_length=255, blank=True)
    discount_pct = models.DecimalField("Remise (%)", max_digits=5, decimal_places=2, default=0)
    credit_exception_requested = models.BooleanField("Exception crédit", default=False)
    notes = models.TextField("Notes", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return self.order_number

    @property
    def total_amount(self) -> float:
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name="Commande", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, verbose_name="Produit", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField("Quantité", default=1)
    unit_price = models.PositiveIntegerField("Prix unitaire (FCFA)", default=0)

    class Meta:
        verbose_name = "Ligne de commande"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.product} x {self.quantity}"

    @property
    def total_price(self) -> float:
        return int(self.quantity) * int(self.unit_price)


class Invoice(TimeStampedModel):
    invoice_number = models.CharField("Numéro de facture", max_length=32, unique=True, default=default_invoice_number)
    source = models.CharField("Source", max_length=16, choices=InvoiceSourceChoices.choices, default=InvoiceSourceChoices.EXPRESS)
    nature = models.CharField(
        "Nature",
        max_length=16,
        choices=InvoiceNatureChoices.choices,
        default=InvoiceNatureChoices.STANDARD,
    )
    customer = models.ForeignKey(Customer, verbose_name="Client", on_delete=models.CASCADE, related_name="invoices")
    order = models.ForeignKey(
        Order,
        verbose_name="Commande source",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    original_invoice = models.ForeignKey(
        "self",
        verbose_name="Facture d'origine",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="credit_notes",
    )
    status = models.CharField("Statut", max_length=24, choices=InvoiceStatusChoices.choices, default=InvoiceStatusChoices.BROUILLON)
    due_date = models.DateField("Date d'échéance", null=True, blank=True)
    issued_at = models.DateTimeField("Émise le", null=True, blank=True)
    currency = models.CharField("Devise", max_length=8, default="FCFA")
    subtotal_amount = models.PositiveIntegerField("Sous-total (FCFA)", default=0)
    discount_amount = models.PositiveIntegerField("Remise totale (FCFA)", default=0)
    tax_amount = models.PositiveIntegerField("Taxes (FCFA)", default=0)
    total_amount = models.PositiveIntegerField("Total TTC (FCFA)", default=0)
    paid_amount = models.PositiveIntegerField("Montant payé (FCFA)", default=0)
    payment_method = models.CharField(
        "Mode de paiement",
        max_length=24,
        choices=InvoicePaymentMethodChoices.choices,
        default=InvoicePaymentMethodChoices.NON_RENSEIGNE,
    )
    payment_reference = models.CharField("Référence paiement", max_length=255, blank=True)
    sales_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Commercial responsable",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_invoices",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Créé par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invoices",
    )
    notes = models.TextField("Notes", blank=True)
    cancellation_reason = models.TextField("Motif d'avoir/annulation", blank=True)
    fne_required = models.BooleanField("Certification FNE requise", default=True)
    fne_status = models.CharField(
        "Statut FNE",
        max_length=24,
        choices=InvoiceFNEStatusChoices.choices,
        default=InvoiceFNEStatusChoices.NOT_SENT,
    )
    fne_reference = models.CharField("Référence FNE", max_length=255, blank=True)
    fne_certified_at = models.DateTimeField("Certifiée FNE le", null=True, blank=True)
    fne_last_error = models.TextField("Dernière erreur FNE", blank=True)
    fne_payload = models.JSONField("Payload FNE", default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["fne_status", "created_at"]),
            models.Index(fields=["nature", "created_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.invoice_number

    @property
    def balance_due(self) -> int:
        return max(0, int(self.total_amount or 0) - int(self.paid_amount or 0))


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, verbose_name="Facture", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, verbose_name="Produit", on_delete=models.PROTECT)
    description = models.CharField("Description", max_length=255, blank=True)
    quantity = models.PositiveIntegerField("Quantité", default=1)
    unit_price = models.PositiveIntegerField("Prix unitaire (FCFA)", default=0)
    discount_pct = models.DecimalField("Remise (%)", max_digits=5, decimal_places=2, default=0)
    tax_rate_pct = models.DecimalField("Taxe (%)", max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Ligne de facture"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.invoice.invoice_number} - {self.product} x {self.quantity}"

    @property
    def subtotal_amount(self) -> int:
        return int(self.quantity or 0) * int(self.unit_price or 0)

    @property
    def discount_amount(self) -> int:
        return int((Decimal(self.subtotal_amount) * Decimal(self.discount_pct or 0)) / Decimal("100"))

    @property
    def taxable_amount(self) -> int:
        return max(0, int(self.subtotal_amount) - int(self.discount_amount))

    @property
    def tax_amount(self) -> int:
        return int((Decimal(self.taxable_amount) * Decimal(self.tax_rate_pct or 0)) / Decimal("100"))

    @property
    def total_amount(self) -> int:
        return int(self.taxable_amount) + int(self.tax_amount)


class InvoicePayment(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, verbose_name="Facture", on_delete=models.CASCADE, related_name="payments")
    amount = models.PositiveIntegerField("Montant payé (FCFA)")
    payment_method = models.CharField(
        "Mode de paiement",
        max_length=24,
        choices=InvoicePaymentMethodChoices.choices,
        default=InvoicePaymentMethodChoices.NON_RENSEIGNE,
    )
    payment_reference = models.CharField("Référence paiement", max_length=255, blank=True)
    paid_at = models.DateTimeField("Payé le", default=timezone.now)
    source = models.CharField(
        "Source",
        max_length=16,
        choices=InvoicePaymentSourceChoices.choices,
        default=InvoicePaymentSourceChoices.MANUAL,
    )
    source_connector = models.CharField("Code connecteur source", max_length=64, blank=True)
    source_event_id = models.CharField("ID événement source", max_length=180, null=True, blank=True)
    notes = models.TextField("Notes", blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Enregistré par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_invoice_payments",
    )

    class Meta:
        ordering = ["-paid_at", "-created_at"]
        indexes = [
            models.Index(fields=["invoice", "paid_at"]),
            models.Index(fields=["source", "source_connector", "source_event_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.invoice.invoice_number} - {self.amount} FCFA"


class SupportCase(TimeStampedModel):
    reference = models.CharField("Référence", max_length=32, default=default_support_ref, unique=True)
    customer = models.ForeignKey(Customer, verbose_name="Client", on_delete=models.CASCADE, related_name="support_cases")
    contact = models.ForeignKey(Contact, verbose_name="Contact", null=True, blank=True, on_delete=models.SET_NULL, related_name="support_cases")
    case_type = models.CharField("Type de ticket", max_length=24, choices=SupportTypeChoices.choices, default=SupportTypeChoices.VISITE_TECHNIQUE)
    status = models.CharField("Statut", max_length=24, choices=SupportStatusChoices.choices, default=SupportStatusChoices.OUVERT)
    priority = models.CharField(
        "Priorité",
        max_length=16,
        choices=[("basse", "Basse"), ("normale", "Normale"), ("haute", "Haute")],
        default="normale",
    )
    species = models.CharField("Espèce", max_length=24, choices=SpeciesChoices.choices, default=SpeciesChoices.VOLAILLES)
    description = models.TextField("Description")
    channel = models.CharField("Canal", max_length=24, choices=ChannelChoices.choices, default=ChannelChoices.WHATSAPP)
    due_date = models.DateField("Échéance", null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Assigné à",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_cases",
    )
    resolution = models.TextField("Résolution", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return self.reference


class VisitReport(TimeStampedModel):
    customer = models.ForeignKey(Customer, verbose_name="Client", on_delete=models.CASCADE, related_name="visits")
    outlet = models.ForeignKey(
        Outlet,
        verbose_name="Point de vente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visits",
    )
    contact = models.ForeignKey(Contact, verbose_name="Contact", null=True, blank=True, on_delete=models.SET_NULL, related_name="visits")
    visit_date = models.DateField("Date de visite", default=timezone.now)
    species = models.CharField("Espèce", max_length=24, choices=SpeciesChoices.choices, default=SpeciesChoices.VOLAILLES)
    purpose = models.CharField(
        "Objet",
        max_length=32,
        choices=[
            ("diagnostic", "Diagnostic"),
            ("suivi", "Suivi technique"),
            ("formation", "Formation"),
            ("audit", "Audit biosécurité"),
        ],
        default="diagnostic",
    )
    observations = models.TextField("Observations")
    actions = models.TextField("Actions")
    follow_up_date = models.DateField("Date de suivi", null=True, blank=True)
    biosecurity_score = models.PositiveIntegerField("Score biosécurité", default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Rédigé par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visit_reports",
    )

    class Meta:
        ordering = ["-visit_date"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Visite {self.customer} ({self.visit_date})"


class Task(TimeStampedModel):
    title = models.CharField("Titre", max_length=255)
    description = models.TextField("Description", blank=True)
    due_date = models.DateField("Échéance", null=True, blank=True)
    status = models.CharField("Statut", max_length=24, choices=TaskStatusChoices.choices, default=TaskStatusChoices.A_FAIRE)
    activity_type = models.CharField("Type d'activité", max_length=24, choices=TaskTypeChoices.choices, default=TaskTypeChoices.APPEL)
    customer = models.ForeignKey(Customer, verbose_name="Client", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    lead = models.ForeignKey(Lead, verbose_name="Lead", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    opportunity = models.ForeignKey(
        Opportunity, verbose_name="Opportunité", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks"
    )
    support_case = models.ForeignKey(
        SupportCase, verbose_name="Ticket support", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks"
    )
    order = models.ForeignKey(Order, verbose_name="Commande", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Assigné à", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks"
    )

    class Meta:
        ordering = ["status", "due_date"]

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Promotion(TimeStampedModel):
    name = models.CharField("Promotion", max_length=255)
    product = models.ForeignKey(Product, verbose_name="Produit", on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField("Date début", default=timezone.now)
    end_date = models.DateField("Date fin", null=True, blank=True)
    budget = models.PositiveIntegerField("Budget (FCFA)", default=0)
    status = models.CharField(
        "Statut",
        max_length=16,
        choices=PromotionStatusChoices.choices,
        default=PromotionStatusChoices.PLANIFIE,
    )
    outlets = models.ManyToManyField(Outlet, blank=True, related_name="promotions")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date", "name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Forecast(TimeStampedModel):
    customer = models.ForeignKey(Customer, verbose_name="Client", on_delete=models.CASCADE, related_name="forecasts")
    outlet = models.ForeignKey(
        Outlet,
        verbose_name="Point de vente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forecasts",
    )
    product = models.ForeignKey(Product, verbose_name="Produit", on_delete=models.CASCADE, related_name="forecasts")
    period = models.DateField("Période", default=timezone.now)
    expected_quantity = models.PositiveIntegerField("Quantité prévue", default=0)
    status = models.CharField(
        "Statut",
        max_length=16,
        choices=ForecastStatusChoices.choices,
        default=ForecastStatusChoices.BROUILLON,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-period"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.customer} - {self.product} ({self.period})"


class ApprovalPolicy(TimeStampedModel):
    name = models.CharField("Nom de la politique", max_length=120, unique=True)
    active = models.BooleanField("Active", default=True)
    min_order_total = models.PositiveIntegerField("Montant minimal commande (FCFA)", default=0)
    min_discount_pct = models.DecimalField("Seuil remise (%)", max_digits=5, decimal_places=2, default=0)
    require_credit_exception = models.BooleanField("Exception crédit requise", default=False)
    approver_group = models.ForeignKey(
        Group,
        verbose_name="Groupe approbateur",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_policies",
    )
    default_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Approbateur par défaut",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_approval_policies",
    )
    notes = models.TextField("Notes", blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    def applies_to_order(self, order_total: int, discount_pct: float, credit_exception_requested: bool) -> bool:
        if not self.active:
            return False
        if order_total < int(self.min_order_total or 0):
            return False
        if float(discount_pct or 0) >= float(self.min_discount_pct or 0):
            return True
        return bool(self.require_credit_exception and credit_exception_requested)


class ApprovalRequest(TimeStampedModel):
    entity_type = models.CharField(
        "Entité",
        max_length=24,
        choices=[
            ("order", "Commande"),
            ("opportunity", "Opportunité"),
            ("support", "Ticket support"),
            ("custom", "Autre"),
        ],
        default="order",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="approval_requests")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    request_type = models.CharField(
        "Type de demande",
        max_length=24,
        choices=ApprovalTypeChoices.choices,
        default=ApprovalTypeChoices.MANUAL,
    )
    status = models.CharField(
        "Statut",
        max_length=24,
        choices=ApprovalStatusChoices.choices,
        default=ApprovalStatusChoices.PENDING,
    )
    reason = models.TextField("Motif", blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Demandé par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_requests_created",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Assigné à",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_requests_assigned",
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Décidé par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_requests_decided",
    )
    amount_fcfa = models.PositiveIntegerField("Montant (FCFA)", default=0)
    discount_pct = models.DecimalField("Remise (%)", max_digits=5, decimal_places=2, default=0)
    decision_note = models.TextField("Commentaire décision", blank=True)
    requested_at = models.DateTimeField("Demandé le", auto_now_add=True)
    decided_at = models.DateTimeField("Décidé le", null=True, blank=True)
    metadata = models.JSONField("Métadonnées", default=dict, blank=True)

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["entity_type", "status"]),
            models.Index(fields=["requested_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_entity_type_display()} #{self.object_id} - {self.get_status_display()}"


class DataQualityIssue(TimeStampedModel):
    source = models.CharField(
        "Source",
        max_length=24,
        choices=[
            ("inbound", "Inbox"),
            ("lead", "Lead"),
            ("customer", "Client"),
            ("contact", "Contact"),
            ("invoice", "Facture"),
            ("career", "Carrière"),
            ("newsletter", "Newsletter"),
        ],
        default="inbound",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="data_quality_issues")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    issue_type = models.CharField(
        "Type d'anomalie",
        max_length=40,
        choices=[
            ("missing_required", "Champ requis manquant"),
            ("duplicate_potential", "Doublon potentiel"),
            ("invalid_format", "Format invalide"),
            ("inconsistent_data", "Donnée incohérente"),
            ("consent_missing", "Consentement manquant"),
        ],
        default="missing_required",
    )
    severity = models.CharField(
        "Sévérité",
        max_length=16,
        choices=DataQualitySeverityChoices.choices,
        default=DataQualitySeverityChoices.MEDIUM,
    )
    status = models.CharField(
        "Statut",
        max_length=16,
        choices=DataQualityStatusChoices.choices,
        default=DataQualityStatusChoices.OPEN,
    )
    fingerprint = models.CharField("Empreinte", max_length=255, blank=True, db_index=True)
    message = models.TextField("Description")
    suggested_action = models.TextField("Action suggérée", blank=True)
    matched_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="data_quality_matches",
    )
    matched_object_id = models.PositiveIntegerField(null=True, blank=True)
    matched_object = GenericForeignKey("matched_content_type", "matched_object_id")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Assigné à",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="data_quality_issues_assigned",
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Résolu par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="data_quality_issues_resolved",
    )
    resolved_at = models.DateTimeField("Résolu le", null=True, blank=True)
    metadata = models.JSONField("Métadonnées", default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "severity"]),
            models.Index(fields=["source", "issue_type"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_source_display()} - {self.get_issue_type_display()}"


class SlaEscalation(TimeStampedModel):
    source_type = models.CharField(
        "Source SLA",
        max_length=24,
        choices=[("inbound", "Inbox"), ("support", "Support"), ("task", "Tâche")],
        default="inbound",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="sla_escalations")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    escalation_level = models.CharField(
        "Niveau",
        max_length=8,
        choices=EscalationLevelChoices.choices,
        default=EscalationLevelChoices.LEVEL_1,
    )
    status = models.CharField(
        "Statut",
        max_length=16,
        choices=EscalationStatusChoices.choices,
        default=EscalationStatusChoices.OPEN,
    )
    due_at = models.DateTimeField("Échéance SLA")
    escalated_at = models.DateTimeField("Escaladé le", auto_now_add=True)
    resolved_at = models.DateTimeField("Résolu le", null=True, blank=True)
    reason = models.CharField("Motif", max_length=255)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Assigné à",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sla_escalations",
    )
    notified_group = models.ForeignKey(
        Group,
        verbose_name="Groupe notifié",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sla_escalations",
    )
    metadata = models.JSONField("Métadonnées", default=dict, blank=True)

    class Meta:
        ordering = ["-escalated_at"]
        indexes = [
            models.Index(fields=["status", "source_type", "escalation_level"]),
            models.Index(fields=["due_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_source_type_display()} - {self.get_escalation_level_display()}"


class AuditTrail(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.CharField("Événement", max_length=24, choices=AuditEventChoices.choices)
    source = models.CharField("Source", max_length=16, choices=AuditSourceChoices.choices, default=AuditSourceChoices.SYSTEM)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="audit_trails")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    object_repr = models.CharField("Objet", max_length=255, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Acteur",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    actor_display = models.CharField("Acteur (texte)", max_length=120, blank=True)
    request_id = models.CharField("Request ID", max_length=64, blank=True)
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("User agent", max_length=255, blank=True)
    message = models.TextField("Message", blank=True)
    changed_fields = models.JSONField("Champs modifiés", default=list, blank=True)
    before_state = models.JSONField("Avant", default=dict, blank=True)
    after_state = models.JSONField("Après", default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["event", "source"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_event_display()} {self.content_type}#{self.object_id}"


class UserSecurityProfile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="security_profile")
    public_uuid = models.UUIDField("UUID public", default=uuid.uuid4, unique=True, editable=False)
    mfa_required = models.BooleanField("MFA requis", default=False)
    force_password_reset = models.BooleanField("Forcer changement mot de passe", default=False)
    is_locked = models.BooleanField("Compte verrouillé", default=False)
    failed_login_count = models.PositiveSmallIntegerField("Échecs de connexion", default=0)
    last_password_rotation_at = models.DateTimeField("Dernière rotation mot de passe", default=timezone.now)
    last_login_ip = models.GenericIPAddressField("Dernière IP", null=True, blank=True)
    trusted_devices = models.JSONField("Terminaux de confiance", default=list, blank=True)
    notes = models.TextField("Notes sécurité", blank=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user.username} [{self.public_uuid}]"

    @property
    def short_uuid(self) -> str:
        return str(self.public_uuid).split("-")[0]


class RoleAssignment(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Utilisateur",
        on_delete=models.CASCADE,
        related_name="role_assignments",
    )
    group = models.ForeignKey(Group, verbose_name="Rôle/Groupe", on_delete=models.CASCADE, related_name="role_assignments")
    assignment_type = models.CharField(
        "Type d'assignation",
        max_length=16,
        choices=RoleAssignmentTypeChoices.choices,
        default=RoleAssignmentTypeChoices.PERMANENT,
    )
    scope = models.CharField(
        "Portée",
        max_length=24,
        choices=RoleScopeChoices.choices,
        default=RoleScopeChoices.GLOBAL,
    )
    scope_reference = models.CharField("Référence dossier/projet", max_length=255, blank=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_assignments",
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    valid_from = models.DateTimeField("Valide à partir de", default=timezone.now)
    valid_to = models.DateTimeField("Valide jusqu'au", null=True, blank=True)
    is_active = models.BooleanField("Actif", default=True)
    reason = models.TextField("Motif", blank=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Accordé par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_assignments_granted",
    )
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Révoqué par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_assignments_revoked",
    )
    revoked_at = models.DateTimeField("Révoqué le", null=True, blank=True)
    metadata = models.JSONField("Métadonnées", default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active", "scope"]),
            models.Index(fields=["group", "assignment_type"]),
            models.Index(fields=["valid_from", "valid_to"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} -> {self.group.name} ({self.get_scope_display()})"

    @property
    def is_current(self) -> bool:
        if not self.is_active:
            return False
        now = timezone.now()
        if self.valid_from and self.valid_from > now:
            return False
        if self.valid_to and self.valid_to < now:
            return False
        return True


class EnterpriseConnector(TimeStampedModel):
    code = models.CharField("Code", max_length=64, unique=True)
    name = models.CharField("Nom", max_length=120)
    integration_type = models.CharField(
        "Type integration",
        max_length=32,
        choices=EnterpriseIntegrationTypeChoices.choices,
    )
    direction = models.CharField(
        "Direction",
        max_length=16,
        choices=EnterpriseIntegrationDirectionChoices.choices,
        default=EnterpriseIntegrationDirectionChoices.BIDIRECTIONAL,
    )
    active = models.BooleanField("Actif", default=True)
    transport = models.CharField(
        "Transport",
        max_length=16,
        choices=EnterpriseConnectorTransportChoices.choices,
        default=EnterpriseConnectorTransportChoices.MOCK,
    )
    base_url = models.URLField("Base URL", blank=True)
    auth_mode = models.CharField(
        "Mode auth",
        max_length=16,
        choices=EnterpriseConnectorAuthModeChoices.choices,
        default=EnterpriseConnectorAuthModeChoices.NONE,
    )
    auth_secret_id = models.CharField("Secret ID", max_length=120, blank=True)
    timeout_seconds = models.PositiveIntegerField("Timeout (seconds)", default=10)
    max_retries = models.PositiveSmallIntegerField("Max retries", default=5)
    retry_backoff_seconds = models.PositiveIntegerField("Retry backoff (seconds)", default=30)
    dlq_after_attempts = models.PositiveSmallIntegerField("DLQ after attempts", default=5)
    metadata = models.JSONField("Metadata", default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["integration_type", "active"]),
            models.Index(fields=["code", "active"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.code})"


class EnterpriseFieldMapping(TimeStampedModel):
    connector = models.ForeignKey(
        EnterpriseConnector,
        verbose_name="Connector",
        on_delete=models.CASCADE,
        related_name="field_mappings",
    )
    entity_type = models.CharField("Entity type", max_length=64)
    source_field = models.CharField("Source field", max_length=120)
    target_field = models.CharField("Target field", max_length=120)
    transform_rule = models.CharField("Transform rule", max_length=64, blank=True)
    is_required = models.BooleanField("Required", default=False)
    default_value = models.CharField("Default value", max_length=255, blank=True)
    version = models.PositiveIntegerField("Version", default=1)
    active = models.BooleanField("Active", default=True)

    class Meta:
        ordering = ["connector", "entity_type", "version", "source_field"]
        indexes = [
            models.Index(fields=["connector", "entity_type", "active"]),
            models.Index(fields=["entity_type", "target_field"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["connector", "entity_type", "source_field", "version"],
                name="uniq_connector_mapping_version",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.connector.code}:{self.entity_type}:{self.source_field}->{self.target_field}"


class EnterpriseOutboxEvent(TimeStampedModel):
    connector = models.ForeignKey(
        EnterpriseConnector,
        verbose_name="Connector",
        on_delete=models.CASCADE,
        related_name="outbox_events",
    )
    entity_type = models.CharField("Entity type", max_length=64)
    entity_id = models.PositiveIntegerField("Entity ID")
    event_type = models.CharField("Event type", max_length=120)
    idempotency_key = models.CharField("Idempotency key", max_length=180)
    payload = models.JSONField("Payload", default=dict)
    status = models.CharField(
        "Status",
        max_length=16,
        choices=EnterpriseOutboxStatusChoices.choices,
        default=EnterpriseOutboxStatusChoices.PENDING,
    )
    attempt_count = models.PositiveIntegerField("Attempt count", default=0)
    next_retry_at = models.DateTimeField("Next retry at", null=True, blank=True)
    delivered_at = models.DateTimeField("Delivered at", null=True, blank=True)
    last_error = models.TextField("Last error", blank=True)
    external_reference = models.CharField("External reference", max_length=255, blank=True)
    request_id = models.CharField("Request ID", max_length=64, blank=True)
    correlation_id = models.CharField("Correlation ID", max_length=64, blank=True)
    metadata = models.JSONField("Metadata", default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["status", "next_retry_at"]),
            models.Index(fields=["connector", "status"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["connector", "idempotency_key"], name="uniq_outbox_idempotency_per_connector")
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.connector.code}:{self.event_type}:{self.status}"


class EnterpriseInboxEvent(TimeStampedModel):
    connector = models.ForeignKey(
        EnterpriseConnector,
        verbose_name="Connector",
        on_delete=models.CASCADE,
        related_name="inbox_events",
    )
    external_event_id = models.CharField("External event ID", max_length=180)
    event_type = models.CharField("Event type", max_length=120)
    payload = models.JSONField("Payload", default=dict)
    status = models.CharField(
        "Status",
        max_length=16,
        choices=EnterpriseInboxStatusChoices.choices,
        default=EnterpriseInboxStatusChoices.PENDING,
    )
    processed_at = models.DateTimeField("Processed at", null=True, blank=True)
    attempt_count = models.PositiveIntegerField("Attempt count", default=0)
    last_error = models.TextField("Last error", blank=True)
    dedup_key = models.CharField("Dedup key", max_length=180, blank=True)
    correlation_id = models.CharField("Correlation ID", max_length=64, blank=True)
    metadata = models.JSONField("Metadata", default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["connector", "status"]),
            models.Index(fields=["dedup_key"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["connector", "external_event_id"], name="uniq_inbox_external_event_per_connector")
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.connector.code}:{self.event_type}:{self.status}"


class EnterpriseDeadLetterEvent(TimeStampedModel):
    connector = models.ForeignKey(
        EnterpriseConnector,
        verbose_name="Connector",
        on_delete=models.SET_NULL,
        related_name="dead_letters",
        null=True,
        blank=True,
    )
    direction = models.CharField(
        "Direction",
        max_length=16,
        choices=EnterpriseDeadLetterDirectionChoices.choices,
    )
    event_type = models.CharField("Event type", max_length=120)
    payload = models.JSONField("Payload", default=dict)
    reason = models.TextField("Reason")
    attempt_count = models.PositiveIntegerField("Attempt count", default=0)
    related_outbox = models.ForeignKey(
        EnterpriseOutboxEvent,
        verbose_name="Related outbox",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dead_letters",
    )
    related_inbox = models.ForeignKey(
        EnterpriseInboxEvent,
        verbose_name="Related inbox",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dead_letters",
    )
    metadata = models.JSONField("Metadata", default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["direction", "created_at"]),
            models.Index(fields=["connector", "direction"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.direction}:{self.event_type}"


# ---------------------------------------------------------------------------
# Phase 1 — Gestion des stocks, lots & péremption (aliments & additifs)
# ---------------------------------------------------------------------------


class WarehouseTypeChoices(models.TextChoices):
    USINE = "usine", "Usine / Production"
    DEPOT = "depot", "Dépôt central"
    MAGASIN = "magasin", "Magasin / Point de vente"
    AUTRE = "autre", "Autre"


class StockUnitChoices(models.TextChoices):
    SAC = "sac", "Sac"
    KG = "kg", "Kilogramme"
    TONNE = "tonne", "Tonne"
    LITRE = "litre", "Litre"
    CARTON = "carton", "Carton"
    UNITE = "unite", "Unité"


class StockLotStatusChoices(models.TextChoices):
    DISPONIBLE = "disponible", "Disponible"
    RESERVE = "reserve", "Réservé"
    QUARANTAINE = "quarantaine", "Quarantaine"
    BLOQUE = "bloque", "Bloqué"
    EPUISE = "epuise", "Épuisé"


class StockMovementTypeChoices(models.TextChoices):
    ENTREE = "entree", "Entrée (production / achat)"
    SORTIE = "sortie", "Sortie (vente / livraison)"
    AJUSTEMENT = "ajustement", "Ajustement d'inventaire"
    PERTE = "perte", "Perte / casse / péremption"
    TRANSFERT_OUT = "transfert_out", "Transfert sortant"
    TRANSFERT_IN = "transfert_in", "Transfert entrant"


# Types qui augmentent le stock du lot, vs. ceux qui le diminuent.
STOCK_MOVEMENT_INBOUND = {
    StockMovementTypeChoices.ENTREE,
    StockMovementTypeChoices.TRANSFERT_IN,
}
STOCK_MOVEMENT_OUTBOUND = {
    StockMovementTypeChoices.SORTIE,
    StockMovementTypeChoices.PERTE,
    StockMovementTypeChoices.TRANSFERT_OUT,
}


class Warehouse(TimeStampedModel):
    name = models.CharField("Nom", max_length=255)
    code = models.CharField("Code", max_length=32, unique=True)
    warehouse_type = models.CharField(
        "Type",
        max_length=16,
        choices=WarehouseTypeChoices.choices,
        default=WarehouseTypeChoices.DEPOT,
    )
    territory = models.ForeignKey(
        Territory,
        verbose_name="Territoire",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warehouses",
    )
    city = models.CharField("Ville", max_length=120, blank=True)
    region = models.CharField("Région", max_length=120, blank=True, choices=REGION_CHOICES)
    address = models.CharField("Adresse", max_length=255, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Responsable",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_warehouses",
    )
    is_active = models.BooleanField("Actif", default=True)
    notes = models.TextField("Notes", blank=True)

    class Meta:
        verbose_name = "Entrepôt"
        verbose_name_plural = "Entrepôts"
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.code})"


class StockLot(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        verbose_name="Produit",
        on_delete=models.PROTECT,
        related_name="lots",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        verbose_name="Entrepôt",
        on_delete=models.PROTECT,
        related_name="lots",
    )
    lot_code = models.CharField("N° de lot", max_length=64)
    unit = models.CharField(
        "Unité",
        max_length=12,
        choices=StockUnitChoices.choices,
        default=StockUnitChoices.SAC,
    )
    quantity_initial = models.DecimalField(
        "Quantité initiale", max_digits=12, decimal_places=2, default=0
    )
    quantity_on_hand = models.DecimalField(
        "Quantité en stock", max_digits=12, decimal_places=2, default=0
    )
    unit_cost = models.PositiveIntegerField("Coût unitaire (FCFA)", default=0)
    production_date = models.DateField("Date de fabrication", null=True, blank=True)
    expiry_date = models.DateField("Date de péremption (DLUO)", null=True, blank=True)
    status = models.CharField(
        "Statut",
        max_length=16,
        choices=StockLotStatusChoices.choices,
        default=StockLotStatusChoices.DISPONIBLE,
    )
    supplier_reference = models.CharField("Référence fournisseur/OF", max_length=120, blank=True)
    notes = models.TextField("Notes", blank=True)

    class Meta:
        verbose_name = "Lot de stock"
        verbose_name_plural = "Lots de stock"
        ordering = ["expiry_date", "product__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "warehouse", "lot_code"],
                name="unique_lot_per_product_warehouse",
            )
        ]
        indexes = [
            models.Index(fields=["status", "expiry_date"]),
            models.Index(fields=["product", "warehouse"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.product.name} · lot {self.lot_code}"

    @property
    def is_expired(self) -> bool:
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.localdate()

    @property
    def days_to_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.localdate()).days

    @property
    def is_near_expiry(self) -> bool:
        d = self.days_to_expiry
        return d is not None and 0 <= d <= 30


class StockMovement(TimeStampedModel):
    lot = models.ForeignKey(
        StockLot,
        verbose_name="Lot",
        on_delete=models.CASCADE,
        related_name="movements",
    )
    movement_type = models.CharField(
        "Type de mouvement",
        max_length=16,
        choices=StockMovementTypeChoices.choices,
    )
    quantity = models.DecimalField("Quantité", max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(
        "Solde après mouvement", max_digits=12, decimal_places=2, default=0
    )
    reason = models.CharField("Motif", max_length=255, blank=True)
    order = models.ForeignKey(
        Order,
        verbose_name="Commande liée",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    invoice = models.ForeignKey(
        Invoice,
        verbose_name="Facture liée",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    counterpart_warehouse = models.ForeignKey(
        Warehouse,
        verbose_name="Entrepôt de contrepartie",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_transfers",
        help_text="Pour les transferts : entrepôt d'origine ou de destination.",
    )
    occurred_at = models.DateTimeField("Date du mouvement", default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Enregistré par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_stock_movements",
    )
    notes = models.TextField("Notes", blank=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ["-occurred_at", "-created_at"]
        indexes = [
            models.Index(fields=["lot", "occurred_at"]),
            models.Index(fields=["movement_type", "occurred_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_movement_type_display()} · {self.quantity} ({self.lot})"

    @property
    def is_inbound(self) -> bool:
        return self.movement_type in STOCK_MOVEMENT_INBOUND

    @property
    def signed_quantity(self) -> Decimal:
        if self.movement_type in STOCK_MOVEMENT_INBOUND:
            return Decimal(self.quantity or 0)
        return -Decimal(self.quantity or 0)


# ---------------------------------------------------------------------------
# Phase 3 — Grille tarifaire par segment de client
# ---------------------------------------------------------------------------


class ProductPrice(TimeStampedModel):
    """Prix dédié d'un produit pour un type de client (distributeur, éleveur, etc.).

    En l'absence de tarif dédié, c'est le prix de référence du produit qui s'applique.
    """

    product = models.ForeignKey(
        Product,
        verbose_name="Produit",
        on_delete=models.CASCADE,
        related_name="segment_prices",
    )
    customer_type = models.CharField(
        "Type de client",
        max_length=24,
        choices=CustomerTypeChoices.choices,
    )
    unit_price = models.PositiveIntegerField("Prix unitaire (FCFA)", default=0)

    class Meta:
        verbose_name = "Tarif par segment"
        verbose_name_plural = "Tarifs par segment"
        ordering = ["product__name", "customer_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "customer_type"],
                name="unique_price_per_product_customer_type",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.product.name} · {self.get_customer_type_display()} : {self.unit_price}"

    @property
    def margin_amount(self) -> int:
        return int(self.unit_price or 0) - int(self.product.cost_price or 0)

    @property
    def margin_pct(self):
        if not self.unit_price:
            return None
        return round(self.margin_amount / int(self.unit_price) * 100, 1)


# ---------------------------------------------------------------------------
# Phase 4 — Objectifs commerciaux (quotas, réalisé, commissions)
# ---------------------------------------------------------------------------


class SalesTargetStatusChoices(models.TextChoices):
    ACTIF = "actif", "Actif"
    CLOS = "clos", "Clôturé"


MONTH_CHOICES = [
    (1, "Janvier"), (2, "Février"), (3, "Mars"), (4, "Avril"),
    (5, "Mai"), (6, "Juin"), (7, "Juillet"), (8, "Août"),
    (9, "Septembre"), (10, "Octobre"), (11, "Novembre"), (12, "Décembre"),
]


class SalesTarget(TimeStampedModel):
    """Objectif commercial mensuel d'un commercial (chiffre d'affaires à réaliser)."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Commercial",
        on_delete=models.CASCADE,
        related_name="sales_targets",
    )
    territory = models.ForeignKey(
        Territory,
        verbose_name="Territoire",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_targets",
    )
    segment = models.CharField(
        "Espèce (optionnel)",
        max_length=24,
        choices=SpeciesChoices.choices,
        blank=True,
    )
    period_year = models.PositiveIntegerField("Année")
    period_month = models.PositiveSmallIntegerField("Mois", choices=MONTH_CHOICES)
    target_amount = models.PositiveIntegerField("Objectif CA (FCFA)", default=0)
    target_quantity = models.DecimalField(
        "Objectif volume", max_digits=12, decimal_places=2, default=0
    )
    commission_rate_pct = models.DecimalField(
        "Taux de commission (%)", max_digits=5, decimal_places=2, default=0
    )
    status = models.CharField(
        "Statut",
        max_length=12,
        choices=SalesTargetStatusChoices.choices,
        default=SalesTargetStatusChoices.ACTIF,
    )
    notes = models.TextField("Notes", blank=True)

    class Meta:
        verbose_name = "Objectif commercial"
        verbose_name_plural = "Objectifs commerciaux"
        ordering = ["-period_year", "-period_month", "owner__username"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "period_year", "period_month", "segment"],
                name="unique_target_per_owner_period_segment",
            )
        ]
        indexes = [models.Index(fields=["period_year", "period_month"])]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.owner} · {self.period_month}/{self.period_year}"
