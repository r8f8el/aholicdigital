#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHOLIC DIGITAL — Minerador Unificado de Leads
Google Maps (Sem Site) + Extração de Fotos do Instagram + Cadastro no SQLite & leads.md

Uso via linha de comando:
  python scripts/minerar-leads.py --nicho "estetica" --cidade "Caldas Novas" --limite 5
  python scripts/minerar-leads.py --nicho "odontologia" --cidade "Goiania" --limite 10 --visible
"""

import asyncio
import argparse
import json
import os
import re
import sqlite3
import sys
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime
from playwright.async_api import async_playwright

# Garante saída UTF-8 no Windows sem erros de charmap
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PASTA_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(PASTA_SCRIPTS, ".."))
DB_PATH = os.path.join(RAIZ, "prospector.db")
LEADS_MD_PATH = os.path.join(RAIZ, "leads.md")
CONFIG_DIR = os.path.join(RAIZ, "config")
SESSION_FILE = os.path.join(CONFIG_DIR, "instagram_session.json")
SITES_DIR = os.path.join(RAIZ, "sites")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

def normalizar_slug(texto):
    """Transforma qualquer texto em slug limpo para diretórios e banco."""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = re.sub(r'[^a-zA-Z0-9\s-]', '', texto).strip().lower()
    texto = re.sub(r'[-\s]+', '-', texto)
    return texto[:60].strip('-')

def formatar_whatsapp(numero_str):
    """Converte telefones no formato 55DDDNUMERO para wa.me."""
    if not numero_str:
        return ""
    limpo = re.sub(r'\D', '', numero_str)
    if limpo.startswith('0'):
        limpo = limpo[1:]
    if len(limpo) in (10, 11):
        limpo = '55' + limpo
    return limpo if len(limpo) >= 12 else ""

def formatar_telefone_br(numero_str):
    """Formata visualmente no padrão (DD) 9XXXX-XXXX."""
    limpo = re.sub(r'\D', '', numero_str)
    if limpo.startswith('55') and len(limpo) in (12, 13):
        limpo = limpo[2:]
    if len(limpo) == 11:
        return f"({limpo[:2]}) {limpo[2:7]}-{limpo[7:]}"
    elif len(limpo) == 10:
        return f"({limpo[:2]}) {limpo[2:6]}-{limpo[6:]}"
    return numero_str

def conectar_banco():
    """Garante conexão com prospector.db e schema alinhado."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS leads(
        slug TEXT PRIMARY KEY, nome TEXT, nicho TEXT, cidade TEXT, nota REAL, avaliacoes INTEGER,
        email TEXT, telefone TEXT, whatsapp TEXT, siteAntigo TEXT, motivo TEXT,
        status TEXT DEFAULT 'novo', urlNova TEXT, dataProposta TEXT, valor REAL, obs TEXT,
        contratoStatus TEXT DEFAULT 'pendente', contratoEm TEXT, manutencao REAL, pago INTEGER DEFAULT 0,
        atualizado TEXT DEFAULT (datetime('now','localtime')),
        docCliente TEXT, endCliente TEXT, direcaoCriativa TEXT)''')
    conn.commit()
    return conn

def lead_ja_existe(slug):
    """Verifica se o lead já está no banco de dados local."""
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT slug FROM leads WHERE slug = ?", (slug,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def salvar_lead_banco(dados):
    """Salva ou atualiza os dados do lead no banco SQLite."""
    conn = conectar_banco()
    campos = [
        'slug', 'nome', 'nicho', 'cidade', 'nota', 'avaliacoes', 'email', 'telefone', 'whatsapp',
        'siteAntigo', 'motivo', 'status', 'urlNova', 'dataProposta', 'valor', 'obs',
        'contratoStatus', 'contratoEm', 'manutencao', 'pago', 'docCliente', 'endCliente', 'direcaoCriativa'
    ]
    interrogacoes = ','.join(['?'] * len(campos))
    nomes_colunas = ','.join(campos)
    valores = [dados.get(k) for k in campos]
    
    conn.execute(f"INSERT OR REPLACE INTO leads ({nomes_colunas}) VALUES ({interrogacoes})", valores)
    conn.commit()
    conn.close()

def atualizar_leads_md(dados):
    """Adiciona o lead minerado na tabela do leads.md se ainda não estiver presente."""
    if not os.path.exists(LEADS_MD_PATH):
        cabecalho = (
            "# Leads Prospector — Aholic Studio\n\n"
            "| # | Nome do Estabelecimento / Especialista | Nota | Aval. | WhatsApp | Tipo | Site Atual | Motivo / Oportunidade | Status |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
        )
        with open(LEADS_MD_PATH, "w", encoding="utf-8") as f:
            f.write(cabecalho)

    with open(LEADS_MD_PATH, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Verifica se já está no leads.md
    if dados['nome'] in conteudo or dados['slug'] in conteudo:
        return

    linhas = [l for l in conteudo.strip().split("\n") if l.strip().startswith("|") and not l.strip().startswith("| #") and not l.strip().startswith("|---")]
    novo_num = len(linhas) + 1

    nota_str = f"{dados['nota']} ★" if dados['nota'] else "-"
    aval_str = str(dados['avaliacoes']) if dados['avaliacoes'] else "-"
    tel_str = dados['telefone'] if dados['telefone'] else (dados['whatsapp'] or "-")
    site_str = dados['siteAntigo'] if dados['siteAntigo'] else "*(Nenhum)*"
    motivo_str = dados['motivo'] or "Negócio de alto valor sem site próprio. Presença apenas no Maps/Instagram."

    nova_linha = f"| {novo_num} | **{dados['nome']}** | {nota_str} | {aval_str} | {tel_str} | **Do Zero** | {site_str} | {motivo_str} | {dados['status']} |\n"

    with open(LEADS_MD_PATH, "a", encoding="utf-8") as f:
        f.write(nova_linha)

async def buscar_instagram_por_nome(page, nome_empresa, cidade):
    """Tenta descobrir o perfil do Instagram da empresa via busca rápida."""
    query = f"{nome_empresa} {cidade} instagram"
    url_busca = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url_busca, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            m = re.findall(r'instagram\.com/([a-zA-Z0-9_.-]+)', html)
            descartar = ['p', 'explore', 'reels', 'stories', 'direct', 'accounts', 'developer', 'about']
            for username in m:
                u = username.strip('/').lower()
                if u not in descartar and not u.startswith(('p/', 'reel/')):
                    return u
    except Exception as e:
        print(f"[-] Aviso busca Insta DDG: {e}")
    return None

async def extrair_assets_instagram(page, username, pasta_assets, max_fotos=6):
    """Extrai logo e fotos do perfil do Instagram usando Playwright com a sessão salva."""
    os.makedirs(pasta_assets, exist_ok=True)
    username = username.strip().replace("@", "").strip("/")
    resultado = {"username": username, "logo": None, "fotos": [], "bio": ""}

    print(f"  📸 Acessando Instagram oficial: @{username}...")
    try:
        await page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_timeout(3000)

        # Fecha modais eventuais de cookies/login
        try:
            btn = await page.query_selector('button:has-text("Recusar"), button:has-text("Decline"), button:has-text("Agora não"), [aria-label*="Fechar"]')
            if btn:
                await btn.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass

        # 1. Extração da Bio
        bio_text = await page.evaluate('''() => {
            const h = document.querySelector('header');
            if (!h) return '';
            const spans = h.querySelectorAll('span, h1, div');
            for (let s of spans) {
                if (s.innerText && s.innerText.length > 25 && !s.innerText.includes('seguidores')) {
                    return s.innerText;
                }
            }
            const ogDesc = document.querySelector('meta[property="og:description"]');
            return ogDesc ? ogDesc.content : '';
        }''')
        resultado["bio"] = bio_text.strip()

        # 2. Extração do Avatar / Logo
        avatar_src = await page.evaluate('''() => {
            const og = document.querySelector('meta[property="og:image"]');
            if (og && og.content) return og.content;
            const img = document.querySelector('header img, img[alt*="profile"], img[alt*="Foto de perfil"]');
            return img ? img.src : null;
        }''')

        if avatar_src:
            logo_path = os.path.join(pasta_assets, "instagram-logo.jpg")
            try:
                req = urllib.request.Request(avatar_src, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=10) as resp, open(logo_path, "wb") as f:
                    f.write(resp.read())
                if os.path.getsize(logo_path) > 1000:
                    resultado["logo"] = "instagram-logo.jpg"
                    print(f"  [+] Logo do Instagram salva: instagram-logo.jpg")
            except Exception as e:
                print(f"  [-] Erro ao salvar avatar Instagram: {e}")

        # 3. Rolar para carregar fotos do feed
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 1000)")
            await page.wait_for_timeout(1500)

        # 4. URLs de fotos
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

        # Baixar fotos
        count = 0
        for img_url in images:
            if count >= max_fotos:
                break
            filename = f"instagram-post-{count+1}.jpg"
            dest_path = os.path.join(pasta_assets, filename)
            try:
                req = urllib.request.Request(img_url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=10) as resp, open(dest_path, "wb") as f:
                    f.write(resp.read())
                size = os.path.getsize(dest_path)
                if size > 15000: # Valida se é imagem real > 15KB
                    resultado["fotos"].append(filename)
                    count += 1
                else:
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
            except Exception:
                pass

        print(f"  [+] {len(resultado['fotos'])} fotos reais extraídas do feed do Instagram.")

    except Exception as e:
        print(f"  [-] Erro ao raspar Instagram: {e}")

    return resultado

async def extrair_fotos_maps_fallback(page, pasta_assets, max_fotos=4):
    """Fallback: se o Instagram não tiver fotos, extrai as fotos do Google Maps."""
    os.makedirs(pasta_assets, exist_ok=True)
    fotos_salvas = []
    try:
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

        count = 0
        for idx, img_url in enumerate(unique_urls):
            if count >= max_fotos:
                break
            high_res = re.sub(r'=w\d+-h\d+.*$', '=w1200-h800-k-no', img_url)
            if '=w' not in high_res:
                high_res += '=w1200-h800-k-no'
            filename = f"maps-foto-{count+1}.jpg"
            dest = os.path.join(pasta_assets, filename)
            try:
                req = urllib.request.Request(high_res, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=10) as resp, open(dest, "wb") as f:
                    f.write(resp.read())
                if os.path.getsize(dest) > 15000:
                    fotos_salvas.append(filename)
                    count += 1
                else:
                    if os.path.exists(dest):
                        os.remove(dest)
            except Exception:
                pass
        if fotos_salvas:
            print(f"  [+] Fallback Maps: {len(fotos_salvas)} fotos salvas do Google Maps.")
    except Exception as e:
        print(f"  [-] Erro no fallback de fotos Maps: {e}")
    return fotos_salvas

async def minerar(nicho, cidade, limite=5, apenas_sem_site=True, visible=False):
    print("=" * 65)
    print(f"🚀 AHOLIC DIGITAL — MINERADOR UNIFICADO DE LEADS")
    print(f"🎯 Nicho: {nicho.upper()} | 📍 Cidade: {cidade.title()} | 🎯 Meta: {limite} leads")
    print(f"🛡️  Filtro: {'Apenas negócios SEM SITE (Modo Do Zero)' if apenas_sem_site else 'Sem site e Sites ruins'}")
    print("=" * 65)

    has_ig_session = os.path.exists(SESSION_FILE)
    if has_ig_session:
        print("[*] Sessão do Instagram autenticada carregada com sucesso.")
    else:
        print("[!] Nenhuma sessão do Instagram em config/instagram_session.json. Rodando modo anônimo.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not visible)
        
        # Contexto para o Google Maps
        context_maps = await browser.new_context(
            user_agent=HEADERS["User-Agent"],
            locale="pt-BR",
            viewport={"width": 1366, "height": 850}
        )
        page_maps = await context_maps.new_page()

        # Contexto para o Instagram (com cookies se disponível)
        ig_context_kwargs = {
            "user_agent": HEADERS["User-Agent"],
            "locale": "pt-BR",
            "viewport": {"width": 1280, "height": 900}
        }
        if has_ig_session:
            ig_context_kwargs["storage_state"] = SESSION_FILE
        context_ig = await browser.new_context(**ig_context_kwargs)
        page_ig = await context_ig.new_page()

        # 1. Busca no Google Maps
        termo_busca = f"{nicho} em {cidade}"
        maps_url = f"https://www.google.com/maps/search/{urllib.parse.quote(termo_busca)}"
        print(f"\n[*] Acessando Google Maps: {termo_busca}...")
        await page_maps.goto(maps_url, wait_until="domcontentloaded", timeout=40000)
        await page_maps.wait_for_timeout(4000)

        # Tratar botões de consentimento
        try:
            btn_consent = await page_maps.query_selector('button:has-text("Aceitar tudo"), button:has-text("Concordo")')
            if btn_consent:
                await btn_consent.click()
                await page_maps.wait_for_timeout(2000)
        except Exception:
            pass

        leads_qualificados = 0
        locais_avaliados = set()

        # Rolar painel lateral para carregar cartões
        for ciclo_scroll in range(6):
            if leads_qualificados >= limite:
                break

            # Localizar cards de locais
            cards = await page_maps.query_selector_all('a[href*="/maps/place/"]')
            print(f"[*] {len(cards)} estabelecimentos encontrados na lista...")

            for card in cards:
                if leads_qualificados >= limite:
                    break

                href = await card.get_attribute("href")
                if not href or href in locais_avaliados:
                    continue
                locais_avaliados.add(href)

                try:
                    await card.scroll_into_view_if_needed()
                    await card.click()
                    await page_maps.wait_for_timeout(3000)
                except Exception:
                    continue

                # Extrair detalhes do card ativo
                detalhes = await page_maps.evaluate('''() => {
                    // Nome
                    const h1 = document.querySelector('h1.fontHeadlineLarge, h1, div.lMbq3e h1');
                    const nome = h1 ? h1.innerText.trim() : '';

                    // Nota
                    const notaEl = document.querySelector('span.fontDisplayLarge, div.F7nice span[aria-hidden="true"]');
                    const nota = notaEl ? parseFloat(notaEl.innerText.replace(',', '.')) : null;

                    // Avaliações
                    let avaliacoes = null;
                    const avalEl = document.querySelector('div.F7nice span:last-child, span[aria-label*="avaliações"]');
                    if (avalEl) {
                        const m = avalEl.innerText.match(/\\(?([0-9.]+)\\)?/);
                        if (m) avaliacoes = parseInt(m[1].replace('.', ''));
                    }

                    // Categoria
                    const catEl = document.querySelector('button.DkEaL, button[jsaction*="category"]');
                    const categoria = catEl ? catEl.innerText.trim() : '';

                    // Website
                    const siteEl = document.querySelector('a[data-tooltip*="site" i], a[data-item-id*="authority"], a[aria-label*="website" i]');
                    const siteUrl = siteEl ? siteEl.href : '';

                    // Telefone
                    const telEl = document.querySelector('button[data-tooltip*="telefone" i], button[data-item-id*="phone"]');
                    const telefone = telEl ? telEl.innerText.trim() : '';

                    // Endereço
                    const endEl = document.querySelector('button[data-item-id*="address"]');
                    const endereco = endEl ? endEl.innerText.trim() : '';

                    return { nome, nota, avaliacoes, categoria, siteUrl, telefone, endereco };
                }''')

                nome = detalhes.get("nome")
                if not nome or len(nome) < 3:
                    continue

                site_url = detalhes.get("siteUrl", "").strip()
                descartar_dominios = ['linktr.ee', 'instagram.com', 'facebook.com', 'wa.me', 'api.whatsapp.com', 'bio.link']
                eh_rede_social = any(d in site_url.lower() for d in descartar_dominios)

                # Filtro de Site
                tem_site_proprio = bool(site_url) and not eh_rede_social
                if apenas_sem_site and tem_site_proprio:
                    # Pula quem já tem site
                    continue

                slug = normalizar_slug(nome)
                if lead_ja_existe(slug):
                    print(f"[!] Lead já cadastrado no banco: {nome} (pulando)")
                    continue

                print("-" * 60)
                print(f"🎯 LEAD QUALIFICADO #{leads_qualificados + 1}: {nome}")
                print(f"  ⭐ Avaliação: {detalhes.get('nota')} ({detalhes.get('avaliacoes')} avaliações)")
                print(f"  📞 Telefone: {detalhes.get('telefone') or '(não informado)'}")
                print(f"  🌐 Site Atual: {site_url if site_url else 'Nenhum (100% sem presença web)'}")

                whatsapp = formatar_whatsapp(detalhes.get("telefone", ""))
                tel_formatado = formatar_telefone_br(detalhes.get("telefone", ""))

                # Descoberta do Instagram
                insta_user = None
                if "instagram.com" in site_url.lower():
                    m = re.search(r'instagram\.com/([a-zA-Z0-9_.-]+)', site_url)
                    if m:
                        insta_user = m.group(1).rstrip('/')
                
                if not insta_user:
                    insta_user = await buscar_instagram_por_nome(page_ig, nome, cidade)

                pasta_lead_assets = os.path.join(SITES_DIR, slug, "assets")
                fotos_instagram = []
                logo_insta = None
                bio_insta = ""

                if insta_user:
                    print(f"  📸 Perfil Instagram identificado: @{insta_user}")
                    ig_data = await extrair_assets_instagram(page_ig, insta_user, pasta_lead_assets, max_fotos=6)
                    fotos_instagram = ig_data.get("fotos", [])
                    logo_insta = ig_data.get("logo")
                    bio_insta = ig_data.get("bio", "")

                # Se não conseguiu fotos do Instagram, pega do Google Maps como fallback
                if not fotos_instagram:
                    print("  [*] Buscando fotos reais diretamente no Google Maps...")
                    fotos_maps = await extrair_fotos_maps_fallback(page_maps, pasta_lead_assets, max_fotos=4)
                    fotos_instagram.extend(fotos_maps)

                # Motivo objetivo para proposta
                if not site_url:
                    motivo = "Negócio com excelente nota no Google, mas NÃO POSSUI SITE oficial. Depende 100% de redes sociais e perde buscas locais de pacientes que procuram no Google."
                else:
                    motivo = f"Usa apenas agregador ou link temporário ({site_url}), sem autoridade nem página dedicada de conversão."

                # Metadados de Direção Criativa
                direcao = {
                    "instagram": f"@{insta_user}" if insta_user else None,
                    "bio": bio_insta,
                    "logo": logo_insta,
                    "fotos_reais": fotos_instagram,
                    "categoria": detalhes.get("categoria"),
                    "endereco": detalhes.get("endereco"),
                    "minerado_em": datetime.now().isoformat()
                }

                # Monta dicionário completo do Lead
                lead_data = {
                    "slug": slug,
                    "nome": nome,
                    "nicho": nicho.title(),
                    "cidade": cidade.title(),
                    "nota": detalhes.get("nota") or 5.0,
                    "avaliacoes": detalhes.get("avaliacoes") or 10,
                    "email": None,
                    "telefone": tel_formatado,
                    "whatsapp": whatsapp,
                    "siteAntigo": site_url if site_url else None,
                    "motivo": motivo,
                    "status": "novo",
                    "urlNova": None,
                    "dataProposta": None,
                    "valor": 1500.0,
                    "obs": f"Instagram: @{insta_user}" if insta_user else "Instagram não localizado",
                    "contratoStatus": "pendente",
                    "contratoEm": None,
                    "manutencao": 150.0,
                    "pago": 0,
                    "docCliente": None,
                    "endCliente": detalhes.get("endereco"),
                    "direcaoCriativa": json.dumps(direcao, ensure_ascii=False)
                }

                # Salva no SQLite e no leads.md
                salvar_lead_banco(lead_data)
                atualizar_leads_md(lead_data)
                leads_qualificados += 1
                print(f"  💾 Lead salvo no prospector.db e leads.md com sucesso!")

            # Rola a barra de resultados do Maps para carregar mais estabelecimentos
            try:
                painel_feed = await page_maps.query_selector('div[role="feed"]')
                if painel_feed:
                    await painel_feed.evaluate('el => el.scrollBy(0, 1200)')
                    await page_maps.wait_for_timeout(2500)
            except Exception:
                pass

        await browser.close()

    print("\n" + "=" * 65)
    print(f"✅ MINERAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"📊 Total de novos leads qualificados: {leads_qualificados}")
    print(f"📂 Verifique o dashboard local em http://localhost:8765 ou o arquivo leads.md")
    print("=" * 65 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Minerador Unificado de Leads Aholic")
    parser.add_argument("--nicho", type=str, default="estetica", help="Nicho a pesquisar (ex: estetica, odontologia, arquitetura)")
    parser.add_argument("--cidade", type=str, default="Caldas Novas", help="Cidade a pesquisar (ex: Caldas Novas, Goiania)")
    parser.add_argument("--limite", type=int, default=5, help="Quantidade máxima de leads qualificados a minerar")
    parser.add_argument("--incluir-com-site", action="store_true", help="Se definido, inclui também empresas que já possuem site")
    parser.add_argument("--visible", action="store_true", help="Abre o navegador de forma visível na tela")
    args = parser.parse_args()

    asyncio.run(minerar(
        nicho=args.nicho,
        cidade=args.cidade,
        limite=args.limite,
        apenas_sem_site=not args.incluir_com_site,
        visible=args.visible
    ))

if __name__ == "__main__":
    main()
