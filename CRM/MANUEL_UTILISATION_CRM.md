# Manuel d'utilisation — CRM MARIDAV Côte d'Ivoire

> Document de formation du personnel. Tenu à jour à chaque évolution du logiciel.
> Langue : français · Devise : FCFA (XOF).

**Adresse du logiciel :** https://maridav.tech-and-web.net/crm/
**Accès :** chaque employé reçoit un identifiant et un mot de passe personnels. Ne jamais
partager ses identifiants. En cas d'oubli, contacter l'administrateur.

---

## Journal des versions du manuel

| Date | Version | Évolution |
|------|---------|-----------|
| 2026-06-22 | v1.0 | Création du manuel. Module **Stock, lots & péremption** (Phase 1). |
| 2026-06-22 | v1.1 | Module **Encours crédit & créances âgées** (Phase 2). |
| 2026-06-22 | v1.2 | Module **Prix par segment & marge** (Phase 3). |
| 2026-06-22 | v1.3 | Module **Objectifs commerciaux & tableau de bord financier** (Phase 4). |

---

## 1. Présentation générale

Le CRM MARIDAV est l'outil unique de gestion de la relation client, des ventes et de
l'activité commerciale. Il accompagne tout le métier de MARIDAV : **fabrication et
distribution d'aliments et d'additifs** pour les **volailles**, **porcs** et **poissons**,
ainsi que les produits de **biosécurité**.

### 1.1 Se connecter
1. Ouvrir https://maridav.tech-and-web.net/crm/
2. Saisir son identifiant et son mot de passe.
3. Cliquer sur **Se connecter**.

### 1.2 Comprendre l'écran
- À gauche : le **menu** (les rubriques visibles dépendent de votre rôle).
- En haut : des **raccourcis** (nouveau client, lead, commande, vente…).
- Au centre : le **contenu** de la rubrique choisie.

### 1.3 Les rôles (qui voit quoi)
Chaque employé appartient à un ou plusieurs **rôles** qui déterminent ce qu'il peut voir
et faire. Principaux rôles : Direction, Administrateur Système, Directeur Commercial,
Commerciaux, Technico-Commerciaux, Experts Métier, Caissière, Comptable, Support
Technique, Gouvernance & Conformité. Si une rubrique n'apparaît pas dans votre menu,
c'est qu'elle n'est pas dans votre périmètre.

---

## 2. Module Stock, lots & péremption  *(Phase 1)*

> **À quoi ça sert ?** Savoir, à tout moment, **combien de produit on a, où, et jusqu'à
> quand il est consommable**. Indispensable pour des aliments et additifs périssables :
> éviter les ruptures, écouler les lots les plus anciens en premier, et ne jamais vendre
> un produit périmé.

### 2.1 Les 3 notions clés
- **Entrepôt** : un lieu de stockage (usine, dépôt central, magasin / point de vente).
- **Lot** : une quantité d'un produit donné, reçue ou fabriquée en une fois, identifiée
  par un **numéro de lot** et une **date de péremption (DLUO)**. Le stock se suit lot par
  lot pour garantir la traçabilité.
- **Mouvement** : toute variation de stock d'un lot (entrée, sortie, ajustement, perte).
  Le stock d'un lot n'évolue **jamais à la main** : il évolue uniquement par des
  mouvements, ce qui laisse une trace complète.

