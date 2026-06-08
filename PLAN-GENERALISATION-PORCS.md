# Plan — Généralisation filière PORCS (même générateur, champ `espece`)

> Suite de la refonte volailles (terminée, étapes 0–5). On **réutilise** le générateur
> `build_maridav.py` et le design system `pdp` + composants de persuasion, en les **généralisant
> au multi-espèce** via le champ `espece`. Les **poissons suivront** avec la même méthode.
> Règles inchangées : FR · FCFA · **Côte d'Ivoire** · 0 chiffre inventé · pas de « tell » IA
> (§5.8) · pas de recon (§5.6) · sécurité GPU mobile ≤991px · archiver, pas supprimer ·
> pas de commit/push sans accord.

---

## 1) État réel constaté (écosystème porcs)

- **Hub filière** : `porcins_maridav_ci.html` (ancien design `hero-premium`/tabs, à refondre
  comme `volailles.html`).
- **10 pages produits** (gabarit premium-old ~29 Ko, à homogénéiser au gabarit `pdp`) :
  - **Aliments complets — engraissement** : `aliment_porc_demarrage` (7–25 kg),
    `aliment_porc_croissance` (25–70 kg), `aliment_porc_finition` (>70 kg).
  - **Aliments complets — reproduction** : `aliment_truie_gestante`, `aliment_truie_allaitante`.
  - **Pré-démarrage porcelet** : `milkeawean.html` (Milkiwean Eco — aliment lacté post-sevrage).
  - **Concentrés 5 %** : `porc_demarrage` (Concentré Porc Démarrage 5 %),
    `porc_croissance_05` (Concentré Porc Croissance 5 %), `truie_porcs_05` (Concentré Truie 5 %).
- **Gaps** (à confirmer avec Maridav, non bloquant) : **pas de macro-prémix / prémix porcs**
  → la gamme **FAF** est incomplète côté micro-incorporation ; slots prévus, gamme à compléter.
- **Junk** : `porcins.html` (capture 404) déjà exclu du sitemap par le scan.

---

## 2) Subtilités de la porciculture à intégrer (le cœur de la demande)

1. **Deux pistes parallèles, PAS un cycle linéaire** (différence majeure avec la volaille) :
   - **Engraissement** : porcelet sevré → **démarrage / 1ᵉʳ âge (7–25 kg)** → **croissance
     (25–70 kg)** → **finition (>70 kg)** → abattage. **Repère = le POIDS (kg)**, pas l'âge.
   - **Reproduction (cheptel truies)** : **gestante** → **allaitante (lactation)** → **sevrage**
     → saillie → gestante (+ cochette = future truie, verrat).
   → le composant **`cycle-timeline` doit avoir une variante « 2 pistes »** (sélecteur
     engraissement / reproduction, par classes JS — pas de `:has()`, GPU-safe), au lieu de la
     frise simple volailles.

2. **Le sevrage = transition critique** (stress post-sevrage, santé intestinale, dysbiose) :
   mettre en avant le **pré-démarrage très digestible** (Milkiwean). C'est le moment qui « fait
   ou casse » la suite de l'engraissement.

3. **FAF très répandu en porc** (rations fermières à base de maïs / son / tourteaux locaux pour
   maîtriser le coût) : le **mode-switch prêt-à-l'emploi / FAF est central** ; les **concentrés
   5 %** matérialisent le pilier FAF. Signaler le **gap prémix** (à compléter).

