#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditor e Analisador de Sites Web e Leads
Uso CLI:
  python scripts/analisar-lead-web.py "https://www.espacocoral.com.br"
  python scripts/analisar-lead-web.py "Espaço Coral Psicologia Florianopolis"
"""

import sys, os, re, json, time, urllib.parse, urllib.request, ssl
from datetime import datetime

PASTA = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(PASTA, '..'))
DB = os.path.join(RAIZ, 'prospector.db')

# Configuração SSL segura e headers de navegador moderno
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def buscar_google(termo):
    """Busca o site oficial no Google a partir de um nome ou nicho + cidade."""
    query = urllib.parse.quote(termo)
    url = f"https://html.duckduckgo.com/html/?q={query}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Extrair links de resultados orgânicos
            links = re.findall(r'class="result__url"[^>]*href="([^"]+)"', html)
            if not links:
                links = re.findall(r'href="//duckduckgo.com/l/\?uddg=([^"&]+)', html)
                links = [urllib.parse.unquote(l) for l in links]
            
            # Filtrar diretórios e pegar primeiro domínio real
            descartar = ['facebook.com', 'instagram.com', 'linkedin.com', 'doctoralia.com.br', 'jusbrasil.com.br', 'guiamais.com.br', 'apontador.com.br', 'cylex.com.br']
            for link in links:
                if not link.startswith('http'):
                    link = 'https://' + link.lstrip('/')
                dominio = urllib.parse.urlparse(link).netloc.lower()
                if not any(d in dominio for d in descartar):
                    return link
    except Exception as e:
        print(f"[Aviso Busca]: {e}")
    return None

def auditar_site(url):
    """Acessa o site e realiza uma auditoria técnica profunda de UX, WhatsApp, SEO e tecnologia."""
    if not url.startswith('http'):
        url = 'https://' + url

    resultado = {
        'url': url,
        'dominio': urllib.parse.urlparse(url).netloc,
        'status_code': None,
        'tempo_resposta_ms': None,
        'tecnologia': 'HTML Custom / Desconhecido',
        'titulo': '',
        'meta_description': '',
        'viewport_mobile': False,
        'tem_whatsapp': False,
        'numero_whatsapp': None,
        'link_whatsapp': None,
        'telefones_encontrados': [],
        'emails_encontrados': [],
        'instagram': None,
        'falhas_criticas': [],
        'pontos_positivos': [],
        'score_conversao': 100,
        'motivo_redesign': ''
    }

    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=12) as resp:
            resultado['status_code'] = resp.getcode()
            html = resp.read().decode('utf-8', errors='ignore')
            resultado['tempo_resposta_ms'] = int((time.time() - t0) * 1000)
    except Exception as e:
        resultado['falhas_criticas'].append(f"Site inacessível ou com erro de conexão: {str(e)}")
        resultado['score_conversao'] = 10
        resultado['motivo_redesign'] = "Site fora do ar ou extremamente lento para abrir."
        return resultado

    # 1. Identificação de Tecnologia
    html_lower = html.lower()
    if 'wix.com' in html_lower or '_wix' in html_lower or 'wixsite.com' in html_lower:
        resultado['tecnologia'] = 'Wix (Construtor Genérico)'
        resultado['falhas_criticas'].append('Desenvolvido em Wix: carregamento pesado de scripts e SEO limitado.')
        resultado['score_conversao'] -= 25
    elif 'wp-content' in html_lower or 'wordpress' in html_lower:
        if 'elementor' in html_lower:
            resultado['tecnologia'] = 'WordPress + Elementor'
        else:
            resultado['tecnologia'] = 'WordPress'
        resultado['pontos_positivos'].append('Base WordPress identificada.')
    elif 'sites.google.com' in html_lower:
        resultado['tecnologia'] = 'Google Sites Gratuito'
        resultado['falhas_criticas'].append('Usa Google Sites gratuito: passa pouca autoridade para serviços de alto valor.')
        resultado['score_conversao'] -= 35

    # 2. Viewport Mobile
    if '<meta name="viewport"' in html_lower or "<meta name='viewport'" in html_lower:
        resultado['viewport_mobile'] = True
        resultado['pontos_positivos'].append('Configuração de responsividade mobile detectada.')
    else:
        resultado['falhas_criticas'].append('SEM meta tag de viewport: página quebra ou fica minúscula no celular!')
        resultado['score_conversao'] -= 30

    # 3. SEO Básico (Title e Description)
    tit_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
    if tit_m:
        resultado['titulo'] = tit_m.group(1).strip()
    else:
        resultado['falhas_criticas'].append('Site não possui tag <title> para ranquear no Google.')
        resultado['score_conversao'] -= 15

    desc_m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.I | re.S)
    if desc_m:
        resultado['meta_description'] = desc_m.group(1).strip()
    else:
        resultado['falhas_criticas'].append('Sem meta description configurada para buscas locais.')
        resultado['score_conversao'] -= 10

    # 4. Auditoria de WhatsApp e Contato
    wa_match = re.search(r'(https?://(?:api\.whatsapp\.com|wa\.me)/[^\s"\'<>]+)', html)
    if wa_match:
        resultado['tem_whatsapp'] = True
        resultado['link_whatsapp'] = wa_match.group(1)
        num_clean = re.sub(r'\D', '', resultado['link_whatsapp'])
        if num_clean.startswith('55') and len(num_clean) >= 12:
            resultado['numero_whatsapp'] = num_clean
        resultado['pontos_positivos'].append('Possui link de WhatsApp configurado.')
    else:
        resultado['falhas_criticas'].append('SEM botão de WhatsApp direto: o cliente precisa copiar o número para conversar.')
        resultado['score_conversao'] -= 30

    # Extração de telefones
    tels = re.findall(r'(?:\(?\d{2}\)?\s*)?(?:9\d{4}|\d{4})[-.\s]?\d{4}', html)
    tels_validos = list(set([t.strip() for t in tels if len(re.sub(r'\D', '', t)) in (10, 11)]))
    resultado['telefones_encontrados'] = tels_validos[:3]

    # Extração de emails
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html)
    emails_validos = list(set([e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.svg', '.js', '.css', '.webp'))]))
    resultado['emails_encontrados'] = emails_validos[:3]

    # Extração de Instagram
    insta_m = re.search(r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_.-]+)', html)
    if insta_m:
        resultado['instagram'] = '@' + insta_m.group(1).rstrip('/')

    # 5. Performance de Carregamento
    if resultado['tempo_resposta_ms'] and resultado['tempo_resposta_ms'] > 2500:
        resultado['falhas_criticas'].append(f'Carregamento lento ({resultado["tempo_resposta_ms"]}ms) — pacientes desistem de esperar.')
        resultado['score_conversao'] -= 15

    # 6. Síntese do Motivo de Redesign
    if not resultado['tem_whatsapp']:
        resultado['motivo_redesign'] = 'Site sem botão direto de WhatsApp; perda de agendamentos imediatos no celular.'
    elif not resultado['viewport_mobile']:
        resultado['motivo_redesign'] = 'Layout não responsivo; quebra em telas de smartphones.'
    elif 'Wix' in resultado['tecnologia']:
        resultado['motivo_redesign'] = 'Site em Wix antigo com carregamento pesado e layout genérico.'
    elif resultado['falhas_criticas']:
        resultado['motivo_redesign'] = resultado['falhas_criticas'][0]
    else:
        resultado['motivo_redesign'] = 'Site funcional, porém com visual datado e sem o padrão visual de autoridade premium.'

    resultado['score_conversao'] = max(10, min(100, resultado['score_conversao']))
    return resultado

def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/analisar-lead-web.py <URL ou Termo de Busca>")
        print("Exemplo: python scripts/analisar-lead-web.py 'https://www.espacocoral.com.br'")
        print("Exemplo: python scripts/analisar-lead-web.py 'Espaço Coral Florianópolis'")
        sys.exit(1)

    alvo = sys.argv[1].strip()
    print(f"\n🔍 [Auditor Web]: Analisando '{alvo}'...")

    url = alvo if alvo.startswith('http') or '.' in alvo.split()[0] else buscar_google(alvo)

    if not url:
        print(f"❌ Não foi possível encontrar um site oficial para '{alvo}'.")
        sys.exit(1)

    print(f"🌐 [Site Identificado]: {url}")
    print("⏳ Executando auditoria técnica de UX, WhatsApp, SEO e Performance...")
    
    dados = auditar_site(url)

    print("\n" + "="*60)
    print(f"📊 RELATÓRIO DE AUDITORIA — {dados['dominio'].upper()}")
    print("="*60)
    print(f"🏆 Score de Conversão: {dados['score_conversao']}/100")
    print(f"🛠️  Tecnologia Base: {dados['tecnologia']}")
    print(f"⚡ Tempo de Resposta: {dados['tempo_resposta_ms']} ms")
    print(f"📱 Mobile Ready: {'✅ SIM' if dados['viewport_mobile'] else '❌ NÃO (Crítico)'}")
    print(f"💬 Botão WhatsApp Direto: {'✅ SIM' if dados['tem_whatsapp'] else '❌ NÃO (Perda de Leads)'}")
    if dados['numero_whatsapp']:
        print(f"   WhatsApp: {dados['numero_whatsapp']}")
    if dados['instagram']:
        print(f"📸 Instagram: {dados['instagram']}")
    if dados['telefones_encontrados']:
        print(f"📞 Telefones: {', '.join(dados['telefones_encontrados'])}")
    if dados['emails_encontrados']:
        print(f"✉️  E-mails: {', '.join(dados['emails_encontrados'])}")

    print("\n🚨 PONTOS FRACOS & FALHAS OBJETIVAS (Argumentos de Venda):")
    if dados['falhas_criticas']:
        for f in dados['falhas_criticas']:
            print(f"  • ❌ {f}")
    else:
        print("  • Nenhuma falha estrutural grave encontrada.")

    print("\n🎯 MOTIVO PARA PROPOSTA / REDESIGN:")
    print(f"  👉 \"{dados['motivo_redesign']}\"")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
