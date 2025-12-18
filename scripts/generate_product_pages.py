from __future__ import annotations

import json
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]

HEADER = """
  <header class="premium-header sticky-top" role="banner">
    <nav class="navbar navbar-expand-lg navbar-premium" aria-label="Navigation principale">
      <div class="container">
        <a class="navbar-brand" href="index.html" aria-label="MARIDAV CI">
          <img src="maridav_ci_image/logo/logo_maridav_ci.png" alt="MARIDAV CI">
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navPremium" aria-controls="navPremium" aria-expanded="false" aria-label="Menu">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navPremium">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item"><a class="nav-link nav-link-compact" href="index.html">ACCUEIL</a></li>
            <li class="nav-item dropdown">
              <button class="nav-link nav-link-compact dropdown-toggle" id="navSolutions" type="button" data-bs-toggle="dropdown" aria-expanded="false">SOLUTIONS</button>
              <ul class="dropdown-menu" aria-labelledby="navSolutions">
                <li><a class="dropdown-item" href="volailles.html">VOLAILLES</a></li>
                <li><a class="dropdown-item" href="porcins_maridav_ci.html">PORCS</a></li>
                <li><a class="dropdown-item" href="pisciculture_maridav_ci.html">POISSONS</a></li>
                <li><a class="dropdown-item" href="biosecurite_maridav_ci.html">BIOSECURITE</a></li>
              </ul>
            </li>
            <li class="nav-item dropdown">
              <button class="nav-link nav-link-compact dropdown-toggle" id="navResources" type="button" data-bs-toggle="dropdown" aria-expanded="false">RESSOURCES</button>
              <ul class="dropdown-menu" aria-labelledby="navResources">
                <li><a class="dropdown-item" href="a-propos.html">A PROPOS DE NOUS</a></li>
                <li><a class="dropdown-item" href="blog_maridav_ci.html">BLOG</a></li>
                <li><a class="dropdown-item" href="ressources/">DOCUMENTATIONS TECHNIQUES</a></li>
              </ul>
            </li>
            <li class="nav-item"><a class="nav-link nav-link-compact" href="distributeurs_maridav.html">POINTS DE VENTE</a></li>
          </ul>
          <div class="nav-meta d-lg-flex align-items-center gap-2 ms-lg-3">
            <a class="meta-pill" href="tel:002252721353242"><i class="fa fa-phone"></i><span>(+225) 27 21 35 32 42</span></a>
            <a class="meta-pill" href="https://api.whatsapp.com/send?phone=+2250574648888" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i><span>05 74 64 88 88</span></a>
          </div>
          <div class="nav-cta d-flex flex-column flex-lg-row gap-2 ms-lg-3">
            <a class="btn btn-brand btn-sm" href="contact.html">Demander un devis</a>
          </div>
        </div>
      </div>
    </nav>
  </header>
"""

FOOTER = """
  <footer class="footer-premium" role="contentinfo">
    <div class="footer-top">
      <div class="container">
        <div class="row g-4">
          <div class="col-12 col-lg-4">
            <div class="brand">
              <img src="maridav_ci_image/logo/logo_maridav_ci.png" alt="MARIDAV">
              <span>MARIDAV Côte d'Ivoire<small>Nutrition &amp; Santé Animales</small></span>
            </div>
            <p class="mt-3 small">Formulations tropicalisées, appui technique terrain et biosécurité pour volailles, porcs et poissons. Distributeur exclusif de produits mondialement reconnus pour couverture nationale en Côte d'Ivoire.</p>
            <a class="btn btn-brand btn-sm mt-3" href="#lead" data-open-lead>Parler à un expert</a>
          </div>
          <div class="col-6 col-lg-2">
            <h6>Solutions</h6>
            <ul class="list-unstyled m-0">
              <li><a class="small-link" href="volailles.html">Volailles</a></li>
              <li><a class="small-link" href="porcins_maridav_ci.html">Porcs</a></li>
              <li><a class="small-link" href="pisciculture_maridav_ci.html">Poissons</a></li>
              <li><a class="small-link" href="biosecurite_maridav_ci.html">Biosécurité</a></li>
            </ul>
          </div>
          <div class="col-6 col-lg-3">
            <h6>Ressources</h6>
            <ul class="list-unstyled m-0">
              <li><a class="small-link" href="a-propos.html">À propos de nous</a></li>
              <li><a class="small-link" href="partenaires-maridav.html">Nos Partenaires</a></li>
              <li><a class="small-link" href="blog_maridav_ci.html">Guides &amp; articles</a></li>
              <li><a class="small-link" href="ressources/">Fiches techniques &amp; PDF</a></li>
              <li><a class="small-link" href="distributeurs_maridav.html">Points de vente</a></li>
              <li><a class="small-link" href="contact.html">Demander un devis</a></li>
            </ul>
          </div>
          <div class="col-12 col-lg-3">
            <h6>Contact</h6>
            <ul class="list-unstyled footer-contact">
              <li><i class="fas fa-map-marker-alt"></i><span>Marcory Zone 4C Biétry, 34 Rue Alex Flemming – Abidjan</span></li>
              <li><i class="far fa-clock"></i><span>Lundi – Vendredi : 08h – 18h<br>Samedi : 08h – 13h</span></li>
            </ul>
            <div class="d-flex flex-column gap-2 mt-3">
              <a class="small-link" href="mailto:info@maridav.ci"><i class="fas fa-envelope"></i> info@maridav.ci</a>
              <a class="small-link" href="tel:002252721353242"><i class="fas fa-phone"></i> (+225) 27 21 35 32 42</a>
            </div>
            <div class="footer-social"><i class="fas fa-share-alt"></i><small> Suivez-Nous! </small>
              <a href="https://www.facebook.com/MaridavCI/" target="_blank" rel="noopener" aria-label="Facebook"><i class="fab fa-facebook"></i></a>
              <a href="https://ci.linkedin.com/company/maridav-ci" target="_blank" rel="noopener" aria-label="LinkedIn"><i class="fab fa-linkedin"></i></a>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="container d-flex flex-column flex-md-row align-items-center justify-content-between gap-2">
        <p class="mb-0 small">© 2025 MARIDAV Côte d'Ivoire — Nutrition &amp; santé animales.</p>
        <p class="mb-0 small">Site web conçu par <a href="https://tech-and-web.com" target="_blank" rel="noopener">TECH &amp; WEB</a></p>
      </div>
    </div>
  </footer>
"""

TEMPLATE = Template("""
<!DOCTYPE html>
<html lang=\"fr\">
<head>
  <meta charset=\"UTF-8\">
  <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, shrink-to-fit=no\">
  <meta name=\"theme-color\" content=\"#061948\">
  <title>$seo_title</title>
  <meta name=\"description\" content=\"$seo_description\">
  <meta property=\"og:title\" content=\"$seo_title\">
  <meta property=\"og:description\" content=\"$seo_description\">
  <meta property=\"og:image\" content=\"$seo_image\">
  <link rel=\"icon\" type=\"image/png\" sizes=\"32x32\" href=\"favicon_io/favicon-32x32.png\">
  <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css\" rel=\"stylesheet\" crossorigin=\"anonymous\">
  <link href=\"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css\" rel=\"stylesheet\">
  <link rel=\"stylesheet\" href=\"https://use.fontawesome.com/releases/v5.15.3/css/all.css\">
  <link rel=\"stylesheet\" type=\"text/css\" href=\"css/style.css\">
  <link rel=\"stylesheet\" type=\"text/css\" href=\"css/responsive.css\">
  <link rel=\"stylesheet\" href=\"dist/assets/owl.carousel.min.css\">
  <link rel=\"stylesheet\" href=\"dist/assets/owl.theme.default.min.css\">
  <link rel=\"stylesheet\" href=\"assets/css/main.min.css\">
  <link rel=\"stylesheet\" href=\"assets/css/product-premium.css\">
</head>
<body class=\"premium-active\">
  <a class=\"skip-link visually-hidden-focusable\" href=\"#main\">Aller au contenu principal</a>
$header
  <div class=\"main-page-wrapper\">
    <div id=\"loader-wrapper\">
      <div id=\"loader\"></div>
    </div>

    <main id=\"main\">
    <section class=\"premium-hero\">
      <div class=\"container\">
        <div class=\"row g-5 align-items-center\">
          <div class=\"col-lg-6\">
            <nav aria-label=\"Fil d'Ariane\" class=\"mb-3\">
              <ol class=\"breadcrumb breadcrumb-premium mb-2\">
$breadcrumb_html
              </ol>
            </nav>
            <div class=\"badge-stack\">
$hero_badges
            </div>
            <h1 class=\"display-5 fw-bold mt-3\">$hero_title</h1>
            <p class=\"lead\">$hero_description</p>
            <div class=\"row g-3 mt-4\" role=\"list\">
$hero_stats
            </div>
            <div class=\"d-flex flex-wrap gap-3 mt-4\">
              <a class=\"btn btn-light btn-lg text-dark\" href=\"contact.html\">Demander un devis</a>
              <a class=\"btn btn-outline-light btn-lg\" href=\"https://api.whatsapp.com/send?phone=+2250574648888\" target=\"_blank\" rel=\"noopener\">Parler à un technicien</a>
            </div>
            <p class=\"small text-white-50 mt-3\">$hero_note</p>
          </div>
          <div class=\"col-lg-6\">
            <div class=\"hero-media\">
              <img src=\"$hero_image\" alt=\"$hero_image_alt\">
              <div class=\"media-badge\">
                <strong>$hero_media_title</strong>
                <ul class=\"mb-0 ps-3\">
$hero_media_list
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class=\"trust-strip\">
      <div class=\"container\">
        <div class=\"row text-center text-md-start g-3 align-items-center\">
$trust_html
        </div>
      </div>
    </div>

    <section class=\"section-spacing\" id=\"benefices\">
      <div class=\"container\">
        <div class=\"row g-4\">
          <div class=\"col-lg-7\">
            <div class=\"card-premium h-100\">
              <div class=\"section-title\">
                <span>$benefits_eyebrow</span>
                <h2>$benefits_title</h2>
              </div>
              <div class=\"d-flex flex-column gap-4 mt-4\">
$features_html
              </div>
            </div>
          </div>
          <div class=\"col-lg-5\">
            <div class=\"card-premium dark h-100\">
              <div class=\"section-title\">
                <span>Pour qui ?</span>
                <h2 class=\"text-white\">$audience_title</h2>
              </div>
              <ul class=\"mt-4 text-white\">
$audience_list
              </ul>
              <div class=\"mt-4\">
                <h6 class=\"text-white-50 text-uppercase\">Badges espèce/stade</h6>
                <div class=\"d-flex flex-wrap gap-2 mt-2\">
$audience_badges
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class=\"section-spacing bg-white\" id=\"composition\">
      <div class=\"container\">
        <div class=\"row g-4 align-items-center\">
          <div class=\"col-lg-5\">
            <div class=\"section-title\">
              <span>Garanties nutritionnelles</span>
              <h2>$composition_title</h2>
            </div>
            <p>$composition_intro</p>
          </div>
          <div class=\"col-lg-7\">
            <div class=\"table-responsive\">
              <table class=\"table table-borderless align-middle\">
                <thead>
                  <tr><th>Paramètre</th><th>Valeur cible</th></tr>
                </thead>
                <tbody>
$composition_rows
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class=\"section-spacing\" id=\"usage\">
      <div class=\"container\">
        <div class=\"row g-4\">
          <div class=\"col-lg-7\">
            <div class=\"card-premium h-100\">
              <div class=\"section-title\">
                <span>Mode d’emploi</span>
                <h2>$usage_title</h2>
              </div>
$usage_steps
              <p class=\"small text-muted mt-3\">$usage_note</p>
            </div>
          </div>
          <div class=\"col-lg-5\">
            <div class=\"card-premium logistics-card h-100\">
              <div class=\"section-title\">
                <span>Formats &amp; logistique</span>
                <h2>$logistics_title</h2>
              </div>
$logistics_items
              <a class=\"btn btn-brand w-100 mt-3\" href=\"distributeurs_maridav.html\">Trouver un distributeur</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class=\"section-spacing bg-white\" id=\"documents\">
      <div class=\"container\">
        <div class=\"row g-4\">
          <div class=\"col-lg-8\">
            <div class=\"card-premium h-100\">
              <div class=\"section-title\">
                <span>Documents &amp; ressources</span>
                <h2>$resources_title</h2>
              </div>
              <p>$resources_intro</p>
              <div class=\"row g-3 mt-3\">
$resources_buttons
              </div>
            </div>
          </div>
          <div class=\"col-lg-4\">
            <div class=\"card-premium lead-card\" id=\"lead\">
              <div class=\"section-title\">
                <span>Parler à un expert</span>
                <h2>$lead_title</h2>
              </div>
              <p class=\"text-muted mt-2\">$lead_intro</p>
              <form class=\"lead-form mt-3\" action=\"https://formspree.io/f/maridav\" method=\"POST\">
                <div class=\"mb-3\">
                  <label class=\"form-label\" for=\"leadName\">$lead_name_label</label>
                  <input class=\"form-control\" id=\"leadName\" name=\"name\" type=\"text\" placeholder=\"$lead_name_placeholder\" required>
                </div>
                <div class=\"mb-3\">
                  <label class=\"form-label\" for=\"leadPhone\">$lead_contact_label</label>
                  <input class=\"form-control\" id=\"leadPhone\" name=\"phone\" type=\"tel\" placeholder=\"(+225) 07 00 00 00\" required>
                </div>
                <div class=\"mb-3\">
                  <label class=\"form-label\" for=\"leadVolume\">$lead_volume_label</label>
                  <input class=\"form-control\" id=\"leadVolume\" name=\"volume\" type=\"text\" placeholder=\"$lead_volume_placeholder\" required>
                </div>
                <div class=\"mb-3\">
                  <label class=\"form-label\" for=\"leadObjective\">$lead_objective_label</label>
                  <select class=\"form-select\" id=\"leadObjective\" name=\"objective\" required>
                    <option value=\"\" selected>Choisir</option>
$lead_objectives
                  </select>
                </div>
                <button class=\"btn btn-brand w-100\" type=\"submit\">$lead_cta</button>
                <p class=\"small text-muted mt-2\">En soumettant ce formulaire, vous acceptez d’être contacté par MARIDAV CI (données hébergées en CI, conformité RGPD).</p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class=\"section-spacing\" id=\"faq\">
      <div class=\"container\">
        <div class=\"row g-4\">
          <div class=\"col-lg-7\">
            <div class=\"section-title\">
              <span>Questions fréquentes</span>
              <h2>$faq_title</h2>
            </div>
            <div class=\"accordion mt-4\" id=\"faqAccordion\">
$faq_items
            </div>
          </div>
          <div class=\"col-lg-5\">
            <div class=\"cta-grid\">
              <div class=\"card-premium h-100 text-center\">
                <h3>$cta_title</h3>
                <p class=\"text-muted\">$cta_text</p>
                <div class=\"d-flex flex-column gap-2\">
                  <a class=\"btn btn-brand\" href=\"$cta_primary_url\">$cta_primary_label</a>
                  <a class=\"btn btn-outline-brand\" href=\"$cta_secondary_url\" target=\"_blank\" rel=\"noopener\">$cta_secondary_label</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    </main>
$footer

  </div>
  <a class="floating-whatsapp" href="https://api.whatsapp.com/send?phone=+2250574648888" target="_blank" aria-label="Discuter avec MARIDAV sur WhatsApp">
    <img src="maridav_ci_image/logo/whatsapp-logo-contact-maridav.png" alt="WhatsApp MARIDAV">
    <span>WhatsApp</span>
  </a>
  <button class="scroll-top tran3s" type="button" aria-label="Revenir en haut">
    <i class="fa fa-angle-up" aria-hidden="true"></i>
  </button>
  <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js\" crossorigin=\"anonymous\" defer></script>
  <script>
    window.addEventListener('load', () => {
      const loader = document.getElementById('loader-wrapper');
      if (loader) loader.style.display = 'none';
    });
    document.addEventListener('DOMContentLoaded', () => {
      document.querySelectorAll('[data-open-lead]').forEach(btn => {
        btn.addEventListener('click', event => {
          event.preventDefault();
          const target = document.getElementById('lead');
          if (target) target.scrollIntoView({ behavior: 'smooth' });
        });
      });
      document.querySelectorAll('.accordion-button').forEach(btn => {
        btn.addEventListener('click', () => {
          const icon = btn.querySelector('i');
          if (icon) icon.classList.toggle('bi-chevron-up');
        });
      });
      const scrollBtn = document.querySelector('.scroll-top');
      if (scrollBtn) {
        const toggleScrollBtn = () => {
          if (window.scrollY > 200) {
            scrollBtn.style.display = 'block';
          } else {
            scrollBtn.style.display = 'none';
          }
        };
        toggleScrollBtn();
        window.addEventListener('scroll', toggleScrollBtn);
        scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
      }
    });
  </script>
  <script type=\"application/ld+json\">
$schema_product
  </script>
  <script type=\"application/ld+json\">
$schema_faq
  </script>
</body>
</html>
""")


def render_list(items: list[str], wrapper: str = "li") -> str:
    return "\n".join(f"                <{wrapper}>{escape(item)}</{wrapper}>" for item in items)


def render_badges(items: list[str]) -> str:
    return "\n".join(f"              <span>{escape(item)}</span>" for item in items)


def render_stat_pills(stats: list[dict[str, str]]) -> str:
    html_parts = []
    for stat in stats:
        value = escape(stat["value"])
        label = escape(stat["label"])
        html_parts.append(
            "            <div class=\"col-6 col-md-4\">\n"
            "              <div class=\"stat-pill\" role=\"listitem\">\n"
            f"                <strong>{value}</strong>\n"
            f"                <small>{label}</small>\n"
            "              </div>\n            </div>"
        )
    return "\n".join(html_parts)


def render_feature_cards(features: list[dict[str, str]]) -> str:
    html_parts = []
    for feat in features:
        icon = escape(feat.get("icon", "bi-star"))
        title = escape(feat["title"])
        text = escape(feat["text"])
        html_parts.append(
            "                <div class=\"d-flex gap-3\">\n"
            f"                  <div class=\"benefit-icon\"><i class=\"bi {icon}\"></i></div>\n"
            "                  <div>\n"
            f"                    <h5>{title}</h5>\n"
            f"                    <p>{text}</p>\n"
            "                  </div>\n"
            "                </div>"
        )
    return "\n".join(html_parts)


def render_trust(trust_items: list[dict[str, str]]) -> str:
    html_parts = []
    for item in trust_items:
        label = escape(item.get("label", ""))
        text = escape(item.get("text", ""))
        if label:
            html_parts.append(f"          <div class=\"col-md-4\"><strong>{label} :</strong> {text}</div>")
        else:
            html_parts.append(f"          <div class=\"col-md-4\">{text}</div>")
    return "\n".join(html_parts)


def render_table_rows(rows: list[dict[str, str]]) -> str:
    return "\n".join(
        f"                  <tr><td>{escape(row['label'])}</td><td>{escape(row['value'])}</td></tr>" for row in rows
    )


def render_usage(steps: list[dict[str, str]]) -> str:
    html_parts = []
    for step in steps:
        badge = escape(step.get("badge", ""))
        title = escape(step["title"])
        text = escape(step["text"])
        html_parts.append(
            "              <div class=\"timeline-step\">\n"
            f"                <span>{badge}</span>\n"
            "                <div>\n"
            f"                  <h5>{title}</h5>\n"
            f"                  <p>{text}</p>\n"
            "                </div>\n"
            "              </div>"
        )
    return "\n".join(html_parts)


def render_logistics(items: list[dict[str, str]]) -> str:
    html_parts = []
    for item in items:
        icon = escape(item.get("icon", "bi-bag"))
        title = escape(item["title"])
        text = escape(item["text"])
        html_parts.append(
            "              <div class=\"d-flex gap-3\">\n"
            f"                <div class=\"icon-circle\"><i class=\"bi {icon}\"></i></div>\n"
            "                <div>\n"
            f"                  <h5>{title}</h5>\n"
            f"                  <p>{text}</p>\n"
            "                </div>\n"
            "              </div>"
        )
    return "\n".join(html_parts)


def render_resource_buttons(resources: list[dict[str, str]]) -> str:
    html_parts = []
    for res in resources:
        icon = escape(res.get("icon", "bi-file-earmark-text"))
        label = escape(res["label"])
        url = escape(res["url"])
        html_parts.append(
            "                <div class=\"col-md-6\">\n"
            f"                  <a class=\"btn btn-outline-brand w-100\" href=\"{url}\" target=\"_blank\"><i class=\"bi {icon}\"></i> {label}</a>\n"
            "                </div>"
        )
    return "\n".join(html_parts)


def render_objectives(options: list[str]) -> str:
    return "\n".join(f"                    <option value=\"{escape(opt)}\">{escape(opt)}</option>" for opt in options)


def render_faq(faq: list[dict[str, str]], slug: str) -> tuple[str, list[dict[str, str]]]:
    faq_entities = []
    html_parts = []
    for idx, item in enumerate(faq, start=1):
        q = escape(item["question"])
        a = escape(item["answer"])
        collapse_id = f"{slug}-faq-{idx}"
        html_parts.append(
            "              <div class=\"accordion-item\">\n"
            f"                <h2 class=\"accordion-header\" id=\"{collapse_id}-header\">\n"
            "                  <button class=\"accordion-button collapsed\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#"
            f"{collapse_id}\" aria-expanded=\"false\" aria-controls=\"{collapse_id}\">{q}</button>\n"
            "                </h2>\n"
            f"                <div id=\"{collapse_id}\" class=\"accordion-collapse collapse\" aria-labelledby=\"{collapse_id}-header\" data-bs-parent=\"#faqAccordion\">\n"
            "                  <div class=\"accordion-body\">"
            f"{a}</div>\n"
            "                </div>\n"
            "              </div>"
        )
        faq_entities.append({"@type": "Question", "name": item["question"], "acceptedAnswer": {"@type": "Answer", "text": item["answer"]}})
    return "\n".join(html_parts), faq_entities


DEFAULT_RESOURCES = [
    {"label": "Demander la fiche technique", "url": "contact.html", "icon": "bi-file-earmark-arrow-down"},
    {"label": "Voir nos guides d’élevage", "url": "blog_maridav_ci.html", "icon": "bi-journal-richtext"},
    {"label": "Consulter les distributeurs", "url": "distributeurs_maridav.html", "icon": "bi-geo-alt"},
    {"label": "Télécharger la brochure MARIDAV", "url": "brochure.html", "icon": "bi-cloud-download"},
]

DEFAULT_TRUST = [
    {"label": "Réseau MARIDAV CI", "text": "Couverture nationale & support terrain"},
    {"label": "Qualité", "text": "Sourcing contrôlé et traçabilité complète"},
    {"label": "Assistance", "text": "Plans nutrition & biosécurité personnalisés"}
]

