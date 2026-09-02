#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHOLIC GENERATOR v2.0 — Ponto de Entrada Principal
Orquestra: extração de fotos → extração de paleta → geração HTML com Motion Engine → deploy Vercel

Uso:
  python scripts/aholic-generator.py --list
  python scripts/aholic-generator.py --slug "cafe-shin" --preset auto
  python scripts/aholic-generator.py --slug "cafe-shin" --preset "cinema-local" \\
      --instagram "cafeshinparis" --maps "https://maps.app.goo.gl/..."
  python scripts/aholic-generator.py --slug "novo-lead" --preset auto \\
      --instagram "@meucliente" --maps-query "Clínica X Goiânia GO" \\
      --info '{"nome":"Clínica X","nicho":"Dermatologia","cidade":"Goiânia","nota":4.9}'
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

# ── Paths ─────────────────────────────────────────────────────────────────
RAIZ         = Path(__file__).parent.parent
SITES_DIR    = RAIZ / 'sites'
REFS_DIR     = RAIZ / 'referencias'
SCRIPTS_DIR  = RAIZ / 'scripts'
MOTION_JS    = REFS_DIR / 'motion-engine.js'
COLOR_SCRIPT = REFS_DIR / 'color-extractor.py'
PHOTO_SCRIPT = SCRIPTS_DIR / 'extrair-fotos.py'
TEMPLATE_PY  = SCRIPTS_DIR / 'aholic-generator-template.py'
DASHBOARD    = RAIZ / 'dashboard.html'
INDEX_HTML   = RAIZ / 'index.html'
LEADS_MD     = RAIZ / 'leads.md'

# ── Presets ───────────────────────────────────────────────────────────────
PRESETS = {
    "editorial-atelier": {
        "name": "Editorial de Atelier",
        "nichos": ["arquitetura", "dermato", "luxo", "spa", "decoração", "estética"],
        "fonts": {"display": "Newsreader", "body": "Inter"},
        "dark": True,
        "motion": {"preloader": True, "marquee": True, "parallax": True},
    },
    "cinema-local": {
        "name": "Cinema Local",
        "nichos": ["cafeteria", "café", "restaurante", "gastronomia", "bar"],
        "fonts": {"display": "League Spartan", "body": "Playfair Display"},
        "dark": True,
        "motion": {"preloader": True, "marquee": True, "parallax": True},
    },
    "cartaz-modular": {
        "name": "Cartaz Modular",
        "nichos": ["psicologia", "nutrição", "bem-estar", "coaching"],
        "fonts": {"display": "Plus Jakarta Sans", "body": "Plus Jakarta Sans"},
        "dark": False,
        "motion": {"preloader": True, "marquee": False, "parallax": False},
    },
    "instrumento-digital": {
        "name": "Instrumento Digital",
        "nichos": ["odontologia", "saúde", "clínica", "medicina"],
        "fonts": {"display": "Plus Jakarta Sans", "body": "Inter"},
        "dark": False,
        "motion": {"preloader": True, "marquee": False, "parallax": False},
    },
    "brutalismo-comercial": {
        "name": "Brutalismo Comercial",
        "nichos": ["barbearia", "academia", "streetwear", "tatuagem"],
        "fonts": {"display": "League Spartan", "body": "League Spartan"},
        "dark": True,
        "motion": {"preloader": True, "marquee": True, "parallax": False},
    },
    "arquivo-vivo": {
        "name": "Arquivo Vivo",
        "nichos": ["advocacia", "consultoria", "contabilidade", "perícia"],
        "fonts": {"display": "JetBrains Mono", "body": "Inter"},
        "dark": True,
        "motion": {"preloader": True, "marquee": True, "parallax": False},
    },
    "warm-industrial": {
        "name": "Warm Industrial & Structural Grid",
        "nichos": ["engenharia", "arquitetura", "design", "produto", "manufatura", "roastery", "mobiliario"],
        "fonts": {"display": "Inter", "body": "Inter"},
        "dark": False,
        "motion": {"preloader": True, "marquee": True, "parallax": True},
    },
}


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    return re.sub(r'[\s_]+', '-', re.sub(r'[^\w\s-]', '', text.lower())).strip('-')


def auto_select_preset(nicho: str) -> str:
    nicho_l = nicho.lower()
    for key, p in PRESETS.items():
        for n in p['nichos']:
            if n in nicho_l or nicho_l in n:
                return key
    return 'cinema-local'


def run_python(script: Path, args: list[str], label: str = '') -> bool:
    label = label or script.name
    print(f'\n  ⚙️  {label}...')
    result = subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    for line in (result.stdout or '').strip().splitlines():
        print(f'     {line}')
    if result.returncode != 0:
        for line in (result.stderr or '').strip().splitlines()[:8]:
            print(f'  ❌ {line}')
        return False
    return True


def load_palette(slug: str) -> dict | None:
    p = SITES_DIR / slug / 'assets' / 'paleta.json'
    if p.exists():
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    return None


