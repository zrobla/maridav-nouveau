from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

from crm.models import SpeciesChoices


class ContentStreamBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(label="Titre", required=False)
    paragraph = blocks.RichTextBlock(label="Texte")
    image = ImageChooserBlock(label="Image")
    quote = blocks.BlockQuoteBlock(label="Citation")
    cta = blocks.StructBlock(
        [
            ("label", blocks.CharBlock(required=True)),
            ("url", blocks.URLBlock(required=True)),
            ("style", blocks.ChoiceBlock(choices=[("primary", "Primary"), ("secondary", "Secondary")], required=False)),
        ],
        label="CTA",
    )
    faq = blocks.StructBlock(
        [("question", blocks.CharBlock()), ("answer", blocks.RichTextBlock())],
        label="FAQ",
    )


class BasePage(Page):
    summary = models.CharField("Résumé", max_length=250, blank=True)
    body = StreamField(ContentStreamBlock(), use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("summary"),
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("summary"),
        APIField("body"),
    ]

    class Meta:
        abstract = True


class HomePage(BasePage):
    hero_title = models.CharField("Titre hero", max_length=200, blank=True)
    hero_subtitle = models.CharField("Sous-titre hero", max_length=300, blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    cta_label = models.CharField("Label CTA", max_length=80, blank=True)
    cta_url = models.URLField("URL CTA", blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("hero_title"),
        FieldPanel("hero_subtitle"),
        FieldPanel("hero_image"),
        FieldPanel("cta_label"),
        FieldPanel("cta_url"),
    ]

    api_fields = BasePage.api_fields + [
        APIField("hero_title"),
        APIField("hero_subtitle"),
        APIField("hero_image"),
        APIField("cta_label"),
        APIField("cta_url"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["SpeciesPage", "ProductPage", "PartnerPage", "ArticlePage", "ResourcePage", "StandardPage"]


class StandardPage(BasePage):
    parent_page_types = ["HomePage", "StandardPage"]
    subpage_types = ["StandardPage"]


class SpeciesPage(BasePage):
    species = models.CharField("Espèce", max_length=24, choices=SpeciesChoices.choices, default=SpeciesChoices.VOLAILLES)

    content_panels = BasePage.content_panels + [FieldPanel("species")]
    api_fields = BasePage.api_fields + [APIField("species")]

    parent_page_types = ["HomePage"]
    subpage_types = ["ProductPage", "ArticlePage", "ResourcePage"]


class ProductPage(BasePage):
    product_category = models.CharField("Catégorie", max_length=120, blank=True)
    stage = models.CharField("Stade", max_length=120, blank=True)
    benefits = StreamField(
        [
            ("benefit", blocks.CharBlock(label="Bénéfice")),
        ],
        use_json_field=True,
        blank=True,
    )
    datasheet = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("product_category"),
        FieldPanel("stage"),
        FieldPanel("benefits"),
        FieldPanel("datasheet"),
    ]

    api_fields = BasePage.api_fields + [
        APIField("product_category"),
        APIField("stage"),
        APIField("benefits"),
        APIField("datasheet"),
    ]

    parent_page_types = ["SpeciesPage", "HomePage"]
    subpage_types = []


class PartnerPage(BasePage):
    website = models.URLField("Site web", blank=True)
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("website"),
        FieldPanel("logo"),
    ]

    api_fields = BasePage.api_fields + [APIField("website"), APIField("logo")]

    parent_page_types = ["HomePage", "StandardPage"]
    subpage_types = []


class ArticlePage(BasePage):
    author_name = models.CharField("Auteur", max_length=120, blank=True)
    published_date = models.DateField("Date de publication", null=True, blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("author_name"),
        FieldPanel("published_date"),
    ]

    api_fields = BasePage.api_fields + [APIField("author_name"), APIField("published_date")]

    parent_page_types = ["HomePage", "SpeciesPage", "StandardPage"]
    subpage_types = []


class ResourcePage(BasePage):
    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    resource_type = models.CharField("Type de ressource", max_length=120, blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("resource_type"),
        FieldPanel("document"),
    ]

    api_fields = BasePage.api_fields + [APIField("resource_type"), APIField("document")]

    parent_page_types = ["HomePage", "SpeciesPage", "StandardPage"]
    subpage_types = []


@register_setting
class SiteSettings(BaseSiteSetting):
    company_name = models.CharField("Nom société", max_length=120, default="MARIDAV CI")
    contact_email = models.EmailField("Email", blank=True)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=40, blank=True)
    address = models.CharField("Adresse", max_length=255, blank=True)
    footer_note = models.CharField("Note de bas de page", max_length=255, blank=True)

    panels = [
        FieldPanel("company_name"),
        FieldPanel("contact_email"),
        FieldPanel("phone"),
        FieldPanel("whatsapp"),
        FieldPanel("address"),
        FieldPanel("footer_note"),
    ]

    class Meta:
        verbose_name = "Paramètres site"
