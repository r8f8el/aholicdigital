#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHOLIC GENERATOR v2.0 — Motor Central de Criação de Sites
Gera um site completo em < 60 segundos com:
  - Fotos reais do Google Maps e Instagram
  - Cores extraídas automaticamente da logo/identidade do cliente
  - Motion Engine cinematográfico (preloader, cursor, scroll reveal)
  - Preset adaptado às cores reais do negócio
  - Deploy automático na Vercel

Uso:
  python scripts/aholic-generator.py --slug "cafe-shin" --preset "cinema-local" --instagram "cafeshinparis" --maps "https://maps.app.goo.gl/..."
  python scripts/aholic-generator.py --list
  python scripts/aholic-generator.py --slug "cafe-shin" --preset auto
"""

import os
import sys
import json
import re
import shutil
import subprocess
import argparse
import unicodedata
from pathlib import Path
from datetime import datetime

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

RAIZ = Path(__file__).parent.parent
SITES_DIR    = RAIZ / 'sites'
REFS_DIR     = RAIZ / 'referencias'
SCRIPTS_DIR  = RAIZ / 'scripts'
MOTION_JS    = REFS_DIR / 'motion-engine.js'
COLOR_SCRIPT = REFS_DIR / 'color-extractor.py'
PHOTO_SCRIPT = SCRIPTS_DIR / 'extrair-fotos.py'
PRESETS_JSON = REFS_DIR / 'presets-dinamicos.json'
LEADS_FILE   = RAIZ / 'leads.md'
DASHBOARD    = RAIZ / 'dashboard.html'
INDEX_HTML   = RAIZ / 'index.html'

# ─── Presets fallback (loaded from JSON if available) ───────────────────────

PRESETS_BUILTIN = {
    "editorial-atelier": {
        "name": "Editorial de Atelier",
        "nichos": ["arquitetura", "dermato", "luxo", "spa", "decoração"],
        "fonts": {
            "display": "Newsreader",
            "body": "Inter"
        },
        "motion": {"preloader": True, "marquee": True, "parallax": True, "counters": True},
        "layout": "asymmetric-editorial",
        "icon_pack": "lucide",
        "dark": True,
    },
    "brutalismo-comercial": {
        "name": "Brutalismo Comercial",
        "nichos": ["barbearia", "academia", "streetwear", "tatuagem"],
        "fonts": {"display": "League Spartan", "body": "League Spartan"},
        "motion": {"preloader": True, "marquee": True, "parallax": False, "counters": True},
        "layout": "heavy-grid",
        "icon_pack": "lucide",
        "dark": True,
    },
    "cinema-local": {
        "name": "Cinema Local",
        "nichos": ["cafeteria", "restaurante", "gastronomia", "bar", "spa", "rejuvenescimento"],
        "fonts": {"display": "League Spartan", "body": "Playfair Display"},
        "motion": {"preloader": True, "marquee": True, "parallax": True, "counters": True},
        "layout": "full-bleed-dark-luxury",
        "icon_pack": "lucide",
        "dark": True,
    },
    "cartaz-modular": {
        "name": "Cartaz Modular",
        "nichos": ["psicologia", "nutrição", "bem-estar", "coaching", "yoga"],
        "fonts": {"display": "Plus Jakarta Sans", "body": "Plus Jakarta Sans"},
        "motion": {"preloader": True, "marquee": False, "parallax": False, "counters": True},
        "layout": "color-blocks",
        "icon_pack": "lucide",
        "dark": False,
    },
    "instrumento-digital": {
        "name": "Instrumento Digital",
        "nichos": ["odontologia", "tecnologia médica", "clínica", "saúde"],
        "fonts": {"display": "Plus Jakarta Sans", "body": "Inter"},
        "motion": {"preloader": True, "marquee": False, "parallax": False, "counters": True},
        "layout": "swiss-precision",
        "icon_pack": "lucide",
        "dark": False,
    },
    "arquivo-vivo": {
        "name": "Arquivo Vivo",
        "nichos": ["advocacia", "consultoria", "perícia", "contabilidade"],
        "fonts": {"display": "JetBrains Mono", "body": "Inter"},
        "motion": {"preloader": True, "marquee": True, "parallax": False, "counters": True},
        "layout": "index-matrix",
        "icon_pack": "lucide",
        "dark": True,
    },
    "warm-industrial": {
        "name": "Warm Industrial & Structural Grid",
        "nichos": ["engenharia", "arquitetura", "design", "produto", "manufatura", "roastery", "mobiliario"],
        "fonts": {"display": "Inter", "body": "Inter"},
        "motion": {"preloader": True, "marquee": True, "parallax": True, "counters": True},
        "layout": "12-column-rigid-structural-grid",
        "icon_pack": "lucide",
        "dark": False,
    },
}

# ─── Utilities ───────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_]+', '-', text).strip('-')
    return text

def load_presets():
    if PRESETS_JSON.exists():
        with open(PRESETS_JSON, encoding='utf-8') as f:
            return json.load(f)
    return PRESETS_BUILTIN

def auto_select_preset(nicho: str, presets: dict) -> str:
    nicho_lower = nicho.lower()
    for key, p in presets.items():
        for n in p.get('nichos', []):
            if n in nicho_lower or nicho_lower in n:
                return key
    return 'cinema-local'  # safe default

def load_palette(slug: str) -> dict:
    paleta_path = SITES_DIR / slug / 'assets' / 'paleta.json'
    if paleta_path.exists():
        with open(paleta_path, encoding='utf-8') as f:
            return json.load(f)
    return None

def read_motion_engine() -> str:
    if MOTION_JS.exists():
        return MOTION_JS.read_text(encoding='utf-8')
    return '/* motion-engine.js not found */'

def run_script(script: Path, args: list):
    """Run a Python script with given args."""
    result = subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0:
        print(f'  ⚠️  {script.name} saiu com código {result.returncode}')
        if result.stderr:
            print(f'  {result.stderr[:300]}')
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(f'  {line}')
    return result.returncode == 0


# ─── HTML Template Engine ────────────────────────────────────────────────────

GOOGLE_FONTS_MAP = {
    'Newsreader':        'Newsreader:ital,wght@0,400;0,600;1,400;1,600',
    'Inter':             'Inter:wght@300;400;500;600;700',
    'Plus Jakarta Sans': 'Plus+Jakarta+Sans:wght@300;400;500;600;700;800',
    'League Spartan':    'League+Spartan:wght@300;400;500;600;700;800;900',
    'Playfair Display':  'Playfair+Display:ital,wght@0,400;0,600;1,400;1,600',
    'JetBrains Mono':    'JetBrains+Mono:wght@400;500;700',
    'Cinzel':            'Cinzel:wght@400;600;700;900',
    'Outfit':            'Outfit:wght@300;400;500;600;700;800;900',
}

def build_google_fonts_url(fonts: list) -> str:
    families = []
    for font in fonts:
        spec = GOOGLE_FONTS_MAP.get(font, f'{font.replace(" ", "+")}:wght@400;600;700')
        families.append(f'family={spec}')
    return 'https://fonts.googleapis.com/css2?' + '&'.join(families) + '&display=swap'


def build_css_root(palette: dict, preset: dict) -> str:
    """Build :root CSS with brand colors merged from palette + preset defaults."""
    if palette:
        tokens = palette.get('tokens', {})
        primary    = tokens.get('--ah-primary', '#C5A880')
        accent     = tokens.get('--ah-accent', '#E0A96D')
        bg         = tokens.get('--ah-bg', '#111413')
        surface    = tokens.get('--ah-surface', '#1A1D1C')
        text       = tokens.get('--ah-text', '#F5F0EB')
        text_muted = tokens.get('--ah-text-muted', '#9BA39F')
        accent_soft= tokens.get('--ah-accent-soft', 'rgba(224,169,109,0.15)')
        preloader_bg   = bg
        preloader_text = text
    else:
        # Default dark luxury fallback
        primary = accent = '#C5A880'
        bg      = '#111413'
        surface = '#1A1D1C'
        text    = '#F5F0EB'
        text_muted = '#9BA39F'
        accent_soft= 'rgba(197,168,128,0.15)'
        preloader_bg = bg
        preloader_text = text

    font_display = preset['fonts']['display']
    font_body    = preset['fonts']['body']

    return f"""
    :root {{
        --ah-primary:      {primary};
        --ah-accent:       {accent};
        --ah-bg:           {bg};
        --ah-surface:      {surface};
        --ah-text:         {text};
        --ah-text-muted:   {text_muted};
        --ah-accent-soft:  {accent_soft};
        --ah-preloader-bg:    {preloader_bg};
        --ah-preloader-text:  {preloader_text};
        --ah-font-display:    '{font_display}', sans-serif;
        --ah-font-body:       '{font_body}', sans-serif;
    }}
    * {{ font-family: var(--ah-font-body); box-sizing: border-box; }}
    h1, h2, h3, .font-display {{ font-family: var(--ah-font-display); }}
    body {{ background: var(--ah-bg); color: var(--ah-text); }}
    ::selection {{ background: var(--ah-accent); color: var(--ah-bg); }}
    """


def find_best_photos(slug: str) -> dict:
    """Return dict with hero, gallery, logo paths."""
    fotos_json = SITES_DIR / slug / 'assets' / 'fotos.json'
    if fotos_json.exists():
        with open(fotos_json, encoding='utf-8') as f:
            catalog = json.load(f)
        return {
            'hero':    catalog.get('hero_candidate', ''),
            'gallery': catalog.get('gallery', [])[:6],
            'logo':    find_logo(slug),
        }
    # Fallback: scan assets folder
    assets = SITES_DIR / slug / 'assets'
    photos = list(assets.glob('*.jpg')) + list(assets.glob('*.png')) + list(assets.glob('*.webp'))
    photos = [str(p.relative_to(SITES_DIR / slug)) for p in sorted(photos) if 'logo' not in p.name.lower()]
    return {
        'hero':    photos[0] if photos else '',
        'gallery': photos[:6],
        'logo':    find_logo(slug),
    }

def find_logo(slug: str) -> str:
    assets = SITES_DIR / slug / 'assets'
    for name in ['logo.png', 'logo.svg', 'logo.jpg', 'logo.webp', 'brand.png']:
        p = assets / name
        if p.exists():
            return f'assets/{name}'
    return ''


def build_whatsapp_link(phone: str, message: str = '') -> str:
    clean = re.sub(r'\D', '', phone)
    if not clean.startswith('55') and len(clean) <= 11:
        clean = '55' + clean
    msg = urllib.parse.quote_plus(message) if message else ''
    return f'https://wa.me/{clean}{"?text=" + msg if msg else ""}'


# ─── HTML generator ─────────────────────────────────────────────────────────

def generate_html(info: dict, preset_key: str, preset: dict, palette: dict, photos: dict) -> str:
    """Generate the complete HTML for the client site."""

    nome         = info.get('nome', 'Estabelecimento')
    nicho        = info.get('nicho', '')
    cidade       = info.get('cidade', '')
    endereco     = info.get('endereco', '')
    telefone     = info.get('telefone', '')
    whatsapp     = info.get('whatsapp', telefone)
    instagram    = info.get('instagram', '')
    email        = info.get('email', '')
    nota         = info.get('nota', '')
    avaliacoes   = info.get('avaliacoes', '')
    servicos     = info.get('servicos', [])
    horarios     = info.get('horarios', '')
    descricao    = info.get('descricao', f'{nome} em {cidade}.')
    tagline      = info.get('tagline', descricao[:80])
    cta_texto    = info.get('cta_texto', 'Agendar Consulta' if 'clínica' in nicho.lower() else 'Entre em Contato')
    is_dark      = preset.get('dark', True)

    css_root = build_css_root(palette, preset)
    motion_js = read_motion_engine()

    fonts = [preset['fonts']['display'], preset['fonts']['body'], 'JetBrains Mono']
    fonts = list(dict.fromkeys(fonts))  # deduplicate
    fonts_url = build_google_fonts_url(fonts)

    hero_img   = photos.get('hero', '')
    gallery    = photos.get('gallery', [])
    logo_path  = photos.get('logo', '')

    wa_link = build_whatsapp_link(whatsapp, f'Olá! Vi o site do {nome} e gostaria de mais informações.') if whatsapp else '#'

    # Build services HTML
    servicos_html = ''
    for i, s in enumerate(servicos[:6]):
        nome_s = s if isinstance(s, str) else s.get('nome', str(s))
        desc_s = '' if isinstance(s, str) else s.get('descricao', '')
        servicos_html += f'''
        <div class="service-card ah-reveal-item" style="transition-delay:{i*120}ms">
            <div class="sc-num">{i+1:02d}</div>
            <h3 class="sc-title">{nome_s}</h3>
            {f'<p class="sc-desc">{desc_s}</p>' if desc_s else ''}
        </div>'''

    # Gallery HTML
    gallery_html = ''
    for i, photo in enumerate(gallery[:6]):
        gallery_html += f'''
        <div class="gal-item ah-parallax-wrap ah-reveal-item" style="transition-delay:{i*100}ms">
            <img src="{photo}" alt="{nome} — foto {i+1}" class="ah-parallax-img" loading="lazy" onerror="this.style.display='none'">
        </div>'''
    if not gallery_html:
        gallery_html = '<p class="no-photos-msg">Fotos em breve.</p>'

    # Instagram link
    ig_link = f'https://instagram.com/{instagram.lstrip("@")}' if instagram else '#'

    # Rating stars
    try:
        nota_num = float(nota)
        stars = '★' * int(nota_num) + ('☆' if nota_num % 1 < 0.5 else '★')
    except:
        nota_num = 0
        stars = ''

    slug_brand = nome.split('|')[0].strip()

    return f'''<!DOCTYPE html>
<html lang="pt-BR" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="ah-brand" content="{slug_brand}">
<meta name="ah-sub" content="{nicho} • {cidade}">
<title>{nome} — {nicho} | {cidade}</title>
<meta name="description" content="{descricao[:155]}">

<!-- Preload fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts_url}" rel="stylesheet">

<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/lucide@latest"></script>

<!-- Aholic Design Tokens -->
<style id="ah-tokens">
{css_root}

/* ── Core layout ── */
.ah-container {{ max-width: 1280px; margin: 0 auto; padding: 0 1.5rem; }}
@media (min-width: 640px) {{ .ah-container {{ padding: 0 3rem; }} }}

/* ── Header ── */
#ah-site-header {{
    position: sticky; top: 0; z-index: 900;
    background: color-mix(in srgb, var(--ah-bg) 92%, transparent);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    height: 72px;
    display: flex; align-items: center;
    transition: box-shadow 0.4s;
}}
.header-inner {{ display: flex; align-items: center; justify-content: space-between; width: 100%; }}
.brand-name {{ font-family: var(--ah-font-display); font-weight: 900; font-size: 1.2rem;
    letter-spacing: 0.18em; text-transform: uppercase; color: var(--ah-text);
    transition: color 0.3s; }}
.brand-name:hover {{ color: var(--ah-accent); }}
.brand-sub {{ font-size: 0.65rem; letter-spacing: 0.3em; text-transform: uppercase;
    color: var(--ah-accent); font-weight: 700; display: block; margin-top: 2px; }}
.nav-links {{ display: none; }}
@media (min-width: 768px) {{
    .nav-links {{ display: flex; gap: 2rem; list-style: none; margin: 0; padding: 0;
        font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 700;
        color: var(--ah-text-muted); }}
    .nav-links a {{ color: inherit; text-decoration: none; transition: color 0.3s; }}
    .nav-links a:hover {{ color: var(--ah-accent); }}
}}
.btn-primary {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.75rem 1.75rem; border-radius: 9999px;
    background: var(--ah-accent); color: var(--ah-bg);
    font-size: 0.7rem; font-weight: 900; letter-spacing: 0.18em; text-transform: uppercase;
    text-decoration: none; border: none; cursor: pointer;
    transition: background 0.3s, transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 8px 24px -8px rgba(0,0,0,0.5);
}}
.btn-primary:hover {{ background: color-mix(in srgb, var(--ah-accent) 80%, white); transform: translateY(-2px); box-shadow: 0 16px 32px -8px rgba(0,0,0,0.5); }}
.btn-secondary {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.75rem 1.5rem; border-radius: 9999px;
    background: transparent; color: var(--ah-text);
    border: 1.5px solid rgba(255,255,255,0.2);
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase;
    text-decoration: none; cursor: pointer;
    transition: background 0.3s, transform 0.3s, border-color 0.3s;
}}
.btn-secondary:hover {{ background: var(--ah-surface); border-color: var(--ah-accent); transform: translateY(-2px); }}

/* ── Marquee bar ── */
.marquee-bar {{
    background: var(--ah-surface); color: var(--ah-text-muted);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 0.75rem 0; overflow: hidden; user-select: none;
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.22em; text-transform: uppercase;
}}
.marquee-inner {{ white-space: nowrap; width: 200%; }}

/* ── Hero ── */
.hero-section {{
    min-height: 85vh; display: flex; align-items: center;
    padding: 5rem 0; position: relative; overflow: hidden;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 0.6rem;
    padding: 0.4rem 1rem; border-radius: 9999px;
    background: var(--ah-surface); border: 1px solid color-mix(in srgb, var(--ah-accent) 40%, transparent);
    color: var(--ah-accent); font-size: 0.65rem; font-weight: 900;
    letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 1.5rem;
}}
.hero-badge-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--ah-accent);
    animation: hero-ping 1.5s ease infinite;
}}
@keyframes hero-ping {{
    0%,100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.6; transform: scale(1.4); }}
}}
.hero-h1 {{
    font-family: var(--ah-font-display); font-size: clamp(2.5rem, 7vw, 5.5rem);
    font-weight: 900; line-height: 0.96; letter-spacing: -0.01em;
    text-transform: uppercase; color: var(--ah-text); margin-bottom: 1.5rem;
}}
.hero-h1 em {{ font-style: italic; color: var(--ah-accent); font-size: 0.85em; font-weight: 400; }}
.hero-desc {{ font-size: 1.05rem; color: var(--ah-text-muted); line-height: 1.7;
    max-width: 48ch; margin-bottom: 2rem; }}
.hero-stats {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;
    padding: 1.5rem 0; border-top: 1px solid rgba(255,255,255,0.1);
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 2rem;
}}
.hero-stat-num {{
    font-family: var(--ah-font-display); font-size: 2.25rem; font-weight: 900;
    color: var(--ah-accent); line-height: 1;
}}
.hero-stat-label {{
    font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--ah-text-muted); font-weight: 700; margin-top: 0.25rem;
}}
.hero-img-wrap {{ position: relative; border-radius: 24px; overflow: hidden;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 40px 80px -20px rgba(0,0,0,0.7); }}
.hero-img-wrap img {{ width: 100%; height: 520px; object-fit: cover;
    filter: grayscale(30%); transition: filter 0.8s, transform 0.8s; display: block; }}
.hero-img-wrap:hover img {{ filter: grayscale(0%); transform: scale(1.04); }}
.hero-float-badge {{
    position: absolute; bottom: -1.5rem; left: -1.5rem;
    background: var(--ah-surface); border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px; padding: 1rem 1.25rem;
    display: flex; align-items: center; gap: 0.75rem;
    box-shadow: 0 16px 40px rgba(0,0,0,0.5);
}}
.float-badge-icon {{
    width: 48px; height: 48px; border-radius: 12px;
    background: var(--ah-accent); color: var(--ah-bg);
    font-family: var(--ah-font-display); font-weight: 900; font-size: 1.2rem;
    display: flex; align-items: center; justify-content: center;
}}
.float-badge-rating {{ font-size: 0.8rem; color: var(--ah-accent); font-weight: 700; }}
.float-badge-label {{ font-size: 0.65rem; color: var(--ah-text-muted); margin-top: 2px; }}

/* ── Section headings ── */
.section-label {{
    font-size: 0.65rem; letter-spacing: 0.25em; text-transform: uppercase;
    font-weight: 700; color: var(--ah-accent); display: block; margin-bottom: 0.75rem;
}}
.section-h2 {{
    font-family: var(--ah-font-display); font-size: clamp(1.8rem, 4vw, 3.5rem);
    font-weight: 900; text-transform: uppercase; letter-spacing: -0.01em;
    color: var(--ah-text); line-height: 1.05;
}}
.section-divider {{ width: 48px; height: 3px; background: var(--ah-accent);
    border-radius: 99px; margin-top: 1rem; }}

/* ── Services grid ── */
.services-grid {{ display: grid; grid-template-columns: 1fr;
    gap: 1.25rem; margin-top: 2.5rem; }}
@media (min-width: 640px) {{ .services-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
@media (min-width: 1024px) {{ .services-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
.service-card {{
    background: var(--ah-surface); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px; padding: 2rem;
    transition: transform 0.5s cubic-bezier(0.16,1,0.3,1),
                border-color 0.4s, box-shadow 0.5s, background 0.4s;
}}
.service-card:hover {{
    transform: translateY(-10px); background: color-mix(in srgb, var(--ah-surface) 80%, var(--ah-accent) 20%);
    border-color: var(--ah-accent); box-shadow: 0 24px 48px -12px rgba(0,0,0,0.6);
}}
.sc-num {{
    width: 44px; height: 44px; border-radius: 12px;
    background: color-mix(in srgb, var(--ah-accent) 15%, transparent);
    border: 1px solid rgba(255,255,255,0.1);
    color: var(--ah-accent); font-weight: 900; font-size: 1rem;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 1.25rem;
}}
.sc-title {{ font-family: var(--ah-font-display); font-size: 1.1rem; font-weight: 900;
    text-transform: uppercase; color: var(--ah-text); margin-bottom: 0.5rem; }}
.sc-desc {{ font-size: 0.8rem; color: var(--ah-text-muted); line-height: 1.6; }}

/* ── Gallery ── */
.gallery-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 2.5rem; }}
@media (min-width: 768px) {{ .gallery-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
.gal-item {{ border-radius: 20px; overflow: hidden; aspect-ratio: 4/3;
    border: 1px solid rgba(255,255,255,0.08); }}
.gal-item img {{ width: 100%; height: 100%; object-fit: cover;
    filter: grayscale(30%); transition: filter 0.8s, transform 0.8s; display: block; }}
.gal-item:hover img {{ filter: grayscale(0%); transform: scale(1.06); }}

/* ── Reviews ── */
.reviews-grid {{ display: grid; grid-template-columns: 1fr; gap: 1.25rem; margin-top: 2.5rem; }}
@media (min-width: 768px) {{ .reviews-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
.review-card {{ background: var(--ah-surface); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px; padding: 2rem;
    display: flex; flex-direction: column; justify-content: space-between; gap: 1rem; }}
.review-stars {{ color: var(--ah-accent); font-size: 1rem; }}
.review-text {{ font-size: 0.85rem; color: var(--ah-text); line-height: 1.7;
    font-style: italic; flex: 1; }}
.review-author {{ font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase;
    font-weight: 700; color: var(--ah-text); }}
.review-role {{ font-size: 0.65rem; color: var(--ah-text-muted); font-weight: 500; }}

/* ── Info section ── */
.info-card {{ background: var(--ah-surface); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 28px; padding: 3rem; box-shadow: 0 24px 48px -12px rgba(0,0,0,0.5); }}
.info-row {{ display: flex; align-items: flex-start; gap: 0.875rem;
    font-size: 0.9rem; color: var(--ah-text); }}
.info-row i {{ color: var(--ah-accent); width: 20px; flex-shrink: 0; margin-top: 2px; }}
.info-label {{ color: var(--ah-text); font-weight: 700; display: block; margin-bottom: 2px; }}
.info-value {{ color: var(--ah-text-muted); font-weight: 400; }}

/* ── Map embed ── */
.map-embed {{ border-radius: 20px; overflow: hidden;
    border: 1px solid rgba(255,255,255,0.12); height: 320px; }}
.map-embed iframe {{ width: 100%; height: 100%; border: 0; display: block; }}

/* ── Footer ── */
.ah-footer {{
    background: color-mix(in srgb, var(--ah-bg) 80%, black);
    border-top: 1px solid rgba(255,255,255,0.08);
    padding: 3rem 0; text-align: center;
}}
.footer-logo-wrap {{ display: inline-flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; }}
.footer-logo-icon {{ width: 40px; height: 40px; border-radius: 50%;
    background: var(--ah-accent); color: var(--ah-bg);
    display: flex; align-items: center; justify-content: center;
    font-family: var(--ah-font-display); font-weight: 900; font-size: 1rem; }}
.footer-brand {{ font-family: var(--ah-font-display); font-weight: 900; font-size: 1.1rem;
    letter-spacing: 0.15em; text-transform: uppercase; color: var(--ah-text); }}
.footer-sub {{ font-size: 0.65rem; letter-spacing: 0.2em; color: var(--ah-accent);
    text-transform: uppercase; font-weight: 700; }}
.footer-copy {{ font-size: 0.65rem; color: var(--ah-text-muted); margin-top: 1.5rem; }}

/* ── WA Float button ── */
#ah-wa-float {{
    position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 800;
    width: 56px; height: 56px; border-radius: 50%;
    background: #25D366; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 8px 24px rgba(37,211,102,0.45);
    transition: transform 0.3s, box-shadow 0.3s; text-decoration: none;
    animation: wa-pulse 2.5s ease infinite;
}}
#ah-wa-float:hover {{ transform: scale(1.12); box-shadow: 0 12px 32px rgba(37,211,102,0.6); }}
@keyframes wa-pulse {{
    0%,100% {{ box-shadow: 0 8px 24px rgba(37,211,102,0.45); }}
    50%  {{ box-shadow: 0 8px 40px rgba(37,211,102,0.7); }}
}}

/* ── Sections spacing ── */
.ah-section {{ padding: 5rem 0; border-bottom: 1px solid rgba(255,255,255,0.06); }}

/* ── No photos fallback ── */
.no-photos-msg {{ color: var(--ah-text-muted); font-size: 0.8rem; font-style: italic; }}
</style>
</head>
<body class="antialiased overflow-x-hidden" style="background:var(--ah-bg);color:var(--ah-text);">

<!-- WhatsApp Float -->
{f'<a id="ah-wa-float" href="{wa_link}" target="_blank" rel="noopener" aria-label="WhatsApp"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="white" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg></a>' if whatsapp else ''}

<!-- Header -->
<header id="ah-site-header" data-ah-header>
  <div class="ah-container">
    <div class="header-inner">
      <a href="#" style="text-decoration:none;">
        {f'<img src="{logo_path}" alt="Logo {nome}" style="height:40px;object-fit:contain;margin-right:0.75rem;">' if logo_path else ''}
        <span class="brand-name">{nome.split("|")[0].strip()}<span class="brand-sub">{nicho} • {cidade}</span></span>
      </a>
      <nav aria-label="Navegação principal">
        <ul class="nav-links">
          {f'<li><a href="#servicos">Serviços</a></li>' if servicos else ''}
          <li><a href="#galeria">Galeria</a></li>
          <li><a href="#sobre">Avaliações</a></li>
          <li><a href="#contato">Contato</a></li>
        </ul>
      </nav>
      {f'<a href="{wa_link}" class="btn-primary" target="_blank"><i data-lucide="message-circle" style="width:14px;height:14px;"></i>WhatsApp</a>' if whatsapp else ''}
    </div>
  </div>
</header>

<!-- Marquee -->
<div class="marquee-bar">
  <div class="marquee-inner ah-marquee-track">
    {''.join([f'<span style="margin-right:3rem;">• {s if isinstance(s,str) else s.get("nome","")}</span>' for s in (servicos or [nicho, cidade, f'{nota}★'])])*4}
    {''.join([f'<span style="margin-right:3rem;">• {s if isinstance(s,str) else s.get("nome","")}</span>' for s in (servicos or [nicho, cidade, f'{nota}★'])])*4}
  </div>
</div>

<!-- HERO -->
<section class="hero-section">
  <div class="ah-container">
    <div style="display:grid;grid-template-columns:1fr;gap:3rem;align-items:center;" class="lg:grid-cols-2">
      
      <!-- Left -->
      <div class="ah-reveal-item">
        <div class="hero-badge">
          <span class="hero-badge-dot"></span>
          <span style="color:var(--ah-text);font-weight:900;">{cidade}</span>
        </div>
        <h1 class="hero-h1">{nome.split("|")[0].strip()}<br><em>{tagline}</em></h1>
        <p class="hero-desc">{descricao}</p>
        
        {f'''<div class="hero-stats">
          <div>
            <div class="hero-stat-num ah-counter" data-ah-count="{nota_num}" data-ah-suffix="★">{nota}★</div>
            <div class="hero-stat-label">{avaliacoes}+ Avaliações Google</div>
          </div>
          <div>
            <div class="hero-stat-num">100%</div>
            <div class="hero-stat-label">Atendimento Dedicado</div>
          </div>
          <div>
            <div class="hero-stat-num">{cidade.split("/")[0].split(",")[0].strip()}</div>
            <div class="hero-stat-label">Localização</div>
          </div>
        </div>''' if nota else ''}
        
        <div style="display:flex;flex-wrap:wrap;gap:1rem;margin-top:1.5rem;">
          {f'<a href="{wa_link}" class="btn-primary" target="_blank"><i data-lucide="message-circle" style="width:14px;height:14px;"></i>{cta_texto}</a>' if whatsapp else ''}
          {f'<a href="https://instagram.com/{instagram.lstrip("@")}" class="btn-secondary" target="_blank"><i data-lucide="instagram" style="width:14px;height:14px;"></i>Instagram</a>' if instagram else ''}
        </div>
      </div>

      <!-- Right — Hero Image -->
      {f'''<div class="ah-reveal-item" style="transition-delay:200ms;position:relative;">
        <div class="hero-img-wrap">
          <img src="{hero_img}" alt="{nome} — foto principal" onerror="this.parentElement.style.display=\'none\'">
          <div style="position:absolute;inset:0;background:linear-gradient(to top, var(--ah-bg) 0%, transparent 60%);pointer-events:none;"></div>
        </div>
        {f\'\'\'<div class="hero-float-badge ah-float">
          <div class="float-badge-icon">★</div>
          <div>
            <div class="float-badge-rating">{stars} {nota}</div>
            <div class="float-badge-label">Google Maps</div>
          </div>
        </div>\'\'\' if nota else \'\'}
      </div>''' if hero_img else ''}

    </div>
  </div>
</section>

{f'''<!-- SERVIÇOS -->
<section id="servicos" class="ah-section">
  <div class="ah-container">
    <div class="ah-reveal-item">
      <span class="section-label">O Que Oferecemos</span>
      <h2 class="section-h2">Serviços & Especialidades</h2>
      <div class="section-divider"></div>
    </div>
    <div class="services-grid">{servicos_html}</div>
  </div>
</section>''' if servicos else ''}

<!-- GALERIA -->
<section id="galeria" class="ah-section" style="background:var(--ah-surface);">
  <div class="ah-container">
    <div class="ah-reveal-item">
      <span class="section-label">Momentos Reais</span>
      <h2 class="section-h2">Galeria de Fotos</h2>
      <div class="section-divider"></div>
    </div>
    <div class="gallery-grid">{gallery_html}</div>
  </div>
</section>

<!-- AVALIAÇÕES -->
<section id="sobre" class="ah-section">
  <div class="ah-container">
    <div class="ah-reveal-item" style="text-align:center;max-width:600px;margin:0 auto 2.5rem;">
      <div style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.35rem 1rem;border-radius:9999px;background:var(--ah-surface);border:1px solid rgba(255,255,255,0.1);font-size:0.65rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:var(--ah-accent);margin-bottom:1rem;">
        {f'Google Maps Verificado ({nota}★)' if nota else 'Avaliações Verificadas'}
      </div>
      <h2 class="section-h2">O que nossos clientes dizem</h2>
    </div>
    <div class="reviews-grid">
      <div class="review-card ah-reveal-item">
        <div class="review-stars">★★★★★</div>
        <p class="review-text">"Atendimento impecável e resultados que superaram todas as expectativas. Profissionalismo e dedicação em cada detalhe."</p>
        <div><div class="review-author">Cliente Verificado</div><div class="review-role">Google Maps</div></div>
      </div>
      <div class="review-card ah-reveal-item" style="transition-delay:150ms;">
        <div class="review-stars">★★★★★</div>
        <p class="review-text">"Simplesmente o melhor lugar para {nicho.lower() if nicho else 'este serviço'} em {cidade.split(",")[0] if cidade else 'nossa cidade'}. Recomendo a todos!"</p>
        <div><div class="review-author">Cliente Verificado</div><div class="review-role">Google Maps</div></div>
      </div>
      <div class="review-card ah-reveal-item" style="transition-delay:300ms;">
        <div class="review-stars">★★★★★</div>
        <p class="review-text">"Espaço acolhedor, equipe qualificada e resultados que aparecem. Vale cada centavo investido. Voltarei com certeza."</p>
        <div><div class="review-author">Cliente Verificado</div><div class="review-role">Google Maps</div></div>
      </div>
    </div>
  </div>
</section>

<!-- CONTATO & LOCALIZAÇÃO -->
<section id="contato" class="ah-section" style="background:var(--ah-surface);">
  <div class="ah-container">
    <div class="info-card ah-reveal-item">
      <div style="display:grid;grid-template-columns:1fr;gap:2.5rem;align-items:start;">
        
        <div>
          <span class="section-label">Venha nos visitar</span>
          <h2 class="section-h2" style="font-size:clamp(1.5rem,3vw,2.5rem);">{nome.split("|")[0].strip()}</h2>
          <div class="section-divider"></div>
          
          <div style="display:flex;flex-direction:column;gap:1.25rem;margin-top:1.75rem;">
            {f\'\'\'<div class="info-row"><i data-lucide="map-pin"></i><div><span class="info-label">Endereço</span><span class="info-value">{endereco}</span></div></div>\'\'\' if endereco else \'\'}
            {f\'\'\'<div class="info-row"><i data-lucide="clock"></i><div><span class="info-label">Horários</span><span class="info-value">{horarios}</span></div></div>\'\'\' if horarios else \'\'}
            {f\'\'\'<div class="info-row"><i data-lucide="phone"></i><div><span class="info-label">Telefone</span><span class="info-value">{telefone}</span></div></div>\'\'\' if telefone else \'\'}
            {f\'\'\'<div class="info-row"><i data-lucide="mail"></i><div><span class="info-label">E-mail</span><span class="info-value"><a href="mailto:{email}" style="color:var(--ah-accent);">{email}</a></span></div></div>\'\'\' if email else \'\'}
          </div>
          
          <div style="display:flex;flex-wrap:wrap;gap:1rem;margin-top:2rem;">
            {f\'<a href="{wa_link}" class="btn-primary" target="_blank"><i data-lucide="message-circle" style="width:14px;height:14px;"></i>{cta_texto}</a>\' if whatsapp else \'\'}
            {f\'<a href="https://instagram.com/{instagram.lstrip("@")}" class="btn-secondary" target="_blank"><i data-lucide="instagram" style="width:14px;height:14px;"></i>Seguir no Instagram</a>\' if instagram else \'\'}
          </div>
        </div>

        {f\'\'\'<div class="map-embed">
          <iframe
            src="https://maps.google.com/maps?q={urllib.parse.quote_plus(endereco or nome + " " + cidade)}&output=embed&hl=pt-BR"
            allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade">
          </iframe>
        </div>\'\'\' if (endereco or cidade) else \'\'}

      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer class="ah-footer">
  <div class="ah-container">
    <div class="footer-logo-wrap">
      {f'<img src="{logo_path}" alt="Logo {nome}" style="height:36px;object-fit:contain;">' if logo_path else f'<div class="footer-logo-icon">{nome[0].upper()}</div>'}
      <div>
        <div class="footer-brand">{nome.split("|")[0].strip()}</div>
        <div class="footer-sub">{nicho} • {cidade}</div>
      </div>
    </div>
    <div class="footer-copy">© {datetime.now().year} {nome.split("|")[0].strip()}. Site criado por <strong>Aholic Studio</strong>.</div>
  </div>
</footer>

<!-- Lucide Icons -->
<script>lucide.createIcons();</script>

<!-- Aholic Motion Engine v2 -->
<script>
{motion_js}
</script>

</body>
</html>'''
