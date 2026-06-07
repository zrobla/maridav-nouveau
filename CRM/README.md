# CRM Maridav CI

Application Django pour gérer la relation client de Maridav Côte d'Ivoire : suivi des leads issus du site et de WhatsApp, pipeline commercial, commandes d'aliments/additifs, tickets techniques/biosécurité et visites terrain.

## Démarrage rapide
1. Créer un environnement virtuel et installer les dépendances :
   ```bash
   cd CRM
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Générer/appliquer les migrations (champs prix en FCFA) et créer un compte :
   ```bash
   python manage.py makemigrations crm
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. Lancer le serveur :
   ```bash
   python manage.py runserver
   ```

4. Initialiser les rôles et permissions :
   ```bash
   python manage.py setup_roles
   ```
   Puis, dans l’admin Django, affectez chaque utilisateur à l’un des groupes :
   - **Direction Générale** : vision et droits complets.
   - **Directeur Commercial** : pilotage commercial (clients, leads, opportunités, commandes, tâches, visites, support, catalogue).
   - **Commerciaux** : gestion portefeuille (clients en lecture, leads/opportunités/tâches/commandes/support en écriture limitée, catalogue en lecture).
   - **Support Technique** : tickets support, visites, tâches, consultation clients/contacts.

5. Importer le catalogue issu du site statique :
   ```bash
   python manage.py import_site_products
   ```
   (optionnel) préciser la source : `python manage.py import_site_products --source ..` si le site statique est dans le dossier parent.

## Fonctionnalités clés
- **UI premium Bootstrap** : layout latéral, topbar actions rapides, cartes metrics et charts (Chart.js) prêtes pour les décideurs.
- **Clients & contacts** : fiches éleveurs, distributeurs, intégrateurs ou vétérinaires avec coordonnées, segmentation par espèce (volailles, porcs, poissons, biosécurité) et notes terrain.
- **Leads entrants** : qualification des demandes web/WhatsApp/appels, besoins (aliments, additifs, biosécurité, formations) et plan d'action avec relance.
- **Opportunités & pipeline** : étapes diagnostic → offre → négociation → gagné/perdu, valeur attendue et probabilité.
- **Catalogue produits** : catégories par espèce (aliments complets, additifs, hygiène), prix et conditionnement.
- **Commandes/Devis** : génération de références, lignes produits, statut (brouillon, devis, confirmé, livré) et total calculé avec lignes produits.
- **Support technique** : tickets visites techniques, biosécurité, réclamations qualité, formations, avec priorités et échéances.
- **Visites terrain** : rapports (diagnostic, suivi, audit), plan d'actions, date de suivi et score biosécurité.
- **Tâches & relances** : appels, visites, livraisons, devis ou formations assignées aux équipes.
- **Tableau de bord** : indicateurs synthétiques (clients, leads, pipeline, tickets ouverts), charts de statuts, prochaines tâches et dernières visites.
- **Recherche globale** : recherche transverse clients/leads/opportunités/tickets pour accéder en un clic aux dossiers.

## Configuration
- Les paramètres par défaut sont dans `crm_project/settings.py` (SQLite, langue fr-FR, fuseau Africa/Abidjan).
- La clé secrète et le mode debug peuvent être fournis via les variables d'environnement `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` et `DJANGO_ALLOWED_HOSTS`.
- Le noyau est maintenant brandable par tenant via `CRM_TENANT_*`, `CRM_PLATFORM_*` et `CRM_BRAND_*` (nom CRM, tagline, logo, sous-titre).
- Les templates et statiques de l'interface CRM se trouvent dans `templates/` et `static/`.

## Alignement métiers Maridav CI
- Segmentation conforme aux espèces servies (volailles, porcs, poissons, biosécurité) et aux typologies de clients (éleveurs, distributeurs, intégrateurs, vétérinaires).
- Suivi des tickets techniques terrain, biosécurité et réclamations qualité, cœur du service après-vente.
- Gestion des visites et formations pour accompagner les performances d'élevage et la conformité réglementaire.
- Pipeline commercial et commandes pour les gammes d'aliments complets, additifs et hygiène.