### 2.2 Vue d'ensemble du stock
Menu **Stock (vue d'ensemble)**. On y voit en un coup d'œil :
- le nombre de lots et la **valeur du stock** (au coût) ;
- les **produits en alerte de rupture** (sous leur seuil) ;
- les **lots périmés** (en rouge) et ceux qui **périment sous 30 jours** (en orange) ;
- les **derniers mouvements**.

C'est l'écran à consulter chaque matin par le responsable de dépôt.

### 2.3 Créer un entrepôt
*(Rôles : Direction / Administrateur Système.)*
1. Menu **Entrepôts** → **Nouvel entrepôt**.
2. Renseigner le **nom**, un **code** court et unique (ex. `DEPOT-ABJ`), le **type**, la
   ville/région et, si possible, le **responsable**.
3. **Enregistrer**.

### 2.4 Créer un lot (réception ou production)
*(Rôles : Directeur Commercial, Administrateur Système, Direction.)*
1. Menu **Lots de stock** → **Nouveau lot**.
2. Choisir le **produit** et l'**entrepôt**.
3. Saisir le **N° de lot** (celui imprimé sur le sac/emballage), l'**unité** (sac, kg,
   tonne…) et la **quantité reçue**.
4. Renseigner le **coût unitaire** (pour la valorisation du stock), la **date de
   fabrication** et surtout la **date de péremption (DLUO)**.
5. **Enregistrer**. ➜ Le logiciel crée automatiquement une **entrée de stock** égale à la
   quantité reçue.

> 💡 Une fois le lot créé, la **quantité reçue ne se modifie plus** : tout changement de
> stock passe par un mouvement (voir 2.5).

### 2.5 Enregistrer un mouvement de stock
*(Sortie de marchandise, ajustement d'inventaire, perte…)*
1. Menu **Mouvements stock** → **Nouveau mouvement**
   *(ou, depuis la liste des lots, bouton **Mouvement** sur la ligne du lot).*
2. Choisir le **lot** concerné.
3. Choisir le **type** :
   - **Entrée** : réception ou production supplémentaire (augmente le stock).
   - **Sortie** : vente / livraison au client (diminue le stock).
   - **Ajustement d'inventaire** : on saisit la **quantité réellement comptée** ; le
     logiciel ajuste le solde à cette valeur (à utiliser après un inventaire physique).
   - **Perte / casse / péremption** : diminue le stock pour une marchandise détruite.
   - **Transfert sortant / entrant** : déplacement entre deux entrepôts.
4. Saisir la **quantité** et un **motif** clair.
5. (Facultatif) Lier une **commande** ou une **facture**.
6. **Enregistrer**.

> ⚠️ Le logiciel **refuse une sortie supérieure au stock disponible** du lot : on ne peut
> pas avoir un stock négatif. Si le message « Stock insuffisant » apparaît, vérifier le
> lot ou faire d'abord une entrée.

### 2.6 Gérer les péremptions (règle DLUO)
- Vendre/livrer **en priorité les lots dont la péremption est la plus proche** (premier
  périmé, premier sorti).
- Les lots **périmés** doivent être **sortis** du stock disponible via un mouvement
  **Perte / péremption**, jamais vendus.
- Le seuil d'alerte rupture se règle **produit par produit** (champ « Seuil d'alerte
  stock » dans la fiche produit) : en dessous, le produit remonte dans les alertes.

### 2.7 Bonnes pratiques
- **Saisir les réceptions le jour même**, avec le vrai n° de lot et la vraie DLUO.
- **Faire les sorties au moment de la livraison**, pas après coup.
- **Inventaire physique régulier** → corriger via un mouvement **Ajustement**.
- Ne jamais « bricoler » une quantité : passer par un mouvement, c'est ce qui protège la
  fiabilité des chiffres et la traçabilité.

---

## 3. Module Encours crédit & créances âgées  *(Phase 2)*

> **À quoi ça sert ?** Savoir **combien chaque client nous doit**, depuis **combien de
> temps**, et **qui dépasse son plafond de crédit**. C'est le nerf de la trésorerie :
> vendre à crédit, oui, mais sous contrôle.

### 3.1 Les notions clés
- **Plafond de crédit** : montant maximum d'encours autorisé pour un client. `0` = aucun
  crédit (paiement comptant obligatoire).
- **Délai de paiement** : nombre de jours accordés pour régler une facture (ex. 30 jours).
- **Encours** : total des factures **émises et non encore soldées** d'un client.
- **Balance âgée** : répartition de l'encours selon l'ancienneté du retard — *Courant*
  (pas encore échu), *1-30 j*, *31-60 j*, *61-90 j*, *plus de 90 j*.
