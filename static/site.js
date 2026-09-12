/* DNNR Tech — shared behavior for dnnr.us (generated pages include this with `defer`). */
(function () {
  'use strict';

  // Sticky header hairline
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 4); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Open <details> targeted by the URL hash (privacy app sections)
  function openHashDetails() {
    var el = location.hash && document.getElementById(location.hash.slice(1));
    if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView(); }
  }
  openHashDetails();
  window.addEventListener('hashchange', openHashDetails);

  // App filter chips (/apps)
  var chips = document.querySelectorAll('.chip[data-filter]');
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      var f = c.dataset.filter;
      chips.forEach(function (x) { x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
      document.querySelectorAll('.app-card').forEach(function (card) {
        card.hidden = f === 'ai' ? card.dataset.ai !== '1' : (f !== 'all' && card.dataset.cat !== f);
      });
    });
  });

  // ---------------- Contact ----------------
  // Same-origin endpoint on dnnr.us / preview hosts; the GitHub Pages mirror posts cross-origin.
  var host = location.hostname;
  var sameOrigin = /(^|\.)dnnr\.us$/.test(host) || /\.pages\.dev$/.test(host) || host === 'localhost' || host === '127.0.0.1';
  var ENDPOINT = sameOrigin ? '/api/contact' : 'https://dnnr.us/api/contact';
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var dialog = document.getElementById('contact-dialog');

  function setTopic(form, topic) {
    var sel = form.querySelector('[name="topic"]');
    if (sel && topic) {
      for (var i = 0; i < sel.options.length; i++) {
        if (sel.options[i].value === topic) { sel.selectedIndex = i; break; }
      }
    }
  }

  function resetForm(form) {
    form.reset();
    form.hidden = false;
    form.querySelectorAll('.field').forEach(function (f) { f.classList.remove('invalid'); var e = f.querySelector('.err'); if (e) e.textContent = ''; });
    var st = form.querySelector('.status'); if (st) st.textContent = '';
    var done = form.parentElement.querySelector('.form-done'); if (done) done.hidden = true;
    form.dataset.opened = String(Date.now());
  }

  document.addEventListener('click', function (ev) {
    var trigger = ev.target.closest('[data-contact]');
    if (!trigger || !dialog || typeof dialog.showModal !== 'function') return; // falls back to href="/contact"
    ev.preventDefault();
    var form = dialog.querySelector('form');
    resetForm(form);
    setTopic(form, trigger.dataset.topic);
    form.dataset.source = trigger.dataset.source || 'unknown';
    form.dataset.button = (trigger.dataset.label || trigger.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80);
    dialog.showModal();
    setTimeout(function () { var n = form.querySelector('[name="name"]'); if (n) n.focus(); }, 60);
  });

  if (dialog) {
    dialog.addEventListener('click', function (ev) { if (ev.target === dialog) dialog.close(); });
    dialog.querySelectorAll('[data-close]').forEach(function (b) { b.addEventListener('click', function () { dialog.close(); }); });
  }

  function fieldError(form, name, msg) {
    var input = form.querySelector('[name="' + name + '"]');
    var field = input && input.closest('.field');
    if (!field) return;
    field.classList.toggle('invalid', !!msg);
    var e = field.querySelector('.err'); if (e) e.textContent = msg || '';
  }

  // Note: form.name is the form's own name attribute, so read inputs by selector.
  function val(form, n) { var el = form.querySelector('[name="' + n + '"]'); return el ? el.value.trim() : ''; }

  function validate(form) {
    var ok = true;
    var name = val(form, 'name'), email = val(form, 'email'), message = val(form, 'message');
    fieldError(form, 'name', name ? '' : 'Please enter your name.'); ok = ok && !!name;
    var emailOk = EMAIL_RE.test(email);
    fieldError(form, 'email', emailOk ? '' : 'Please enter a valid email so we can reply.'); ok = ok && emailOk;
    var msgOk = message.length >= 10;
    fieldError(form, 'message', msgOk ? '' : 'Please tell us a little more (10+ characters).'); ok = ok && msgOk;
    return ok;
  }

  document.querySelectorAll('form.contact-form').forEach(function (form) {
    form.dataset.opened = String(Date.now());
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var status = form.querySelector('.status');
      status.textContent = '';
      if (!validate(form)) return;
      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      var label = btn.textContent; btn.textContent = 'Sending…';
      var payload = {
        name: val(form, 'name'),
        email: val(form, 'email'),
        company: val(form, 'company'),
        topic: val(form, 'topic'),
        message: val(form, 'message'),
        website: val(form, 'website'),
        source: form.dataset.source || 'unknown',
        button: form.dataset.button || '',
        page: location.pathname + location.search,
        host: location.host,
        elapsed_ms: Date.now() - Number(form.dataset.opened || Date.now())
      };
      fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, body: j }; }); })
        .then(function (res) {
          if (res.ok && res.body.ok) {
            form.hidden = true;
            var done = form.parentElement.querySelector('.form-done');
            if (done) done.hidden = false;
          } else {
            if (res.body.field) fieldError(form, res.body.field, res.body.error);
            status.textContent = res.body.error || 'Something went wrong. Please try again in a moment.';
          }
        })
        .catch(function () { status.textContent = 'Network error. Please check your connection and try again.'; })
        .finally(function () { btn.disabled = false; btn.textContent = label; });
    });
  });
})();
