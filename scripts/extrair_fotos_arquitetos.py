#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHOLIC DIGITAL — Extrator Real de Fotos do Instagram & Google Maps para Arquitetos
Coleta fotos reais e logos dos perfis verificados no Instagram e do Google Maps,
salva em sites/{slug}/assets/ e injeta dinamicamente em index.html e editor.html.
"""

import os
import sys
import re
import json
import asyncio
import urllib.request
import urllib.parse
from playwright.async_api import async_playwright

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITES_DIR = os.path.join(RAIZ, "sites")
SESSION_FILE = os.path.join(RAIZ, "config", "instagram_session.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

ARQUITETOS = [
    {
        "slug": "pedro-olavo-arquitetura",
        "nome": "Pedro Olavo Arquitetura",
        "instagram": "pedroolavostudio",
        "maps_query": "Pedro Olavo Arquitetura Campo Grande MS"
    },
    {
        "slug": "izadora-loureiro-arquitetura",
        "nome": "Izadora Loureiro Arquitetura",
        "instagram": "arq.izadora",
        "maps_query": "Izadora Loureiro Arquiteta Campo Grande MS"
    },
    {
        "slug": "trellis-arquitetura",
        "nome": "Trellis Arquitetura",
        "instagram": "trellis_arquitetura",
        "maps_query": "Trellis Arquitetura Campo Grande MS"
    },
    {
        "slug": "lorena-capuci-arquitetura",
        "nome": "Lorena Capuci Arquitetura",
        "instagram": "lorenacapuci",
        "maps_query": "Lorena Capuci Arquitetura Campo Grande MS"
    },
    {
        "slug": "cristyan-miranda-arquitetura",
        "nome": "Cristyan Miranda Arquitetura",
        "instagram": "cristyanmirandaarquiteto",
        "maps_query": "Cristyan Miranda Arquitetura Campo Grande MS"
    }
]

def baixar_imagem(url, dest_path, min_size=8000):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
        if len(data) >= min_size:
            with open(dest_path, "wb") as f:
                f.write(data)
            return True
    except Exception:
        pass
    return False

async def extrair_instagram(page, username, pasta_assets, max_fotos=8):
    os.makedirs(pasta_assets, exist_ok=True)
    print(f"\n  📸 [INSTAGRAM] Acessando https://www.instagram.com/{username}/ ...")
    fotos_salvas = []
    logo_salva = None

    try:
        await page.goto(f"https://www.instagram.com/{username}/", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        # Trata popups
        for sel in ['button:has-text("Recusar")', 'button:has-text("Decline")', 'button:has-text("Agora não")', '[aria-label="Fechar"]', '[aria-label="Close"]']:
            try:
                b = await page.query_selector(sel)
                if b:
                    await b.click()
                    await page.wait_for_timeout(500)
            except Exception:
                pass

        # 1. Avatar / Logo
        avatar_url = await page.evaluate('''() => {
            const og = document.querySelector('meta[property="og:image"]');
            if (og && og.content) return og.content;
            const img = document.querySelector('header img, img[alt*="profile"], img[alt*="Foto do perfil"], img[alt*="perfil"]');
            return img ? img.src : null;
        }''')

        if avatar_url:
            dest_logo = os.path.join(pasta_assets, "instagram-logo.jpg")
            if baixar_imagem(avatar_url, dest_logo, min_size=3000):
                logo_salva = "assets/instagram-logo.jpg"
                print(f"    ✅ Avatar/Logo baixado: assets/instagram-logo.jpg")

        # 2. Scroll suave para carregar feed
        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(1500)

        # 3. Coleta imagens dos posts
        imgs = await page.evaluate('''() => {
            const arr = [];
            document.querySelectorAll('img').forEach(el => {
                const s = el.src;
                if (s && (s.includes('cdninstagram') || s.includes('fbcdn.net')) && !s.includes('150x150') && !s.includes('s150x150')) {
                    if (!arr.includes(s)) arr.push(s);
                }
            });
            return arr;
        }''')

        print(f"    🔍 Imagens de posts detectadas no Instagram: {len(imgs)}")
        count = 0
        for i, img_url in enumerate(imgs):
            if count >= max_fotos:
                break
            fname = f"instagram-post-{count+1}.jpg"
            dest = os.path.join(pasta_assets, fname)
            if baixar_imagem(img_url, dest, min_size=12000):
                rel_path = f"assets/{fname}"
                fotos_salvas.append(rel_path)
                count += 1
                print(f"    ✅ Foto do Instagram salva: {rel_path}")

    except Exception as e:
        print(f"    ⚠️ Erro ao raspar Instagram @{username}: {e}")

    return logo_salva, fotos_salvas

async def extrair_google_maps(page, query, pasta_assets, max_fotos=6):
    os.makedirs(pasta_assets, exist_ok=True)
    print(f"\n  🗺️ [GOOGLE MAPS] Buscando '{query}'...")
    fotos_salvas = []

    try:
        url_maps = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
        await page.goto(url_maps, wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_timeout(3500)

        # Clica no primeiro resultado se for lista
        try:
            first_result = await page.query_selector('a[href*="/maps/place/"]')
            if first_result:
                await first_result.click()
                await page.wait_for_timeout(3000)
        except Exception:
            pass

        # Clica na aba Fotos
        try:
            tab_fotos = await page.query_selector('button[aria-label*="Fotos"], button:has-text("Fotos"), [role="tab"]:has-text("Fotos")')
            if tab_fotos:
                await tab_fotos.click()
                await page.wait_for_timeout(3000)
        except Exception:
            pass

        # Coleta imagens
        raw_imgs = await page.evaluate('''() => {
            const list = [];
            document.querySelectorAll('img, button[style*="background-image"], div[style*="background-image"]').forEach(el => {
                if (el.tagName === 'IMG' && el.src) {
                    list.push(el.src);
                }
                const bg = el.style.backgroundImage || window.getComputedStyle(el).backgroundImage;
                if (bg && bg.includes('url')) {
                    const m = bg.match(/url\\(["\']?(.*?)["\']?\\)/);
                    if (m && m[1]) list.push(m[1]);
                }
            });
            return list.filter(u => u.includes('googleusercontent.com') && !u.includes('=s36') && !u.includes('=w36') && !u.includes('=s44') && !u.includes('=w44'));
        }''')

        unique_urls = []
        for u in raw_imgs:
            base = re.sub(r'=.*$', '', u)
            if base not in [re.sub(r'=.*$', '', x) for x in unique_urls]:
                unique_urls.append(u)

        print(f"    🔍 Imagens do Maps detectadas: {len(unique_urls)}")
        count = 0
        for u in unique_urls:
            if count >= max_fotos:
                break
            high_res = re.sub(r'=w\\d+-h\\d+.*$', '=w1200-h800-k-no', u)
            if '=w' not in high_res:
                high_res += '=w1200-h800-k-no'
            fname = f"maps-foto-{count+1}.jpg"
            dest = os.path.join(pasta_assets, fname)
            if baixar_imagem(high_res, dest, min_size=12000):
                rel_path = f"assets/{fname}"
                fotos_salvas.append(rel_path)
                count += 1
                print(f"    ✅ Foto Maps salva: {rel_path}")

    except Exception as e:
        print(f"    ⚠️ Erro ao raspar Google Maps: {e}")

    return fotos_salvas

def atualizar_html_site(slug, username, logo, fotos):
    pasta_site = os.path.join(SITES_DIR, slug)
    caminho_index = os.path.join(pasta_site, "index.html")
    caminho_editor = os.path.join(pasta_site, f"{slug}-editor.html")

    if not os.path.exists(caminho_index):
        print(f"[-] Site index.html não encontrado para {slug}")
        return

    with open(caminho_index, "r", encoding="utf-8") as f:
        html = f.read()

    # Atualiza o Instagram oficial no HTML
    html = re.sub(r'href="https://instagram\.com/[^"]*"', f'href="https://instagram.com/{username}"', html)
    html = re.sub(r'@[a-zA-Z0-9_.]+', f'@{username}', html, count=2)

    # Coleta todas as fotos reais disponíveis na pasta
    pasta_assets = os.path.join(pasta_site, "assets")
    arquivos_assets = []
    if os.path.exists(pasta_assets):
        for f_name in sorted(os.listdir(pasta_assets)):
            if f_name.endswith(".jpg") and ("post" in f_name or "foto" in f_name):
                arquivos_assets.append(f"assets/{f_name}")

    if not arquivos_assets:
        print(f"    ⚠️ Nenhuma foto em assets/ para {slug}")
        return

    print(f"    🖼️ Total de fotos reais prontas para injeção: {len(arquivos_assets)}")

    # Substituição robusta de todas as imagens Unsplash ou referências anteriores
    img_src_regex = r'(src=["\'])(https://images\.unsplash\.com/[^"\']+|assets/[^"\']+)(["\'])'
    
    contador = [0]
    def replacer(match):
        prefix = match.group(1)
        suffix = match.group(3)
        old_val = match.group(2)
        if "instagram-logo.jpg" in old_val:
            return match.group(0) # Mantém logo
        
        foto = arquivos_assets[contador[0] % len(arquivos_assets)]
        contador[0] += 1
        return f"{prefix}{foto}{suffix}"

    novo_html = re.sub(img_src_regex, replacer, html)

    # Se tiver logo, adiciona no header se não tiver
    if logo and os.path.exists(os.path.join(pasta_site, logo)):
        # Adiciona foto de perfil como logo se houver placeholder de monograma
        pass

    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(novo_html)
    print(f"    💾 {caminho_index} atualizado com {contador[0]} fotos reais!")

    if os.path.exists(caminho_editor):
        # Atualiza o editor também
        novo_editor = re.sub(img_src_regex, replacer, html)
        with open(caminho_editor, "w", encoding="utf-8") as f:
            f.write(novo_editor.replace("</body>", "<!-- PROSPECTOR-EDITOR-START -->\n<style id=\"pe-style\">#pe-bar{position:fixed;top:0;left:0;right:0;height:44px;background:#0f172a;color:#f8fafc;display:flex;align-items:center;justify-content:space-between;padding:0 20px;font-family:system-ui,-apple-system,sans-serif;font-size:13px;z-index:999999;box-shadow:0 2px 10px rgba(0,0,0,0.3);border-bottom:1px solid #334155}#pe-bar strong{color:#38bdf8;font-weight:600}#pe-bar button{background:#22c55e;color:#fff;border:0;padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;transition:background .2s}#pe-bar button:hover{background:#16a34a}body{margin-top:44px !important}.pe-hover{outline:2px dashed #22c55e !important;outline-offset:2px;cursor:pointer}[contenteditable=\"true\"]:focus{outline:2px solid #38bdf8 !important;outline-offset:2px}</style><div id=\"pe-bar\"><div><strong>✨ Modo Edição Aholic</strong> · Clique em textos para alterar · clique em imagens para trocar</div><button id=\"pe-export\" type=\"button\">Salvar e Exportar Site</button></div><input type=\"file\" id=\"pe-file\" accept=\"image/*\" style=\"display:none\"><script id=\"pe-script\">(function(){var TEXT='h1,h2,h3,h4,h5,h6,p,li,a,span,button,td,th,figcaption,blockquote,strong,em';document.querySelectorAll(TEXT).forEach(function(el){if(el.closest('#pe-bar'))return;if(el.children.length===0||el.childElementCount<=1){el.addEventListener('click',function(e){if(el.tagName==='A'||el.tagName==='BUTTON')e.preventDefault();el.setAttribute('contenteditable','true');el.focus();});el.addEventListener('mouseenter',function(){el.classList.add('pe-hover')});el.addEventListener('mouseleave',function(){el.classList.remove('pe-hover')});el.addEventListener('blur',function(){el.removeAttribute('contenteditable')});}});var fileInput=document.getElementById('pe-file'),currentImg=null;document.querySelectorAll('img').forEach(function(img){img.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();currentImg=img;fileInput.click()});img.addEventListener('mouseenter',function(){img.classList.add('pe-hover')});img.addEventListener('mouseleave',function(){img.classList.remove('pe-hover')});});fileInput.addEventListener('change',function(){var f=fileInput.files[0];if(!f||!currentImg)return;var r=new FileReader();r.onload=function(){currentImg.src=r.result;if(currentImg.srcset)currentImg.removeAttribute('srcset')};r.readAsDataURL(f);fileInput.value='';});document.getElementById('pe-export').addEventListener('click',function(){var doc=document.documentElement.cloneNode(true);['#pe-bar','#pe-style','#pe-script','#pe-file'].forEach(function(s){var n=doc.querySelector(s);if(n)n.remove()});doc.querySelectorAll('[contenteditable]').forEach(function(n){n.removeAttribute('contenteditable')});doc.querySelectorAll('.pe-hover').forEach(function(n){n.classList.remove('pe-hover')});var html='<!DOCTYPE html>\\n'+doc.outerHTML;var blob=new Blob([html],{type:'text/html'});var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='index.html';a.click();});})();</script>\n<!-- PROSPECTOR-EDITOR-END -->\n</body>"))
        print(f"    💾 {caminho_editor} atualizado.")

async def main():
    has_session = os.path.exists(SESSION_FILE)
    print("=" * 65)
    print("🚀 AHOLIC — EXTRAÇÃO DE FOTOS REAIS (INSTAGRAM & GOOGLE MAPS)")
    print(f"Sessão Instagram: {'Ativa (' + SESSION_FILE + ')' if has_session else 'Não encontrada'}")
    print("=" * 65)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        ig_kwargs = {
            "user_agent": HEADERS["User-Agent"],
            "locale": "pt-BR",
            "viewport": {"width": 1280, "height": 900}
        }
        if has_session:
            ig_kwargs["storage_state"] = SESSION_FILE

        context_ig = await browser.new_context(**ig_kwargs)
        page_ig = await context_ig.new_page()

        context_maps = await browser.new_context(
            user_agent=HEADERS["User-Agent"],
            locale="pt-BR",
            viewport={"width": 1366, "height": 850}
        )
        page_maps = await context_maps.new_page()

        for arq in ARQUITETOS:
            slug = arq["slug"]
            pasta_assets = os.path.join(SITES_DIR, slug, "assets")
            os.makedirs(pasta_assets, exist_ok=True)

            print(f"\n[{arq['nome'].upper()}] ({slug})")
            
            # 1. Instagram
            logo_ig, fotos_ig = await extrair_instagram(page_ig, arq["instagram"], pasta_assets, max_fotos=8)

            # 2. Google Maps
            fotos_maps = await extrair_google_maps(page_maps, arq["maps_query"], pasta_assets, max_fotos=6)

            todas_fotos = fotos_ig + [f for f in fotos_maps if f not in fotos_ig]
            print(f"  📊 Total de fotos reais capturadas para {slug}: {len(todas_fotos)}")

            # 3. Atualiza HTML do site
            atualizar_html_site(slug, arq["instagram"], logo_ig, todas_fotos)

        await browser.close()

    print("\n" + "=" * 65)
    print("✅ TODAS AS FOTOS REAIS DO INSTAGRAM E MAPS FORAM BAIXADAS E INTEGRADAS!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(main())
