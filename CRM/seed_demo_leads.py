"""
Seed de démonstration — MARIDAV CI
==================================
Crée des demandes entrantes réalistes (éleveurs / fermes de Côte d'Ivoire) en
passant par le MÊME chemin que les formulaires publics du site
(`PublicLeadCreateSerializer`). Score de lead, priorité et fenêtres SLA sont donc
calculés par l'automation réelle — exactement comme une vraie demande du site.

Usage (depuis le dossier CRM, venv activé) :
    python seed_demo_leads.py            # crée le jeu de démo
    python seed_demo_leads.py --purge    # supprime UNIQUEMENT les records de démo
    python seed_demo_leads.py --list     # liste les records de démo existants

Sécurité : tous les records portent le marqueur source_page="seed-demo-maridav"
et un e-mail @demo-maridav.ci → purge ciblée, jamais de suppression en masse.
"""
import os, sys, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm_project.settings")
django.setup()

from crm.api.serializers import PublicLeadCreateSerializer  # noqa: E402
from crm.models import InboundRequest  # noqa: E402

MARKER = "seed-demo-maridav"

# Jeu de démo : éventail volontaire de priorités/scores pour un inbox vivant.
DEMO = [
    {
        "kind": "lead", "name": "Konan Yao Aristide", "company": "Aviculture du Bélier",
        "phone": "+2250707112233", "email": "achats@demo-maridav.ci",
        "segment": "volailles", "product": "Aliment Ponte 1",
        "volume": "5000 pondeuses / 80 sacs par mois",
        "intent": "Demande de devis", "channel_preference": "whatsapp",
        "region": "Yamoussoukro",
        "message": "Bonjour, nous souhaitons un devis aliment ponte pour 5000 pondeuses, livraison mensuelle.",
        "consent": True,
    },
    {
        "kind": "lead", "name": "Dr Aka Mireille", "company": "Ferme Avicole Akwaba",
        "phone": "+2250505889977", "email": "ferme.akwaba@demo-maridav.ci",
        "segment": "biosecurite", "product": "Virocid",
        "volume": "Bâtiment de 8000 sujets",
        "intent": "Urgence sanitaire - hausse de mortalité", "channel_preference": "appel",
        "region": "Bingerville",
        "message": "Pic de mortalité depuis 3 jours, besoin d'un protocole de désinfection et d'un appui technique rapide.",
        "consent": True,
    },
    {
        "kind": "lead", "name": "Coulibaly Drissa", "company": "GIE Éleveurs de Daloa",
        "phone": "+2250708445566", "email": "gie.daloa@demo-maridav.ci",
        "segment": "multi", "product": "Aliments complets + prémix",
        "volume": "Coopérative ~120 éleveurs",
        "intent": "Devis et conditions de gros", "channel_preference": "appel",
        "region": "Daloa",
        "message": "Nous regroupons une centaine d'éleveurs et cherchons un fournisseur en gros sur volailles et porcs.",
        "consent": True,
    },
    {
        "kind": "lead", "name": "N'Guessan Patrick", "company": "Élevage Porcin La Référence",
        "phone": "+2250102334455", "email": "laref.porcs@demo-maridav.ci",
        "segment": "porcins", "product": "Aliment Porc Croissance",
        "volume": "200 porcs en engraissement",
        "intent": "Demande de prix", "channel_preference": "whatsapp",
        "region": "Anyama",
        "message": "Quel est le prix de l'aliment porc croissance en sacs de 50 kg, et les délais de livraison ?",
        "consent": True,
    },
    {
        "kind": "lead", "name": "Touré Salif", "company": "Pisciculture Lagune Bleue",
        "phone": "+2250709667788", "email": "lagunebleue@demo-maridav.ci",
        "segment": "poissons", "product": "Nutra Tilapia",
        "volume": "Étangs ~30 000 alevins",
        "intent": "Renseignement gamme tilapia", "channel_preference": "whatsapp",
        "region": "Grand-Lahou",
        "message": "Je démarre en pisciculture tilapia, je voudrais être conseillé sur la gamme et le plan d'alimentation.",
        "consent": True,
    },
    {
        "kind": "lead", "name": "Adjoua Estelle", "company": "",
        "email": "estelle.particulier@demo-maridav.ci",
        "segment": "volailles", "intent": "Renseignement",
        "region": "Abidjan",
        "message": "Bonjour, je débute un petit poulailler familial, avez-vous de la documentation ?",
        "consent": True,
    },
]


def purge():
    qs = InboundRequest.objects.filter(source_page=MARKER)
    n = qs.count()
    print(f"Records de démo trouvés : {n}")
    if n:
        qs.delete()
        print(f"Supprimés : {n}")


def listing():
    qs = InboundRequest.objects.filter(source_page=MARKER).order_by("-id")
    print(f"Records de démo : {qs.count()}")
    for r in qs:
        print(f"  #{r.id:>3} {r.name[:26]:26} | {r.company[:22]:22} | prio={r.priority} | due={r.first_response_due_at}")


def seed():
    created = []
    for payload in DEMO:
        payload = {**payload, "source_page": MARKER}
        ser = PublicLeadCreateSerializer(data=payload)
        if not ser.is_valid():
            print(f"  ⚠ invalide ({payload['name']}): {ser.errors}")
            continue
        obj = ser.save()
        inbound = obj if isinstance(obj, InboundRequest) else getattr(obj, "inbound", None)
        created.append(payload["name"])
        print(f"  ✓ {payload['name']:26} créé")
    print(f"\n{len(created)} demandes de démo créées via le funnel public.")
    listing()


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "seed"
    if arg == "--purge":
        purge()
    elif arg == "--list":
        listing()
    else:
        seed()