4. **Biosécurité = argument fort** (contexte **PPA / peste porcine africaine** en Afrique de
   l'Ouest) : vendre la **prévention sanitaire** comme bénéfice, **sans** exposer de dispositif
   précis (§5.6).

5. **Indicateurs — NE PAS INVENTER** : engraissement = **GMQ** (gain moyen quotidien),
   **IC** (indice de consommation = FCR porc), poids / âge à l'abattage ; reproduction =
   **nés-vivants / portée**, **sevrés / truie / an**, **ISSF** (intervalle sevrage–saillie
   fécondante), taux de mise-bas. → slots `proof`/`testimonial` **vides** tant que Maridav n'a
   pas fourni de chiffres/références réels.

6. **Pas de transversalité avec la volaille** : concentrés/prémix porcs sont spécifiques
   → badges « transversal » **off** (filtrage par `filieres` porc uniquement).

---

## 3) Architecture technique (réutiliser, NE PAS dupliquer)

- **Données** : nouveau `products-porcs.json` au **même schéma** que `products.json`
  (catégories `aliments_complets` / `concentres` / `macro_premix?` / `premix?`), avec
  `espece="porcs"`, `filieres=["porcs-engraissement" | "porcs-reproduction"]`, `phase` = palier
  de poids (engraissement) ou stade (reproduction). Slots persuasion identiques.
- **Générateur** : passer du `DATA` unique à un **registre d'espèces** dans `build_maridav.py` :
  `ESPECES = [{slug, data_file, filieres, hub}]`. La boucle produits réutilise **`render_page`
  tel quel** (le gabarit produit est déjà espèce-agnostique). Les pages filière/hub réutilisent
  `render_filiere_page` / `render_hub_page` en **généralisant** `FILIERES`/`HUB` par espèce.
- **Nouveau composant** : `cycle-timeline` **variante 2 pistes** (réutilise le CSS `.fl-timeline`
  + un track-switch JS façon `mode-switch`). Tout le reste (`pillars-strip`, `mode-switch`,
  `product-matrix`, `proof-bar`, `technician-cta`) est réutilisé tel quel.
- **Filière/hub porcs** : refondre `porcins_maridav_ci.html` en **un hub à 2 pistes**
  (engraissement / reproduction) plutôt que 2 pages — aiguillage + 4 piliers + « comment ça
  marche » + matrice prêt/FAF + proof-bar + technician-cta.
- **SEO** : le scan `sitemap`/`robots`/`llms` couvre **déjà tout le site** → les pages porcs
  régénérées seront prises automatiquement ; `llms.txt` pointe déjà `porcins_maridav_ci.html`.
  Bumper `BUILD_DATE`.

---

## 4) Déroulé d'exécution

0. **Données** `products-porcs.json` (10 produits + wording des 4 piliers décliné porc +
   slots proof/témoignage vides). Lister les chiffres à demander à Maridav.
1. **Généraliser le générateur** (registre d'espèces) + **composant timeline 2 pistes**.
   **De-risking gate** : convertir d'abord **2 pages de référence** (ex. `aliment_porc_croissance`
   + `aliment_truie_allaitante`) au gabarit `pdp` et valider rendu/SEO avant le reste.
2. **Générer les 10 pages produits porcs** ; **archiver** les premium-old dans
   `_archive/premium-old-porcs/` (audit liens entrants d'abord).
3. **Hub/filière porcs** `porcins_maridav_ci.html` (2 pistes + 4 piliers + comment ça marche +
   matrice prêt/FAF + proof-bar + technician-cta).
4. **SEO auto** (déjà en place) + **QA** : 1 `<h1>`/page, JSON-LD valides, 0 lien cassé, GPU
   mobile ≤991px, 0 chiffre inventé, pas de tell IA, release-gate vert.
5. **Validation utilisateur → commit.**

---

## 5) En attente / à confirmer avec Maridav

- **Gamme prémix / macro-prémix porcs (FAF)** : manquante — à confirmer (slots prévus).
- **Chiffres GMQ / IC / reproduction + témoignages** : slots **vides**, ne rien inventer.
- **Découpage filière** : ✅ **DÉCIDÉ (2026-06-08)** = **1 page hub porcs à 2 pistes**
  (`porcins_maridav_ci.html` avec track-switch Engraissement / Reproduction).

## 6) Ensuite — POISSONS (même méthode)

`pisciculture_maridav_ci.html` + gamme `nutra_tilapia_*`, `aquacare`, `profish`… ; cycle =
**alevin → grossissement**, repère = poids/stade ; spécificité **qualité d'eau** (O₂, pH).
