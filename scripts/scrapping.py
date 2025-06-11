#!/usr/bin/env python3
"""
download_die_linke_documents.py
--------------------------------
Recursively download all PDFs and full-text resolution pages
from Die Linke's Parteitag & Parteivorstand sections.

Usage:
    python download_die_linke_documents.py

Dependencies:
    pip install requests beautifulsoup4
"""

import os
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# === CONFIGURATION ============================================================
START_URLS = [
    "https://www.die-linke.de/partei/parteidemokratie/parteitag/parteitage-der-partei-die-linke-archiv/",
    "https://www.die-linke.de/partei/parteidemokratie/parteivorstand/parteivorstand-2024-2026/beschluesse/",
]

OUTPUT_DIR = "internal_docs"     # Everything lands in this folder
DELAY_SEC  = 1                   # Be polite: wait between requests
HEADERS    = {                   # Minimal, honest UA string
    "User-Agent": "DieLinkeScraper/1.0 (+github.com/your-org/your-repo)"
}
# ==============================================================================

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def slugify(url: str, default: str = "index") -> str:
    """
    Turn a URL into a safe filename (keeps the original PDF basename when possible).
    """
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    if not path:
        return default
    # Use the last two parts of the path to ensure uniqueness
    parts = path.split('/')[-2:]
    name = '-'.join(parts) or default
    # sanitise anything weird
    name = re.sub(r"[^\w.\-]+", "-", name)
    return name.lower()


def fetch(url: str) -> requests.Response:
    """GET with basic error handling & throttling."""
    time.sleep(DELAY_SEC)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None  # Return None instead of raising to allow the script to continue


def save_pdf(url: str, folder: str) -> None:
    """Download and write a PDF file exactly as delivered."""
    fname = slugify(url)
    if not fname.endswith(".pdf"):
        fname += ".pdf"

    path = os.path.join(folder, fname)
    if os.path.exists(path):           # already saved
        return

    logger.info(f"⭳ PDF   {url}")
    resp = fetch(url)
    if resp is None:  # Skip if fetch failed
        return
    with open(path, "wb") as fh:
        fh.write(resp.content)


def save_html(url: str, folder: str) -> BeautifulSoup | None:
    """
    Download an HTML page, save it, and return a BeautifulSoup object
    so we can continue crawling.
    """
    fname = slugify(url, default="index") + ".html"
    path  = os.path.join(folder, fname)

    logger.info(f"⭳ HTML  {url}")
    resp = fetch(url)
    if resp is None:  # Skip if fetch failed
        return None

    with open(path, "wb") as fh:
        fh.write(resp.content)

    return BeautifulSoup(resp.text, "html.parser")


def crawl() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    seen: set[str] = set()
    pdf_count = 0
    html_count = 0

    def _walk_page(page_url: str) -> None:
        nonlocal pdf_count, html_count
        if page_url in seen:
            return
        seen.add(page_url)

        soup = save_html(page_url, OUTPUT_DIR)
        if soup is None:
            return
        html_count += 1

        # find every <a href="…">
        for tag in soup.find_all("a", href=True):
            href = tag["href"].strip()
            if not href or href.startswith("#"):
                continue

            url = urljoin(page_url, href)

            # skip off-site links
            if not url.startswith("https://www.die-linke.de/"):
                continue

            if url in seen:
                continue

            if url.lower().endswith(".pdf"):
                save_pdf(url, OUTPUT_DIR)
                seen.add(url)
                pdf_count += 1
            elif any(keyword in url for keyword in ("/beschluesse/", "/parteitag/")):
                _walk_page(url)   # recurse into resolution / congress pages

    for root in START_URLS:
        _walk_page(root)

    logger.info(f"\nDone! Files saved in: {os.path.abspath(OUTPUT_DIR)}")
    logger.info(f"Downloaded {pdf_count} PDFs and {html_count} HTML files.")


if __name__ == "__main__":
    crawl()