"""Check generated public routes, metadata, structured data and cross-page links."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
HOST = "rochaproauto.com.br"


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.refs = []
        self.meta = {}
        self.canonical = []
        self.h1 = 0
        self.title = ""
        self.in_title = False
        self.script = None
        self.jsonld = []
        self.feed(text)

    def handle_starttag(self, tag, values):
        attrs = dict(values)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag in ("a", "link") and attrs.get("href"):
            self.refs.append(attrs["href"])
        if tag == "img":
            assert "alt" in attrs and "width" in attrs and "height" in attrs
            self.refs.append(attrs["src"])
            self.refs.extend(x.strip().split()[0] for x in attrs.get("srcset", "").split(",") if x.strip())
        if tag == "script" and attrs.get("src"):
            self.refs.append(attrs["src"])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.script = ""
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1 += 1
        if tag == "meta":
            self.meta[attrs.get("name", attrs.get("property"))] = attrs.get("content")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs["href"])

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.script is not None:
            self.script += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.script is not None:
            self.jsonld.append(json.loads(self.script))
            self.script = None


def local_path(url):
    pathname = unquote(urlsplit(url).path)
    path = ROOT / pathname.lstrip("/")
    return path / "index.html" if path.is_dir() else path


class PublicPagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sitemap = ET.parse(ROOT / "sitemap.xml")
        cls.urls = [node.text for node in sitemap.findall("{*}url/{*}loc")]
        cls.pages = {url: Page(local_path(url).read_text(encoding="utf-8")) for url in cls.urls}

    def test_all_routes_have_unique_indexable_metadata(self):
        self.assertEqual(len(self.urls), 42)
        self.assertEqual(len({p.title for p in self.pages.values()}), 42)
        self.assertEqual(len({p.meta["description"] for p in self.pages.values()}), 42)
        for url, page in self.pages.items():
            with self.subTest(url=url):
                self.assertEqual(page.canonical, [url])
                self.assertEqual(page.h1, 1)
                self.assertTrue(page.title and page.meta["description"])
                self.assertIn("index,follow", page.meta["robots"])
                self.assertEqual(page.meta["og:url"], url)
                self.assertEqual(page.meta["twitter:card"], "summary_large_image")
                self.assertTrue(local_path(page.meta["og:image"]).is_file())
                self.assertTrue(page.jsonld)
                self.assertEqual(len(page.ids), len(set(page.ids)))
                text = local_path(url).read_text(encoding="utf-8")
                self.assertNotRegex(text, r"__PRODUCTS__|__KIT55_|__SEO__|private/|anotacao_csv|composicao|1971606904")
                self.assertNotIn("\ufffd", text)

    def test_local_resources_and_cross_page_kit_anchors_exist(self):
        for origin, page in self.pages.items():
            for ref in page.refs:
                parts = urlsplit(ref)
                if parts.scheme and parts.netloc != HOST:
                    continue
                if parts.path.startswith("/") or parts.netloc == HOST:
                    target = local_path(ref)
                elif parts.path:
                    target = local_path(origin).parent / parts.path
                else:
                    target = local_path(origin)
                self.assertTrue(target.is_file(), f"{origin}: recurso ausente {ref}")
                if parts.fragment and target.suffix == ".html":
                    parsed = Page(target.read_text(encoding="utf-8"))
                    self.assertIn(unquote(parts.fragment), parsed.ids, f"{origin}: âncora ausente {ref}")

    def test_article_schema_and_kits_finish_every_post(self):
        articles = [url for url in self.urls if url.startswith(f"https://{HOST}/blog/") and url != f"https://{HOST}/blog/"]
        self.assertEqual(len(articles), 36)
        for url in articles:
            page = self.pages[url]
            graph = page.jsonld[0]["@graph"]
            article = next(x for x in graph if x["@type"] == "BlogPosting")
            self.assertEqual(article["mainEntityOfPage"]["@id"], url)
            self.assertIn(article["headline"], page.title)
            self.assertTrue(article["datePublished"].endswith("-03:00"))
            self.assertEqual(article["author"]["name"], "Equipe RochaPro")
            text = local_path(url).read_text(encoding="utf-8")
            self.assertGreaterEqual(text.count('class="kit-link"'), 1)
            self.assertEqual(re.findall(r'<section[^>]*id="([^"]+)"', text)[-1], "kits-relacionados")
            self.assertIn('class="source-link"', text)
            self.assertNotIn('"offers"', text)
            self.assertNotIn('"aggregateRating"', text)

    def test_catalog_lists_match_visible_products(self):
        for slug, count in [("troller", 7), ("hilux", 21), ("frontier", 22), ("tr4", 13)]:
            page = self.pages[f"https://{HOST}/{slug}/"]
            graph = page.jsonld[0]["@graph"]
            itemlist = next(x for x in graph if x["@type"] == "ItemList")
            self.assertEqual(itemlist["numberOfItems"], count)
            self.assertEqual(len(itemlist["itemListElement"]), count)
            for entry in itemlist["itemListElement"]:
                self.assertIn(urlsplit(entry["url"]).fragment, page.ids)
        hilux = local_path("/hilux/").read_text(encoding="utf-8")
        for sw4_only in ["KIT10948", "KIT10270", "KIT10269", "KIT10201", "KIT10100"]:
            self.assertNotIn(f'id="kit-{sw4_only}"', hilux)

    def test_sitemap_feed_and_crawl_entrypoints(self):
        self.assertEqual(len(self.urls), len(set(self.urls)))
        feed = ET.parse(ROOT / "blog/feed.xml")
        self.assertEqual(len(feed.findall(".//item")), 36)
        robots = (ROOT / "robots.txt").read_text()
        self.assertIn(f"Sitemap: https://{HOST}/sitemap.xml", robots)
        self.assertNotIn("Disallow: /\n", robots)
        self.assertNotIn("Disallow: /assets/", robots)
        self.assertNotIn("Disallow: /links", robots)
        self.assertNotIn(f"https://{HOST}/links/", self.urls)
        links_page = Page((ROOT / "links/index.html").read_text(encoding="utf-8"))
        self.assertEqual(links_page.meta["robots"], "noindex,follow")
        self.assertEqual(links_page.canonical, [f"https://{HOST}/links/"])
        for page in self.pages.values():
            self.assertNotIn("/links/", page.refs)
            self.assertNotIn(f"https://{HOST}/links/", json.dumps(page.jsonld))
        for image in ET.parse(ROOT / "sitemap.xml").findall(".//{http://www.google.com/schemas/sitemap-image/1.1}loc"):
            self.assertTrue(local_path(image.text).is_file())
        home = self.pages[f"https://{HOST}/"]
        for route in ("/tr4/", "/troller/", "/hilux/", "/frontier/", "/blog/"):
            self.assertIn(route, home.refs)
        for css in (ROOT / "assets/site/site.css", ROOT / "tr4/style.css"):
            for resource in re.findall(r"url\(['\"]?([^)'\"]+)", css.read_text(encoding="utf-8")):
                self.assertTrue(local_path(resource).is_file(), resource)


if __name__ == "__main__":
    unittest.main()
