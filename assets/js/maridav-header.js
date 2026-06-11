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
      st.innerHTML = '<i class="fa fa-angle-up" aria-hidden="true"></i>';
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
