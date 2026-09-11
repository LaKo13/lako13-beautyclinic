#!/usr/bin/env python3
"""Generate the static GitHub Pages site: python3 scripts/build_site.py."""
from pathlib import Path
from html import escape
from urllib.parse import urlencode
import json
import sys
from content import LANG, SERVICES

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://beautyclinicmallorca.com'
EMAIL = 'info@beautyclinicmallorca.com'
PHONE = '+34 971 707 725'
ADDRESS = 'Calle Arquitecto Francisco Casas 17'
MAP_SRC = json.loads((ROOT/'scripts/map.json').read_text())['src']
DIRECTIONS = 'https://www.google.com/maps/dir/?api=1&destination=' + 'Beauty%20Clinic%20Mallorca%2C%20Calle%20Arquitecto%20Francisco%20Casas%2017%2C%20Bendinat'
PAGES = []

def e(value): return escape(str(value), quote=True)
def route(lang, kind, slug=''):
    if kind == 'home': return LANG[lang]['home']
    prefix = '' if lang == 'en' else '/de'
    if kind == 'service': return f'{prefix}/treatments/{slug}/'
    return f'{prefix}/{kind}/'
def email_link(lang, treatment=None):
    subject = ('Consultation enquiry' if lang == 'en' else 'Beratungsanfrage')
    if treatment: subject += ' — ' + treatment
    return 'mailto:' + EMAIL + '?' + urlencode({'subject': subject})
def img(file, alt, hero=False):
    size = (1920,1080) if file == 'Dentaface_Cover.jpg' else (370,450) if file == 'dr-koerge-profile.jpg' else (370,200)
    loading = 'fetchpriority="high"' if hero else 'loading="lazy"'
    return f'<img src="/images/dentaface/{e(file)}" alt="{e(alt)}" width="{size[0]}" height="{size[1]}" {loading} decoding="async">'
def arrow(): return '<span aria-hidden="true">↗</span>'
def button(url, text, cls='', attr=''):
    return f'<a class="button {cls}" href="{e(url)}" {attr}>{e(text)}{arrow()}</a>'
def brand():
    return '<strong>Beauty Clinic</strong><small>Mallorca</small>'
def header(lang, kind, slug=''):
    t=LANG[lang]; home=t['home']; language=[]
    for code in LANG:
        active=' aria-current="page"' if code == lang else ''
        language.append(f'<a href="{route(code,kind,slug)}" lang="{code}" hreflang="{code}" aria-label="{LANG[code]["name"]}"{active}>{code.upper()}</a>')
    return f'''<a class="skip" href="#main">{t['skip']}</a><header class="site-header"><div class="wrap header-inner">
<a class="brand" href="{home}" aria-label="Beauty Clinic Mallorca — {t['home_label']}">{brand()}</a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation">{t['menu']} <span aria-hidden="true">☰</span></button>
<nav id="navigation" class="nav-links" aria-label="{'Main navigation' if lang=='en' else 'Hauptnavigation'}">
<a href="{home}#services">{t['services']}</a><a href="{home}#about">{t['about']}</a><a href="{home}#contact">{t['contact']}</a>
<div class="languages">{''.join(language)}</div>{button(home+'#contact',t['cta'],'header-cta')}</nav></div></header>'''
def footer(lang):
    t=LANG[lang]
    return f'''<footer class="footer"><div class="wrap"><div class="footer-top"><div><a class="brand" href="{t['home']}" aria-label="Beauty Clinic Mallorca">{brand()}</a><p>{t['footer_note']}</p></div><nav class="footer-links" aria-label="{'Footer navigation' if lang=='en' else 'Fußnavigation'}"><a href="{route(lang,'dr-erik-koerge')}">Dr. Erik Koerge</a><a href="{route(lang,'clinic-information')}">{t['clinic_info']}</a><a href="{route(lang,'privacy')}">{t['privacy']}</a></nav></div><div class="footer-bottom"><span>© 2026 Beauty Clinic Mallorca. {t['rights']}</span><a href="mailto:{EMAIL}">{EMAIL}</a><a href="tel:+34971707725">{PHONE}</a></div></div></footer>
<nav class="mobile-bar" aria-label="{'Contact the clinic' if lang=='en' else 'Klinik kontaktieren'}">{button('tel:+34971707725','Call' if lang=='en' else 'Anrufen','secondary')}{button(t['home']+'#contact','Consultation' if lang=='en' else 'Beratung')}</nav>'''
def clinic_schema():
    return {'@type':'LocalBusiness','@id':BASE+'/#clinic','name':'Beauty Clinic Mallorca','url':BASE+'/','telephone':'+34971707725','email':EMAIL,'image':BASE+'/images/dentaface/dr-koerge-profile.jpg','address':{'@type':'PostalAddress','streetAddress':ADDRESS+', Plaza Bendinat, Local B10','addressLocality':'Bendinat','addressRegion':'Balearic Islands','postalCode':'07181','addressCountry':'ES'},'openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday'],'opens':'09:30','closes':'18:00'}]}
