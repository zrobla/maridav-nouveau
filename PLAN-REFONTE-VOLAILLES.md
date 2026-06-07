# Plan de refonte — Architecture produits « Volailles » (MARIDAV CI)
> Document de travail à exécuter à la prochaine session. Rédigé après analyse de
> `volailles.html`, `poulets_chair_maridav_ci.html`, `pondeuses_maridav_ci.html` et du
> catalogue produits volailles. Objectif : une présentation **premium, intuitive et
> réutilisable** qui fait comprendre l'offre Maridav (par **espèce → filière → type →
> phase / taux**) et permet à chaque visiteur de **trouver son produit en < 30 s**.

---

## 0. Périmètre — un système complet, pas seulement le haut niveau
Cette refonte est un **« tout meilleur »** qui traite **les 3 étages d'un même parcours** :
1. **Hub** `volailles.html` — aiguillage filière + pédagogie.
2. **Pages filière** `poulets_chair` / `pondeuses` — frise du cycle, tableau « je fabrique ».
3. **Pages produits** (aliments, concentrés, prémix, additifs) — **gabarit unifié + enrichi**
   (§4.3) **et conversion des pages legacy** (§4.4). Elles montent au **même niveau premium**
   et s'intègrent au maillage (mini-frise « où je suis dans le cycle », produits liés, badges).

> **Ordre d'exécution** : on commence par **les pages produits** (étape 1 du §7) — elles sont
> le socle de données et de design qui alimente ensuite les pages filière et le hub.

---

## 1. Le problème métier (ce qu'on doit résoudre)

Maridav vend la nutrition animale **par espèce ET par cycle de production**. Pour les
volailles, deux **filières** distinctes qui ne se confondent jamais dans la tête de
l'éleveur :

- **Poulet de chair** (viande) — cycle court, objectif poids/FCR/carcasse.
- **Pondeuse** (œufs) — cycle long, objectif uniformité → pic de ponte → persistance.

Et pour chaque filière, l'offre se décline sur **3 dimensions** que le site doit rendre
limpides :

| Axe | Valeurs | Sert à répondre à la question… |
|---|---|---|
| **Phase du cycle** | chair : Démarrage 0-14 j · Croissance 15-28 j · Finition 29 j+ <br> ponte : Pré-démarrage 0-5 j · Démarrage 0-6 sem · Poulette 7-18 sem · Pré-ponte · Ponte 1 · Ponte 2 | « Mon lot a X jours, que lui donner **maintenant** ? » |
| **Type de produit** | Aliment complet · Concentré · Macro-prémix · Prémix · Additif/biosécurité | « Est-ce que **j'achète prêt à l'emploi** ou **je fabrique** ? » |
| **Taux d'inclusion (%)** | concentrés 5 / 12,5 / 31 % · macro-prémix 1,5 / 1,7 / 2 % · prémix 0,25 % | « Avec quel **taux** je complète mes matières premières ? » |

