"""Importe les produits du site statique dans le CRM."""

from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from crm.models import ProductCategory, Product, SpeciesChoices


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


KEYWORDS = {
    "bio": ["biosecur", "hygiene", "virocid", "keno", "cid", "sanit"],
    "additifs": ["additif", "additifs", "mycotox", "acid", "biotronic", "biomix", "digestarom"],
    "premix": ["premix", "macro"],
    "porcs": ["porc", "truie", "porcin"],
    "poissons": ["tilapia", "poisson", "aqua"],
    "volailles": ["volaille", "poulet", "pondeuse", "chair", "ponte", "poulette"],
}


def infer_category(title: str, path: Path) -> tuple[str, str]:
    text = f"{title} {path.as_posix()}".lower()
    segment = SpeciesChoices.VOLAILLES
    name = "Aliments Volailles"

    def has(keys):
        return any(k in text for k in keys)

    if has(KEYWORDS["bio"]):
        name = "Biosécurité & Hygiène"
        segment = SpeciesChoices.MULTI
    elif has(KEYWORDS["additifs"]):
        name = "Additifs / Correcteurs"
        segment = SpeciesChoices.MULTI
    elif has(KEYWORDS["premix"]):
        name = "Premix / Macro"
        segment = SpeciesChoices.MULTI
    elif has(KEYWORDS["porcs"]):
        name = "Aliments Porcs"
        segment = SpeciesChoices.PORCINS
    elif has(KEYWORDS["poissons"]):
        name = "Aliments Poissons"
        segment = SpeciesChoices.POISSONS
    elif has(KEYWORDS["volailles"]):
        name = "Aliments Volailles"
        segment = SpeciesChoices.VOLAILLES
    return name, segment


class Command(BaseCommand):
    help = "Parcourt les fichiers HTML du site statique et crée les catégories/produits dans le CRM."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default=str(Path(settings.BASE_DIR).parent),
            help="Dossier racine du site statique (par défaut le parent de BASE_DIR)",
        )

    def handle(self, *args, **options):
        source = Path(options["source"]).resolve()
        if not source.exists():
            raise CommandError(f"Dossier source introuvable: {source}")

        html_files = list(source.rglob("*.html"))
        created = 0
        for html_file in html_files:
            try:
                content = html_file.read_text(encoding="utf-8", errors="ignore")
            except UnicodeDecodeError:
                continue
            title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
            if not title_match:
                continue
            raw_title = title_match.group(1).strip()
            name = re.sub(r"^MARIDAV\s*—\s*", "", raw_title).strip()
            if not name:
                continue
            cat_name, segment = infer_category(name, html_file)
            cat_slug = slugify(cat_name)
            category, _ = ProductCategory.objects.get_or_create(
                slug=cat_slug,
                defaults={"name": cat_name, "segment": segment, "description": "Importé depuis le site statique"},
            )
            sku = slugify(name).upper()[:64]
            defaults = {
                "category": category,
                "name": name,
                "packaging": "",
                "unit_price": 0,
                "status": "actif",
                "usage_notes": "Import automatique depuis le site statique",
            }
            Product.objects.update_or_create(sku=sku, defaults=defaults)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Produits importés ou mis à jour: {created}"))
