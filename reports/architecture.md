# Architecture proposée — MARIDAV CI (version premium)

Objectif: moderniser le site existant tout en restant pragmatique (Bootstrap 5.3, HTML/SCSS, JS léger), améliorer UX, SEO, accessibilité et conversions.

Choix clés

- Front: Bootstrap 5.3 + design tokens SCSS (couleurs, radius, typographie)
- JS: vanille + petits modules (htmx/alpine possibles au besoin), pas de jQuery nouveau
- Structure: Atomic-ish (sections/blocks réutilisables), includes manuels via partiels HTML
- Performance: lazy-load images, WebP/AVIF si disponibles, CSS/JS minimaux, SW pour cache statique
- SEO: sémantique HTML5, JSON-LD (Organization, Product, FAQ, Breadcrumb)
- Tracking: GA4 + pixels (Meta/TikTok), dataLayer unifié + événements clés

Arborescence cible (ASCII)

site/
├─ index.html
├─ volailles.html | porcins_maridav_ci.html | pisciculture_maridav_ci.html
├─ produits/
│  ├─ volailles/
│  │  └─ aliment-grower-volailles.html
│  └─ premix/ …
├─ partenaires/ (biomin, dsm, trouw, skretting, cid lines…)
├─ ressources/ (guides, protocoles, pdf)
├─ assets/
│  ├─ css/main.min.css (tokens + overrides)
│  ├─ js/main.min.js (CTA, JSON-LD, tracking, a11y)
│  └─ js/sw.js (cache statique)
├─ maridav_ci_image/ (images optimisées)
├─ content/
│  ├─ schemas/ (cms.json, bootstrap-forms.html)
│  ├─ templates/ (product.md)
│  └─ examples/ (maridav-grower-volailles.md)
└─ reports/ (audit, redirects, seo-plan, tracking-plan, sitemap)

Patrons & conventions

- Nommage slug-kebab pour URLs: exemple `aliment-grower-volailles.html`
- Composants UI: Hero, CardProduit, TableNutrition, CTAWhatsApp, FormLead (multi-étapes au besoin)
- Données structurées injectées côté page ou via `assets/js/main.min.js`
- Images: `img[loading=lazy]` + `alt` obligatoire, `srcset` pour grands visuels

Checklist d’implémentation

- [ ] Charger Bootstrap 5.3 + `assets/css/main.min.css` sur toutes les pages
- [ ] Charger `assets/js/main.min.js` (lazy-load, JSON-LD, CTA, a11y)
- [ ] Ajouter meta description + canonical sur pages espèces et fiches produit
- [ ] Mettre en place redirections 301 (voir `reports/redirects.csv`)
- [ ] Créer au moins 1 fiche produit premium (exemple livré)
- [ ] Ajouter FAQ + JSON-LD (FAQPage) sur pages piliers
- [ ] Brancher GA4 + pixels avec événements `lead_submit`, `whatsapp_click`, `call_click`, `pdf_download`, `filter_use`, `compare_open`
- [ ] Vérifier contrastes/Focus (WCAG 2.2 AA)

Raisons du choix

- Compatibilité forte avec le site actuel (HTML existant conservé)
- Gains immédiats en UX/SEO/Core Web Vitals sans migration lourde
- Base extensible pour un futur CMS statique (eleventy/astro) si souhaité

