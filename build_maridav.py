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
import sys
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "products.json"

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


def main():
    check = "--check" in sys.argv
    data = json.loads(DATA.read_text(encoding="utf-8"))
    products = list(iter_products(data))
    written = 0
    for p in products:
        html_out = render_page(p)
        target = ROOT / p["url"]
        if check:
            print(f"  [check] {p['url']:48s} {len(html_out):6d} o")
        else:
            target.write_text(html_out, encoding="utf-8")
            print(f"  écrit  {p['url']:48s} {len(html_out):6d} o")
        written += 1
    print(f"\n{written} page(s) produit générée(s).")


if __name__ == "__main__":
    main()
