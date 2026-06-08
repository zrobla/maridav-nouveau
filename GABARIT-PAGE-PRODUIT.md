# Gabarit standard — Pages produits MARIDAV CI
> Standard unique de toutes les pages produits (aliments complets, concentrés, prémix,
> additifs…). Remplace l'ancien gabarit `chickcare`. Implémentations de référence :
> **`concentre_chair_31.html`** (produit transversal, specs renvoyées à la fiche) et
> **`aliments_chair_finition_maridav_ci.html`** (aliment complet, specs complètes,
> mono‑filière). Tout nouveau produit ou page à convertir DOIT suivre ce document.

---

## 1. Principe
Identité **marque Maridav** (navy `#000066` + vert `#1b8e3e` + neutres), typo **Fraunces**
(titres) + **Inter** (corps), éditorial premium. Une page = **blocs standardisés** dont
certains sont **optionnels** (selon le produit) et d'autres **variables** (le contenu change,
pas la structure). **Aucune valeur chiffrée inventée** : si non connue → « sur fiche technique ».

## 2. Chrome & dépendances (OBLIGATOIRE, identique partout)
- **`<head>`** : meta UTF‑8/viewport/theme‑color `#000066`, `<title>`, `<meta description>`,
  `canonical`, OG (`og:type=article`), favicon.
- **CSS** (dans l'ordre) : Google Fonts (Fraunces+Inter) · Bootstrap 5.3.3 **avec
  `integrity` SRI** · bootstrap‑icons · fontawesome · `css/style.css` · `css/responsive.css`
  · `assets/css/main.min.css` · puis le **bloc `<style>` inline** (design tokens `:root` +
  composants `.pdp-*` — copier tel quel depuis une page de référence).
- **`<body class="pdp">`** + skip‑link.
- **Header/Nav = celui de `index.html`** (navbar‑premium, liens MAJUSCULES `nav-link-compact`,
  Solutions/Ressources dropdowns + Carrière, pills tél/WhatsApp, CTA devis).
- **Footer = celui de `index.html`** (`footer-premium`).
- **Scripts (fin de body)** : `vendor/jquery` · `vendor/popper` · `vendor/bootstrap` ·
  **`assets/js/main.min.js`** ⟵ *indispensable : gère les dropdowns du menu* · puis les
  3 blocs JSON‑LD · `assets/js/site-crm-bridge.js`.
- **Menu sticky** : `overflow` sur `<main>` (PAS sur `<body>` — sinon casse le `position:sticky`)
  + `.pdp .premium-header{position:sticky;top:0;z-index:1030}`.

## 3. Structure des sections

| # | Bloc | Statut | Ce qui varie |
|---|------|--------|--------------|
| 1 | **Hero** (`.pdp-hero`) | **OBLIGATOIRE** | breadcrumb, eyebrow (filière), `<h1>` (+ mot‑clé en `.accent`), **pill** (voir §4), lead, **facts strip** (4 cases, voir §5), image produit + figchip, 2 CTA |
| 2 | **Trust strip** (`.trust-strip`)* | OPTIONNEL | distribution / paiements / support |
| 3 | **Sticker transversalité** (`.pdp-transbadge`) | **OPTIONNEL** | **uniquement si produit multi‑filières** ; chips = filières concernées. Sinon **retirer toute la section** |
| 4 | **Bénéfices** (`.pdp-benefit`) | **OBLIGATOIRE** | intro + 4 cartes (icône bi + titre + texte) propres au produit |
| 5 | **Mode d'emploi** (`.pdp-step`) + **Fiche** (`.pdp-spec`) | **OBLIGATOIRE** | étapes (phases OU taux d'incorporation) ; table specs **complète** ou « sur fiche technique » (§6) |
| 6 | **Cross‑sell mode de production** (`.pdp-card` liseré vert) | OPTIONNEL | sens **inversé** selon le produit (§7) |
| 7 | **FAQ** (`<details>` natifs) | **OBLIGATOIRE** | 4–6 Q/R propres au produit (miroir du JSON‑LD FAQPage) |
| 8 | **Produits associés** (`.pdp-rel`) | OPTIONNEL | **libellé du kicker variable** : « Produits associés » / « Gamme volailles » / « Gamme je fabrique » / « Autres produits » ; 3 cartes, **images `object-fit:contain` fond blanc** |
| 9 | **CTA band** (`.pdp-ctaband`) | **OBLIGATOIRE** | accroche + 2 CTA (devis + WhatsApp) |

\* aligner sur la page de référence selon besoin.

## 4. La « pill » sous le titre (`.pdp-trans`) — VARIABLE
Un seul composant, 3 usages selon le produit :
- **Transversal** : `↔ Transversal — chair & pondeuses` **+** afficher le sticker (bloc 3).
- **Phase** (aliment complet) : `⚑ Phase finition — 29 à 42 jours`.
- **Taux** (prémix/concentré mono‑filière) : `% Taux d'incorporation 0,25 %`.

## 5. Facts strip (4 cases) — VARIABLE, **jamais de retour à la ligne**
`white-space:nowrap` sur valeur ET libellé ; colonnes ajustées (élargir la case au texte
le plus long). Exemples : aliment complet → `PB 18–18,5 % · EM 3 200 kcal · Sac 50 kg ·
Phase` ; concentré → `Taux 31 % · Sac 50 kg · Filières · FAF`.

## 6. Specs — VARIABLE (honnêteté)
- Données connues (aliments complets) → **table complète** (EM, PB, Lysine, Met+Cys, Ca/P, Na…).
- Données non publiables/inconnues → table « identité » + ligne **« Valeurs détaillées : sur
  fiche technique (selon lot) »**. **Ne jamais inventer de chiffres.**

## 7. Cross‑sell « mode de production » — VARIABLE
- Page **aliment complet** → « Vous fabriquez votre aliment ? » → lien **concentré**.
- Page **concentré/prémix** → « Vous préférez ne pas fabriquer ? » → lien **aliment complet**.

## 8. SEO / données structurées (OBLIGATOIRE)
- **1 seul `<h1>`** ; `BreadcrumbList` Accueil → Volailles → (Filière) → Produit.
- `Product` JSON‑LD (name, description, image, sku, category, audience, offer **sans `price`**
  — « sur devis »). `FAQPage` JSON‑LD **synchronisé** avec la FAQ visible.
- Images : `alt` descriptif ; produits associés en `object-fit:contain` fond blanc.

## 9. Definition of Done (à 100 % avant commit)
`[ ]` chrome index (nav+footer+main.min.js) · `[ ]` menu sticky + dropdowns OK ·
`[ ]` 1 `<h1>` · `[ ]` **0 lien cassé** (scan) · `[ ]` 3 JSON‑LD valides ·
`[ ]` SRI Bootstrap · `[ ]` 0 valeur chiffrée inventée · `[ ]` blocs optionnels retirés si
non pertinents · `[ ]` rendu vérifié **desktop + mobile**.

## 10. Procédure pour une nouvelle page produit
1. `cp` une page de référence (`concentre_chair_31.html` si transversal, sinon
   `aliments_chair_finition_maridav_ci.html`).
2. Récupérer les données du produit **depuis le site** (specs/conditionnement) et
   `products-volailles.json`.
3. Adapter chaque bloc (§3) ; **retirer** les blocs optionnels non pertinents (ex. sticker).
4. Réparer/valider tous les liens ; remplir JSON‑LD ; vérifier la DoD (§9).
5. Commit (un produit = une unité finie ; jamais de page à moitié).