- **Compte bloqué** : interrupteur manuel pour signaler « ne plus livrer à crédit ».

### 3.2 Définir les conditions de crédit d'un client
*(Rôles : Direction, Directeur Commercial, Administrateur Système.)*
1. Ouvrir la fiche client → **Modifier**.
2. Section **Conditions de crédit** : renseigner le **plafond**, le **délai de paiement**,
   et cocher **Compte bloqué** si le client doit être gelé.
3. **Enregistrer**.

### 3.3 Lire l'encours sur une fiche client
La fiche client affiche un panneau **Crédit & encours** :
- Plafond, **encours actuel**, **crédit disponible** (vert = il reste de la marge, rouge =
  dépassement), délai de paiement.
- La **balance âgée** détaillée et le **total en retard**.
- Un bandeau rouge **« Plafond dépassé »** ou **« Compte bloqué »** apparaît si besoin.

> 💡 **Avant de livrer à crédit**, vérifier le panneau : si le crédit disponible est
> négatif ou le compte bloqué, escalader au Directeur Commercial (procédure d'exception
> de crédit déjà prévue dans les commandes).

### 3.4 Suivre toutes les créances : la page « Créances »
*(Rôles : Direction, Directeur Commercial, Comptable, Caissière…)* — menu **Créances**.
- Cartes de synthèse : **encours total**, **en retard**, **retard > 90 jours**, nombre de
  clients concernés.
- Tableau par client avec la balance âgée, l'encours, le plafond, et les badges
  **Bloqué / Plafond dépassé**.
- Filtres rapides : **Tous**, **En retard**, **Plafond dépassé / bloqués**.
- La ligne **Total** en bas donne la balance âgée globale de l'entreprise.

### 3.5 Bonnes pratiques de recouvrement
- Revoir la page **Créances** chaque semaine ; **traiter en priorité la colonne > 90 j**.
- Encaisser une facture met automatiquement à jour l'encours (enregistrer le paiement sur
  la facture concernée).
- Un client qui dépasse son plafood doit **régulariser avant toute nouvelle livraison à
  crédit** ; sinon, basculer en **paiement comptant** ou activer **Compte bloqué**.

---

## 4. Module Prix par segment & marge  *(Phase 3)*

> **À quoi ça sert ?** Vendre **au bon prix selon le type de client** (un distributeur
> n'achète pas au même tarif qu'un éleveur direct) et **piloter la marge** pour ne jamais
> vendre à perte.

### 4.1 Les notions clés
- **Prix de vente de référence** : le tarif par défaut d'un produit.
- **Coût de revient** : ce que le produit coûte à MARIDAV (achat/production). Sert au
  calcul de la marge.
- **Marge** : prix de référence − coût de revient (en FCFA et en %).
- **Grille tarifaire par segment** : un prix dédié par **type de client** (distributeur,
  éleveur, intégrateur, vétérinaire, revendeur, industrie). Si un segment n'a pas de prix
  dédié, c'est le prix de référence qui s'applique.

### 4.2 Renseigner coût et prix d'un produit
*(Rôles : Direction, Directeur Commercial, Administrateur Système.)*
1. Menu **Produits** → ouvrir un produit (**Mettre à jour**) ou **Nouveau produit**.
2. Renseigner le **prix de vente de référence** et le **coût de revient**.
3. (Facultatif) Régler le **seuil d'alerte stock** (utilisé par le module Stock).
4. **Enregistrer**.

### 4.3 Définir des prix par segment
Dans la fiche produit, section **Grille tarifaire par type de client** :
1. Choisir un **type de client** et saisir son **prix unitaire**.
2. Ajouter autant de lignes que de segments à différencier (laisser vide = prix de
   référence).
3. **Enregistrer**. Pour retirer un tarif, cocher **Supprimer** sur sa ligne.

