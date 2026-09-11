"""Regression checks for the generated site. Run: python3 -m unittest discover -s tests -v."""
import json
import re
import sys
import unittest
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, parse_qs
from collections import Counter
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
BASE='https://beautyclinicmallorca.com'
sys.path.insert(0,str(ROOT/'scripts'))
from content import LANG, SERVICES
from build_site import route

class Document(HTMLParser):
    def __init__(self,path):
        super().__init__(convert_charrefs=True)
        self.path=path; self.tags=[]; self.text=[]; self.structured=[]; self.in_schema=False; self.schema=''
        self.feed(path.read_text())
    def handle_starttag(self,tag,attrs):
        d=dict(attrs);self.tags.append((tag,d))
        if tag=='script' and d.get('type')=='application/ld+json':self.in_schema=True;self.schema=''
    def handle_data(self,data):
        self.text.append(data)
        if self.in_schema:self.schema+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.in_schema:
            self.structured.append(json.loads(self.schema));self.in_schema=False
    def select(self,tag,**attrs):return [d for t,d in self.tags if t==tag and all(d.get(k)==v for k,v in attrs.items())]

def file_for(url):
    p=unquote(urlsplit(url).path)
    if p=='/':return ROOT/'index.html'
    return ROOT/p.lstrip('/')/('index.html') if p.endswith('/') else ROOT/p.lstrip('/')

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes=[]
        for lang in LANG:
            cls.routes.append((lang,'home',''))
            cls.routes.extend((lang,'service',s['slug']) for s in SERVICES)
            cls.routes.extend((lang,k,'') for k in ['dr-erik-koerge','privacy','clinic-information'])
        cls.docs={route(*r):Document(file_for(route(*r))) for r in cls.routes}

    def test_expected_pages_and_metadata(self):
        self.assertEqual(len(self.docs),20)
        for lang,kind,slug in self.routes:
            url=route(lang,kind,slug);d=self.docs[url]
            with self.subTest(url=url):
                self.assertEqual(len(d.select('title')),1)
                self.assertEqual(len(d.select('h1')),1)
                self.assertEqual(d.select('html')[0]['lang'],lang)
                descriptions=d.select('meta',name='description');self.assertEqual(len(descriptions),1)
                self.assertGreater(len(descriptions[0]['content']),20)
                self.assertEqual(d.select('link',rel='canonical')[0]['href'],BASE+url)
                self.assertNotIn('maximum-scale',d.select('meta',name='viewport')[0]['content'])
                self.assertFalse(d.select('meta',name='robots'))
                ids=[a['id'] for _,a in d.tags if 'id'in a];self.assertEqual(len(ids),len(set(ids)))

    def test_reciprocal_languages_on_every_page(self):
        for lang,kind,slug in self.routes:
            d=self.docs[route(lang,kind,slug)]
            for code in LANG:
                links=d.select('link',rel='alternate',hreflang=code)
                self.assertEqual([x['href'] for x in links],[BASE+route(code,kind,slug)])
            self.assertEqual(d.select('link',rel='alternate',hreflang='x-default')[0]['href'],BASE+route('en',kind,slug))

    def test_local_links_assets_and_anchors(self):
        for url,d in self.docs.items():
            for tag,a in d.tags:
                for attr in ['href','src']:
                    link=a.get(attr)
                    if not link:continue
                    parsed=urlsplit(link)
                    if parsed.scheme in ['mailto','tel']:continue
                    if parsed.netloc and parsed.netloc!='beautyclinicmallorca.com':continue
                    if not parsed.path:target=d.path
                    else:target=file_for(link)
                    with self.subTest(page=url,link=link):
                        self.assertTrue(target.is_file(),str(target))
                        if parsed.fragment:
                            dest=d if target==d.path else Document(target)
                            self.assertTrue(any(x.get('id')==parsed.fragment for _,x in dest.tags),link)

    def test_consistent_clinic_schema(self):
        expected=None
        for url,d in self.docs.items():
            self.assertEqual(len(d.structured),1,url)
            graph=d.structured[0]['@graph']
            clinics=[v for v in graph if v.get('@id')==BASE+'/#clinic']
            self.assertEqual(len(clinics),1)
            clinic=clinics[0]
            if expected is None:expected=clinic
            self.assertEqual(clinic,expected)
            self.assertEqual(clinic['address']['postalCode'],'07181')
            self.assertEqual(clinic['telephone'],'+34971707725')
            hours=clinic['openingHoursSpecification'][0]
            self.assertEqual(hours['opens'],'09:30');self.assertEqual(hours['closes'],'18:00')
            self.assertEqual(len(hours['dayOfWeek']),5)

    def test_native_accessible_controls_and_images(self):
        for url,d in self.docs.items():
            with self.subTest(url=url):
                menu=d.select('button',**{'class':'menu-toggle'})[0]
                self.assertEqual(menu['aria-expanded'],'false');self.assertEqual(menu['aria-controls'],'navigation')
                self.assertTrue(d.select('a',href='#main'))
                self.assertEqual(d.select('main',id='main')[0].get('tabindex'),'-1')
                self.assertTrue(d.select('a',href='tel:+34971707725'))
                self.assertFalse(d.select('iframe'))
                for image in d.select('img'):
                    self.assertIn('alt',image);self.assertGreater(int(image['width']),0);self.assertGreater(int(image['height']),0)
                    self.assertTrue(image.get('loading')=='lazy' or image.get('fetchpriority')=='high')

    def test_no_obsolete_scripts_or_tracking(self):
        for url,d in self.docs.items():
            scripts=[a['src'] for a in d.select('script') if 'src'in a]
            self.assertEqual(scripts,['/assets/site.js?v=20260911'])
            body=d.path.read_text()
            for old in ['UA-45901968-5','php Copy code','Carrer de Sant Miquel','07002','maximum-scale','page-loader']:
                self.assertNotIn(old,body)
        self.assertFalse((ROOT/'js/jquery-1.11.2.min.js').exists())
        self.assertFalse((ROOT/'contact_me_smtp.php').exists())

    def test_contact_enquiry_is_an_email_not_fake_booking(self):
        for url,d in self.docs.items():
            links=d.select('a')
            mails=[a['href'] for a in links if a.get('href','').startswith('mailto:')]
            self.assertTrue(mails)
            for link in mails:
                parsed=urlsplit(link);self.assertEqual(parsed.path,'info@beautyclinicmallorca.com')
                if parsed.query:self.assertTrue(parse_qs(parsed.query)['subject'][0])
            self.assertFalse(d.select('form'))
        for lang in LANG:
            for s in SERVICES:
                d=self.docs[route(lang,'service',s['slug'])]
                self.assertTrue(any(s[lang]['name'] in parse_qs(urlsplit(a.get('href','')).query).get('subject',[''])[0] for a in d.select('a')))

    def test_sitemap_contains_only_canonical_pages(self):
        tree=ET.parse(ROOT/'sitemap.xml')
        locs=[x.text for x in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertEqual(set(locs),{BASE+u for u in self.docs});self.assertEqual(len(locs),20)
        self.assertIn('Sitemap: '+BASE+'/sitemap.xml',(ROOT/'robots.txt').read_text())

    def test_legacy_redirects_and_error_page(self):
        for lang,file in [('en','index.html'),('de','index-de.html')]:
            d=Document(ROOT/'lako13-beautyclinic'/file)
            target=BASE+route(lang,'home')
            self.assertEqual(d.select('link',rel='canonical')[0]['href'],target)
            self.assertEqual(d.select('meta',**{'http-equiv':'refresh'})[0]['content'],'0;url='+target)
            self.assertIn('noindex',d.select('meta',name='robots')[0]['content'])
            self.assertNotIn('10 years',(d.path).read_text())
        self.assertTrue((ROOT/'404.html').exists())

    def test_readable_colour_pairs(self):
        css=(ROOT/'assets/site.css').read_text()
        colours=dict(re.findall(r'--(ink|text|muted|wash|accent):(#(?:[0-9a-f]{6}|[0-9a-f]{3}))(?:;|})',css))
        def luminance(hexcolour):
            h=hexcolour.lstrip('#')
            if len(h)==3:h=''.join(c*2 for c in h)
            channels=[int(h[i:i+2],16)/255 for i in [0,2,4]]
            channels=[c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in channels]
            return sum(c*w for c,w in zip(channels,[0.2126,0.7152,0.0722]))
        for fg,bg in [(colours[k],b) for k in ['ink','text','muted','accent'] for b in ['#ffffff',colours['wash']]]:
            a,b=sorted([luminance(fg),luminance(bg)])
            self.assertGreaterEqual((b+0.05)/(a+0.05),4.5,(fg,bg))

    def test_source_has_no_case_collisions(self):
        import subprocess
        tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
        paths=[p for p in tracked if p and (ROOT/p).is_file()]
        duplicates=[p for p,n in Counter(p.lower() for p in paths).items() if n>1]
        self.assertEqual(duplicates,[])

if __name__=='__main__':unittest.main()
