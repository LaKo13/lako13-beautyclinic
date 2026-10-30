/*
 * Cookie consent (EN/DE/ES, chosen from <html lang>) with Google Consent Mode v2.
 *
 * Categories:
 *   necessary  – always on (stores this consent choice in localStorage)
 *   marketing  – Google Ads conversion measurement (ad_storage, ad_user_data,
 *                ad_personalization, analytics_storage)
 *   media      – external media (Google Maps embed, click-to-load)
 *
 * The choice is stored as JSON in localStorage.bcm_consent:
 *   { v: 1, ts: <ms since epoch>, marketing: bool, media: bool }
 * It is ignored (and the banner shown again) when the version changes or
 * after 12 months.
 *
 * Must be loaded synchronously in <head> BEFORE js/conversion-tracking.js so
 * the consent defaults (and a stored grant) are set before the Google tag loads.
 *
 * Any element with [data-consent-open] (footer "Cookie settings" link) reopens
 * the settings panel, so consent can be withdrawn at any time.
 */
(function () {
  var CONSENT_KEY = 'bcm_consent';
  var CONSENT_VERSION = 1;
  var MAX_AGE_MS = 365 * 24 * 60 * 60 * 1000; // 12 months

  // One dataLayer and one gtag function per page.
  window.dataLayer = window.dataLayer || [];
  var gtag = window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  function readConsent() {
    var raw;
    try { raw = window.localStorage.getItem(CONSENT_KEY); } catch (err) { return null; }
    if (!raw) return null;
    var c;
    try { c = JSON.parse(raw); } catch (err) { return null; }
    if (!c || c.v !== CONSENT_VERSION || typeof c.ts !== 'number') return null;
    if (Date.now() - c.ts > MAX_AGE_MS || c.ts > Date.now()) return null;
    return { v: c.v, ts: c.ts, marketing: c.marketing === true, media: c.media === true };
  }
  function storeConsent(c) {
    try { window.localStorage.setItem(CONSENT_KEY, JSON.stringify(c)); } catch (err) {}
  }
  function marketingConsent(value) {
    gtag('consent', 'update', {
      ad_storage: value, ad_user_data: value, ad_personalization: value,
      analytics_storage: value
    });
  }

  // Google Ads cookies are first-party (_gcl_*); remove them on withdrawal.
  function clearGoogleCookies() {
    var host = window.location.hostname;
    var domains = ['', host, '.' + host.replace(/^www\./, '')];
    document.cookie.split(';').forEach(function (part) {
      var name = part.split('=')[0].replace(/^\s+|\s+$/g, '');
      if (name.indexOf('_gcl') !== 0 && name.indexOf('_ga') !== 0) return;
      domains.forEach(function (d) {
        document.cookie = name + '=; Max-Age=0; path=/' + (d ? '; domain=' + d : '');
      });
    });
  }

  // Consent Mode v2 defaults: denied until the visitor opts in to marketing.
  gtag('consent', 'default', {
    ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
    analytics_storage: 'denied', wait_for_update: 500
  });
  gtag('set', 'ads_data_redaction', true);
  gtag('set', 'url_passthrough', true);

  // Re-apply a stored marketing grant before the Google tag loads.
  var current = readConsent();
  if (current && current.marketing) marketingConsent('granted');

  // ---- External media (Google Maps click-to-load) ----

  function loadMedia() {
    var frames = document.querySelectorAll('iframe[data-consent-src]');
    for (var i = 0; i < frames.length; i++) {
      if (frames[i].getAttribute('src') !== frames[i].getAttribute('data-consent-src')) {
        frames[i].setAttribute('src', frames[i].getAttribute('data-consent-src'));
      }
    }
    var holders = document.querySelectorAll('[data-consent-placeholder]');
    for (var j = 0; j < holders.length; j++) holders[j].hidden = true;
  }
  function unloadMedia() {
    var frames = document.querySelectorAll('iframe[data-consent-src]');
    for (var i = 0; i < frames.length; i++) {
      if (frames[i].hasAttribute('src')) frames[i].removeAttribute('src');
    }
    var holders = document.querySelectorAll('[data-consent-placeholder]');
    for (var j = 0; j < holders.length; j++) holders[j].hidden = false;
  }

  // ---- Saving a choice ----

  function saveConsent(marketing, media) {
    var previous = current;
    current = { v: CONSENT_VERSION, ts: Date.now(), marketing: !!marketing, media: !!media };
    storeConsent(current);

    if (current.marketing && !(previous && previous.marketing)) {
      marketingConsent('granted');
    } else if (!current.marketing && previous && previous.marketing) {
      marketingConsent('denied');
      clearGoogleCookies();
    }

    if (current.media) loadMedia();
    else unloadMedia();
  }

  // ---- Banner and settings panel ----

  var TEXTS = {
    en: {
      title: 'Cookie settings',
      text: 'We use Google cookies to measure whether visits from our ads lead to calls or emails, and Google Maps to show our location. Both are only used with your consent. You can change your choice at any time via "Cookie settings" at the bottom of every page.',
      more: 'Privacy policy', privacy: 'privacy.html#cookies',
      accept: 'Accept all', reject: 'Reject all', settings: 'Settings', save: 'Save choices',
      necessary: 'Necessary', necessaryDesc: 'Stores your cookie choice in your browser. Always active.',
      marketing: 'Marketing / measurement (Google Ads)', marketingDesc: 'Measures whether visits from our Google ads lead to calls, emails or enquiries. Sets Google Ads cookies.',
      media: 'External media (Google Maps)', mediaDesc: 'Shows the embedded Google Map. Loading it sends data such as your IP address to Google.'
    },
    de: {
      title: 'Cookie-Einstellungen',
      text: 'Wir verwenden Cookies von Google, um zu messen, ob Besuche über unsere Anzeigen zu Anrufen oder E-Mails führen, und Google Maps, um unseren Standort anzuzeigen. Beides nutzen wir nur mit Ihrer Einwilligung. Sie können Ihre Auswahl jederzeit über „Cookie-Einstellungen“ unten auf jeder Seite ändern.',
      more: 'Datenschutzerklärung', privacy: 'datenschutz.html#cookies',
      accept: 'Alle akzeptieren', reject: 'Alle ablehnen', settings: 'Einstellungen', save: 'Auswahl speichern',
      necessary: 'Notwendig', necessaryDesc: 'Speichert Ihre Cookie-Auswahl in Ihrem Browser. Immer aktiv.',
      marketing: 'Marketing / Messung (Google Ads)', marketingDesc: 'Misst, ob Besuche über unsere Google-Anzeigen zu Anrufen, E-Mails oder Anfragen führen. Setzt Google-Ads-Cookies.',
      media: 'Externe Medien (Google Maps)', mediaDesc: 'Zeigt die eingebettete Google-Karte. Beim Laden werden Daten wie Ihre IP-Adresse an Google übermittelt.'
    },
    es: {
      title: 'Configuración de cookies',
      text: 'Utilizamos cookies de Google para medir si las visitas desde nuestros anuncios generan llamadas o correos electrónicos, y Google Maps para mostrar nuestra ubicación. Solo los usamos con su consentimiento. Puede cambiar su elección en cualquier momento en «Configuración de cookies», al pie de cada página.',
      more: 'Política de privacidad', privacy: 'privacidad.html#cookies',
      accept: 'Aceptar todo', reject: 'Rechazar todo', settings: 'Configuración', save: 'Guardar selección',
      necessary: 'Necesarias', necessaryDesc: 'Guardan su elección de cookies en su navegador. Siempre activas.',
      marketing: 'Marketing / medición (Google Ads)', marketingDesc: 'Miden si las visitas desde nuestros anuncios de Google generan llamadas, correos o consultas. Instalan cookies de Google Ads.',
      media: 'Contenido externo (Google Maps)', mediaDesc: 'Muestra el mapa de Google integrado. Al cargarlo se envían a Google datos como su dirección IP.'
    }
  };

  var banner = null;

  function texts() {
    var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
    return TEXTS[lang] || TEXTS.en;
  }

  function closeBanner() {
    if (banner && banner.parentNode) banner.parentNode.removeChild(banner);
    banner = null;
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function addCategory(list, id, label, desc, checked, locked) {
    var item = el('div', 'consent-category');
    var lbl = el('label', 'consent-category-label');
    var box = document.createElement('input');
    box.type = 'checkbox';
    box.id = 'consent-' + id;
    box.checked = checked;
    if (locked) box.disabled = true;
    lbl.setAttribute('for', box.id);
    lbl.appendChild(box);
    lbl.appendChild(document.createTextNode(' ' + label));
    item.appendChild(lbl);
    item.appendChild(el('p', 'consent-category-desc', desc));
    list.appendChild(item);
    return box;
  }

  function showBanner(withSettings) {
    closeBanner();
    var t = texts();

    banner = el('div', 'consent-banner');
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', t.title);

    var p = el('p', 'consent-banner-text', t.text + ' ');
    var link = el('a', null, t.more);
    link.href = t.privacy;
    p.appendChild(link);
    banner.appendChild(p);

    // Settings layer (hidden until "Settings" is clicked).
    var panel = el('div', 'consent-settings');
    panel.id = 'consent-settings';
    panel.hidden = !withSettings;
    addCategory(panel, 'necessary', t.necessary, t.necessaryDesc, true, true);
    var marketingBox = addCategory(panel, 'marketing', t.marketing, t.marketingDesc, !!(current && current.marketing), false);
    var mediaBox = addCategory(panel, 'media', t.media, t.mediaDesc, !!(current && current.media), false);
    banner.appendChild(panel);

    // Reject all, Settings / Save choices and Accept all share one style and row.
    var actions = el('div', 'consent-banner-actions');
    function addButton(label, onClick) {
      var btn = el('button', 'btn btn-mod btn-small', label);
      btn.type = 'button';
      btn.addEventListener('click', onClick);
      actions.appendChild(btn);
      return btn;
    }
    addButton(t.reject, function () { saveConsent(false, false); closeBanner(); });
    var settingsBtn = addButton(withSettings ? t.save : t.settings, function () {
      if (panel.hidden) {
        panel.hidden = false;
        settingsBtn.textContent = t.save;
        settingsBtn.setAttribute('aria-expanded', 'true');
        marketingBox.focus();
      } else {
        saveConsent(marketingBox.checked, mediaBox.checked);
        closeBanner();
      }
    });
    settingsBtn.setAttribute('aria-controls', panel.id);
    settingsBtn.setAttribute('aria-expanded', withSettings ? 'true' : 'false');
    addButton(t.accept, function () { saveConsent(true, true); closeBanner(); });
    banner.appendChild(actions);

    document.body.appendChild(banner);
  }

  window.bcmConsent = {
    get: function () { return current; },
    open: function () { showBanner(true); }
  };

  // Footer "Cookie settings" links and map "Load map" buttons.
  document.addEventListener('click', function (e) {
    var opener = e.target.closest && e.target.closest('[data-consent-open]');
    if (opener) {
      e.preventDefault();
      showBanner(true);
      return;
    }
    var loader = e.target.closest && e.target.closest('[data-consent-load-media]');
    if (loader) {
      e.preventDefault();
      // Loading the map is consent for external media only; marketing keeps
      // its current state (denied if not yet chosen).
      var bannerOpen = !!banner;
      saveConsent(current ? current.marketing : false, true);
      if (bannerOpen) showBanner(false);
    }
  });

  function init() {
    if (current && current.media) loadMedia();
    if (!current) showBanner(false);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
