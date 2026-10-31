# CLAUDE.md – Beauty Clinic off-limits rules

These rules apply to every Claude run in this repo.

## Medical copy
- Any health or treatment statement (indications, durations, risks, aftercare, results, credentials) needs Dr. Koerge's sign-off before merge.
- Never invent medical facts or statistics. Use only facts already on the live site or in the issue.

## Spanish health-advertising law
(RDL 1/2015 art. 80 and 80.7; Balearic Decreto 100/2010.) Do not use any of the following on new pages or in ad landing copy:
- Prescription-medicine or device brand names (e.g. Botox, Vistabel, Juvederm, Allergan, Profhilo, IBSA, Filorga, Lemon Bottle, Invisalign, Straumann, Nobel).
- Prices or the € sign.
- Free or offer incentives.
- "Safe", "painless", "guaranteed" or "permanent" claims.
- Testimonials or before/after images.

## HANSEATICUM
Never mention or link HANSEATICUM.

## NAP and hours
- Name, address, phone and opening hours must match the live site exactly.
- Beauty Clinic hours: Mon–Fri 09:30–16:00.

## Design
- Preserve the existing design and components.
- Add no new CSS frameworks and no inline style hacks.

## Tracking
- Keep the PostHog snippet (EU, cookieless, no session recording) and `contact_click` tracking intact on every page.
- Every page loads `js/consent.js` synchronously in `<head>` before `js/conversion-tracking.js` (Consent Mode v2 defaults denied; Google Ads only after Marketing consent). Keep that order and the footer "Cookie settings" / "Cookie-Einstellungen" / "Configuración de cookies" link (`data-consent-open`) on every page.
- Third-party embeds (e.g. Google Maps) must stay click-to-load: put the URL in `data-consent-src`, never `src`. List any new cookie or third-party service in the cookie section of privacy.html, datenschutz.html and privacidad.html.

## Workflow
- Work via PRs only. Never push to the default branch and never merge.
- Keep changes within the issue's scope. List side ideas in the PR body instead of doing them.
- Validate the sitemap and JSON-LD.
- Keep FAQ text identical to the FAQPage schema.
- Keep hreflang reciprocal.
- Grep for forbidden terms (brand names, €, HANSEATICUM, "safe", "painless", "guaranteed", "permanent") before pushing.
