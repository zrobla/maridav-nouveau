#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constructeur des pages produits VOLAILLES — MARIDAV CI.

Source unique : products.json (catalogue + contenu éditorial par produit).
Sortie : une page HTML par produit, au gabarit premium « pdp » (cf. GABARIT-PAGE-PRODUIT.md).

Principe : le chrome (head CSS, navbar, footer, scripts) est identique partout et figé
ici en constantes ; seul le contenu (hero, bénéfices, mode d'emploi, fiche, FAQ, liés,
CTA) + les métadonnées + les 3 blocs JSON-LD varient, dérivés de la donnée.

Usage : python3 build_maridav.py            # génère toutes les pages produits
        python3 build_maridav.py --check    # génère en mémoire et montre un résumé
"""
import json
import re
import sys
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "products.json"            # volailles (source historique)
PORC_DATA    = ROOT / "products-porcs.json"     # porcs
POISSON_DATA = ROOT / "products-poissons.json"  # pisciculture

# Registre des sources produits (même schéma). Les pages produits sont générées
# pour chaque source ; render_page est espèce-agnostique.
PRODUCT_SOURCES = [DATA, PORC_DATA, POISSON_DATA]

# --------------------------------------------------------------------------- #
#  Constantes de marque (source unique)                                        #
# --------------------------------------------------------------------------- #
SITE = {
    "base": "https://maridav.ci",
    "brand": "MARIDAV Côte d'Ivoire",
    "tel_href": "tel:002252721353242",
    "tel_label": "(+225) 27 21 35 32 42",
    "wa": "https://api.whatsapp.com/send?phone=+2250574648888",
    "wa_label": "05 74 64 88 88",
}

# --------------------------------------------------------------------------- #
#  Chrome — verbatim depuis les pages de référence (concentre_chair_31 /       #
#  aliments_chair_finition). NE PAS diverger sans mettre à jour le gabarit.    #
# --------------------------------------------------------------------------- #
HEAD_CSS = r"""  <style>
    :root{
      --navy:#000066; --navy-2:#04153b; --navy-deep:#020b22;
      --green:#1b8e3e; --green-2:#2aa154; --green-soft:#6ee7a8;
      --gold:#6ee7a8; --ink:#0e1c36; --muted:#34465f; --line:rgba(2,12,46,.10);
      --paper:#f6f7f9; --radius:20px;
      --shadow:0 26px 60px -34px rgba(2,12,46,.5);
    }
    body.pdp{background:var(--paper);color:var(--ink);font-family:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
    .pdp main{overflow:hidden}
    .pdp .premium-header{position:sticky;top:0;z-index:1030}
    .pdp .text-muted{color:var(--muted)!important}
    .pdp h1,.pdp h2,.pdp .display{font-family:"Fraunces","Georgia",serif;letter-spacing:-.01em}
    .pdp ::selection{background:rgba(27,142,62,.22)}
    .navbar-premium{background:rgba(255,255,255,.97);box-shadow:0 14px 34px rgba(2,12,46,.10)}
    .pdp .btn-pill{display:inline-flex;align-items:center;gap:.5rem;border-radius:999px;font-weight:700;font-size:.95rem;padding:.8rem 1.4rem;text-decoration:none;transition:transform .25s,box-shadow .25s,gap .25s}
    .pdp .btn-green{background:linear-gradient(135deg,var(--green),var(--green-2));color:#fff;box-shadow:0 16px 30px -12px rgba(27,142,62,.7)}
    .pdp .btn-green:hover{transform:translateY(-2px);gap:.7rem;box-shadow:0 22px 40px -12px rgba(27,142,62,.85);color:#fff}
    .pdp .btn-ghost{border:1.5px solid rgba(255,255,255,.5);color:#fff}
    .pdp .btn-ghost:hover{background:rgba(255,255,255,.12);color:#fff;transform:translateY(-2px)}
    .pdp .btn-line{color:var(--navy);font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.4rem;border-bottom:2px solid rgba(0,0,102,.25);padding-bottom:2px;transition:gap .25s,border-color .25s}
    .pdp .btn-line:hover{gap:.65rem;border-bottom-color:var(--green)}

    /* HERO */
    .pdp-hero{position:relative;background:radial-gradient(120% 120% at 80% -10%,#0a2a73 0%,var(--navy) 38%,var(--navy-deep) 100%);color:#fff;overflow:hidden;padding:clamp(2.6rem,5vw,4.6rem) 0 clamp(3rem,5vw,4.4rem)}
    .pdp-hero::before{content:"";position:absolute;inset:0;background:radial-gradient(closest-side,rgba(27,142,62,.4),transparent 70%);width:520px;height:520px;top:-180px;left:-120px;filter:blur(20px);opacity:.5;pointer-events:none}
    .pdp-hero::after{content:"";position:absolute;inset:0;opacity:.5;pointer-events:none;background-image:radial-gradient(rgba(255,255,255,.10) 1px,transparent 1px);background-size:22px 22px;mask-image:linear-gradient(180deg,transparent,#000 40%,transparent)}
    .pdp-hero .container{position:relative;z-index:2}
    .pdp-crumb a{color:rgba(255,255,255,.7);text-decoration:none}
    .pdp-crumb a:hover{color:#fff}
    .pdp-eyebrow{display:inline-flex;align-items:center;gap:.55rem;font-size:.74rem;font-weight:800;letter-spacing:.22em;text-transform:uppercase;color:var(--green-soft)}
    .pdp-eyebrow::before{content:"";width:26px;height:2px;background:var(--gold);display:inline-block}
    .pdp-hero h1{font-weight:600;font-size:clamp(2.2rem,4.6vw,3.5rem);line-height:1.05;margin:.7rem 0 .2rem}
    .pdp-hero h1 .accent{color:var(--green-soft);font-style:normal}
    .pdp-trans{display:inline-flex;align-items:center;gap:.5rem;margin:.7rem 0;padding:.4rem .9rem;border-radius:999px;background:rgba(110,231,168,.14);border:1px solid rgba(110,231,168,.35);color:#cde7d6;font-weight:700;font-size:.82rem}
    .pdp-lead{color:rgba(255,255,255,.82);font-size:1.06rem;line-height:1.6;max-width:36rem}
    .pdp-figure{position:relative;border-radius:24px;background:linear-gradient(160deg,#fff,#eef3fb);box-shadow:0 40px 80px -30px rgba(0,0,0,.6);padding:18px;transform:rotate(-1.4deg);transition:transform .5s}
    .pdp-figure:hover{transform:rotate(0)}
    .pdp-figure img{width:100%;border-radius:14px;display:block}
    .pdp-figure::before{content:"";position:absolute;width:64px;height:64px;border-top:3px solid var(--green);border-right:3px solid var(--green);top:-10px;right:-10px;border-radius:0 10px 0 0}
    .pdp-figchip{position:absolute;bottom:-16px;left:24px;background:var(--navy);color:#fff;border-radius:14px;padding:.7rem 1.1rem;box-shadow:var(--shadow);font-weight:700}
    .pdp-figchip small{display:block;color:var(--green-soft);font-weight:600;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase}
    /* facts strip */
    .pdp-facts{display:grid;grid-template-columns:.8fr .68fr 1.32fr .92fr;gap:0;margin-top:clamp(1.6rem,4vw,2.6rem);border:1px solid rgba(255,255,255,.14);border-radius:16px;overflow:hidden;background:rgba(255,255,255,.04)}
    .pdp-fact{padding:.85rem .9rem;border-right:1px solid rgba(255,255,255,.12);min-width:0}
    .pdp-fact:last-child{border-right:0}
    .pdp-fact b{display:block;font-family:"Fraunces",serif;font-size:1.05rem;color:#fff;line-height:1.1;white-space:nowrap}
    .pdp-fact span{display:block;font-size:.72rem;color:rgba(255,255,255,.64);white-space:nowrap}

    /* SECTIONS */
    .pdp-sec{padding:clamp(2.8rem,5vw,4.4rem) 0}
    .pdp-kicker{font-size:.74rem;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:var(--green)}
    .pdp-h2{font-weight:600;font-size:clamp(1.6rem,3.2vw,2.3rem);color:var(--navy);margin:.4rem 0 0;line-height:1.12}
    /* titres sur fonds sombres = blanc (neutralise le h1..h6{color:#232323} global du legacy) */
    .pdp-hero h1,.pdp-hero h2,.pdp-ctaband h1,.pdp-ctaband h2,.pdp-ctaband h3,.pdp-spec h2,.pdp-spec h3,.pdp-spec h4,.pdp-figchip{color:#fff}
    .pdp-card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:1.6rem}
    .pdp-benefit{display:flex;gap:1rem;align-items:flex-start}
    .pdp-bicon{flex:none;width:46px;height:46px;border-radius:13px;display:inline-flex;align-items:center;justify-content:center;background:linear-gradient(135deg,rgba(27,142,62,.14),rgba(42,161,84,.14));color:var(--green);font-size:1.2rem}
    .pdp-benefit h5{font-weight:700;margin:0 0 .2rem;color:var(--navy)}
    .pdp-benefit p{margin:0;color:var(--muted);font-size:.93rem;line-height:1.5}

    /* sticker transversalité (réutilisable: produits multi-filières) */
    .pdp-transbadge{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1rem 1.4rem;background:linear-gradient(120deg,#04204a,var(--navy));color:#fff;border-radius:16px;padding:1rem 1.4rem;box-shadow:var(--shadow);position:relative;overflow:hidden}
    .pdp-transbadge::before{content:"";position:absolute;width:200px;height:200px;left:-70px;top:-70px;background:radial-gradient(closest-side,rgba(27,142,62,.4),transparent);pointer-events:none}
    .pdp-transbadge .tb-head{display:flex;align-items:center;gap:.85rem;position:relative;z-index:1}
    .pdp-transbadge .tb-ic{flex:none;width:44px;height:44px;border-radius:12px;background:rgba(110,231,168,.16);border:1px solid rgba(110,231,168,.35);color:var(--green-soft);display:inline-flex;align-items:center;justify-content:center;font-size:1.2rem}
    .pdp-transbadge .tb-label{display:block;font-family:"Fraunces",serif;font-weight:600;font-size:1.08rem;color:#fff;line-height:1.15}
    .pdp-transbadge .tb-sub{display:block;font-size:.82rem;color:rgba(255,255,255,.66)}
    .pdp-transbadge .tb-filieres{display:flex;flex-wrap:wrap;gap:.5rem;position:relative;z-index:1}
    .pdp-transbadge .tb-chip{display:inline-flex;align-items:center;gap:.45rem;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);border-radius:999px;padding:.5rem .95rem;font-weight:700;font-size:.86rem;color:#fff}
    .pdp-transbadge .tb-chip i{color:var(--green-soft)}

    /* steps */
    .pdp-step{display:flex;gap:1.2rem;align-items:flex-start;position:relative;padding-bottom:1.6rem}
    .pdp-step:not(:last-child)::before{content:"";position:absolute;left:23px;top:48px;bottom:0;width:2px;background:linear-gradient(var(--green),rgba(27,142,62,.1))}
    .pdp-step .num{flex:none;width:48px;height:48px;border-radius:50%;background:var(--navy);color:#fff;font-family:"Fraunces",serif;font-weight:600;display:inline-flex;align-items:center;justify-content:center;font-size:1.2rem;z-index:1}
    .pdp-step h5{font-weight:700;color:var(--navy);margin:.4rem 0 .2rem}
    .pdp-step p{margin:0;color:var(--muted);font-size:.94rem;line-height:1.55}

    /* spec table (navy card) */
    .pdp-spec{background:linear-gradient(165deg,#04204a,var(--navy-deep));border-radius:var(--radius);padding:1.8rem;color:#fff;box-shadow:var(--shadow);position:relative;overflow:hidden}
    .pdp-spec::before{content:"";position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--gold),var(--green))}
    .pdp-spec table{width:100%;border-collapse:collapse}
    .pdp-spec td{padding:.7rem 0;border-bottom:1px dashed rgba(255,255,255,.14);vertical-align:top;font-size:.92rem}
    .pdp-spec tr:last-child td{border-bottom:0}
    .pdp-spec td:first-child{color:rgba(255,255,255,.62);width:46%;padding-right:1rem}
    .pdp-spec td:last-child{color:#fff;font-weight:600}

    /* faq via details */
    .pdp-faq details{background:#fff;border:1px solid var(--line);border-radius:14px;margin-bottom:.7rem;overflow:hidden}
    .pdp-faq summary{list-style:none;cursor:pointer;padding:1.05rem 1.2rem;font-weight:700;color:var(--navy);display:flex;justify-content:space-between;align-items:center;gap:1rem}
    .pdp-faq summary::-webkit-details-marker{display:none}
    .pdp-faq summary::after{content:"\F4FE";font-family:"bootstrap-icons";color:var(--green);transition:transform .3s;font-weight:400}
    .pdp-faq details[open] summary::after{transform:rotate(45deg)}
    .pdp-faq details[open] summary{background:rgba(27,142,62,.06)}
    .pdp-faq .ans{padding:0 1.2rem 1.1rem;color:var(--muted);font-size:.94rem;line-height:1.6}

    /* related */
    .pdp-rel{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);transition:transform .3s,box-shadow .3s;height:100%}
    .pdp-rel:hover{transform:translateY(-6px);box-shadow:0 36px 64px -30px rgba(2,12,46,.5)}
    .pdp-rel img{width:100%;height:180px;object-fit:contain;background:#fff;padding:.7rem}
    .pdp-rel .bd{padding:1.2rem;display:flex;flex-direction:column;flex:1}
    .pdp-rel h5{font-weight:700;color:var(--navy);margin:0 0 .25rem}
    .pdp-rel p{color:var(--muted);font-size:.88rem;margin:0 0 .9rem}
    .pdp-rel .btn-line{margin-top:auto;align-self:flex-start}
    .pdp-tag{display:inline-block;font-size:.68rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--green);background:rgba(27,142,62,.1);border-radius:999px;padding:.25rem .6rem;margin-bottom:.5rem;align-self:flex-start}

    /* CTA band */
    .pdp-ctaband{background:radial-gradient(120% 140% at 0% 0%,#0a2a73,var(--navy) 45%,var(--navy-deep));color:#fff;border-radius:26px;padding:clamp(2rem,4vw,3.2rem);position:relative;overflow:hidden;box-shadow:var(--shadow)}
    .pdp-ctaband::after{content:"";position:absolute;right:-60px;bottom:-80px;width:300px;height:300px;border-radius:50%;background:radial-gradient(closest-side,rgba(27,142,62,.35),transparent);pointer-events:none}
    .pdp-ctaband h2{font-weight:600;font-size:clamp(1.5rem,3vw,2.1rem)}

    /* reveal */
    @keyframes pdpUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
    .pdp-reveal{animation:pdpUp .7s both}
    .d1{animation-delay:.08s}.d2{animation-delay:.16s}.d3{animation-delay:.24s}.d4{animation-delay:.32s}

    /* footer */
    .footer-premium .footer-top{padding:3rem 0;background:#020a1c;color:#fff}
    .footer-premium .footer-bottom{background:#010512;color:#b2bed5;padding:1rem 0}
    .footer-premium .brand{display:flex;align-items:center;gap:1rem}
    .footer-premium .brand img{height:46px}
    .footer-premium .small-link{color:#d0d7ea;text-decoration:none;font-size:.95rem}
    .footer-premium .small-link:hover{color:var(--green-soft)}
    .footer-contact li{display:flex;gap:.6rem;font-size:.95rem;margin-bottom:.85rem}
    .footer-social a{color:#fff;margin-right:.65rem}

    @media (max-width:991px){
      .pdp-facts{grid-template-columns:repeat(2,1fr)}
      .pdp-fact:nth-child(2){border-right:0}
      .pdp-transbadge{align-items:flex-start}
      .pdp-figure{transform:none;margin-top:1.4rem}
    }
    @media (prefers-reduced-motion:reduce){.pdp-reveal{animation:none}.pdp-figure,.pdp-rel,.btn-green,.btn-ghost{transition:none}}
  </style>"""

NAVBAR = """  <header class="premium-header sticky-top" role="banner">
    <nav class="navbar navbar-expand-lg navbar-premium" aria-label="Navigation principale">
      <div class="container">
        <a class="navbar-brand" href="index.html" aria-label="MARIDAV CI">
          <img src="maridav_ci_image/logo/logo_maridav_ci.png" alt="Logo MARIDAV CI">
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
                <li><a class="dropdown-item" href="carriere-maridav.html">CARRIÈRE</a></li>
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
  </header>"""

FOOTER = """  <footer class="footer-premium" role="contentinfo">
    <div class="footer-top">
      <div class="container">
        <div class="row g-4">
          <div class="col-12 col-lg-4">
            <div class="brand">
              <img src="maridav_ci_image/logo/logo_maridav_ci.png" alt="MARIDAV">
              <span>MARIDAV Côte d'Ivoire<small>Nutrition &amp; Santé Animales</small></span>
            </div>
            <p class="mt-3 small">Formulations tropicalisées, appui technique terrain et biosécurité pour volailles, porcs et poissons. Couverture nationale en Côte d'Ivoire.</p>
            <a class="btn btn-brand btn-sm mt-2" href="contact.html">Parler à un expert</a>
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
              <li><a class="small-link" href="distributeurs_maridav.html">Points de vente</a></li>
              <li><a class="small-link" href="contact.html">Demander un devis</a></li>
              <li><a class="small-link" href="carriere-maridav.html">Carrière</a></li>
            </ul>
          </div>
          <div class="col-12 col-lg-3">
            <h6>Contact</h6>
            <ul class="list-unstyled footer-contact">
              <li><i class="fas fa-map-marker-alt"></i><span>Marcory Zone 4C Biétry, 34 Rue Alex Flemming – Abidjan</span></li>
              <li><i class="far fa-clock"></i><span>Lundi – Vendredi : 08h – 18h<br>Samedi : 08h – 13h</span></li>
            </ul>
            <div class="d-flex flex-column gap-2 mt-2">
              <a class="small-link" href="mailto:info@maridav.ci"><i class="fas fa-envelope"></i> info@maridav.ci</a>
              <a class="small-link" href="tel:002252721353242"><i class="fas fa-phone"></i> (+225) 27 21 35 32 42</a>
            </div>
            <div class="footer-social mt-2"><i class="fas fa-share-alt"></i><small> Suivez-Nous! </small>
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
        <p class="mb-0 small">Site web conçu par <a href="https://tech-and-web.com" target="_blank" rel="noopener" style="color:var(--green-soft)">TECH &amp; WEB</a></p>
      </div>
    </div>
  </footer>"""

# Libellés filière pour les chips de transversalité
FILIERE_LABELS = {
    "volailles-chair": ("bi-egg-fried", "Poulets de chair"),
    "volailles-ponte": ("bi-egg", "Pondeuses"),
    "porcs": ("bi-piggy-bank", "Porcs"),
    "poissons": ("bi-water", "Poissons"),
}

# Métadonnées par catégorie produit (clé top-level products.json) — pilote la matrice :
# mode de production (prêt à l'emploi vs FAF) + libellé de carte.
CATEGORY_META = {
    "aliments_complets": {"mode": "pret", "label": "Aliment complet", "icon": "bi-bag-check"},
    "concentres":        {"mode": "faf",  "label": "Concentré",       "icon": "bi-sliders"},
    "macro_premix":      {"mode": "faf",  "label": "Macro-prémix",    "icon": "bi-grid-3x3-gap"},
    "premix":            {"mode": "faf",  "label": "Prémix",          "icon": "bi-eyedropper"},
    "additifs":          {"mode": "pret", "label": "Additif",         "icon": "bi-water"},
}

# --------------------------------------------------------------------------- #
#  Configuration éditoriale des pages FILIÈRE (hub-niveau, pas produit).        #
#  La matrice produits est DÉRIVÉE de products.json (filtrée par filière) ;     #
#  ici seul le contenu rédactionnel de page (hero, frise, modes, preuve) vit.   #
#  Règles : FR, FCFA, Côte d'Ivoire, AUCUN chiffre de résultat inventé.         #
# --------------------------------------------------------------------------- #
FILIERES = {
    "volailles-chair": {
        "url": "poulets_chair_maridav_ci.html",
        "title": "Poulets de chair — programme complet & FAF | MARIDAV Côte d'Ivoire",
        "description": "Nutrition poulets de chair en Côte d'Ivoire : programme démarrage → croissance → finition, concentrés et prémix pour fabriquer votre aliment (FAF), appui technicien et devis en FCFA sous 24 h.",
        "eyebrow": "Filière volailles — Poulets de chair",
        "h1": 'Poulets de chair : le bon aliment à <span class="accent">chaque phase</span>',
        "lead": "Du démarrage à la finition, un programme nutritionnel complet pensé pour le climat ivoirien — <strong>prêt à l'emploi</strong> ou en <strong>fabrication assistée (FAF)</strong>, avec l'appui de nos techniciens sur le terrain.",
        "image": "maridav_ci_image/aliments_complets/aliments_complets.jpg",
        "image_alt": "Gamme aliments poulets de chair MARIDAV Côte d'Ivoire",
        "facts": [
            {"b": "3 phases", "span": "Démarrage → finition"},
            {"b": "Prêt ou FAF", "span": "Deux modes de production"},
            {"b": "24 h", "span": "Devis en FCFA"},
            {"b": "Côte d'Ivoire", "span": "Réseau de points de vente"},
        ],
        "timeline_kicker": "Le cycle du poulet de chair",
        "timeline_h2": "Quel aliment, à quel âge",
        "timeline_intro": "Repère naturel de l'éleveur : à chaque phase du cycle, l'aliment qui sécurise la performance suivante.",
        "timeline": [
            {"phase": "Démarrage", "age": "0 – 14 jours", "text": "Starter haute appétence : démarrage rapide du poussin et poids moyen sécurisé.", "url": "aliment_chair_demarrage_maridav_ci.html", "cta": "Aliment Démarrage"},
            {"phase": "Croissance", "age": "15 – 28 jours", "text": "Optimisation du FCR et homogénéité de la bande.", "url": "aliments_chair_croissance_maridav_ci.html", "cta": "Aliment Croissance"},
            {"phase": "Finition", "age": "29 – 42 jours", "text": "Rendement carcasse et maîtrise du coût des derniers kilos.", "url": "aliments_chair_finition_maridav_ci.html", "cta": "Aliment Finition"},
        ],
        "additives": [
            {"name": "Biotronic Top liquide", "text": "Acidifiant — qualité de l'eau et confort digestif.", "url": "biotronic_top_liquide_maridav_ci.html"},
            {"name": "Digestarom", "text": "Additif phytogénique — appétence et digestion.", "url": "digestarom_maridav_ci.html"},
            {"name": "Nutricool", "text": "Soutien anti-stress thermique en climat chaud.", "url": "nutricool_maridav_ci.html"},
        ],
        "cross_url": "pondeuses_maridav_ci.html",
        "cross_label": "Vous élevez des pondeuses ?",
        "cross_text": "Découvrez le programme poussinière → poulette → ponte.",
        "cross_link": "Filière pondeuses",
    },
    "volailles-ponte": {
        "url": "pondeuses_maridav_ci.html",
        "title": "Pondeuses & poulettes — programme complet & FAF | MARIDAV Côte d'Ivoire",
        "description": "Nutrition pondeuses en Côte d'Ivoire : programme pré-démarrage → poulette → ponte, concentrés et prémix pour fabriquer votre aliment (FAF), appui technicien et devis en FCFA sous 24 h.",
        "eyebrow": "Filière volailles — Pondeuses",
        "h1": 'Pondeuses : sécuriser le pic et la <span class="accent">persistance de ponte</span>',
        "lead": "De la poussinière à la fin de ponte, un programme nutritionnel complet adapté au climat ivoirien — <strong>prêt à l'emploi</strong> ou en <strong>fabrication assistée (FAF)</strong>, avec l'appui de nos techniciens sur le terrain.",
        "image": "maridav_ci_image/aliments_complets/aliments_complets.jpg",
        "image_alt": "Gamme aliments pondeuses MARIDAV Côte d'Ivoire",
        "facts": [
            {"b": "5 phases", "span": "Pré-démarrage → ponte"},
            {"b": "Prêt ou FAF", "span": "Deux modes de production"},
            {"b": "24 h", "span": "Devis en FCFA"},
            {"b": "Côte d'Ivoire", "span": "Réseau de points de vente"},
        ],
        "timeline_kicker": "Le cycle de la pondeuse",
        "timeline_h2": "Quel aliment, à quel âge",
        "timeline_intro": "Repère naturel de l'éleveur : à chaque phase du cycle, l'aliment qui prépare le pic et la persistance de ponte.",
        "timeline": [
            {"phase": "Pré-démarrage", "age": "0 – 5 jours", "text": "ChickCare : sécuriser les tout premiers jours du poussin.", "url": "chickcare.html", "cta": "ChickCare"},
            {"phase": "Démarrage", "age": "0 – 6 semaines", "text": "Construire le bon démarrage de la future pondeuse.", "url": "aliment_demarrage_ponte.html", "cta": "Aliment Démarrage"},
            {"phase": "Poulette", "age": "7 – 18 semaines", "text": "Développer un squelette et un poids cible homogènes.", "url": "aliment_poulette.html", "cta": "Aliment Poulette"},
            {"phase": "Ponte 1", "age": "Entrée → pic", "text": "Accompagner l'entrée en ponte jusqu'au pic.", "url": "aliment_ponte_1_maridav_ci.html", "cta": "Aliment Ponte 1"},
            {"phase": "Ponte 2", "age": "Persistance", "text": "Soutenir la persistance et la qualité de coquille.", "url": "aliment_ponte_2_maridav_ci.html", "cta": "Aliment Ponte 2"},
        ],
        "additives": [
            {"name": "Biotronic Top liquide", "text": "Acidifiant — qualité de l'eau et confort digestif.", "url": "biotronic_top_liquide_maridav_ci.html"},
            {"name": "Digestarom", "text": "Additif phytogénique — appétence et digestion.", "url": "digestarom_maridav_ci.html"},
            {"name": "Nutricool", "text": "Soutien anti-stress thermique en climat chaud.", "url": "nutricool_maridav_ci.html"},
            {"name": "Profish", "text": "Complément protéique d'origine marine.", "url": "profish_maridav_ci.html"},
        ],
        "cross_url": "poulets_chair_maridav_ci.html",
        "cross_label": "Vous élevez des poulets de chair ?",
        "cross_text": "Découvrez le programme démarrage → croissance → finition.",
        "cross_link": "Filière chair",
    },
}

# Points de preuve filière — claims VÉRIFIABLES uniquement (structure de l'offre,
# disponibilité, accompagnement). Les résultats chiffrés (FCR, poids, ponte) restent
# en attente de données Maridav : surtout NE PAS inventer ici.
PROOF_POINTS = [
    {"b": "Tout le cycle", "span": "Un aliment pour chaque phase"},
    {"b": "Prêt ou FAF", "span": "Acheter prêt à l'emploi ou fabriquer"},
    {"b": "Devis 24 h", "span": "Réponse chiffrée en FCFA"},
    {"b": "Appui terrain", "span": "Techniciens MARIDAV en Côte d'Ivoire"},
]

# --------------------------------------------------------------------------- #
#  Configuration du HUB volailles (volailles.html) — aiguillage + pourquoi      #
#  + comment ça marche. Pas de témoignage inventé (slot vide tant que Maridav   #
#  n'a pas fourni de référence réelle).                                          #
# --------------------------------------------------------------------------- #
HUB = {
    "url": "volailles.html",
    "title": "Volailles — aliments & programmes | MARIDAV Côte d'Ivoire",
    "description": "Nutrition volailles en Côte d'Ivoire : programmes complets poulets de chair et pondeuses, aliments prêts à l'emploi ou fabrication assistée (FAF), additifs, appui technicien et devis en FCFA sous 24 h.",
    "eyebrow": "Solutions volailles",
    "h1": 'Nutrition volailles : <span class="accent">chair & pondeuses</span>, du poussin à la performance',
    "lead": "Un programme nutritionnel complet pour chaque filière, adapté au climat ivoirien — <strong>prêt à l'emploi</strong> ou en <strong>fabrication assistée (FAF)</strong>, avec l'appui de nos techniciens sur le terrain.",
    "image": "maridav_ci_image/especes_maridav_ci/poulets_de_chair_maridav_ci.webp",
    "image_alt": "Élevage de volailles accompagné par MARIDAV Côte d'Ivoire",
    "facts": [
        {"b": "2 filières", "span": "Chair & pondeuses"},
        {"b": "Prêt ou FAF", "span": "Deux modes de production"},
        {"b": "24 h", "span": "Devis en FCFA"},
        {"b": "Côte d'Ivoire", "span": "Réseau de points de vente"},
    ],
    "choices": [
        {
            "title": "Poulets de chair",
            "sub": "Croissance homogène, FCR maîtrisé, carcasses conformes.",
            "image": "maridav_ci_image/especes_maridav_ci/poulets_de_chair_maridav_ci.webp",
            "bullets": [
                "Programme démarrage → croissance → finition",
                "Concentrés & prémix pour fabriquer votre aliment",
                "Additifs performance & biosécurité",
            ],
            "url": "poulets_chair_maridav_ci.html",
        },
        {
            "title": "Pondeuses",
            "sub": "Entrée en ponte sécurisée, pic et persistance soutenus.",
            "image": "maridav_ci_image/especes_maridav_ci/pondeuses_maridav_ci.webp",
            "bullets": [
                "Programme poussinière → poulette → ponte",
                "Concentrés & prémix pour fabriquer votre aliment",
                "Additifs performance & biosécurité",
            ],
            "url": "pondeuses_maridav_ci.html",
        },
    ],
    "steps": [
        {"title": "Dites-nous votre élevage", "text": "Filière, effectif, âge des bandes et mode de production (prêt à l'emploi ou FAF)."},
        {"title": "On cadre le programme", "text": "Nos techniciens proposent l'aliment ou la formulation adaptée à chaque phase, et un devis en FCFA."},
        {"title": "Devis sous 24 h + appui terrain", "text": "Réponse chiffrée sous 24 h, retrait au point de vente le plus proche et suivi de vos performances."},
    ],
}

# --------------------------------------------------------------------------- #
#  Hub PORCS (porcins_maridav_ci.html) — 2 pistes engraissement / reproduction  #
#  Matrice dérivée de products-porcs.json (impossible de mal catégoriser).       #
# --------------------------------------------------------------------------- #
PORC_HUB = {
    "url": "porcins_maridav_ci.html",
    "title": "Porcs — aliments & concentrés | MARIDAV Côte d'Ivoire",
    "description": "Nutrition porcine en Côte d'Ivoire : aliments complets et concentrés 5 % pour l'engraissement (7–70 kg et finition) et la reproduction (gestation, lactation, Milkiwean). Appui technicien, devis en FCFA sous 24 h.",
    "eyebrow": "Filière porcs",
    "h1": 'Nutrition porcine : <span class="accent">engraissement & reproduction</span>',
    "lead": "Des formulations tropicalisées pour chaque phase du cycle — <strong>prêts à l'emploi</strong> ou en <strong>fabrication assistée (FAF)</strong> avec vos matières locales — accompagnées par nos techniciens sur le terrain.",
    "image": "maridav_ci_image/aliments_complets/aliments_complets.jpg",
    "image_alt": "Gamme aliments porcs MARIDAV Côte d'Ivoire",
    "facts": [
        {"b": "2 pistes", "span": "Engraissement & Reproduction"},
        {"b": "Prêt ou FAF", "span": "Deux modes de production"},
        {"b": "24 h", "span": "Devis en FCFA"},
        {"b": "Côte d'Ivoire", "span": "Réseau de points de vente"},
    ],
    "timeline": {
        "kicker": "Le cycle porcin",
        "h2": "Quel aliment, à quelle étape",
        "intro": "Deux pistes distinctes : engraissement (du porcelet à l'abattage, repère = le poids) et reproduction (cheptel truies). Choisissez votre piste.",
        "eng": [
            {"phase": "Pré-démarrage", "age": "Post-sevrage", "text": "Milkiwean Eco : aliment lacté pour sécuriser le porcelet dès les premières heures.", "url": "milkeawean.html", "cta": "Milkiwean Eco"},
            {"phase": "Démarrage", "age": "7 – 25 kg", "text": "Aliment complet ou concentré 5 % pour démarrer le lot sur de bonnes bases.", "url": "aliment_porc_demarrage_maridav_ci.html", "cta": "Aliment Démarrage"},
            {"phase": "Croissance", "age": "25 – 70 kg", "text": "Ration tropicalisée pour soutenir le gain de poids et maîtriser l'indice de consommation.", "url": "aliment_porc_croissance_maridav_ci.html", "cta": "Aliment Croissance"},
            {"phase": "Finition", "age": "> 70 kg", "text": "Équilibre énergie/protéines pour préparer les carcasses à l'objectif de vente.", "url": "aliment_porc_finition_maridav_ci.html", "cta": "Aliment Finition"},
        ],
        "rep": [
            {"phase": "Gestation", "age": "Saillie → mise bas", "text": "Fibres et minéraux biodisponibles pour préserver la condition corporelle et soutenir la prolificité.", "url": "aliment_truie_gestante.html", "cta": "Truie Gestante"},
            {"phase": "Lactation", "age": "Mise bas → sevrage", "text": "Haute énergie et acides aminés digestibles pour soutenir la production laitière et préparer le retour en saillie.", "url": "aliment_truie_allaitante_maridav_ci.html", "cta": "Truie Allaitante"},
            {"phase": "Sevrage", "age": "Transition", "text": "Milkiwean Eco pour sécuriser le porcelet au sevrage avant le passage à l'aliment démarrage solide.", "url": "milkeawean.html", "cta": "Milkiwean Eco"},
        ],
    },
    "steps": [
        {"title": "Dites-nous votre élevage", "text": "Piste (engraissement, reproduction ou les deux), effectif, phase actuelle et mode de production (prêt à l'emploi ou FAF)."},
        {"title": "On cadre le programme", "text": "Nos techniciens proposent l'aliment ou la formulation adaptée à chaque phase — avec un devis en FCFA sous 24 h."},
        {"title": "Livraison + appui terrain", "text": "Retrait au point de vente le plus proche, suivi des performances et ajustements si nécessaire."},
    ],
}

# --------------------------------------------------------------------------- #
#  Hub POISSONS (pisciculture_maridav_ci.html) — cycle linéaire tilapia          #
#  Matrice dérivée de products-poissons.json.                                   #
# --------------------------------------------------------------------------- #
POISSON_HUB = {
    "url": "pisciculture_maridav_ci.html",
    "title": "Poissons — aliments tilapia | MARIDAV Côte d'Ivoire",
    "description": "Alimentation piscicole tilapia en Côte d'Ivoire : gamme complète Nutra (alevinage/prégrossissement) et Optiline (grossissement/finition), plus AquaCare (qualité d'eau) et Profish (FAF). Appui technicien, devis en FCFA sous 24 h.",
    "eyebrow": "Filière pisciculture",
    "h1": 'Pisciculture tilapia : <span class="accent">de l\'alevin à l\'abattage</span>',
    "lead": "Une gamme complète de granulés flottants pour chaque stade du cycle tilapia — <strong>alevinage, prégrossissement, grossissement et finition</strong> — accompagnée par nos techniciens et disponible en Côte d'Ivoire.",
    "image": "maridav_ci_image/aliments_poissons/nutra_poissons_maridav_ci.jpg",
    "image_alt": "Gamme aliments pisciculture tilapia MARIDAV Côte d'Ivoire",
    "facts": [
        {"b": "7 aliments", "span": "De l'alevin à la finition"},
        {"b": "Flottants", "span": "Gamme granulés extrudés"},
        {"b": "24 h", "span": "Devis en FCFA"},
        {"b": "Côte d'Ivoire", "span": "Réseau de points de vente"},
    ],
    "timeline": {
        "kicker": "Le cycle tilapia",
        "h2": "Quel aliment, à quelle étape",
        "intro": "Un cycle linéaire guidé par le poids du poisson : de l'écloserie à l'abattage, chaque stade a son aliment. Repère = poids en grammes.",
        "steps": [
            {"phase": "Alevinage", "age": "0–5 g", "text": "Nutra 0 : granulé micro-extrudé haute digestibilité pour démarrer les alevins dès les premières heures.", "url": "nutra_tilapia_0_maridav_ci.html", "cta": "Nutra® 0"},
            {"phase": "Alevinage", "age": "5–20 g", "text": "Nutra 80 : profil amino équilibré pour croissance homogène et faible encrassement des bassins.", "url": "nutra_tilapia_80_maridav_ci.html", "cta": "Nutra® 80"},
            {"phase": "Prégrossissement", "age": "20–80 g", "text": "Nutra 120 : qualité constante lot à lot pour conduire la phase de prégrossissement vers 80 g.", "url": "nutra_tilapia_120_maridav_ci.html", "cta": "Nutra® 120"},
            {"phase": "Prégrossissement", "age": "80–120 g", "text": "Nutra 160 : dernière étape Nutra, profil proche d'Optiline pour une bascule sans stress.", "url": "nutra_tilapia_160_maridav_ci.html", "cta": "Nutra® 160"},
            {"phase": "Grossissement", "age": "120–200 g", "text": "Optiline 2 : granulé 2,5–3 mm pour démarrer le grossissement avec vitamines et antioxydants renforcés.", "url": "maridav_optiline_2_maridav_ci.html", "cta": "Optiline® 2"},
            {"phase": "Grossissement", "age": "200–400 g", "text": "Optiline 3 : granulé 3–4 mm pour la phase centrale du grossissement.", "url": "maridav_optiline_3_maridav_ci.html", "cta": "Optiline® 3"},
            {"phase": "Finition", "age": "> 400 g", "text": "Optiline 4.5 : granulé 4–5 mm pour préparer les lots à l'abattage et au marché.", "url": "maridav_optiline_4_5.html", "cta": "Optiline® 4.5"},
        ],
    },
    "steps": [
        {"title": "Partagez votre situation", "text": "Stade actuel (poids des poissons), effectif, type de système (étang, cage, RAS) et mode de production visé."},
        {"title": "On bâtit le programme", "text": "Nos techniciens vous proposent le bon aliment pour chaque stade — avec un devis en FCFA sous 24 h."},
        {"title": "Livraison + appui terrain", "text": "Retrait au point de vente le plus proche, suivi qualité d'eau et ajustements si nécessaire tout au long du cycle."},
    ],
}

# --------------------------------------------------------------------------- #
#  SEO — sitemap.xml / robots.txt / llms.txt générés depuis l'état du site.     #
#  Date de build (= lastmod). À bumper au déploiement.                          #
# --------------------------------------------------------------------------- #
BUILD_DATE = "2026-06-08"

# Pages non indexables détectables par leur contenu : captures d'erreur HTTrack
# (« 400 Bad Request » / « 404 Not Found ») et gabarits (« {{TITLE}} »).
SITEMAP_SKIP_TITLE = ("404 Not Found", "400 Bad Request", "Bad Request", "Not Found", "{{")

# Priorité / fréquence par page (sitemap). Tout le reste = produit/additif (0.6 monthly).
SITEMAP_RULES = {
    "index.html": ("1.0", "daily"),
    "volailles.html": ("0.9", "weekly"),
    "poulets_chair_maridav_ci.html": ("0.9", "weekly"),
    "pondeuses_maridav_ci.html": ("0.9", "weekly"),
    "porcins_maridav_ci.html": ("0.9", "weekly"),
    "pisciculture_maridav_ci.html": ("0.9", "weekly"),
    "biosecurite_maridav_ci.html": ("0.8", "weekly"),
    "a-propos.html": ("0.8", "weekly"),
    "contact.html": ("0.8", "weekly"),
    "distributeurs_maridav.html": ("0.8", "weekly"),
    "partenaires-maridav.html": ("0.7", "monthly"),
    "carriere-maridav.html": ("0.6", "monthly"),
    "blog_maridav_ci.html": ("0.8", "weekly"),
    "blog_maridav_ci_page2.html": ("0.5", "monthly"),
}

# robots.txt — contenu statique (indexation ouverte moteurs + assistants IA).
ROBOTS_TXT = """# robots.txt — MARIDAV Côte d'Ivoire
# Indexation ouverte aux moteurs de recherche et aux assistants IA.

User-agent: *
Allow: /

# Assistants IA / moteurs de réponse (citation et découverte)
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-Web
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: Bingbot
Allow: /

Sitemap: {base}/sitemap.xml
""".format(base=SITE["base"])

# llms.txt — digest structuré pour les assistants IA. Sections curées (porcs/poissons/
# blog stables) ; les pages volailles pointent vers le hub généré. FR, sans recon (§5.6).
LLMS = {
    "title": "MARIDAV Côte d'Ivoire",
    "summary": "Nutrition et santé animales en Côte d'Ivoire : aliments complets, additifs, biosécurité et appui technique terrain pour éleveurs de volailles, de porcs et de poissons. Devis en FCFA sous 24 h, distribution nationale, accompagnement par des techniciens.",
    "sections": [
        ("Solutions", [
            ("Volailles", "volailles.html", "programme chair & pondeuses, prêt à l'emploi ou fabrication assistée (FAF)"),
            ("Poulets de chair", "poulets_chair_maridav_ci.html", "démarrage → croissance → finition"),
            ("Pondeuses", "pondeuses_maridav_ci.html", "poussinière → poulette → ponte"),
            ("Porcs", "porcins_maridav_ci.html", "aliments porcelets, croissance, finition, truies"),
            ("Poissons", "pisciculture_maridav_ci.html", "aliments tilapia, pisciculture"),
            ("Biosécurité", "biosecurite_maridav_ci.html", "hygiène, désinfection, prévention sanitaire"),
        ]),
        ("Pages clés", [
            ("Accueil", "", ""),
            ("À propos", "a-propos.html", ""),
            ("Points de vente / distributeurs", "distributeurs_maridav.html", ""),
            ("Partenaires", "partenaires-maridav.html", ""),
            ("Carrière", "carriere-maridav.html", ""),
        ]),
        ("Blog & ressources techniques", [
            ("Blog", "blog_maridav_ci.html", ""),
            ("Démarrage des poussins", "article-demarrage-poussins.html", ""),
            ("Biosécurité poulet de chair", "article-biosecurite-poulet-chair.html", ""),
            ("Ponte en saison chaude", "article-ponte-chaleur-maridav.html", ""),
            ("Porcs : FCR et chaleur", "article-porcs-fcr-chaleur.html", ""),
            ("Tilapia : eau et ration", "article-tilapia-eau-ration.html", ""),
        ]),
    ],
    "contact": [
        "Adresse : Zone 4C Biétry, 34 Rue Alex Flemming, Abidjan, Côte d'Ivoire",
        "Téléphone : +225 27 21 35 32 42",
        "WhatsApp : +225 05 74 64 88 88",
        "[Page contact / devis](%s/contact.html)" % SITE["base"],
    ],
}

# --------------------------------------------------------------------------- #
#  CSS des composants de persuasion FILIÈRE (.fl-*) — s'ajoute à HEAD_CSS.      #
#  Sécurité GPU mobile ≤991px : pas de backdrop-filter, pas de :has(),          #
#  filtrage par classes JS (.is-hidden/.is-active), ombres/animations allégées. #
# --------------------------------------------------------------------------- #
FILIERE_CSS = r"""  <style>
    /* ---- pillars-strip (4 piliers) ---- */
    .fl-pillars{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
    .fl-pillar{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:1.3rem;box-shadow:var(--shadow)}
    .fl-pillar .ic{width:46px;height:46px;border-radius:13px;display:inline-flex;align-items:center;justify-content:center;background:linear-gradient(135deg,rgba(27,142,62,.14),rgba(42,161,84,.14));color:var(--green);font-size:1.25rem;margin-bottom:.7rem}
    .fl-pillar h3{font-family:"Fraunces",serif;font-weight:600;font-size:1.05rem;color:var(--navy);margin:0 0 .35rem}
    .fl-pillar p{margin:0;color:var(--muted);font-size:.9rem;line-height:1.5}

    /* ---- cycle-timeline (frise du cycle) ---- */
    .fl-timeline{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:1rem;position:relative}
    .fl-tstep{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:1.2rem;box-shadow:var(--shadow);position:relative;display:flex;flex-direction:column}
    .fl-tstep .num{width:38px;height:38px;border-radius:50%;background:var(--navy);color:#fff;font-family:"Fraunces",serif;font-weight:600;display:inline-flex;align-items:center;justify-content:center;margin-bottom:.7rem}
    .fl-tstep .age{font-size:.72rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--green)}
    .fl-tstep h3{font-family:"Fraunces",serif;font-weight:600;font-size:1.1rem;color:var(--navy);margin:.15rem 0 .4rem}
    .fl-tstep p{margin:0 0 .9rem;color:var(--muted);font-size:.88rem;line-height:1.5}
    .fl-tstep .btn-line{margin-top:auto;align-self:flex-start}
    .fl-tstep:not(:last-child)::after{content:"\F285";font-family:"bootstrap-icons";position:absolute;right:-.85rem;top:50%;transform:translateY(-50%);color:var(--green);font-size:1.1rem;z-index:1}

    /* ---- mode-switch (prêt à l'emploi / FAF) ---- */
    .fl-modes{display:inline-flex;flex-wrap:wrap;gap:.4rem;background:#fff;border:1px solid var(--line);border-radius:999px;padding:.35rem;box-shadow:var(--shadow)}
    .fl-mode{border:0;background:transparent;border-radius:999px;font-weight:700;font-size:.9rem;color:var(--muted);padding:.55rem 1.1rem;cursor:pointer;transition:background .2s,color .2s;display:inline-flex;align-items:center;gap:.45rem}
    .fl-mode:hover{color:var(--navy)}
    .fl-mode.is-active{background:linear-gradient(135deg,var(--green),var(--green-2));color:#fff;box-shadow:0 10px 22px -10px rgba(27,142,62,.7)}
    .fl-modehint{color:var(--muted);font-size:.92rem;margin:.9rem 0 0;min-height:1.2em}

    /* ---- product-matrix ---- */
    .fl-matrix{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
    .fl-mcard{background:#fff;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:1.2rem;display:flex;flex-direction:column;transition:transform .25s,box-shadow .25s}
    .fl-mcard:hover{transform:translateY(-5px);box-shadow:0 30px 56px -30px rgba(2,12,46,.45)}
    .fl-mcard.is-hidden{display:none}
    .fl-mcard .cat{display:inline-flex;align-items:center;gap:.4rem;font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--green);background:rgba(27,142,62,.1);border-radius:999px;padding:.28rem .65rem;align-self:flex-start;margin-bottom:.6rem}
    .fl-mcard h3{font-family:"Fraunces",serif;font-weight:600;font-size:1.08rem;color:var(--navy);margin:0 0 .25rem}
    .fl-mcard .badge-phase{font-size:.78rem;color:var(--muted);margin:0 0 .5rem}
    .fl-mcard p{margin:0 0 .9rem;color:var(--muted);font-size:.88rem;line-height:1.5}
    .fl-mcard .tags{display:flex;flex-wrap:wrap;gap:.35rem;margin-bottom:.8rem}
    .fl-mcard .tg{font-size:.72rem;font-weight:700;color:var(--navy);background:rgba(0,0,102,.06);border-radius:999px;padding:.2rem .6rem}
    .fl-mcard .btn-line{margin-top:auto;align-self:flex-start}
    .fl-empty{display:none;color:var(--muted);text-align:center;padding:2rem 0}

    /* ---- proof-bar ---- */
    .fl-proof{background:linear-gradient(165deg,#04204a,var(--navy-deep));border-radius:var(--radius);padding:1.6rem;color:#fff;box-shadow:var(--shadow);position:relative;overflow:hidden}
    .fl-proof::before{content:"";position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--gold),var(--green))}
    .fl-proofgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
    .fl-pitem b{display:block;font-family:"Fraunces",serif;font-size:1.15rem;color:#fff;line-height:1.1}
    .fl-pitem span{display:block;font-size:.8rem;color:rgba(255,255,255,.66);margin-top:.2rem}
    .fl-proofnote{margin:1rem 0 0;font-size:.84rem;color:rgba(255,255,255,.62)}

    /* ---- technician-cta ---- */
    .fl-tech{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1.2rem;background:linear-gradient(120deg,#04204a,var(--navy));color:#fff;border-radius:var(--radius);padding:1.5rem 1.7rem;box-shadow:var(--shadow)}
    .fl-tech .tx h3{font-family:"Fraunces",serif;font-weight:600;font-size:1.25rem;color:#fff;margin:0 0 .25rem}
    .fl-tech .tx p{margin:0;color:rgba(255,255,255,.74);font-size:.93rem}
    .fl-tech .ax{display:flex;flex-wrap:wrap;gap:.7rem}

    /* ---- hub: aiguillage filières ---- */
    .hub-choices{display:grid;grid-template-columns:repeat(2,1fr);gap:1.4rem}
    .hub-choice{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);transition:transform .3s,box-shadow .3s}
    .hub-choice:hover{transform:translateY(-6px);box-shadow:0 36px 64px -30px rgba(2,12,46,.5)}
    .hub-choice .vis{height:210px;background-size:cover;background-position:center}
    .hub-choice .bd{padding:1.5rem;display:flex;flex-direction:column;flex:1}
    .hub-choice h3{font-family:"Fraunces",serif;font-weight:600;font-size:1.4rem;color:var(--navy);margin:0 0 .35rem}
    .hub-choice .sub{color:var(--muted);font-size:.92rem;margin:0 0 .9rem}
    .hub-choice ul{list-style:none;padding:0;margin:0 0 1.1rem}
    .hub-choice li{display:flex;gap:.55rem;align-items:flex-start;color:var(--ink);font-size:.9rem;margin-bottom:.5rem}
    .hub-choice li i{color:var(--green);margin-top:.15rem}
    .hub-choice .ax{margin-top:auto;display:flex;flex-wrap:wrap;gap:.6rem}

    /* ---- hub: comment ça marche (3 étapes) ---- */
    .hub-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem}
    .hub-step{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:1.5rem;box-shadow:var(--shadow);position:relative}
    .hub-step .num{width:44px;height:44px;border-radius:50%;background:var(--navy);color:#fff;font-family:"Fraunces",serif;font-weight:600;display:inline-flex;align-items:center;justify-content:center;font-size:1.15rem;margin-bottom:.8rem}
    .hub-step h3{font-family:"Fraunces",serif;font-weight:600;font-size:1.1rem;color:var(--navy);margin:0 0 .35rem}
    .hub-step p{margin:0;color:var(--muted);font-size:.92rem;line-height:1.55}

    /* ---- cycle-timeline 2 pistes (porcs hub) ---- */
    .fl-track-switch{display:inline-flex;flex-wrap:wrap;gap:.4rem;background:#fff;border:1px solid var(--line);border-radius:999px;padding:.35rem;box-shadow:var(--shadow);margin-bottom:1.2rem}
    .fl-tswitch{border:0;background:transparent;border-radius:999px;font-weight:700;font-size:.9rem;color:var(--muted);padding:.55rem 1.1rem;cursor:pointer;transition:background .2s,color .2s;display:inline-flex;align-items:center;gap:.45rem}
    .fl-tswitch:hover{color:var(--navy)}
    .fl-tswitch.is-active{background:linear-gradient(135deg,var(--green),var(--green-2));color:#fff;box-shadow:0 10px 22px -10px rgba(27,142,62,.7)}
    .fl-track{display:none}
    .fl-track.is-active{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:1rem;position:relative}

    @media (max-width:991px){
      .hub-choices,.hub-steps{grid-template-columns:1fr}
      .hub-choice:hover{transform:none}
      .fl-pillars{grid-template-columns:repeat(2,1fr)}
      .fl-timeline{grid-auto-flow:row;grid-auto-columns:auto}
      .fl-tstep:not(:last-child)::after{content:"\F282";right:auto;left:1.2rem;top:auto;bottom:-.95rem;transform:none}
      .fl-matrix{grid-template-columns:repeat(2,1fr)}
      .fl-proofgrid{grid-template-columns:repeat(2,1fr)}
      .fl-mcard:hover,.fl-pillar:hover{transform:none}
      .fl-track.is-active{grid-auto-flow:row;grid-auto-columns:auto}
    }
    @media (max-width:575px){
      .fl-pillars,.fl-matrix,.fl-proofgrid{grid-template-columns:1fr}
    }
  </style>"""

# JS vanilla léger : mode-switch + filtrage de la matrice par classes (pas de :has()).
FILIERE_JS = r"""  <script>
  (function(){
    var matrix=document.getElementById('fl-matrix');
    if(!matrix)return;
    var modes=document.querySelectorAll('.fl-mode');
    var cards=matrix.querySelectorAll('.fl-mcard');
    var empty=document.getElementById('fl-empty');
    var hints={pret:"Aliments complets, prêts à distribuer.",faf:"Concentrés et prémix pour fabriquer votre aliment et maîtriser votre coût de ration.",all:"Toute la gamme volailles, prête à l'emploi comme en fabrication assistée."};
    var hintEl=document.getElementById('fl-modehint');
    function apply(mode){
      var shown=0;
      cards.forEach(function(c){
        var ok=(mode==='all')||(c.getAttribute('data-mode')===mode);
        c.classList.toggle('is-hidden',!ok);
        if(ok)shown++;
      });
      if(empty)empty.style.display=shown?'none':'block';
      if(hintEl)hintEl.textContent=hints[mode]||'';
    }
    modes.forEach(function(b){
      b.addEventListener('click',function(){
        modes.forEach(function(x){x.classList.remove('is-active');});
        b.classList.add('is-active');
        apply(b.getAttribute('data-filter'));
      });
    });
  })();
  (function(){
    var tswitches=document.querySelectorAll('.fl-tswitch');
    if(!tswitches.length)return;
    tswitches.forEach(function(btn){
      btn.addEventListener('click',function(){
        var track=btn.getAttribute('data-track');
        tswitches.forEach(function(b){b.classList.remove('is-active')});
        btn.classList.add('is-active');
        document.querySelectorAll('.fl-track').forEach(function(t){t.classList.remove('is-active')});
        var el=document.getElementById('fl-track-'+track);
        if(el)el.classList.add('is-active');
      });
    });
  })();
  </script>"""


# --------------------------------------------------------------------------- #
#  Renderers de sections                                                       #
# --------------------------------------------------------------------------- #
def render_head(p):
    """<head> complet : métadonnées dérivées de la donnée + CSS figé."""
    url = f'{SITE["base"]}/{p["url"]}'
    og_img = p.get("og_image") or f'{SITE["base"]}/{p["image"]}'
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta name="theme-color" content="#000066">
  <title>{p["title"]}</title>
  <meta name="description" content="{p["description"]}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{p.get("og_title", p["title"])}">
  <meta property="og:description" content="{p.get("og_description", p["description"])}">
  <meta property="og:image" content="{og_img}">
  <link rel="icon" type="image/png" sizes="56x56" href="favicon_io/favicon-32x32.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.15.3/css/all.css">
  <link rel="stylesheet" type="text/css" href="css/style.css">
  <link rel="stylesheet" type="text/css" href="css/responsive.css">
  <link rel="stylesheet" href="assets/css/main.min.css">
{HEAD_CSS}
</head>"""


def render_breadcrumb(p):
    """Fil d'Ariane HTML : liste de {name, url?} ; le dernier sans lien."""
    parts = []
    for item in p["breadcrumb"]:
        if item.get("url"):
            parts.append(f'<a href="{item["url"]}">{item["name"]}</a>')
        else:
            parts.append(f'<span class="text-white-50">{item["name"]}</span>')
    sep = ' <span class="mx-1 text-white-50">/</span>\n          '
    return sep.join(parts)


def render_facts(facts):
    out = []
    for f in facts:
        out.append(f'<div class="pdp-fact"><b>{f["b"]}</b><span>{f["span"]}</span></div>')
    return "\n              ".join(out)


def render_hero(p):
    h = p["hero"]
    pill = h["pill"]
    return f"""    <!-- HERO -->
    <section class="pdp-hero">
      <div class="container">
        <nav class="pdp-crumb small mb-3 pdp-reveal" aria-label="Fil d'Ariane">
          {render_breadcrumb(p)}
        </nav>
        <div class="row g-5 align-items-center">
          <div class="col-lg-7">
            <span class="pdp-eyebrow pdp-reveal d1">{h["eyebrow"]}</span>
            <h1 class="pdp-reveal d1">{h["h1"]}</h1>
            <div class="pdp-trans pdp-reveal d2"><i class="bi {pill["icon"]}"></i> {pill["text"]}</div>
            <p class="pdp-lead pdp-reveal d2">{h["lead"]}</p>
            <div class="d-flex flex-wrap gap-3 mt-4 pdp-reveal d3">
              <a class="btn-pill btn-green" href="contact.html">Demander un devis <i class="bi bi-arrow-right"></i></a>
              <a class="btn-pill btn-ghost" href="{SITE["wa"]}" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i> Parler à un technicien</a>
            </div>
            <div class="pdp-facts pdp-reveal d4">
              {render_facts(h["facts"])}
            </div>
          </div>
          <div class="col-lg-5">
            <figure class="pdp-figure pdp-reveal d2 mb-0">
              <img src="{p["image"]}" alt="{h["image_alt"]}">
              <figcaption class="pdp-figchip"><small>{h["figchip"]["small"]}</small>{h["figchip"]["label"]}</figcaption>
            </figure>
          </div>
        </div>
      </div>
    </section>"""


def render_benefits(p):
    b = p["benefits"]
    cards = []
    for c in b["cards"]:
        cards.append(
            f'<div class="col-md-6"><div class="pdp-card h-100 pdp-benefit">'
            f'<div class="pdp-bicon"><i class="bi {c["icon"]}"></i></div>'
            f'<div><h5>{c["title"]}</h5><p>{c["text"]}</p></div></div></div>'
        )
    cards_html = "\n              ".join(cards)
    return f"""    <!-- BÉNÉFICES -->
    <section class="pdp-sec" id="benefices">
      <div class="container">
        <div class="row g-5">
          <div class="col-lg-4">
            <span class="pdp-kicker">{b.get("kicker", "L’essentiel")}</span>
            <h2 class="pdp-h2">{b["h2"]}</h2>
            <p class="text-muted mt-3 mb-0">{b["intro"]}</p>
          </div>
          <div class="col-lg-8">
            <div class="row g-4">
              {cards_html}
            </div>
          </div>
        </div>
      </div>
    </section>"""


def render_transbadge(p):
    """Sticker transversalité — uniquement si multi-filières."""
    if not p.get("transversal"):
        return ""
    chips = []
    for f in p["filieres"]:
        icon, label = FILIERE_LABELS.get(f, ("bi-check", f))
        chips.append(f'<span class="tb-chip"><i class="bi {icon}"></i> {label}</span>')
    chips_html = "\n            ".join(chips)
    return f"""    <!-- STICKER TRANSVERSALITÉ (réutilisable: produits multi-filières) -->
    <section class="pdp-sec pt-0" id="transversal">
      <div class="container">
        <div class="pdp-transbadge">
          <div class="tb-head">
            <span class="tb-ic"><i class="bi bi-arrow-left-right"></i></span>
            <div>
              <span class="tb-label">Produit transversal</span>
              <span class="tb-sub">Une même base, utilisable sur plusieurs filières</span>
            </div>
          </div>
          <div class="tb-filieres">
            {chips_html}
          </div>
        </div>
      </div>
    </section>"""


def render_usage_spec(p):
    u = p["usage"]
    s = p["spec"]
    steps = []
    for i, st in enumerate(u["steps"], 1):
        steps.append(
            f'<div class="pdp-step"><span class="num">{i}</span>'
            f'<div><h5>{st["title"]}</h5><p>{st["text"]}</p></div></div>'
        )
    steps_html = "\n            ".join(steps)
    rows = []
    for r in s["rows"]:
        rows.append(f'<tr><td>{r["k"]}</td><td>{r["v"]}</td></tr>')
    rows_html = "\n                ".join(rows)
    return f"""    <!-- USAGE + FICHE -->
    <section class="pdp-sec pt-0">
      <div class="container">
        <div class="row g-5">
          <div class="col-lg-7">
            <span class="pdp-kicker">Mode d’emploi</span>
            <h2 class="pdp-h2 mb-4">{u["h2"]}</h2>
            {steps_html}
            <p class="small text-muted mt-2"><i class="bi bi-info-circle text-success"></i> {u["note"]}</p>
          </div>
          <div class="col-lg-5">
            <div class="pdp-spec">
              <span class="pdp-kicker" style="color:var(--gold)">{s["kicker"]}</span>
              <h2 class="display h4 mt-2 mb-3" style="color:#fff">{s["h2"]}</h2>
              <table>
                {rows_html}
              </table>
              <a class="btn-pill btn-green w-100 justify-content-center mt-3" href="contact.html">Recevoir la fiche technique</a>
            </div>
          </div>
        </div>
      </div>
    </section>"""


def render_crosssell(p):
    c = p.get("crosssell")
    if not c:
        return ""
    return f"""    <!-- CROSS-SELL mode de production -->
    <section class="pdp-sec pt-0">
      <div class="container">
        <div class="pdp-card d-flex flex-column flex-md-row align-items-md-center gap-3" style="border-left:4px solid var(--green)">
          <div class="flex-grow-1">
            <span class="pdp-tag">Mode de production</span>
            <h3 class="h5 mb-1" style="color:var(--navy);font-family:'Fraunces',serif">{c["title"]}</h3>
            <p class="text-muted mb-0">{c["text"]}</p>
          </div>
          <a class="btn-pill btn-green flex-none" href="{c["url"]}">{c["link_text"]} <i class="bi bi-arrow-right"></i></a>
        </div>
      </div>
    </section>"""


def render_faq(p):
    items = []
    for q in p["faq"]:
        items.append(
            f'<details><summary>{q["q"]}</summary><div class="ans">{q["a"]}</div></details>'
        )
    items_html = "\n            ".join(items)
    intro = p.get("faq_intro", "Une question ? ")
    return f"""    <!-- FAQ -->
    <section class="pdp-sec pt-0" id="faq">
      <div class="container">
        <div class="row g-5">
          <div class="col-lg-5">
            <span class="pdp-kicker">Questions fréquentes</span>
            <h2 class="pdp-h2">Tout comprendre</h2>
            <p class="text-muted mt-3">{intro}<a class="btn-line" href="{SITE["wa"]}" target="_blank" rel="noopener">Écrivez-nous</a></p>
          </div>
          <div class="col-lg-7 pdp-faq">
            {items_html}
          </div>
        </div>
      </div>
    </section>"""


def render_related(p):
    r = p.get("related")
    if not r:
        return ""
    cards = []
    for c in r["cards"]:
        cards.append(
            f'<div class="col-md-4"><div class="pdp-rel">'
            f'<img src="{c["img"]}" alt="{c["alt"]}">'
            f'<div class="bd"><span class="pdp-tag">{c["tag"]}</span>'
            f'<h5>{c["title"]}</h5><p>{c["text"]}</p>'
            f'<a class="btn-line" href="{c["url"]}">Découvrir <i class="bi bi-arrow-right"></i></a>'
            f'</div></div></div>'
        )
    cards_html = "\n          ".join(cards)
    return f"""    <!-- PRODUITS LIÉS -->
    <section class="pdp-sec pt-0">
      <div class="container">
        <div class="text-center mb-4">
          <span class="pdp-kicker">{r.get("kicker", "Produits associés")}</span>
          <h2 class="pdp-h2">Produits associés</h2>
        </div>
        <div class="row g-4">
          {cards_html}
        </div>
      </div>
    </section>"""


def render_ctaband(p):
    c = p["ctaband"]
    return f"""    <!-- CTA BAND -->
    <section class="pdp-sec pt-0">
      <div class="container">
        <div class="pdp-ctaband">
          <div class="row align-items-center g-4">
            <div class="col-lg-8">
              <span class="pdp-eyebrow">{c["eyebrow"]}</span>
              <h2 class="mt-2 mb-2">{c["h2"]}</h2>
              <p class="mb-0" style="color:rgba(255,255,255,.78)">{c["text"]}</p>
            </div>
            <div class="col-lg-4 text-lg-end">
              <a class="btn-pill btn-green mb-2" href="contact.html">Demander un devis <i class="bi bi-arrow-right"></i></a><br>
              <a class="btn-pill btn-ghost" href="{SITE["wa"]}" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i> WhatsApp direct</a>
            </div>
          </div>
        </div>
      </div>
    </section>"""


def render_jsonld(p):
    url = f'{SITE["base"]}/{p["url"]}'
    j = p["jsonld"]
    product = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": j["name"],
        "description": j["description"],
        "brand": {"@type": "Organization", "name": j.get("brand", SITE["brand"])},
        "image": p.get("og_image") or f'{SITE["base"]}/{p["image"]}',
        "sku": j["sku"],
        "category": j["category"],
        "audience": {"@type": "Audience", "audienceType": j["audience"]},
        "offers": {
            "@type": "Offer",
            "priceCurrency": "XOF",
            "availability": "https://schema.org/InStock",
            "url": url,
        },
    }
    crumbs = []
    for i, item in enumerate(p["breadcrumb_jsonld"], 1):
        crumbs.append({
            "@type": "ListItem",
            "position": i,
            "name": item["name"],
            "item": item["item"],
        })
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": crumbs,
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": strip_tags(q["q"]),
                "acceptedAnswer": {"@type": "Answer", "text": strip_tags(q.get("a_short", q["a"]))},
            }
            for q in p["faq"]
        ],
    }
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    return f"""  <script type="application/ld+json">
  {dump(product)}
  </script>
  <script type="application/ld+json">
  {dump(breadcrumb)}
  </script>
  <script type="application/ld+json">
  {dump(faq)}
  </script>"""


def strip_tags(s):
    """Retire les balises HTML simples pour le JSON-LD (texte brut)."""
    import re
    return html.unescape(re.sub(r"<[^>]+>", "", s))


# --------------------------------------------------------------------------- #
#  Page complète                                                               #
# --------------------------------------------------------------------------- #
def render_page(p):
    sections = [
        render_hero(p),
        render_benefits(p),
        render_transbadge(p),
        render_usage_spec(p),
        render_crosssell(p),
        render_faq(p),
        render_related(p),
        render_ctaband(p),
    ]
    main = "\n\n".join(s for s in sections if s)
    return f"""{render_head(p)}
<body class="pdp">
  <a class="skip-link visually-hidden-focusable" href="#main">Aller au contenu principal</a>
{NAVBAR}

  <main id="main">
{main}
  </main>

{FOOTER}

  <script src="vendor/jquery.2.2.3.min.js"></script>
  <script src="vendor/popper.js/popper.min.js"></script>
  <script src="vendor/bootstrap/js/bootstrap.min.js"></script>
  <script src="assets/js/main.min.js" defer></script>
{render_jsonld(p)}
  <script src="assets/js/site-crm-bridge.js" defer></script>
</body>
</html>
"""


def iter_products(data):
    """Aplatit toutes les catégories produits du JSON en une liste."""
    for key, items in data.items():
        if key.startswith("_"):
            continue
        if isinstance(items, list):
            for it in items:
                if it.get("_render", True) and "hero" in it:
                    yield it


# --------------------------------------------------------------------------- #
#  Renderers de PAGES FILIÈRE (matrice dérivée de products.json)               #
# --------------------------------------------------------------------------- #
def products_for_filiere(data, slug):
    """Cartes matrice pour une filière, ordonnées prêt-à-l'emploi puis FAF.

    Dérivé de products.json : impossible de placer un produit sur la mauvaise
    filière (la donnée fait foi)."""
    cards = []
    for cat in ("aliments_complets", "concentres", "macro_premix", "premix"):
        meta = CATEGORY_META[cat]
        for it in data.get(cat, []):
            if not it.get("_render", True) or "hero" not in it:
                continue
            if slug not in it.get("filieres", []):
                continue
            hero = it["hero"]
            cards.append({
                "url": it["url"],
                "name": it["jsonld"]["name"],
                "cat_label": meta["label"],
                "cat_icon": meta["icon"],
                "mode": meta["mode"],
                "badge": hero["pill"]["text"],
                "tagline": hero.get("figchip", {}).get("label", ""),
                "transversal": it.get("transversal", False),
            })
    return cards


def render_filiere_head(fl):
    url = f'{SITE["base"]}/{fl["url"]}'
    og_img = f'{SITE["base"]}/{fl["image"]}'
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta name="theme-color" content="#000066">
  <title>{fl["title"]}</title>
  <meta name="description" content="{fl["description"]}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{fl["title"]}">
  <meta property="og:description" content="{fl["description"]}">
  <meta property="og:image" content="{og_img}">
  <link rel="icon" type="image/png" sizes="56x56" href="favicon_io/favicon-32x32.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.15.3/css/all.css">
  <link rel="stylesheet" type="text/css" href="css/style.css">
  <link rel="stylesheet" type="text/css" href="css/responsive.css">
  <link rel="stylesheet" href="assets/css/main.min.css">
{HEAD_CSS}
{FILIERE_CSS}
</head>"""


def render_filiere_hero(fl):
    crumb = (
        '<a href="index.html">Accueil</a>'
        ' <span class="mx-1 text-white-50">/</span>\n          '
        '<a href="volailles.html">Volailles</a>'
        ' <span class="mx-1 text-white-50">/</span>\n          '
        f'<span class="text-white-50">{fl["eyebrow"].split("—")[-1].strip()}</span>'
    )
    return f"""    <!-- HERO FILIÈRE -->
    <section class="pdp-hero">
      <div class="container">
        <nav class="pdp-crumb small mb-3 pdp-reveal" aria-label="Fil d'Ariane">
          {crumb}
        </nav>
        <div class="row g-5 align-items-center">
          <div class="col-lg-7">
            <span class="pdp-eyebrow pdp-reveal d1">{fl["eyebrow"]}</span>
            <h1 class="pdp-reveal d1">{fl["h1"]}</h1>
            <p class="pdp-lead pdp-reveal d2">{fl["lead"]}</p>
            <div class="d-flex flex-wrap gap-3 mt-4 pdp-reveal d3">
              <a class="btn-pill btn-green" href="#gamme">Voir la gamme <i class="bi bi-arrow-down"></i></a>
              <a class="btn-pill btn-ghost" href="{SITE["wa"]}" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i> Parler à un technicien</a>
            </div>
            <div class="pdp-facts pdp-reveal d4">
              {render_facts(fl["facts"])}
            </div>
          </div>
          <div class="col-lg-5">
            <figure class="pdp-figure pdp-reveal d2 mb-0">
              <img src="{fl["image"]}" alt="{fl["image_alt"]}">
            </figure>
          </div>
        </div>
      </div>
    </section>"""


def render_pillars(piliers):
    cards = []
    for p in piliers:
        cards.append(
            f'<div class="fl-pillar"><span class="ic"><i class="bi {p["icon"]}"></i></span>'
            f'<h3>{p["titre"]}</h3><p>{p["phrase"]}</p></div>'
        )
    cards_html = "\n          ".join(cards)
    return f"""    <!-- PILLARS-STRIP (4 piliers) -->
    <section class="pdp-sec" id="pourquoi">
      <div class="container">
        <div class="text-center mb-4">
          <span class="pdp-kicker">Pourquoi MARIDAV</span>
          <h2 class="pdp-h2">Quatre raisons de nous confier vos bandes</h2>
        </div>
        <div class="fl-pillars">
          {cards_html}
        </div>
      </div>
    </section>"""


def render_timeline(fl):
    steps = []
    for i, t in enumerate(fl["timeline"], 1):
        steps.append(
            f'<div class="fl-tstep"><span class="num">{i}</span>'
            f'<span class="age">{t["age"]}</span><h3>{t["phase"]}</h3>'
            f'<p>{t["text"]}</p>'
            f'<a class="btn-line" href="{t["url"]}">{t["cta"]} <i class="bi bi-arrow-right"></i></a>'
            f'</div>'
        )
    steps_html = "\n          ".join(steps)
    return f"""    <!-- CYCLE-TIMELINE -->
    <section class="pdp-sec pt-0" id="cycle">
      <div class="container">
        <div class="mb-4">
          <span class="pdp-kicker">{fl["timeline_kicker"]}</span>
          <h2 class="pdp-h2">{fl["timeline_h2"]}</h2>
          <p class="text-muted mt-3 mb-0" style="max-width:46rem">{fl["timeline_intro"]}</p>
        </div>
        <div class="fl-timeline">
          {steps_html}
        </div>
      </div>
    </section>"""


def render_matrix(fl, cards):
    has_faf = any(c["mode"] == "faf" for c in cards)
    has_pret = any(c["mode"] == "pret" for c in cards)
    modes = ['<button class="fl-mode is-active" data-filter="all"><i class="bi bi-grid"></i> Tout voir</button>']
    if has_pret:
        modes.append('<button class="fl-mode" data-filter="pret"><i class="bi bi-bag-check"></i> Prêt à l\'emploi</button>')
    if has_faf:
        modes.append('<button class="fl-mode" data-filter="faf"><i class="bi bi-sliders"></i> Je fabrique (FAF)</button>')
    modes_html = "\n            ".join(modes)
    items = []
    for c in cards:
        tags = ""
        if c["transversal"]:
            tags = '<div class="tags"><span class="tg"><i class="bi bi-arrow-left-right"></i> Transversal</span></div>'
        items.append(
            f'<article class="fl-mcard" data-mode="{c["mode"]}">'
            f'<span class="cat"><i class="bi {c["cat_icon"]}"></i> {c["cat_label"]}</span>'
            f'<h3>{c["name"]}</h3>'
            f'<p class="badge-phase">{c["badge"]}</p>'
            f'<p>{c["tagline"]}</p>'
            f'{tags}'
            f'<a class="btn-line" href="{c["url"]}">Découvrir <i class="bi bi-arrow-right"></i></a>'
            f'</article>'
        )
    items_html = "\n            ".join(items)
    return f"""    <!-- MODE-SWITCH + PRODUCT-MATRIX -->
    <section class="pdp-sec pt-0" id="gamme">
      <div class="container">
        <div class="mb-4">
          <span class="pdp-kicker">La gamme</span>
          <h2 class="pdp-h2">Acheter prêt à l'emploi, ou fabriquer votre aliment</h2>
          <div class="fl-modes mt-3" role="group" aria-label="Mode de production">
            {modes_html}
          </div>
          <p class="fl-modehint" id="fl-modehint">Toute la gamme volailles, prête à l'emploi comme en fabrication assistée.</p>
        </div>
        <div class="fl-matrix" id="fl-matrix">
            {items_html}
        </div>
        <p class="fl-empty" id="fl-empty">Aucun produit dans cette sélection.</p>
      </div>
    </section>"""


def render_additives(fl):
    adds = fl.get("additives")
    if not adds:
        return ""
    cards = []
    for a in adds:
        cards.append(
            f'<div class="col-md-6 col-lg-3"><div class="pdp-card h-100">'
            f'<span class="pdp-tag">Additif</span>'
            f'<h3 class="h6" style="color:var(--navy);font-family:\'Fraunces\',serif;margin:.2rem 0 .35rem">{a["name"]}</h3>'
            f'<p class="text-muted small mb-3">{a["text"]}</p>'
            f'<a class="btn-line" href="{a["url"]}">Découvrir <i class="bi bi-arrow-right"></i></a>'
            f'</div></div>'
        )
    cards_html = "\n          ".join(cards)
    return f"""    <!-- ADDITIFS & BIOSÉCURITÉ -->
    <section class="pdp-sec pt-0" id="additifs">
      <div class="container">
        <div class="mb-4">
          <span class="pdp-kicker">Additifs &amp; biosécurité</span>
          <h2 class="pdp-h2">Compléter le programme</h2>
        </div>
        <div class="row g-4">
          {cards_html}
        </div>
      </div>
    </section>"""


def render_proofbar():
    items = []
    for p in PROOF_POINTS:
        items.append(f'<div class="fl-pitem"><b>{p["b"]}</b><span>{p["span"]}</span></div>')
    items_html = "\n            ".join(items)
    return f"""    <!-- PROOF-BAR -->
    <section class="pdp-sec pt-0" id="preuve">
      <div class="container">
        <div class="fl-proof">
          <div class="fl-proofgrid">
            {items_html}
          </div>
          <p class="fl-proofnote">Résultats chiffrés (FCR, poids/âge, taux de ponte) et références d'élevages communiqués par nos techniciens, selon votre conduite d'élevage.</p>
        </div>
      </div>
    </section>"""


def render_techcta():
    return f"""    <!-- TECHNICIAN-CTA -->
    <section class="pdp-sec pt-0">
      <div class="container">
        <div class="fl-tech">
          <div class="tx">
            <h3>Pas sûr du bon programme pour votre bande&nbsp;?</h3>
            <p>Parlez à un technicien MARIDAV : il cadre la formulation et le devis avec vous.</p>
          </div>
          <div class="ax">
            <a class="btn-pill btn-green" href="contact.html">Demander un devis <i class="bi bi-arrow-right"></i></a>
            <a class="btn-pill btn-ghost" href="{SITE["wa"]}" target="_blank" rel="noopener" style="border-color:rgba(255,255,255,.5)"><i class="bi bi-whatsapp"></i> WhatsApp</a>
          </div>
        </div>
      </div>
    </section>"""


def render_filiere_crosssell(fl):
    return f"""    <!-- CROSS-SELL FILIÈRE -->
    <section class="pdp-sec pt-0">
      <div class="container">
        <div class="pdp-card d-flex flex-column flex-md-row align-items-md-center gap-3" style="border-left:4px solid var(--green)">
          <div class="flex-grow-1">
            <span class="pdp-tag">Autre filière</span>
            <h3 class="h5 mb-1" style="color:var(--navy);font-family:'Fraunces',serif">{fl["cross_label"]}</h3>
            <p class="text-muted mb-0">{fl["cross_text"]}</p>
          </div>
          <a class="btn-pill btn-green flex-none" href="{fl["cross_url"]}">{fl["cross_link"]} <i class="bi bi-arrow-right"></i></a>
        </div>
      </div>
    </section>"""


def render_filiere_jsonld(fl, cards):
    url = f'{SITE["base"]}/{fl["url"]}'
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f'{SITE["base"]}/'},
            {"@type": "ListItem", "position": 2, "name": "Volailles", "item": f'{SITE["base"]}/volailles.html'},
            {"@type": "ListItem", "position": 3, "name": fl["eyebrow"].split("—")[-1].strip(), "item": url},
        ],
    }
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": fl["title"],
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": c["name"], "url": f'{SITE["base"]}/{c["url"]}'}
            for i, c in enumerate(cards, 1)
        ],
    }
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    return f"""  <script type="application/ld+json">
  {dump(breadcrumb)}
  </script>
  <script type="application/ld+json">
  {dump(itemlist)}
  </script>"""


def render_filiere_page(fl, data):
    piliers = data["_meta"]["piliers"]
    cards = products_for_filiere(data, fl["_slug"])
    sections = [
        render_filiere_hero(fl),
        render_pillars(piliers),
        render_timeline(fl),
        render_matrix(fl, cards),
        render_additives(fl),
        render_proofbar(),
        render_techcta(),
        render_filiere_crosssell(fl),
    ]
    main = "\n\n".join(s for s in sections if s)
    return f"""{render_filiere_head(fl)}
<body class="pdp">
  <a class="skip-link visually-hidden-focusable" href="#main">Aller au contenu principal</a>
{NAVBAR}

  <main id="main">
{main}
  </main>

{FOOTER}

  <script src="vendor/jquery.2.2.3.min.js"></script>
  <script src="vendor/popper.js/popper.min.js"></script>
  <script src="vendor/bootstrap/js/bootstrap.min.js"></script>
  <script src="assets/js/main.min.js" defer></script>
{render_filiere_jsonld(fl, cards)}
{FILIERE_JS}
  <script src="assets/js/site-crm-bridge.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
#  Renderer du HUB volailles                                                    #
# --------------------------------------------------------------------------- #
def render_hub_hero(h):
    crumb = (
        '<a href="index.html">Accueil</a>'
        ' <span class="mx-1 text-white-50">/</span>\n          '
        '<span class="text-white-50">Volailles</span>'
    )
    return f"""    <!-- HERO HUB -->
    <section class="pdp-hero">
      <div class="container">
        <nav class="pdp-crumb small mb-3 pdp-reveal" aria-label="Fil d'Ariane">
          {crumb}
        </nav>
        <div class="row g-5 align-items-center">
          <div class="col-lg-7">
            <span class="pdp-eyebrow pdp-reveal d1">{h["eyebrow"]}</span>
            <h1 class="pdp-reveal d1">{h["h1"]}</h1>
            <p class="pdp-lead pdp-reveal d2">{h["lead"]}</p>
            <div class="d-flex flex-wrap gap-3 mt-4 pdp-reveal d3">
              <a class="btn-pill btn-green" href="#filieres">Choisir ma filière <i class="bi bi-arrow-down"></i></a>
              <a class="btn-pill btn-ghost" href="{SITE["wa"]}" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i> Parler à un technicien</a>
            </div>
            <div class="pdp-facts pdp-reveal d4">
              {render_facts(h["facts"])}
            </div>
          </div>
          <div class="col-lg-5">
            <figure class="pdp-figure pdp-reveal d2 mb-0">
              <img src="{h["image"]}" alt="{h["image_alt"]}">
            </figure>
          </div>
        </div>
      </div>
    </section>"""


def render_hub_choices(h):
    cards = []
    for c in h["choices"]:
        bullets = "\n              ".join(
            f'<li><i class="bi bi-check-circle-fill"></i><span>{b}</span></li>' for b in c["bullets"]
        )
        cards.append(f"""<article class="hub-choice">
            <div class="vis" style="background-image:url('{c["image"]}')" role="img" aria-label="{c["title"]}"></div>
            <div class="bd">
              <h3>{c["title"]}</h3>
              <p class="sub">{c["sub"]}</p>
              <ul>
              {bullets}
              </ul>
              <div class="ax">
                <a class="btn-pill btn-green" href="{c["url"]}">Voir la gamme <i class="bi bi-arrow-right"></i></a>
                <a class="btn-line" href="contact.html">Demander un devis</a>
              </div>
            </div>
          </article>""")
    cards_html = "\n          ".join(cards)
    return f"""    <!-- AIGUILLAGE FILIÈRES -->
    <section class="pdp-sec" id="filieres">
      <div class="container">
        <div class="text-center mb-4">
          <span class="pdp-kicker">Choisissez votre filière</span>
          <h2 class="pdp-h2">Deux programmes, une même exigence</h2>
        </div>
        <div class="hub-choices">
          {cards_html}
        </div>
      </div>
    </section>"""


def render_hub_steps(h):
    steps = []
    for i, s in enumerate(h["steps"], 1):
        steps.append(
            f'<div class="hub-step"><span class="num">{i}</span>'
            f'<h3>{s["title"]}</h3><p>{s["text"]}</p></div>'
        )
    steps_html = "\n          ".join(steps)
    return f"""    <!-- COMMENT ÇA MARCHE -->
    <section class="pdp-sec pt-0" id="comment">
      <div class="container">
        <div class="mb-4">
          <span class="pdp-kicker">Comment ça marche</span>
          <h2 class="pdp-h2">De votre élevage au devis, en 3 étapes</h2>
        </div>
        <div class="hub-steps">
          {steps_html}
        </div>
      </div>
    </section>"""


def render_hub_jsonld(h):
    url = f'{SITE["base"]}/{h["url"]}'
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f'{SITE["base"]}/'},
            {"@type": "ListItem", "position": 2, "name": "Volailles", "item": url},
        ],
    }
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": h["title"],
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": c["title"], "url": f'{SITE["base"]}/{c["url"]}'}
            for i, c in enumerate(h["choices"], 1)
        ],
    }
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    return f"""  <script type="application/ld+json">
  {dump(breadcrumb)}
  </script>
  <script type="application/ld+json">
  {dump(itemlist)}
  </script>"""


def render_hub_page(h, data):
    piliers = data["_meta"]["piliers"]
    sections = [
        render_hub_hero(h),
        render_hub_choices(h),
        render_pillars(piliers),
        render_hub_steps(h),
        render_proofbar(),
        render_techcta(),
    ]
    main = "\n\n".join(s for s in sections if s)
    return f"""{render_filiere_head(h)}
<body class="pdp">
  <a class="skip-link visually-hidden-focusable" href="#main">Aller au contenu principal</a>
{NAVBAR}

  <main id="main">
{main}
  </main>

{FOOTER}

  <script src="vendor/jquery.2.2.3.min.js"></script>
  <script src="vendor/popper.js/popper.min.js"></script>
  <script src="vendor/bootstrap/js/bootstrap.min.js"></script>
  <script src="assets/js/main.min.js" defer></script>
{render_hub_jsonld(h)}
  <script src="assets/js/site-crm-bridge.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
#  Génération SEO (sitemap / robots / llms) depuis l'état réel du site          #
# --------------------------------------------------------------------------- #
def is_indexable(path):
    """True si la page root est une vraie page (pas une capture d'erreur ni un gabarit)."""
    if "%" in path.name:           # vestiges d'URL encodée (%) → non indexable
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:2000]
    except Exception:
        return False
    m = re.search(r"<title>(.*?)</title>", head, re.S | re.I)
    if not m:
        return False
    title = m.group(1).strip()
    return not any(bad in title for bad in SITEMAP_SKIP_TITLE)


def indexable_pages():
    """Liste triée des pages root indexables (noms de fichiers)."""
    pages = []
    for p in sorted(ROOT.glob("*.html")):
        if is_indexable(p):
            pages.append(p.name)
    return pages


def page_loc(name):
    return f'{SITE["base"]}/' if name == "index.html" else f'{SITE["base"]}/{name}'


def sitemap_meta(name):
    if name in SITEMAP_RULES:
        return SITEMAP_RULES[name]
    if name.startswith("article-"):
        return ("0.7", "monthly")
    return ("0.6", "monthly")


def build_sitemap(pages):
    rows = []
    for name in pages:
        prio, freq = sitemap_meta(name)
        rows.append(
            f"  <url>\n    <loc>{page_loc(name)}</loc>\n"
            f"    <lastmod>{BUILD_DATE}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{prio}</priority>\n  </url>"
        )
    body = "\n".join(rows)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n"
    )


def build_llms():
    out = [f'# {LLMS["title"]}', "", f'> {LLMS["summary"]}', ""]
    for heading, items in LLMS["sections"]:
        out.append(f"## {heading}")
        for label, url, desc in items:
            full = f'{SITE["base"]}/' if url == "" else f'{SITE["base"]}/{url}'
            line = f"- [{label}]({full})"
            if desc:
                line += f" : {desc}"
            out.append(line)
        out.append("")
    out.append("## Contact")
    for c in LLMS["contact"]:
        out.append(f"- {c}")
    return "\n".join(out) + "\n"


def seo_gate(pages):
    """Release-gate SEO : vérifie la cohérence des artefacts générés. Retourne (ok, msgs)."""
    msgs = []
    ok = True
    on_disk = {p.name for p in ROOT.glob("*.html")}

    # 1) toute URL du sitemap existe sur disque
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>(.*?)</loc>", sm)
    for loc in locs:
        name = loc.replace(f'{SITE["base"]}/', "") or "index.html"
        if name not in on_disk:
            ok = False
            msgs.append(f"  ✗ sitemap → fichier absent : {name}")
    # 2) pas de page d'erreur/junk dans le sitemap
    for loc in locs:
        name = loc.replace(f'{SITE["base"]}/', "") or "index.html"
        if name in on_disk and not is_indexable(ROOT / name):
            ok = False
            msgs.append(f"  ✗ sitemap → page non indexable listée : {name}")
    # 3) toute page générée (produits toutes espèces + filières + hub) est dans le sitemap
    vol = []
    for src in PRODUCT_SOURCES:
        if src.exists():
            vol += [p["url"] for p in iter_products(json.loads(src.read_text(encoding="utf-8")))]
    vol += [fl["url"] for fl in FILIERES.values()] + [HUB["url"]]
    smnames = {loc.replace(f'{SITE["base"]}/', "") or "index.html" for loc in locs}
    for u in vol:
        if u not in smnames:
            ok = False
            msgs.append(f"  ✗ sitemap → page volailles manquante : {u}")
    # 4) liens llms.txt résolus
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for url in re.findall(r"\((%s/[^)]*)\)" % re.escape(SITE["base"]), llms):
        name = url.replace(f'{SITE["base"]}/', "") or "index.html"
        if name not in on_disk:
            ok = False
            msgs.append(f"  ✗ llms.txt → fichier absent : {name}")
    # 5) robots référence le sitemap
    rb = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap:" not in rb:
        ok = False
        msgs.append("  ✗ robots.txt → directive Sitemap absente")

    msgs.append(f"  {'✓' if ok else '✗'} {len(locs)} URL au sitemap, {len(pages)} pages indexables détectées")
    return ok, msgs


# --------------------------------------------------------------------------- #
#  Renderers HUB PORCS                                                          #
# --------------------------------------------------------------------------- #
def render_porc_hub_hero(h):
    crumb = (
        '<a href="index.html">Accueil</a>'
        ' <span class="mx-1 text-white-50">/</span>\n          '
        '<span class="text-white-50">Porcs</span>'
    )
    return f"""    <!-- HERO HUB PORCS -->
    <section class="pdp-hero">
      <div class="container">
        <nav class="pdp-crumb small mb-3 pdp-reveal" aria-label="Fil d'Ariane">
          {crumb}
        </nav>
        <div class="row g-5 align-items-center">
          <div class="col-lg-7">
            <span class="pdp-eyebrow pdp-reveal d1">{h["eyebrow"]}</span>
            <h1 class="pdp-reveal d1">{h["h1"]}</h1>
            <p class="pdp-lead pdp-reveal d2">{h["lead"]}</p>
            <div class="d-flex flex-wrap gap-3 mt-4 pdp-reveal d3">
              <a class="btn-pill btn-green" href="#cycle">Voir le cycle <i class="bi bi-arrow-down"></i></a>
              <a class="btn-pill btn-ghost" href="{SITE["wa"]}" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i> Parler à un technicien</a>
            </div>
            <div class="pdp-facts pdp-reveal d4">
              {render_facts(h["facts"])}
            </div>
          </div>
          <div class="col-lg-5">
            <figure class="pdp-figure pdp-reveal d2 mb-0">
              <img src="{h["image"]}" alt="{h["image_alt"]}">
            </figure>
          </div>
        </div>
      </div>
    </section>"""


def render_porc_timeline_2tracks(tl):
    def step_html(s, idx):
        return (
            f'<div class="fl-tstep">'
            f'<span class="num">{idx + 1}</span>'
            f'<span class="age">{s["age"]}</span>'
            f'<h3>{s["phase"]}</h3>'
            f'<p>{s["text"]}</p>'
            f'<a class="btn-line" href="{s["url"]}">{s["cta"]} <i class="bi bi-arrow-right"></i></a>'
            f'</div>'
        )

    eng_steps = "\n          ".join(step_html(s, i) for i, s in enumerate(tl["eng"]))
    rep_steps = "\n          ".join(step_html(s, i) for i, s in enumerate(tl["rep"]))
    return f"""    <!-- CYCLE-TIMELINE 2 PISTES -->
    <section class="pdp-sec" id="cycle">
      <div class="container">
        <div class="text-center mb-4">
          <span class="pdp-kicker">{tl["kicker"]}</span>
          <h2 class="pdp-h2">{tl["h2"]}</h2>
          <p class="pdp-muted mt-2">{tl["intro"]}</p>
        </div>
        <div class="fl-track-switch mb-3" role="group" aria-label="Piste du cycle">
          <button class="fl-tswitch is-active" data-track="eng"><i class="bi bi-arrow-right-square"></i> Engraissement</button>
          <button class="fl-tswitch" data-track="rep"><i class="bi bi-heart"></i> Reproduction</button>
        </div>
        <div id="fl-track-eng" class="fl-track is-active">
          {eng_steps}
        </div>
        <div id="fl-track-rep" class="fl-track">
          {rep_steps}
        </div>
      </div>
    </section>"""


def render_porc_matrix(porc_data):
    cards = []
    for cat in ("aliments_complets", "concentres"):
        meta = CATEGORY_META[cat]
        for p in porc_data.get(cat, []):
            if not p.get("_render", True) or "hero" not in p:
                continue
            hero = p["hero"]
            tags = ""
            if p.get("transversal", False):
                tags = '<div class="tags"><span class="tg"><i class="bi bi-arrow-left-right"></i> Transversal</span></div>'
            cards.append(
                f'<article class="fl-mcard" data-mode="{meta["mode"]}">'
                f'<span class="cat"><i class="bi {meta["icon"]}"></i> {meta["label"]}</span>'
                f'<h3>{p["jsonld"]["name"]}</h3>'
                f'<p class="badge-phase">{hero["pill"]["text"]}</p>'
                f'<p>{hero.get("figchip", {}).get("label", "")}</p>'
                f'{tags}'
                f'<a class="btn-line" href="{p["url"]}">Découvrir <i class="bi bi-arrow-right"></i></a>'
                f'</article>'
            )

    modes_btns = (
        '<button class="fl-mode is-active" data-filter="all"><i class="bi bi-grid"></i> Tout voir</button>'
        '<button class="fl-mode" data-filter="pret"><i class="bi bi-bag-check"></i> Prêt à l\'emploi</button>'
        '<button class="fl-mode" data-filter="faf"><i class="bi bi-sliders"></i> Je fabrique (FAF)</button>'
    )
    cards_html = "\n          ".join(cards)
    return f"""    <!-- MATRICE PRODUITS PORCS -->
    <section class="pdp-sec" id="gamme">
      <div class="container">
        <div class="mb-4">
          <span class="pdp-kicker">Toute la gamme</span>
          <h2 class="pdp-h2">Aliments & concentrés — engraissement et reproduction</h2>
          <div class="fl-modes mt-3" role="group" aria-label="Mode de production">
            {modes_btns}
          </div>
          <p class="fl-modehint" id="fl-modehint">Toute la gamme porcs, prête à l'emploi comme en fabrication assistée.</p>
        </div>
        <div class="fl-matrix" id="fl-matrix">
          {cards_html}
        </div>
        <p class="fl-empty" id="fl-empty">Aucun produit pour ce filtre.</p>
      </div>
    </section>"""


def render_porc_hub_jsonld(h):
    url = f'{SITE["base"]}/{h["url"]}'
    all_products = list(h["timeline"]["eng"]) + list(h["timeline"]["rep"])
    seen = {}
    deduped = []
    for p in all_products:
        if p["url"] not in seen:
            seen[p["url"]] = True
            deduped.append(p)
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f'{SITE["base"]}/'},
            {"@type": "ListItem", "position": 2, "name": "Porcs", "item": url},
        ],
    }
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": h["title"],
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": p["phase"], "url": f'{SITE["base"]}/{p["url"]}'}
            for i, p in enumerate(deduped, 1)
        ],
    }
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    return f"""  <script type="application/ld+json">
  {dump(breadcrumb)}
  </script>
  <script type="application/ld+json">
  {dump(itemlist)}
  </script>"""


def render_porc_hub_page(h, porc_data):
    piliers = porc_data["_meta"]["piliers"]
    sections = [
        render_porc_hub_hero(h),
        render_porc_timeline_2tracks(h["timeline"]),
        render_pillars(piliers),
        render_porc_matrix(porc_data),
        render_proofbar(),
        render_techcta(),
        render_hub_steps(h),
    ]
    main = "\n\n".join(s for s in sections if s)
    return f"""{render_filiere_head(h)}
<body class="pdp">
  <a class="skip-link visually-hidden-focusable" href="#main">Aller au contenu principal</a>
{NAVBAR}

  <main id="main">
{main}
  </main>

{FOOTER}

  <script src="vendor/jquery.2.2.3.min.js"></script>
  <script src="vendor/popper.js/popper.min.js"></script>
  <script src="vendor/bootstrap/js/bootstrap.min.js"></script>
  <script src="assets/js/main.min.js" defer></script>
{FILIERE_JS}
{render_porc_hub_jsonld(h)}
  <script src="assets/js/site-crm-bridge.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
#  Renderers HUB POISSONS                                                       #
# --------------------------------------------------------------------------- #
def render_poisson_hub_hero(h):
    crumb = (
        '<a href="index.html">Accueil</a>'
        ' <span class="mx-1 text-white-50">/</span>\n          '
        '<span class="text-white-50">Poissons</span>'
    )
    return f"""    <!-- HERO HUB POISSONS -->
    <section class="pdp-hero">
      <div class="container">
        <nav class="pdp-crumb small mb-3 pdp-reveal" aria-label="Fil d'Ariane">
          {crumb}
        </nav>
        <div class="row g-5 align-items-center">
          <div class="col-lg-7">
            <span class="pdp-eyebrow pdp-reveal d1">{h["eyebrow"]}</span>
            <h1 class="pdp-reveal d1">{h["h1"]}</h1>
            <p class="pdp-lead pdp-reveal d2">{h["lead"]}</p>
            <div class="d-flex flex-wrap gap-3 mt-4 pdp-reveal d3">
              <a class="btn-pill btn-green" href="#cycle">Voir le cycle <i class="bi bi-arrow-down"></i></a>
              <a class="btn-pill btn-ghost" href="{SITE["wa"]}" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i> Parler à un technicien</a>
            </div>
            <div class="pdp-facts pdp-reveal d4">
              {render_facts(h["facts"])}
            </div>
          </div>
          <div class="col-lg-5">
            <figure class="pdp-figure pdp-reveal d2 mb-0">
              <img src="{h["image"]}" alt="{h["image_alt"]}">
            </figure>
          </div>
        </div>
      </div>
    </section>"""


def render_poisson_timeline(tl):
    def step_html(s, idx):
        return (
            f'<div class="fl-tstep">'
            f'<span class="num">{idx + 1}</span>'
            f'<span class="age">{s["age"]}</span>'
            f'<h3>{s["phase"]}</h3>'
            f'<p>{s["text"]}</p>'
            f'<a class="btn-line" href="{s["url"]}">{s["cta"]} <i class="bi bi-arrow-right"></i></a>'
            f'</div>'
        )

    steps_html = "\n          ".join(step_html(s, i) for i, s in enumerate(tl["steps"]))
    return f"""    <!-- CYCLE-TIMELINE POISSONS (linéaire) -->
    <section class="pdp-sec" id="cycle">
      <div class="container">
        <div class="text-center mb-4">
          <span class="pdp-kicker">{tl["kicker"]}</span>
          <h2 class="pdp-h2">{tl["h2"]}</h2>
          <p class="pdp-muted mt-2">{tl["intro"]}</p>
        </div>
        <div id="fl-track-tilapia" class="fl-track is-active">
          {steps_html}
        </div>
      </div>
    </section>"""


def render_poisson_matrix(poisson_data):
    cards = []
    for cat in ("aliments_complets", "additifs", "concentres"):
        if cat not in CATEGORY_META:
            continue
        meta = CATEGORY_META[cat]
        for p in poisson_data.get(cat, []):
            if not p.get("_render", True) or "hero" not in p:
                continue
            hero = p["hero"]
            tags = ""
            if p.get("transversal", False):
                tags = '<div class="tags"><span class="tg"><i class="bi bi-arrow-left-right"></i> Transversal</span></div>'
            cards.append(
                f'<article class="fl-mcard" data-mode="{meta["mode"]}">'
                f'<span class="cat"><i class="bi {meta["icon"]}"></i> {meta["label"]}</span>'
                f'<h3>{p["jsonld"]["name"]}</h3>'
                f'<p class="badge-phase">{hero["pill"]["text"]}</p>'
                f'<p>{hero.get("figchip", {}).get("label", "")}</p>'
                f'{tags}'
                f'<a class="btn-line" href="{p["url"]}">Découvrir <i class="bi bi-arrow-right"></i></a>'
                f'</article>'
            )

    modes_btns = (
        '<button class="fl-mode is-active" data-filter="all"><i class="bi bi-grid"></i> Tout voir</button>'
        '<button class="fl-mode" data-filter="pret"><i class="bi bi-bag-check"></i> Prêt à l\'emploi</button>'
        '<button class="fl-mode" data-filter="faf"><i class="bi bi-sliders"></i> Je fabrique (FAF)</button>'
    )
    cards_html = "\n          ".join(cards)
    return f"""    <!-- MATRICE PRODUITS POISSONS -->
    <section class="pdp-sec" id="gamme">
      <div class="container">
        <div class="mb-4">
          <span class="pdp-kicker">Toute la gamme</span>
          <h2 class="pdp-h2">Aliments & additifs — du granulé à la qualité d'eau</h2>
          <div class="fl-modes mt-3" role="group" aria-label="Mode de production">
            {modes_btns}
          </div>
          <p class="fl-modehint" id="fl-modehint">Toute la gamme pisciculture, prête à l'emploi comme en fabrication assistée.</p>
        </div>
        <div class="fl-matrix" id="fl-matrix">
          {cards_html}
        </div>
        <p class="fl-empty" id="fl-empty">Aucun produit pour ce filtre.</p>
      </div>
    </section>"""


def render_poisson_hub_jsonld(h):
    url = f'{SITE["base"]}/{h["url"]}'
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f'{SITE["base"]}/'},
            {"@type": "ListItem", "position": 2, "name": "Poissons", "item": url},
        ],
    }
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": h["title"],
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": s["phase"] + " " + s["age"], "url": f'{SITE["base"]}/{s["url"]}'}
            for i, s in enumerate(h["timeline"]["steps"], 1)
        ],
    }
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    return f"""  <script type="application/ld+json">
  {dump(breadcrumb)}
  </script>
  <script type="application/ld+json">
  {dump(itemlist)}
  </script>"""


def render_poisson_hub_page(h, poisson_data):
    piliers = poisson_data["_meta"]["piliers"]
    sections = [
        render_poisson_hub_hero(h),
        render_poisson_timeline(h["timeline"]),
        render_pillars(piliers),
        render_poisson_matrix(poisson_data),
        render_proofbar(),
        render_techcta(),
        render_hub_steps(h),
    ]
    main = "\n\n".join(s for s in sections if s)
    return f"""{render_filiere_head(h)}
<body class="pdp">
  <a class="skip-link visually-hidden-focusable" href="#main">Aller au contenu principal</a>
{NAVBAR}

  <main id="main">
{main}
  </main>

{FOOTER}

  <script src="vendor/jquery.2.2.3.min.js"></script>
  <script src="vendor/popper.js/popper.min.js"></script>
  <script src="vendor/bootstrap/js/bootstrap.min.js"></script>
  <script src="assets/js/main.min.js" defer></script>
{FILIERE_JS}
{render_poisson_hub_jsonld(h)}
  <script src="assets/js/site-crm-bridge.js" defer></script>
</body>
</html>
"""


def generate_seo():
    pages = indexable_pages()
    (ROOT / "sitemap.xml").write_text(build_sitemap(pages), encoding="utf-8")
    (ROOT / "robots.txt").write_text(ROBOTS_TXT, encoding="utf-8")
    (ROOT / "llms.txt").write_text(build_llms(), encoding="utf-8")
    print(f"  écrit  sitemap.xml ({len(pages)} URL) · robots.txt · llms.txt")
    ok, msgs = seo_gate(pages)
    print("\n— Release-gate SEO —")
    for m in msgs:
        print(m)
    return ok


def main():
    check = "--check" in sys.argv
    data = json.loads(DATA.read_text(encoding="utf-8"))

    # 1) Pages produits (toutes espèces)
    written = 0
    for src in PRODUCT_SOURCES:
        if not src.exists():
            continue
        sdata = json.loads(src.read_text(encoding="utf-8"))
        for p in iter_products(sdata):
            html_out = render_page(p)
            target = ROOT / p["url"]
            if check:
                print(f"  [check] {p['url']:48s} {len(html_out):6d} o")
            else:
                target.write_text(html_out, encoding="utf-8")
                print(f"  écrit  {p['url']:48s} {len(html_out):6d} o")
            written += 1
    print(f"\n{written} page(s) produit générée(s).")

    # 2) Pages filière (matrice dérivée de products.json)
    fwritten = 0
    for slug, fl in FILIERES.items():
        fl = {**fl, "_slug": slug}
        html_out = render_filiere_page(fl, data)
        target = ROOT / fl["url"]
        n = len(products_for_filiere(data, slug))
        if check:
            print(f"  [check] {fl['url']:48s} {len(html_out):6d} o ({n} produits)")
        else:
            target.write_text(html_out, encoding="utf-8")
            print(f"  écrit  {fl['url']:48s} {len(html_out):6d} o ({n} produits)")
        fwritten += 1
    print(f"{fwritten} page(s) filière générée(s).")

    # 3) Hub volailles
    hub_out = render_hub_page(HUB, data)
    if check:
        print(f"  [check] {HUB['url']:48s} {len(hub_out):6d} o (hub)")
    else:
        (ROOT / HUB["url"]).write_text(hub_out, encoding="utf-8")
        print(f"  écrit  {HUB['url']:48s} {len(hub_out):6d} o (hub)")

    # 3b) Hub porcs
    porc_data = json.loads(PORC_DATA.read_text(encoding="utf-8"))
    porc_hub_out = render_porc_hub_page(PORC_HUB, porc_data)
    if check:
        print(f"  [check] {PORC_HUB['url']:48s} {len(porc_hub_out):6d} o (hub)")
    else:
        (ROOT / PORC_HUB["url"]).write_text(porc_hub_out, encoding="utf-8")
        print(f"  écrit  {PORC_HUB['url']:48s} {len(porc_hub_out):6d} o (hub)")

    # 3c) Hub poissons
    poisson_data = json.loads(POISSON_DATA.read_text(encoding="utf-8"))
    poisson_hub_out = render_poisson_hub_page(POISSON_HUB, poisson_data)
    if check:
        print(f"  [check] {POISSON_HUB['url']:48s} {len(poisson_hub_out):6d} o (hub)")
    else:
        (ROOT / POISSON_HUB["url"]).write_text(poisson_hub_out, encoding="utf-8")
        print(f"  écrit  {POISSON_HUB['url']:48s} {len(poisson_hub_out):6d} o (hub)")
    print("3 hubs générés (volailles + porcs + poissons).")

    # 4) SEO (sitemap / robots / llms) + release-gate
    if not check:
        print()
        ok = generate_seo()
        if not ok:
            print("\n⚠ Release-gate SEO en échec — voir ci-dessus.")
            sys.exit(1)


if __name__ == "__main__":
    main()
