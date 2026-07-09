/* =====================================================================
   MARIDAV CI — Header partagé (barre desktop + tiroir mobile)
   Autonome, vanilla, indépendant de Bootstrap (le site tourne en BS4 JS).
   Chargé en defer par chaque page via le markup du <header>.
   Gère : tiroir latéral mobile, dropdowns desktop (clic + survol),
   lien actif selon la page courante, verrou de scroll anti-saut,
   ligne de progression de scroll.
   ===================================================================== */
(function () {
  if (window.__maridavHeaderInit) return;        // anti double-init
  window.__maridavHeaderInit = true;

  function init() {
    var drawer   = document.getElementById('mobileDrawer');
    var backdrop = document.getElementById('drawerBackdrop');
    var toggle   = document.getElementById('drawerToggle');

    /* ---------- Tiroir latéral mobile ---------- */
    if (drawer && backdrop && toggle) {
      var scrollY = 0;
      var open = function () {
        scrollY = window.scrollY || document.documentElement.scrollTop || 0;
        drawer.classList.add('is-open');
        backdrop.classList.add('is-open');
        // Verrou de scroll : on fige le body à sa position courante.
        // Empêche le "saut" du menu et le défilement de la page derrière
        // (écrans mobiles hauts, barre d'adresse dynamique).
        document.body.style.top = (-scrollY) + 'px';
        document.body.classList.add('drawer-open');
        drawer.setAttribute('aria-hidden', 'false');
        toggle.setAttribute('aria-expanded', 'true');
      };
      var close = function () {
        drawer.classList.remove('is-open');
        backdrop.classList.remove('is-open');
        document.body.classList.remove('drawer-open');
        document.body.style.top = '';
        window.scrollTo(0, scrollY);               // on restaure la position
        drawer.setAttribute('aria-hidden', 'true');
        toggle.setAttribute('aria-expanded', 'false');
      };
      toggle.addEventListener('click', open);
      backdrop.addEventListener('click', close);
      drawer.querySelectorAll('[data-drawer-close]').forEach(function (el) {
        el.addEventListener('click', close);
      });
      drawer.querySelectorAll('a[href]').forEach(function (a) {
        a.addEventListener('click', close);
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' || e.keyCode === 27) close();
      });
      window.addEventListener('resize', function () {
        if (window.innerWidth >= 992) close();
      });
      // Accordéons Solutions / Ressources dans le tiroir
      drawer.querySelectorAll('.md-acc').forEach(function (b) {
        b.addEventListener('click', function () {
          var isOpen = b.classList.toggle('open');
          b.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
      });
    }

    /* ---------- Dropdowns desktop (JS maison) ---------- */
    var dds = [].slice.call(document.querySelectorAll('.navbar-premium .nav-item.dropdown'));
    var closeAll = function (except) {
      dds.forEach(function (o) {
        if (o === except) return;
        var m = o.querySelector('.dropdown-menu');
        var b = o.querySelector('.dropdown-toggle');
        if (m) m.classList.remove('show');
        if (b) b.setAttribute('aria-expanded', 'false');
      });
    };
    dds.forEach(function (item) {
      var btn  = item.querySelector('.dropdown-toggle');
      var menu = item.querySelector('.dropdown-menu');
      if (!btn || !menu) return;
      var openDd  = function () { menu.classList.add('show');    btn.setAttribute('aria-expanded', 'true'); };
      var closeDd = function () { menu.classList.remove('show'); btn.setAttribute('aria-expanded', 'false'); };
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var shown = menu.classList.contains('show');
        closeAll(item);
        if (shown) { closeDd(); } else { openDd(); }
      });
      // Survol desktop avec intention : on garde le menu ouvert le temps que le
      // curseur passe du bouton vers les items (anti-fermeture trop rapide).
      var hoverTimer = null;
      item.addEventListener('mouseenter', function () {
        if (window.innerWidth >= 992) { clearTimeout(hoverTimer); closeAll(item); openDd(); }
      });
      item.addEventListener('mouseleave', function () {
        if (window.innerWidth >= 992) {
          clearTimeout(hoverTimer);
          hoverTimer = setTimeout(closeDd, 320);   // délai de grâce
        }
      });
    });
    if (dds.length) {
      document.addEventListener('click', function (e) {
        var inside = dds.some(function (o) { return o.contains(e.target); });
        if (!inside) closeAll(null);
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' || e.keyCode === 27) closeAll(null);
      });
    }

    /* ---------- Lien actif selon la page courante ---------- */
    var here = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    if (here === '') here = 'index.html';
    var links = [].slice.call(document.querySelectorAll(
      '.navbar-premium a.nav-link-compact[href], .mobile-drawer .md-link[href], .mobile-drawer .md-sub a[href]'
    ));
    links.forEach(function (a) {
      var raw = (a.getAttribute('href') || '');
      var seg = raw.split('#')[0].split('?')[0];
      var file = (seg.split('/').pop() || 'index.html').toLowerCase();
      if (file === '') file = 'index.html';
      if (file === here) {
        a.classList.add('active');
        a.setAttribute('aria-current', 'page');
      }
    });

    /* ---------- Bouton « revenir en haut » (partagé sur toutes les pages) ---------- */
    // Créé s'il n'existe pas encore ; câblé dans tous les cas (double-câblage
    // inoffensif sur les pages qui gèrent déjà leur propre bouton).
    var st = document.querySelector('.scroll-top');
    if (!st) {
      st = document.createElement('button');
      st.type = 'button';
      st.className = 'scroll-top tran3s';
      st.setAttribute('aria-label', 'Revenir en haut');
      st.innerHTML = '<i class="fas fa-angle-up" aria-hidden="true"></i>';
      document.body.appendChild(st);
    }
    var toggleSt = function () {
      st.style.display = ((window.scrollY || document.documentElement.scrollTop) > 200) ? 'block' : 'none';
    };
    toggleSt();
    window.addEventListener('scroll', toggleSt, { passive: true });
    st.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    /* ---------- Ligne de progression de scroll ---------- */
    var sp = document.querySelector('.scroll-progress');
    if (sp) {
      var update = function () {
        var d = document.documentElement;
        var max = d.scrollHeight - d.clientHeight;
        var r = max > 0 ? (window.scrollY || d.scrollTop) / max : 0;
        sp.style.setProperty('--sp', (r < 0 ? 0 : r > 1 ? 1 : r).toFixed(3));
      };
      window.addEventListener('scroll', update, { passive: true });
      window.addEventListener('resize', update, { passive: true });
      update();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* ===== MARIDAV — OVERLAY FIN DE VERSION DE TEST (vitrine uniquement) =====
   Recouvre la vitrine avec un message invitant Maridav à activer son
   hébergement et à publier le site sur www.maridav.ci.
   Le CRM (/crm/) ne charge pas ce script : il n'est pas affecté.
   POUR DÉSACTIVER : supprimer ce bloc (de ce commentaire jusqu'au marqueur
   de fin) puis redéployer. Réversible sans autre modification.
   ======================================================================== */
(function () {
  'use strict';

  function build() {
    if (document.getElementById('mdv-test-overlay')) return;

    var style = document.createElement('style');
    style.id = 'mdv-test-overlay-style';
    style.textContent =
      '#mdv-test-overlay{position:fixed;inset:0;z-index:2147483000;display:flex;' +
      'align-items:center;justify-content:center;padding:6vw 5vw;' +
      'background:radial-gradient(120% 120% at 50% 0%,#12385c 0%,#0a1f36 55%,#06121f 100%);' +
      'color:#fff;text-align:center;overflow:auto;' +
      "font-family:'Segoe UI',system-ui,-apple-system,Arial,sans-serif;}" +
      '#mdv-test-overlay .mdv-card{max-width:640px;width:100%;}' +
      '#mdv-test-overlay .mdv-badge{display:inline-flex;align-items:center;gap:.55rem;' +
      'padding:.5rem 1.15rem;border:1px solid rgba(255,255,255,.28);border-radius:999px;' +
      'font-size:.9rem;letter-spacing:.14em;text-transform:uppercase;' +
      'color:rgba(255,255,255,.82);margin-bottom:1.8rem;}' +
      '#mdv-test-overlay .mdv-badge .dot{width:.7rem;height:.7rem;border-radius:50%;' +
      'background:#3ddc97;box-shadow:0 0 0 4px rgba(61,220,151,.2);}' +
      '#mdv-test-overlay h1{font-family:Fraunces,Georgia,"Times New Roman",serif;' +
      'font-weight:600;line-height:1.12;margin:0 0 1.15rem;' +
      'font-size:clamp(2rem,5vw,3.1rem);}' +
      '#mdv-test-overlay p{font-size:clamp(1.12rem,2.2vw,1.3rem);line-height:1.6;' +
      'color:rgba(255,255,255,.86);margin:0 auto 1.9rem;max-width:34rem;}' +
      '#mdv-test-overlay .mdv-domain{display:inline-block;font-weight:700;' +
      'font-size:clamp(1.3rem,3vw,1.8rem);letter-spacing:.01em;color:#ffd479;' +
      'padding:.6rem 1.4rem;border:1px solid rgba(255,212,121,.4);border-radius:14px;' +
      'background:rgba(255,212,121,.08);}' +
      '#mdv-test-overlay .mdv-foot{margin-top:2.2rem;font-size:.92rem;' +
      'color:rgba(255,255,255,.55);letter-spacing:.02em;}' +
      'html.mdv-lock,body.mdv-lock{overflow:hidden !important;}';
    document.head.appendChild(style);

    var ov = document.createElement('div');
    ov.id = 'mdv-test-overlay';
    ov.setAttribute('role', 'dialog');
    ov.setAttribute('aria-modal', 'true');
    ov.setAttribute('aria-label', 'Version de test terminée');
    ov.innerHTML =
      '<div class="mdv-card">' +
        '<span class="mdv-badge"><span class="dot"></span>Version de test terminée</span>' +
        '<h1>Le site est prêt à être mis en ligne.</h1>' +
        '<p>Veuillez activer votre hébergement et publier votre site web sur&nbsp;:</p>' +
        '<span class="mdv-domain">www.maridav.ci</span>' +
        '<div class="mdv-foot">Maridav&nbsp;CI</div>' +
      '</div>';

    (document.body || document.documentElement).appendChild(ov);
    document.documentElement.classList.add('mdv-lock');
    if (document.body) document.body.classList.add('mdv-lock');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
/* ===== FIN OVERLAY FIN DE VERSION DE TEST ===== */
