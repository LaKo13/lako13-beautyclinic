# Beauty Clinic Mallorca

Static, bilingual clinic website at https://beautyclinicmallorca.com/.

Published from the root of `master` through GitHub Pages. No application server, Node package installation, external font service or frontend framework is required.

## Updating the site

- Edit English/German content in `scripts/content.py`.
- Edit shared templates and business data in `scripts/build_site.py`.
- Edit the visual system in `assets/site.css` and progressive enhancements in `assets/site.js`.
- Generate pages with `python3 scripts/build_site.py` and commit the generated HTML and sitemap with source changes.
- Run `python3 -m unittest discover -s tests -v` and `node --check assets/site.js`.
- Preview with `python3 -m http.server 8765 --bind 127.0.0.1`.

The GitHub Actions validation job checks generated-source consistency, all local page links and anchors, language alternatives, metadata, images, business schema, contact links and legacy redirects.

## Routes

English homepage: `/`. German homepage: `/index-de.html` (existing URL retained).

Each language has six treatment pages, a Dr. Erik Koerge profile, website privacy information and clinic contact information. German detail pages use `/de/`. Language controls preserve the current topic. `sitemap.xml` includes the 20 canonical pages and reciprocal language alternatives.

The old nested `/lako13-beautyclinic/` pages contain immediate HTML redirects to the appropriate current homepage, plus canonical and noindex metadata. They are not HTTP 301 redirects: GitHub Pages does not provide arbitrary server-side redirect configuration. HTTP and www normalization remain handled by the existing host.

## Contact, privacy and clinical copy

Consultations are requested by phone or email. Treatment pages prefill the email subject with the selected treatment. There is no fake booking form, automatic confirmation or unattended transmission of patient information.

Google Maps is not loaded until the visitor presses the explicit load button. No analytics tracker or browser storage is installed. If analytics is added, use the actual account configuration, update the privacy information, and implement the corresponding consent approach. Do not send medical or identifying details in analytics events.

The address and hours match the previously visible clinic contact details: Plaza Bendinat, Local B10, Calle Arquitecto Francisco Casas 17, 07181 Bendinat; Monday–Friday 09:30–18:00. Unverified floor-level claims have been removed.

The site retains the user-confirmed 20+ years of practitioner experience. No professional registration numbers, named qualifications, product availability promises, clinical review attribution or treatment outcome guarantees have been invented. The practitioner should review the treatment copy and supply verified credentials. Testimonials and before/after claims were omitted from the refreshed pages because their provenance and permission were not available; the previous version is recoverable in Git history.

The website privacy notice describes the actual website behavior. Full patient-record policies and formal legal/operator disclosures require the clinic's verified details. This is not a legal compliance certification.

## Testing on 11 September 2026

- 11 regression test groups, covering all 20 canonical pages, passed.
- Browser inspection of every canonical page at 320, 390, 768 and 1440 pixels: 80 combinations passed overflow, heading, loaded-image and deferred-map checks after correcting narrow-screen issues.
- Visual inspection of desktop/mobile homepages, treatment pages, German narrow-screen content, service cards and contact content.
- Interactive checks: mobile menu open/close, Escape and focus restoration, section navigation, same-topic language switching, keyboard FAQ controls, map consent/load and contact link destinations.
- Static JavaScript syntax and generated-file consistency checks passed.

Responsive viewport testing is not a substitute for testing every physical phone or browser engine. No email was sent, phone call placed, appointment submitted or analytics conversion fabricated during testing. No Lighthouse/Core Web Vitals score is claimed.
