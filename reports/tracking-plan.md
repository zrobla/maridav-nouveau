# Plan de tracking — GA4 & Pixels

Propriétés & conteneurs

- GA4: `G-XXXXXXXXXX` (à définir) — dataLayer global
- Meta Pixel: `XXXXXXXXXX` — pageview + events
- TikTok Pixel: `XXXXXX` — pageview + events

Evenements (noms + paramètres)

- `lead_submit` — { name, phone, email, species, product, message }
- `whatsapp_click` — { href, page }
- `call_click` — { href, page }
- `pdf_download` — { file, product }
- `filter_use` — { q, list_id }
- `compare_open` — { products }
- `lead_open` — { page }

Implémentation

- Déclenchement par `assets/js/main.min.js` (listeners sur `tel:`, bouton WhatsApp, formulaire lead)
- Mapper vers GA4 via `gtag('event', ...)` ou Google Tag Manager (si disponible)
- Pixels Meta/TikTok paramétrés via Tag Manager pour reprendre les mêmes événements

Spécificités RGPD/CMP

- Consentement géré via CMP (mode basique: bannière + opt‑in)
- Ne pas collecter de données personnelles sans consentement explicite; anonymiser IP côté GA

Tests

- Vérifier la présence de `dataLayer` et l’émission des événements dans la console
- Scénarios: clic WhatsApp, clic Appel, envoi lead, téléchargement PDF, recherche dans listing

