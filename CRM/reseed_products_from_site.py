"""Reconstruit le catalogue produits du CRM depuis les pages produits du site.

Source UNIQUE : les catalogues JSON du site (parent de CRM/), ceux que lit
build_maridav.py pour générer les pages produits. Un « produit » = toute page
produit du site (entrée JSON avec un bloc `hero`, rendue), rattachée à une
filière/département, y compris les produits transversaux. Le nom retenu est le
titre AFFICHÉ sur la page (hero.h1), pas le nom de fichier.

Lancer :  source .maridav/bin/activate
          python manage.py shell -c "import reseed_products_from_site as r; r.run()"
"""
from __future__ import annotations
import json, re, html
from pathlib import Path
from django.db import transaction
from django.utils.text import slugify

from crm.models import (
    Product, ProductCategory, OrderItem, InvoiceItem, Forecast,
)

ROOT = Path(__file__).resolve().parent.parent  # racine du site (parent de CRM/)
FILES = [
    "products.json",            # volailles
    "products-porcs.json",      # porcs
    "products-poissons.json",   # poissons
    "products-biosecurite.json",# biosécurité (transversale)
]


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def iter_products(data: dict):
    """Même logique que build_maridav.iter_products : une page produit = item
    d'une liste top-level (hors clés `_`) qui porte un `hero` et est rendue."""
    for key, items in data.items():
        if key.startswith("_") or not isinstance(items, list):
            continue
        for it in items:
            if it.get("_render", True) and "hero" in it:
                yield it


def packaging_of(it: dict) -> str:
    """Conditionnement tel qu'indiqué sur la fiche (ligne spec dédiée)."""
    for r in it.get("spec", {}).get("rows", []):
        k = clean(r.get("k", "")).lower()
        if "conditionnement" in k or k in ("formats", "format"):
            return clean(r.get("v", ""))
    return ""


def category_of(it: dict):
    """(segment, nom, slug) reflétant filière + département du site.
    Transversal multi-espèces -> segment multi ; sinon segment = espèce."""
    t = it.get("type", "")
    esp = it.get("espece", "")
    species_in_fl = {f.split("-")[0] for f in it.get("filieres", [])}

    if t == "biosecurite":
        return ("biosecurite", "Biosécurité & hygiène", "biosecurite-hygiene")
    if t == "concentre-proteique" and len(species_in_fl) > 1:
        return ("multi", "Multi-espèces — Concentrés", "multi-concentres")

    M = {
        ("volailles", "aliment-complet"): ("volailles", "Volailles — Aliments complets", "volailles-aliments-complets"),
        ("volailles", "concentre"):       ("volailles", "Volailles — Concentrés", "volailles-concentres"),
        ("volailles", "macro-premix"):    ("volailles", "Volailles — Macro-prémix", "volailles-macro-premix"),
        ("volailles", "premix"):          ("volailles", "Volailles — Prémix", "volailles-premix"),
        ("porcs", "aliment-complet"):     ("porcins", "Porcs — Aliments complets", "porcs-aliments-complets"),
        ("porcs", "concentre"):           ("porcins", "Porcs — Concentrés", "porcs-concentres"),
        ("poissons", "aliment-complet"):  ("poissons", "Poissons — Aliments complets", "poissons-aliments-complets"),
        ("poissons", "additif-eau"):      ("poissons", "Poissons — Additifs", "poissons-additifs"),
    }
    key = (esp, t)
    if key in M:
        return M[key]
    # garde-fou : pas de perte silencieuse
    return ("multi", f"Divers — {esp}/{t}", slugify(f"divers-{esp}-{t}"))


def build_catalog():
    """Retourne la liste des produits à créer (dicts prêts pour le modèle)."""
    rows = []
    seen_sku = {}
    for f in FILES:
        data = json.loads((ROOT / f).read_text(encoding="utf-8"))
        for it in iter_products(data):
            name = clean(it["hero"]["h1"])
            seg, cat_name, cat_slug = category_of(it)
            seg_prefix = {"volailles": "VOL", "porcins": "POR", "poissons": "POI",
                          "biosecurite": "BIO", "multi": "MUL"}.get(seg, "DIV")
            base = f"MAR-{seg_prefix}-{slugify(name).upper()}"[:60]
            sku = base
            n = 2
            while sku in seen_sku:
                sku = f"{base}-{n}"
                n += 1
            seen_sku[sku] = name
            rows.append({
                "name": name,
                "sku": sku,
                "packaging": packaging_of(it),
                "segment": seg,
                "cat_name": cat_name,
                "cat_slug": cat_slug,
                "usage_notes": clean(it.get("hero", {}).get("eyebrow", "")),
                "transversal": bool(it.get("transversal")),
            })
    return rows


