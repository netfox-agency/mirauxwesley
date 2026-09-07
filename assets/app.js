/* =========================================================================
   WM Couverture · interactions
   Aucune dépendance. Tout est désactivable via prefers-reduced-motion.
   ========================================================================= */
(function () {
  'use strict';

  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------------------------------------------------------- année ---- */
  var y = $('#year'); if (y) y.textContent = new Date().getFullYear();
  var fp = $('#f_page'); if (fp) fp.value = location.href;

  /* ---------------------------------------------------------- hero ----- */
  // Les mots du h1 montent un par un.
  var h1 = $('.hero__h1');
  if (h1) {
    $$('.w', h1).forEach(function (w, i) {
      w.style.transitionDelay = (0.06 + i * 0.055) + 's';
    });
    requestAnimationFrame(function () {
      setTimeout(function () { h1.classList.add('go'); }, 60);
    });
  }

  /* ---------------------------------------------------------- reveal --- */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -9% 0px', threshold: 0.08 });
  $$('.reveal').forEach(function (el) { io.observe(el); });

  /* ---------------------------------------------------------- compteurs  */
  var cio = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      cio.unobserve(e.target);
      var el = e.target, to = parseInt(el.getAttribute('data-count'), 10) || 0;
      if (reduced) { el.textContent = to; return; }
      var t0 = null, dur = 1100;
      (function step(t) {
        if (!t0) t0 = t;
        var p = Math.min((t - t0) / dur, 1);
        el.textContent = Math.round(to * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      })(performance.now());
    });
  }, { threshold: 0.6 });
  $$('[data-count]').forEach(function (el) { cio.observe(el); });

  /* ---------------------------------------------------------- nav ------ */
  var nav = $('#nav'), bar = $('.progress span'), callbar = $('#callbar');
  var doc = document.documentElement;
  function onScroll() {
    var sy = window.scrollY || doc.scrollTop;
    nav.classList.toggle('scrolled', sy > 24);
    if (bar) {
      var max = doc.scrollHeight - window.innerHeight;
      bar.style.width = (max > 0 ? (sy / max) * 100 : 0) + '%';
    }
    if (callbar) callbar.classList.toggle('show', sy > 520);
  }
  var ticking = false;
  addEventListener('scroll', function () {
    if (ticking) return; ticking = true;
    requestAnimationFrame(function () { onScroll(); ticking = false; });
  }, { passive: true });
  onScroll();


  /* ---------------------------------------------------------- menus ---- */
  // Survol sur les appareils qui pointent, clic sur ceux qui touchent.
  // Le focus clavier ouvre aussi, pour que Tab atteigne les liens.
  var canHover = matchMedia('(hover:hover)').matches;
  $$('.drop').forEach(function (d) {
    var btn = $('.drop__btn', d);
    if (!btn) return;
    function set(open) {
      d.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', String(open));
    }
    function closeOthers() {
      $$('.drop').forEach(function (o) {
        if (o !== d) { o.classList.remove('open'); $('.drop__btn', o).setAttribute('aria-expanded', 'false'); }
      });
    }
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (canHover) { closeOthers(); set(true); return; }
      var was = d.classList.contains('open');
      closeOthers(); set(!was);
    });
    if (canHover) {
      d.addEventListener('mouseenter', function () { closeOthers(); set(true); });
      d.addEventListener('mouseleave', function () { set(false); });
    }
    d.addEventListener('focusin', function () { closeOthers(); set(true); });
    d.addEventListener('focusout', function () {
      setTimeout(function () { if (!d.contains(document.activeElement)) set(false); }, 0);
    });
  });
  document.addEventListener('click', function () {
    $$('.drop').forEach(function (o) {
      o.classList.remove('open');
      $('.drop__btn', o).setAttribute('aria-expanded', 'false');
    });
  });
  addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    $$('.drop.open').forEach(function (o) {
      o.classList.remove('open');
      var b = $('.drop__btn', o); b.setAttribute('aria-expanded', 'false'); b.focus();
    });
  });

  /* ---------------------------------------------------------- drawer --- */
  var burger = $('#burger'), drawer = $('#drawer');
  function setDrawer(open) {
    burger.setAttribute('aria-expanded', String(open));
    drawer.hidden = !open;
    // le tiroir défile tout seul : on bloque la page derrière pour éviter
    // que le doigt entraîne le fond au lieu du menu
    document.body.classList.toggle('lock', open);
    burger.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
    if (open) drawer.scrollTop = 0;
  }
  burger.addEventListener('click', function () {
    setDrawer(burger.getAttribute('aria-expanded') !== 'true');
  });
  drawer.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') setDrawer(false);
  });
  addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !drawer.hidden) setDrawer(false);
  });

  /* ---------------------------------------------------------- avant/après */
  var frame = $('#baFrame'), after = $('#baAfter'), handle = $('#baHandle');
  if (frame && after && handle) {
    var dragging = false;
    function setPos(pct) {
      pct = Math.max(0, Math.min(100, pct));
      after.style.clipPath = 'inset(0 0 0 ' + pct + '%)';
      handle.style.left = pct + '%';
      handle.setAttribute('aria-valuenow', Math.round(pct));
    }
    function fromEvent(e) {
      var r = frame.getBoundingClientRect();
      var x = (e.touches ? e.touches[0].clientX : e.clientX) - r.left;
      setPos((x / r.width) * 100);
    }
    frame.addEventListener('pointerdown', function (e) {
      dragging = true; frame.setPointerCapture(e.pointerId); fromEvent(e);
    });
    frame.addEventListener('pointermove', function (e) { if (dragging) fromEvent(e); });
    ['pointerup', 'pointercancel'].forEach(function (t) {
      frame.addEventListener(t, function () { dragging = false; });
    });
    handle.addEventListener('keydown', function (e) {
      var cur = parseFloat(handle.getAttribute('aria-valuenow')) || 50, step = e.shiftKey ? 10 : 4;
      if (e.key === 'ArrowLeft')  { setPos(cur - step); e.preventDefault(); }
      if (e.key === 'ArrowRight') { setPos(cur + step); e.preventDefault(); }
      if (e.key === 'Home')       { setPos(0);  e.preventDefault(); }
      if (e.key === 'End')        { setPos(100); e.preventDefault(); }
    });
    // Petit geste d'invitation quand la section entre à l'écran.
    if (!reduced) {
      var bio = new IntersectionObserver(function (en) {
        en.forEach(function (e) {
          if (!e.isIntersecting) return;
          bio.unobserve(e.target);
          var seq = [50, 62, 38, 50], i = 0;
          after.style.transition = handle.style.transition = 'clip-path .8s cubic-bezier(.2,.7,.25,1), left .8s cubic-bezier(.2,.7,.25,1)';
          var iv = setInterval(function () {
            setPos(seq[++i]);
            if (i >= seq.length - 1) {
              clearInterval(iv);
              setTimeout(function () { after.style.transition = handle.style.transition = ''; }, 900);
            }
          }, 620);
        });
      }, { threshold: 0.45 });
      bio.observe(frame);
    }
  }

  /* ---------------------------------------------------------- avis ----- */
  var rail = $('#avisRail');
  if (rail) {
    function slide(dir) {
      var card = rail.querySelector('.avis__c');
      var step = card ? card.getBoundingClientRect().width + 18 : 320;
      rail.scrollBy({ left: dir * step, behavior: reduced ? 'auto' : 'smooth' });
    }
    $('#avisPrev').addEventListener('click', function () { slide(-1); });
    $('#avisNext').addEventListener('click', function () { slide(1); });
  }

  /* ---------------------------------------------------------- lightbox - */
  var items = $$('.gal__i'), lb = $('#lb'), lbImg = $('#lbImg'), lbCap = $('#lbCap');
  var idx = 0, lastFocus = null;

  function show(i) {
    idx = (i + items.length) % items.length;
    var b = items[idx];
    lbImg.src = b.getAttribute('data-src');
    lbImg.alt = b.querySelector('img').alt;
    lbCap.textContent = b.getAttribute('data-cap') || '';
  }
  function openLb(i) {
    lastFocus = document.activeElement;
    show(i); lb.hidden = false; document.body.classList.add('lock');
    $('#lbClose').focus();
  }
  function closeLb() {
    lb.hidden = true; document.body.classList.remove('lock');
    if (lastFocus) lastFocus.focus();
  }
  items.forEach(function (b, i) { b.addEventListener('click', function () { openLb(i); }); });
  if (lb) {
    $('#lbClose').addEventListener('click', closeLb);
    $('#lbPrev').addEventListener('click', function () { show(idx - 1); });
    $('#lbNext').addEventListener('click', function () { show(idx + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lb__fig')) closeLb(); });
    addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') closeLb();
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
  }

  /* ---------------------------------------------------------- formulaire */
  var form = $('#devisForm'), msg = $('#formMsg');
  if (form) {
    var started = false;
    form.addEventListener('input', function () {
      if (started) return; started = true;
      (window.dataLayer = window.dataLayer || []).push({ event: 'form_start' });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      msg.className = 'form__msg'; msg.textContent = '';

      var bad = null;
      ['#f_nom', '#f_tel', '#f_ville'].forEach(function (s) {
        var el = $(s), ok = el.value.trim().length > 1;
        if (s === '#f_tel') ok = el.value.replace(/[^0-9+]/g, '').length >= 9;
        el.classList.toggle('err', !ok);
        if (!ok && !bad) bad = el;
      });
      if (bad) {
        msg.className = 'form__msg ko';
        msg.textContent = 'Merci de renseigner votre nom, votre téléphone et votre commune.';
        bad.focus();
        return;
      }

      var key = form.querySelector('[name="access_key"]').value;
      if (key.indexOf('REMPLACER') === 0) {
        msg.className = 'form__msg ko';
        msg.textContent = 'Formulaire en cours de configuration. Appelez le 06 24 59 26 77.';
        return;
      }

      var btn = form.querySelector('button[type="submit"]');
      btn.classList.add('is-loading'); btn.disabled = true;

      // Web3Forms : FormData obligatoire (un envoi JSON déclenche un preflight refusé).
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          btn.classList.remove('is-loading'); btn.disabled = false;
          if (d && d.success) {
            form.reset();
            msg.className = 'form__msg ok';
            msg.textContent = 'Message bien reçu. Nous vous rappelons rapidement.';
            (window.dataLayer = window.dataLayer || []).push({ event: 'generate_lead' });
          } else {
            msg.className = 'form__msg ko';
            msg.textContent = "L'envoi a échoué. Appelez-nous au 06 24 59 26 77.";
          }
        })
        .catch(function () {
          btn.classList.remove('is-loading'); btn.disabled = false;
          msg.className = 'form__msg ko';
          msg.textContent = "L'envoi a échoué. Appelez-nous au 06 24 59 26 77.";
        });
    });
  }


  /* ---------------------------------------------------------- calcul --- */
  // Surface de rampant = emprise au sol x coefficient de pente.
  // Aucun prix : nous n'en inventons pas.
  var calc = $('#calc');
  if (calc) {
    var out = $('#calcOut');
    function compute() {
      var l = parseFloat($('#c_l').value), w = parseFloat($('#c_w').value);
      var k = parseFloat((calc.querySelector('[name="pente"]:checked') || {}).value || 1.15);
      var u = parseFloat((calc.querySelector('[name="mat"]:checked') || {}).value || 13);
      if (!(l > 0 && w > 0)) { out.classList.remove('on'); return; }
      var sol = l * w, ramp = sol * k;
      var pieces = Math.round(ramp * u / 10) * 10;
      out.classList.add('on');
      out.innerHTML =
        '<b>' + ramp.toFixed(0) + ' m² de rampant</b>' +
        '<span>Pour ' + sol.toFixed(0) + ' m² au sol. Soit environ ' +
        pieces.toLocaleString('fr-FR') + ' éléments de couverture à poser. ' +
        'Les débords, lucarnes et noues ne sont pas comptés : ils ajoutent, ils n\'enlèvent jamais.</span>';
    }
    calc.addEventListener('input', compute);
    calc.addEventListener('change', compute);
    calc.addEventListener('submit', function (e) { e.preventDefault(); compute(); });
  }

  /* ---------------------------------------------------------- tracking - */
  $$('[data-track="call"]').forEach(function (a) {
    a.addEventListener('click', function () {
      (window.dataLayer = window.dataLayer || []).push({ event: 'phone_call' });
    });
  });

})();
