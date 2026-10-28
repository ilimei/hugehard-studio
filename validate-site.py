#!/usr/bin/env python3
"""Validate the static bilingual site without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent
BASE = "https://hugehard.app"
ICON = f"{BASE}/assets/app-icon.png"
TESTFLIGHT_URL = "https://testflight.apple.com/join/GK8ht2vv"
TESTFLIGHT_HTML_PLACEMENTS = {
    "/": "home_hero",
    "/en/": "home_hero",
    "/apps/this-pic-can-change/": "product_hero",
    "/en/apps/this-pic-can-change/": "product_hero",
    "/guides/video-to-live-photo/": "live_photo_guide",
    "/en/guides/video-to-live-photo/": "live_photo_guide",
}
ANALYTICS_SCRIPT = "/assets/site-analytics.js"

# Canonical URL -> (file in this repository, document language)
ROUTES = {
    "/": ("index.html", "zh-CN"),
    "/privacy.html": ("privacy.html", "zh-CN"),
    "/badges/": ("badges/index.html", "zh-CN"),
    "/apps/this-pic-can-change/": ("apps/this-pic-can-change/index.html", "zh-CN"),
    "/apps/this-pic-can-change/privacy.html": ("apps/this-pic-can-change/privacy.html", "zh-CN"),
    "/apps/this-pic-can-change/support.html": ("apps/this-pic-can-change/support.html", "zh-CN"),
    "/guides/": ("guides/index.html", "zh-CN"),
    "/guides/image-compression/": ("guides/image-compression/index.html", "zh-CN"),
    "/guides/crop-rotate-photo/": ("guides/crop-rotate-photo/index.html", "zh-CN"),
    "/guides/video-to-live-photo/": ("guides/video-to-live-photo/index.html", "zh-CN"),
    "/guides/screenshot-delivery/": ("guides/screenshot-delivery/index.html", "zh-CN"),
    "/guides/video-to-gif/": ("guides/video-to-gif/index.html", "zh-CN"),
    "/guides/heic-to-jpg/": ("guides/heic-to-jpg/index.html", "zh-CN"),
    "/guides/compress-video/": ("guides/compress-video/index.html", "zh-CN"),
    "/en/": ("en/index.html", "en"),
    "/en/privacy.html": ("en/privacy.html", "en"),
    "/en/badges/": ("en/badges/index.html", "en"),
    "/en/apps/this-pic-can-change/": ("en/apps/this-pic-can-change/index.html", "en"),
    "/en/apps/this-pic-can-change/privacy.html": ("en/apps/this-pic-can-change/privacy.html", "en"),
    "/en/apps/this-pic-can-change/support.html": ("en/apps/this-pic-can-change/support.html", "en"),
    "/en/guides/": ("en/guides/index.html", "en"),
    "/en/guides/image-compression/": ("en/guides/image-compression/index.html", "en"),
    "/en/guides/crop-rotate-photo/": ("en/guides/crop-rotate-photo/index.html", "en"),
    "/en/guides/video-to-live-photo/": ("en/guides/video-to-live-photo/index.html", "en"),
    "/en/guides/screenshot-delivery/": ("en/guides/screenshot-delivery/index.html", "en"),
    "/en/guides/video-to-gif/": ("en/guides/video-to-gif/index.html", "en"),
    "/en/guides/heic-to-jpg/": ("en/guides/heic-to-jpg/index.html", "en"),
    "/en/guides/compress-video/": ("en/guides/compress-video/index.html", "en"),
}

LANGUAGE_PAIRS = (
    ("/", "/en/"),
    ("/privacy.html", "/en/privacy.html"),
    ("/badges/", "/en/badges/"),
    ("/apps/this-pic-can-change/", "/en/apps/this-pic-can-change/"),
    ("/apps/this-pic-can-change/privacy.html", "/en/apps/this-pic-can-change/privacy.html"),
    ("/apps/this-pic-can-change/support.html", "/en/apps/this-pic-can-change/support.html"),
    ("/guides/", "/en/guides/"),
    ("/guides/image-compression/", "/en/guides/image-compression/"),
    ("/guides/crop-rotate-photo/", "/en/guides/crop-rotate-photo/"),
    ("/guides/video-to-live-photo/", "/en/guides/video-to-live-photo/"),
    ("/guides/screenshot-delivery/", "/en/guides/screenshot-delivery/"),
    ("/guides/video-to-gif/", "/en/guides/video-to-gif/"),
    ("/guides/heic-to-jpg/", "/en/guides/heic-to-jpg/"),
    ("/guides/compress-video/", "/en/guides/compress-video/"),
)

MARKDOWN_PAGES = {
    "/apps/this-pic-can-change/": "apps/this-pic-can-change/index.md",
    "/en/apps/this-pic-can-change/": "en/apps/this-pic-can-change/index.md",
    "/guides/video-to-live-photo/": "guides/video-to-live-photo/index.md",
    "/en/guides/video-to-live-photo/": "en/guides/video-to-live-photo/index.md",
}
LLMS_DESCRIBED_ROUTES = {
    "/", "/en/",
    "/apps/this-pic-can-change/", "/en/apps/this-pic-can-change/",
    "/guides/video-to-live-photo/", "/en/guides/video-to-live-photo/",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.title_open = False
        self.h1_open = False
        self.h1_count = 0
        self.meta: dict[str, list[str]] = defaultdict(list)
        self.canonicals: list[str] = []
        self.alternates: dict[str, list[str]] = defaultdict(list)
        self.describedby: list[str] = []
        self.markdown_alternates: list[str] = []
        self.hrefs: list[str] = []
        self.script_srcs: list[str] = []
        self.analytics_ctas: list[tuple[str, str]] = []
        self.language_links: list[str] = []
        self.resources: list[str] = []
        self.videos: list[dict[str, str | None]] = []
        self.video_sources: list[str] = []
        self.video_source_types: list[str] = []
        self.ids: set[str] = set()
        self.jsonld_parts: list[str] = []
        self.current_script_is_jsonld = False
        self.current_jsonld_parts: list[str] = []

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def h1(self) -> str:
        return " ".join("".join(self.h1_parts).split())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang", "") or ""
        if "id" in values:
            self.ids.add(values["id"] or "")
        if tag == "title":
            self.title_open = True
        if tag == "h1":
            self.h1_open = True
            self.h1_count += 1
        if tag == "meta":
            key = values.get("name") or values.get("property")
            content = values.get("content")
            if key and content is not None:
                self.meta[key.lower()].append(content)
        if tag == "link":
            rels = set((values.get("rel") or "").lower().split())
            href = values.get("href")
            if href:
                if "canonical" in rels:
                    self.canonicals.append(href)
                if "alternate" in rels and values.get("hreflang"):
                    self.alternates[values["hreflang"] or ""].append(href)
                if "describedby" in rels:
                    self.describedby.append(href)
                    self.resources.append(href)
                if "alternate" in rels and values.get("type", "").lower() == "text/markdown":
                    self.markdown_alternates.append(href)
                    self.resources.append(href)
                if rels.intersection({"stylesheet", "icon"}):
                    self.resources.append(href)
        if tag == "a" and values.get("href"):
            href = values["href"] or ""
            self.hrefs.append(href)
            if "data-ga4-placement" in values:
                self.analytics_ctas.append((href, values.get("data-ga4-placement") or ""))
            if "language-link" in (values.get("class") or "").split():
                self.language_links.append(values["href"] or "")
        if tag == "img" and values.get("src"):
            self.resources.append(values["src"] or "")
        if tag == "video":
            self.videos.append(values)
            if values.get("poster"):
                self.resources.append(values["poster"] or "")
            if values.get("src"):
                self.resources.append(values["src"] or "")
        if tag == "source" and values.get("src"):
            source = values["src"] or ""
            self.video_sources.append(source)
            self.video_source_types.append(values.get("type", "") or "")
            self.resources.append(source)
        if tag == "script":
            if values.get("src"):
                script_src = values["src"] or ""
                self.script_srcs.append(script_src)
                self.resources.append(script_src)
            if values.get("type", "").lower() == "application/ld+json":
                self.current_script_is_jsonld = True
                self.current_jsonld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.title_open = False
        if tag == "h1":
            self.h1_open = False
        if tag == "script" and self.current_script_is_jsonld:
            self.jsonld_parts.append("".join(self.current_jsonld_parts))
            self.current_script_is_jsonld = False
            self.current_jsonld_parts = []

    def handle_data(self, data: str) -> None:
        if self.title_open:
            self.title_parts.append(data)
        if self.h1_open:
            self.h1_parts.append(data)
        if self.current_script_is_jsonld:
            self.current_jsonld_parts.append(data)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_page(path: Path, errors: list[str]) -> PageParser:
    parser = PageParser()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        fail(errors, f"Cannot read {path.relative_to(ROOT)}: {exc}")
    return parser


def check_local_reference(page_file: Path, ref: str, pages: dict[Path, PageParser], errors: list[str]) -> None:
    parsed = urlparse(ref)
    if parsed.scheme or parsed.netloc:
        return
    path = unquote(parsed.path)
    if not path:
        target = page_file
    elif path.startswith("/"):
        target = ROOT / path.lstrip("/")
    else:
        target = page_file.parent / path
    if target.is_dir():
        target = target / "index.html"
    try:
        target = target.resolve()
        target.relative_to(ROOT)
    except ValueError:
        fail(errors, f"Reference escapes site root in {page_file.relative_to(ROOT)}: {ref}")
        return
    if not target.is_file():
        fail(errors, f"Missing local reference in {page_file.relative_to(ROOT)}: {ref}")
        return
    if parsed.fragment and target.suffix.lower() == ".html":
        destination = pages.get(target)
        if destination and unquote(parsed.fragment) not in destination.ids:
            fail(errors, f"Missing anchor in {page_file.relative_to(ROOT)}: {ref}")


def schema_types(value: object) -> list[dict]:
    found: list[dict] = []
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            found.append(value)
        elif isinstance(kind, list):
            found.append(value)
        for key, item in value.items():
            if key != "@type" and isinstance(item, (dict, list)):
                found.extend(schema_types(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(schema_types(item))
    return found


def markdown_links(path: Path, errors: list[str]) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        fail(errors, f"Cannot read {path.relative_to(ROOT)}: {exc}")
        return []
    if not any(line.startswith("# ") for line in source.splitlines()):
        fail(errors, f"Markdown source needs an H1: {path.relative_to(ROOT)}")
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", source)


def check_public_markdown_link(ref: str, source: Path, errors: list[str]) -> str | None:
    if ref == TESTFLIGHT_URL:
        return None
    parsed = urlparse(ref)
    if parsed.scheme != "https" or parsed.netloc != "hugehard.app":
        fail(errors, f"Markdown link must stay on the public site origin in {source.relative_to(ROOT)}: {ref}")
        return None
    target_path = unquote(parsed.path)
    target = ROOT / target_path.lstrip("/")
    if target.is_dir():
        target = target / "index.html"
    try:
        target = target.resolve()
        target.relative_to(ROOT)
    except ValueError:
        fail(errors, f"Markdown link escapes site root in {source.relative_to(ROOT)}: {ref}")
        return None
    if not target.is_file():
        fail(errors, f"Missing Markdown link target in {source.relative_to(ROOT)}: {ref}")
    return target_path


def main() -> int:
    errors: list[str] = []
    route_files: dict[str, Path] = {}
    route_parsers: dict[str, PageParser] = {}
    page_by_file: dict[Path, PageParser] = {}
    titles: dict[str, list[str]] = defaultdict(list)
    unique_descriptions: dict[str, list[str]] = defaultdict(list)

    for route, (relative, language) in ROUTES.items():
        file = (ROOT / relative).resolve()
        route_files[route] = file
        if not file.is_file():
            fail(errors, f"Missing page for {route}: {relative}")
            continue
        parser = parse_page(file, errors)
        route_parsers[route] = parser
        page_by_file[file] = parser
        expected_language = "zh-CN" if language == "zh-CN" else "en"
        if parser.lang != expected_language:
            fail(errors, f"Wrong html lang for {route}: expected {expected_language}, got {parser.lang}")
        if not parser.title or parser.h1_count != 1 or not parser.h1:
            fail(errors, f"Expected a title and exactly one h1 on {route}")
        titles[parser.title].append(route)
        page_descriptions = parser.meta.get("description", [])
        if len(page_descriptions) != 1 or not page_descriptions[0].strip():
            fail(errors, f"Expected one non-empty description on {route}")
        elif page_descriptions[0].strip():
            unique_descriptions[page_descriptions[0].strip()].append(route)
        for field in ("og:title", "og:description", "og:url", "og:image", "twitter:title", "twitter:description", "twitter:image"):
            if len(parser.meta.get(field, [])) != 1:
                fail(errors, f"Expected one {field} on {route}")
        if parser.meta.get("og:url", [""])[0] != f"{BASE}{route}":
            fail(errors, f"og:url does not match canonical route {route}")
        if parser.meta.get("og:image", [""])[0] != ICON or parser.meta.get("twitter:image", [""])[0] != ICON:
            fail(errors, f"Social image must use the shared app icon on {route}")
        if parser.meta.get("twitter:card", [""])[0] != "summary":
            fail(errors, f"Expected Twitter summary card on {route}")
        if len(parser.canonicals) != 1 or parser.canonicals[0] != f"{BASE}{route}":
            fail(errors, f"Canonical must be self-referencing for {route}")
        if parser.script_srcs.count(ANALYTICS_SCRIPT) != 1:
            fail(errors, f"Expected one shared site analytics/consent script on {route}")
        expected_describedby = ["/llms.txt"] if route in LLMS_DESCRIBED_ROUTES else []
        if parser.describedby != expected_describedby:
            fail(errors, f"Unexpected describedby target on {route}: {parser.describedby}")
        expected_markdown = [f"/{MARKDOWN_PAGES[route]}"] if route in MARKDOWN_PAGES else []
        if parser.markdown_alternates != expected_markdown:
            fail(errors, f"Unexpected Markdown alternate on {route}: {parser.markdown_alternates}")
        for ref in parser.describedby + parser.markdown_alternates:
            parsed_metadata_link = urlparse(ref)
            if parsed_metadata_link.scheme or parsed_metadata_link.netloc or not ref.startswith("/"):
                fail(errors, f"Metadata link must use a root-relative same-origin path on {route}: {ref}")
        for ref in parser.hrefs + parser.resources:
            parsed_ref = urlparse(ref)
            if not parsed_ref.scheme and not parsed_ref.netloc and Path(parsed_ref.path).name == "index.html":
                fail(errors, f"Internal link uses non-canonical index.html on {route}: {ref}")
        expected_analytics_ctas = (
            [(TESTFLIGHT_URL, TESTFLIGHT_HTML_PLACEMENTS[route])]
            if route in TESTFLIGHT_HTML_PLACEMENTS
            else []
        )
        if parser.analytics_ctas != expected_analytics_ctas:
            fail(errors, f"TestFlight analytics placements do not match the approved route map on {route}")
        if route in TESTFLIGHT_HTML_PLACEMENTS and parser.hrefs.count(TESTFLIGHT_URL) != 1:
            fail(errors, f"Expected one verified TestFlight link on {route}")
        if route not in TESTFLIGHT_HTML_PLACEMENTS and TESTFLIGHT_URL in parser.hrefs:
            fail(errors, f"Unexpected TestFlight link outside its approved route on {route}")

    # Parse all HTML first so internal fragment checks can resolve every page.
    for file in ROOT.rglob("*.html"):
        resolved = file.resolve()
        page_by_file.setdefault(resolved, parse_page(resolved, errors))
    for route, (relative, _) in ROUTES.items():
        file = route_files[route]
        parser = route_parsers.get(route)
        if not parser:
            continue
        for ref in parser.hrefs + parser.resources:
            check_local_reference(file, ref, page_by_file, errors)

    for title, routes in titles.items():
        if len(routes) > 1:
            fail(errors, f"Page titles should be unique: {title!r} on {', '.join(routes)}")
    for description, routes in unique_descriptions.items():
        if len(routes) > 1:
            fail(errors, f"Page descriptions should be unique: {', '.join(routes)}")

    # Each language pair declares itself, its counterpart, and Chinese x-default.
    for zh_route, en_route in LANGUAGE_PAIRS:
        zh = route_parsers.get(zh_route)
        en = route_parsers.get(en_route)
        if not zh or not en:
            continue
        for route, parser, zh_url, en_url in (
            (zh_route, zh, f"{BASE}{zh_route}", f"{BASE}{en_route}"),
            (en_route, en, f"{BASE}{zh_route}", f"{BASE}{en_route}"),
        ):
            expected = {"zh-Hans": [zh_url], "en": [en_url], "x-default": [zh_url]}
            if dict(parser.alternates) != expected:
                fail(errors, f"Incorrect hreflang pair on {route}: {dict(parser.alternates)}")
        zh_switch = [f"{BASE}{href}" if href.startswith("/") else href for href in zh.language_links]
        en_switch = [f"{BASE}{href}" if href.startswith("/") else href for href in en.language_links]
        if zh_switch != [f"{BASE}{en_route}"]:
            fail(errors, f"Chinese language switch must point to its English counterpart: {zh_route}")
        if en_switch != [f"{BASE}{zh_route}"]:
            fail(errors, f"English language switch must point to its Chinese counterpart: {en_route}")

    # 404 is explicitly excluded from indexing and has no canonical.
    not_found = parse_page(ROOT / "404.html", errors)
    if not not_found.title or not not_found.meta.get("description") or not_found.h1_count != 1:
        fail(errors, "404.html must retain its own title, description, and heading")
    if len(not_found.canonicals) != 0:
        fail(errors, "404.html must not declare a canonical")
    if not_found.meta.get("robots", [""])[0].replace(" ", "").lower() != "noindex,follow":
        fail(errors, "404.html must declare noindex,follow")
    if not_found.script_srcs:
        fail(errors, "404.html must not load analytics or transmit arbitrary request paths")
    for ref in not_found.hrefs + not_found.resources:
        parsed_ref = urlparse(ref)
        if parsed_ref.path and not parsed_ref.scheme and not parsed_ref.netloc and not ref.startswith("/"):
            fail(errors, f"404.html local references must use root-absolute paths: {ref}")
        check_local_reference(ROOT / "404.html", ref, page_by_file, errors)

    # Sitemap contains exactly the canonical, indexable routes.
    try:
        xml = ET.parse(ROOT / "sitemap.xml")
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = [node.text or "" for node in xml.findall(".//s:loc", namespace)]
        expected_urls = {f"{BASE}{route}" for route in ROUTES}
        if len(sitemap_urls) != len(set(sitemap_urls)):
            fail(errors, "sitemap.xml contains duplicate URLs")
        if set(sitemap_urls) != expected_urls:
            fail(errors, f"sitemap.xml URLs do not match canonical routes (found {len(sitemap_urls)}, expected {len(expected_urls)})")
        if any("index.html" in url for url in sitemap_urls):
            fail(errors, "sitemap.xml contains a non-canonical index.html URL")
    except (ET.ParseError, OSError) as exc:
        fail(errors, f"Cannot parse sitemap.xml: {exc}")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Allow: /" not in robots or f"Sitemap: {BASE}/sitemap.xml" not in robots:
        fail(errors, "robots.txt must allow crawling and advertise sitemap.xml")

    analytics_source = ROOT / ANALYTICS_SCRIPT.lstrip("/")
    if not analytics_source.is_file():
        fail(errors, "Missing the shared analytics/consent script")
    else:
        source = analytics_source.read_text(encoding="utf-8")
        measurement_ids = re.findall(r'measurementId:\s*"(G-[A-Z0-9]+)"', source)
        if len(measurement_ids) != 1:
            fail(errors, "The shared analytics script must have exactly one valid GA4 Measurement ID config")

    # llms.txt is an optional Markdown index, separate from the search sitemap.
    llms_file = ROOT / "llms.txt"
    llms_links = markdown_links(llms_file, errors)
    if llms_links.count(TESTFLIGHT_URL) != 1:
        fail(errors, "llms.txt must include the verified TestFlight link once")
    checked_llms_paths = [check_public_markdown_link(ref, llms_file, errors) for ref in llms_links]
    expected_llms_paths = set(ROUTES)
    expected_llms_paths.update(f"/{relative}" for relative in MARKDOWN_PAGES.values())
    if set(path for path in checked_llms_paths if path is not None) != expected_llms_paths:
        fail(errors, "llms.txt must link all canonical HTML routes and the four clean Markdown pages")
    if any(path.endswith("/llms.txt") for path in checked_llms_paths if path is not None):
        fail(errors, "llms.txt must not link to itself")
    markdown_file_paths = [ROOT / relative for relative in MARKDOWN_PAGES.values()]
    for markdown_file in markdown_file_paths:
        if not markdown_file.is_file():
            fail(errors, f"Missing clean Markdown page: {markdown_file.relative_to(ROOT)}")
            continue
        refs = markdown_links(markdown_file, errors)
        if refs.count(TESTFLIGHT_URL) != 1:
            fail(errors, f"Expected one verified TestFlight link in {markdown_file.relative_to(ROOT)}")
        for ref in refs:
            check_public_markdown_link(ref, markdown_file, errors)

    # Every JSON-LD block parses, and page-specific types match the visible pages.
    parsed_schemas: dict[str, list[dict]] = {}
    for route, parser in route_parsers.items():
        all_nodes: list[dict] = []
        for raw in parser.jsonld_parts:
            try:
                all_nodes.extend(schema_types(json.loads(raw)))
            except json.JSONDecodeError as exc:
                fail(errors, f"Invalid JSON-LD on {route}: {exc}")
        parsed_schemas[route] = all_nodes
        types = {node.get("@type") for node in all_nodes}
        if route in ("/", "/en/"):
            if not {"Organization", "WebSite"}.issubset(types):
                fail(errors, f"Home page needs Organization and WebSite JSON-LD: {route}")
        elif route in ("/apps/this-pic-can-change/", "/en/apps/this-pic-can-change/"):
            page_nodes = [node for node in all_nodes if node.get("@type") == "WebPage"]
            app_nodes = [node for node in all_nodes if node.get("@type") == "SoftwareApplication"]
            about_nodes = [node for node in all_nodes if node.get("@type") == "Thing" and node.get("@id") == f"{BASE}/apps/this-pic-can-change/#application"]
            if len(page_nodes) != 1 or len(about_nodes) != 1 or app_nodes:
                fail(errors, f"Product page needs one WebPage/about Thing and no SoftwareApplication: {route}")
            else:
                product_page = page_nodes[0]
                about = about_nodes[0]
                expected_language = ROUTES[route][1]
                if product_page.get("url") != f"{BASE}{route}" or product_page.get("inLanguage") != expected_language:
                    fail(errors, f"Product WebPage URL or language must match its canonical: {route}")
                if product_page.get("isPartOf", {}).get("@id") != f"{BASE}/#website":
                    fail(errors, f"Product WebPage must point to the shared WebSite entity: {route}")
                if product_page.get("publisher", {}).get("@id") != f"{BASE}/#organization":
                    fail(errors, f"Product WebPage must point to the shared Organization entity: {route}")
                if about.get("name") != "这图能改" or about.get("alternateName") != "This Pic Can Change":
                    fail(errors, f"Product Thing must keep the Chinese name and English site rendering consistent: {route}")
                if "operatingSystem" in about or "operatingSystem" in product_page:
                    fail(errors, f"Product entity must not imply English app UI or unverified app availability: {route}")
        elif route.startswith("/guides/") or route.startswith("/en/guides/"):
            if route not in ("/guides/", "/en/guides/"):
                articles = [node for node in all_nodes if node.get("@type") == "Article"]
                crumbs = [node for node in all_nodes if node.get("@type") == "BreadcrumbList"]
                if len(articles) != 1 or len(crumbs) != 1:
                    fail(errors, f"Guide article needs Article and BreadcrumbList JSON-LD: {route}")
                else:
                    article = articles[0]
                    if article.get("mainEntityOfPage", {}).get("@id") != f"{BASE}{route}":
                        fail(errors, f"Article mainEntityOfPage must match canonical: {route}")
                    if article.get("author", {}).get("name") != "HugeHard Studio":
                        fail(errors, f"Article author must be HugeHard Studio: {route}")
                    expected_language = "en" if route.startswith("/en/") else "zh-CN"
                    if article.get("inLanguage") != expected_language:
                        fail(errors, f"Article language does not match page: {route}")
                    items = crumbs[0].get("itemListElement", [])
                    expected_breadcrumb_urls = (
                        [f"{BASE}/en/", f"{BASE}/en/guides/", f"{BASE}{route}"]
                        if route.startswith("/en/")
                        else [f"{BASE}/", f"{BASE}/guides/", f"{BASE}{route}"]
                    )
                    actual_breadcrumb_urls = [item.get("item") for item in items]
                    if actual_breadcrumb_urls != expected_breadcrumb_urls:
                        fail(errors, f"Breadcrumb URLs do not match route hierarchy: {route}")

    video_routes = ("/guides/video-to-live-photo/", "/en/guides/video-to-live-photo/")
    video_object_id = f"{BASE}/#live-photo-demo"
    video_content_url = f"{BASE}/assets/video-to-live-photo-demo.mp4"
    video_thumbnail_url = f"{BASE}/apps/this-pic-can-change/assets/04-livephoto-result.jpeg"
    for route, parser in route_parsers.items():
        if route not in video_routes:
            if parser.videos or parser.video_sources:
                fail(errors, f"Unexpected video player outside the approved Live Photo guide: {route}")
            continue
        if len(parser.videos) != 1 or parser.video_sources != ["/assets/video-to-live-photo-demo.mp4"]:
            fail(errors, f"Live Photo guide must use the approved local demo video once: {route}")
        if parser.video_source_types != ["video/mp4"]:
            fail(errors, f"Live Photo demo source must be declared as video/mp4: {route}")
        if len(parser.videos) == 1:
            player = parser.videos[0]
            expected_poster = "/apps/this-pic-can-change/assets/04-livephoto-result.jpeg"
            if player.get("poster") != expected_poster:
                fail(errors, f"Live Photo demo must use the approved screenshot poster: {route}")
            if not {"controls", "playsinline"}.issubset(player) or player.get("preload") != "none" or "autoplay" in player:
                fail(errors, f"Live Photo demo must be user-controlled, inline, and non-autoplaying: {route}")
            if player.get("width") != "720" or player.get("height") != "1564":
                fail(errors, f"Live Photo demo dimensions must match the source video: {route}")
        objects = [node for node in parsed_schemas.get(route, []) if node.get("@type") == "VideoObject"]
        if len(objects) != 1:
            fail(errors, f"Live Photo guide needs exactly one VideoObject: {route}")
        else:
            video = objects[0]
            if video.get("@id") != video_object_id or video.get("contentUrl") != video_content_url:
                fail(errors, f"VideoObject contentUrl and shared @id must match the embedded asset: {route}")
            if video.get("thumbnailUrl") != video_thumbnail_url:
                fail(errors, f"VideoObject thumbnail must use the approved screenshot: {route}")
            if video.get("duration") != "PT19S" or video.get("uploadDate") != "2026-10-14T12:50:25Z":
                fail(errors, f"VideoObject duration and first-publication date must match the reviewed clip: {route}")
            if video.get("inLanguage") != "zh-Hans":
                fail(errors, f"VideoObject language must describe the Simplified Chinese app UI: {route}")
            if any(key in video for key in ("interactionStatistic", "userInteractionCount", "aggregateRating", "review")):
                fail(errors, f"VideoObject must not invent viewing statistics or ratings: {route}")

    zh_home = parsed_schemas.get("/", [])
    en_home = parsed_schemas.get("/en/", [])
    zh_website = next((node for node in zh_home if node.get("@type") == "WebSite"), {})
    en_website = next((node for node in en_home if node.get("@type") == "WebSite"), {})
    if zh_website.get("@id") != en_website.get("@id") or zh_website.get("url") != en_website.get("url"):
        fail(errors, "Chinese and English home pages must share the same WebSite @id and URL")
    if zh_website.get("inLanguage") != ["zh-Hans", "en"] or en_website.get("inLanguage") != ["zh-Hans", "en"]:
        fail(errors, "The shared WebSite entity must declare both zh-Hans and en languages")

    zh_product = parsed_schemas.get("/apps/this-pic-can-change/", [])
    en_product = parsed_schemas.get("/en/apps/this-pic-can-change/", [])
    zh_about = next((node for node in zh_product if node.get("@type") == "Thing"), {})
    en_about = next((node for node in en_product if node.get("@type") == "Thing"), {})
    for prop in ("@id", "name", "alternateName"):
        if zh_about.get(prop) != en_about.get(prop):
            fail(errors, f"Chinese and English product pages must share the same about Thing {prop}")

    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Site validation passed: {len(ROUTES)} canonical routes, {len(LANGUAGE_PAIRS)} language pairs, llms.txt and Markdown links, sitemap, local references, and JSON-LD.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
