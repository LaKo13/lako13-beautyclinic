/*
 * Google Ads conversion click-tracking with Consent Mode v2 and a
 * lightweight consent banner (EN/DE/ES, chosen from <html lang>).
 *
 * Consent: every consent type defaults to 'denied'. Only after the visitor
 * clicks Accept (stored in localStorage, re-applied on later page loads)
 * is consent updated to 'granted'. On Reject the defaults stay 'denied' and
 * Google only receives cookieless, consent-denied pings.
 *
 * Must be loaded synchronously in <head> so the consent defaults run
 * before the Google tag loads.
 */
(function () {
  // Google Ads conversion IDs (account ITV en Claro 988-964-7384)
  var GADS_ID = 'AW-18364793342';
  var GADS_LABELS = { phone: 'KdoqCN3dsaodEP6DgrVE', email: 'bKBNCKOhvqodEP6DgrVE', form: 'eLsdCKbcsaodEP6DgrVE' };
  var CONSENT_KEY = 'bcm_consent'; // 'granted' | 'denied'

  // One dataLayer and one gtag function per page.
  window.dataLayer = window.dataLayer || [];
  var gtag = window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  function readConsent() {
    try { return window.localStorage.getItem(CONSENT_KEY); } catch (err) { return null; }
  }
  function storeConsent(value) {
    try { window.localStorage.setItem(CONSENT_KEY, value); } catch (err) {}
  }
  function grantConsent() {
    gtag('consent', 'update', {
      ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted',
      analytics_storage: 'granted'
    });
  }

  // Consent Mode v2 defaults: denied until the visitor accepts.
  gtag('consent', 'default', {
    ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
    analytics_storage: 'denied', wait_for_update: 500
  });
  gtag('set', 'ads_data_redaction', true);
  gtag('set', 'url_passthrough', true);

  // Re-apply a previous Accept before the Google tag loads.
  var stored = readConsent();
  if (stored === 'granted') grantConsent();

  // Google tag
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GADS_ID;
  var first = document.getElementsByTagName('script')[0];
  first.parentNode.insertBefore(s, first);
  gtag('js', new Date());
  gtag('config', GADS_ID);

  // Call trackConversion('form') only after a confirmed successful form submit.
  function trackConversion(channel) {
    var label = GADS_LABELS[channel];
    if (label && typeof gtag === 'function') {
      gtag('event', 'conversion', { send_to: GADS_ID + '/' + label });
    }
  }
  window.trackConversion = trackConversion;

  // tel: and mailto: clicks. No preventDefault: gtag sends via beacon.
  document.addEventListener('click', function (e) {
    var target = e.target.closest('a[href]');
    if (!target) return;
    var href = target.getAttribute('href');
    if (href.indexOf('tel:') === 0) trackConversion('phone');
    else if (href.indexOf('mailto:') === 0) trackConversion('email');
  });

  // Consent banner, shown until the visitor accepts or rejects.
  if (stored === 'granted' || stored === 'denied') return;

  var TEXTS = {
    en: {
      text: 'We use cookies from Google to measure whether visits from our ads lead to calls or emails. You can accept or reject them.',
      more: 'Privacy policy', privacy: 'privacy.html', accept: 'Accept', reject: 'Reject'
    },
    de: {
      text: 'Wir verwenden Cookies von Google, um zu messen, ob Besuche über unsere Anzeigen zu Anrufen oder E-Mails führen. Sie können zustimmen oder ablehnen.',
      more: 'Datenschutzerklärung', privacy: 'datenschutz.html', accept: 'Akzeptieren', reject: 'Ablehnen'
    },
    es: {
      text: 'Utilizamos cookies de Google para medir si las visitas desde nuestros anuncios generan llamadas o correos electrónicos. Puede aceptarlas o rechazarlas.',
      more: 'Política de privacidad', privacy: 'privacy.html', accept: 'Aceptar', reject: 'Rechazar'
    }
  };

  function showBanner() {
    var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
    var t = TEXTS[lang] || TEXTS.en;

    var banner = document.createElement('div');
    banner.className = 'consent-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-live', 'polite');
    banner.setAttribute('aria-label', t.more);

    var p = document.createElement('p');
    p.className = 'consent-banner-text';
    p.appendChild(document.createTextNode(t.text + ' '));
    var link = document.createElement('a');
    link.href = t.privacy;
    link.textContent = t.more;
    p.appendChild(link);
    banner.appendChild(p);

    var actions = document.createElement('div');
    actions.className = 'consent-banner-actions';
    function addButton(label, value) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-mod btn-small';
      btn.textContent = label;
      btn.addEventListener('click', function () {
        storeConsent(value);
        if (value === 'granted') grantConsent();
        banner.parentNode.removeChild(banner);
      });
      actions.appendChild(btn);
    }
    addButton(t.reject, 'denied');
    addButton(t.accept, 'granted');
    banner.appendChild(actions);

    document.body.appendChild(banner);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', showBanner);
  else showBanner();
})();