def page(lang, kind, title, desc, body, slug='', extra=None):
    url=route(lang,kind,slug); title=title+' | Beauty Clinic Mallorca'
    graph=[clinic_schema(),{'@type':'WebPage','@id':BASE+url+'#webpage','url':BASE+url,'name':title,'description':desc,'inLanguage':lang,'about':{'@id':BASE+'/#clinic'}}]
    if extra: graph.extend(extra)
    hreflangs=''.join(f'<link rel="alternate" hreflang="{code}" href="{BASE+route(code,kind,slug)}">' for code in LANG)
    hreflangs+=f'<link rel="alternate" hreflang="x-default" href="{BASE+route("en",kind,slug)}">'
    structured = json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<', chr(92)+'u003c')
    result=f'''<!doctype html>
<html lang="{lang}" class="no-js"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#153b3d"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE+url}">{hreflangs}<meta property="og:type" content="website"><meta property="og:site_name" content="Beauty Clinic Mallorca"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE+url}"><meta property="og:locale" content="{'en_GB' if lang=='en' else 'de_DE'}"><meta name="twitter:card" content="summary"><meta name="referrer" content="strict-origin-when-cross-origin"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css?v=20260911"><script src="/assets/site.js?v=20260911" defer></script><script type="application/ld+json">{structured}</script></head><body id="top">{header(lang,kind,slug)}<main id="main" tabindex="-1">{body}</main>{footer(lang)}</body></html>'''
    path=ROOT/('index.html' if url=='/' else url.strip('/')+('index.html' if url.endswith('/') else ''))
    # A trailing-slash URL maps to its own directory index.
    if url!='/' and url.endswith('/'):path=ROOT/url.strip('/')/'index.html'
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(result)
    PAGES.append((url,lang,kind,slug))
def faq(items):
    return ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q,a in items)
def contact(lang):
    t=LANG[lang]
    return f'''<section class="section" id="contact"><div class="wrap contact-grid"><div class="contact-intro"><p class="eyebrow">{t['contact_eyebrow']}</p><h2>{t['contact_title']}</h2><p>{t['contact_intro']}</p><div class="contact-options"><a class="contact-option" href="tel:+34971707725"><span><small>{t['call']}</small><strong>{PHONE}</strong></span>{arrow()}</a><a class="contact-option" href="{e(email_link(lang))}"><span><small>{t['email']}</small><strong>{EMAIL}</strong></span>{arrow()}</a></div><p class="hero-note">{t['contact_note']}</p></div>
<div class="visit-card"><p class="eyebrow">Plaza Bendinat · Mallorca</p><h3>{t['visit_title']}</h3><address>{ADDRESS}<br>Plaza Bendinat, Local B10<br>07181 Bendinat, Mallorca</address><p class="hours"><strong>{t['hours_label']}</strong>{t['hours']}</p><p class="fine">{t['parking']}</p>{button(DIRECTIONS,t['directions'],'secondary','target="_blank" rel="noopener noreferrer"')}<details class="map-area"><summary>{t['map_summary']}</summary><div class="map-panel"><p>{t['map_note']} <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">{t['map_privacy']}</a></p><button type="button" class="button secondary" data-map-src="{e(MAP_SRC)}" data-map-title="{t['map_title']}">{t['map_load']}</button><noscript><p><a href="{DIRECTIONS}">{t['directions']}</a></p></noscript></div></details></div></div></section>'''
def home(lang):
    t=LANG[lang]
    cards=''.join(f'''<a class="service-card" href="{route(lang,'service',s['slug'])}">{img(s['image'],'')}<div class="card-title"><h3>{s[lang]['name']}</h3>{arrow()}</div><p>{s[lang]['short']}</p></a>''' for s in SERVICES)
    trusts=''.join(f'<div class="trust-item"><span class="trust-number">{a}</span><span class="trust-label">{b}</span></div>' for a,b in t['trust'])
    steps=''.join(f'<div class="step"><span class="step-number">0{i+1}</span><h3>{a}</h3><p>{b}</p></div>' for i,(a,b) in enumerate(t['steps']))
    body=f'''<section class="wrap hero" id="home"><div class="hero-copy"><p class="eyebrow">{t['eyebrow']}</p><h1>{t['headline']}</h1><p class="lead">{t['lead']}</p><div class="hero-actions">{button('#contact',t['cta'])}<a class="text-link" href="#services">{t['explore']}{arrow()}</a></div><p class="hero-note"><span class="dot" aria-hidden="true"></span>{t['note']}</p></div><div class="hero-image">{img('Dentaface_Cover.jpg',t['hero_alt'],True)}<div class="photo-caption"><div><span>{t['caption_small']}</span><strong>{t['caption']}</strong></div><span class="mark" aria-hidden="true">✳</span></div></div></section>
<div class="trust-strip"><div class="wrap trust-inner">{trusts}</div></div>
<section class="section wrap" id="services"><div class="section-head"><div><p class="eyebrow">{t['services']}</p><h2>{t['services_title']}</h2></div><p>{t['services_intro']}</p></div><div class="service-grid">{cards}</div></section>
<section class="section doctor-section" id="about"><div class="wrap doctor-grid"><figure class="doctor-photo">{img('dr-koerge-profile.jpg',t['portrait_alt'])}<figcaption>Dr. Erik Koerge · Beauty Clinic Mallorca</figcaption></figure><div class="doctor-copy"><p class="eyebrow">{t['doctor_eyebrow']}</p><h2>{t['doctor_title']}</h2><p>{t['doctor_intro']}</p><p>{t['doctor_body']}</p><a class="text-link" href="{route(lang,'dr-erik-koerge')}">{t['doctor_link']}{arrow()}</a></div></div></section>
<section class="section wrap"><p class="eyebrow">{t['process_eyebrow']}</p><h2>{t['process_title']}</h2><div class="steps-grid">{steps}</div></section>
<section class="section faq-section"><div class="wrap faq-layout"><div class="faq-intro"><p class="eyebrow">{t['faq_eyebrow']}</p><h2>{t['faq_title']}</h2><p>{t['faq_intro']}</p></div><div>{faq(t['faqs'])}</div></div></section>{contact(lang)}'''
    title='Aesthetic treatments in Bendinat, Mallorca' if lang=='en' else 'Ästhetische Behandlungen in Bendinat, Mallorca'
    desc='Explore aesthetic treatments with Dr. Erik Koerge in Bendinat, Mallorca. Over 20 years of experience. Call or email for a free initial consultation.' if lang=='en' else 'Ästhetische Behandlungen mit Dr. Erik Koerge in Bendinat, Mallorca. Über 20 Jahre Erfahrung. Kostenlose Erstberatung telefonisch oder per E-Mail anfragen.'
    page(lang,'home',title,desc,body)