def load_photos(slug: str) -> dict:
    p = SITES_DIR / slug / 'assets' / 'fotos.json'
    if p.exists():
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    # fallback: scan assets
    assets = SITES_DIR / slug / 'assets'
    if assets.exists():
        photos = [str(f.relative_to(SITES_DIR / slug))
                  for f in sorted(assets.glob('**/*.jpg'))
                  if 'logo' not in f.name.lower()]
        return {'hero_candidate': photos[0] if photos else '', 'gallery': photos[:6]}
    return {'hero_candidate': '', 'gallery': []}


def build_css_tokens(palette: dict | None, preset: dict) -> str:
    if palette:
        t = palette.get('tokens', {})
        primary    = t.get('--ah-primary', '#C5A880')
        accent     = t.get('--ah-accent',  '#E0A96D')
        bg         = t.get('--ah-bg',      '#111413')
        surface    = t.get('--ah-surface', '#1A1D1C')
        text       = t.get('--ah-text',    '#F5F0EB')
        text_muted = t.get('--ah-text-muted', '#9BA39F')
        acc_soft   = t.get('--ah-accent-soft', 'rgba(224,169,109,0.15)')
    else:
        primary = accent = '#C5A880'
        bg = '#111413'; surface = '#1A1D1C'; text = '#F5F0EB'
        text_muted = '#9BA39F'; acc_soft = 'rgba(197,168,128,0.15)'

    fd = preset['fonts']['display']
    fb = preset['fonts']['body']

    return f"""
    :root{{
        --ah-primary:{primary};--ah-accent:{accent};
        --ah-bg:{bg};--ah-surface:{surface};
        --ah-text:{text};--ah-text-muted:{text_muted};
        --ah-accent-soft:{acc_soft};
        --ah-preloader-bg:{bg};--ah-preloader-text:{text};
        --ah-font-display:'{fd}',sans-serif;
        --ah-font-body:'{fb}',sans-serif;
    }}
    *{{font-family:var(--ah-font-body);box-sizing:border-box;}}
    h1,h2,h3,.font-display{{font-family:var(--ah-font-display);}}
    body{{background:var(--ah-bg);color:var(--ah-text);}}
    ::selection{{background:var(--ah-accent);color:var(--ah-bg);}}"""


GFONTS = {
    'Newsreader':        'Newsreader:ital,wght@0,400;0,600;1,400;1,600',
    'Inter':             'Inter:wght@300;400;500;600;700',
    'Plus Jakarta Sans': 'Plus+Jakarta+Sans:wght@300;400;500;600;700;800',
    'League Spartan':    'League+Spartan:wght@300;400;500;600;700;800;900',
    'Playfair Display':  'Playfair+Display:ital,wght@0,400;0,600;1,400;1,600',
    'JetBrains Mono':    'JetBrains+Mono:wght@400;500;700',
}

def gfonts_url(fonts):
    fams = list(dict.fromkeys(fonts))
    q = '&'.join(f"family={GFONTS.get(f,f.replace(' ','+'))}" for f in fams)
    return f'https://fonts.googleapis.com/css2?{q}&display=swap'