# Repointage des lignes commande/facture (PROTECT) : ancien produit -> nom du
# nouveau produit catalogue. Clé = sku actuel.
REPOINT = {
    "ALIMENT-PONTE-PHASE-1-18-40-SEMAINES": "Aliment Ponte Phase 1",
    "VITALIS-BROODSTOCK-REPRODUCTION-TILAPIA-MARIDAV-CI": "Vitalis®",
    "ALIMENT-PORC-CROISSANCE-25-70-KG-MARIDAV-CI": "Aliment Porc Croissance",
    "AQUACARE-PROBIOTIQUE-QUALIT-D-EAU-MARIDAV-CI": "AquaCare®",
    "ALIMENT-POULETTE-CROISSANCE-7-18-SEMAINES": "Aliment Poulette",
    "ALIMENT-PORC-FINITION-70-KG-MARIDAV-CI": "Aliment Porc Finition",
}
# Produits/ligne purement de test à supprimer (aucun équivalent réel sur le site)
DROP_TEST_SKUS = {"QA-SKU-001"}


@transaction.atomic
def run(apply: bool = True):
    catalog = build_catalog()
    print(f"Catalogue site : {len(catalog)} produits")

    if not apply:
        return catalog

    # 1) Créer les nouvelles catégories (segment imposé) + index par nom de produit
    cats = {}
    for r in catalog:
        if r["cat_slug"] not in cats:
            cats[r["cat_slug"]] = ProductCategory.objects.create(
                name=r["cat_name"], slug=r["cat_slug"], segment=r["segment"],
                description="Catégorie dérivée des pages produits du site maridav.ci.",
            )
    # 2) Créer les nouveaux produits (SKU préfixés MAR- : aucune collision)
    new_by_name = {}
    for r in catalog:
        p = Product.objects.create(
            category=cats[r["cat_slug"]],
            name=r["name"], sku=r["sku"], packaging=r["packaging"],
            unit_price=0, status="actif", usage_notes=r["usage_notes"],
        )
        new_by_name.setdefault(r["name"], p)
    print(f"Créés : {len(new_by_name)} produits dans {len(cats)} catégories")

    # 3) Repointer les lignes commande/facture vers les nouveaux produits
    for old_sku, new_name in REPOINT.items():
        target = new_by_name.get(new_name)
        if not target:
            raise RuntimeError(f"Cible de repointage introuvable : {new_name!r}")
        n_oi = OrderItem.objects.filter(product__sku=old_sku).update(product=target)
        n_ii = InvoiceItem.objects.filter(product__sku=old_sku).update(product=target)
        if n_oi or n_ii:
            print(f"  repointé {old_sku} -> {new_name} (OI={n_oi}, II={n_ii})")

    # 4) Supprimer les lignes de test (QA) puis leurs produits
    for sku in DROP_TEST_SKUS:
        d_oi = OrderItem.objects.filter(product__sku=sku).delete()
        d_ii = InvoiceItem.objects.filter(product__sku=sku).delete()
        print(f"  supprimé lignes test {sku} : OI={d_oi}, II={d_ii}")

    # 5) Supprimer tous les anciens produits (ceux hors nouveau préfixe MAR-)
    old_qs = Product.objects.exclude(sku__startswith="MAR-")
    # garde-fou PROTECT : il ne doit plus rester de référence
    still_ref = old_qs.filter(invoiceitem__isnull=False) | old_qs.filter(orderitem__isnull=False)
    if still_ref.exists():
        refs = list(still_ref.values_list("sku", flat=True).distinct())
        raise RuntimeError(f"Produits encore référencés, refus de supprimer : {refs}")
    Forecast.objects.filter(product__in=old_qs).delete()
    n_del, _ = old_qs.delete()
    print(f"Anciens produits supprimés : {n_del} lignes")

    # 6) Supprimer les anciennes catégories désormais vides
    empty = ProductCategory.objects.filter(products__isnull=True)
    n_cat, _ = empty.delete()
    print(f"Anciennes catégories vides supprimées : {n_cat}")

    print(f"\nFINAL : {Product.objects.count()} produits, {ProductCategory.objects.count()} catégories")
    return catalog