def intro(lang,title,lead,eyebrow):
    t=LANG[lang]
    return f'<section class="page-intro"><div class="wrap"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{t["home"]}">{t["home_label"]}</a><span aria-hidden="true">/</span><span>{e(title)}</span></nav><p class="eyebrow">{e(eyebrow)}</p><h1>{e(title)}</h1><p class="lead">{e(lead)}</p></div></section>'
def treatment(lang,s):
    t=LANG[lang]; c=s[lang]; title=c['name']+(' in Mallorca' if lang=='en' else ' auf Mallorca'); url=route(lang,'service',s['slug'])
    qs=''.join(f'<li>{e(q)}</li>' for q in c['questions'])
    source=f'<p class="source">{t["source"]}: <a href="{e(s["source"][1])}" target="_blank" rel="noopener noreferrer">{e(s["source"][0])}</a>.</p>' if s.get('source') else ''
    related=''.join(f'<a href="{route(lang,"service",other["slug"])}">{other[lang]["name"]}{arrow()}</a>' for other in SERVICES if other!=s)
    body=intro(lang,title,c['intro'],t['treatment_label'])+f'''<section class="section wrap article-grid"><article class="article-body"><h2>{t['overview']}</h2><p>{c['body']}</p><h2>{t['discuss']}</h2><ul>{qs}</ul><h2>{t['consider']}</h2><p>{c['consider']}</p>{source}<h2>{t['planning']}</h2><p>{t['plan_body']}</p><div class="article-faq">{faq([t['faqs'][0],t['faqs'][1],t['faqs'][3]])}</div></article><aside class="article-aside" aria-label="{t['contact']}">{img(s['image'],c['name'])}<div class="aside-box"><p class="eyebrow">{t['note']}</p><h3>{t['guide_cta']}</h3><p>{t['guide_note']}</p>{button(email_link(lang,c['name']),t['email'])}<a class="text-link" href="tel:+34971707725">{PHONE}</a></div></aside></section><section class="section related"><div class="wrap"><h2>{t['related']}</h2><div class="related-links">{related}</div></div></section>{contact(lang)}'''
    extra=[{'@type':'Service','@id':BASE+url+'#service','name':c['name'],'description':c['intro'],'provider':{'@id':BASE+'/#clinic'},'url':BASE+url,'areaServed':'Mallorca'},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':t['home_label'],'item':BASE+t['home']},{'@type':'ListItem','position':2,'name':c['name'],'item':BASE+url}]}]
    page(lang,'service',title,c['intro'],body,s['slug'],extra)
def doctor(lang):
    t=LANG[lang]
    body=intro(lang,t['doctor_page_title'],t['doctor_page_intro'],t['doctor_eyebrow'])+f'''<section class="section wrap article-grid"><article class="article-body"><h2>{t['doctor_section']}</h2><p>{t['doctor_intro']}</p><p>{t['doctor_more']}</p><h2>{t['doctor_questions']}</h2><p>{t['doctor_questions_body']}</p><h2>{t['location_title']}</h2><p>{t['location_body']}</p>{button(t['home']+'#services',t['explore'],'secondary')}</article><aside class="article-aside">{img('dr-koerge-profile.jpg',t['portrait_alt'])}<div class="aside-box"><h3>Dr. Erik Koerge</h3><p>Beauty Clinic Mallorca<br>Plaza Bendinat, Mallorca</p>{button(email_link(lang),t['cta'])}</div></aside></section>{contact(lang)}'''
    page(lang,'dr-erik-koerge',t['doctor_page_title'],t['doctor_page_intro'],body,extra=[{'@type':'Person','@id':BASE+'/dr-erik-koerge/#person','name':'Dr. Erik Koerge','url':BASE+route(lang,'dr-erik-koerge'),'image':BASE+'/images/dentaface/dr-koerge-profile.jpg'}])
def policies(lang):
    t=LANG[lang]
    body=intro(lang,t['privacy'],t['privacy_intro'], 'Beauty Clinic Mallorca')+'<section class="section wrap policy">'+''.join(f'<h2>{e(h)}</h2><p>{e(p)}</p>' for h,p in t['privacy_sections'])+'<p><a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener noreferrer" target="_blank">GitHub privacy statement</a> · <a href="https://policies.google.com/privacy" rel="noopener noreferrer" target="_blank">Google privacy policy</a></p>'+f'<p class="source">{t["updated"]}</p></section>'
    page(lang,'privacy',t['privacy'],t['privacy_intro'],body)
    body=intro(lang,t['clinic_info'],t['clinic_intro'],'Beauty Clinic Mallorca')+f'''<section class="section wrap policy"><h2>Beauty Clinic Mallorca</h2><p>{ADDRESS}<br>Plaza Bendinat, Local B10<br>07181 Bendinat, Mallorca, España</p><p><a href="tel:+34971707725">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p><h2>{t['hours_label']}</h2><p>{t['hours']}</p><p>{t['clinic_note']}</p><a href="{route(lang,'privacy')}">{t['privacy']}</a></section>'''
    page(lang,'clinic-information',t['clinic_info'],t['clinic_intro'],body)
def supporting_files():
    urls=[]
    for url,lang,kind,slug in PAGES:
        alt=''.join(f'<xhtml:link rel="alternate" hreflang="{code}" href="{BASE+route(code,kind,slug)}"/>' for code in LANG)
        alt+=f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE+route("en",kind,slug)}"/>'
        urls.append(f'<url><loc>{BASE+url}</loc>{alt}</url>')
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+''.join(urls)+'</urlset>')
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
    # GitHub Pages does not support custom server-side 301 rules. Immediate HTML
    # redirects replace the obsolete pages; canonical/noindex prevent duplicate copy.
    for lang,file in [('en','index.html'),('de','index-de.html')]:
        target=BASE+LANG[lang]['home']
        path=ROOT/'lako13-beautyclinic'/file;path.parent.mkdir(exist_ok=True)
        path.write_text(f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>Beauty Clinic Mallorca</title><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="{target}"><link rel="stylesheet" href="/assets/site.css?v=20260911"></head><body><main class="wrap section"><p><a href="{target}">{LANG[lang]["redirect"]}</a></p></main></body></html>')
    t=LANG['en']
    (ROOT/'404.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Page not found | Beauty Clinic Mallorca</title><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><link rel="stylesheet" href="/assets/site.css?v=20260911"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"></head><body><main class="wrap error-page"><div><p class="eyebrow">Beauty Clinic Mallorca · 404</p><h1>{t["not_found"]}</h1><p>{t["not_found_intro"]}</p>{button("/",t["return_home"])} <a href="/index-de.html" lang="de">Zur deutschen Startseite</a></div></main></body></html>')

if __name__=='__main__':
    for lang in LANG:
        home(lang)
        if '--home-only' not in sys.argv:
            for service in SERVICES:treatment(lang,service)
            doctor(lang);policies(lang)
    if '--home-only' not in sys.argv:supporting_files()
    print(f'Generated {len(PAGES)} canonical pages'+(' plus sitemap, robots, redirects and 404.' if '--home-only' not in sys.argv else '.'))