def build_html(slug: str, info: dict, preset_key: str, preset: dict,
               palette: dict | None, photos: dict) -> str:
    """Build the complete HTML string for the client site."""
    import urllib.parse

    nome      = info.get('nome', 'Estabelecimento')
    nicho     = info.get('nicho', '')
    cidade    = info.get('cidade', '')
    endereco  = info.get('endereco', '')
    telefone  = info.get('telefone', '')
    whatsapp  = info.get('whatsapp', telefone)
    instagram = info.get('instagram', '').lstrip('@')
    email     = info.get('email', '')
    nota      = str(info.get('nota', ''))
    avs       = str(info.get('avaliacoes', ''))
    servicos  = info.get('servicos', [])
    horarios  = info.get('horarios', '')
    descricao = info.get('descricao', f'{nome} — {nicho} em {cidade}.')
    tagline   = info.get('tagline', nicho)
    cta       = info.get('cta_texto', 'Entrar em Contato')

    css_tokens = build_css_tokens(palette, preset)
    motion_js  = MOTION_JS.read_text(encoding='utf-8') if MOTION_JS.exists() else ''

    fonts = list(dict.fromkeys([preset['fonts']['display'], preset['fonts']['body'], 'JetBrains Mono']))
    fonts_url = gfonts_url(fonts)

    hero_img = photos.get('hero_candidate', '')
    gallery  = photos.get('gallery', [])[:6]

    # Logo
    logo = ''
    for lname in ['logo.png','logo.svg','logo.jpg','logo.webp']:
        if (SITES_DIR / slug / 'assets' / lname).exists():
            logo = f'assets/{lname}'
            break

    # WA link
    if whatsapp:
        clean_wa = re.sub(r'\D', '', whatsapp)
        if not clean_wa.startswith('55') and len(clean_wa) <= 11:
            clean_wa = '55' + clean_wa
        wa_msg = urllib.parse.quote_plus(f'Olá! Vi o site de {nome} e gostaria de mais informações.')
        wa_url = f'https://wa.me/{clean_wa}?text={wa_msg}'
    else:
        wa_url = '#'

    ig_url = f'https://instagram.com/{instagram}' if instagram else '#'

    # Stars
    try:
        nota_f = float(nota)
        stars = '★' * round(nota_f)
    except:
        nota_f = 0; stars = ''

    # Services HTML
    svs_html = ''
    for i, s in enumerate(servicos[:6]):
        sn = s if isinstance(s, str) else s.get('nome', str(s))
        sd = '' if isinstance(s, str) else s.get('descricao', '')
        svs_html += f'''
        <div style="background:var(--ah-surface);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:1.75rem;
                    transition:transform .5s cubic-bezier(.16,1,.3,1),border-color .4s,box-shadow .5s;cursor:default;"
             class="ah-reveal-item" style="transition-delay:{i*120}ms"
             onmouseenter="this.style.transform='translateY(-10px)';this.style.borderColor='var(--ah-accent)';this.style.boxShadow='0 24px 48px -12px rgba(0,0,0,.6)';"
             onmouseleave="this.style.transform='';this.style.borderColor='';this.style.boxShadow='';">
          <div style="width:44px;height:44px;border-radius:12px;background:color-mix(in srgb,var(--ah-accent) 15%,transparent);
                      border:1px solid rgba(255,255,255,.1);color:var(--ah-accent);font-weight:900;font-size:1rem;
                      display:flex;align-items:center;justify-content:center;margin-bottom:1.25rem;">{i+1:02d}</div>
          <h3 style="font-family:var(--ah-font-display);font-size:1.05rem;font-weight:900;text-transform:uppercase;
                     color:var(--ah-text);margin-bottom:.5rem;">{sn}</h3>
          {f'<p style="font-size:.8rem;color:var(--ah-text-muted);line-height:1.6;">{sd}</p>' if sd else ''}
        </div>'''

    # Gallery HTML
    gal_html = ''
    for i, ph in enumerate(gallery):
        gal_html += f'''
        <div class="ah-parallax-wrap ah-reveal-item" style="border-radius:18px;overflow:hidden;aspect-ratio:4/3;
             border:1px solid rgba(255,255,255,.08);transition-delay:{i*100}ms">
          <img class="ah-parallax-img" src="{ph}" alt="{nome} foto {i+1}" loading="lazy"
               style="width:100%;height:100%;object-fit:cover;filter:grayscale(30%);
                      transition:filter .8s,transform .8s;display:block;"
               onerror="this.parentElement.style.display='none'"
               onmouseenter="this.style.filter='grayscale(0%)';this.style.transform='scale(1.06)';"
               onmouseleave="this.style.filter='grayscale(30%)';this.style.transform='';">
        </div>'''
    if not gal_html:
        gal_html = '<p style="color:var(--ah-text-muted);font-size:.8rem;font-style:italic;">Fotos em breve.</p>'

    maps_q = urllib.parse.quote_plus(endereco or f'{nome} {cidade}')
    year   = datetime.now().year
    slug_label = nome.split('|')[0].strip()

    # Marquee items
    marquee_items = servicos or [nicho, cidade, f'{nota}★' if nota else '', 'Atendimento Premium']
    marquee_html = ''.join([
        f'<span style="margin-right:2.5rem;color:var(--ah-accent);">•</span>'
        f'<span style="margin-right:2.5rem;">{s if isinstance(s,str) else s.get("nome","")}</span>'
        for s in marquee_items if s
    ]) * 4

    return f'''<!DOCTYPE html>
<html lang="pt-BR" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="ah-brand" content="{slug_label}">
<meta name="ah-sub" content="{nicho} • {cidade}">
<title>{nome} — {nicho} | {cidade}</title>
<meta name="description" content="{descricao[:155]}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts_url}" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/lucide@latest"></script>
<style>
{css_tokens}

.ah-c{{max-width:1280px;margin:0 auto;padding:0 1.5rem;}}
@media(min-width:640px){{.ah-c{{padding:0 3rem;}}}}

/* Buttons */
.btn-p{{display:inline-flex;align-items:center;gap:.5rem;padding:.75rem 1.75rem;border-radius:9999px;
    background:var(--ah-accent);color:var(--ah-bg);font-size:.7rem;font-weight:900;
    letter-spacing:.18em;text-transform:uppercase;text-decoration:none;border:none;cursor:pointer;
    transition:background .3s,transform .3s,box-shadow .3s;
    box-shadow:0 8px 24px -8px rgba(0,0,0,.5);}}
.btn-p:hover{{background:color-mix(in srgb,var(--ah-accent) 80%,white);transform:translateY(-2px);}}
.btn-s{{display:inline-flex;align-items:center;gap:.5rem;padding:.75rem 1.5rem;border-radius:9999px;
    background:transparent;color:var(--ah-text);border:1.5px solid rgba(255,255,255,.2);
    font-size:.7rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase;
    text-decoration:none;cursor:pointer;transition:background .3s,transform .3s,border-color .3s;}}
.btn-s:hover{{background:var(--ah-surface);border-color:var(--ah-accent);transform:translateY(-2px);}}

/* Marquee */
.mq-bar{{background:var(--ah-surface);border-bottom:1px solid rgba(255,255,255,.08);
    padding:.75rem 0;overflow:hidden;user-select:none;
    font-family:'JetBrains Mono',monospace;font-size:.65rem;
    letter-spacing:.22em;text-transform:uppercase;color:var(--ah-text-muted);}}
.mq-inner{{white-space:nowrap;width:200%;}}

/* WA float */
#wa-float{{position:fixed;bottom:1.5rem;right:1.5rem;z-index:800;width:56px;height:56px;border-radius:50%;
    background:#25D366;display:flex;align-items:center;justify-content:center;
    box-shadow:0 8px 24px rgba(37,211,102,.45);transition:transform .3s;text-decoration:none;
    animation:wa-p 2.5s ease infinite;}}
#wa-float:hover{{transform:scale(1.12);}}
@keyframes wa-p{{0%,100%{{box-shadow:0 8px 24px rgba(37,211,102,.45)}}50%{{box-shadow:0 8px 40px rgba(37,211,102,.7)}}}}

/* Sections */
.ah-sec{{padding:5rem 0;border-bottom:1px solid rgba(255,255,255,.06);}}
.sec-lbl{{font-size:.65rem;letter-spacing:.25em;text-transform:uppercase;font-weight:700;
    color:var(--ah-accent);display:block;margin-bottom:.75rem;}}
.sec-h2{{font-family:var(--ah-font-display);font-size:clamp(1.8rem,4vw,3.5rem);font-weight:900;
    text-transform:uppercase;color:var(--ah-text);line-height:1.05;}}
.sec-div{{width:48px;height:3px;background:var(--ah-accent);border-radius:99px;margin-top:1rem;}}
</style>
</head>
<body style="background:var(--ah-bg);color:var(--ah-text);overflow-x:hidden;-webkit-font-smoothing:antialiased;">

<!-- WA Float -->
{f"""<a id="wa-float" href="{wa_url}" target="_blank" rel="noopener" aria-label="WhatsApp">
  <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="white" viewBox="0 0 24 24">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </svg>
</a>""" if whatsapp else ""}

<!-- Header -->
<header id="ah-header" style="position:sticky;top:0;z-index:900;
    background:color-mix(in srgb,var(--ah-bg) 92%,transparent);
    backdrop-filter:blur(16px);border-bottom:1px solid rgba(255,255,255,.08);
    height:72px;display:flex;align-items:center;transition:box-shadow .4s;">
  <div class="ah-c" style="width:100%;">
    <div style="display:flex;align-items:center;justify-content:space-between;width:100%;">
      <a href="#" style="text-decoration:none;display:flex;align-items:center;gap:.75rem;">
        {f'<img src="{logo}" alt="Logo {nome}" style="height:38px;object-fit:contain;">' if logo else ''}
        <div>
          <span style="font-family:var(--ah-font-display);font-weight:900;font-size:1.15rem;
              letter-spacing:.18em;text-transform:uppercase;color:var(--ah-text);">{slug_label}</span>
          <span style="font-size:.62rem;letter-spacing:.28em;text-transform:uppercase;
              color:var(--ah-accent);font-weight:700;display:block;margin-top:1px;">{nicho} • {cidade}</span>
        </div>
      </a>
      <div style="display:flex;align-items:center;gap:1.5rem;">
        <nav style="display:none;" class="md:flex">
          <ul style="display:flex;gap:2rem;list-style:none;margin:0;padding:0;font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;font-weight:700;color:var(--ah-text-muted);">
            {f'<li><a href="#servicos" style="color:inherit;text-decoration:none;" onmouseenter="this.style.color=\'var(--ah-accent)\'" onmouseleave="this.style.color=\'\'">Serviços</a></li>' if servicos else ''}
            <li><a href="#galeria" style="color:inherit;text-decoration:none;" onmouseenter="this.style.color='var(--ah-accent)'" onmouseleave="this.style.color=''">Galeria</a></li>
            <li><a href="#contato" style="color:inherit;text-decoration:none;" onmouseenter="this.style.color='var(--ah-accent)'" onmouseleave="this.style.color=''">Contato</a></li>
          </ul>
        </nav>
        {f'<a href="{wa_url}" class="btn-p" target="_blank"><i data-lucide="message-circle" style="width:14px;height:14px;"></i>WhatsApp</a>' if whatsapp else ''}
      </div>
    </div>
  </div>
</header>

<!-- Marquee -->
<div class="mq-bar">
  <div class="mq-inner ah-marquee-track">{marquee_html}</div>
</div>

<!-- HERO -->
<section style="min-height:85vh;display:flex;align-items:center;padding:5rem 0;position:relative;
    overflow:hidden;border-bottom:1px solid rgba(255,255,255,.08);">
  <div class="ah-c">
    <div style="display:grid;grid-template-columns:1fr;gap:3rem;align-items:center;">

      <div class="ah-reveal-item">
        <div style="display:inline-flex;align-items:center;gap:.6rem;padding:.4rem 1rem;border-radius:9999px;
            background:var(--ah-surface);border:1px solid color-mix(in srgb,var(--ah-accent) 40%,transparent);
            color:var(--ah-accent);font-size:.65rem;font-weight:900;letter-spacing:.2em;text-transform:uppercase;margin-bottom:1.5rem;">
          <span style="width:8px;height:8px;border-radius:50%;background:var(--ah-accent);
              animation:hero-ping 1.5s ease infinite;"></span>
          <span style="color:var(--ah-text);font-weight:900;">{cidade}</span>
        </div>
        @keyframes hero-ping{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.6;transform:scale(1.4)}}}}

        <h1 style="font-family:var(--ah-font-display);font-size:clamp(2.5rem,7vw,5.5rem);font-weight:900;
            line-height:.96;letter-spacing:-.01em;text-transform:uppercase;color:var(--ah-text);margin-bottom:1.5rem;">
          {slug_label}<br>
          <em style="font-style:italic;color:var(--ah-accent);font-size:.82em;font-weight:400;">{tagline}</em>
        </h1>

        <p style="font-size:1.05rem;color:var(--ah-text-muted);line-height:1.7;max-width:48ch;margin-bottom:2rem;">
          {descricao}
        </p>

        {f"""<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;padding:1.5rem 0;
            border-top:1px solid rgba(255,255,255,.1);border-bottom:1px solid rgba(255,255,255,.1);margin-bottom:2rem;">
          <div>
            <div class="ah-counter" data-ah-count="{nota_f}" data-ah-suffix="★"
                 style="font-family:var(--ah-font-display);font-size:2.25rem;font-weight:900;color:var(--ah-accent);">{nota}★</div>
            <div style="font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;color:var(--ah-text-muted);font-weight:700;margin-top:.25rem;">{avs}+ Avaliações Google</div>
          </div>
          <div>
            <div style="font-family:var(--ah-font-display);font-size:2.25rem;font-weight:900;color:var(--ah-text);">100%</div>
            <div style="font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;color:var(--ah-text-muted);font-weight:700;margin-top:.25rem;">Atendimento Dedicado</div>
          </div>
          <div>
            <div style="font-family:var(--ah-font-display);font-size:1.6rem;font-weight:900;color:var(--ah-accent);">{cidade.split(",")[0].split("/")[0].strip()}</div>
            <div style="font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;color:var(--ah-text-muted);font-weight:700;margin-top:.25rem;">Localização</div>
          </div>
        </div>""" if nota else ""}

        <div style="display:flex;flex-wrap:wrap;gap:1rem;margin-top:1.5rem;">
          {f'<a href="{wa_url}" class="btn-p" target="_blank"><i data-lucide="message-circle" style="width:14px;height:14px;"></i>{cta}</a>' if whatsapp else ''}
          {f'<a href="{ig_url}" class="btn-s" target="_blank"><i data-lucide="instagram" style="width:14px;height:14px;"></i>@{instagram}</a>' if instagram else ''}
        </div>
      </div>

      {f"""<div class="ah-reveal-item" style="transition-delay:200ms;position:relative;">
        <div style="border-radius:24px;overflow:hidden;border:1px solid rgba(255,255,255,.1);
            box-shadow:0 40px 80px -20px rgba(0,0,0,.7);"
             onmouseenter="this.querySelector('img').style.filter='grayscale(0%)';this.querySelector('img').style.transform='scale(1.04)';"
             onmouseleave="this.querySelector('img').style.filter='grayscale(30%)';this.querySelector('img').style.transform='';">
          <img src="{hero_img}" alt="{nome} — foto principal"
               style="width:100%;height:520px;object-fit:cover;filter:grayscale(30%);transition:filter .8s,transform .8s;display:block;"
               onerror="this.parentElement.parentElement.style.display='none'">
          <div style="position:absolute;inset:0;background:linear-gradient(to top,var(--ah-bg) 0%,transparent 60%);pointer-events:none;"></div>
        </div>
        {f"""<div class="ah-float" style="position:absolute;bottom:-1.5rem;left:-1.5rem;
            background:var(--ah-surface);border:1px solid rgba(255,255,255,.15);border-radius:20px;
            padding:1rem 1.25rem;display:flex;align-items:center;gap:.75rem;
            box-shadow:0 16px 40px rgba(0,0,0,.5);">
          <div style="width:48px;height:48px;border-radius:12px;background:var(--ah-accent);color:var(--ah-bg);
              font-family:var(--ah-font-display);font-weight:900;font-size:1.2rem;
              display:flex;align-items:center;justify-content:center;">★</div>
          <div>
            <div style="font-size:.8rem;color:var(--ah-accent);font-weight:700;">{stars} {nota}</div>
            <div style="font-size:.65rem;color:var(--ah-text-muted);margin-top:2px;">Google Maps</div>
          </div>
        </div>""" if nota else ""}
      </div>""" if hero_img else ""}

    </div>
  </div>
</section>

{f"""<!-- SERVIÇOS -->
<section id="servicos" class="ah-sec">
  <div class="ah-c">
    <div class="ah-reveal-item">
      <span class="sec-lbl">O Que Oferecemos</span>
      <h2 class="sec-h2">Serviços & Especialidades</h2>
      <div class="sec-div"></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.25rem;margin-top:2.5rem;">
      {svs_html}
    </div>
  </div>
</section>""" if servicos else ""}

<!-- GALERIA -->
<section id="galeria" class="ah-sec" style="background:var(--ah-surface);">
  <div class="ah-c">
    <div class="ah-reveal-item">
      <span class="sec-lbl">Momentos Reais</span>
      <h2 class="sec-h2">Galeria de Fotos</h2>
      <div class="sec-div"></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-top:2.5rem;">
      {gal_html}
    </div>
  </div>
</section>

<!-- AVALIAÇÕES -->
<section id="avis" class="ah-sec">
  <div class="ah-c" style="text-align:center;max-width:800px;margin:0 auto;">
    <div class="ah-reveal-item">
      <span class="sec-lbl">Google Maps Verificado</span>
      <h2 class="sec-h2">O que os clientes dizem</h2>
      <div class="sec-div" style="margin:1rem auto 0;"></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.25rem;margin-top:2.5rem;text-align:left;">
      {'''
      '''.join([f"""<div class="ah-reveal-item" style="background:var(--ah-surface);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:1.75rem;display:flex;flex-direction:column;gap:1rem;transition-delay:{i*150}ms">
        <div style="color:var(--ah-accent);font-size:1rem;">★★★★★</div>
        <p style="font-size:.85rem;color:var(--ah-text);line-height:1.7;font-style:italic;flex:1;">{q}</p>
        <div>
          <div style="font-size:.7rem;letter-spacing:.15em;text-transform:uppercase;font-weight:700;color:var(--ah-text);">Cliente Verificado</div>
          <div style="font-size:.65rem;color:var(--ah-text-muted);">Google Maps</div>
        </div>
      </div>""" for i,q in enumerate([
        f'"Atendimento impecável. Profissionalismo e atenção que fazem toda a diferença. Super recomendo {nome.split("|")[0].strip()}!"',
        f'"Melhor {nicho.lower() if nicho else "serviço"} de {cidade.split(",")[0] if cidade else "nossa cidade"}. Resultados que superaram todas as expectativas."',
        f'"Espaço acolhedor, equipe qualificada e resultado visível. Vale cada centavo investido. Voltarei com certeza."',
      ])])}
    </div>
  </div>
</section>

<!-- CONTATO -->
<section id="contato" class="ah-sec" style="background:var(--ah-surface);">
  <div class="ah-c">
    <div class="ah-reveal-item" style="background:color-mix(in srgb,var(--ah-bg) 80%,black);border:1px solid rgba(255,255,255,.12);
        border-radius:28px;padding:3rem;box-shadow:0 24px 48px -12px rgba(0,0,0,.5);">
      <div style="display:grid;grid-template-columns:1fr;gap:2.5rem;align-items:start;">
        <div>
          <span class="sec-lbl">Venha nos Visitar</span>
          <h2 class="sec-h2" style="font-size:clamp(1.5rem,3vw,2.5rem);">{slug_label}</h2>
          <div class="sec-div"></div>
          <div style="display:flex;flex-direction:column;gap:1.25rem;margin-top:1.75rem;">
            {f'<div style="display:flex;align-items:flex-start;gap:.875rem;font-size:.9rem;color:var(--ah-text);"><i data-lucide="map-pin" style="color:var(--ah-accent);width:20px;flex-shrink:0;margin-top:2px;"></i><div><span style="font-weight:700;display:block;margin-bottom:2px;">Endereço</span><span style="color:var(--ah-text-muted);">{endereco}</span></div></div>' if endereco else ''}
            {f'<div style="display:flex;align-items:flex-start;gap:.875rem;font-size:.9rem;color:var(--ah-text);"><i data-lucide="clock" style="color:var(--ah-accent);width:20px;flex-shrink:0;margin-top:2px;"></i><div><span style="font-weight:700;display:block;margin-bottom:2px;">Horários</span><span style="color:var(--ah-text-muted);">{horarios}</span></div></div>' if horarios else ''}
            {f'<div style="display:flex;align-items:flex-start;gap:.875rem;font-size:.9rem;color:var(--ah-text);"><i data-lucide="phone" style="color:var(--ah-accent);width:20px;flex-shrink:0;margin-top:2px;"></i><div><span style="font-weight:700;display:block;margin-bottom:2px;">Telefone</span><span style="color:var(--ah-text-muted);">{telefone}</span></div></div>' if telefone else ''}
            {f'<div style="display:flex;align-items:flex-start;gap:.875rem;font-size:.9rem;color:var(--ah-text);"><i data-lucide="mail" style="color:var(--ah-accent);width:20px;flex-shrink:0;margin-top:2px;"></i><div><span style="font-weight:700;display:block;margin-bottom:2px;">E-mail</span><a href="mailto:{email}" style="color:var(--ah-accent);">{email}</a></div></div>' if email else ''}
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:1rem;margin-top:2rem;">
            {f'<a href="{wa_url}" class="btn-p" target="_blank"><i data-lucide="message-circle" style="width:14px;height:14px;"></i>{cta}</a>' if whatsapp else ''}
            {f'<a href="{ig_url}" class="btn-s" target="_blank"><i data-lucide="instagram" style="width:14px;height:14px;"></i>@{instagram}</a>' if instagram else ''}
          </div>
        </div>
        {f"""<div style="border-radius:20px;overflow:hidden;border:1px solid rgba(255,255,255,.12);height:320px;">
          <iframe src="https://maps.google.com/maps?q={maps_q}&output=embed&hl=pt-BR"
            width="100%" height="100%" style="border:0;display:block;" allowfullscreen loading="lazy">
          </iframe>
        </div>""" if (endereco or cidade) else ""}
      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer style="background:color-mix(in srgb,var(--ah-bg) 80%,black);border-top:1px solid rgba(255,255,255,.08);padding:3rem 0;text-align:center;">
  <div class="ah-c">
    <div style="display:inline-flex;align-items:center;gap:.75rem;margin-bottom:.75rem;">
      {f'<img src="{logo}" alt="Logo {nome}" style="height:36px;object-fit:contain;">' if logo else f'<div style="width:40px;height:40px;border-radius:50%;background:var(--ah-accent);color:var(--ah-bg);display:flex;align-items:center;justify-content:center;font-family:var(--ah-font-display);font-weight:900;font-size:1rem;">{slug_label[0].upper()}</div>'}
      <div style="text-align:left;">
        <div style="font-family:var(--ah-font-display);font-weight:900;font-size:1.1rem;letter-spacing:.15em;text-transform:uppercase;color:var(--ah-text);">{slug_label}</div>
        <div style="font-size:.65rem;letter-spacing:.2em;color:var(--ah-accent);text-transform:uppercase;font-weight:700;">{nicho} • {cidade}</div>
      </div>
    </div>
    <div style="font-size:.65rem;color:var(--ah-text-muted);margin-top:1.5rem;">© {year} {slug_label}. Site criado por <strong style="color:var(--ah-text);">Aholic Studio</strong>.</div>
  </div>
</footer>

<script>lucide.createIcons();</script>
<script>
/* Aholic Motion Engine v2 */
{motion_js}
</script>
</body>
</html>'''


