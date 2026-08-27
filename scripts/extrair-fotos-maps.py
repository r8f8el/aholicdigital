#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator Oficial de Fotos Reais e Logo do Google Maps / Redes Sociais.
Uso: python extrair-fotos-maps.py "Nome do Cliente e Cidade" "sites/[slug]/assets" [max_fotos]
"""
import asyncio, os, re, sys, json, urllib.request, urllib.parse
from playwright.async_api import async_playwright

async def extrair(query, output_dir, max_fotos=5):
    os.makedirs(output_dir, exist_ok=True)
    results = {"query": query, "output_dir": output_dir, "fotos": []}
    
    print(f"[*] Iniciando extração para: {query}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR",
            viewport={"width": 1280, "height": 900}
        )
        page = await context.new_page()
        
        search_url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
        print(f"[*] Acessando Google Maps: {search_url}")
        await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)
        
        # Click place card if multiple results appear
        first_card = await page.query_selector('a[href*="/maps/place/"]')
        if first_card:
            print("[*] Abrindo perfil detalhado da empresa...")
            await first_card.click()
            await page.wait_for_timeout(4000)

        # Collect images on place profile
        raw_images = await page.evaluate('''() => {
            const urls = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.tagName === 'IMG' && el.src) urls.push(el.src);
                const bg = window.getComputedStyle(el).backgroundImage;
                if (bg && bg.includes('url')) {
                    const m = bg.match(/url\(["']?(.*?)["']?\)/);
                    if (m && m[1]) urls.push(m[1]);
                }
            });
            return urls.filter(u => u.includes('googleusercontent.com') && !u.includes('=s36') && !u.includes('=w36') && !u.includes('=s44'));
        }''')
        
        unique_urls = []
        for u in raw_images:
            base = re.sub(r'=.*$', '', u)
            if base not in [re.sub(r'=.*$', '', x) for x in unique_urls]:
                unique_urls.append(u)
                
        print(f"[*] Fotos reais identificadas: {len(unique_urls)}")
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        count = 0
        for idx, img_url in enumerate(unique_urls):
            if count >= max_fotos:
                break
            
            high_res_url = re.sub(r'=w\d+-h\d+.*$', '=w1600-h1200-k-no', img_url)
            if '=w' not in high_res_url and '=h' not in high_res_url:
                high_res_url += '=w1600-h1200-no'
            elif '=w' not in high_res_url:
                high_res_url = re.sub(r'=.*$', '=w1600-h1200-k-no', high_res_url)

            filename = f"google-maps-foto-{count+1}.jpg" if count > 0 else "fachada-principal.jpg"
            dest_path = os.path.join(output_dir, filename)
            
            try:
                req = urllib.request.Request(high_res_url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as resp, open(dest_path, "wb") as f:
                    f.write(resp.read())
                
                size = os.path.getsize(dest_path)
                if size > 15000:
                    results["fotos"].append({"arquivo": filename, "tamanho_kb": round(size/1024, 1), "caminho": dest_path})
                    print(f"[+] Baixada com sucesso: {filename} ({round(size/1024, 1)} KB)")
                    count += 1
                else:
                    os.remove(dest_path)
            except Exception as e:
                print(f"[-] Erro ao baixar imagem {idx}: {e}")

        await browser.close()

    print(f"[*] Concluído! {len(results['fotos'])} fotos reais salvas em {output_dir}")
    return results

if __name__ == '__main__':
    args = sys.argv[1:]
    q = args[0] if len(args) > 0 else "Quality Odontologia e Face Caldas Novas"
    o = args[1] if len(args) > 1 else r"sites/quality-odontologia-face/assets"
    m = int(args[2]) if len(args) > 2 else 5
    asyncio.run(extrair(q, o, m))
