#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHOLIC PHOTO EXTRACTOR v1.0
Extrai fotos reais de perfis públicos do Google Maps e Instagram
sem precisar de API key, usando scraping via requests + BeautifulSoup
e, quando disponível, Playwright.

Dependências:
  pip install requests beautifulsoup4 pillow
  (opcional para Maps): playwright install chromium

Uso:
  python scripts/extrair-fotos.py --slug "cafe-shin" --maps "https://maps.google.com/?cid=XXX" --instagram "cafeshinparis"
  python scripts/extrair-fotos.py --slug "cafe-shin" --maps-query "Café Shin Paris 10e" --instagram "cafeshinparis"
"""

import os
import sys
import re
import json
import time
import argparse
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

RAIZ = Path(__file__).parent.parent
SITES_DIR = RAIZ / 'sites'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}


# ─── Utilities ───────────────────────────────────────────────────────────────

def download_image(url: str, dest: Path, label: str = ''):
    """Download an image file from a URL."""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': HEADERS['User-Agent'],
            'Referer': 'https://www.google.com/',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if len(data) < 2000:  # skip tiny placeholders
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, 'wb') as f:
            f.write(data)
        print(f'  ✅ {label}: {dest.name} ({len(data)//1024}KB)')
        return True
    except Exception as e:
        print(f'  ⚠️  Falha ao baixar {label}: {e}')
        return False


def slugify_url(url: str) -> str:
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    return h


# ─── Instagram (public profile, no login) ────────────────────────────────────

def fetch_instagram_photos(username: str, slug: str, max_photos: int = 9):
    """
    Fetch recent photo URLs from a public Instagram profile
    using the unofficial embed endpoint (no API key required).
    """
    assets_dir = SITES_DIR / slug / 'assets' / 'fotos'
    assets_dir.mkdir(parents=True, exist_ok=True)

    username = username.lstrip('@')
    print(f'\n📸 Instagram: @{username}')

    saved = []

    # Method 1: Instagram embed JSON endpoint
    try:
        url = f'https://www.instagram.com/{username}/?__a=1&__d=dis'
        if HAS_REQUESTS:
            session = requests.Session()
            session.headers.update(HEADERS)
            resp = session.get(url, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                edges = data.get('graphql', {}).get('user', {}).get('edge_owner_to_timeline_media', {}).get('edges', [])
                for i, edge in enumerate(edges[:max_photos]):
                    node = edge.get('node', {})
                    img_url = node.get('display_url') or node.get('thumbnail_src')
                    if img_url:
                        dest = assets_dir / f'instagram-{i+1:02d}.jpg'
                        if download_image(img_url, dest, f'Instagram foto {i+1}'):
                            saved.append(str(dest.relative_to(SITES_DIR / slug)))
    except Exception as e:
        print(f'  ⚠️  Método 1 falhou: {e}')

    # Method 2: Scrape the embed page for thumbnail URLs
    if not saved:
        try:
            embed_url = f'https://www.instagram.com/{username}/embed/'
            if HAS_REQUESTS:
                session = requests.Session()
                session.headers.update(HEADERS)
                resp = session.get(embed_url, timeout=12)
                soup = BeautifulSoup(resp.text, 'html.parser')
                imgs = soup.find_all('img', src=re.compile(r'instagram'))
                for i, img in enumerate(imgs[:max_photos]):
                    src = img.get('src', '')
                    if src and 'profile_pic' not in src:
                        dest = assets_dir / f'instagram-{i+1:02d}.jpg'
                        if download_image(src, dest, f'Instagram embed foto {i+1}'):
                            saved.append(str(dest.relative_to(SITES_DIR / slug)))
        except Exception as e:
            print(f'  ⚠️  Método 2 falhou: {e}')

    # Method 3: Playwright fallback (if available)
    if not saved:
        saved = _fetch_instagram_playwright(username, slug, assets_dir, max_photos)

    print(f'  📷 {len(saved)} fotos salvas do Instagram')
    return saved


def _fetch_instagram_playwright(username: str, slug: str, assets_dir: Path, max_photos: int):
    """Use Playwright to load the Instagram profile page and capture image URLs."""
    saved = []
    try:
        from playwright.sync_api import sync_playwright
        print('  🤖 Usando Playwright para Instagram...')
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers(HEADERS)
            page.goto(f'https://www.instagram.com/{username}/', wait_until='networkidle', timeout=20000)
            time.sleep(2)

            imgs = page.query_selector_all('img[srcset]')
            seen = set()
            for i, img in enumerate(imgs):
                if len(saved) >= max_photos:
                    break
                src = img.get_attribute('src') or ''
                if not src or src in seen or 'profile_pic' in src or '150x150' in src:
                    continue
                seen.add(src)
                dest = assets_dir / f'instagram-{len(saved)+1:02d}.jpg'
                if download_image(src, dest, f'Instagram Playwright {len(saved)+1}'):
                    saved.append(str(dest.relative_to(Path(str(assets_dir)).parent.parent)))
            browser.close()
    except ImportError:
        print('  ℹ️  Playwright não disponível (pip install playwright && playwright install chromium)')
    except Exception as e:
        print(f'  ⚠️  Playwright Instagram falhou: {e}')
    return saved


# ─── Google Maps (Playwright-first, requests fallback) ───────────────────────

def fetch_maps_photos(query_or_url: str, slug: str, max_photos: int = 6):
    """
    Fetch photos from a Google Maps listing.
    query_or_url: a Google Maps URL (https://maps.app.goo.gl/... or https://maps.google.com/...)
                  or a plain text query like "Café Shin 47 Rue des Petites-Écuries Paris"
    """
    assets_dir = SITES_DIR / slug / 'assets' / 'fotos'
    assets_dir.mkdir(parents=True, exist_ok=True)

    print(f'\n🗺️  Google Maps: {query_or_url[:60]}...' if len(query_or_url) > 60 else f'\n🗺️  Google Maps: {query_or_url}')

    saved = _fetch_maps_playwright(query_or_url, slug, assets_dir, max_photos)

    if not saved:
        saved = _fetch_maps_serp(query_or_url, slug, assets_dir, max_photos)

    print(f'  📷 {len(saved)} fotos salvas do Maps')
    return saved


def _fetch_maps_playwright(query_or_url: str, slug: str, assets_dir: Path, max_photos: int):
    """Load the Maps listing with Playwright and intercept image requests."""
    saved = []
    try:
        from playwright.sync_api import sync_playwright
        print('  🤖 Usando Playwright para Maps...')

        intercepted_urls = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS['User-Agent'],
                locale='pt-BR',
            )
            page = context.new_page()

            # Intercept image responses
            def on_response(response):
                url = response.url
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type and 'googleusercontent' in url and len(url) > 80:
                    if url not in intercepted_urls:
                        intercepted_urls.append(url)

            page.on('response', on_response)

            # Navigate
            if 'maps' in query_or_url or 'goo.gl' in query_or_url:
                page.goto(query_or_url, wait_until='networkidle', timeout=25000)
            else:
                encoded = urllib.parse.quote_plus(query_or_url)
                page.goto(f'https://www.google.com/maps/search/{encoded}', wait_until='networkidle', timeout=25000)

            time.sleep(3)

            # Scroll to trigger lazy loads
            for _ in range(3):
                page.keyboard.press('End')
                time.sleep(1)

            # Try clicking the photos tab
            try:
                photos_btn = page.query_selector('button[aria-label*="Photo"], button[aria-label*="Foto"], [data-tab-index="1"]')
                if photos_btn:
                    photos_btn.click()
                    time.sleep(2)
                    for _ in range(2):
                        page.keyboard.press('End')
                        time.sleep(1)
            except Exception:
                pass

            browser.close()

        # Download intercepted images (deduplicate, pick best resolution)
        seen_bases = set()
        for url in intercepted_urls:
            if len(saved) >= max_photos:
                break
            # Extract base URL without size params
            base = re.sub(r'=w\d+.*$', '', url)
            if base in seen_bases:
                continue
            seen_bases.add(base)
            # Request at 1200px width
            hi_res = base + '=w1200-h800-k-no'
            dest = assets_dir / f'maps-{len(saved)+1:02d}.jpg'
            if download_image(hi_res, dest, f'Maps foto {len(saved)+1}'):
                saved.append(str(dest.relative_to(SITES_DIR / slug)))
            elif download_image(url, dest, f'Maps foto {len(saved)+1} (original)'):
                saved.append(str(dest.relative_to(SITES_DIR / slug)))

    except ImportError:
        print('  ℹ️  Playwright não disponível — usando método alternativo')
    except Exception as e:
        print(f'  ⚠️  Playwright Maps falhou: {e}')

    return saved


def _fetch_maps_serp(query: str, slug: str, assets_dir: Path, max_photos: int):
    """Fallback: search Google Images for the establishment name and grab results."""
    saved = []
    if not HAS_REQUESTS:
        return saved

    try:
        search_term = query if not query.startswith('http') else slug.replace('-', ' ')
        encoded = urllib.parse.quote_plus(f'{search_term} café photos')
        url = f'https://www.google.com/search?q={encoded}&tbm=isch&hl=pt-BR'

        session = requests.Session()
        session.headers.update(HEADERS)
        resp = session.get(url, timeout=12)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Extract image URLs from Google Images JSON blobs
        img_urls = re.findall(r'"(https://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"', resp.text)
        seen = set()
        for img_url in img_urls:
            if len(saved) >= max_photos:
                break
            if img_url in seen or len(img_url) < 50:
                continue
            seen.add(img_url)
            dest = assets_dir / f'maps-{len(saved)+1:02d}.jpg'
            if download_image(img_url, dest, f'Google Images {len(saved)+1}'):
                saved.append(str(dest.relative_to(SITES_DIR / slug)))

    except Exception as e:
        print(f'  ⚠️  Fallback Google Images falhou: {e}')

    return saved


# ─── Photo catalog ─────────────────────────────────────────────────────────

def save_photo_catalog(slug: str, maps_photos: list, instagram_photos: list):
    """Save a JSON catalog of all photos found."""
    catalog = {
        'slug': slug,
        'total': len(maps_photos) + len(instagram_photos),
        'maps': maps_photos,
        'instagram': instagram_photos,
        'hero_candidate': (maps_photos + instagram_photos + [''])[0],
        'gallery': (maps_photos + instagram_photos)[:9],
    }
    out = SITES_DIR / slug / 'assets' / 'fotos.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f'\n📄 Catálogo de fotos salvo: {out}')
    return catalog


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Aholic Photo Extractor — fotos reais do Maps e Instagram'
    )
    parser.add_argument('--slug',       required=True, help='Slug do lead (ex: cafe-shin)')
    parser.add_argument('--maps',       help='URL do Google Maps do estabelecimento')
    parser.add_argument('--maps-query', help='Busca textual do Maps (ex: "Café Shin Paris 10e")')
    parser.add_argument('--instagram',  help='Username do Instagram (com ou sem @)')
    parser.add_argument('--max',        type=int, default=8, help='Máximo de fotos por fonte (default: 8)')
    args = parser.parse_args()

    slug = args.slug
    maps_source = args.maps or args.maps_query
    instagram = args.instagram
    max_photos = args.max

    maps_photos = []
    instagram_photos = []

    if maps_source:
        maps_photos = fetch_maps_photos(maps_source, slug, max_photos)

    if instagram:
        instagram_photos = fetch_instagram_photos(instagram, slug, max_photos)

    if not maps_source and not instagram:
        print('⚠️  Informe ao menos --maps ou --instagram')
        sys.exit(1)

    catalog = save_photo_catalog(slug, maps_photos, instagram_photos)

    print(f'\n✅ Total de fotos baixadas: {catalog["total"]}')
    print(f'   Hero sugerida: {catalog["hero_candidate"]}')

    return catalog


if __name__ == '__main__':
    main()
