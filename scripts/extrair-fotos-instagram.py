#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator Oficial de Fotos e Logo do Instagram com Suporte a Sessão Salva.
Uso: python extrair-fotos-instagram.py <usuario_instagram> <pasta_destino> [max_fotos]
"""
import asyncio, os, re, sys, json, urllib.request, urllib.parse
from playwright.async_api import async_playwright

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_DIR = os.path.join(WORKSPACE, "config")
SESSION_FILE = os.path.join(CONFIG_DIR, "instagram_session.json")

async def extrair_instagram(username, output_dir, max_fotos=8):
    os.makedirs(output_dir, exist_ok=True)
    username = username.strip().replace("@", "").replace("https://www.instagram.com/", "").replace("https://instagram.com/", "").strip("/")
    results = {"username": username, "logo": None, "fotos": []}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    has_session = os.path.exists(SESSION_FILE)
    if has_session:
        print(f"[*] Usando sessão autenticada do Instagram ({SESSION_FILE})")
    else:
        print("[*] Nenhuma sessão salva encontrada. Rodando em modo público / visitante.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        context_kwargs = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "locale": "pt-BR",
            "viewport": {"width": 1280, "height": 900}
        }
        if has_session:
            context_kwargs["storage_state"] = SESSION_FILE

        context = await browser.new_context(**context_kwargs)
        page = await context.new_page()

        url = f"https://www.instagram.com/{username}/"
        print(f"[*] Acessando Instagram oficial: @{username}")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3500)

        # Fecha modais de cookies/login se aparecerem
        try:
            btn = await page.query_selector('button:has-text("Recusar"), button:has-text("Decline"), button:has-text("Agora não"), [aria-label*="Fechar"], svg[aria-label*="Fechar"]')
            if btn:
                await btn.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass

        # 1. Extrair Avatar / Logo oficial do perfil
        avatar_src = await page.evaluate('''() => {
            const og = document.querySelector('meta[property="og:image"]');
            if (og && og.content) return og.content;
            const img = document.querySelector('header img, img[alt*="profile"], img[alt*="Foto de perfil"]');
            return img ? img.src : null;
        }''')

        if avatar_src:
            logo_path = os.path.join(output_dir, "instagram-logo.jpg")
            try:
                req = urllib.request.Request(avatar_src, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp, open(logo_path, "wb") as f:
                    f.write(resp.read())
                results["logo"] = "instagram-logo.jpg"
                print(f"[+] Logo oficial do Instagram salva: {logo_path} ({os.path.getsize(logo_path)} bytes)")
            except Exception as e:
                print("[-] Erro ao salvar avatar:", e)

        # 2. Scroll para carregar mais posts (se logado, rola várias vezes)
        scroll_count = 4 if has_session else 2
        for s in range(scroll_count):
            await page.evaluate("window.scrollBy(0, 1000)")
            await page.wait_for_timeout(2000)

        # 3. Coletar URLs das imagens dos posts
        images = await page.evaluate('''() => {
            const list = [];
            document.querySelectorAll('img').forEach(img => {
                let s = img.src;
                if (s && (s.includes('cdninstagram') || s.includes('fbcdn.net')) && !s.includes('150x150') && !s.includes('s150x150')) {
                    if (!list.includes(s)) list.push(s);
                }
            });
            return list;
        }''')

        print(f"[*] Fotos de posts identificadas no Instagram: {len(images)}")

        # 4. Fallback para espelho se não encontrou imagens suficientes
        if len(images) < 4:
            print("[*] Tentando espelho público para carregar fotos adicionais...")
            try:
                await page.goto(f"https://imginn.com/{username}/", timeout=15000)
                await page.wait_for_timeout(3000)
                more_imgs = await page.evaluate('''() => {
                    const l = [];
                    document.querySelectorAll('.items img, .post-item img').forEach(i => {
                        if (i.src && !l.includes(i.src)) l.push(i.src);
                    });
                    return l;
                }''')
                for m in more_imgs:
                    if m not in images:
                        images.append(m)
            except Exception as e:
                print("[-] Espelho fallback:", e)

        # 5. Baixar as fotos reais em alta resolução
        count = 0
        for idx, img_url in enumerate(images):
            if count >= max_fotos:
                break
            filename = f"instagram-post-{count+1}.jpg"
            dest_path = os.path.join(output_dir, filename)

            try:
                req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as resp, open(dest_path, "wb") as f:
                    f.write(resp.read())
                
                size = os.path.getsize(dest_path)
                if size > 15000: # Foto válida > 15KB
                    results["fotos"].append({"arquivo": filename, "tamanho_kb": round(size/1024, 1), "caminho": dest_path})
                    print(f"[+] Foto do post {count+1} salva: {filename} ({round(size/1024, 1)} KB)")
                    count += 1
                else:
                    os.remove(dest_path)
            except Exception as e:
                print(f"[-] Erro ao baixar foto {idx}: {e}")

        await browser.close()

    print(f"[*] Concluído! {len(results['fotos'])} fotos reais salvas em {output_dir}")
    return results

if __name__ == '__main__':
    args = sys.argv[1:]
    user = args[0] if len(args) > 0 else "karlabarrosarquitetura"
    out = args[1] if len(args) > 1 else r"sites/karla-barros-arquitetura/assets"
    m = int(args[2]) if len(args) > 2 else 6
    asyncio.run(extrair_instagram(user, out, m))