> **Insight central** : l'éleveur n'arrive pas en pensant « type de produit ». Il pense
> **« ma filière + l'âge de mon lot »**, puis seulement ensuite **« mode d'achat »**
> (prêt à l'emploi vs fabrication). L'architecture doit suivre **ce parcours mental**,
> pas l'organigramme interne du catalogue.

---

## 2. État des lieux (analyse de l'existant)

### 2.1 Ce qui fonctionne déjà (à garder)
- Le **hub `volailles.html`** sépare bien les 2 filières (« Choisissez votre filière »)
  et décrit les cycles (« Stades clés poulets de chair » / « Cycle pondeuses »).
- Les 2 sous-pages utilisent un système **onglets par type** (Aliments / Concentrés /
  Macro-prémix / Prémix / Additifs) avec des **badges de phase** sur les cartes
  (`Démarrage 0-14 j`, `7–18 semaines`…). La logique est là.
- Pages produits individuelles existantes (1 page par produit) + JSON-LD `Product`.

### 2.2 Ce qui pose problème (à corriger)

1. **Produits transversaux mal signalés** *(priorité haute — clarifié avec Maridav)*
   - Les **concentrés** et **macro-prémix** (« Concentré 31 / 12,5 / 5 % », « Macro Prémix
     2 / 1,7 % ») sont **volontairement transversaux** : utilisables en **chair ET en
     ponte**. Ce n'est **pas** une erreur. De même, **`Profish`** est **bien à sa place**
     (offre complémentaire validée par Maridav — à conserver).
   - **Le vrai problème = l'absence de signal.** Rien n'indique au visiteur que ces
     produits sont **partagés entre filières**. Sur une page « pondeuses », un libellé
     « Concentré **Chair** 31 % » lu sans contexte sème le doute (« est-ce vraiment pour
     mes pondeuses ? »).
   - → **Fix** : (a) un **marquage explicite « Transversal — chair & ponte »** sur ces
     produits ; (b) **dé-spécifier le nom** des concentrés/prémix transversaux (« Concentré
     31 % » plutôt que « Concentré **Chair** 31 % ») ; (c) les regrouper dans la section
     « Je fabrique mon aliment » (cf. §4.2-B), identique sur les deux filières.

2. **Asymétrie entre les deux pages**
   - Chair : ~7 produits, onglet Concentrés = **1** carte.
   - Ponte : **22** produits en vrac, onglets surchargés.
   - → Même filière-mère, traitement visuel incohérent.

3. **Le cycle de production n'est pas exploité comme colonne vertébrale**
   - Il est en **texte** sur le hub et en **badges** isolés sur les cartes, mais il n'y a
     **aucune frise / parcours visuel** qui relie *« âge du lot → produit recommandé »*.
     C'est pourtant **le** repère naturel de l'éleveur.

4. **Aucune aide au choix « mode de production »**
   - Rien n'explique la différence **Aliment complet** (prêt) vs **Concentré / Prémix**
     (à mélanger), ni **quel taux pour qui**. Or c'est la 1ʳᵉ question d'un éleveur qui
     fabrique son aliment.

5. **Cartes produits pauvres**
   - Titre + 1 phrase + bouton. Pas de **specs clés** (protéine, énergie, âge cible,
     présentation granulé/farine, conditionnement) → l'éleveur ne peut pas comparer.

6. **Présentation = grille de cartes**, pas les « tableaux organisés » voulus. Pas de
   **vue comparative** (tableau) ni de **filtres**.

---

## 3. La cible : modèle de données produit (à formaliser)

Avant tout HTML, figer **un seul modèle** (servira aussi à porcs/poissons). Chaque produit
= un objet avec ces champs :

```
produit:
  slug:            aliment-chair-demarrage
  nom:             "Aliment Chair Démarrage"
  filieres:        [volailles-chair]      # LISTE. Aliment complet = 1 filière. Concentré/prémix/certains additifs = TRANSVERSAUX -> [volailles-chair, volailles-ponte] (voire porcs/poissons)
  transversal:     false                  # true = produit partagé entre filières (concentrés, macro-prémix, prémix, Profish…) -> affiché sur chaque filière avec badge "Transversal"
  type:            aliment-complet        # aliment-complet | concentre | macro-premix | premix | additif
  phase:           demarrage              # demarrage | croissance | finition | poulette | pre-ponte | ponte-1 | ponte-2 | pre-demarrage | (null pour transversaux/additifs)
  age_cible:       "0 – 14 jours"
  taux_inclusion:  null                   # ex "31 %" pour concentrés/prémix, null pour aliment complet
  presentation:    "Granulé fin (miette)" # miette | granulé | farine | liquide | gel
  conditionnement: "Sac 50 kg"            # PUBLIABLE (source Maridav) -> à afficher sur cartes + page produit
  benefice_cle:    "Sécurise le poids moyen au démarrage"
  specs:           { proteine: "…", energie: "…", calcium: "…", phosphore: "…" }   # PUBLIABLE -> bloc specs sur la page produit (valeurs exactes à fournir par Maridav)
  fonction:        null                   # pour additifs: "anti-mycotoxines" | "anti-chaleur" | "santé intestinale" | "biosécurité"
  url:             aliment_chair_demarrage_maridav_ci.html
  image:           …
```

> ✅ **Déjà amorcé** : `products-volailles.json` (à la racine) contient le catalogue volailles
> **extrait du site** (aliments complets avec protéine/énergie, concentrés/macro-prémix/prémix
> avec taux + conditionnement, additifs par fonction, filières + flag `transversal`). C'est la
> source de vérité de départ — à compléter (cf. `_meta.a_verifier`) puis figer.

**Recommandation forte** : externaliser ce catalogue dans **un seul `products.json`** (ou
un bloc de données en tête de page) et **générer les pages volailles depuis ces données**
(comme on le fait sur d'autres projets via script de build). Bénéfices : zéro doublon,
cohérence garantie, `sitemap`/JSON-LD/`llms.txt` synchronisés, et un produit ne peut plus
« atterrir » sur la mauvaise filière. *(À valider — sinon, refonte manuelle page par page
en respectant strictement le modèle ci-dessus.)*

---

## 4. Architecture proposée (premium, « refactor & enhance »)

### 4.1 Hub `volailles.html` — « Quelle est votre filière ? »
Rôle : **aiguillage** + pédagogie de haut niveau. Ne PAS lister les produits ici.
- **Hero** : promesse volailles (déjà bon).
- **2 grandes cartes filière** (chair / ponte) — visuelles, avec mini-frise du cycle en
  aperçu et CTA « Voir les programmes ».
- **Bloc « Comment ça marche »** : 3 étapes (1. Je choisis ma filière → 2. Je repère la
  phase de mon lot → 3. Je choisis aliment complet **ou** concentré/prémix selon mon mode).
- Réassurance (appui technique, biosécurité, partenaires) + CTA devis.

### 4.2 Page filière (chair / ponte) — **le cœur de la refonte**
Structure recommandée, de haut en bas :

**A. La frise du cycle de production (composant signature)** 🆕
> Une **timeline horizontale** des phases, cliquable. C'est l'élément « waouh » et le plus
> utile : l'éleveur clique sur la phase correspondant à l'âge de son lot et voit
> immédiatement le(s) produit(s) recommandé(s).

```
 CHAIR   ●───────────●───────────●
       Démarrage   Croissance   Finition
        0-14 j      15-28 j      29 j+
        ▼            ▼            ▼
     [Aliment      [Aliment     [Aliment
      Démarrage]    Croissance]  Finition]

 PONTE   ●─────●─────────●─────────●────────●────────●
      Pré-dém  Démarrage  Poulette  Pré-ponte Ponte 1  Ponte 2
       0-5 j   0-6 sem    7-18 sem    …        pic     persistance
```
- Chaque jalon = phase + âge + produit complet associé (carte enrichie au clic/scroll).
- Barre de progression colorée (vert marque) façon « parcours ».
- 100 % responsive : devient **verticale** en mobile (frise → liste d'étapes).

**B. Sélecteur « Mode de production »** 🆕
> Deux onglets clairs qui répondent à « j'achète prêt OU je fabrique » :
- **« Aliment complet — prêt à l'emploi »** → la gamme par **phase** (la frise ci-dessus).
- **« Je fabrique mon aliment »** → **Concentrés / Macro-prémix / Prémix**, présentés en
  **tableau comparatif par taux d'inclusion** (colonne : produit · taux % · pour quel
  stade · présentation · **conditionnement** · note d'emploi). C'est ici que « tableau
  organisé » prend tout son sens.
  - **Ces produits sont transversaux** (chair & ponte) : afficher un **badge
    « Transversal — chair & ponte »** et présenter **la même section sur les deux pages
    filière**, avec un nommage neutre (« Concentré 31 % », pas « Concentré Chair 31 % »).
    L'éleveur comprend qu'il achète un même concentré quel que soit son atelier.

**C. Additifs & biosécurité — par FONCTION (pas par phase)** 🆕
> Les additifs sont transversaux. Les présenter par **bénéfice** :
santé intestinale · anti-mycotoxines · anti-stress thermique · qualité d'eau · désinfection.
Chips/filtres cliquables. (Retirer les additifs qui ne concernent pas la filière.)

**D. Tableau récapitulatif filtrable (vue « catalogue »)** 🆕 *(optionnel mais premium)*
> Un **tableau unique** de tous les produits de la filière avec **filtres** (type, phase,
> taux) et **recherche**. Pour l'éleveur pressé / le revendeur. Colonnes : Produit · Type ·
> Phase/Âge · Taux · Présentation · Action.

**E. Réassurance + CTA** : « Pas sûr du bon programme ? Parlez à un technicien » → WhatsApp.

### 4.3 Page produit (gabarit unifié) — enrichir
Chaque produit doit afficher : badge filière + badge phase/taux · présentation (granulé…) ·
**bloc specs** (protéine, énergie, Ca/P, âge) · bénéfices · **« où il se situe dans le
cycle »** (mini-frise avec la phase en surbrillance) · **produits de la phase suivante**
(cross-sell logique) · conditionnement · CTA devis. JSON-LD `Product` complété.

### 4.4 Conversion des pages produits « legacy » 🔴 *(phase obligatoire)*
**Constat** : toutes les pages produits ne sont pas au même niveau. Certaines (ex.
`chickcare.html`) ont reçu le **redesign de référence** ; d'autres sont restées sur une
**ancienne architecture** issue d'une conversion ratée d'un ancien site **PHP** — structure
pauvre (« Nous distribuons ce produit pour… », « Autres produits relatifs ») **et liens
cassés** (`about.php.html`, `contact.php.html`, `anh.php.html`, `macropremix_chair_2%25.html`…).

**Gabarit de référence = `chickcare.html`** — toute page produit doit suivre cette ossature :
1. Hero produit (nom + badges filière/phase ou taux) · 2. **Bénéfices clés** · 3. **Élevages /
stades ciblés** · 4. **Tableau de composition indicative** (specs : énergie, protéine, Ca/P…) ·
5. **Programme / mode d'emploi** (phase ou taux d'inclusion) · 6. **Disponibilité Côte d'Ivoire**
+ conditionnement · 7. **Briefing express (48 h)** / CTA devis · 8. **FAQ** · 9. **Termes clés**
· 10. **Produits liés** (phase suivante / même filière) · JSON-LD `Product` valide · 1 `<h1>`.

**8 pages à convertir** (= toute la gamme « Je fabrique » — concentrés/macro-prémix/prémix) :
`concentre_chair_31` · `chair_12_5` · `chair_05` · `maxiponte_5` · `macropremix_chair_1_7` ·
`macropremix_pondeuses_1_7` · `premix_chair_0_25_maridav_ci` · `premix_ponte_0_25_maridav_ci`.

**À traiter dans la même passe :**
- **Réparer TOUS les liens cassés** (legacy `.php.html`, `%25`, `trouwnutrition.html`,
  `macropremix_pondeuses_2%.html`) — y compris les 3 résiduels repérés sur des pages neuves
  (`aliments_chair_finition`, `chickcare`, `aliment_demarrage_ponte`, `aliment_ponte_2`).
- **Compléter les 2 stubs** `macropremix_chair_2%` et `macropremix_pondeuse_2%` (~8 Ko, vides).
- **Renommer** le fichier piège `macropremix_chair_2%.html` (le `%` casse les URLs) → slug
  propre (ex. `macropremix-chair-2pct.html`) + maj des liens + sitemap.
- Remplir specs/conditionnement depuis `products-volailles.json` ; **badge transversalité**
  (chair & ponte) sur les concentrés/prémix.

> Règle : **aucune page produit ne doit rester sur l'ancienne architecture**. Le gabarit
> `chickcare` (extrait en template réutilisable) devient le standard unique des pages produits.

**Specs techniques d'exécution (debt-proof) :**
- **CSS du gabarit** = `assets/css/product-premium.css` (+ `css/style.css`, `responsive.css`,
  `assets/css/main.min.css`) → chaque page convertie doit lier ces feuilles.
- **Structure de section** = `premium-hero` puis `section-spacing` / `section-spacing bg-white`
  en alternance (cf. squelette `chickcare`).
- **Liens cassés `.php.html`** = vestiges d'un ancien header/footer anglais (About us, Animal/
  Human Nutrition & Health, Gallery…). **Fix = remplacer header + footer par le chrome standard
  de `chickcare`** (navbar-premium + footer actuels) → les 6 liens morts disparaissent d'un
  coup. **Ne pas mapper un par un.**
- **Liens « autres produits relatifs »** (`macropremix_chair_2%25.html` = `%`-encodé) → pointer
  vers le **slug propre renommé** ; vérifier que chaque cible existe.
- **Données** = `products-volailles.json` (specs, conditionnement, taux, transversalité).

**DoD par page (checklist, à 100 % avant de passer à la suivante) :**
`[ ]` chrome standard (header/footer chickcare) · `[ ]` sections au gabarit · `[ ]` specs +
conditionnement remplis · `[ ]` badge filière/phase ou taux (+ transversal si concerné) ·
`[ ]` mini-frise « où dans le cycle » + produits liés · `[ ]` **0 lien cassé** (scan) ·
`[ ]` JSON-LD `Product` valide · `[ ]` 1 `<h1>` · `[ ]` rendu vérifié desktop + mobile.

---

## 5. Composants design à créer (premium, cohérents avec le nouveau site)
Tous dans le langage déjà posé (navy/vert marque, filets d'accent, cartes éditoriales,
puces ▹, CTA pilule à flèche, sûr GPU mobile : pas de `backdrop-filter`/`:has()` lourd) :
1. **`cycle-timeline`** : frise de phases horizontale → verticale en mobile, jalons
   cliquables, barre de progression.
2. **`mode-switch`** : gros toggle « Prêt à l'emploi / Je fabrique ».
3. **`product-matrix`** : tableau comparatif responsive (devient cartes empilées en mobile)
   avec filtres chips + recherche (JS vanilla léger, comme le carrousel partenaires).
4. **`product-card-rich`** : carte produit avec badges (phase/taux), specs condensées,
   présentation, CTA.
5. **`function-filter`** : chips de filtrage des additifs par bénéfice.
6. **`phase-locator`** : mini-frise réutilisable sur les pages produits.

---

## 6. SEO & cohérence (à intégrer dès la conception)
- 1 `<h1>`/page ; `BreadcrumbList` Accueil → Volailles → Filière → Produit.
- `Product` JSON-LD enrichi (corriger le `price` « Sur devis » invalide déjà repéré).
- **Maillage interne** : hub ↔ filières ↔ produits ↔ phase suivante ↔ additifs liés.
- Vocabulaire de recherche réel (« aliment poulet chair démarrage prix Côte d'Ivoire »,
  « concentré ponte 5% », « provende pondeuse ») dans titres/alts/`llms.txt`.
- Mettre à jour `sitemap.xml` / `llms.txt` après refonte.

---

## 7. Plan d'exécution (étapes pour la prochaine session)
> **Ordre voulu** : on **convertit/répare d'abord les pages produits** (le socle), car leurs
> données et leur gabarit alimentent ensuite les pages filière et le hub.

0. *(Prérequis — fait cette session)* `products-volailles.json` extrait + modèle de données (§3).
   Reste à compléter `_meta.a_verifier` et homogénéiser la transversalité (§8-8).
1. 🔴 **PREMIÈRE TÂCHE — Pages produits au standard unique.** Extraire le gabarit
   `chickcare` en **template réutilisable**, puis **CONVERTIR les 8 pages legacy** (§4.4),
   **réparer TOUS les liens cassés**, **compléter les 2 stubs**, **renommer**
   `macropremix_chair_2%.html`. Remplir specs/conditionnement depuis `products-volailles.json`
   + **enrichir chaque fiche** (mini-frise phase, produits liés, badge transversal).
   → *Aucune page produit ne reste sur l'ancienne archi ; toutes prêtes à être maillées.*
2. **Construire les composants IA** (§5) — frise du cycle, mode-switch, tableau filtrable —
   sur la filière pilote (chair).
3. **Refondre `poulets_chair`** : frise du cycle + mode-switch + tableau « je fabrique » +
   additifs par fonction (s'appuie sur les pages produits déjà converties à l'étape 1).
4. **Refondre `pondeuses`** sur le même gabarit (transversaux signalés, **Profish conservé**).
5. **Refondre le hub `volailles`** (aiguillage + « comment ça marche »).
6. **SEO** (JSON-LD, breadcrumb, sitemap, llms) + **QA responsive** + **scan final 0 lien cassé**.
7. **Généraliser** le pattern à **porcs** et **poissons** (même architecture, mêmes étapes).
8. Étude de cas Tech & Web (portfolio) une fois la filière volailles livrée.

---

## 8. Décisions Maridav

### ✅ Tranché (intégré au plan)
1. **Concentrés / macro-prémix = TRANSVERSAUX** (chair **et** ponte). → taxonomie
   `filieres: [liste]` + badge « Transversal », nommage neutre (§2.2-1, §3, §4.2-B).
2. **Specs PUBLIABLES** (protéine, énergie, Ca/P, âge). → bloc specs sur page produit (§4.3).
3. **Conditionnements PUBLIABLES**. → affichés sur cartes + tableau + page produit.
4. **`Profish` reste** (offre complémentaire validée). → conservé, pas un défaut.

### ✅ Récupéré depuis le site → `products-volailles.json`
5. **Specs + conditionnements + filières** sont **déjà sur les pages produits** et ont été
   **extraits** dans **`products-volailles.json`** : protéine/énergie des aliments complets,
   conditionnements (Sac 50 / 25 / 17 kg), taux d'inclusion des concentrés/prémix, et la
   **carte produit → filière(s)** déduite des liens des pages d'espèces (9 transversaux
   détectés). Plus besoin de demander ces données à Maridav. Quelques cases à compléter
   (nutricool, profish, kg de 2 macro-prémix) — voir `_meta.a_verifier` du JSON.