DEFAULT_AUDIENCE = {
    "title": "Élevages concernés",
    "items": [
        "Élevages industriels recherchant une solution premium",
        "Producteurs semi-intensifs accompagnés par MARIDAV CI"
    ],
    "badges": ["Multi-espèces"]
}

PRODUCTS = [
    {
        "file": "milkeawean.html",
        "slug": "milkiwean",
        "seo": {
            "title": "Milkiwean Eco — Pré-démarrage porcelets | MARIDAV CI",
            "description": "Préparation lactée Milkiwean Eco pour sécuriser les 10 premiers jours des porcelets : ingestion rapide, immunité renforcée et soutien digestif.",
            "image": "https://maridav.ci/maridav_ci_image/predemarrage/Milkiwean%20Complete%20Maridav.png",
        },
        "breadcrumbs": [
            {"label": "Porcs", "url": "porcins_maridav_ci.html"},
            {"label": "Pré-démarrage"}
        ],
        "hero": {
            "badges": ["Porcelets", "0-10 jours", "Préparation lactée"],
            "title": "Milkiwean Eco — programme lacté haute performance",
            "description": "Gel/préparation riche en protéines laitières, vitamines et additifs fonctionnels pour stimuler la prise d’aliment et limiter les pertes en maternité.",
            "stats": [
                {"value": "+95%", "label": "Porcelets ayant ingéré en moins de 6 h"},
                {"value": "22 %", "label": "Protéines digestibles"},
                {"value": "10 kg", "label": "Conditionnement seau"}
            ],
            "note": "Performances observées sur lots suivis MARIDAV CI — maternités Abidjan & Bouaflé (2024).",
            "image": "maridav_ci_image/predemarrage/Milkiwean%20Complete%20Maridav.png",
            "image_alt": "Seaux Milkiwean Eco distribué par MARIDAV CI",
            "media_title": "Appui technique porcelets",
            "media_points": [
                "Coaching ingestion (6 h / 24 h)",
                "Plan lumière maternité",
                "Suivi GMQ & homogénéité"
            ]
        },
        "trust": [
            {"label": "Distribution", "text": "Maternités Abidjan, Bouaké, San Pedro, Korhogo"},
            {"label": "Livraison", "text": "48 h max sur fermes clientes (camion isotherme)"},
            {"label": "Normes", "text": "Traçabilité DSM/Trouw, contrôle bactério & mycotoxines"}
        ],
        "benefits": {
            "eyebrow": "Promesse produit",
            "title": "Pourquoi choisir Milkiwean Eco",
            "features": [
                {"icon": "bi-baby", "title": "Ingestion express", "text": "Texture gourmande et arômes lactés pour inciter les porcelets fragiles à consommer dès les premières heures."},
                {"icon": "bi-shield-check", "title": "Immunité renforcée", "text": "Beta-glucanes, vitamines A-D3-E et sélénium organique pour soutenir le système immunitaire néonatal."},
                {"icon": "bi-speedometer2", "title": "Homogénéité des portées", "text": "Profil nutritionnel équilibré pour lisser les écarts de poids avant le sevrage."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Intégrateurs porcins équipés de salles de maternité climatisées",
                "Producteurs semi-intensifs recherchant une solution clé en main",
                "Techniciens souhaitant réduire la mortalité &lt; 5 % avant sevrage"
            ],
            "badges": ["Porcelets", "Maternité", "0-10 jours"]
        },
        "composition": {
            "title": "Profil nutritionnel Milkiwean Eco",
            "intro": "Valeurs indicatives pouvant évoluer selon les matières premières disponibles tout en respectant les standards DSM/Trouw.",
            "rows": [
                {"label": "Protéines brutes", "value": "22 %"},
                {"label": "Matières grasses", "value": "18 %"},
                {"label": "Lactose", "value": "20 %"},
                {"label": "Vitamine A / D3 / E", "value": "12 000 UI / 2 400 UI / 140 mg"},
                {"label": "Additifs digestifs", "value": "Acidifiants, MOS, enzymes"}
            ]
        },
        "usage": {
            "title": "Programme d’utilisation conseillé",
            "note": "Respecter les bonnes pratiques d’hygiène des biberons/tétines et maintenir l’eau à 38–40 °C lors de la reconstitution.",
            "steps": [
                {"badge": "J0-J1", "title": "Parcours colostrum", "text": "Assurez-vous que chaque porcelet ingère du colostrum avant l’introduction de Milkiwean Eco."},
                {"badge": "J1-J3", "title": "Introduction progressive", "text": "Réhydratez la poudre (1:4) et répartissez sur plateaux propres toutes les 4 heures."},
                {"badge": "J4-J10", "title": "Distribution ad libitum", "text": "Complétez avec aliment pré-démarrage sec une fois l’ingestion lactée stabilisée."}
            ]
        },
        "logistics": {
            "title": "Disponibilité Côte d’Ivoire",
            "items": [
                {"icon": "bi-bucket", "title": "Conditionnement", "text": "Seaux hermétiques 10 kg & 20 kg avec dosette."},
                {"icon": "bi-thermometer", "title": "Stockage", "text": "Local tempéré &lt; 25 °C, palettes en hauteur."},
                {"icon": "bi-headset", "title": "Support", "text": "Hotline maternité 24/7 & visites terrain."}
            ]
        },
        "resources": {
            "title": "Outils techniques disponibles",
            "intro": "Demandez fiches techniques, protocoles lait artificiel et checklists maternité auprès de nos conseillers.",
        },
        "lead": {
            "title": "Briefing express porcelets",
            "intro": "Partagez vos effectifs et vos objectifs : un technicien porcin vous répond sous 48 h.",
            "name_label": "Nom &amp; structure d'exploitation",
            "name_placeholder": "Ex : Ferme porcine d'Azaguié",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de porcelets par lot",
            "volume_placeholder": "Ex : 480 porcelets",
            "objective_label": "Objectif",
            "objectives": [
                "Booster l’ingestion néonatale",
                "Sécuriser le GMQ avant sevrage",
                "Mettre en place Milkiwean Eco",
                "Former mon équipe maternité"
            ],
            "cta": "Recevoir un plan porcelets"
        },
        "cta": {
            "title": "Prêt à lancer Milkiwean Eco ?",
            "text": "Nos équipes planifient vos livraisons et paramètrent vos protocoles.",
            "primary_label": "Parler à un expert",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Comment préparer Milkiwean Eco ?", "answer": "Mélangez 1 kg de poudre dans 4 L d’eau à 45 °C, agitez puis laissez retomber à 38 °C avant distribution."},
            {"question": "Peut-on l’utiliser avec un nourrisseur automatique ?", "answer": "Oui, assurez-vous de nettoyer le circuit quotidiennement et de calibrer la température."},
            {"question": "Quel est le délai d’utilisation après reconstitution ?", "answer": "Consommer dans les 2 heures. Au-delà, jeter la préparation et nettoyer le récipient."}
        ],
        "schema": {
            "name": "Milkiwean Eco",
            "description": "Préparation lactée premium pour porcelets 0-10 jours distribuée par MARIDAV Côte d’Ivoire.",
            "image": "https://maridav.ci/maridav_ci_image/predemarrage/Milkiwean%20Complete%20Maridav.png",
            "sku": "MILKIWEAN-ECO",
            "category": "Préparation lactée",
            "audience": "Porcs — Porcelets"
        }
    },
    {
        "file": "aliment_porc_demarrage_maridav_ci.html",
        "slug": "porc-demarrage",
        "seo": {
            "title": "Aliment Porc Démarrage (7–25 kg) | MARIDAV CI",
            "description": "Aliment complet démarrage pour porcs 7–25 kg : croissance sécurisée, FCR optimisée et soutien digestif en post-sevrage.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
        },
        "breadcrumbs": [
            {"label": "Porcs", "url": "porcins_maridav_ci.html"},
            {"label": "Aliments complets"}
        ],
        "hero": {
            "badges": ["Porcs", "Démarrage 7–25 kg", "Aliment complet"],
            "title": "Aliment Porc Démarrage — Croissance maîtrisée",
            "description": "Granulé premium formulé pour soutenir l’ingestion et la conversion des porcelets post-sevrés tout en réduisant les troubles digestifs.",
            "stats": [
                {"value": "+620 g", "label": "GMQ cible / jour"},
                {"value": "1,60", "label": "FCR visée"},
                {"value": "50 kg", "label": "Sac laminé tropicalisé"}
            ],
            "note": "Performances basées sur des élevages suivis par MARIDAV CI (Bouaké & Bouaflé, 2024).",
            "image": "maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "image_alt": "Sacs d’aliments porcins MARIDAV",
            "media_title": "Support post-sevrage",
            "media_points": [
                "Plan de transition lacté → sec",
                "Mesure consommation & FCR",
                "Coaching biosécurité eau"
            ]
        },
        "trust": [
            {"label": "Distribution", "text": "Abidjan, Bouaké, Bouaflé, Korhogo"},
            {"label": "Livraison", "text": "Camions compartimentés et livret de lot fourni"},
            {"label": "Normes", "text": "Échantillons conservés 6 mois, contrôles mycotoxines"}
        ],
        "benefits": {
            "eyebrow": "Promesse produit",
            "title": "Ce que l’Aliment Porc Démarrage vous apporte",
            "features": [
                {"icon": "bi-rocket-takeoff", "title": "Démarrage tonique", "text": "Énergie métabolisable élevée (3 400 kcal/kg) pour soutenir l’hyperprolificité moderne."},
                {"icon": "bi-shield-lock", "title": "Protection digestive", "text": "Acidifiants, fibres fonctionnelles et probiotiques pour limiter les diarrhées post-sevrage."},
                {"icon": "bi-diagram-3", "title": "Profil amino calibré", "text": "Lysine, Méthionine, Thréonine digestibles adaptés aux génétiques DanBred, Topigs, PIC."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Ateliers post-sevrage (500 – 5 000 porcs) recherchant une ration prête à l’emploi.",
                "Intégrateurs voulant uniformiser leurs performances inter-sites.",
                "Équipes techniques souhaitant sécuriser la transition lactée."
            ],
            "badges": ["Porcs", "7–25 kg", "Post-sevrage"]
        },
        "composition": {
            "title": "Tableau de composition indicative",
            "intro": "Matières premières sélectionnées (maïs, soja, primes) et additifs DSM/Trouw pour garantir la constance d’un lot à l’autre.",
            "rows": [
                {"label": "Énergie métabolisable", "value": "3 350 – 3 450 kcal/kg"},
                {"label": "Protéines brutes", "value": "18 %"},
                {"label": "Lysine digestible", "value": "1,30 %"},
                {"label": "Thréonine digestible", "value": "0,83 %"},
                {"label": "Calcium / Phosphore digestible", "value": "0,80 % / 0,42 %"}
            ]
        },
        "usage": {
            "title": "Programme d’utilisation conseillé",
            "note": "Toujours fournir une eau propre, fraîche, avec acidification possible (Biotronic Top Liquide).",
            "steps": [
                {"badge": "Jour 0", "title": "Transition progressive", "text": "Mélangez 75 % d’aliment pré-démarrage avec 25 % d’Aliment Porc Démarrage durant 2 jours."},
                {"badge": "Jour 2-14", "title": "Distribution à volonté", "text": "Viser 650 g/jour, 1 auge pour 12 porcs, nettoyage quotidien des trémies."},
                {"badge": "Jour 15-28", "title": "Préparation du stade croissance", "text": "Introduire 25 % d’aliment croissance pour habituer les porcs à la nouvelle ration."}
            ]
        },
        "logistics": {
            "title": "Disponibilité Côte d’Ivoire",
            "items": [
                {"icon": "bi-bag", "title": "Conditionnement", "text": "Sac 50 kg laminé, insert anti-humidité."},
                {"icon": "bi-truck", "title": "Livraison régionale", "text": "Routage hebdomadaire Abidjan → centre / nord sur devis."},
                {"icon": "bi-people", "title": "Accompagnement", "text": "Suivi technico-économique & tableur FCR fournis."}
            ]
        },
        "resources": {
            "title": "Documents techniques sur demande",
            "intro": "Contactez-nous pour recevoir fiche technique, étiquette actualisée et modèle de plan de ration post-sevrage."
        },
        "lead": {
            "title": "Parler à un expert porcin",
            "intro": "Partagez votre effectif, vos densités et vos objectifs pour recevoir un plan adapté.",
            "name_label": "Nom &amp; structure d'exploitation",
            "name_placeholder": "Ex : Ferme porcine d'Adzopé",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de porcs par lot",
            "volume_placeholder": "Ex : 900 porcs",
            "objective_label": "Objectif",
            "objectives": [
                "Améliorer le GMQ post-sevrage",
                "Réduire la FCR (<1,65)",
                "Mettre à jour mon plan d’alimentation",
                "Sécuriser la biosécurité eau"
            ],
            "cta": "Recevoir un plan porcs"
        },
        "cta": {
            "title": "Boostez votre phase démarrage",
            "text": "Un technicien MARIDAV CI vous accompagne sur les réglages d’auge, d’éclairage et de ration.",
            "primary_label": "Demander un rendez-vous",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quelle consommation journalière viser ?", "answer": "Entre 0,55 et 0,75 kg par porc et par jour selon la génétique et la température ambiante."},
            {"question": "Puis-je mélanger avec des matières premières locales ?", "answer": "L’aliment est complet. Évitez de le diluer pour conserver l’équilibre nutritionnel. Contactez-nous pour un plan concentré si vous souhaitez incorporer vos propres matières."},
            {"question": "Comment stocker les sacs ?", "answer": "Sur palettes, dans un local ventilé, à l’abri des rongeurs. Respecter la rotation FIFO et refermer les sacs entamés."}
        ],
        "schema": {
            "name": "Aliment Porc Démarrage",
            "description": "Aliment complet porcin 7–25 kg distribué par MARIDAV Côte d’Ivoire.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "sku": "PORC-DEMARRAGE",
            "category": "Aliment complet",
            "audience": "Porcs — Post-sevrage"
        }
    },
    {
        "file": "aliment_porc_croissance_maridav_ci.html",
        "slug": "porc-croissance",
        "seo": {
            "title": "Aliment Porc Croissance (25–70 kg) | MARIDAV CI",
            "description": "Aliment complet croissance pour porcs 25–70 kg : GMQ robuste, FCR maîtrisée et homogénéité des bandes.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
        },
        "breadcrumbs": [
            {"label": "Porcs", "url": "porcins_maridav_ci.html"},
            {"label": "Aliments complets"}
        ],
        "hero": {
            "badges": ["Porcs", "Croissance 25–70 kg", "Aliment complet"],
            "title": "Aliment Porc Croissance — FCR sous contrôle",
            "description": "Formulation tropicalisée pour convertir efficacement les matières premières locales tout en sécurisant le GMQ des bandes.",
            "stats": [
                {"value": "+840 g", "label": "GMQ cible / jour"},
                {"value": "2,35", "label": "FCR visée"},
                {"value": "50 kg", "label": "Sac laminé"}
            ],
            "note": "Indicateurs issus des suivis MARIDAV CI (Korhogo, 2024).",
            "image": "maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "image_alt": "Sac aliment porc croissance MARIDAV",
            "media_title": "Suivi engraissement",
            "media_points": [
                "Planification des phases",
                "Tableaux de consommation",
                "Coaching densité / ventilation"
            ]
        },
        "trust": [
            {"label": "Distribution", "text": "Abidjan, Bouaké, Korhogo, San Pedro"},
            {"label": "Approvisionnement", "text": "Lignes d’écrasement MARIDAV + sourcing local contrôlé"},
            {"label": "Normes", "text": "Analyses EM, protéine et mycotoxines sur chaque lot"}
        ],
        "benefits": {
            "eyebrow": "Promesse produit",
            "title": "Des performances au rendez-vous",
            "features": [
                {"icon": "bi-graph-up", "title": "Gain moyen quotidien élevé", "text": "Profil énergétique et amino optimisé pour dépasser 840 g/jour en climat ivoirien."},
                {"icon": "bi-sliders", "title": "Ration équilibrée", "text": "Apport en lysine, thréonine et valine pour soutenir la carcasse tout en limitant le gras dorsal."},
                {"icon": "bi-droplet", "title": "Confort digestif", "text": "Acidifiants et fibres sélectionnées pour limiter les troubles digestifs et maintenir la consommation."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Engraisseurs voulant une ration prête à distribuer avec assistance technique.",
                "Intégrateurs ou coopératives souhaitant uniformiser leurs performances de lot.",
                "Sites avec matières premières locales cherchant une alternative sécurisée."
            ],
            "badges": ["Porcs", "Croissance", "25–70 kg"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Les formulations peuvent être ajustées selon les cours du maïs et du soja tout en respectant le profil digestible défini par MARIDAV CI.",
            "rows": [
                {"label": "Énergie métabolisable", "value": "3 200 – 3 250 kcal/kg"},
                {"label": "Protéines brutes", "value": "16 %"},
                {"label": "Lysine digestible", "value": "0,95 %"},
                {"label": "Thréonine digestible", "value": "0,62 %"},
                {"label": "Calcium / Phosphore digestible", "value": "0,75 % / 0,38 %"}
            ]
        },
        "usage": {
            "title": "Programme conseillé",
            "note": "Toujours vérifier la hauteur des auges et la densité (0,65 m² / porc minimum).",
            "steps": [
                {"badge": "25 kg", "title": "Transition démarrage → croissance", "text": "Sur 3 jours, mélangez l’aliment démarrage et croissance puis basculez à 100 % croissance."},
                {"badge": "25–60 kg", "title": "Distribution ad libitum", "text": "Consommation visée : 1,8 – 2,4 kg/porc/j selon la température. Assurez un abreuvement continu."},
                {"badge": "60–70 kg", "title": "Préparation finition", "text": "Introduire progressivement l’aliment finition pour aligner les carcasses sur l’objectif de vente."}
            ]
        },
        "logistics": {
            "title": "Logistique & formats",
            "items": [
                {"icon": "bi-bag-check", "title": "Sac 50 kg", "text": "Sac laminé avec insert anti-humidité."},
                {"icon": "bi-truck-front", "title": "Livraison régulière", "text": "Organisation de tournées hebdomadaires selon volumes."},
                {"icon": "bi-cash-stack", "title": "Modalités de paiement", "text": "XOF, virement, Mobile Money Pro (MTN, Orange)."}
            ]
        },
        "resources": {
            "title": "Ressources disponibles",
            "intro": "Recevez fiche technique, grille de consommation et guide d’ajustement FCR."
        },
        "lead": {
            "title": "Obtenir un plan croissance",
            "intro": "Renseignez vos effectifs et vos objectifs : nous vous aidons à calibrer la ration.",
            "name_label": "Nom &amp; structure d'exploitation",
            "name_placeholder": "Ex : Ferme porcine de Korhogo",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de porcs en engraissement",
            "volume_placeholder": "Ex : 1 200 porcs",
            "objective_label": "Objectif",
            "objectives": [
                "Améliorer ma FCR",
                "Uniformiser mes lots",
                "Sécuriser l’approvisionnement",
                "Conseil ventilation / densité"
            ],
            "cta": "Recevoir un plan croissance"
        },
        "cta": {
            "title": "Accélérez vos bandes",
            "text": "Nous dimensionnons vos besoins en aliment et organisons vos livraisons.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quelle densité d’auge recommandez-vous ?", "answer": "Prévoir au minimum 3 cm d’auge par porc avec 12 porcs par point d’alimentation automatique."},
            {"question": "Peut-on ajuster l’énergie ?", "answer": "Oui, nous pouvons adapter l’énergie selon vos objectifs de carcasse. Contactez-nous pour une formulation spécifique."},
            {"question": "Comment suivre la consommation ?", "answer": "Utilisez le tableau fourni par MARIDAV CI et pesez les restes quotidiennement afin d’anticiper les dérives de FCR."}
        ],
        "schema": {
            "name": "Aliment Porc Croissance",
            "description": "Aliment complet porcin 25–70 kg formulé et distribué par MARIDAV Côte d’Ivoire.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "sku": "PORC-CROISSANCE",
            "category": "Aliment complet",
            "audience": "Porcs — Croissance"
        }
    },
    {
        "file": "aliment_porc_finition_maridav_ci.html",
        "slug": "porc-finition",
        "seo": {
            "title": "Aliment Porc Finition (>70 kg) | MARIDAV CI",
            "description": "Aliment complet finition pour porcs >70 kg : carcasses régulières, rendement muscle optimal et maîtrise du coût alimentaire.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
        },
        "breadcrumbs": [
            {"label": "Porcs", "url": "porcins_maridav_ci.html"},
            {"label": "Aliments complets"}
        ],
        "hero": {
            "badges": ["Porcs", "Finition >70 kg", "Aliment complet"],
            "title": "Aliment Porc Finition — Valorisez vos carcasses",
            "description": "Profil énergétique ajusté pour optimiser le dépôt musculaire et livrer une carcasse régulière conforme aux abattoirs ivoiriens.",
            "stats": [
                {"value": "115 kg", "label": "Poids cible abattage"},
                {"value": "2,95", "label": "FCR visée"},
                {"value": "50 kg", "label": "Sac tropicalisé"}
            ],
            "note": "Validé sur lots MARIDAV CI (Abidjan / San Pedro, 2024).",
            "image": "maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "image_alt": "Sacs aliment finition MARIDAV",
            "media_title": "Appui préparation abattoir",
            "media_points": [
                "Plan d’abattage",
                "Suivi gras dorsal",
                "Optimisation du coût aliment"
            ]
        },
        "trust": [
            {"label": "Distribution", "text": "Couverture nationale via réseau MARIDAV"},
            {"label": "Stockage", "text": "Plateformes Abidjan / Bouaké / Korhogo"},
            {"label": "Normes", "text": "Traçabilité matières premières & audits internes"}
        ],
        "benefits": {
            "eyebrow": "Promesse produit",
            "title": "Des carcasses conformes aux attentes",
            "features": [
                {"icon": "bi-award", "title": "Conformation régulière", "text": "Équilibre énergie/protéines pour respecter les cahiers des charges abattoirs."},
                {"icon": "bi-speedometer", "title": "FCR maîtrisée", "text": "Additifs enzymatiques pour tirer parti des matières premières locales."},
                {"icon": "bi-fan", "title": "Résilience thermique", "text": "Électrolytes et vitamines pour maintenir la consommation en saison chaude."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Engraisseurs livrant les abattoirs d’Abidjan ou San Pedro.",
                "Coopératives voulant sécuriser la qualité carcasse.",
                "Sites cherchant à réduire le coût par kg vif."
            ],
            "badges": ["Porcs", "Finition", ">70 kg"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs susceptibles de varier selon les matières premières, tout en gardant l’équilibre nutritionnel attendu.",
            "rows": [
                {"label": "Énergie métabolisable", "value": "3 150 kcal/kg"},
                {"label": "Protéines brutes", "value": "15 %"},
                {"label": "Lysine digestible", "value": "0,75 %"},
                {"label": "Thréonine digestible", "value": "0,52 %"},
                {"label": "Calcium / Phosphore digestible", "value": "0,65 % / 0,32 %"}
            ]
        },
        "usage": {
            "title": "Mode d’emploi",
            "note": "Surveiller la consommation et ajuster la ventilation pour éviter les coups de chaleur.",
            "steps": [
                {"badge": "70 kg", "title": "Transition croissance → finition", "text": "Introduire 30 % de finition pendant 3 jours avant bascule complète."},
                {"badge": "70–100 kg", "title": "Distribution ad libitum", "text": "Consommation cible 2,6 – 3,0 kg/porc/j selon la température."},
                {"badge": "100 kg+", "title": "Préparation à l’abattage", "text": "Réduire le temps de jeûne avant transport, organiser le chargement aux heures fraîches."}
            ]
        },
        "logistics": {
            "title": "Formats & services",
            "items": [
                {"icon": "bi-bag", "title": "Sac 50 kg", "text": "Sac renforcé, stockage sur palettes conseillé."},
                {"icon": "bi-calendar-event", "title": "Planification", "text": "Calendrier de livraison aligné sur les départs abattoirs."},
                {"icon": "bi-diagram-3", "title": "Conseil techno-éco", "text": "Simulations coût/kg vif disponibles."}
            ]
        },
        "resources": {
            "title": "Guides finition",
            "intro": "Fiches techniques, checklists abattoir et guides de transport disponibles sur demande."
        },
        "lead": {
            "title": "Optimiser ma finition",
            "intro": "Nos experts vous aident à dimensionner vos besoins et préparer les objectifs d’abattage.",
            "name_label": "Nom &amp; structure d'exploitation",
            "name_placeholder": "Ex : Ferme porcine de Yopougon",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de porcs prêts à finir",
            "volume_placeholder": "Ex : 750 porcs",
            "objective_label": "Objectif",
            "objectives": [
                "Optimiser la qualité carcasse",
                "Réduire le coût alimentaire",
                "Planifier les livraisons",
                "Appui transport / abattoir"
            ],
            "cta": "Recevoir un plan finition"
        },
        "cta": {
            "title": "Valorisez chaque kg vif",
            "text": "Contactez MARIDAV CI pour sécuriser votre phase finition et vos programmes logistiques.",
            "primary_label": "Contacter un expert",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quel poids viser avant abattage ?", "answer": "Nous recommandons 110 à 115 kg pour optimiser la carcasse tout en maîtrisant le coût alimentaire."},
            {"question": "Faut-il restreindre l’aliment avant transport ?", "answer": "Un jeûne de 6 à 8 heures suffit. Maintenez l’accès à l’eau jusqu’au chargement."},
            {"question": "Comment gérer les chaleurs ? ", "answer": "Ventilation, brumisation et distribution nocturne peuvent aider à maintenir l’ingestion. Contactez-nous pour un plan adapté."}
        ],
        "schema": {
            "name": "Aliment Porc Finition",
            "description": "Aliment complet finition pour porcs >70 kg distribué par MARIDAV Côte d’Ivoire.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "sku": "PORC-FINITION",
            "category": "Aliment complet",
            "audience": "Porcs — Finition"
        }
    },
    {
        "file": "aliment_truie_gestante.html",
        "slug": "truie-gestante",
        "seo": {
            "title": "Aliment Truie Gestante | MARIDAV CI",
            "description": "Ration gestation équilibrée pour truies : fibres structurantes, minéraux biodisponibles et soutien de la prolificité.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
        },
        "breadcrumbs": [
            {"label": "Porcs", "url": "porcins_maridav_ci.html"},
            {"label": "Aliments complets"}
        ],
        "hero": {
            "badges": ["Truies", "Gestation", "Aliment complet"],
            "title": "Aliment Truie Gestante — Lot homogène & prolificité",
            "description": "Formule riche en fibres digestibles, vitamines et minéraux chélatés pour préparer la gestation et la prochaine lactation.",
            "stats": [
                {"value": "2,8 kg", "label": "Ration cible / truie / jour"},
                {"value": "3,2 %", "label": "Fibres digestibles"},
                {"value": "50 kg", "label": "Sac tropicalisé"}
            ],
            "note": "Programmes validés sur élevages partenaires MARIDAV CI (Anyama, 2024).",
            "image": "maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "image_alt": "Aliment truie gestante MARIDAV",
            "media_title": "Suivi reproduction",
            "media_points": [
                "Courbe d’état corporel",
                "Plan lumière gestation",
                "Checklist mise-bas"
            ]
        },
        "trust": [
            {"label": "Distribution", "text": "Grand Abidjan, Sud et Centre via réseau MARIDAV"},
            {"label": "Sourcing", "text": "Fibres sélectionnées et minéraux DSM/Trouw"},
            {"label": "Support", "text": "Techniciens reproduction & nutrition truis"}
        ],
        "benefits": {
            "eyebrow": "Promesse produit",
            "title": "Préparez des truies performantes",
            "features": [
                {"icon": "bi-heart", "title": "Santé métabolique", "text": "Fibres structurelles pour limiter l’appétit excessif et éviter les constipations."},
                {"icon": "bi-layers", "title": "Minéraux biodisponibles", "text": "Calcium, phosphore et oligo-éléments chélatés pour soutenir squelette & prolificité."},
                {"icon": "bi-activity", "title": "Préparation à la lactation", "text": "Profil vitaminique renforcé (A, D3, E, biotine) pour des mamelles saines."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Noyaux reproducteurs cherchant un programme clé en main.",
                "Élevages industriels voulant uniformiser l’état corporel.",
                "Producteurs semi-intensifs souhaitant limiter les pertes en gestation."
            ],
            "badges": ["Truies", "Gestation", "Fibres"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs ajustées selon disponibilité des fibres locales (son de blé, coprah, etc.).",
            "rows": [
                {"label": "Énergie métabolisable", "value": "2 850 kcal/kg"},
                {"label": "Protéines brutes", "value": "14 %"},
                {"label": "Fibres brutes", "value": "7 %"},
                {"label": "Calcium / Phosphore digestible", "value": "0,90 % / 0,40 %"},
                {"label": "Additifs", "value": "Antioxydants, vitamines, oligo-éléments chélatés"}
            ]
        },
        "usage": {
            "title": "Programme conseillé",
            "note": "Toujours adapter la ration selon l’état corporel (BCS) et la saison.",
            "steps": [
                {"badge": "J0-J28", "title": "Phase implantation", "text": "Distribuer 2,4 – 2,6 kg/jour, surveiller la prise alimentaire."},
                {"badge": "J29-J90", "title": "Gestation milieu", "text": "2,6 – 2,8 kg/jour, ajustements selon BCS (cible 3)."},
                {"badge": "J90-Mise bas", "title": "Préparation lactation", "text": "Augmenter progressivement à 3 kg/jour et ajouter laxatif naturel."}
            ]
        },
        "logistics": {
            "title": "Livraison & services",
            "items": [
                {"icon": "bi-bag-plus", "title": "Sac 50 kg", "text": "Stockage sur palettes, zone ventilée."},
                {"icon": "bi-clipboard-heart", "title": "Plan d’alimentation", "text": "Fiches de ration fournies par poids / stade."},
                {"icon": "bi-people", "title": "Coaching reproduction", "text": "Visites terrain pour suivi prolificité."}
            ]
        },
        "resources": {
            "title": "Ressources truies",
            "intro": "Demandes de fiches techniques, planning de ration et guides de préparation mise bas."
        },
        "lead": {
            "title": "Parler à un expert reproduction",
            "intro": "Nous vous accompagnons sur la conduite des truies gestantes.",
            "name_label": "Nom &amp; structure d'exploitation",
            "name_placeholder": "Ex : Elevage Porcin d'Anyama",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de truies gestantes",
            "volume_placeholder": "Ex : 350 truies",
            "objective_label": "Objectif",
            "objectives": [
                "Stabiliser l’état corporel",
                "Améliorer la prolificité",
                "Préparer la lactation",
                "Former mon équipe"
            ],
            "cta": "Recevoir un plan truies"
        },
        "cta": {
            "title": "Renforcez vos truies gestantes",
            "text": "Planifiez un audit nutritionnel avec MARIDAV CI.",
            "primary_label": "Demander un audit",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quelle ration cible en gestation ?", "answer": "Entre 2,4 et 3,0 kg selon le stade et l’état corporel. Nous fournissons des tableaux personnalisés."},
            {"question": "Faut-il ajouter des fibres ?", "answer": "La formule inclut déjà des fibres structurantes. Évitez les surcharges qui diluent l’énergie."},
            {"question": "Comment éviter les constipations ?", "answer": "Hydratez correctement, maintenez un apport en fibres et ajoutez un laxatif naturel J-5 avant mise bas."}
        ],
        "schema": {
            "name": "Aliment Truie Gestante",
            "description": "Aliment complet gestation pour truies distribué par MARIDAV Côte d’Ivoire.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "sku": "TRUIE-GESTANTE",
            "category": "Aliment complet",
            "audience": "Truies — Gestation"
        }
    },
    {
        "file": "aliment_truie_allaitante_maridav_ci.html",
        "slug": "truie-allaitante",
        "seo": {
            "title": "Aliment Truie Allaitante | MARIDAV CI",
            "description": "Aliment complet lactation riche en énergie et acides aminés pour soutenir des portées nombreuses et limiter la perte d’état corporel.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
        },
        "breadcrumbs": [
            {"label": "Porcs", "url": "porcins_maridav_ci.html"},
            {"label": "Aliments complets"}
        ],
        "hero": {
            "badges": ["Truies", "Lactation", "Aliment complet"],
            "title": "Aliment Truie Allaitante — Lait & vitalité",
            "description": "Ration haute énergie et acides aminés digestibles pour maximiser la production laitière et protéger la condition des truies.",
            "stats": [
                {"value": "3 300 kcal", "label": "Énergie métabolisable"},
                {"value": "18 %", "label": "Protéines brutes"},
                {"value": "10 kg", "label": "Gain moyen porté visé"}
            ],
            "note": "Recommandations basées sur élevages MARIDAV CI (Yamoussoukro, 2024).",
            "image": "maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "image_alt": "Sacs aliment truie allaitante MARIDAV",
            "media_title": "Support maternité",
            "media_points": [
                "Plan d’alimentation lactation",
                "Suivi pertes d’état corporel",
                "Formation équipes maternité"
            ]
        },
        "trust": [
            {"label": "Distribution", "text": "Sites MARIDAV & réseau distributeurs nationaux"},
            {"label": "Nutrition", "text": "Formulation DSM/Trouw avec additifs digestifs"},
            {"label": "Accompagnement", "text": "Techniciens MARIDAV CI (lactation & sevrage)"}
        ],
        "benefits": {
            "eyebrow": "Promesse produit",
            "title": "Des porcelets vigoureux",
            "features": [
                {"icon": "bi-lightning-charge", "title": "Énergie disponible", "text": "Densité énergétique élevée pour soutenir les portées nombreuses."},
                {"icon": "bi-droplet-half", "title": "Production laitière", "text": "Acides aminés digestibles (Lysine 1,1 %, Thréonine, Valine) pour booster le lait."},
                {"icon": "bi-shield-plus", "title": "Soutien immunitaire", "text": "Vitamines, oligo-éléments et antioxydants pour minimiser les mammites et troubles métaboliques."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Élevages hyperprolifiques recherchant une ration sécurisée.",
                "Fermes souhaitant limiter la perte d’état corporel des truies.",
                "Producteurs qui veulent réduire la mortalité pré-sevrage."
            ],
            "badges": ["Truies", "Lactation"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Ajustements possibles selon matières premières disponibles tout en conservant la densité nutritionnelle cible.",
            "rows": [
                {"label": "Énergie métabolisable", "value": "3 250 – 3 300 kcal/kg"},
                {"label": "Protéines brutes", "value": "18 %"},
                {"label": "Lysine digestible", "value": "1,10 %"},
                {"label": "Valine digestible", "value": "0,90 %"},
                {"label": "Calcium / Phosphore digestible", "value": "0,85 % / 0,45 %"}
            ]
        },
        "usage": {
            "title": "Programme conseillé",
            "note": "Assurer une eau fraîche et abondante (>15 L/jour).",
            "steps": [
                {"badge": "Pré-mise bas", "title": "Montée progressive", "text": "Commencez 10 jours avant mise bas par 2,5 kg/jour, puis augmentez après la mise bas."},
                {"badge": "J0-J7", "title": "Lactation début", "text": "Augmentez de 0,5 kg/jour pour atteindre 6-7 kg selon taille de portée."},
                {"badge": "J8-sevrage", "title": "Phase pic de lait", "text": "Distribuer à volonté (jusqu’à 9 kg) en fractionnant les repas."}
            ]
        },
        "logistics": {
            "title": "Logistique & services",
            "items": [
                {"icon": "bi-bag-heart", "title": "Sac 50 kg", "text": "Stockage conseillé dans un local ventilé et sec."},
                {"icon": "bi-clipboard-data", "title": "Plan d’alimentation", "text": "Tableaux fournis selon nombre de porcelets et stade."},
                {"icon": "bi-headset", "title": "Accompagnement", "text": "Support WhatsApp + visites techniques."}
            ]
        },
        "resources": {
            "title": "Guides maternité",
            "intro": "Checklists mise bas, protocoles de conduite et fiches nutrition disponibles."
        },
        "lead": {
            "title": "Obtenir un plan lactation",
            "intro": "Nous dimensionnons vos rations selon la prolificité et l’état corporel.",
            "name_label": "Nom &amp; structure d'exploitation",
            "name_placeholder": "Ex : Ferme maternité de Bouaké",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de truies en lactation",
            "volume_placeholder": "Ex : 180 truies",
            "objective_label": "Objectif",
            "objectives": [
                "Augmenter la production laitière",
                "Limiter la perte d’état corporel",
                "Optimiser le sevrage",
                "Former l’équipe maternité"
            ],
            "cta": "Recevoir un plan lactation"
        },
        "cta": {
            "title": "Boostez vos truies allaitantes",
            "text": "Nos experts MARIDAV CI accompagnent vos maternités pour sécuriser la lactation.",
            "primary_label": "Contacter un expert",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Comment ajuster la ration selon la portée ?", "answer": "Comptez +0,5 kg d’aliment par porcelet au-delà de 10, en surveillant l’état corporel."},
            {"question": "Peut-on distribuer en 2 repas ?", "answer": "Nous recommandons 3 à 4 apports pour limiter les refus et soutenir la digestion."},
            {"question": "Comment préparer le retour en saillie ?", "answer": "Réduisez progressivement la ration après sevrage puis passez sur un aliment flushing. Contactez-nous pour les détails."}
        ],
        "schema": {
            "name": "Aliment Truie Allaitante",
            "description": "Aliment complet lactation pour truies distribué par MARIDAV Côte d’Ivoire.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_complets/aliments_complets.jpg",
            "sku": "TRUIE-ALLAITANTE",
            "category": "Aliment complet",
            "audience": "Truies — Lactation"
        }
    },
    {
        "file": "porc_demarrage.html",
        "slug": "concentre-demarrage",
        "seo": {
            "title": "Concentré Porc Démarrage 5 % | MARIDAV CI",
            "description": "Concentré 5 % pour fabriquer un aliment démarrage performant avec vos matières premières locales.",
            "image": "https://maridav.ci/maridav_ci_image/concentres/hendrix.webp",
        },
        "breadcrumbs": [
            {"label": "Porcs", "url": "porcins_maridav_ci.html"},
            {"label": "Concentrés"}
        ],
        "hero": {
            "badges": ["Porcs", "Démarrage", "Concentré 5 %"],
            "title": "Concentré Porc Démarrage 5 %",
            "description": "Base vitamines, minéraux et additifs de qualité DSM/Trouw pour vos fabrications locales 7–25 kg.",
            "stats": [
                {"value": "5 %", "label": "Inclusion recommandée"},
                {"value": "22 %", "label": "Protéines visées (formulation finale)"},
                {"value": "25 kg", "label": "Sac"}
            ],
            "note": "Recettes validées avec maïs ivoirien et tourteau soja importé.",
            "image": "maridav_ci_image/concentres/hendrix.webp",
            "image_alt": "Concentré porcin MARIDAV",
            "media_title": "Starter kit formulation",
            "media_points": [
                "Recettes détaillées",
                "Suivi FCR",
                "Contrôle qualité matières"
            ]
        },
        "trust": [
            {"label": "Clients", "text": "Meuniers régionaux, fermes intégrées"},
            {"label": "Sourcing", "text": "DSM/Trouw + additifs Biomin"},
            {"label": "Support", "text": "Techniciens formulation & appui QA"}
        ],
        "benefits": {
            "eyebrow": "Pourquoi ce concentré",
            "title": "Formuler efficacement vos aliments",
            "features": [
                {"icon": "bi-gear", "title": "Recettes clé en main", "text": "Tableaux maïs/soja + additifs pour calibrer vos formulations."},
                {"icon": "bi-shield-lock", "title": "Sécurité sanitaire", "text": "Pré-mixé avec acidifiants et antioxydants pour protéger vos fabrications."},
                {"icon": "bi-graph-up-arrow", "title": "Performance assurée", "text": "Profil amino conforme aux standards internationaux."}
            ]
        },
        "audience": {
            "title": "Pour qui ?",
            "items": [
                "Fabricants d’aliments souhaitant maîtriser leur ration démarrage.",
                "Fermes équipées d’un broyeur-mélangeur.",
                "Coopératives voulant mutualiser les matières premières."
            ],
            "badges": ["Meunerie", "Porcelets", "5 %"]
        },
        "composition": {
            "title": "Ingrédients clés",
            "intro": "Mélange complet d’acides aminés, vitamines et oligo-éléments.",
            "rows": [
                {"label": "Acides aminés", "value": "Lysine, Méthionine, Thréonine, Tryptophane"},
                {"label": "Minéraux", "value": "Calcium, Phosphore, Sodium, Zinc, Cuivre, Sélénium"},
                {"label": "Additifs", "value": "Enzymes, antioxydants, acidifiants"},
                {"label": "Portion d’inclusion", "value": "5 % de la ration totale"},
                {"label": "Conditionnement", "value": "Sac 25 kg hermétique"}
            ]
        },
        "usage": {
            "title": "Mode d’emploi",
            "note": "Suivez les recettes MARIDAV CI pour garantir l’équilibre final.",
            "steps": [
                {"badge": "1", "title": "Peser correctement", "text": "Ajouter 5 % de concentré à vos matières (ex : 50 kg dans 1 tonne)."},
                {"badge": "2", "title": "Mélanger uniformément", "text": "Broyeur-mélangeur ou mélangeur horizontal recommandé."},
                {"badge": "3", "title": "Stocker à l’abri", "text": "Conserver la ration finale dans des sacs propres et secs."}
            ]
        },
        "logistics": {
            "title": "Services associés",
            "items": [
                {"icon": "bi-rulers", "title": "Recettes personnalisées", "text": "Adaptées à vos matières premières analysées."},
                {"icon": "bi-flask", "title": "Contrôle labo", "text": "Support analyses EM/protéines/mycotoxines."},
                {"icon": "bi-people", "title": "Formation", "text": "Sessions meunerie et hygiène des lignes."}
            ]
        },
        "resources": {
            "title": "Documentation formulation",
            "intro": "Fiches recettes, guide d’hygiène meunerie et suivi FCR."
        },
        "lead": {
            "title": "Parler à un expert formulation",
            "intro": "Transmettez vos matières et vos objectifs, nous fournirons les recettes adaptées.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Meunerie d'Azaguié",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Volume à formuler (tonnes/mois)",
            "volume_placeholder": "Ex : 30 tonnes/mois",
            "objective_label": "Objectif",
            "objectives": [
                "Recevoir des recettes 5 %",
                "Analyser mes matières",
                "Mettre en place un QA meunerie",
                "Optimiser la FCR"
            ],
            "cta": "Recevoir une recette"
        },
        "cta": {
            "title": "Internalisez vos fabrications",
            "text": "Avec le concentré MARIDAV CI, vous gardez la main sur la qualité de vos aliments démarrage.",
            "primary_label": "Demander une recette",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quelles matières premières utiliser ?", "answer": "Maïs, tourteau soja, huile végétale, minéraux locaux selon la recette fournie."},
            {"question": "Peut-on descendre en dessous de 5 % ?", "answer": "Non, l’inclusion de 5 % garantit l’apport complet en vitamines/minéraux/additifs."},
            {"question": "Proposez-vous les analyses ?", "answer": "Oui, nous pouvons analyser vos matières pour adapter la recette."}
        ],
        "schema": {
            "name": "Concentré Porc Démarrage 5 %",
            "description": "Concentré 5 % pour aliment démarrage porcs produit par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/concentres/hendrix.webp",
            "sku": "CONC-PORC-DEM-5",
            "category": "Concentré porcin",
            "audience": "Porcs — Préparateurs d’aliments"
        }
    },
    {
        "file": "porc_croissance_05.html",
        "slug": "concentre-croissance",
        "seo": {
            "title": "Concentré Porc Croissance 5 % | MARIDAV CI",
            "description": "Concentré 5 % pour fabriquer vos aliments croissance 25–70 kg avec vos matières premières locales.",
            "image": "https://maridav.ci/maridav_ci_image/concentres/hendrix.webp",
        },
        "breadcrumbs": [
            {"label": "Porcs", "url": "porcins_maridav_ci.html"},
            {"label": "Concentrés"}
        ],
        "hero": {
            "badges": ["Porcs", "Croissance", "Concentré 5 %"],
            "title": "Concentré Porc Croissance 5 %",
            "description": "Solution complète en vitamines, minéraux et additifs pour produire vos aliments croissance performants.",
            "stats": [
                {"value": "5 %", "label": "Inclusion"},
                {"value": "16 %", "label": "Protéines visées (ration finale)"},
                {"value": "25 kg", "label": "Sac"}
            ],
            "note": "Fournit le profil idéal pour des rations locales homogènes.",
            "image": "maridav_ci_image/concentres/hendrix.webp",
            "image_alt": "Sac concentré croissance MARIDAV",
            "media_title": "Kit formulation croissance",
            "media_points": [
                "Recettes maïs/soja",
                "Support analytique",
                "Calculateur coût alimentaire"
            ]
        },
        "trust": [
            {"label": "Réseau", "text": "Meuniers côtiers & nord, intégrateurs régionaux"},
            {"label": "Normes", "text": "DSM/Trouw + additifs Biomin"},
            {"label": "Assistance", "text": "Techniciens formulation MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Pourquoi l’adopter",
            "title": "Flexibilité & performance",
            "features": [
                {"icon": "bi-cpu", "title": "Recettes modulables", "text": "S’adapte à vos matières (maïs jaune/blanc, tourteaux) avec corrections EM."},
                {"icon": "bi-activity", "title": "Profil amino maîtrisé", "text": "Garantit lysine/thréonine conformes aux standards internationaux."},
                {"icon": "bi-water", "title": "Sécurité sanitaire", "text": "Intègre acidifiants et antioxydants pour protéger vos fabriqués."}
            ]
        },
        "audience": {
            "title": "Pour qui ?",
            "items": [
                "Meuniers souhaitant rester autonomes sur la ration croissance.",
                "Groupements d’éleveurs mutualisant un broyeur-mélangeur.",
                "Fermes mixtes voulant ajuster la formulation selon les prix."
            ],
            "badges": ["Concentré", "5 %", "25–70 kg"]
        },
        "composition": {
            "title": "Ingrédients & additifs",
            "intro": "Paquet complet d’acides aminés, minéraux et enzyme pour 5 % d’inclusion.",
            "rows": [
                {"label": "Acides aminés", "value": "Lysine, Méthionine, Thréonine, Valine"},
                {"label": "Minéraux", "value": "Macro & oligo éléments chélatés"},
                {"label": "Vitamines", "value": "A, D3, E, B-complexe"},
                {"label": "Additifs", "value": "Enzymes, antioxydants, acidifiants"},
                {"label": "Portion", "value": "50 kg pour 1 tonne d’aliment"}
            ]
        },
        "usage": {
            "title": "Mode d’emploi",
            "note": "Suivez nos fiches de formulation pour garantir l’équilibre final.",
            "steps": [
                {"badge": "1", "title": "Pesée & dosage", "text": "Incorporer 5 % du concentré dans chaque lot."},
                {"badge": "2", "title": "Mélange homogène", "text": "Mélangeur horizontal ou vertical entretenu."},
                {"badge": "3", "title": "Contrôles réguliers", "text": "Vérifier l’humidité et conserver des échantillons."}
            ]
        },
        "logistics": {
            "title": "Services MARIDAV",
            "items": [
                {"icon": "bi-hammer", "title": "Paramétrage ligne", "text": "Support à l’installation / réglage des mélangeurs."},
                {"icon": "bi-search", "title": "Audit formulation", "text": "Vérification des recettes et ajustements EM."},
                {"icon": "bi-currency-dollar", "title": "Suivi coût alimentaire", "text": "Tableurs fournis pour suivre vos marges."}
            ]
        },
        "resources": {
            "title": "Guides formulation",
            "intro": "Fiches recettes, guides mixité et bonnes pratiques d’hygiène meunerie."
        },
        "lead": {
            "title": "Obtenir mes recettes croissance",
            "intro": "Envoyez les analyses de vos matières pour recevoir la recette calibrée.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Coopérative de Bouaké",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Volume mensuel (tonnes)",
            "volume_placeholder": "Ex : 50 tonnes/mois",
            "objective_label": "Objectif",
            "objectives": [
                "Recevoir des recettes",
                "Auditer ma ligne",
                "Optimiser ma FCR",
                "Contrôler mes matières"
            ],
            "cta": "Recevoir une recette"
        },
        "cta": {
            "title": "Gardez la main sur vos rations",
            "text": "Avec le concentré 5 %, produisez localement sans sacrifier la performance.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quelles matières sont compatibles ?", "answer": "Maïs, sorgho, tourteaux soja/coton/arachide. Nous adaptons les recettes selon vos analyses."},
            {"question": "Puis-je ajouter des additifs supplémentaires ?", "answer": "Le concentré est complet. Ajoutez seulement si validé par notre équipe technique."},
            {"question": "Quel est le délai de conservation ?", "answer": "12 mois en sac fermé. Refermez soigneusement après ouverture et stockez dans un local sec."}
        ],
        "schema": {
            "name": "Concentré Porc Croissance 5 %",
            "description": "Concentré 5 % pour aliment croissance porcs, proposé par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/concentres/hendrix.webp",
            "sku": "CONC-PORC-CROISS-5",
            "category": "Concentré porcin",
            "audience": "Porcs — Fabricants d’aliments"
        }
    },
    {
        "file": "truie_porcs_05.html",
        "slug": "concentre-truie",
        "seo": {
            "title": "Concentré Truie 5 % | MARIDAV CI",
            "description": "Concentré 5 % pour ration truies gestantes/allaitantes, afin de fabriquer localement vos aliments reproduction.",
            "image": "https://maridav.ci/maridav_ci_image/concentres/hendrix.webp",
        },
        "breadcrumbs": [
            {"label": "Porcs", "url": "porcins_maridav_ci.html"},
            {"label": "Concentrés"}
        ],
        "hero": {
            "badges": ["Truies", "Gestation & lactation", "Concentré 5 %"],
            "title": "Concentré Truie 5 %",
            "description": "Kit complet en vitamines, minéraux et additifs pour vos fabrications truies reproduction.",
            "stats": [
                {"value": "5 %", "label": "Inclusion recommandée"},
                {"value": "Fibres & minéraux", "label": "Profil spécialisé"},
                {"value": "25 kg", "label": "Sac"}
            ],
            "note": "Compatible avec aliments gestation et lactation.",
            "image": "maridav_ci_image/concentres/hendrix.webp",
            "image_alt": "Concentré truie MARIDAV",
            "media_title": "Support reproduction",
            "media_points": [
                "Recettes gestation",
                "Recettes lactation",
                "Planification rations"
            ]
        },
        "trust": [
            {"label": "Normes", "text": "Base DSM/Trouw validée par les équipes reproduction MARIDAV"},
            {"label": "Support", "text": "Formulation + suivi état corporel"},
            {"label": "Sécurité", "text": "Antioxydants et acidifiants intégrés"}
        ],
        "benefits": {
            "eyebrow": "Avantages",
            "title": "Formule reproduction prête à l’emploi",
            "features": [
                {"icon": "bi-heart-pulse", "title": "Soutien métabolique", "text": "Fournit vitamines et oligo-éléments essentiels aux truies."},
                {"icon": "bi-diagram-2", "title": "Flexibilité", "text": "Permet de fabriquer autant la ration gestante que lactation en adaptant les matières locales."},
                {"icon": "bi-umbrella", "title": "Protection", "text": "Additifs antimycotoxines et antioxydants pour sécuriser vos rations."}
            ]
        },
        "audience": {
            "title": "Pour qui ?",
            "items": [
                "Fermes reproductrices voulant garder la main sur l’alimentation truies.",
                "Coopératives disposant d’une ligne meunerie.",
                "Intégrateurs adaptant la ration selon les saisons."
            ],
            "badges": ["Truies", "Concentré", "5 %"]
        },
        "composition": {
            "title": "Ingrédients majeurs",
            "intro": "Inclut acides aminés, vitamines, minéraux & fibres fonctionnelles.",
            "rows": [
                {"label": "Complexe vitaminique", "value": "A, D3, E, K, B, biotine"},
                {"label": "Oligo-éléments", "value": "Cuivre, fer, zinc, manganèse, sélénium"},
                {"label": "Acides aminés", "value": "Lysine, Méthionine, Thréonine"},
                {"label": "Additifs", "value": "Antioxydants, capteurs mycotoxines, acidifiants"},
                {"label": "Fibres fonctionnelles", "value": "Sources destinées au confort digestif"}
            ]
        },
        "usage": {
            "title": "Mode d’emploi",
            "note": "Respecter les recettes transmises par MARIDAV CI.",
            "steps": [
                {"badge": "1", "title": "Pesée", "text": "Intégrer 5 % dans chaque tonne d’aliment truie."},
                {"badge": "2", "title": "Mélange", "text": "Assurer un mélange homogène (plusieurs cycles si besoin)."},
                {"badge": "3", "title": "Recettes", "text": "Utiliser les fiches gestation/lactation fournies selon vos objectifs."}
            ]
        },
        "logistics": {
            "title": "Services associés",
            "items": [
                {"icon": "bi-people", "title": "Coaching reproduction", "text": "Support sur les rations gestation/lactation."},
                {"icon": "bi-clipboard-check", "title": "Audit nutrition", "text": "Analyse de vos rations existantes et suggestions d’amélioration."},
                {"icon": "bi-diagram-3", "title": "Planification", "text": "Aide à structurer les courbes d’alimentation truies."}
            ]
        },
        "resources": {
            "title": "Fiches truies",
            "intro": "Recettes, guides gestation & lactation, checklists reproduction."
        },
        "lead": {
            "title": "Recevoir des recettes truies",
            "intro": "Contactez-nous pour adapter le concentré à vos matières premières.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme truies Abengourou",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Volume mensuel (tonnes)",
            "volume_placeholder": "Ex : 20 tonnes/mois",
            "objective_label": "Objectif",
            "objectives": [
                "Formuler ration gestante",
                "Formuler ration lactation",
                "Analyser mes matières",
                "Former mes équipes"
            ],
            "cta": "Recevoir mes recettes"
        },
        "cta": {
            "title": "Personnalisez vos rations truies",
            "text": "Le concentré 5 % MARIDAV CI vous garantit constance et performance.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Peut-on utiliser le même concentré pour gestation et lactation ?", "answer": "Oui, il suffit d’adapter les matières énergétiques selon la recette fournie."},
            {"question": "Offrez-vous un accompagnement formulation ?", "answer": "Nos nutritionnistes fournissent recettes et suivis réguliers selon vos matières."},
            {"question": "Quel stockage pour le concentré ?", "answer": "Local sec, ventilé, sur palettes. Refermez les sacs entamés et consommez dans les 12 mois."}
        ],
        "schema": {
            "name": "Concentré Truie 5 %",
            "description": "Concentré reproduction 5 % pour truies, formulé par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/concentres/hendrix.webp",
            "sku": "CONC-TRUIE-5",
            "category": "Concentré truies",
            "audience": "Truies — Fabricants d’aliments"
        }
    },
    {
        "file": "biotronic_top3_maridav_ci.html",
        "slug": "biotronic-top3",
        "seo": {
            "title": "Biotronic® Top3 — Acides organiques | MARIDAV CI",
            "description": "Additif acides organiques + phytogéniques pour sécuriser l’intestin des monogastriques et améliorer la performance.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Biotronic Top3 Maridav.png",
        },
        "breadcrumbs": [
            {"label": "Additifs", "url": "additifs/index.html"},
            {"label": "Biotronic Top3"}
        ],
        "hero": {
            "badges": ["Additif", "Acides organiques", "Multi-espèces"],
            "title": "Biotronic® Top3",
            "description": "Synergie d’acides organiques et d’huiles essentielles pour protéger l’intestin et améliorer la conversion alimentaire.",
            "stats": [
                {"value": "-0,05", "label": "Points de FCR observés"},
                {"value": "0,5–1,0 kg/t", "label": "Dosage standard"},
                {"value": "25 kg", "label": "Sac"}
            ],
            "note": "Résultats observés sur élevages MARIDAV CI volailles & porcs.",
            "image": "maridav_ci_image/additifs _alimentaires/Biotronic Top3 Maridav.png",
            "image_alt": "Sacs Biotronic Top3",
            "media_title": "Protection intestinale",
            "media_points": [
                "Contrôle Salmonella / E. coli",
                "Stabilisation FCR",
                "Amélioration ingestion"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Produit BIOMIN (DSM) distribué par MARIDAV CI"},
            {"label": "Usages", "text": "Volailles, porcs, ruminants & aquaculture"},
            {"label": "Support", "text": "Techniciens MARIDAV pour les dosages et suivis"}
        ],
        "benefits": {
            "eyebrow": "Pourquoi Biotronic Top3",
            "title": "Un additif 3 en 1",
            "features": [
                {"icon": "bi-shield-lock", "title": "Hygiène alimentaire", "text": "Réduit la charge bactérienne dans l’aliment et le tractus digestif."},
                {"icon": "bi-droplet", "title": "Microflore équilibrée", "text": "Stimule les bactéries bénéfiques grâce aux huiles essentielles encapsulées."},
                {"icon": "bi-graph-up", "title": "Performance améliorée", "text": "Meilleure digestibilité des nutriments, baisse de la FCR et gain de GMQ."}
            ]
        },
        "audience": {
            "title": "Espèces ciblées",
            "items": [
                "Poulets de chair, pondeuses, dindes",
                "Porcelets, porcs en croissance, truies",
                "Ruminants & poissons (usage via ration)"
            ],
            "badges": ["Volailles", "Porcs", "Ruminants", "Aquaculture"]
        },
        "composition": {
            "title": "Composition fonctionnelle",
            "intro": "Association d’acides organiques, de sels organiques et de phytogéniques.",
            "rows": [
                {"label": "Acide formique / propionique", "value": "Contrôle pathogènes"},
                {"label": "Sels organiques", "value": "Libération ciblée dans l’intestin"},
                {"label": "Huiles essentielles", "value": "Effet synergique sur la microflore"},
                {"label": "Support minéral", "value": "Protège les actifs jusqu’à l’intestin"},
                {"label": "Conditionnement", "value": "Sac 25 kg ou 5 kg"}
            ]
        },
        "usage": {
            "title": "Dosages & recommandations",
            "note": "Se référer aux fiches techniques selon espèce et âge.",
            "steps": [
                {"badge": "Volailles", "title": "0,5 – 1 kg/t d’aliment", "text": "Incorporer directement dans l’aliment ou pré-mix."},
                {"badge": "Porcs", "title": "0,7 – 1,2 kg/t", "text": "Porcelets et croissance : ajuster selon pression sanitaire."},
                {"badge": "Ruminants / Aqua", "title": "Selon ration", "text": "Consultez votre technicien MARIDAV CI pour le dosage précis."}
            ]
        },
        "logistics": {
            "title": "Logistique & support",
            "items": [
                {"icon": "bi-bag", "title": "Formats", "text": "Sacs 5 kg / 25 kg scellés."},
                {"icon": "bi-headset", "title": "Accompagnement", "text": "Formation des équipes sur les dosages."},
                {"icon": "bi-layers", "title": "Compatibilité", "text": "S’intègre dans aliment complet ou prémix."}
            ]
        },
        "resources": {
            "title": "Documents additifs",
            "intro": "Fiches techniques, études de cas et protocoles d’utilisation disponibles."
        },
        "lead": {
            "title": "Parler à un expert additifs",
            "intro": "Nous définissons avec vous le dosage selon l’espèce et la pression sanitaire.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme Avicole d'Anyama",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Volume d’aliment à traiter (t/mois)",
            "volume_placeholder": "Ex : 40 tonnes/mois",
            "objective_label": "Objectif",
            "objectives": [
                "Réduire la FCR",
                "Sécuriser mon aliment",
                "Contrôler Salmonella",
                "Améliorer la digestibilité"
            ],
            "cta": "Recevoir un plan additifs"
        },
        "cta": {
            "title": "Sécurisez vos rations",
            "text": "Biotronic® Top3 est disponible en Côte d’Ivoire via MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Biotronic Top3 remplace-t-il un antibiotique ?", "answer": "Non, il s’agit d’un additif nutritionnel qui soutient la santé intestinale et réduit la pression bactérienne."},
            {"question": "Peut-on l’utiliser en même temps qu’un probiotique ?", "answer": "Oui, il est compatible avec les probiotiques et autres additifs nutritionnels."},
            {"question": "Comment l’intégrer dans une ration maison ?", "answer": "Ajoutez-le lors du mélange des matières sèches en respectant la dose recommandée."}
        ],
        "schema": {
            "name": "Biotronic Top3",
            "description": "Additif acides organiques et huiles essentielles pour alimentation animale, distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Biotronic Top3 Maridav.png",
            "sku": "BIOTRONIC-TOP3",
            "category": "Additif nutritionnel",
            "audience": "Multi-espèces"
        }
    },
    {
        "file": "biotronic_top_liquide_maridav_ci.html",
        "slug": "biotronic-top-liquide",
        "seo": {
            "title": "Biotronic® Top Liquid — Acidifiant eau | MARIDAV CI",
            "description": "Acidifiant liquide pour l’eau de boisson : contrôle des bactéries et amélioration de l’ingestion.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Biotronic Top Liquid Maridav.png",
        },
        "breadcrumbs": [
            {"label": "Additifs", "url": "additifs/index.html"},
            {"label": "Biotronic Top Liquid"}
        ],
        "hero": {
            "badges": ["Additif eau", "Acides organiques", "Multi-espèces"],
            "title": "Biotronic® Top Liquid",
            "description": "Acidifiant liquide concentré pour sécuriser l’eau de boisson et améliorer la santé intestinale.",
            "stats": [
                {"value": "0,2–0,5 mL/L", "label": "Dosage standard"},
                {"value": "5 L / 25 L", "label": "Bidons disponibles"},
                {"value": "pH cible 3,5–4", "label": "Adapté aux réseaux fermiers"}
            ],
            "note": "Compatible avec chenaux, pipettes et brumisateurs.",
            "image": "maridav_ci_image/additifs _alimentaires/Biotronic Top Liquid Maridav.png",
            "image_alt": "Bidon Biotronic Top Liquid",
            "media_title": "Hygiène eau",
            "media_points": [
                "Contrôle E. coli & Salmonella",
                "Maintien du pH",
                "Amélioration ingestion"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Produit BIOMIN (DSM) distribué par MARIDAV CI"},
            {"label": "Sécurité", "text": "Formule non corrosive pour équipements"},
            {"label": "Support", "text": "Paramétrage des pompes doseuses par nos équipes"}
        ],
        "benefits": {
            "eyebrow": "Pourquoi l’utiliser",
            "title": "Eau saine = performances améliorées",
            "features": [
                {"icon": "bi-droplet", "title": "pH maîtrisé", "text": "Stabilise le pH de l’eau pour limiter le développement bactérien."},
                {"icon": "bi-thermometer", "title": "Confort digestif", "text": "Réduit les risques de diarrhées en climat chaud."},
                {"icon": "bi-graph-up-arrow", "title": "Meilleure ingestion", "text": "Une eau appétente favorise la consommation d’aliment."}
            ]
        },
        "audience": {
            "title": "Espèces ciblées",
            "items": [
                "Volailles (chair & ponte)",
                "Porcs (porcelets, engraissement, truies)",
                "Ruminants & aquaculture (eau de boisson)"
            ],
            "badges": ["Volailles", "Porcs", "Multi-espèces"]
        },
        "composition": {
            "title": "Composition fonctionnelle",
            "intro": "Mélange d’acides organiques liquides (formique, propionique) et de composés synergiques.",
            "rows": [
                {"label": "Acides organiques", "value": "Formique, propionique, acide lactique"},
                {"label": "Agents surfactants", "value": "Permettent une répartition homogène"},
                {"label": "Stabilisants", "value": "Protègent contre la corrosion"},
                {"label": "Compatibilité", "value": "Lignes PVC, inox, pompes doseuses"},
                {"label": "Formats", "value": "Bidons 5 L / 25 L"}
            ]
        },
        "usage": {
            "title": "Dosages & protocole",
            "note": "Nous vous aidons à calibrer les pompes doseuses selon vos équipements.",
            "steps": [
                {"badge": "Préparation", "title": "Dilution", "text": "Diluer dans l’eau propre du bac mère (si pompe doseuse)."},
                {"badge": "Dosage", "title": "0,2 – 0,5 mL/litre", "text": "Adapter selon la qualité d’eau et l’espèce."},
                {"badge": "Contrôle", "title": "Mesure du pH", "text": "Vérifier que l’eau sortant des lignes se situe entre 3,5 et 4,5."}
            ]
        },
        "logistics": {
            "title": "Services MARIDAV CI",
            "items": [
                {"icon": "bi-tools", "title": "Installation", "text": "Aide au réglage des pompes doseuses."},
                {"icon": "bi-droplet-half", "title": "Analyses eau", "text": "Contrôle pH, dureté et charge bactérienne."},
                {"icon": "bi-people", "title": "Formation équipes", "text": "Bonnes pratiques de nettoyage des lignes."}
            ]
        },
        "resources": {
            "title": "Guides hygiène eau",
            "intro": "Protocoles de nettoyage tuyauteries, checklists et fiches d’acidification."
        },
        "lead": {
            "title": "Parler à un expert hygiène eau",
            "intro": "Planifiez un audit eau avec les équipes MARIDAV CI.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme Avicole de Bingerville",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Volume d’eau/jour (m³)",
            "volume_placeholder": "Ex : 12 m³ / jour",
            "objective_label": "Objectif",
            "objectives": [
                "Acidifier mon réseau eau",
                "Nettoyer mes tuyauteries",
                "Installer une pompe doseuse",
                "Former mes équipes"
            ],
            "cta": "Recevoir un protocole"
        },
        "cta": {
            "title": "Sécurisez votre eau de boisson",
            "text": "Biotronic® Top Liquid est disponible avec support terrain MARIDAV CI.",
            "primary_label": "Demander un audit",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Peut-on l’utiliser en continu ?", "answer": "Oui, en ajustant le dosage selon la consommation et le niveau de performance souhaité."},
            {"question": "Est-il compatible avec les vaccins eau ?", "answer": "Suspendez l’acidification durant les traitements ou vaccinations via l’eau."},
            {"question": "Quelle est la durée de conservation ?", "answer": "24 mois en bidon fermé, stocké à l’abri de la chaleur."}
        ],
        "schema": {
            "name": "Biotronic Top Liquid",
            "description": "Acidifiant liquide pour l’eau de boisson distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Biotronic Top Liquid Maridav.png",
            "sku": "BIOTRONIC-LIQUIDE",
            "category": "Additif eau",
            "audience": "Volailles, porcs, multi-espèces"
        }
    },
    {
        "file": "digestarom_maridav_ci.html",
        "slug": "digestarom",
        "seo": {
            "title": "Digestarom® — Phytogénique performance | MARIDAV CI",
            "description": "Mélange d’extraits végétaux pour stimuler l’appétit, la digestibilité et le gain moyen quotidien.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Digestarom Maridav.png",
        },
        "breadcrumbs": [
            {"label": "Additifs", "url": "additifs/index.html"},
            {"label": "Digestarom"}
        ],
        "hero": {
            "badges": ["Additif", "Phytogénique", "Multi-espèces"],
            "title": "Digestarom®",
            "description": "Complexe phytogénique BIOMIN pour améliorer l’appétit, la digestion et la croissance des animaux.",
            "stats": [
                {"value": "+3 %", "label": "Amélioration moyenne du GMQ"},
                {"value": "0,3–1,0 kg/t", "label": "Dosage"},
                {"value": "20 kg", "label": "Sac"}
            ],
            "note": "Effets validés sur volailles et porcs en climat tropical.",
            "image": "maridav_ci_image/additifs _alimentaires/Digestarom Maridav.png",
            "image_alt": "Sacs Digestarom MARIDAV",
            "media_title": "Stimulation phytogénique",
            "media_points": [
                "Odeur appétente",
                "Sécrétion enzymatique",
                "Meilleure conversion"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Produit BIOMIN (DSM)"},
            {"label": "Usage", "text": "Volailles, porcs, ruminants, aqua"},
            {"label": "Support", "text": "Techniciens MARIDAV CI"}
        ],
        "benefits": {
            "eyebrow": "Avantages clés",
            "title": "Améliorez l’ingestion & la digestibilité",
            "features": [
                {"icon": "bi-emoji-smile", "title": "Appétence renforcée", "text": "Arômes naturels qui stimulent la prise d’aliment."},
                {"icon": "bi-wind", "title": "Stimulation enzymatique", "text": "Favorise la sécrétion d’enzymes digestives."},
                {"icon": "bi-bar-chart", "title": "Performance économique", "text": "Hausse du GMQ, baisse de la FCR et meilleur retour sur investissement."}
            ]
        },
        "audience": {
            "title": "Espèces ciblées",
            "items": [
                "Poulets de chair, pondeuses, breeders",
                "Porcelets, croissance, truies",
                "Ruminants & aquaculture (selon formulation)"
            ],
            "badges": ["Phytogénique", "Volailles", "Porcs"]
        },
        "composition": {
            "title": "Composition fonctionnelle",
            "intro": "Mélange d’extraits végétaux sélectionnés : anis, fenouil, menthe, etc.",
            "rows": [
                {"label": "Phytogéniques", "value": "Anis, fenouil, menthe, poivre, autres huiles essentielles"},
                {"label": "Support", "value": "Support minéral pour une libération progressive"},
                {"label": "Stabilisants", "value": "Protègent les composés actifs lors du process"},
                {"label": "Forme", "value": "Poudre fine; version liquide disponible"},
                {"label": "Conditionnement", "value": "Sac 20 kg ou seau 5 kg"}
            ]
        },
        "usage": {
            "title": "Dosages recommandés",
            "note": "Consultez nos fiches pour chaque espèce.",
            "steps": [
                {"badge": "Volailles", "title": "0,3 – 0,5 kg/t", "text": "Renforce l’appétence en période chaude."},
                {"badge": "Porcs", "title": "0,5 – 1,0 kg/t", "text": "Porcelets, croissance et truies."},
                {"badge": "Autres espèces", "title": "Sur devis", "text": "Ruminants, lapins, poissons : contacter MARIDAV CI."}
            ]
        },
        "logistics": {
            "title": "Livraison & support",
            "items": [
                {"icon": "bi-box-seam", "title": "Stock Côte d’Ivoire", "text": "Disponibilité rapide depuis Abidjan."},
                {"icon": "bi-people", "title": "Coaching", "text": "Formation de vos équipes nutrition."},
                {"icon": "bi-journal-richtext", "title": "Études de cas", "text": "Partage de résultats obtenus en climat tropical."}
            ]
        },
        "resources": {
            "title": "Ressources phytogéniques",
            "intro": "Fiches produits, études économiques et recommandations d’incorporation."
        },
        "lead": {
            "title": "Parler à un expert phytogénique",
            "intro": "Nous adaptons le dosage à votre espèce et à vos objectifs.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme Avicole de Grand-Bassam",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Tonnes d’aliment / mois",
            "volume_placeholder": "Ex : 25 tonnes/mois",
            "objective_label": "Objectif",
            "objectives": [
                "Stimuler l’ingestion",
                "Réduire la FCR",
                "Améliorer le GMQ",
                "Tester sur un lot pilote"
            ],
            "cta": "Recevoir un protocole"
        },
        "cta": {
            "title": "Boostez vos performances naturellement",
            "text": "Digestarom® est disponible chez MARIDAV CI avec support terrain.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Est-il compatible avec les antibiotiques ?", "answer": "Oui, mais nous recommandons de privilégier une approche nutritionnelle intégrée avec nos techniciens."},
            {"question": "Peut-on l’utiliser en mash et en granulé ?", "answer": "Oui, les composés sont protégés pour résister au process de granulation."},
            {"question": "Quel retour sur investissement ?", "answer": "En moyenne, 3 à 5 fois le coût de l’additif via l’amélioration FCR / GMQ observée."}
        ],
        "schema": {
            "name": "Digestarom",
            "description": "Additif phytogénique pour améliorer l’appétence et la digestibilité — MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Digestarom Maridav.png",
            "sku": "DIGESTAROM",
            "category": "Additif phytogénique",
            "audience": "Multi-espèces"
        }
    },
    {
        "file": "mycofix_select_3.0.html",
        "slug": "mycofix",
        "seo": {
            "title": "Mycofix® Select 3.0 — Capteur de mycotoxines | MARIDAV CI",
            "description": "Additif premium pour lier et dégrader un large spectre de mycotoxines dans l’aliment.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Mycofix Select Maridav .png",
        },
        "breadcrumbs": [
            {"label": "Additifs", "url": "additifs/index.html"},
            {"label": "Mycofix Select 3.0"}
        ],
        "hero": {
            "badges": ["Additif", "Mycotoxines", "Multi-espèces"],
            "title": "Mycofix® Select 3.0",
            "description": "Protection complète contre les mycotoxines : adsorption, biotransformation et soutien immunitaire.",
            "stats": [
                {"value": "0,5–2 kg/t", "label": "Incorporation selon pression"},
                {"value": "Large spectre", "label": "Aflatoxines, DON, T-2, Fumonisines..."},
                {"value": "25 kg", "label": "Sac"}
            ],
            "note": "Programme DSM/BIOMIN reconnu mondialement.",
            "image": "maridav_ci_image/additifs _alimentaires/Mycofix Select Maridav .png",
            "image_alt": "Sacs Mycofix Select",
            "media_title": "Sécurité mycotoxines",
            "media_points": [
                "Adsorption rapide",
                "Biotransformation enzymatique",
                "Protection organes sensibles"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Mycofix® par DSM/BIOMIN"},
            {"label": "Certification", "text": "HACCP, GMP+, EFSA"},
            {"label": "Support", "text": "MARIDAV CI pour analyses et dosage"}
        ],
        "benefits": {
            "eyebrow": "Pourquoi Mycofix",
            "title": "Une triple action unique",
            "features": [
                {"icon": "bi-shield-check", "title": "Adsorption ciblée", "text": "Capteurs minéraux efficaces sur aflatoxines."},
                {"icon": "bi-lightning", "title": "Biotransformation", "text": "Enzymes spécifiques dégradant DON, T-2, fumonisines."},
                {"icon": "bi-life-preserver", "title": "Soutien immunitaire", "text": "Complexes de bio-protection pour foie et intestin."}
            ]
        },
        "audience": {
            "title": "Espèces ciblées",
            "items": [
                "Volailles (chair, ponte, reproducteurs)",
                "Porcs (porcelets, truies)",
                "Ruminants, aquaculture, animaux de compagnie"
            ],
            "badges": ["Anti-mycotoxines", "Multi-espèces"]
        },
        "composition": {
            "title": "Technologie brevetée",
            "intro": "Combine argiles sélectionnées, levures, enzymes et extraits végétaux.",
            "rows": [
                {"label": "Adsorbants minéraux", "value": "Argiles activées, phyllosilicates"},
                {"label": "Biotransformateurs", "value": "Enzymes spécifiques à chaque mycotoxine"},
                {"label": "Bioprotection", "value": "Extraits végétaux, antioxydants"},
                {"label": "Formats", "value": "Sac 25 kg ou 5 kg"},
                {"label": "Compatibilité", "value": "Prémix, aliment complet, concentré"}
            ]
        },
        "usage": {
            "title": "Schéma d’utilisation",
            "note": "Dosage selon analyses mycotoxines. MARIDAV CI propose un accompagnement complet.",
            "steps": [
                {"badge": "Préventif", "title": "0,5 – 1 kg/t", "text": "Utilisation continue pour sécuriser l’aliment."},
                {"badge": "Curatif", "title": "1 – 2 kg/t", "text": "En cas d’alerte mycotoxine confirmée."},
                {"badge": "Analyses", "title": "Plan d’échantillonnage", "text": "Nous analysons vos matières premières pour ajuster le dosage."}
            ]
        },
        "logistics": {
            "title": "Services MARIDAV",
            "items": [
                {"icon": "bi-flask", "title": "Analyses mycotoxines", "text": "Organisation des prélèvements et interprétation."},
                {"icon": "bi-diagram-3", "title": "Plan mycotoxine", "text": "Protocoles de prévention pour vos silos / entrepôts."},
                {"icon": "bi-people", "title": "Formation", "text": "Sensibilisation des équipes aux risques mycotoxines."}
            ]
        },
        "resources": {
            "title": "Guides mycotoxines",
            "intro": "Fiches techniques, rapports d’analyses régionales, checklists de prévention."
        },
        "lead": {
            "title": "Parler à un expert mycotoxines",
            "intro": "Définissez un plan de prévention avec MARIDAV CI.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Coopérative de Korhogo",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Volume d’aliment/mois",
            "volume_placeholder": "Ex : 60 tonnes/mois",
            "objective_label": "Objectif",
            "objectives": [
                "Mettre en place un plan mycotoxines",
                "Analyser mes matières",
                "Protéger mes reproducteurs",
                "Optimiser mon budget additifs"
            ],
            "cta": "Recevoir un plan mycotoxines"
        },
        "cta": {
            "title": "Sécurisez vos performances",
            "text": "Mycofix® Select 3.0 est disponible en stock chez MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quelle est la différence avec un simple capteur ?", "answer": "Mycofix associe adsorption, biotransformation et bioprotection pour couvrir un large spectre."},
            {"question": "Dois-je l’utiliser toute l’année ?", "answer": "Nous recommandons un usage continu en prévention, avec des doses renforcées en période à risque."},
            {"question": "Est-il compatible avec d’autres additifs ?", "answer": "Oui, il peut être utilisé avec des phytogéniques, probiotiques et acides organiques."}
        ],
        "schema": {
            "name": "Mycofix Select 3.0",
            "description": "Additif anti-mycotoxines multi-voies distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Mycofix Select Maridav .png",
            "sku": "MYCOFIX-3.0",
            "category": "Additif anti-mycotoxines",
            "audience": "Multi-espèces"
        }
    },
    {
        "file": "nutricool_maridav_ci.html",
        "slug": "nutricool",
        "seo": {
            "title": "Nutricool® — Électrolytes anti-stress thermique | MARIDAV CI",
            "description": "Mélange d’électrolytes, vitamines et antioxydants pour soutenir les animaux en période de chaleur.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/NUTRICOOL.png",
        },
        "breadcrumbs": [
            {"label": "Additifs", "url": "additifs/index.html"},
            {"label": "Nutricool"}
        ],
        "hero": {
            "badges": ["Additif", "Électrolytes", "Anti-stress"],
            "title": "Nutricool®",
            "description": "Solution électrolytique premium pour réduire l’impact du stress thermique sur volailles et porcs.",
            "stats": [
                {"value": "Eau", "label": "Distribution via eau de boisson"},
                {"value": "1 g/L", "label": "Dosage courant"},
                {"value": "5 kg", "label": "Seau / sachets"}
            ],
            "note": "Idéal pendant les pics de température et phases de transport.",
            "image": "maridav_ci_image/additifs _alimentaires/NUTRICOOL.png",
            "image_alt": "Seau Nutricool",
            "media_title": "Thermotolérance",
            "media_points": [
                "Restaurer l’équilibre électrolytique",
                "Soutenir l’immunité",
                "Maintenir l’ingestion"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Programme DSM / BIOMIN"},
            {"label": "Espèces", "text": "Volailles, porcs, lapins, ruminants"},
            {"label": "Support", "text": "Techniciens MARIDAV CI pour le protocole"}
        ],
        "benefits": {
            "eyebrow": "Pourquoi Nutricool",
            "title": "Un allié en saison chaude",
            "features": [
                {"icon": "bi-wind", "title": "Hydratation optimale", "text": "Électrolytes équilibrés (Na/K/Cl) pour compenser les pertes."},
                {"icon": "bi-lightbulb", "title": "Vitamines antioxydantes", "text": "Vitamine C & E pour limiter l’oxydation due au stress."},
                {"icon": "bi-heart", "title": "Soutien métabolique", "text": "Appui sur la respiration cellulaire et récupération post-stress."}
            ]
        },
        "audience": {
            "title": "Espèces ciblées",
            "items": [
                "Poulets, dindes, pondeuses",
                "Porcelets, truies, engraissement",
                "Lapins, veaux, ruminants"
            ],
            "badges": ["Anti-stress", "Électrolytes"]
        },
        "composition": {
            "title": "Composition fonctionnelle",
            "intro": "Électrolytes, vitamines et additifs anti-stress.",
            "rows": [
                {"label": "Électrolytes", "value": "Sodium, potassium, chlorure, bicarbonate"},
                {"label": "Vitamines", "value": "Vitamine C, E, B-complexe"},
                {"label": "Additifs", "value": "Acides aminés, antioxydants"},
                {"label": "Formats", "value": "Sachets 1 kg / Seau 5 kg"},
                {"label": "Utilisation", "value": "Eau de boisson ou top dressing"}
            ]
        },
        "usage": {
            "title": "Plan d’utilisation",
            "note": "Adapter le dosage selon l’intensité du stress thermique.",
            "steps": [
                {"badge": "Prévention", "title": "0,5 g/L", "text": "48 h avant un transport ou une vague de chaleur."},
                {"badge": "Curatif", "title": "1 g/L", "text": "Pendant la période de stress thermique."},
                {"badge": "Récupération", "title": "0,5 g/L", "text": "24 h après l’événement."}
            ]
        },
        "logistics": {
            "title": "Services associés",
            "items": [
                {"icon": "bi-brightness-high", "title": "Audit ventilation", "text": "Appui pour réduire la température dans les bâtiments."},
                {"icon": "bi-moisture", "title": "Suivi consommation eau", "text": "Outils de suivi pour détecter les baisses d’ingestion."},
                {"icon": "bi-people", "title": "Formation équipes", "text": "Gestion du stress thermique sur le terrain."}
            ]
        },
        "resources": {
            "title": "Guides anti-chaleur",
            "intro": "Fiches pratiques, checklists ventilation et protocoles Nutricool."
        },
        "lead": {
            "title": "Parler à un expert stress thermique",
            "intro": "Partagez vos pics de mortalité ou baisses de performances pour recevoir un plan.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Elevage Chair d'Abidjan",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre d’animaux concernés",
            "volume_placeholder": "Ex : 12 000 poulets",
            "objective_label": "Objectif",
            "objectives": [
                "Réduire la mortalité chaleur",
                "Stabiliser l’ingestion",
                "Préparer un transport",
                "Former l’équipe"
            ],
            "cta": "Recevoir un plan Nutricool"
        },
        "cta": {
            "title": "Affrontez les vagues de chaleur",
            "text": "Nutricool® est disponible en stock pour sécuriser vos élevages.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Peut-on l’utiliser en continu ?", "answer": "Préférez des cures ciblées. En période très chaude, vous pouvez l’utiliser plusieurs jours d’affilée."},
            {"question": "Compatible avec les vaccins ?", "answer": "Suspendre Nutricool pendant les vaccinations ou traitements via l’eau."},
            {"question": "Convient-il aux reproducteurs ?", "answer": "Oui, adapter la dose avec nos techniciens selon l’espèce et l’objectif."}
        ],
        "schema": {
            "name": "Nutricool",
            "description": "Électrolytes et vitamines anti-stress thermique — MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/NUTRICOOL.png",
            "sku": "NUTRICOOL",
            "category": "Additif électrolytique",
            "audience": "Multi-espèces"
        }
    },
    {
        "file": "profish_maridav_ci.html",
        "slug": "profish",
        "seo": {
            "title": "Profish® — Protéines fonctionnelles | MARIDAV CI",
            "description": "Concentré protéique marin hautement digestible pour booster vos formulations fermes ou meuneries.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Profish.png",
        },
        "breadcrumbs": [
            {"label": "Additifs", "url": "additifs/index.html"},
            {"label": "Profish"}
        ],
        "hero": {
            "badges": ["Ingrédient protéique", "Multi-espèces"],
            "title": "Profish®",
            "description": "Ingrédient protéique marin à haute digestibilité pour renforcer vos aliments maison.",
            "stats": [
                {"value": "60 %", "label": "Protéines brutes"},
                {"value": "91 %", "label": "Digestibilité apparente"},
                {"value": "25 kg", "label": "Sac"}
            ],
            "note": "Idéal pour volailles, porcs, poissons et ruminants jeunes.",
            "image": "maridav_ci_image/additifs _alimentaires/Profish.png",
            "image_alt": "Sacs Profish",
            "media_title": "Apport protéique premium",
            "media_points": [
                "Améliore la croissance",
                "Remplace partiellement le tourteau soja",
                "Profil amino équilibré"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Sources marines contrôlées"},
            {"label": "Sécurité", "text": "Basses teneurs en cendres et contaminants"},
            {"label": "Support", "text": "Formulation par MARIDAV CI"}
        ],
        "benefits": {
            "eyebrow": "Pourquoi Profish",
            "title": "Un concentré protéique fonctionnel",
            "features": [
                {"icon": "bi-bullseye", "title": "Profil amino supérieur", "text": "Apports élevés en Lysine, Méthionine, Thréonine."},
                {"icon": "bi-fire", "title": "Haute digestibilité", "text": "Traité à basse température pour préserver les acides aminés."},
                {"icon": "bi-boxes", "title": "Flexibilité", "text": "S’intègre dans vos formulations volailles, porcs, poissons."}
            ]
        },
        "audience": {
            "title": "Applications",
            "items": [
                "Volailles : démarrage, croissance",
                "Porcs : pré-démarrage et croissance",
                "Aquaculture : tilapia, silure",
                "Ruminants jeunes / animaux de compagnie"
            ],
            "badges": ["Ingrédient", "Multi-espèces"]
        },
        "composition": {
            "title": "Spécifications",
            "intro": "Valeurs indicatives, fiches analytiques disponibles.",
            "rows": [
                {"label": "Protéines brutes", "value": "≥ 60 %"},
                {"label": "Matières grasses", "value": "8 – 10 %"},
                {"label": "Cendres", "value": "< 15 %"},
                {"label": "Digestibilité", "value": "≈ 91 % (volailles)"},
                {"label": "Profil amino", "value": "Lysine 4,5 %, Méthionine 1,7 %, Thréonine 2,8 %"}
            ]
        },
        "usage": {
            "title": "Conseils d’incorporation",
            "note": "Formulations fournies par nos nutritionnistes.",
            "steps": [
                {"badge": "Volailles", "title": "3 – 6 %", "text": "Selon stade (démarrage/croissance)."},
                {"badge": "Porcs", "title": "2 – 5 %", "text": "Porcelets, aliment fermier."},
                {"badge": "Poissons", "title": "4 – 8 %", "text": "Tilapia & silure."}
            ]
        },
        "logistics": {
            "title": "Support MARIDAV",
            "items": [
                {"icon": "bi-truck", "title": "Livraisons régulières", "text": "Abidjan et régions via réseau MARIDAV."},
                {"icon": "bi-clipboard-data", "title": "Analyses", "text": "Fiches analytiques fournies pour chaque lot."},
                {"icon": "bi-people", "title": "Formulation", "text": "Plan nutritionnel personnalisé."}
            ]
        },
        "resources": {
            "title": "Guides formulation",
            "intro": "Fiches d’incorporation par espèce, études de cas et outils de calcul."
        },
        "lead": {
            "title": "Parler à un expert formulation",
            "intro": "Optimisez vos recettes avec Profish®.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Meunerie de Yamoussoukro",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Volume mensuel (tonnes)",
            "volume_placeholder": "Ex : 15 tonnes/mois",
            "objective_label": "Objectif",
            "objectives": [
                "Améliorer mon profil amino",
                "Remplacer une partie du tourteau soja",
                "Formuler un aliment premium",
                "Tester en aquaculture"
            ],
            "cta": "Recevoir une formulation"
        },
        "cta": {
            "title": "Ajoutez une protéine premium",
            "text": "Profish® est disponible avec un accompagnement formulation complet.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Profish peut-il remplacer totalement le soja ?", "answer": "Non, il vient en complément pour améliorer le profil amino et la digestibilité."},
            {"question": "Existe-t-il une version pour ruminants ?", "answer": "Oui, contactez-nous pour le profil adapté aux veaux et ruminants jeunes."},
            {"question": "Comment le stocker ?", "answer": "Dans un local sec et ventilé, sacs sur palettes, à l’abri des nuisibles."}
        ],
        "schema": {
            "name": "Profish",
            "description": "Ingrédient protéique marin hautement digestible distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/additifs _alimentaires/Profish.png",
            "sku": "PROFISH",
            "category": "Ingrédient protéique",
            "audience": "Multi-espèces"
        }
    },
    {
        "file": "vitalis_maridav_ci.html",
        "slug": "vitalis",
        "seo": {
            "title": "Vitalis® — Broodstock & reproduction tilapia | MARIDAV CI",
            "description": "Aliment premium Vitalis (Skretting/Nutreco) pour reproducteurs : œufs viables et alevins vigoureux.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/vitalis_poissons_maridav_ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Pisciculture", "url": "pisciculture_maridav_ci.html"},
            {"label": "Vitalis"}
        ],
        "hero": {
            "badges": ["Tilapia", "Broodstock", "Granulés premium"],
            "title": "Vitalis® — Reproducteurs tilapia",
            "description": "Aliment extrudé à forte densité nutritionnelle pour booster la fécondité, la qualité d’œuf et la vigueur des alevins.",
            "stats": [
                {"value": "+15 %", "label": "Taux d’éclosion constaté"},
                {"value": "3–4 mm", "label": "Granulométrie"},
                {"value": "25 kg", "label": "Sac hermétique"}
            ],
            "note": "Programme Skretting/Nutreco distribué par MARIDAV CI.",
            "image": "maridav_ci_image/aliments_poissons/vitalis_poissons_maridav_ci.jpg",
            "image_alt": "Sac Vitalis reproducteurs",
            "media_title": "Performance broodstock",
            "media_points": [
                "Profil amino et lipides optimisé",
                "Vitamines & antioxydants renforcés",
                "Support MARIDAV CI (plan de ration)"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Skretting / Nutreco"},
            {"label": "Distribution", "text": "Exclusivité MARIDAV CI"},
            {"label": "Support", "text": "Techniciens pisciculture MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Atouts Vitalis",
            "title": "Préparez votre prochaine génération",
            "features": [
                {"icon": "bi-egg", "title": "Œufs viables", "text": "Apports en EPA/DHA pour une membrane ovocytaire solide."},
                {"icon": "bi-droplet", "title": "Vigueur larvaire", "text": "Vitamines et antioxydants pour un démarrage rapide des alevins."},
                {"icon": "bi-graph-up-arrow", "title": "Production continue", "text": "Ration stable favorisant la ponte toute l’année."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Stations de reproduction tilapia",
                "Fermes intégrées avec nursery",
                "Opérateurs recherchant un broodstock performant"
            ],
            "badges": ["Reproducteurs", "Tilapia", "Premium"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs Skretting adaptées au climat tropical.",
            "rows": [
                {"label": "Protéines brutes", "value": "45 %"},
                {"label": "Lipides", "value": "14 % (riches en EPA/DHA)"},
                {"label": "Énergie digestible", "value": "Digestibilité élevée"},
                {"label": "Vitamines & minéraux", "value": "Profil complet broodstock"},
                {"label": "Stabilisants", "value": "Antioxydants naturels"}
            ]
        },
        "usage": {
            "title": "Programme d’utilisation",
            "note": "Nos techniciens adaptent la ration selon densité et température.",
            "steps": [
                {"badge": "Journée", "title": "2–3 repas", "text": "Distribuer 1,5–2 % du poids vif / jour."},
                {"badge": "Température", "title": "22–32 °C", "text": "Adapter la ration si < 24 °C."},
                {"badge": "Observation", "title": "Contrôle quotidien", "text": "Vérifier l’appétit et l’état corporel des géniteurs."}
            ]
        },
        "logistics": {
            "title": "Services piscicoles",
            "items": [
                {"icon": "bi-water", "title": "Audit qualité d’eau", "text": "Suivi O₂, pH, alcalinité."},
                {"icon": "bi-diagram-3", "title": "Plan de ration", "text": "Recommandations par densité et bassin."},
                {"icon": "bi-people", "title": "Formation équipes", "text": "Gestion broodstock & récolte d’œufs."}
            ]
        },
        "resources": {
            "title": "Guides reproduction",
            "intro": "Fiches techniques, checklists broodstock et protocoles d’écloserie."
        },
        "lead": {
            "title": "Parler à un expert piscicole",
            "intro": "Recevez un plan broodstock adapté à vos bassins.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme Tilapia de Grand-Lahou",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de reproducteurs",
            "volume_placeholder": "Ex : 2 000 reproducteurs",
            "objective_label": "Objectif",
            "objectives": [
                "Booster la fécondité",
                "Stabiliser la qualité d’œufs",
                "Mettre en place Vitalis",
                "Former mon équipe"
            ],
            "cta": "Recevoir un plan broodstock"
        },
        "cta": {
            "title": "Élevez des alevins plus forts",
            "text": "Vitalis® est disponible en Côte d’Ivoire avec support MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quelle est la ration journalière ?", "answer": "Entre 1,5 et 2 % du poids vif répartis en 2–3 repas."},
            {"question": "Peut-on l’utiliser pour d’autres espèces ?", "answer": "Oui, pour d’autres poissons tropicaux à forte valeur. Consultez-nous pour adapter."},
            {"question": "Comment stocker les sacs ?", "answer": "Local frais et ventilé, sur palettes. Fermer hermétiquement après ouverture."}
        ],
        "schema": {
            "name": "Vitalis Broodstock",
            "description": "Aliment reproducteurs tilapia Vitalis distribué par MARIDAV Côte d’Ivoire.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/vitalis_poissons_maridav_ci.jpg",
            "sku": "VITALIS-BROODSTOCK",
            "category": "Aliment poissons",
            "audience": "Tilapia — Reproducteurs"
        }
    },
    {
        "file": "nutra_tilapia_0_maridav_ci.html",
        "slug": "nutra-0",
        "seo": {
            "title": "Nutra® 0 — Alevinage tilapia 0–5 g | MARIDAV CI",
            "description": "Granulé micro-extrudé Nutra 0 pour démarrer vos alevins de tilapia en écloserie.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Pisciculture", "url": "pisciculture_maridav_ci.html"},
            {"label": "Nutra 0"}
        ],
        "hero": {
            "badges": ["Tilapia", "Alevinage", "Micro-granulé"],
            "title": "Nutra® 0",
            "description": "Aliment micro-extrudé pour alevins 0–5 g : haute digestibilité, granulométrie régulière et croissance homogène.",
            "stats": [
                {"value": "0,3–0,8 mm", "label": "Granulométrie"},
                {"value": "≥ 52 %", "label": "Protéines brutes"},
                {"value": "25 kg", "label": "Sac laminé"}
            ],
            "note": "Programme Skretting/Nutreco pour nurseries africaines.",
            "image": "maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
            "image_alt": "Sac Nutra tilapia",
            "media_title": "Démarrage sécurisé",
            "media_points": [
                "Densité adaptée aux nurseries",
                "Profil vitaminique complet",
                "Support MARIDAV CI sur les protocoles"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Skretting / Nutreco"},
            {"label": "Distribution", "text": "Exclusivité MARIDAV CI"},
            {"label": "Support", "text": "Techniciens pisciculture MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Atouts Nutra 0",
            "title": "Réussissez vos phases critiques",
            "features": [
                {"icon": "bi-droplet", "title": "Faible pollution", "text": "Granulé flottant stable pour limiter les pertes et la charge organique."},
                {"icon": "bi-speedometer2", "title": "Croissance rapide", "text": "Densité énergétique élevée pour atteindre rapidement 5 g."},
                {"icon": "bi-heart", "title": "Santé larvaire", "text": "Vitamine C stabilisée et immunostimulants."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Nurseries intensives 0–5 g",
                "Fermes intégrées avec bac d’alevinage",
                "Producteurs recherchant une constance d’alevins"
            ],
            "badges": ["Alevins", "0–5 g"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs Skretting adaptées au tilapia.",
            "rows": [
                {"label": "Protéines brutes", "value": "52 %"},
                {"label": "Lipides", "value": "12 %"},
                {"label": "Énergie", "value": "Digestibilité élevée"},
                {"label": "Vitamines/Minéraux", "value": "Profil complet alevins"},
                {"label": "Additifs", "value": "Immunostimulants, antioxydants"}
            ]
        },
        "usage": {
            "title": "Programme d’utilisation",
            "note": "Adaptez selon densité et brassage.",
            "steps": [
                {"badge": "J0-J7", "title": "Alimentation en continu", "text": "Petites rations fréquentes (6–8 fois/jour)."},
                {"badge": "J8-J14", "title": "Réduction progressive", "text": "4–5 repas/jour selon consommation."},
                {"badge": "Transition", "title": "Vers Nutra 80", "text": "Introduire Nutra 80 quand les alevins atteignent 5 g."}
            ]
        },
        "logistics": {
            "title": "Services piscicoles",
            "items": [
                {"icon": "bi-water", "title": "Qualité d’eau", "text": "Conseils sur l’oxygénation et l’évacuation des déchets."},
                {"icon": "bi-diagram-3", "title": "Plan de ration", "text": "Courbes de consommation fournies."},
                {"icon": "bi-people", "title": "Formation", "text": "Gestion d’alevinage et tamisage."}
            ]
        },
        "resources": {
            "title": "Guides Nutra",
            "intro": "Fiches techniques, checklists nursery et tableaux de consommation."
        },
        "lead": {
            "title": "Parler à un expert tilapia",
            "intro": "Recevez un plan d’alevinage adapté à votre station.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Nursery Tilapia de Jacqueville",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre d’alevins / lot",
            "volume_placeholder": "Ex : 100 000 alevins",
            "objective_label": "Objectif",
            "objectives": [
                "Sécuriser mon alevinage",
                "Optimiser ma consommation",
                "Mettre en place Nutra",
                "Former mon équipe nursery"
            ],
            "cta": "Recevoir un plan Nutra"
        },
        "cta": {
            "title": "Réussissez vos premières semaines",
            "text": "Nutra® 0 est disponible chez MARIDAV CI avec support technique.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Comment éviter la pollution ?", "answer": "Distribuez de petites quantités fréquentes et ajustez selon le comportement d’ingestion."},
            {"question": "Quelle densité recommandez-vous ?", "answer": "Consultez-nous pour un dimensionnement selon vos bassins (souvent 300–400 alevins/m² en bac)."},
            {"question": "Peut-on distribuer en étang ?", "answer": "Nutra 0 est idéal en systèmes contrôlés. Pour étangs, veillez à bien maîtriser l’oxygène."}
        ],
        "schema": {
            "name": "Nutra 0",
            "description": "Aliment alevinage 0–5 g pour tilapia distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
            "sku": "NUTRA-0",
            "category": "Aliment poissons",
            "audience": "Tilapia — Alevinage"
        }
    },
    {
        "file": "nutra_tilapia_80_maridav_ci.html",
        "slug": "nutra-80",
        "seo": {
            "title": "Nutra® 80 — Alevinage 5–20 g | MARIDAV CI",
            "description": "Granulé flottant Nutra 80 pour accélérer la croissance des alevins de tilapia (5–20 g).",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Pisciculture", "url": "pisciculture_maridav_ci.html"},
            {"label": "Nutra 80"}
        ],
        "hero": {
            "badges": ["Tilapia", "Alevinage 5–20 g", "Granulé flottant"],
            "title": "Nutra® 80",
            "description": "Aliment granulé premium pour atteindre rapidement le stade prégrossissement avec une excellente homogénéité.",
            "stats": [
                {"value": "0,8–1,2 mm", "label": "Granulométrie"},
                {"value": "48 %", "label": "Protéines brutes"},
                {"value": "25 kg", "label": "Sac"}
            ],
            "note": "Programme Skretting adapté aux densités africaines.",
            "image": "maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
            "image_alt": "Sac Nutra 80",
            "media_title": "Croissance accélérée",
            "media_points": [
                "Taux de survie élevé",
                "Granulé flottant stable",
                "Support MARIDAV CI"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Skretting / Nutreco"},
            {"label": "Distribution", "text": "Exclusivité MARIDAV CI"},
            {"label": "Support", "text": "Techniciens pisciculture MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Atouts Nutra 80",
            "title": "Préparez vos prégrossissements",
            "features": [
                {"icon": "bi-activity", "title": "Croissance homogène", "text": "Profil amino équilibré pour limiter les écarts de taille."},
                {"icon": "bi-shield-plus", "title": "Soutien sanitaire", "text": "Vitamines, minéraux et antioxydants renforcés."},
                {"icon": "bi-droplet-half", "title": "Faible pollution", "text": "Granulé flottant qui réduit l’encrassement des bassins."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Nurseries 5–20 g",
                "Fermes semi-intensives",
                "Opérateurs préparant le prégrossissement"
            ],
            "badges": ["5–20 g", "Alevins"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs Skretting adaptées au tilapia.",
            "rows": [
                {"label": "Protéines brutes", "value": "48 %"},
                {"label": "Lipides", "value": "10 %"},
                {"label": "Énergie digestible", "value": "Haute"},
                {"label": "Vitamines/minéraux", "value": "Profil complet"},
                {"label": "Additifs", "value": "Immunostimulants"}
            ]
        },
        "usage": {
            "title": "Programme d’alimentation",
            "note": "Adapter selon densité et température.",
            "steps": [
                {"badge": "Rations", "title": "4–5 repas/jour", "text": "Distribuer 3–6 % du poids vif selon taille."},
                {"badge": "Transition", "title": "Vers Nutra 120", "text": "Lorsque les poissons dépassent 20 g."},
                {"badge": "Observation", "title": "Contrôle de l’appétit", "text": "Ajuster la ration pour éviter les refus."}
            ]
        },
        "logistics": {
            "title": "Services piscicoles",
            "items": [
                {"icon": "bi-bar-chart", "title": "Tableaux de ration", "text": "Fourni pour chaque densité."},
                {"icon": "bi-water", "title": "Suivi eau", "text": "Conseils sur l’oxygénation."},
                {"icon": "bi-people", "title": "Formation équipes", "text": "Gestion couveuse et alevinage."}
            ]
        },
        "resources": {
            "title": "Guides Nutra",
            "intro": "Fiches techniques, checklists et outils de consommation."
        },
        "lead": {
            "title": "Parler à un expert tilapia",
            "intro": "Recevez un plan Nutra personnalisé.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Station tilapia de Tiassalé",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre d’alevins",
            "volume_placeholder": "Ex : 80 000 sujets",
            "objective_label": "Objectif",
            "objectives": [
                "Homogénéiser mes lots",
                "Réduire la mortalité",
                "Planifier la transition",
                "Former mon équipe"
            ],
            "cta": "Recevoir un plan Nutra"
        },
        "cta": {
            "title": "Passez au niveau supérieur",
            "text": "Nutra® 80 est disponible avec support MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quelle quantité d’eau par kg d’aliment ?", "answer": "Veillez à maintenir un brassage suffisant et un taux d’O₂ > 5 mg/L."},
            {"question": "Peut-on extruder sur site ?", "answer": "Nutra est prêt à l’emploi; inutile de retraiter le granulé."},
            {"question": "Comment limiter les restes ?", "answer": "Distribuez en plusieurs repas et observez l’appétit pour ajuster."}
        ],
        "schema": {
            "name": "Nutra 80",
            "description": "Aliment alevinage 5–20 g pour tilapia distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
            "sku": "NUTRA-80",
            "category": "Aliment poissons",
            "audience": "Tilapia — Alevinage"
        }
    },
    {
        "file": "nutra_tilapia_120_maridav_ci.html",
        "slug": "nutra-120",
        "seo": {
            "title": "Nutra® 120 — Prégrossissement 20–80 g | MARIDAV CI",
            "description": "Granulé Nutra 120 pour prégrossissement tilapia (20–80 g) : croissance rapide et homogène.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Pisciculture", "url": "pisciculture_maridav_ci.html"},
            {"label": "Nutra 120"}
        ],
        "hero": {
            "badges": ["Tilapia", "Prégrossissement 20–80 g", "Granulé flottant"],
            "title": "Nutra® 120",
            "description": "Aliment performance pour amener vos juvéniles à 80 g avec une FCR maîtrisée.",
            "stats": [
                {"value": "1,5–2 mm", "label": "Granulométrie"},
                {"value": "44 %", "label": "Protéines brutes"},
                {"value": "1,0–1,2", "label": "FCR cible"}
            ],
            "note": "Programme Skretting — prégrossissement.",
            "image": "maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
            "image_alt": "Sac Nutra 120",
            "media_title": "Montée rapide en poids",
            "media_points": [
                "Profil amino optimisé",
                "Granulé stable",
                "Support MARIDAV CI"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Skretting / Nutreco"},
            {"label": "Distribution", "text": "Exclusivité MARIDAV CI"},
            {"label": "Support", "text": "Techniciens pisciculture MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Atouts Nutra 120",
            "title": "Préparez le grossissement",
            "features": [
                {"icon": "bi-speedometer", "title": "GMQ élevé", "text": "Permet d’atteindre rapidement 80 g."},
                {"icon": "bi-droplet", "title": "Qualité d’eau préservée", "text": "Granulé à très faible taux de fines."},
                {"icon": "bi-check-circle", "title": "Stabilité nutritionnelle", "text": "Valeurs constantes d’un sac à l’autre."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Prégrossissement intensif",
                "Fermes semi-intensives préparant l’étang",
                "Opérateurs souhaitant réduire le cycle"
            ],
            "badges": ["20–80 g", "Prégrossissement"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs Skretting pour tilapia.",
            "rows": [
                {"label": "Protéines brutes", "value": "44 %"},
                {"label": "Lipides", "value": "9 %"},
                {"label": "Énergie digestible", "value": "3 350 kcal/kg"},
                {"label": "Additifs", "value": "Antioxydants, immunostimulants"},
                {"label": "Granulométrie", "value": "1,5 – 2 mm"}
            ]
        },
        "usage": {
            "title": "Calendrier conseillé",
            "note": "Adapter selon densité et température.",
            "steps": [
                {"badge": "20–40 g", "title": "Ration 3–4 % PV", "text": "3 repas par jour selon appétit."},
                {"badge": "40–80 g", "title": "Ration 2,5–3 % PV", "text": "2–3 repas par jour."},
                {"badge": "Transition", "title": "Vers Nutra 160 ou Optiline", "text": "Lorsque les poissons dépassent 80 g."}
            ]
        },
        "logistics": {
            "title": "Services piscicoles",
            "items": [
                {"icon": "bi-water", "title": "Suivi qualité d’eau", "text": "Paramètres O₂/pH surveillés."},
                {"icon": "bi-diagram-3", "title": "Rations personnalisées", "text": "Courbes fournies selon densité."},
                {"icon": "bi-people", "title": "Coaching", "text": "Gestion des prégrossissements."}
            ]
        },
        "resources": {
            "title": "Guides Nutra",
            "intro": "Fiches techniques et outils de suivi de consommation."
        },
        "lead": {
            "title": "Parler à un expert tilapia",
            "intro": "Recevez un plan Nutra 120 sur mesure.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme tilapia de Bouaké",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de poissons",
            "volume_placeholder": "Ex : 60 000 juvéniles",
            "objective_label": "Objectif",
            "objectives": [
                "Réduire mon cycle",
                "Homogénéiser les lots",
                "Préparer la transition",
                "Former l’équipe"
            ],
            "cta": "Recevoir un plan Nutra"
        },
        "cta": {
            "title": "Gagnez du temps sur vos cycles",
            "text": "Nutra® 120 disponible chez MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quel FCR viser ?", "answer": "Entre 1,0 et 1,2 selon les conditions d’élevage."},
            {"question": "Peut-on l’utiliser en cages flottantes ?", "answer": "Oui, le granulé flottant reste stable pour ce type d’élevage."},
            {"question": "Comment éviter les tailles inégales ?", "answer": "Triez régulièrement vos poissons et ajustez la ration selon la taille."}
        ],
        "schema": {
            "name": "Nutra 120",
            "description": "Aliment prégrossissement 20–80 g pour tilapia distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
            "sku": "NUTRA-120",
            "category": "Aliment poissons",
            "audience": "Tilapia — Prégrossissement"
        }
    },
    {
        "file": "nutra_tilapia_160_maridav_ci.html",
        "slug": "nutra-160",
        "seo": {
            "title": "Nutra® 160 — Prégrossissement 80–120 g | MARIDAV CI",
            "description": "Granulé Nutra 160 pour finaliser le prégrossissement avant l’entrée en Optiline.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Pisciculture", "url": "pisciculture_maridav_ci.html"},
            {"label": "Nutra 160"}
        ],
        "hero": {
            "badges": ["Tilapia", "Prégrossissement 80–120 g", "Granulé flottant"],
            "title": "Nutra® 160",
            "description": "Dernière étape Nutra avant Optiline, pour des poissons robustes et homogènes.",
            "stats": [
                {"value": "2–2,5 mm", "label": "Granulométrie"},
                {"value": "40 %", "label": "Protéines brutes"},
                {"value": "25 kg", "label": "Sac"}
            ],
            "note": "Programme Skretting — prégrossissement tardif.",
            "image": "maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
            "image_alt": "Sac Nutra 160",
            "media_title": "Homogénéité des lots",
            "media_points": [
                "Granulé stable",
                "Transition facilitée vers Optiline",
                "Support technique MARIDAV"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Skretting / Nutreco"},
            {"label": "Distribution", "text": "MARIDAV CI"},
            {"label": "Support", "text": "Experts piscicoles MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Atouts Nutra 160",
            "title": "Prépare vos poissons au grossissement",
            "features": [
                {"icon": "bi-graph-up", "title": "Croissance rapide", "text": "Profil nutritionnel pour atteindre 120 g rapidement."},
                {"icon": "bi-droplet", "title": "Qualité d’eau", "text": "Granulé flottant pauvre en fines."},
                {"icon": "bi-check", "title": "Transition facile", "text": "Formulation proche d’Optiline pour limiter le stress."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Prégrossissements intensifs",
                "Fermes qui livrent des juvéniles prêts à grossir",
                "Sites voulant sécuriser la transition vers Optiline"
            ],
            "badges": ["80–120 g", "Prégrossissement"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs Skretting pour tilapia.",
            "rows": [
                {"label": "Protéines brutes", "value": "40 %"},
                {"label": "Lipides", "value": "8 %"},
                {"label": "Énergie digestible", "value": "3 250 kcal/kg"},
                {"label": "Vitamines/minéraux", "value": "Profil complet"},
                {"label": "Additifs", "value": "Immunostimulants"}
            ]
        },
        "usage": {
            "title": "Plan d’alimentation",
            "note": "Adapter selon densité et température.",
            "steps": [
                {"badge": "80–100 g", "title": "2,5 % PV", "text": "2–3 repas/jour."},
                {"badge": "100–120 g", "title": "2 % PV", "text": "2 repas/jour."},
                {"badge": "Transition", "title": "Vers Optiline 2/3", "text": "Bascule progressive sur 3 jours."}
            ]
        },
        "logistics": {
            "title": "Services piscicoles",
            "items": [
                {"icon": "bi-water", "title": "Monitoring qualité d’eau", "text": "Conseils sur l’oxygène et la filtration."},
                {"icon": "bi-diagram-3", "title": "Plan de ration", "text": "Courbes fournies."},
                {"icon": "bi-people", "title": "Formation", "text": "Gestion prégrossissement tardif."}
            ]
        },
        "resources": {
            "title": "Guides Nutra",
            "intro": "Fiches techniques et outils de suivi."
        },
        "lead": {
            "title": "Parler à un expert tilapia",
            "intro": "Recevez un plan Nutra 160 personnalisé.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme tilapia de Daloa",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de poissons",
            "volume_placeholder": "Ex : 40 000 poissons",
            "objective_label": "Objectif",
            "objectives": [
                "Accélérer mon prégrossissement",
                "Préparer la transition Optiline",
                "Homogénéiser mes lots",
                "Former mon équipe"
            ],
            "cta": "Recevoir un plan Nutra"
        },
        "cta": {
            "title": "Livrez des juvéniles prêts à grossir",
            "text": "Nutra® 160 disponible chez MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quel FCR viser ?", "answer": "Autour de 1,1 selon température et densité."},
            {"question": "Peut-on l’utiliser en étang ?", "answer": "Oui, mais veillez à la qualité d’eau et à la distribution homogène."},
            {"question": "Combien de temps rester sur Nutra 160 ?", "answer": "Jusqu’à atteindre 120 g avant bascule sur Optiline."}
        ],
        "schema": {
            "name": "Nutra 160",
            "description": "Aliment prégrossissement 80–120 g pour tilapia distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
            "sku": "NUTRA-160",
            "category": "Aliment poissons",
            "audience": "Tilapia — Prégrossissement"
        }
    },
    {
        "file": "maridav_optiline_2_maridav_ci.html",
        "slug": "optiline-2",
        "seo": {
            "title": "Optiline® 2 — Grossissement 120–200 g | MARIDAV CI",
            "description": "Aliment Optiline 2 pour démarrer le grossissement tilapia avec une FCR optimisée.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/optiline_maridav_ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Pisciculture", "url": "pisciculture_maridav_ci.html"},
            {"label": "Optiline 2"}
        ],
        "hero": {
            "badges": ["Tilapia", "Grossissement 120–200 g", "Granulé flottant"],
            "title": "Optiline® 2",
            "description": "Aliment premium de grossissement initial pour convertir efficacement vos juvéniles.",
            "stats": [
                {"value": "2,5–3 mm", "label": "Granulométrie"},
                {"value": "38 %", "label": "Protéines brutes"},
                {"value": "1,3", "label": "FCR cible"}
            ],
            "note": "Programme Skretting / MARIDAV CI.",
            "image": "maridav_ci_image/aliments_poissons/optiline_maridav_ci.jpg",
            "image_alt": "Sac Optiline",
            "media_title": "Grossissement performant",
            "media_points": [
                "Profil amino calibré",
                "Granulé stable",
                "Support plan de ration"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Skretting / Nutreco"},
            {"label": "Distribution", "text": "Exclusivité MARIDAV CI"},
            {"label": "Support", "text": "Experts piscicoles MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Atouts Optiline 2",
            "title": "Maintenez une croissance rapide",
            "features": [
                {"icon": "bi-graph-up-arrow", "title": "Performance GMQ", "text": "Permet d’atteindre 200 g rapidement."},
                {"icon": "bi-droplet", "title": "Qualité d’eau préservée", "text": "Granulé flottant à faible taux de fines."},
                {"icon": "bi-shield", "title": "Soutien sanitaire", "text": "Vitamines et antioxydants renforcés."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Cages flottantes",
                "Étangs intensifs",
                "Fermes semi-intensives"
            ],
            "badges": ["120–200 g", "Grossissement"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs Skretting pour tilapia.",
            "rows": [
                {"label": "Protéines brutes", "value": "38 %"},
                {"label": "Lipides", "value": "8 %"},
                {"label": "Énergie digestible", "value": "3 200 kcal/kg"},
                {"label": "Additifs", "value": "Antioxydants, immunostimulants"},
                {"label": "Granulométrie", "value": "2,5 – 3 mm"}
            ]
        },
        "usage": {
            "title": "Plan d’alimentation",
            "note": "Adapter selon densité et température.",
            "steps": [
                {"badge": "120–150 g", "title": "2 % PV", "text": "2–3 repas/jour."},
                {"badge": "150–200 g", "title": "1,8 % PV", "text": "2 repas/jour."},
                {"badge": "Transition", "title": "Vers Optiline 3", "text": "Sur 3 jours."}
            ]
        },
        "logistics": {
            "title": "Services pisciculture",
            "items": [
                {"icon": "bi-water", "title": "Qualité d’eau", "text": "Conseils sur l’oxygénation."},
                {"icon": "bi-diagram-3", "title": "Plan de ration", "text": "Courbes fournies."},
                {"icon": "bi-people", "title": "Formation", "text": "Gestion grossissement initial."}
            ]
        },
        "resources": {
            "title": "Guides Optiline",
            "intro": "Fiches techniques et outils de pilotage."
        },
        "lead": {
            "title": "Parler à un expert tilapia",
            "intro": "Recevez un plan Optiline 2 adapté.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme tilapia de Dabou",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de poissons",
            "volume_placeholder": "Ex : 30 000 poissons",
            "objective_label": "Objectif",
            "objectives": [
                "Optimiser la FCR",
                "Réduire la durée de cycle",
                "Planifier la transition",
                "Former les équipes"
            ],
            "cta": "Recevoir un plan Optiline"
        },
        "cta": {
            "title": "Accélérez votre grossissement",
            "text": "Optiline® 2 disponible avec support MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Peut-on l’utiliser en étang traditionnel ?", "answer": "Oui, en adaptant la ration et en assurant un apport d’oxygène suffisant."},
            {"question": "Quel FCR viser ?", "answer": "Entre 1,3 et 1,4 selon conditions."},
            {"question": "Combien de temps rester sur Optiline 2 ?", "answer": "Jusqu’à atteindre ~200 g avant bascule sur Optiline 3."}
        ],
        "schema": {
            "name": "Optiline 2",
            "description": "Aliment grossissement 120–200 g pour tilapia distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/optiline_maridav_ci.jpg",
            "sku": "OPTILINE-2",
            "category": "Aliment poissons",
            "audience": "Tilapia — Grossissement"
        }
    },
    {
        "file": "maridav_optiline_3_maridav_ci.html",
        "slug": "optiline-3",
        "seo": {
            "title": "Optiline® 3 — Grossissement 200–400 g | MARIDAV CI",
            "description": "Aliment Optiline 3 pour poursuite du grossissement tilapia avec FCR maîtrisée.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/optiline_maridav_ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Pisciculture", "url": "pisciculture_maridav_ci.html"},
            {"label": "Optiline 3"}
        ],
        "hero": {
            "badges": ["Tilapia", "Grossissement 200–400 g", "Granulé flottant"],
            "title": "Optiline® 3",
            "description": "Aliment haute performance pour accélérer le grossissement intermédiaire.",
            "stats": [
                {"value": "3–4 mm", "label": "Granulométrie"},
                {"value": "35 %", "label": "Protéines brutes"},
                {"value": "1,4", "label": "FCR cible"}
            ],
            "note": "Programme Skretting / MARIDAV CI.",
            "image": "maridav_ci_image/aliments_poissons/optiline_maridav_ci.jpg",
            "image_alt": "Sac Optiline 3",
            "media_title": "Croissance régulière",
            "media_points": [
                "Énergie adaptée",
                "Granulé stable",
                "Support ration"
            ]
        },
        "benefits": {
            "eyebrow": "Atouts Optiline 3",
            "title": "Poursuivez la performance",
            "features": [
                {"icon": "bi-graph-up", "title": "Gain rapide", "text": "Permet d’atteindre 400 g plus vite."},
                {"icon": "bi-shield", "title": "Soutien sanitaire", "text": "Vitamines et minéraux renforcés."},
                {"icon": "bi-droplet", "title": "Qualité d’eau", "text": "Granulé flottant minimisant les déchets."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Fermes intensives",
                "Étangs gérés",
                "Cages flottantes"
            ],
            "badges": ["200–400 g", "Grossissement"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs Skretting pour tilapia.",
            "rows": [
                {"label": "Protéines brutes", "value": "35 %"},
                {"label": "Lipides", "value": "7 %"},
                {"label": "Énergie", "value": "3 150 kcal/kg"},
                {"label": "Additifs", "value": "Antioxydants, immunostimulants"},
                {"label": "Granulométrie", "value": "3 – 4 mm"}
            ]
        },
        "usage": {
            "title": "Plan d’alimentation",
            "note": "Adapter selon densité.",
            "steps": [
                {"badge": "200–300 g", "title": "1,8 % PV", "text": "2 repas/jour."},
                {"badge": "300–400 g", "title": "1,5 % PV", "text": "1–2 repas/jour."},
                {"badge": "Transition", "title": "Vers Optiline 4.5", "text": "Étape finale selon poids cible."}
            ]
        },
        "logistics": {
            "title": "Services MARIDAV",
            "items": [
                {"icon": "bi-water", "title": "Qualité d’eau", "text": "Conseils O₂/pH."},
                {"icon": "bi-diagram-3", "title": "Plans de ration", "text": "Courbes fournies."},
                {"icon": "bi-people", "title": "Coaching", "text": "Pilotage du grossissement."}
            ]
        },
        "resources": {
            "title": "Guides Optiline",
            "intro": "Fiches techniques et outils de suivi."
        },
        "lead": {
            "title": "Parler à un expert tilapia",
            "intro": "Recevez un plan Optiline 3 adapté.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme tilapia de San Pedro",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Nombre de poissons",
            "volume_placeholder": "Ex : 25 000 poissons",
            "objective_label": "Objectif",
            "objectives": [
                "Réduire mon FCR",
                "Accélérer le cycle",
                "Préparer la transition",
                "Former l’équipe"
            ],
            "cta": "Recevoir un plan Optiline"
        },
        "cta": {
            "title": "Optimisez votre grossissement",
            "text": "Optiline® 3 disponible avec support MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Peut-on l’utiliser pour d’autres espèces ?", "answer": "Principalement conçu pour tilapia. Contactez-nous pour d’autres espèces."},
            {"question": "Quel FCR viser ?", "answer": "Environ 1,4 selon conditions."},
            {"question": "Quelle durée du cycle ?", "answer": "Dépend du poids cible et des conditions. Nos techniciens vous accompagnent."}
        ],
        "schema": {
            "name": "Optiline 3",
            "description": "Aliment grossissement 200–400 g pour tilapia distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/optiline_maridav_ci.jpg",
            "sku": "OPTILINE-3",
            "category": "Aliment poissons",
            "audience": "Tilapia — Grossissement"
        }
    },
    {
        "file": "maridav_optiline_4_5.html",
        "slug": "optiline-4-5",
        "seo": {
            "title": "Optiline® 4.5 — Finition >400 g | MARIDAV CI",
            "description": "Aliment finition tilapia (pré-abattage) pour optimiser le poids commercial et la rentabilité.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/optiline_maridav_ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Pisciculture", "url": "pisciculture_maridav_ci.html"},
            {"label": "Optiline 4.5"}
        ],
        "hero": {
            "badges": ["Tilapia", "Finition >400 g", "Granulé flottant"],
            "title": "Optiline® 4.5",
            "description": "La phase finale pour obtenir une taille commerciale homogène avec un coût alimentaire maîtrisé.",
            "stats": [
                {"value": "4–5 mm", "label": "Granulométrie"},
                {"value": "32 %", "label": "Protéines brutes"},
                {"value": "1,6", "label": "FCR cible"}
            ],
            "note": "Conçu pour préparer l’abattage ou la vente en vif.",
            "image": "maridav_ci_image/aliments_poissons/optiline_maridav_ci.jpg",
            "image_alt": "Sac Optiline 4.5",
            "media_title": "Finition premium",
            "media_points": [
                "Poids commercial uniforme",
                "Teneur en lipides maîtrisée",
                "Support logistique"
            ]
        },
        "benefits": {
            "eyebrow": "Atouts Optiline 4.5",
            "title": "Valorisez votre production",
            "features": [
                {"icon": "bi-weight", "title": "Poids cible atteint", "text": "Permet d’atteindre 500 g et + selon marché."},
                {"icon": "bi-currency-dollar", "title": "Coût maîtrisé", "text": "Profil énergétique pour optimiser le coût/kg vif."},
                {"icon": "bi-check-circle", "title": "Finition homogène", "text": "Granulé constant pour limiter les variations."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Fermes préparant l’abattage",
                "Producteurs vendant en vif",
                "Opérateurs export"
            ],
            "badges": [">400 g", "Finition"]
        },
        "composition": {
            "title": "Composition indicative",
            "intro": "Valeurs Skretting pour finition tilapia.",
            "rows": [
                {"label": "Protéines brutes", "value": "32 %"},
                {"label": "Lipides", "value": "6 %"},
                {"label": "Énergie digestible", "value": "3 100 kcal/kg"},
                {"label": "Additifs", "value": "Antioxydants, minéraux"},
                {"label": "Granulométrie", "value": "4 – 5 mm"}
            ]
        },
        "usage": {
            "title": "Plan d’alimentation",
            "note": "Adapter selon poids cible et durée de cycle.",
            "steps": [
                {"badge": "400–500 g", "title": "1,2 – 1,5 % PV", "text": "2 repas/jour."},
                {"badge": "Pré-abattage", "title": "1 % PV", "text": "1 repas/jour ou ration contrôlée."},
                {"badge": "Transport", "title": "Gestion stress", "text": "Réduire l’aliment 24 h avant transport."}
            ]
        },
        "logistics": {
            "title": "Services MARIDAV CI",
            "items": [
                {"icon": "bi-truck", "title": "Planification abattage", "text": "Coordination avec nos partenaires logistiques."},
                {"icon": "bi-water", "title": "Qualité d’eau", "text": "Conseils pour maintenir l’oxygène aux densités élevées."},
                {"icon": "bi-people", "title": "Formation", "text": "Gestion de la finition et du transport."}
            ]
        },
        "resources": {
            "title": "Guides Optiline",
            "intro": "Checklists finition, protocoles pré-transport et fiches nutrition."
        },
        "lead": {
            "title": "Parler à un expert tilapia",
            "intro": "Recevez un plan Optiline 4.5 adapté à vos objectifs commerciaux.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme tilapia de Yamoussoukro",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Tonnage mensuel",
            "volume_placeholder": "Ex : 15 tonnes/mois",
            "objective_label": "Objectif",
            "objectives": [
                "Optimiser ma finition",
                "Planifier l’abattage",
                "Réduire mon coût alimentaire",
                "Former mes équipes"
            ],
            "cta": "Recevoir un plan Optiline"
        },
        "cta": {
            "title": "Livrez une qualité constante",
            "text": "Optiline® 4.5 disponible avec support MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quel FCR viser ?", "answer": "Entre 1,5 et 1,6 selon les conditions."},
            {"question": "Peut-on exporter avec Optiline 4.5 ?", "answer": "Oui, l’aliment est conçu pour répondre aux standards export."},
            {"question": "Comment gérer les pics de chaleur ?", "answer": "Réduire la ration, augmenter les apports d’oxygène et utiliser nos protocoles Nutricool si besoin."}
        ],
        "schema": {
            "name": "Optiline 4.5",
            "description": "Aliment finition tilapia >400 g distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/optiline_maridav_ci.jpg",
            "sku": "OPTILINE-4.5",
            "category": "Aliment poissons",
            "audience": "Tilapia — Finition"
        }
    },
    {
        "file": "aquacare_maridav_ci.html",
        "slug": "aquacare",
        "seo": {
            "title": "AquaCare® — Probiotique qualité d’eau | MARIDAV CI",
            "description": "Solution AquaCare (Skretting/Nutreco) pour stabiliser la microflore des bassins et améliorer la qualité d’eau.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/aquacare_poissons_maridav_ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Pisciculture", "url": "pisciculture_maridav_ci.html"},
            {"label": "AquaCare"}
        ],
        "hero": {
            "badges": ["Additif eau", "Probiotique", "Pisciculture"],
            "title": "AquaCare®",
            "description": "Probiotiques et enzymes pour améliorer la qualité d’eau, réduire les déchets organiques et soutenir la santé des poissons.",
            "stats": [
                {"value": "500 g – 10 kg", "label": "Formats"},
                {"value": "Application eau / fond", "label": "Modulable selon système"},
                {"value": "Multi-espèces", "label": "Tilapia, silure, crevettes"}
            ],
            "note": "Programme Skretting/Nutreco — exclusif MARIDAV CI.",
            "image": "maridav_ci_image/aliments_poissons/aquacare_poissons_maridav_ci.jpg",
            "image_alt": "Sacs AquaCare",
            "media_title": "Qualité d’eau maîtrisée",
            "media_points": [
                "Réduction de l’ammoniac",
                "Dégradation des matières organiques",
                "Soutien immunitaire"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "Skretting / Nutreco"},
            {"label": "Distribution", "text": "MARIDAV CI"},
            {"label": "Support", "text": "Techniciens pisciculture MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Atouts AquaCare",
            "title": "Stabilisez vos bassins",
            "features": [
                {"icon": "bi-water", "title": "Clarté de l’eau", "text": "Réduit la turbidité et les matières en suspension."},
                {"icon": "bi-recycle", "title": "Dégradation des déchets", "text": "Enzymes et probiotiques qui consomment les matières organiques."},
                {"icon": "bi-heart-pulse", "title": "Santé des poissons", "text": "Limite les pathogènes opportunistes."}
            ]
        },
        "audience": {
            "title": "Élevages ciblés",
            "items": [
                "Étangs et bassins tilapia",
                "Cages flottantes",
                "Systèmes intensifs / RAS"
            ],
            "badges": ["Probiotique", "Qualité d’eau"]
        },
        "composition": {
            "title": "Composition fonctionnelle",
            "intro": "Mélange de bactéries bénéfiques, enzymes et minéraux.",
            "rows": [
                {"label": "Souches probiotiques", "value": "Bacillus spp. sélectionnés"},
                {"label": "Enzymes", "value": "Dégradeurs d’amidon et de fibroses"},
                {"label": "Support minéral", "value": "Assure la dispersion dans l’eau"},
                {"label": "Additifs", "value": "Oligo-éléments et activateurs biologiques"},
                {"label": "Formats", "value": "Sachets 500 g / Sacs 10 kg"}
            ]
        },
        "usage": {
            "title": "Mode d’application",
            "note": "Plan adapté selon densité et qualité d’eau actuelle.",
            "steps": [
                {"badge": "Préparation", "title": "Pré-mélange", "text": "Diluer AquaCare dans de l’eau propre avant application."},
                {"badge": "Application", "title": "Pulvérisation", "text": "Répartir sur la surface ou injecter dans le système."},
                {"badge": "Fréquence", "title": "Hebdomadaire ou bi-hebdo", "text": "Selon charge organique."}
            ]
        },
        "logistics": {
            "title": "Services associés",
            "items": [
                {"icon": "bi-flask", "title": "Analyses eau", "text": "pH, ammoniaque, nitrites, O₂."},
                {"icon": "bi-clipboard-data", "title": "Plan AquaCare", "text": "Protocoles personnalisés."},
                {"icon": "bi-people", "title": "Formation", "text": "Application et suivi sur le terrain."}
            ]
        },
        "resources": {
            "title": "Guides AquaCare",
            "intro": "Fiches techniques, checklists de traitement, protocoles RAS."
        },
        "lead": {
            "title": "Parler à un expert qualité d’eau",
            "intro": "Recevez un protocole AquaCare adapté à vos bassins.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme piscicole de Bingerville",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Surface / Volume à traiter",
            "volume_placeholder": "Ex : 1 hectare d’étang",
            "objective_label": "Objectif",
            "objectives": [
                "Réduire les matières organiques",
                "Stabiliser l’ammoniac",
                "Prévenir les mortalités estivales",
                "Installer un protocole durable"
            ],
            "cta": "Recevoir un plan AquaCare"
        },
        "cta": {
            "title": "Gardez le contrôle de votre eau",
            "text": "AquaCare® est disponible avec accompagnement MARIDAV CI.",
            "primary_label": "Demander un protocole",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "AquaCare remplace-t-il les changements d’eau ?", "answer": "Non, il complète vos bonnes pratiques de gestion d’eau."},
            {"question": "Peut-on l’utiliser en présence de poissons ?", "answer": "Oui, il est conçu pour être appliqué en cours de production."},
            {"question": "Comment mesurer l’efficacité ?", "answer": "Surveillez l’ammoniac, la turbidité et la mortalité. Nos techniciens vous accompagnent."}
        ],
        "schema": {
            "name": "AquaCare",
            "description": "Probiotique qualité d’eau Skretting/Nutreco distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/aliments_poissons/aquacare_poissons_maridav_ci.jpg",
            "sku": "AQUACARE",
            "category": "Traitement qualité d’eau",
            "audience": "Pisciculture"
        }
    },
    {
        "file": "kenosan_maridav_ci.html",
        "slug": "kenosan",
        "seo": {
            "title": "Kenosan® — Détergent moussant | MARIDAV CI",
            "description": "Détergent alcalin moussant pour nettoyage des bâtiments d’élevage : puissance et adhérence optimales.",
            "image": "https://maridav.ci/maridav_ci_image/hygiene_biosecurite/Kenosan Maridav.png",
        },
        "breadcrumbs": [
            {"label": "Biosécurité", "url": "biosecurite_maridav_ci.html"},
            {"label": "Kenosan"}
        ],
        "hero": {
            "badges": ["Biosécurité", "Détergent moussant", "Multi-espèces"],
            "title": "Kenosan®",
            "description": "Détergent alcalin ultra-moussant pour éliminer graisses, protéines et matières organiques avant désinfection.",
            "stats": [
                {"value": "1–3 %", "label": "Dilution"},
                {"value": "Bidons 5/20 L", "label": "Formats"},
                {"value": "Action moussante", "label": "Fort pouvoir d’adhérence"}
            ],
            "note": "Produit CID LINES distribué par MARIDAV CI.",
            "image": "maridav_ci_image/hygiene_biosecurite/Kenosan Maridav.png",
            "image_alt": "Bidons Kenosan",
            "media_title": "Nettoyage professionnel",
            "media_points": [
                "Mousse épaisse longue durée",
                "Compatible bâtiments avicoles, porcins, ruminants",
                "Optimise l’efficacité du désinfectant"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "CID LINES (ECOLAB)"},
            {"label": "Distribution", "text": "Exclusivité MARIDAV CI"},
            {"label": "Support", "text": "Techniciens biosécurité MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Atouts Kenosan",
            "title": "Un détergent moussant haut de gamme",
            "features": [
                {"icon": "bi-bucket", "title": "Pouvoir mouillant", "text": "La mousse adhère longtemps pour dissoudre les graisses."},
                {"icon": "bi-arrow-repeat", "title": "Facile à rincer", "text": "Se rince aisément sans laisser de résidus."},
                {"icon": "bi-hammer", "title": "Polyvalent", "text": "Convient aux murs, sols, équipements et véhicules."}
            ]
        },
        "audience": {
            "title": "Sites ciblés",
            "items": [
                "Bâtiments avicoles (chair, ponte)",
                "Sites porcins, ruminants",
                "Abattoirs, camions, silos"
            ],
            "badges": ["Nettoyage", "Détergent"]
        },
        "composition": {
            "title": "Caractéristiques techniques",
            "intro": "Formule alcaline douce pour les surfaces mais puissante contre les graisses.",
            "rows": [
                {"label": "Nature", "value": "Détergent alcalin moussant"},
                {"label": "pH", "value": "Alcalin (≈13)"},
                {"label": "Compatibilité", "value": "Acier inox, carrelage, PVC"},
                {"label": "Formats", "value": "Bidons 5 L, 20 L, IBC"},
                {"label": "Application", "value": "Canon mousse, nettoyeur haute pression"}
            ]
        },
        "usage": {
            "title": "Protocole recommandé",
            "note": "Toujours porter les EPI et suivre les fiches sécurité.",
            "steps": [
                {"badge": "1", "title": "Pré-mouillage", "text": "Retirer la matière organique grossière et mouiller les surfaces."},
                {"badge": "2", "title": "Application mousse", "text": "Diluer 1–3 %, appliquer du bas vers le haut, laisser agir 10–15 min."},
                {"badge": "3", "title": "Rinçage", "text": "Rincer abondamment à l’eau claire avant désinfection."}
            ]
        },
        "logistics": {
            "title": "Services MARIDAV CI",
            "items": [
                {"icon": "bi-hdd-network", "title": "Plan biosécurité", "text": "Protocoles personnalisés par espèce."},
                {"icon": "bi-tools", "title": "Équipement mousse", "text": "Fourniture et réglage des canons mousse."},
                {"icon": "bi-people", "title": "Formation équipes", "text": "Sensibilisation aux bonnes pratiques."}
            ]
        },
        "resources": {
            "title": "Guides nettoyage",
            "intro": "Checklists pré-lavage, fiches sécurité et protocole complet."
        },
        "lead": {
            "title": "Parler à un expert biosécurité",
            "intro": "Planifiez un audit nettoyage & désinfection avec MARIDAV CI.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme Avicole de Bingerville",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Surface à nettoyer (m²)",
            "volume_placeholder": "Ex : 2 000 m²",
            "objective_label": "Objectif",
            "objectives": [
                "Mettre en place Kenosan",
                "Former mes équipes",
                "Optimiser mon protocole",
                "Dimensionner mes équipements"
            ],
            "cta": "Recevoir un plan nettoyage"
        },
        "cta": {
            "title": "Adoptez Kenosan®",
            "text": "Disponible en Côte d’Ivoire avec accompagnement MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Peut-on l’utiliser sur surfaces peintes ?", "answer": "Oui, si la dilution est respectée. Effectuez un test préalable sur nouvelles surfaces."},
            {"question": "Compatibilité avec la mousse chaude ?", "answer": "Oui, Kenosan peut être utilisé avec de l’eau froide ou chaude."},
            {"question": "Quelle est la consommation moyenne ?", "answer": "Entre 0,5 et 1 L de solution par 10 m² selon l’état de surface."}
        ],
        "schema": {
            "name": "Kenosan",
            "description": "Détergent moussant alcalin CID LINES distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/hygiene_biosecurite/Kenosan Maridav.png",
            "sku": "KENOSAN",
            "category": "Détergent biosécurité",
            "audience": "Bâtiments d’élevage"
        }
    },
    {
        "file": "dm_cid_maridav_ci.html",
        "slug": "dm-cid",
        "seo": {
            "title": "DM CID® S24 — Détergent acide | MARIDAV CI",
            "description": "Détergent acide pour éliminer les dépôts minéraux, biofilms et tartres dans les bâtiments et équipements d’élevage.",
            "image": "https://maridav.ci/maridav_ci_image/hygiene_biosecurite/DM Cid S24 Maridav.png",
        },
        "breadcrumbs": [
            {"label": "Biosécurité", "url": "biosecurite_maridav_ci.html"},
            {"label": "DM CID"}
        ],
        "hero": {
            "badges": ["Biosécurité", "Détergent acide", "Multi-espèces"],
            "title": "DM CID® S24",
            "description": "Détergent acide puissant pour dissoudre les dépôts minéraux et préparer les surfaces avant désinfection.",
            "stats": [
                {"value": "0,5–3 %", "label": "Dilution"},
                {"value": "Bidons 5/20 L", "label": "Formats"},
                {"value": "Action rapide", "label": "Élimine les biofilms tenaces"}
            ],
            "note": "Produit CID LINES distribué par MARIDAV CI.",
            "image": "maridav_ci_image/hygiene_biosecurite/DM Cid S24 Maridav.png",
            "image_alt": "Bidons DM CID",
            "media_title": "Nettoyage en profondeur",
            "media_points": [
                "Enlève tartres & dépôts minéraux",
                "Recommandé après plusieurs cycles",
                "Optimise la désinfection"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "CID LINES (ECOLAB)"},
            {"label": "Distribution", "text": "Exclusivité MARIDAV CI"},
            {"label": "Support", "text": "Appui biosécurité MARIDAV"}
        ],
        "benefits": {
            "eyebrow": "Atouts DM CID",
            "title": "Un complément indispensable",
            "features": [
                {"icon": "bi-lightning-charge", "title": "Action rapide", "text": "Dissout les biofilms et dépôts difficiles en quelques minutes."},
                {"icon": "bi-gear", "title": "Polyvalent", "text": "S’utilise sur parois, sols, équipements et circuits d’eau."},
                {"icon": "bi-brush", "title": "Finition impeccable", "text": "Prépare les surfaces pour un résultat de désinfection optimal."}
            ]
        },
        "composition": {
            "title": "Caractéristiques techniques",
            "intro": "Détergent acide à base de phosphates et tensioactifs.",
            "rows": [
                {"label": "Nature", "value": "Détergent acide"},
                {"label": "Compatibilité", "value": "Inox, carrelage, surfaces plastiques"},
                {"label": "Formats", "value": "Bidons 5 L, 20 L, IBC"},
                {"label": "Application", "value": "Basse ou haute pression"},
                {"label": "Usage", "value": "Bâtiments, véhicules, équipements"}
            ]
        },
        "usage": {
            "title": "Protocole recommandé",
            "note": "Porter les EPI adaptés.",
            "steps": [
                {"badge": "1", "title": "Pré-nettoyage", "text": "Retirer la matière organique et mouiller les surfaces."},
                {"badge": "2", "title": "Application", "text": "Diluer 0,5–3 %, appliquer uniformément, laisser agir 10 min."},
                {"badge": "3", "title": "Rinçage", "text": "Rincer abondamment à l’eau claire avant désinfection."}
            ]
        },
        "logistics": {
            "title": "Services MARIDAV",
            "items": [
                {"icon": "bi-tools", "title": "Plan de nettoyage", "text": "Protocoles combinant Kenosan + DM CID + Virocid."},
                {"icon": "bi-truck", "title": "Livraisons rapides", "text": "Stock permanent à Abidjan."},
                {"icon": "bi-people", "title": "Formation", "text": "Sensibilisation des équipes biosécurité."}
            ]
        },
        "resources": {
            "title": "Guides nettoyage acide",
            "intro": "Fiches techniques, fiches sécurité et checklists."
        },
        "lead": {
            "title": "Parler à un expert biosécurité",
            "intro": "Nous dimensionnons votre protocole de lavage selon l’espèce et les surfaces.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Elevage Porcin de Bouaké",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Surface / équipements",
            "volume_placeholder": "Ex : 1 bâtiment 1 500 m²",
            "objective_label": "Objectif",
            "objectives": [
                "Dégraisser mes bâtiments",
                "Traiter mes dépôts calcaires",
                "Former mes équipes",
                "Mettre à jour mon protocole"
            ],
            "cta": "Recevoir un plan lavage"
        },
        "cta": {
            "title": "Ajoutez DM CID à votre protocole",
            "text": "Disponible en Côte d’Ivoire via MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Quand utiliser DM CID ?", "answer": "Après plusieurs cycles ou lorsque des dépôts minéraux apparaissent."},
            {"question": "Est-il compatible avec l’inox ?", "answer": "Oui, respecter les dilutions pour éviter toute corrosion."},
            {"question": "Peut-on l’utiliser dans les circuits d’eau ?", "answer": "Préférez CID 2000 pour les tuyauteries. DM CID est destiné aux surfaces."}
        ],
        "schema": {
            "name": "DM CID S24",
            "description": "Détergent acide pour biosécurité CID LINES distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/hygiene_biosecurite/DM Cid S24 Maridav.png",
            "sku": "DM-CID",
            "category": "Détergent acide",
            "audience": "Bâtiments d’élevage"
        }
    },
    {
        "file": "virocid_maridav_ci.html",
        "slug": "virocid",
        "seo": {
            "title": "Virocid® — Désinfectant large spectre | MARIDAV CI",
            "description": "Désinfectant homologué (virus, bactéries, spores, levures) pour bâtiments d’élevage et transport.",
            "image": "https://maridav.ci/maridav_ci_image/hygiene_biosecurite/virocid.webp",
        },
        "breadcrumbs": [
            {"label": "Biosécurité", "url": "biosecurite_maridav_ci.html"},
            {"label": "Virocid"}
        ],
        "hero": {
            "badges": ["Biosécurité", "Désinfectant", "Large spectre"],
            "title": "Virocid®",
            "description": "Référence mondiale des désinfectants : actif sur virus, bactéries, levures et spores à très faible dosage.",
            "stats": [
                {"value": "0,25–0,5 %", "label": "Dilution standard"},
                {"value": "Homologations", "label": "OIE / normes internationales"},
                {"value": "Bidons 5/20 L", "label": "Formats"}
            ],
            "note": "Produit CID LINES (ECOLAB) distribué par MARIDAV CI.",
            "image": "maridav_ci_image/hygiene_biosecurite/virocid.webp",
            "image_alt": "Bidons Virocid",
            "media_title": "Désinfection totale",
            "media_points": [
                "Spectre complet",
                "Efficace même en eau dure",
                "Compatible fumigation"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "CID LINES (ECOLAB)"},
            {"label": "Homologations", "text": "Reconnu par l’OIE et organismes vétérinaires internationaux"},
            {"label": "Support", "text": "Programme biosécurité MARIDAV CI"}
        ],
        "benefits": {
            "eyebrow": "Atouts Virocid",
            "title": "La référence désinfection",
            "features": [
                {"icon": "bi-shield-lock", "title": "Spectre large", "text": "Actif sur plus de 300 souches testées."},
                {"icon": "bi-droplet", "title": "Utilisation flexible", "text": "Pulvérisation, nébulisation, pédiluves, etc."},
                {"icon": "bi-cash-coin", "title": "Faible dosage", "text": "Economique grâce à des dilutions réduites."}
            ]
        },
        "composition": {
            "title": "Caractéristiques",
            "intro": "Synergie de composés quaternaires, glutaraldéhyde et alcool.",
            "rows": [
                {"label": "Nature", "value": "Désinfectant concentré"},
                {"label": "Compatibilité", "value": "Matériaux courants (suivre dilutions)"},
                {"label": "Applications", "value": "Bâtiments, véhicules, pédiluves, nébulisation"},
                {"label": "Temps de contact", "value": "5–10 min selon dilution"},
                {"label": "Formats", "value": "5 L, 20 L, 200 L"}
            ]
        },
        "usage": {
            "title": "Protocole",
            "note": "Toujours nettoyer avant de désinfecter.",
            "steps": [
                {"badge": "Pulvérisation", "title": "0,25–0,5 %", "text": "Appliquer sur surfaces propres, laisser sécher."},
                {"badge": "Fumigation", "title": "0,5–1 %", "text": "Nébuliser pour traiter l’air et les zones difficiles."},
                {"badge": "Pédiluves", "title": "1 %", "text": "Renouveler régulièrement pour garantir l’efficacité."}
            ]
        },
        "logistics": {
            "title": "Services MARIDAV",
            "items": [
                {"icon": "bi-tools", "title": "Plan biosécurité", "text": "Protocoles personnalisés par espèce."},
                {"icon": "bi-truck", "title": "Livraison & stockage", "text": "Stock permanent à Abidjan."},
                {"icon": "bi-people", "title": "Formation", "text": "Application & sécurité."}
            ]
        },
        "resources": {
            "title": "Guides désinfection",
            "intro": "Fiches techniques, fiches sécurité et checklists Virocid."
        },
        "lead": {
            "title": "Parler à un expert biosécurité",
            "intro": "Recevez un plan désinfection complet (nettoyage + désinfection).",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme Avicole de Korhogo",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Surface / volume",
            "volume_placeholder": "Ex : 3 bâtiments 1500 m²",
            "objective_label": "Objectif",
            "objectives": [
                "Mettre à jour mon protocole",
                "Installer des pédiluves",
                "Former mes équipes",
                "Planifier une nébulisation"
            ],
            "cta": "Recevoir un plan désinfection"
        },
        "cta": {
            "title": "Adoptez Virocid®",
            "text": "Le désinfectant n°1 mondial disponible chez MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Virocid est-il compatible avec l’eau dure ?", "answer": "Oui, sa formule reste efficace même en eau dure."},
            {"question": "Peut-on l’utiliser en présence d’animaux ?", "answer": "Appliquer hors présence d’animaux, laisser sécher avant réintroduction."},
            {"question": "Quelle est la stabilité de la solution ?", "answer": "Utiliser les solutions préparées dans les 24 h."}
        ],
        "schema": {
            "name": "Virocid",
            "description": "Désinfectant large spectre CID LINES distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/hygiene_biosecurite/virocid.webp",
            "sku": "VIROCID",
            "category": "Désinfectant",
            "audience": "Bâtiments d’élevage"
        }
    },
    {
        "file": "cid_2000_maridav_ci.html",
        "slug": "cid-2000",
        "seo": {
            "title": "CID 2000® — Nettoyant tuyauteries & eau | MARIDAV CI",
            "description": "Détergent acide pour nettoyer et désinfecter les circuits d’eau, abreuvoirs et brumisateurs.",
            "image": "https://maridav.ci/maridav_ci_image/hygiene_biosecurite/cid_2000_maridav.ci.jpg",
        },
        "breadcrumbs": [
            {"label": "Biosécurité", "url": "biosecurite_maridav_ci.html"},
            {"label": "CID 2000"}
        ],
        "hero": {
            "badges": ["Biosécurité", "Nettoyage eau", "Multi-espèces"],
            "title": "CID 2000®",
            "description": "Nettoyant acide et désinfectant pour circuits d’eau : élimine biofilms, dépôts de calcaire et bactéries.",
            "stats": [
                {"value": "0,5–2 %", "label": "Dosage"},
                {"value": "Compatibilité", "label": "PVC, inox, PE"},
                {"value": "Bidons 5/20 L", "label": "Formats"}
            ],
            "note": "Produit CID LINES distribué par MARIDAV CI.",
            "image": "maridav_ci_image/hygiene_biosecurite/cid_2000_maridav.ci.jpg",
            "image_alt": "Bidon CID 2000",
            "media_title": "Hygiène eau",
            "media_points": [
                "Nettoie et désinfecte en un passage",
                "Élimine les biofilms",
                "Prépare les lignes pour l’alimentation en eau"
            ]
        },
        "trust": [
            {"label": "Origine", "text": "CID LINES (ECOLAB)"},
            {"label": "Usage", "text": "Approbation vétérinaire multi-espèces"},
            {"label": "Support", "text": "Techniciens eau MARIDAV CI"}
        ],
        "benefits": {
            "eyebrow": "Atouts CID 2000",
            "title": "Des lignes d’eau propres",
            "features": [
                {"icon": "bi-droplet", "title": "Qualité d’eau", "text": "Supprime les biofilms et dépôts qui hébergent les bactéries."},
                {"icon": "bi-tools", "title": "Polyvalent", "text": "S’utilise en curatif ou préventif sur toutes les lignes d’eau."},
                {"icon": "bi-thermometer-sun", "title": "Compatible eau chaude/froide", "text": "Efficace quelle que soit la température."}
            ]
        },
        "composition": {
            "title": "Caractéristiques techniques",
            "intro": "Détergent acide contenant agents tensioactifs et désinfectants.",
            "rows": [
                {"label": "Nature", "value": "Détergent acide pour circuits d’eau"},
                {"label": "Compatibilité", "value": "PVC, PE, inox (suivre dilution)"},
                {"label": "Formats", "value": "5 L, 20 L"},
                {"label": "Applications", "value": "Abreuvoirs, brumisateurs, tanks"},
                {"label": "Temps de contact", "value": "30–60 min selon encrassement"}
            ]
        },
        "usage": {
            "title": "Protocole recommandées",
            "note": "Hors présence d’animaux.",
            "steps": [
                {"badge": "1", "title": "Vidange des lignes", "text": "Éliminer l’eau stagnante."},
                {"badge": "2", "title": "Circulation", "text": "Injecter la solution diluée (0,5–2 %) et laisser agir."},
                {"badge": "3", "title": "Rinçage", "text": "Rincer abondamment jusqu’à pH neutre avant remise en eau."}
            ]
        },
        "logistics": {
            "title": "Services MARIDAV",
            "items": [
                {"icon": "bi-droplet-half", "title": "Audit eau", "text": "Analyses pH/dureté pour dimensionner le protocole."},
                {"icon": "bi-broadcast", "title": "Installation pompe doseuse", "text": "Support à l’équipement."},
                {"icon": "bi-people", "title": "Formation", "text": "Opérations de nettoyage des lignes."}
            ]
        },
        "resources": {
            "title": "Guides eau",
            "intro": "Checklists de nettoyage, fiches sécurité, protocole combiné avec Biotronic Liquid."
        },
        "lead": {
            "title": "Parler à un expert hygiène eau",
            "intro": "Planifiez vos opérations de nettoyage avec MARIDAV CI.",
            "name_label": "Nom &amp; structure",
            "name_placeholder": "Ex : Ferme Avicole de Songon",
            "contact_label": "Téléphone / WhatsApp",
            "volume_label": "Longueur de tuyauterie (m)",
            "volume_placeholder": "Ex : 600 m",
            "objective_label": "Objectif",
            "objectives": [
                "Nettoyer mes lignes d’eau",
                "Installer une pompe doseuse",
                "Contrôler mes biofilms",
                "Former mes équipes"
            ],
            "cta": "Recevoir un protocole CID 2000"
        },
        "cta": {
            "title": "Gardez vos lignes propres",
            "text": "CID 2000® est en stock chez MARIDAV CI.",
            "primary_label": "Demander un devis",
            "primary_url": "contact.html",
            "secondary_label": "WhatsApp direct",
            "secondary_url": "https://api.whatsapp.com/send?phone=+2250574648888"
        },
        "faq": [
            {"question": "Peut-on l’utiliser en présence d’animaux ?", "answer": "Non, nettoyer et rincer avant de remettre l’eau aux animaux."},
            {"question": "Fréquence recommandée ?", "answer": "À chaque vide sanitaire et en prévention toutes les 6–8 semaines."},
            {"question": "Compatible avec les pompes doseuses ?", "answer": "Oui, en respectant les matériaux compatibles et les dilutions."}
        ],
        "schema": {
            "name": "CID 2000",
            "description": "Nettoyant acide et désinfectant pour circuits d’eau distribué par MARIDAV CI.",
            "image": "https://maridav.ci/maridav_ci_image/hygiene_biosecurite/cid_2000_maridav.ci.jpg",
            "sku": "CID-2000",
            "category": "Nettoyant circuits d’eau",
            "audience": "Bâtiments d’élevage"
        }
    }
]


def build_product(product: dict[str, object]) -> None:
    hero = product["hero"]
    resources = product.get("resources", {})
    lead = product["lead"]

    breadcrumb_items = []
    for crumb in product["breadcrumbs"]:
        label = escape(crumb["label"])
        url = crumb.get("url")
        if url:
            breadcrumb_items.append(f"                <li class=\"breadcrumb-item\"><a href=\"{url}\">{label}</a></li>")
        else:
            breadcrumb_items.append(f"                <li class=\"breadcrumb-item active\" aria-current=\"page\">{label}</li>")

    features_html = render_feature_cards(product["benefits"]["features"])
    audience_data = product.get("audience", DEFAULT_AUDIENCE)
    audience_list = render_list(audience_data["items"])
    audience_badges = render_badges(audience_data["badges"])
    hero_stats = render_stat_pills(hero["stats"])
    hero_media = "\n".join(f"                  <li>{escape(item)}</li>" for item in hero["media_points"])
    trust_html = render_trust(product.get("trust", DEFAULT_TRUST))
    composition_rows = render_table_rows(product["composition"]["rows"])
    usage_steps = render_usage(product["usage"]["steps"])
    logistics_items = render_logistics(product["logistics"]["items"])
    resources_buttons = render_resource_buttons(resources.get("buttons", DEFAULT_RESOURCES))
    lead_objectives = render_objectives(lead["objectives"])

    faq_html, faq_entities = render_faq(product["faq"], product["slug"])

    schema_product = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product["schema"]["name"],
        "description": product["schema"]["description"],
        "brand": {"@type": "Organization", "name": "MARIDAV Côte d'Ivoire"},
        "image": product["schema"]["image"],
        "sku": product["schema"]["sku"],
        "category": product["schema"]["category"],
        "audience": {"@type": "Audience", "audienceType": product["schema"]["audience"]},
        "offers": {
            "@type": "Offer",
            "priceCurrency": "XOF",
            "price": "Sur devis",
            "availability": "https://schema.org/InStock",
            "url": f"https://maridav.ci/{product['file']}"
        }
    }, ensure_ascii=False, indent=2)

    schema_faq = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_entities}, ensure_ascii=False, indent=2)

    context = {
        "seo_title": product["seo"]["title"],
        "seo_description": product["seo"]["description"],
        "seo_image": product["seo"]["image"],
        "header": HEADER,
        "footer": FOOTER,
        "breadcrumb_html": "\n".join(breadcrumb_items),
        "hero_badges": render_badges(hero["badges"]),
        "hero_title": escape(hero["title"]),
        "hero_description": escape(hero["description"]),
        "hero_stats": hero_stats,
        "hero_note": escape(hero["note"]),
        "hero_image": hero["image"],
        "hero_image_alt": escape(hero["image_alt"]),
        "hero_media_title": escape(hero["media_title"]),
        "hero_media_list": hero_media,
        "trust_html": trust_html,
        "benefits_eyebrow": escape(product["benefits"].get("eyebrow", "Promesse produit")),
        "benefits_title": escape(product["benefits"]["title"]),
        "features_html": features_html,
        "audience_title": escape(audience_data["title"]),
        "audience_list": audience_list,
        "audience_badges": audience_badges,
        "composition_title": escape(product["composition"]["title"]),
        "composition_intro": escape(product["composition"]["intro"]),
        "composition_rows": composition_rows,
        "usage_title": escape(product["usage"]["title"]),
        "usage_steps": usage_steps,
        "usage_note": escape(product["usage"].get("note", "")),
        "logistics_title": escape(product["logistics"]["title"]),
        "logistics_items": logistics_items,
        "resources_title": escape(resources.get("title", "Kits techniques à télécharger")),
        "resources_intro": escape(resources.get("intro", "Fiches techniques, guides et checklists disponibles auprès de nos équipes.")),
        "resources_buttons": resources_buttons,
        "lead_title": escape(lead["title"]),
        "lead_intro": escape(lead["intro"]),
        "lead_name_label": lead["name_label"],
        "lead_name_placeholder": lead["name_placeholder"],
        "lead_contact_label": lead["contact_label"],
        "lead_volume_label": lead["volume_label"],
        "lead_volume_placeholder": lead["volume_placeholder"],
        "lead_objective_label": lead["objective_label"],
        "lead_objectives": lead_objectives,
        "lead_cta": lead["cta"],
        "faq_title": escape(product.get("faq_title", f"FAQ {product['schema']['name']}")),
        "faq_items": faq_html,
        "cta_title": escape(product["cta"]["title"]),
        "cta_text": escape(product["cta"]["text"]),
        "cta_primary_label": escape(product["cta"]["primary_label"]),
        "cta_primary_url": product["cta"]["primary_url"],
        "cta_secondary_label": escape(product["cta"]["secondary_label"]),
        "cta_secondary_url": product["cta"]["secondary_url"],
        "schema_product": schema_product,
        "schema_faq": schema_faq,
    }

    html = TEMPLATE.substitute(**context)
    (ROOT / product["file"]).write_text(html, encoding='utf-8')


def main() -> None:
    for product in PRODUCTS:
        build_product(product)


if __name__ == "__main__":
    main()
