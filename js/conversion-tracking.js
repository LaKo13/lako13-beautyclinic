/*
 * Google Ads conversion click-tracking (Consent Mode v2).
 *
 * Consent defaults, a stored marketing grant and the consent banner live in
 * js/consent.js, which must be loaded synchronously in <head> BEFORE this file
 * so they are set before the Google tag loads.
 */
(function () {
  // Google Ads conversion IDs (account ITV en Claro 988-964-7384)
  var GADS_ID = 'AW-18364793342';
  var GADS_LABELS = { phone: 'KdoqCN3dsaodEP6DgrVE', email: 'bKBNCKOhvqodEP6DgrVE', form: 'eLsdCKbcsaodEP6DgrVE' };

  // One dataLayer and one gtag function per page (normally created by consent.js).
  window.dataLayer = window.dataLayer || [];
  var gtag = window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

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
})();