### ⏳ Encore à confirmer (non bloquant)
6. **Prix** : « sur devis » partout ? (si oui, retirer la valeur `price` invalide du JSON-LD).
7. **Gamme à jour ?** Produits volailles manquants sur le site, ou obsolètes à retirer ?
8. **Transversalité à homogénéiser** : les liens actuels **sous-référencent la page CHAIR**
   (ses concentrés/prémix n'apparaissent que via la page ponte). Maridav a validé le
   principe transversal → compléter `filieres` en `[volailles-chair, volailles-ponte]` pour
   ces produits et les afficher symétriquement.

---

## 9. Définition de « terminé » (Definition of Done)
- Un éleveur trouve **son** produit en partant de **filière + âge du lot** sans connaître le
  jargon « concentré/prémix ».
- Un éleveur **fabricant** comprend quel concentré/prémix et à quel taux, via un **tableau**.
- **Produits transversaux clairement signalés** (badge « chair & ponte », nommage neutre),
  affichés à l'identique sur les deux filières ; chair et ponte **symétriques** et cohérentes.
- Frise du cycle fonctionnelle desktop **et** mobile.
- **Toutes les pages produits sur le gabarit unique** (`chickcare`) — 0 page sur l'ancienne
  architecture — et **0 lien cassé** sur toute la filière volailles.
- SEO : 1 h1/page, JSON-LD valide, breadcrumb, sitemap/llms à jour.
- Rendu **premium** au niveau du reste du site refondu, prêt à servir de **référence
  portfolio Tech & Web**.
```
