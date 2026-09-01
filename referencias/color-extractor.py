#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHOLIC COLOR EXTRACTOR v1.0
Extrai a paleta de cores dominante de uma logo/imagem do cliente
e gera os tokens CSS parametrizáveis para uso nos presets.

Dependências: pip install Pillow colorthief requests

Uso:
  python referencias/color-extractor.py --url "https://..." --slug "cafe-shin"
  python referencias/color-extractor.py --img "sites/cafe-shin/assets/logo.png" --slug "cafe-shin"
  python referencias/color-extractor.py --slug "cafe-shin"   # busca logo automática em assets/
"""

import os
import sys
import json
import math
import argparse
import colorsys
import urllib.request
import urllib.parse
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

RAIZ = Path(__file__).parent.parent
SITES_DIR = RAIZ / 'sites'

# ─── Color helpers ──────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return '#{:02X}{:02X}{:02X}'.format(int(r), int(g), int(b))

def luminance(r, g, b):
    """Relative luminance (WCAG 2.1)"""
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)

def contrast_ratio(rgb1, rgb2):
    l1 = luminance(*rgb1) + 0.05
    l2 = luminance(*rgb2) + 0.05
    return max(l1, l2) / min(l1, l2)

def is_dark(r, g, b):
    return luminance(r, g, b) < 0.35

def saturate(r, g, b, factor=1.15):
    """Boost saturation slightly."""
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    s = min(1.0, s * factor)
    nr, ng, nb = colorsys.hsv_to_rgb(h, s, v)
    return int(nr*255), int(ng*255), int(nb*255)

def darken(r, g, b, factor=0.65):
    return int(r*factor), int(g*factor), int(b*factor)

def lighten(r, g, b, factor=1.5):
    return min(255, int(r*factor)), min(255, int(g*factor)), min(255, int(b*factor))

def is_too_neutral(r, g, b, threshold=20):
    """Returns True if color is nearly grayscale."""
    return max(abs(r-g), abs(g-b), abs(r-b)) < threshold

def is_too_white(r, g, b, threshold=230):
    return r > threshold and g > threshold and b > threshold

def is_too_black(r, g, b, threshold=30):
    return r < threshold and g < threshold and b < threshold


# ─── Image loading ──────────────────────────────────────────────────────────

def load_image(source: str):
    """Load an image from path or URL. Returns (PIL.Image, source_path)."""
    try:
        from PIL import Image
    except ImportError:
        print('❌ Pillow não instalado. Execute: pip install Pillow colorthief')
        sys.exit(1)

    if source.startswith('http://') or source.startswith('https://'):
        import io
        req = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        img = Image.open(io.BytesIO(data)).convert('RGBA')
        return img, source
    else:
        img = Image.open(source).convert('RGBA')
        return img, source


def find_logo_in_assets(slug: str):
    """Look for common logo file names in sites/<slug>/assets/."""
    asset_dir = SITES_DIR / slug / 'assets'
    candidates = ['logo.png', 'logo.jpg', 'logo.svg', 'logo.webp',
                  'logo-white.png', 'logo-dark.png', 'brand.png']
    for c in candidates:
        p = asset_dir / c
        if p.exists():
            return str(p)
    return None


# ─── Palette extraction ─────────────────────────────────────────────────────

def extract_palette(image_source: str, n_colors: int = 8):
    """
    Extract dominant colors using ColorThief.
    Returns list of (r, g, b) tuples sorted by dominance.
    """
    try:
        from colorthief import ColorThief
    except ImportError:
        print('❌ colorthief não instalado. Execute: pip install colorthief')
        sys.exit(1)

    import io
    try:
        from PIL import Image
        img, _ = load_image(image_source)
        # Remove alpha (white background)
        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img_rgb = background.convert('RGB')
        buf = io.BytesIO()
        img_rgb.save(buf, format='PNG')
        buf.seek(0)
        ct = ColorThief(buf)
        palette = ct.get_palette(color_count=n_colors, quality=1)
        return palette
    except Exception as e:
        print(f'⚠️  Erro ao extrair paleta: {e}')
        return [(100, 80, 60)]  # fallback


def pick_brand_colors(palette):
    """
    From the raw palette, intelligently select:
      - primary: most saturated/distinctive (not white, not black)
      - accent:  second most distinctive, contrasting with primary
      - bg:      darkest usable color (or pure dark if all light)
      - text:    auto-computed for contrast
    """
    # Filter out near-white, near-black, and gray
    useful = [
        c for c in palette
        if not is_too_white(*c) and not is_too_black(*c) and not is_too_neutral(*c)
    ]

    if not useful:
        useful = palette  # nothing filtered, use all

    # Sort by saturation descending
    def sat(rgb):
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        return s

    useful_sorted = sorted(useful, key=sat, reverse=True)

    primary = useful_sorted[0] if useful_sorted else (180, 140, 80)
    accent  = useful_sorted[1] if len(useful_sorted) > 1 else saturate(*primary, 1.2)

    # Background: prefer the darkest color from the original palette
    dark_candidates = sorted(palette, key=lambda c: luminance(*c))
    bg_raw = dark_candidates[0]

    # If the darkest is still quite light, push it darker
    if luminance(*bg_raw) > 0.15:
        bg = darken(*bg_raw, 0.45)
    else:
        bg = bg_raw

    # Surface (card bg): slightly lighter than bg
    surface = lighten(*bg, 1.3)
    surface = (min(255, surface[0]), min(255, surface[1]), min(255, surface[2]))

    # Text: choose white or off-white vs near-black based on bg luminance
    if is_dark(*bg):
        text = (245, 242, 235)  # off-white
        text_muted = (155, 163, 159)
    else:
        text = (20, 20, 18)
        text_muted = (100, 100, 95)

    # Accent soft (for backgrounds/borders)
    accent_r, accent_g, accent_b = accent
    accent_soft = f'rgba({accent_r},{accent_g},{accent_b},0.15)'

    return {
        'primary': primary,
        'accent': accent,
        'bg': bg,
        'surface': surface,
        'text': text,
        'text_muted': text_muted,
        'accent_soft': accent_soft,
    }


def build_palette_json(slug: str, colors: dict, image_source: str, raw_palette: list):
    """Build the full paleta.json structure."""
    def to_hex(rgb): return rgb_to_hex(*rgb)

    return {
        'slug': slug,
        'source': image_source,
        'generated_at': __import__('datetime').datetime.now().isoformat(),
        'raw_palette': [to_hex(*c) for c in raw_palette[:6]],
        'tokens': {
            '--ah-primary':    to_hex(*colors['primary']),
            '--ah-accent':     to_hex(*colors['accent']),
            '--ah-bg':         to_hex(*colors['bg']),
            '--ah-surface':    to_hex(*colors['surface']),
            '--ah-text':       to_hex(*colors['text']),
            '--ah-text-muted': to_hex(*colors['text_muted']),
            '--ah-accent-soft':colors['accent_soft'],
        },
        'css_vars': build_css_vars(colors),
        'tailwind_safe': build_tailwind(colors),
        'contrast_check': {
            'text_on_bg': round(contrast_ratio(colors['text'], colors['bg']), 2),
            'accent_on_bg': round(contrast_ratio(colors['accent'], colors['bg']), 2),
            'wcag_aa_pass': contrast_ratio(colors['text'], colors['bg']) >= 4.5,
        }
    }


def build_css_vars(colors):
    def to_hex(rgb): return rgb_to_hex(*rgb)
    lines = [
        ':root {',
        f"  --ah-primary:     {to_hex(*colors['primary'])};",
        f"  --ah-accent:      {to_hex(*colors['accent'])};",
        f"  --ah-bg:          {to_hex(*colors['bg'])};",
        f"  --ah-surface:     {to_hex(*colors['surface'])};",
        f"  --ah-text:        {to_hex(*colors['text'])};",
        f"  --ah-text-muted:  {to_hex(*colors['text_muted'])};",
        f"  --ah-accent-soft: {colors['accent_soft']};",
        f"  --ah-preloader-bg:   {to_hex(*colors['bg'])};",
        f"  --ah-preloader-text: {to_hex(*colors['text'])};",
        '}',
    ]
    return '\n'.join(lines)


def build_tailwind(colors):
    def to_hex(rgb): return rgb_to_hex(*rgb)
    return {
        'primary': to_hex(*colors['primary']),
        'accent':  to_hex(*colors['accent']),
        'bg':      to_hex(*colors['bg']),
        'surface': to_hex(*colors['surface']),
        'text':    to_hex(*colors['text']),
    }


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Aholic Color Extractor — extrai paleta de cores da logo do cliente'
    )
    parser.add_argument('--slug', required=True, help='Slug do lead (ex: cafe-shin)')
    parser.add_argument('--url', help='URL pública da logo/imagem')
    parser.add_argument('--img', help='Caminho local para a logo')
    parser.add_argument('--out', help='Caminho de saída (default: sites/<slug>/assets/paleta.json)')
    args = parser.parse_args()

    slug = args.slug
    source = args.url or args.img or find_logo_in_assets(slug)

    if not source:
        print(f'❌ Nenhuma logo encontrada para "{slug}".')
        print(f'   Passe --url ou --img, ou coloque logo.png em sites/{slug}/assets/')
        sys.exit(1)

    print(f'🎨 Extraindo paleta de cores para "{slug}"')
    print(f'   Fonte: {source}')

    # Extract
    raw_palette = extract_palette(source)
    colors = pick_brand_colors(raw_palette)

    # Build output
    palette_data = build_palette_json(slug, colors, source, raw_palette)

    # Save
    out_path = args.out or str(SITES_DIR / slug / 'assets' / 'paleta.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(palette_data, f, ensure_ascii=False, indent=2)

    print(f'\n✅ Paleta gerada: {out_path}')
    print(f'\n📊 Tokens de Cor:')
    for k, v in palette_data['tokens'].items():
        print(f'   {k}: {v}')
    print(f'\n📐 Contraste texto/fundo: {palette_data["contrast_check"]["text_on_bg"]}:1', end='')
    print(f'  {"✅ WCAG AA" if palette_data["contrast_check"]["wcag_aa_pass"] else "⚠️  Abaixo AA"}')

    print(f'\n🎨 CSS Vars (cole no <style> do site):')
    print(palette_data['css_vars'])

    return palette_data


if __name__ == '__main__':
    main()