### 4.4 Lire les marges : la page « Marges »
Menu **Produits** → bouton **Marges**. On y voit :
- la **marge moyenne** des produits ayant un coût renseigné ;
- le nombre de **produits sans coût de revient** (à compléter pour fiabiliser l'analyse) ;
- pour chaque produit : coût, prix, **marge en FCFA et en %** (rouge si négative), et les
  **tarifs par segment** existants.

La liste **Produits** affiche désormais aussi le coût, la marge % et le **stock
disponible** de chaque produit.

### 4.5 Bonnes pratiques
- **Renseigner le coût de revient de tous les produits actifs** : sans coût, pas de marge
  fiable.
- Revoir les **prix par segment** à chaque évolution tarifaire (hausse matières
  premières, négociation distributeur).
- Une **marge négative** (rouge) = alerte : prix trop bas ou coût mal saisi, à corriger.

---

## 5. Module Objectifs commerciaux & tableau de bord financier  *(Phase 4)*

> **À quoi ça sert ?** Fixer un **objectif de chiffre d'affaires à chaque commercial**,
> suivre en temps réel **où il en est**, calculer sa **commission**, et donner à la
> direction une **vue financière consolidée** (CA, encours, top produits).

### 5.1 Les notions clés
- **Objectif commercial** : un montant de CA à réaliser par un **commercial**, pour un
  **mois donné**, éventuellement par **espèce** (volailles, porcs…).
- **Réalisé** : le CA effectivement facturé par ce commercial sur la période (factures
  émises / partiellement payées / payées dont il est le **commercial responsable**).
- **Atteinte** : réalisé ÷ objectif, en %.
- **Commission** : réalisé × taux de commission de l'objectif.

### 5.2 Définir un objectif
*(Rôles : Direction, Directeur Commercial.)* — menu **Objectifs commerciaux** → **Nouvel
objectif**.
1. Choisir le **commercial**, l'**année** et le **mois**.
2. (Facultatif) restreindre à une **espèce** et/ou un **territoire**.
3. Saisir l'**objectif de CA**, éventuellement un **objectif de volume** et un **taux de
   commission**.
4. **Enregistrer**.

> 💡 Un seul objectif par commercial, par mois et par espèce. Pour un objectif « toutes
> espèces », laisser le champ espèce vide.

### 5.3 Suivre les objectifs
Menu **Objectifs commerciaux** : liste filtrable par année/mois, avec pour chaque
commercial l'**objectif**, le **réalisé**, une **barre d'atteinte** colorée (vert ≥ 100 %,
bleu ≥ 60 %, orange en dessous) et la **commission estimée**.

### 5.4 Le tableau de bord « Pilotage commercial »
*(Rôles : Direction, Directeur Commercial, Comptable…)* — menu **Pilotage commercial**.
Sélectionner une **période** (année/mois) pour afficher :
- **CA du mois**, **CA cumulé de l'année**, **encours total**, **créances en retard** ;
- un **graphe d'évolution** du CA mois par mois ;
- le tableau **Objectifs des commerciaux** (réalisé, atteinte, écart, commission) ;
- **CA par commercial**, **CA par espèce**, et le **Top produits** de la période.

### 5.5 Comment le CA est rattaché à un commercial
Le réalisé d'un commercial provient des **factures dont il est le commercial responsable**
(`Commercial responsable` sur la facture/vente). Pour que le pilotage soit juste, **toujours
renseigner le commercial responsable** lors de la création d'une vente ou d'une facture.

### 5.6 Bonnes pratiques
- **Fixer les objectifs en début de mois** pour toute l'équipe.
- Vérifier le **Pilotage commercial** chaque semaine et recadrer les commerciaux sous
  60 % d'atteinte.
- Croiser **CA et encours** : un fort CA avec un encours qui explose n'est pas une bonne
  performance — la trésorerie prime.

---

*Manuel à jour des 4 modules livrés. À enrichir à chaque nouvelle évolution du logiciel.*