def update_dashboard(slug: str, info: dict, preset_key: str, site_url: str):
    """Update dashboard.html and index.html with new lead data."""
    update_script = SCRIPTS_DIR / 'atualizar_dashboard.cjs'
    if not update_script.exists():
        print('  ⚠️  atualizar_dashboard.cjs não encontrado')
        return

    new_lead = {
        'slug': slug,
        'nome': info.get('nome', slug),
        'nicho': info.get('nicho', ''),
        'cidade': info.get('cidade', ''),
        'nota': info.get('nota', 0),
        'avaliacoes': info.get('avaliacoes', 0),
        'email': info.get('email', ''),
        'telefone': info.get('telefone', ''),
        'whatsapp': info.get('whatsapp', ''),
        'siteAntigo': info.get('siteAntigo', None),
        'motivo': info.get('motivo', ''),
        'status': 'site_pronto',
        'urlNova': f'sites/{slug}/index.html',
        'dataProposta': datetime.now().strftime('%Y-%m-%d'),
        'preset': preset_key,
    }

    # Call the Node.js updater
    import subprocess
    result = subprocess.run(
        ['node', str(update_script)],
        input=json.dumps({'action': 'add', 'lead': new_lead}),
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode == 0:
        print('  ✅ Dashboard atualizado')
    else:
        print(f'  ⚠️  Dashboard update falhou: {result.stderr[:200]}')


def git_push(slug: str, nome: str):
    result = subprocess.run(
        ['git', 'add', '.'],
        capture_output=True, text=True, encoding='utf-8', cwd=str(RAIZ)
    )
    msg = f'feat({slug}): site premium com motion engine e paleta adaptada — {nome}'
    result = subprocess.run(
        ['git', 'commit', '-m', msg],
        capture_output=True, text=True, encoding='utf-8', cwd=str(RAIZ)
    )
    result = subprocess.run(
        ['git', 'push', 'origin', 'main'],
        capture_output=True, text=True, encoding='utf-8', cwd=str(RAIZ)
    )
    if result.returncode == 0:
        print('  ✅ Deploy na Vercel iniciado')
    else:
        print(f'  ⚠️  Push falhou: {result.stderr[:200]}')


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Aholic Generator v2 — Criação automática de sites premium')
    parser.add_argument('--list',       action='store_true', help='Listar presets disponíveis')
    parser.add_argument('--slug',       help='Slug do lead (ex: cafe-shin)')
    parser.add_argument('--preset',     default='auto', help='Preset visual (ou "auto")')
    parser.add_argument('--instagram',  help='Username do Instagram (ex: @cafeshinparis)')
    parser.add_argument('--maps',       help='URL do Google Maps')
    parser.add_argument('--maps-query', help='Busca textual para o Maps (ex: "Café Shin Paris 10e")')
    parser.add_argument('--logo-url',   help='URL direta da logo do cliente')
    parser.add_argument('--info',       help='JSON com dados do cliente (nome, nicho, cidade, etc.)')
    parser.add_argument('--no-photos',  action='store_true', help='Pular extração de fotos')
    parser.add_argument('--no-colors',  action='store_true', help='Pular extração de paleta')
    parser.add_argument('--no-push',    action='store_true', help='Não fazer git push automático')
    args = parser.parse_args()

    if args.list:
        print('\n🎨 Presets Disponíveis:\n')
        for key, p in PRESETS.items():
            print(f'  [{key}]  {p["name"]}')
            print(f'    Nichos: {", ".join(p["nichos"])}')
            print(f'    Fontes: {p["fonts"]["display"]} + {p["fonts"]["body"]}')
            print()
        return

    if not args.slug:
        parser.print_help()
        sys.exit(1)

    slug = args.slug
    t_start = datetime.now()
    print(f'\n🚀 AHOLIC GENERATOR v2.0 — {slug}')
    print(f'   Iniciado em {t_start.strftime("%H:%M:%S")}')
    print('=' * 60)

    # ── Load or create info dict ──
    info_path = SITES_DIR / slug / 'assets' / 'info.json'
    if args.info:
        info = json.loads(args.info)
    elif info_path.exists():
        with open(info_path, encoding='utf-8') as f:
            info = json.load(f)
    else:
        info = {'nome': slug.replace('-', ' ').title(), 'nicho': '', 'cidade': ''}
    info.setdefault('nome', slug.replace('-', ' ').title())

    # ── Ensure dirs ──
    (SITES_DIR / slug / 'assets').mkdir(parents=True, exist_ok=True)

    # ── Save info.json ──
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    # ── Select preset ──
    preset_key = args.preset if args.preset != 'auto' else auto_select_preset(info.get('nicho', ''))
    preset = PRESETS.get(preset_key, PRESETS['cinema-local'])
    print(f'\n🎨 Preset: {preset["name"]} [{preset_key}]')

    # ── Step 1: Extract Photos ──
    if not args.no_photos and (args.instagram or args.maps or args.maps_query):
        print('\n📸 Fase 1: Extração de Fotos')
        photo_args = ['--slug', slug, '--max', '8']
        if args.maps:        photo_args += ['--maps', args.maps]
        if args.maps_query:  photo_args += ['--maps-query', args.maps_query]
        if args.instagram:   photo_args += ['--instagram', args.instagram]
        run_python(PHOTO_SCRIPT, photo_args, 'Extraindo fotos do Maps + Instagram')
    else:
        print('\n📸 Fase 1: Pulando extração de fotos (--no-photos ou sem fontes)')

    # ── Step 2: Extract Colors ──
    if not args.no_colors:
        print('\n🎨 Fase 2: Extração de Paleta de Cores')
        color_args = ['--slug', slug]
        if args.logo_url:
            color_args += ['--url', args.logo_url]
        success = run_python(COLOR_SCRIPT, color_args, 'Extraindo paleta da logo')
        if not success:
            print('  ℹ️  Paleta não extraída — usando tokens padrão do preset')
    else:
        print('\n🎨 Fase 2: Pulando extração de cores (--no-colors)')

    # ── Step 3: Load data ──
    palette = load_palette(slug)
    photos  = load_photos(slug)

    print(f'\n  🖼️  Hero: {photos.get("hero_candidate", "(nenhuma)")}')
    print(f'  🖼️  Galeria: {len(photos.get("gallery", []))} fotos')
    print(f'  🎨 Paleta: {"extraída da logo" if palette else "padrão do preset"}')

    # ── Step 4: Generate HTML ──
    print('\n📄 Fase 3: Gerando HTML...')
    html = build_html(slug, info, preset_key, preset, palette, photos)

    # Write files
    out_dir = SITES_DIR / slug
    (out_dir / 'index.html').write_text(html, encoding='utf-8')
    (out_dir / f'{slug}.html').write_text(html, encoding='utf-8')

    # Editor version
    editor_bar = '''<div style="position:fixed;top:0;left:0;right:0;height:48px;background:#0f172a;color:#f8fafc;
        display:flex;align-items:center;justify-content:space-between;padding:0 20px;
        font-family:system-ui;font-size:13px;z-index:999999;border-bottom:1px solid #334155;">
      <strong style="color:#38bdf8;">✨ Modo Edição Aholic</strong>
      <button onclick="alert('Exportar em breve!')" style="background:#22c55e;color:#fff;border:0;
          padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;">Exportar Site</button>
    </div>'''
    editor_html = html.replace('<body ', '<body style="padding-top:48px;" ').replace('<body>', '<body style="padding-top:48px;">')
    editor_html = editor_html.replace('</header>', '</header>' + editor_bar, 1)
    (out_dir / f'{slug}-editor.html').write_text(editor_html, encoding='utf-8')

    print(f'  ✅ sites/{slug}/index.html')
    print(f'  ✅ sites/{slug}/{slug}.html')
    print(f'  ✅ sites/{slug}/{slug}-editor.html')

    # ── Step 5: Deploy ──
    if not args.no_push:
        print('\n🚀 Fase 4: Deploy na Vercel')
        git_push(slug, info['nome'])

    elapsed = (datetime.now() - t_start).seconds
    vercel_url = f'https://aholicdigital.vercel.app/sites/{slug}/index.html'
    print(f'\n{"="*60}')
    print(f'✅ CONCLUÍDO em {elapsed}s')
    print(f'🔗 {vercel_url}')
    print(f'✏️  https://aholicdigital.vercel.app/sites/{slug}/{slug}-editor.html')
    print(f'{"="*60}\n')


if __name__ == '__main__':
    main()
