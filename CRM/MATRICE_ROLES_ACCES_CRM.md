# Matrice des rôles & accès — CRM Maridav CI

> Document de référence pour la **gouvernance des accès** du CRM Maridav.
> Il liste chaque **profil (rôle)** et les **pages / fonctions** auxquelles il est censé
> accéder pour la bonne marche du système. À tenir à jour à chaque évolution des droits.
>
> **Source d'autorité** : la commande `python manage.py setup_roles` (fichier
> `crm/management/commands/setup_roles.py`). Si on modifie les droits, on modifie cette
> commande **puis** on relance `setup_roles`, **puis** on met à jour ce document.
>
> Compagnon du **`MANUEL_UTILISATION_CRM.md`** (mode d'emploi des écrans).

**Version : v1.2 — 2026-06-22** (Pilotage verrouillé `view_reports` ; créances cloisonnées par portefeuille + badge de portée).

---

## 1. Comment fonctionnent les accès (à lire avant la matrice)

Le CRM applique un contrôle d'accès **par rôle** (RBAC). Trois notions :

1. **Le compte utilisateur** (login/mot de passe) — créé par l'Administrateur Système /
   la Direction. Sans compte, aucun accès.
2. **Le groupe (= rôle)** — chaque utilisateur est rattaché à un ou plusieurs groupes.
   Le groupe porte les **permissions**. C'est ce qui décide des écrans visibles.
3. **La permission** — autorisation élémentaire sur un type d'objet, déclinée en
   **4 niveaux** :
   - **V** = *Voir* (consulter listes et fiches)
   - **A** = *Ajouter* (créer)
   - **M** = *Modifier* (éditer l'existant)
   - **S** = *Supprimer*

> Dans les tableaux ci-dessous : `V` / `V A` / `V A M` / `V A M S` indiquent le niveau
> cumulé. Une case **vide** = aucun accès (le menu n'apparaît même pas, et l'URL renvoie
> vers la page de connexion ou un refus).

**Règle d'or de sécurité (moindre privilège)** : on n'attribue que ce qui est nécessaire
au métier de la personne. En cas de doute, on donne **moins**, puis on élargit sur demande
justifiée — jamais l'inverse.

**Affectation d'un rôle à une personne** : depuis le CRM, menu **Accès / Utilisateurs**
(`/crm/access/users/`) ou via l'admin Django. La couche **RoleAssignment**
(`/crm/access/assignments/`) permet en plus des affectations **avec périmètre** (région,
espèce…) et une date de révocation.

---

## 2. Les 12 profils (rôles) du système

| # | Rôle (groupe) | Vocation en une phrase |
|---|---------------|------------------------|
| 1 | **Direction/Propriétaire** | Contrôle total — direction de l'entreprise. |
| 2 | **Direction Générale** | Contrôle total — pilotage exécutif. |
| 3 | **Administrateur Système** | Exploitation de la plateforme + gestion des comptes/groupes (IAM). |
| 4 | **Directeur Commercial** | Pilotage des équipes de vente, du pipeline, des objectifs et des stocks. |
| 5 | **Commerciaux** | Gestion du portefeuille clients et conversion des ventes. |
| 6 | **Technico-Commerciaux** | Vente + expertise terrain (territoires, points de vente, technique). |
| 7 | **Experts Métier** | Conseil par espèce/stade/objectif, support technique. |
| 8 | **Technicien CRM & Support IT** | Exploitation quotidienne + support plateforme + intégrations. |
| 9 | **Support Technique** | Identique au Technicien CRM & Support IT (même jeu de droits). |
| 10 | **Caissière** | Exécution des commandes, encaissement, mouvements de stock de sortie. |
| 11 | **Comptable** | Visibilité financière, factures, créances, conformité. |
| 12 | **Gouvernance & Conformité** | Politiques d'approbation, audit, qualité de données, IAM. |

> Les rôles **1, 2, 3** disposent du **CRM complet** (`V A M S` partout) **plus** la
> gestion des comptes et groupes (`auth_user`, `auth_group`). Ce sont les seuls profils
> habilités à créer/supprimer des utilisateurs et à modifier les rôles.

---

## 3. Matrice synthétique — module métier × rôle

Légende : **V**oir · **A**jouter · **M**odifier · **S**upprimer · *(vide)* = pas d'accès.
DP/DG/Admin = Direction-Propriétaire, Direction Générale, Administrateur Système.

| Module / fonction | DP·DG·Admin | Dir. Commercial | Commerciaux | Technico-Comm. | Experts Métier | Tech. CRM / Support | Caissière | Comptable | Gouvernance |
|---|---|---|---|---|---|---|---|---|---|
| **Tableau de bord** | V | V | V | V | V | V | V | V | V |
| **Rapports** | V | V | | | V | | | V | V |
| **Demandes entrantes (Inbox)** | VAMS | VM | VAM | VAM | VM | VM | | | |
| **Clients** | VAMS | VAM | V | VAM | V | V | V | V | |
| **Contacts** | VAMS | VAM | VAM | VAM | V | V | V | | |
| **Leads** | VAMS | VAM | VAM | VAM | VM | | | | |
| **Opportunités** | VAMS | VAM | VAM | VAM | VM | | | V | |
| **Commandes** | VAMS | VAM | VAM | VAM | V | | VAM | VM | |
| **Factures (ventes)** | VAMS | VAM | VAM | VAM | V | VAM | VAM | VM | VM |
| **Paiements / encaissement** | VAMS | VAM | VAM | VAM | | VAM | VAM | VM | |
| **Produits & catégories** | VAMS | VAM | V | V | V | | V | | |
| **Grille tarifaire & marges** | VAMS | VAM | V | V | V | | V | | |
| **Stock — Lots** | VAMS | VAM | V | V | V | | V | V | |
| **Stock — Entrepôts** | VAMS | V | V | V | | | V | V | |
| **Stock — Mouvements** | VAMS | VA | | V | | | VA | V | |
| **Objectifs commerciaux** | VAMS | VAM | V | V | | | | V | |
| **Pilotage commercial & financier** | V | V | | | V | | | V | V |
| **Prévisions (Forecasts)** | VAMS | VAM | | V | V | | | VM | |
| **Promotions** | VAMS | VAM | | V | V | | | V | |
| **Territoires** | VAMS | | | V | V | | | | |
| **Points de vente (Outlets)** | VAMS | | | V | V | | V | V | |
| **Support / SAV (cas)** | VAMS | VAM | VAM | VAM | VAM | VAM | | | |
| **Visites terrain** | VAMS | VAM | VA | VAM | VAM | VAM | | | |
| **Tâches** | VAMS | VAM | VAM | VAM | VAM | VAM | VA | | |
| **Règles de routage** | VAMS | | | | | VAM | | | |
| **Candidatures (carrières)** | VAMS | | | | | VM | | | |
| **Newsletter** | VAMS | | | | | VM | | | |
| **Gouvernance — Audit** | V | V | | | | V | | V | V |
| **Gouvernance — Qualité données** | VAMS | VM | V | V | V | VM | | | VM |
| **Gouvernance — Escalades SLA** | VAMS | VM | V | V | V | VM | | | VM |
| **Gouvernance — Approbations** | VAMS | VM | V | | | | V | VM | VM |
| **Gouvernance — Politiques d'appro.** | VAMS | V | | | | | | | VAM |
| **Accès / IAM — Affectations rôles** | VAMS | | | | | VAM | | | VAM |
| **Accès / Comptes & profils sécurité** | VAMS | | | | | VM | | | VM |
| **Intégrations entreprise (connecteurs)** | VAMS | V* | | | | VAM | | V* | VAM |
| **Comptes utilisateurs & groupes (IAM)** | VAMS | | | | | | | | |

> `*` Pour les connecteurs entreprise, Dir. Commercial et Comptable n'ont que la **vue**
> des événements (outbox/inbox), pas la configuration. Seuls DP/DG/Admin, Tech. CRM/Support
> et Gouvernance configurent les connecteurs.
>
> **Comptes utilisateurs & groupes (dernière ligne)** : réservé strictement à
> **DP / DG / Administrateur Système** (création/suppression de comptes, attribution des
> groupes). Les autres profils ne gèrent pas les comptes.

---

## 4. Détail par profil — « ce que la personne doit pouvoir faire »

### 4.1 Direction/Propriétaire · Direction Générale · Administrateur Système
**Accès : la totalité du CRM (V A M S) + gestion des comptes et des groupes.**
- Tous les écrans des sections 3 sans restriction.
- **Seuls** habilités à : créer/modifier/supprimer des **comptes utilisateurs**, créer/
  modifier des **groupes (rôles)**, réinitialiser des accès.
- L'Administrateur Système assure en plus l'exploitation technique (déploiement, sauvegardes,
  intégrations). La Direction conserve la vision stratégique et la validation finale.
- *Bonne pratique* : limiter le nombre de comptes à ce niveau (2–3 superutilisateurs max),
  car ils peuvent tout faire, y compris purger des données.

### 4.2 Directeur Commercial
**Vocation : piloter la force de vente, le pipeline, les objectifs, les tarifs et le stock.**
Doit pouvoir :
- **Piloter** : Tableau de bord, **Rapports**, **Pilotage commercial & financier**
  (`/crm/performance/`), **Objectifs commerciaux** (créer/ajuster — `/crm/targets/`).
- **Animer la vente** : Clients, Contacts, Leads, Opportunités, Commandes, Factures
  (créer & modifier), Tâches, Visites, Support.
- **Tarification** : Produits, **Grille tarifaire & marges** (`/crm/products/margins/`) en
  création/modification.
- **Stock** : voir les entrepôts, gérer les **lots** (créer/modifier), **enregistrer des
  mouvements** (entrées) ; ne supprime pas le stock.
- **Gouvernance** : traiter les **approbations** (remises ≥ 8 %, exceptions crédit), suivre
  audit, qualité de données, escalades.
- Ne gère **pas** les comptes utilisateurs ni les territoires/points de vente (lecture
  uniquement via les écrans concernés).

### 4.3 Commerciaux
**Vocation : gérer leur portefeuille et convertir.** Doit pouvoir :
- **Demandes entrantes** : créer et qualifier (V A M).
- **Clients** : **consulter** (pas de création — passe par Technico ou Dir. Commercial) ;
  **Contacts** : créer/modifier.
- **Leads, Opportunités, Commandes, Factures, Paiements** : créer & modifier (cycle de vente
  complet jusqu'à l'encaissement).
- **Produits, Tarifs/marges, Lots, Objectifs** : **consultation** (pour vendre au bon prix
  et connaître la dispo) — pas de modification.
- **Visites** : créer (compte rendu) ; **Tâches & Support** : gérer.
- Ne voit ni la gouvernance avancée ni l'IAM.

### 4.4 Technico-Commerciaux
**Vocation : vendre + apporter l'expertise terrain.** Comme les Commerciaux, **plus** :
- **Clients** : peut **créer/modifier** (et pas seulement consulter).
- **Territoires, Points de vente** : consultation.
- **Stock — Mouvements** : consultation (suivi technique des lots livrés).
- **Prévisions, Promotions** : consultation.
- Reste sans accès à l'IAM et aux comptes.

### 4.5 Experts Métier
**Vocation : conseil technique par espèce/stade/objectif, SAV.** Doit pouvoir :
- **Tableau de bord & Rapports** : consultation.
- **Demandes entrantes, Leads, Opportunités** : consulter et **modifier** (apport
  d'expertise), sans création de masse.
- **Clients, Contacts, Commandes, Factures, Produits, Tarifs, Lots, Territoires, Points de
  vente, Prévisions, Promotions** : **consultation**.
- **Support / SAV, Visites, Tâches** : **gestion complète** (c'est leur terrain).
- Pas d'accès stock-écriture, ni finance-écriture, ni IAM.

### 4.6 Technicien CRM & Support IT  *(= Support Technique, droits identiques)*
**Vocation : faire tourner la plateforme au quotidien + support + intégrations.** Doit pouvoir :
- **Clients, Contacts** : consultation ; **Demandes entrantes** : voir/modifier (réaffecter).
- **Factures** : créer/modifier (assistance facturation) ; **Support, Visites, Tâches** :
  gestion complète.
- **Règles de routage, Candidatures, Newsletter** : gérer.
- **Gouvernance** : audit (vue), qualité de données & escalades (traiter).
- **IAM** : gérer **affectations de rôles** et **profils de sécurité** (mais **pas** la
  création de comptes/superutilisateurs, réservée à la Direction/Admin Système).
- **Intégrations entreprise** : configurer connecteurs, mappings, rejouer les événements.

### 4.7 Caissière
**Vocation : exécuter les commandes, encaisser, mouvements de sortie de stock.** Doit pouvoir :
- **Tableau de bord** ; **Clients, Contacts, Produits, Points de vente, Entrepôts, Lots** :
  consultation.
- **Commandes, Factures, Paiements** : créer & modifier (vente comptoir, encaissement).
- **Stock — Mouvements** : **voir + ajouter** (enregistrer les sorties liées aux ventes).
- **Tâches** : voir + créer ; **Approbations** : consultation (suivre l'état d'une demande
  de remise/exception).
- Aucun accès gouvernance avancée / IAM / objectifs.

### 4.8 Comptable
**Vocation : visibilité financière et conformité.** Doit pouvoir :
- **Tableau de bord, Rapports, Pilotage commercial & financier** : consultation.
- **Factures** : consulter & **modifier** (régularisation/statut) ; **Commandes** : voir &
  modifier ; **Paiements** : consulter.
- **Créances âgées** : via le pilotage et les factures (suivi de l'encours).
- **Clients, Points de vente, Entrepôts, Lots, Mouvements, Produits, Objectifs, Promotions,
  Prévisions** : consultation (Prévisions : peut modifier).
- **Approbations** : traiter (volet financier) ; **Audit** : consultation.
- Pas d'IAM ni de configuration plateforme.

### 4.9 Gouvernance & Conformité
**Vocation : règles, audit, qualité, IAM de contrôle.** Doit pouvoir :
- **Politiques d'approbation** : créer/modifier ; **Approbations** : traiter.
- **Qualité de données, Escalades SLA** : traiter ; **Audit** : consultation.
- **Factures** : voir & modifier (contrôle conformité, FNE).
- **IAM** : gérer **affectations de rôles** et **profils de sécurité** ; **Intégrations
  entreprise** : configurer.
- Ne gère pas le cycle de vente opérationnel (leads/commandes en création).

---

## 5. Carte des pages (URL → permission requise → profils)

> Toutes les URLs sont préfixées par `/crm/`. « DP/DG/Admin » ont accès partout.

| Page / écran | URL | Permission requise | Profils ayant l'accès |
|---|---|---|---|
| Tableau de bord | `/crm/` | `view_dashboard` | Tous (les 12 rôles) |
| Demandes entrantes | `/crm/inbox/` | `view_inboundrequest` | DP/DG/Admin, Dir.Comm, Comm, Technico, Experts, Tech.CRM |
| Clients | `/crm/customers/` | `view_customer` | + Caissière, Comptable |
| Contacts | *(sur fiche client)* | `view_contact` | DP/DG/Admin, Dir.Comm, Comm, Technico, Experts, Tech.CRM, Caissière |
| Leads | `/crm/leads/` | `view_lead` | DP/DG/Admin, Dir.Comm, Comm, Technico, Experts |
| Opportunités | `/crm/opportunities/` | `view_opportunity` | + Comptable |
| Produits | `/crm/products/` | `view_product` | DP/DG/Admin, Dir.Comm, Comm, Technico, Experts, Caissière |
| Catégories produits | `/crm/products/categories/` | `view_productcategory` | idem Produits (hors Caissière) |
| **Grille tarifaire & marges** | `/crm/products/margins/` | `view_product` | DP/DG/Admin, Dir.Comm, Comm, Technico, Experts, Caissière |
| Commandes | `/crm/orders/` | `view_order` | DP/DG/Admin, Dir.Comm, Comm, Technico, Experts, Caissière, Comptable |
| Factures (ventes) | `/crm/sales/` | `view_invoice` | + Tech.CRM, Gouvernance |
| Impression facture | `/crm/sales/<id>/print/` | `view_invoice` | idem Factures |
| Support / SAV | `/crm/support/` | `view_supportcase` | DP/DG/Admin, Dir.Comm, Comm, Technico, Experts, Tech.CRM |
| Visites terrain | `/crm/visits/` | `view_visitreport` | idem Support |
| Tâches | `/crm/tasks/` | `view_task` | + Caissière |
| Promotions | `/crm/promotions/` | `view_promotion` | DP/DG/Admin, Dir.Comm, Technico, Experts, Comptable |
| Prévisions | `/crm/forecasts/` | `view_forecast` | DP/DG/Admin, Dir.Comm, Technico, Experts, Comptable |
| Territoires | `/crm/territories/` | `view_territory` | DP/DG/Admin, Technico, Experts |
| Points de vente | `/crm/outlets/` | `view_outlet` | DP/DG/Admin, Technico, Experts, Caissière, Comptable |
| **Stock — Tableau de bord** | `/crm/stock/` | `view_stocklot` | DP/DG/Admin, Dir.Comm, Comm, Technico, Experts, Caissière, Comptable |
| **Stock — Lots** | `/crm/stock/lots/` | `view_stocklot` | idem Stock |
| **Stock — Entrepôts** | `/crm/stock/warehouses/` | `view_warehouse` | DP/DG/Admin, Dir.Comm, Comm, Technico, Caissière, Comptable |
| **Stock — Mouvements** | `/crm/stock/movements/` | `view_stockmovement` | DP/DG/Admin, Dir.Comm, Technico, Caissière, Comptable |
| **Créances âgées** | `/crm/finance/receivables/` | `view_invoice` | DP/DG/Admin, Dir.Comm, Experts, Tech.CRM, Caissière, Comptable, Gouvernance = **encours global** · Comm/Technico = **leur portefeuille uniquement** (données cloisonnées) |
| **Pilotage commercial & financier** | `/crm/performance/` | `view_reports` | DP/DG/Admin, Dir.Comm, Experts Métier, Comptable, Gouvernance |
| **Objectifs commerciaux** | `/crm/targets/` | `view_salestarget` | DP/DG/Admin, Dir.Comm, Comm, Technico, Comptable |
| Routage | `/crm/routing-rules/` | `view_routingrule` | DP/DG/Admin, Tech.CRM |
| Carrières | `/crm/careers/` | `view_careerapplication` | DP/DG/Admin, Tech.CRM |
| Newsletter | `/crm/newsletter/` | `view_newslettersubscription` | DP/DG/Admin, Tech.CRM |
| Gouvernance — Audit | `/crm/governance/audit/` | `view_audittrail` | DP/DG/Admin, Dir.Comm, Tech.CRM, Comptable, Gouvernance |
| Gouvernance — Qualité données | `/crm/governance/data-quality/` | `view_dataqualityissue` | DP/DG/Admin, Dir.Comm, Comm, Technico, Experts, Tech.CRM, Gouvernance |
| Gouvernance — Escalades | `/crm/governance/escalations/` | `view_slaescalation` | idem Qualité données |
| Gouvernance — Approbations | `/crm/governance/approvals/` | `view_approvalrequest` | DP/DG/Admin, Dir.Comm, Comm, Caissière, Comptable, Gouvernance |
| Accès — Comptes utilisateurs | `/crm/access/users/` | `view_user` | DP/DG/Admin **uniquement** |
| Accès — Affectations de rôles | `/crm/access/assignments/` | `view_roleassignment` | DP/DG/Admin, Tech.CRM, Gouvernance |
| Recherche globale | `/crm/search/` | connecté | Tous les utilisateurs connectés |

> **Note « Pilotage »** : l'écran `/crm/performance/` est désormais **réservé** aux profils
> disposant de `view_reports` (Direction/Propriétaire, Direction Générale, Administrateur
> Système, Directeur Commercial, Experts Métier, Comptable, Gouvernance & Conformité). Les
> Commerciaux, Technico-Commerciaux et la Caissière n'y ont **pas** accès : les chiffres
> financiers consolidés (CA global, commissions) restent dans le cercle direction/reporting.
> Le lien de menu correspondant n'apparaît que pour ces profils.

---

## 6. Points d'arbitrage à valider avec la Direction

Quelques droits méritent une décision explicite (laissés en l'état actuel ; à confirmer) :

1. **Pilotage financier consolidé** (`/crm/performance/`) : ✅ **arbitré le 2026-06-22** —
   restreint aux profils `view_reports` (Direction, Dir. Commercial, Experts Métier,
   Comptable, Gouvernance). Plus accessible aux Commerciaux/Technico/Caissière.
2. **Encours & créances** (`/crm/finance/receivables/`) : ✅ **arbitré le 2026-06-22** —
   cloisonnement par portefeuille confirmé. Les **Commerciaux** et **Technico-Commerciaux**
   ne voient que l'encours de **leurs** clients (ceux qui leur sont rattachés : commandes,
   opportunités, tâches, visites) ; les totaux affichés sont eux aussi limités à ce
   périmètre. L'**encours global** reste réservé aux profils direction/finance/reporting
   (`view_reports` / `manage_sales_team` / groupes privilégiés). Comportement déjà assuré
   par `services/access_scope.py::scoped_customers_queryset` ; un badge de portée
   (« Votre portefeuille uniquement » / « Encours global ») a été ajouté à l'écran.
3. **Suppression de données** : seuls DP/DG/Admin peuvent supprimer (clients, factures,
   lots…). C'est volontaire (traçabilité). Ne pas distribuer le droit `delete_*` aux
   profils opérationnels.
4. **Caissière & mouvements de stock** : elle peut **ajouter** des sorties mais pas annuler ;
   toute correction passe par un lot/Dir. Commercial. Confirmer que c'est le bon
   cloisonnement comptoir.

---

## 7. Procédure : attribuer / modifier un rôle

1. **Créer le compte** (si nécessaire) : Admin Système → `/crm/access/users/` ou admin Django.
2. **Rattacher au(x) groupe(s)** correspondant(s) au métier de la personne (un seul rôle
   principal en général ; cumul possible mais à éviter pour rester lisible).
3. **Périmètre optionnel** : via `/crm/access/assignments/` (région, espèce, date de fin).
4. **Vérifier** : se connecter avec le compte (ou demander à la personne) et contrôler que
   seuls les menus attendus apparaissent.
5. **Tout changement de droits structurel** (nouvelle permission, nouveau module) se fait
   dans `setup_roles.py`, suivi de `python manage.py setup_roles`, **puis** mise à jour de
   ce document (incrémenter la version au §0).

---

## Journal des versions
- **v1.0 — 2026-06-22** : création du document, alignée sur `setup_roles.py` après le
  déploiement des 4 modules métier (stock/lots, crédit/créances, prix-marge, objectifs).
- **v1.1 — 2026-06-22** : arbitrage §6.1 appliqué — le **Pilotage commercial & financier**
  (`/crm/performance/`) passe de `view_dashboard` à `view_reports` (réservé Direction /
  Dir. Commercial / Experts Métier / Comptable / Gouvernance) ; menu et matrice mis à jour.
- **v1.2 — 2026-06-22** : arbitrage §6.2 appliqué — **créances** cloisonnées par portefeuille
  pour Commerciaux/Technico (encours global réservé direction/finance/reporting) ; badge de
  portée ajouté à l'écran `/crm/finance/receivables/`. Comportement déjà porté par
  `scoped_customers_queryset`, rendu explicite et documenté.
