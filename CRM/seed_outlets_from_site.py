"""Peuple les points de vente du CRM depuis la page réseau du site.

Source UNIQUE : distributeurs_maridav.html (racine du site) — la grille
`#pdvGrid` des 13 points de vente MARIDAV (agences & dépôts). Un point de vente
= un <article class="pdv-loc">. Le nom retenu est celui AFFICHÉ (h3 de la carte),
pas l'identifiant technique (data-city). Aucune donnée inventée : le site ne
publie ni prix ni GPS par agence -> gps laissé vide.

Lancer :  source .maridav/bin/activate
          python manage.py shell -c "import seed_outlets_from_site as s; s.run()"
"""
from __future__ import annotations
import re, html
from pathlib import Path
from django.db import transaction

from crm.models import Outlet

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "distributeurs_maridav.html"

PHONE_RE = re.compile(r"\(\+225\)[\d  ]+")


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def parse_outlets():
    src = PAGE.read_text(encoding="utf-8")
    grid = src.split('id="pdvGrid"', 1)[1]
    articles = re.findall(r'<article class="pdv-loc"(.*?)</article>', grid, re.S)
    out = []
    for a in articles:
        city_id = (re.search(r'data-city="([^"]*)"', a) or [None, ""])[1] if re.search(r'data-city="([^"]*)"', a) else ""
        name = clean((re.search(r"<h3[^>]*>(.*?)</h3>", a, re.S) or [None, ""])[1])
        tag = clean((re.search(r'pdv-tag">(.*?)</span>', a, re.S) or [None, ""])[1])
        lines = [clean(x) for x in re.findall(r"<(?:p|span|address)[^>]*>(.*?)</(?:p|span|address)>", a, re.S)]
        lines = [x for x in lines if x and x != tag]
        # Téléphones : scan du texte complet de la carte (liens tel: inclus).
        phones = []
        for m in PHONE_RE.findall(clean(a)):
            m = re.sub(r"\s+", " ", m).strip()
            if m not in phones:
                phones.append(m)
        addr_lines = [x for x in lines if not PHONE_RE.search(x)]
        address = addr_lines[0] if addr_lines else ""

        # Région : le tag de zone ; le siège (Marcory) rattaché au Grand Abidjan.
        region = "Grand Abidjan" if tag.lower().startswith("siège") else tag
        # Ville : le nom affiché, sauf le siège dont le nom porte la marque.
        city = "Abidjan" if name.lower().startswith("maridav") else name
        channel = "grossiste" if tag.lower().startswith("siège") else "detail"
        notes = ("Tél. : " + " · ".join(phones)) if phones else ""

        out.append(dict(name=name, city=city, region=region, address=address,
                        channel=channel, notes=notes))
    return out


@transaction.atomic
def run(apply: bool = True):
    rows = parse_outlets()
    print(f"Points de vente sur le site : {len(rows)}")
    if not apply:
        for r in rows:
            print(" ", r)
        return rows
    for r in rows:
        Outlet.objects.update_or_create(
            name=r["name"],
            defaults=dict(
                city=r["city"], region=r["region"], address=r["address"],
                channel=r["channel"], status="actif", notes=r["notes"],
            ),
        )
    print(f"FINAL : {Outlet.objects.count()} points de vente")
    return rows
