#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHOLIC DIGITAL — Gerador Automático de Sites Anti-Slop
Gera sites de altíssimo padrão visual com transições refinadas, coleta de logo real,
galeria de fotos reais e suporte a presets dinâmicos e modulares.

Uso CLI:
  python scripts/gerar-site-lead.py --list
  python scripts/gerar-site-lead.py --slug "clinica-anielly-vilela" --preset "quiet-luxury"
  python scripts/gerar-site-lead.py --slug "clinica-anielly-vilela" --preset auto
"""

import os
import sys
import json
import re
import glob
import sqlite3
import argparse
import unicodedata
import urllib.parse
from datetime import datetime

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
SITES_DIR = os.path.join(RAIZ, "sites")
TEMPLATES_DIR = os.path.join(RAIZ, "referencias", "templates")
PRESETS_JSON = os.path.join(RAIZ, "referencias", "presets-visuais.json")

# Código do Editor Visual Inline (pe-bar) para [slug]-editor.html
EDITOR_SNIPPET = """
<!-- PROSPECTOR-EDITOR-START -->
<style id="pe-style">
#pe-bar{position:fixed;top:0;left:0;right:0;height:44px;background:#0f172a;color:#f8fafc;display:flex;align-items:center;justify-content:space-between;padding:0 20px;font-family:system-ui,-apple-system,sans-serif;font-size:13px;z-index:999999;box-shadow:0 2px 10px rgba(0,0,0,0.3);border-bottom:1px solid #334155}
#pe-bar strong{color:#38bdf8;font-weight:600}
#pe-bar button{background:#22c55e;color:#fff;border:0;padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;transition:background .2s}
#pe-bar button:hover{background:#16a34a}
body{margin-top:44px !important}
.pe-hover{outline:2px dashed #22c55e !important;outline-offset:2px;cursor:pointer}
[contenteditable="true"]:focus{outline:2px solid #38bdf8 !important;outline-offset:2px}
</style>
<div id="pe-bar">
  <div><strong>✨ Modo Edição Aholic</strong> · Clique em textos para alterar · clique em imagens para trocar</div>
  <button id="pe-export" type="button">Salvar e Exportar Site</button>
</div>
<input type="file" id="pe-file" accept="image/*" style="display:none">
<script id="pe-script">
(function(){
  var TEXT='h1,h2,h3,h4,h5,h6,p,li,a,span,button,td,th,figcaption,blockquote,strong,em';
  document.querySelectorAll(TEXT).forEach(function(el){
    if(el.closest('#pe-bar'))return;
    if(el.children.length===0||el.childElementCount<=1){
      el.addEventListener('click',function(e){
        if(el.tagName==='A'||el.tagName==='BUTTON')e.preventDefault();
        el.setAttribute('contenteditable','true');el.focus();
      });
      el.addEventListener('mouseenter',function(){el.classList.add('pe-hover')});
      el.addEventListener('mouseleave',function(){el.classList.remove('pe-hover')});
      el.addEventListener('blur',function(){el.removeAttribute('contenteditable')});
    }
  });
  var fileInput=document.getElementById('pe-file'),currentImg=null;
  document.querySelectorAll('img').forEach(function(img){
    img.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();currentImg=img;fileInput.click()});
    img.addEventListener('mouseenter',function(){img.classList.add('pe-hover')});
    img.addEventListener('mouseleave',function(){img.classList.remove('pe-hover')});
  });
  fileInput.addEventListener('change',function(){
    var f=fileInput.files[0];if(!f||!currentImg)return;
    var r=new FileReader();
    r.onload=function(){currentImg.src=r.result;if(currentImg.srcset)currentImg.removeAttribute('srcset')};
    r.readAsDataURL(f);fileInput.value='';
  });
  document.getElementById('pe-export').addEventListener('click',function(){
    var doc=document.documentElement.cloneNode(true);
    ['#pe-bar','#pe-style','#pe-script','#pe-file'].forEach(function(s){var n=doc.querySelector(s);if(n)n.remove()});
    doc.querySelectorAll('[contenteditable]').forEach(function(n){n.removeAttribute('contenteditable')});
    doc.querySelectorAll('.pe-hover').forEach(function(n){n.classList.remove('pe-hover')});
    var html='<!DOCTYPE html>\\n'+doc.outerHTML;
    var blob=new Blob([html],{type:'text/html'});
    var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='index.html';a.click();
  });
})();
</script>
<!-- PROSPECTOR-EDITOR-END -->
"""

# Script de Animações de Revelação e Transições Fluidas
ANIMATION_SCRIPT = """
<script>
// Transições e animações fluidas de scroll (IntersectionObserver)
document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el));
    if (window.lucide) { lucide.createIcons(); }
});
</script>
"""

def conectar_banco():
    return sqlite3.connect(DB_PATH)

def buscar_lead(slug):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""SELECT slug, nome, nicho, cidade, nota, avaliacoes, email, telefone, whatsapp, 
                             siteAntigo, motivo, status, direcaoCriativa, obs, endCliente 
                      FROM leads WHERE slug = ?""", (slug,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    campos = ['slug', 'nome', 'nicho', 'cidade', 'nota', 'avaliacoes', 'email', 'telefone', 'whatsapp', 
              'siteAntigo', 'motivo', 'status', 'direcaoCriativa', 'obs', 'endCliente']
    return dict(zip(campos, row))

def listar_leads():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT slug, nome, nicho, cidade, status FROM leads ORDER BY rowid DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def atualizar_status_lead(slug, url_site):
    conn = conectar_banco()
    conn.execute("UPDATE leads SET status = 'redesenhado', urlNova = ?, atualizado = datetime('now','localtime') WHERE slug = ?", (url_site, slug))
    conn.commit()
    conn.close()

def detectar_assets_lead(slug):
    """Encontra logo oficial e fotos reais baixadas do Instagram ou Google Maps."""
    pasta_assets = os.path.join(SITES_DIR, slug, "assets")
    logo = None
    fotos = []

    if os.path.exists(pasta_assets):
        # 1. Busca de Logo
        possiveis_logos = ["instagram-logo.jpg", "logo.png", "logo.jpg", "logo.svg", "avatar.jpg", "instagram-avatar.jpg"]
        for nome_logo in possiveis_logos:
            caminho = os.path.join(pasta_assets, nome_logo)
            if os.path.exists(caminho) and os.path.getsize(caminho) > 1000:
                logo = f"assets/{nome_logo}"
                break

        # 2. Busca de Fotos do Feed e Maps
        exts = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
        todos_arquivos = []
        for ext in exts:
            todos_arquivos.extend(glob.glob(os.path.join(pasta_assets, ext)))
        
        # Filtra e ordena
        for arq in todos_arquivos:
            nome_arq = os.path.basename(arq)
            if "logo" in nome_arq.lower() or "avatar" in nome_arq.lower() or "preview" in nome_arq.lower():
                continue
            if os.path.getsize(arq) > 12000: # Valida imagem válida
                fotos.append(f"assets/{nome_arq}")

    return logo, fotos

def gerar_iniciais(nome):
    partes = [p for p in nome.split() if len(p) > 2 and p.lower() not in ['dra.', 'dr.', 'clinica', 'instituto', 'studio', 'centro', 'espaco', 'de', 'da', 'do', 'e']]
    if len(partes) >= 2:
        return (partes[0][0] + partes[1][0]).upper()
    elif len(partes) == 1:
        return partes[0][:2].upper()
    return "AH"

def escolher_preset_auto(nicho):
    n = (nicho or "").lower()
    if any(k in n for k in ['estet', 'dermato', 'cirurg', 'facial', 'laser', 'beleza']):
        return "quiet-luxury"
    elif any(k in n for k in ['odont', 'dent', 'implante', 'sorriso', 'facial']):
        return "swiss-precision"
    elif any(k in n for k in ['psico', 'terap', 'mente', 'bem-estar', 'spa', 'nutri', 'acolh']):
        return "warm-organic"
    elif any(k in n for k in ['arquit', 'interio', 'engenh', 'decor', 'obras']):
        return "monografia-editorial"
    elif any(k in n for k in ['cinema', 'futur', 'spatial', 'tech', 'digital']):
        return "cinema-3d-spatial"
    return "quiet-luxury"

# ==============================================================================
# MOTORES DE PRESETS COM TRANSIÇÕES E DESIGN ANTI-SLOP
# ==============================================================================

def renderizar_quiet_luxury(lead, logo_path, fotos):
    """Arquétipo: Quiet Luxury / Editorial Sofisticado (Estética, Dermatologia, Cirurgia Plástica)."""
    nome = lead.get('nome', 'Clínica Especializada')
    cidade = lead.get('cidade', 'Brasil')
    nicho = lead.get('nicho', 'Estética Avançada')
    whatsapp = lead.get('whatsapp') or "5564999999999"
    telefone = lead.get('telefone') or "(64) 99999-9999"
    endereco = lead.get('endCliente') or f"{cidade} — Atendimento com hora marcada"
    nota = lead.get('nota') or 5.0
    avaliacoes = lead.get('avaliacoes') or 35
    iniciais = gerar_iniciais(nome)
    
    wa_msg = urllib.parse.quote(f"Olá! Conheci a {nome} através do site e gostaria de agendar uma avaliação.")
    wa_link = f"https://wa.me/{whatsapp}?text={wa_msg}"

    # Logo HTML
    if logo_path:
        logo_html = f'<img src="{logo_path}" alt="{nome}" class="w-11 h-11 rounded-full object-cover border border-[#E2D6CA] shadow-sm group-hover:scale-105 transition-transform duration-300">'
    else:
        logo_html = f'<div class="w-11 h-11 rounded-full bg-[#EFE8E1] border border-[#E2D6CA] flex items-center justify-center text-[#845749] font-serif font-semibold text-base shadow-sm">{iniciais}</div>'

    # Fotos reais para hero e galeria
    hero_img = fotos[0] if len(fotos) > 0 else "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1200&q=80"
    especialista_img = fotos[1] if len(fotos) > 1 else hero_img
    
    galeria_html = ""
    fotos_grid = fotos[2:6] if len(fotos) >= 6 else (fotos if fotos else [hero_img])
    for f in fotos_grid:
        galeria_html += f"""
        <div class="group relative overflow-hidden rounded-md bg-[#EFE8E1] shadow-sm aspect-[4/5] cursor-pointer">
            <img src="{f}" alt="Procedimento e Ambiente" class="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105">
            <div class="absolute inset-0 bg-gradient-to-t from-[#1F1D1B]/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                <span class="text-xs font-serif text-white tracking-wider">Acabamento Natural & Exclusivo</span>
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nome} | {nicho} — {cidade}</title>
    <meta name="description" content="{nome} — Atendimento exclusivo de {nicho} em {cidade}. Agendamento com hora marcada e tecnologia de alta performance.">
    
    <!-- Google Fonts: Newsreader (Editorial Serif) + Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap" rel="stylesheet">
    
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        nude: {{
                            50: '#FDFBF9', 100: '#F9F5F1', 200: '#EFE8E1', 300: '#E2D6CA',
                            400: '#CDBBB0', 500: '#B29B8E', 600: '#947D70', 700: '#756054',
                            800: '#57463D', 900: '#382D27'
                        }},
                        rosewood: {{ 500: '#9D6E5F', 600: '#845749' }}
                    }},
                    fontFamily: {{
                        sans: ['"Inter"', 'sans-serif'],
                        serif: ['"Newsreader"', 'Georgia', 'serif']
                    }}
                }}
            }}
        }}
    </script>
    <style>
        ::selection {{ background: #EFE8E1; color: #1F1D1B; }}
        .reveal-on-scroll {{
            opacity: 0;
            transform: translateY(24px);
            transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .reveal-on-scroll.is-visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        .wa-float {{
            position: fixed;
            bottom: 28px;
            right: 28px;
            z-index: 50;
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .wa-float:hover {{
            transform: translateY(-4px) scale(1.04);
        }}
    </style>
</head>
<body class="bg-[#FDFBF9] text-[#1F1D1B] font-sans antialiased">

    <!-- Top Utility Bar -->
    <div class="border-b border-nude-200 bg-nude-100/70 text-xs text-nude-700 py-2.5 px-4">
        <div class="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-2">
            <div class="flex items-center gap-2.5">
                <span class="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
                <span>Atendimento Exclusivo &bull; {cidade} &bull; Protocolos Personalizados</span>
            </div>
            <div class="flex items-center gap-4 text-nude-800 text-xs">
                <span>{endereco}</span>
                <span class="text-nude-300">|</span>
                <a href="{wa_link}" target="_blank" class="font-medium hover:text-black transition-colors">{telefone}</a>
            </div>
        </div>
    </div>

    <!-- Header / Navbar -->
    <header class="sticky top-0 z-40 bg-[#FDFBF9]/90 backdrop-blur-md border-b border-nude-200">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 h-20 flex items-center justify-between">
            <a href="#" class="flex items-center gap-3.5 group">
                {logo_html}
                <div class="flex flex-col">
                    <span class="font-serif text-xl font-medium tracking-tight text-neutral-950">{nome}</span>
                    <span class="text-[10px] tracking-[0.2em] uppercase text-nude-600 font-medium">{nicho}</span>
                </div>
            </a>

            <nav class="hidden md:flex items-center gap-8 text-xs uppercase tracking-widest font-medium text-neutral-600">
                <a href="#procedimentos" class="hover:text-black transition-colors">Tratamentos</a>
                <a href="#galeria" class="hover:text-black transition-colors">Galeria Real</a>
                <a href="#sobre" class="hover:text-black transition-colors">A Clínica</a>
                <a href="#depoimentos" class="hover:text-black transition-colors">Avaliações</a>
                <a href="#localizacao" class="hover:text-black transition-colors">Localização</a>
            </nav>

            <a href="{wa_link}" target="_blank" 
               class="inline-flex items-center gap-2 bg-[#1F1D1B] hover:bg-neutral-800 text-white text-xs font-medium px-5 py-2.5 rounded-sm tracking-wide transition-all shadow-sm hover:shadow-md">
                <span>Agendar Consulta</span>
                <i data-lucide="arrow-up-right" class="w-3.5 h-3.5 text-nude-300"></i>
            </a>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="relative pt-12 pb-20 md:pt-20 md:pb-28 border-b border-nude-200 overflow-hidden">
        <div class="max-w-6xl mx-auto px-4 sm:px-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
                <div class="lg:col-span-7 space-y-6 reveal-on-scroll">
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-nude-200/80 border border-nude-300 text-xs text-rosewood-600 font-medium">
                        <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
                        <span>Medicina Estética & Tecnologia Avançada</span>
                    </div>
                    <h1 class="font-serif text-4xl sm:text-5xl lg:text-6xl text-neutral-950 font-normal leading-[1.1] tracking-tight">
                        Realce sua beleza natural com <span class="italic font-normal text-rosewood-600">precisão e sofisticação</span>.
                    </h1>
                    <p class="text-base text-neutral-600 font-light max-w-xl leading-relaxed">
                        Procedimentos autorais com foco em harmonia, rejuvenescimento e bem-estar. Planos de tratamento personalizados em um ambiente privativo e acolhedor em {cidade}.
                    </p>
                    <div class="pt-2 flex flex-col sm:flex-row gap-4">
                        <a href="{wa_link}" target="_blank" 
                           class="inline-flex items-center justify-center gap-2.5 bg-[#1F1D1B] hover:bg-neutral-800 text-white text-sm font-medium px-7 py-3.5 rounded-sm tracking-wide transition-all shadow-md hover:shadow-lg">
                            <span>Agendar Avaliação Privativa</span>
                            <i data-lucide="calendar" class="w-4 h-4 text-nude-300"></i>
                        </a>
                        <a href="#procedimentos" 
                           class="inline-flex items-center justify-center gap-2 border border-nude-300 hover:bg-nude-200/50 text-neutral-800 text-sm font-medium px-6 py-3.5 rounded-sm transition-colors">
                            <span>Conhecer Tratamentos</span>
                        </a>
                    </div>
                    <div class="pt-6 flex items-center gap-8 border-t border-nude-200 text-xs text-neutral-600">
                        <div>
                            <span class="block font-serif text-2xl font-semibold text-neutral-900">{nota} ★</span>
                            <span class="text-neutral-500">Google Avaliações ({avaliacoes} opiniões)</span>
                        </div>
                        <div class="w-px h-8 bg-nude-300"></div>
                        <div>
                            <span class="block font-serif text-2xl font-semibold text-neutral-900">100%</span>
                            <span class="text-neutral-500">Atendimento Individualizado</span>
                        </div>
                    </div>
                </div>
                <div class="lg:col-span-5 reveal-on-scroll">
                    <div class="relative">
                        <div class="aspect-[3/4] rounded-md overflow-hidden shadow-2xl bg-nude-200 border-4 border-white">
                            <img src="{hero_img}" alt="{nome}" class="w-full h-full object-cover hover:scale-105 transition-transform duration-700 ease-out">
                        </div>
                        <div class="absolute -bottom-6 -left-6 bg-white/95 backdrop-blur-md p-5 rounded-md border border-nude-200 shadow-xl max-w-xs">
                            <p class="text-xs font-serif italic text-neutral-900">"Cada traço é único. Nossa missão é valorizar a sua essência com elegância."</p>
                            <span class="block mt-2 text-[10px] tracking-wider uppercase text-rosewood-600 font-semibold">{nome}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Galeria com Fotos Reais do Feed -->
    <section id="galeria" class="py-20 bg-nude-100/50 border-b border-nude-200">
        <div class="max-w-6xl mx-auto px-4 sm:px-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 gap-4 reveal-on-scroll">
                <div>
                    <span class="text-xs uppercase tracking-widest font-semibold text-rosewood-600">Resultados & Atmosfera</span>
                    <h2 class="font-serif text-3xl sm:text-4xl text-neutral-950 font-normal mt-1">Galeria de Atendimentos Reais</h2>
                </div>
                <a href="{wa_link}" target="_blank" class="inline-flex items-center gap-1.5 text-xs uppercase tracking-wider font-semibold text-neutral-900 hover:text-rosewood-600 transition-colors">
                    <span>Falar no WhatsApp</span>
                    <i data-lucide="arrow-right" class="w-4 h-4"></i>
                </a>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 reveal-on-scroll">
                {galeria_html}
            </div>
        </div>
    </section>

    <!-- Procedimentos Exclusivos -->
    <section id="procedimentos" class="py-20 border-b border-nude-200">
        <div class="max-w-6xl mx-auto px-4 sm:px-6">
            <div class="text-center max-w-2xl mx-auto mb-16 reveal-on-scroll">
                <span class="text-xs uppercase tracking-widest font-semibold text-rosewood-600">Especialidades</span>
                <h2 class="font-serif text-3xl sm:text-4xl text-neutral-950 font-normal mt-1">Protocolos de Alta Performance</h2>
                <p class="text-sm text-neutral-600 font-light mt-3">Tecnologias consagradas mundialmente para estimular colágeno, reposicionar tecidos e revitalizar a derme.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="p-8 bg-white border border-nude-200 rounded-sm hover:-translate-y-1.5 hover:shadow-xl transition-all duration-300 reveal-on-scroll">
                    <span class="text-xs font-serif italic text-rosewood-600">01 / Rejuvenescimento</span>
                    <h3 class="font-serif text-2xl text-neutral-950 mt-2 mb-3">Ultraformer III & Efeito Lifting</h3>
                    <p class="text-xs text-neutral-600 leading-relaxed font-light mb-6">Ultrassom micro e macrofocado que combate flacidez facial e corporal sem cirurgia, estimulando colágeno profundo.</p>
                    <a href="{wa_link}" target="_blank" class="text-xs font-medium text-neutral-950 inline-flex items-center gap-1 hover:text-rosewood-600 transition-colors">
                        <span>Consultar Disponibilidade</span>
                        <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
                    </a>
                </div>
                <div class="p-8 bg-white border border-nude-200 rounded-sm hover:-translate-y-1.5 hover:shadow-xl transition-all duration-300 reveal-on-scroll">
                    <span class="text-xs font-serif italic text-rosewood-600">02 / Estruturação</span>
                    <h3 class="font-serif text-2xl text-neutral-950 mt-2 mb-3">Harmonização Facial Natural</h3>
                    <p class="text-xs text-neutral-600 leading-relaxed font-light mb-6">Preenchimento com ácido hialurônico focado em pontos de sustentação, contorno mandibular e labial equilibrado.</p>
                    <a href="{wa_link}" target="_blank" class="text-xs font-medium text-neutral-950 inline-flex items-center gap-1 hover:text-rosewood-600 transition-colors">
                        <span>Consultar Disponibilidade</span>
                        <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
                    </a>
                </div>
                <div class="p-8 bg-white border border-nude-200 rounded-sm hover:-translate-y-1.5 hover:shadow-xl transition-all duration-300 reveal-on-scroll">
                    <span class="text-xs font-serif italic text-rosewood-600">03 / Estímulo</span>
                    <h3 class="font-serif text-2xl text-neutral-950 mt-2 mb-3">Bioestimuladores de Colágeno</h3>
                    <p class="text-xs text-neutral-600 leading-relaxed font-light mb-6">Restauração da firmeza e densidade cutânea com produtos biocompatíveis de longa duração e viço imediato.</p>
                    <a href="{wa_link}" target="_blank" class="text-xs font-medium text-neutral-950 inline-flex items-center gap-1 hover:text-rosewood-600 transition-colors">
                        <span>Consultar Disponibilidade</span>
                        <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
                    </a>
                </div>
            </div>
        </div>
    </section>

    <!-- Floating WhatsApp CTA -->
    <div class="wa-float">
        <a href="{wa_link}" target="_blank" 
           class="flex items-center gap-3 bg-[#25D366] hover:bg-[#20bd5a] text-white px-5 py-3.5 rounded-full shadow-2xl transition-all">
            <i data-lucide="message-circle" class="w-5 h-5 fill-current"></i>
            <span class="text-xs font-semibold tracking-wide">Agendar no WhatsApp</span>
        </a>
    </div>

    <!-- Footer -->
    <footer id="localizacao" class="bg-[#1F1D1B] text-white py-16 text-xs">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 grid grid-cols-1 md:grid-cols-3 gap-12">
            <div class="space-y-4">
                <div class="flex items-center gap-3">
                    {logo_html}
                    <span class="font-serif text-xl font-medium tracking-tight text-white">{nome}</span>
                </div>
                <p class="text-neutral-400 font-light leading-relaxed">
                    Compromisso com o requinte, segurança médica e naturalidade estética em {cidade}.
                </p>
            </div>
            <div class="space-y-2">
                <span class="text-[10px] tracking-widest uppercase text-nude-400 font-semibold block mb-2">Localização & Contato</span>
                <p class="text-neutral-300 font-light">{endereco}</p>
                <p class="text-neutral-300 font-light">WhatsApp: {telefone}</p>
            </div>
            <div class="space-y-2">
                <span class="text-[10px] tracking-widest uppercase text-nude-400 font-semibold block mb-2">Horário de Funcionamento</span>
                <p class="text-neutral-300 font-light">Segunda a Sexta: 08h às 19h</p>
                <p class="text-neutral-300 font-light">Sábados: Atendimento agendado</p>
            </div>
        </div>
        <div class="max-w-6xl mx-auto px-4 sm:px-6 pt-12 mt-12 border-t border-neutral-800 flex flex-col sm:flex-row justify-between items-center gap-4 text-neutral-500">
            <span>&copy; {datetime.now().year} {nome}. Todos os direitos reservados.</span>
            <span>Design por <strong class="text-neutral-400">AHOLIC STUDIO</strong></span>
        </div>
    </footer>

    {ANIMATION_SCRIPT}
</body>
</html>
"""

def renderizar_swiss_precision(lead, logo_path, fotos):
    """Arquétipo: Swiss Precision / High-Tech Cirúrgico (Odontologia, Implantes, Alta Tecnologia)."""
    nome = lead.get('nome', 'Clínica Odontológica')
    cidade = lead.get('cidade', 'Brasil')
    nicho = lead.get('nicho', 'Odontologia Avançada')
    whatsapp = lead.get('whatsapp') or "5564999999999"
    telefone = lead.get('telefone') or "(64) 99999-9999"
    endereco = lead.get('endCliente') or f"{cidade} — Centro Clínico Integrado"
    nota = lead.get('nota') or 5.0
    avaliacoes = lead.get('avaliacoes') or 40
    iniciais = gerar_iniciais(nome)

    wa_msg = urllib.parse.quote(f"Olá! Gostaria de agendar uma consulta de avaliação na {nome}.")
    wa_link = f"https://wa.me/{whatsapp}?text={wa_msg}"

    if logo_path:
        logo_html = f'<img src="{logo_path}" alt="{nome}" class="h-10 w-auto max-h-11 rounded-md object-contain border border-slate-200 shadow-sm">'
    else:
        logo_html = f'<div class="w-10 h-10 rounded-md bg-[#0F172A] text-white flex items-center justify-center font-mono font-bold text-sm">{iniciais}</div>'

    hero_img = fotos[0] if len(fotos) > 0 else "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=1200&q=80"
    
    galeria_html = ""
    fotos_grid = fotos[1:5] if len(fotos) >= 5 else (fotos if fotos else [hero_img])
    for f in fotos_grid:
        galeria_html += f"""
        <div class="group relative overflow-hidden rounded-lg bg-slate-100 border border-slate-200 shadow-sm aspect-[4/3]">
            <img src="{f}" alt="Estrutura e Casos Clínicos" class="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105">
            <div class="absolute inset-0 bg-slate-950/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                <span class="text-xs font-mono text-white">Precisão Digital e Conforto</span>
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nome} | {nicho} — {cidade}</title>
    <meta name="description" content="{nome} — Centro de referência em {nicho} em {cidade}. Implantes guiados, reabilitação oral e precisão clínica.">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    
    <style>
        .reveal-on-scroll {{
            opacity: 0;
            transform: translateY(24px);
            transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .reveal-on-scroll.is-visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        .wa-float {{
            position: fixed; bottom: 28px; right: 28px; z-index: 50;
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .wa-float:hover {{ transform: translateY(-4px) scale(1.04); }}
    </style>
</head>
<body class="bg-white text-slate-900 font-sans antialiased">

    <!-- Top Technical Bar -->
    <div class="bg-slate-950 text-slate-300 text-xs py-2 px-4 border-b border-slate-800">
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-2">
            <div class="flex items-center gap-2 font-mono text-[11px]">
                <span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
                <span>TECNOLOGIA DIGITAL &bull; DIAGNÓSTICO GUIADO 3D &bull; {cidade}</span>
            </div>
            <div class="flex items-center gap-4 text-slate-400 text-xs">
                <span>{endereco}</span>
                <span class="text-slate-700">|</span>
                <a href="{wa_link}" target="_blank" class="text-cyan-400 hover:text-white transition-colors">{telefone}</a>
            </div>
        </div>
    </div>

    <!-- Header -->
    <header class="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 h-20 flex items-center justify-between">
            <a href="#" class="flex items-center gap-3.5 group">
                {logo_html}
                <div class="flex flex-col">
                    <span class="text-lg font-bold tracking-tight text-slate-950">{nome}</span>
                    <span class="text-[10px] tracking-wider uppercase font-mono text-cyan-700 font-semibold">{nicho}</span>
                </div>
            </a>

            <nav class="hidden md:flex items-center gap-8 text-xs uppercase tracking-wider font-semibold text-slate-600">
                <a href="#especialidades" class="hover:text-cyan-600 transition-colors">Especialidades</a>
                <a href="#estrutura" class="hover:text-cyan-600 transition-colors">Estrutura</a>
                <a href="#avaliacoes" class="hover:text-cyan-600 transition-colors">Avaliações</a>
                <a href="#contato" class="hover:text-cyan-600 transition-colors">Contato</a>
            </nav>

            <a href="{wa_link}" target="_blank" 
               class="inline-flex items-center gap-2 bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold px-5 py-2.5 rounded-md tracking-wide transition-all shadow-sm">
                <span>Agendar Avaliação</span>
                <i data-lucide="arrow-up-right" class="w-4 h-4"></i>
            </a>
        </div>
    </header>

    <!-- Hero -->
    <section class="py-16 md:py-24 bg-slate-50 border-b border-slate-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
                <div class="lg:col-span-7 space-y-6 reveal-on-scroll">
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded bg-cyan-100 text-cyan-800 text-xs font-mono font-medium">
                        <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
                        <span>Excelência e Biossegurança Rígida</span>
                    </div>
                    <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-950 tracking-tight leading-[1.1]">
                        Precisão milimétrica para o seu <span class="text-[#0284C7]">novo sorriso</span>.
                    </h1>
                    <p class="text-base text-slate-600 max-w-xl font-normal leading-relaxed">
                        Reabilitação oral de alta complexidade com planejamento 100% digital, lentes em cerâmica pura e implantes guiados sem dor.
                    </p>
                    <div class="pt-2 flex flex-col sm:flex-row gap-4">
                        <a href="{wa_link}" target="_blank" 
                           class="inline-flex items-center justify-center gap-2 bg-[#0284C7] hover:bg-[#0369A1] text-white text-sm font-semibold px-7 py-3.5 rounded-md transition-all shadow-md">
                            <span>Agendar Consulta Diagnóstica</span>
                            <i data-lucide="calendar" class="w-4 h-4"></i>
                        </a>
                        <a href="#especialidades" 
                           class="inline-flex items-center justify-center gap-2 border border-slate-300 hover:bg-white text-slate-800 text-sm font-medium px-6 py-3.5 rounded-md transition-colors">
                            <span>Ver Procedimentos</span>
                        </a>
                    </div>
                </div>
                <div class="lg:col-span-5 reveal-on-scroll">
                    <div class="aspect-[4/3] rounded-xl overflow-hidden shadow-2xl border border-slate-200 bg-white">
                        <img src="{hero_img}" alt="{nome}" class="w-full h-full object-cover hover:scale-105 transition-transform duration-700">
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Galeria -->
    <section id="estrutura" class="py-20 border-b border-slate-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6">
            <div class="mb-12 reveal-on-scroll">
                <span class="text-xs uppercase font-mono text-cyan-600 font-bold tracking-wider">Instalações & Tecnologia</span>
                <h2 class="text-3xl font-bold text-slate-950 mt-1">Nossa Estrutura Clínica em {cidade}</h2>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-6 reveal-on-scroll">
                {galeria_html}
            </div>
        </div>
    </section>

    <!-- Floating WhatsApp -->
    <div class="wa-float">
        <a href="{wa_link}" target="_blank" class="flex items-center gap-2.5 bg-[#25D366] hover:bg-[#20bd5a] text-white px-5 py-3 rounded-full shadow-2xl transition-all">
            <i data-lucide="message-circle" class="w-5 h-5 fill-current"></i>
            <span class="text-xs font-bold">Falar no WhatsApp</span>
        </a>
    </div>

    <!-- Footer -->
    <footer id="contato" class="bg-slate-950 text-white py-12 text-xs">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row justify-between items-center gap-6">
            <div>
                <span class="text-base font-bold text-white block">{nome}</span>
                <span class="text-slate-400 font-mono text-[11px]">{endereco} &bull; {telefone}</span>
            </div>
            <div class="text-slate-500">
                &copy; {datetime.now().year} {nome}. Desenvolvido por <strong>AHOLIC STUDIO</strong>
            </div>
        </div>
    </footer>

    {ANIMATION_SCRIPT}
</body>
</html>
"""

def compilar_site(slug, preset_id="auto"):
    lead = buscar_lead(slug)
    if not lead:
        print(f"[-] Erro: Lead com slug '{slug}' não encontrado no banco prospector.db.")
        return False

    pasta_lead = os.path.join(SITES_DIR, slug)
    os.makedirs(pasta_lead, exist_ok=True)
    
    logo_path, fotos = detectar_assets_lead(slug)
    print(f"[*] Compilando site para: {lead['nome']} ({slug})")
    print(f"  • Logo identificado: {logo_path if logo_path else '(monograma autoral gerado)'}")
    print(f"  • Fotos reais disponíveis: {len(fotos)}")

    # Seleção de preset
    if preset_id == "auto" or not preset_id:
        preset_id = escolher_preset_auto(lead.get('nicho'))
    
    print(f"  • Preset visual selecionado: {preset_id}")

    # Renderiza HTML de acordo com o preset
    if preset_id in ["quiet-luxury", "estetica-luxo", "editorial-atelier"]:
        html_puro = renderizar_quiet_luxury(lead, logo_path, fotos)
    elif preset_id in ["swiss-precision", "odonto-tech", "swiss-tech"]:
        html_puro = renderizar_swiss_precision(lead, logo_path, fotos)
    else:
        # Fallback padrão
        html_puro = renderizar_quiet_luxury(lead, logo_path, fotos)

    # 1. Gera o arquivo final limpo: index.html
    caminho_index = os.path.join(pasta_lead, "index.html")
    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(html_puro)
    print(f"[+] Versão final de produção salva em: {caminho_index}")

    # 2. Gera a versão com Editor Inline embutido: [slug]-editor.html
    html_editor = html_puro.replace("</body>", f"{EDITOR_SNIPPET}\n</body>")
    caminho_editor = os.path.join(pasta_lead, f"{slug}-editor.html")
    with open(caminho_editor, "w", encoding="utf-8") as f:
        f.write(html_editor)
    print(f"[+] Versão com editor visual salva em: {caminho_editor}")

    # 3. Atualiza banco SQLite para 'redesenhado'
    url_relativa = f"sites/{slug}/index.html"
    atualizar_status_lead(slug, url_relativa)
    print(f"[+] Status do lead atualizado para 'redesenhado' no prospector.db!")

    return True

def main():
    parser = argparse.ArgumentParser(description="Gerador Automático de Sites Anti-Slop Aholic")
    parser.add_argument("--slug", type=str, help="Slug do lead a gerar (ex: clinica-anielly-vilela)")
    parser.add_argument("--preset", type=str, default="auto", help="Preset visual (ex: quiet-luxury, swiss-precision, warm-organic, auto)")
    parser.add_argument("--list", action="store_true", help="Lista os leads cadastrados no banco")
    args = parser.parse_args()

    if args.list:
        leads = listar_leads()
        print("\n" + "="*65)
        print(f"📋 LEADS CADASTRADOS NO PROSPECTOR ({len(leads)} encontrados)")
        print("="*65)
        for idx, l in enumerate(leads, 1):
            print(f"{idx:2d}. [{l[4].upper():12s}] {l[1]} ({l[0]}) — Nicho: {l[2] or 'Geral'}")
        print("="*65 + "\n")
        return

    if not args.slug:
        print("[-] Especifique um slug com --slug <nome> ou use --list para ver os disponíveis.")
        sys.exit(1)

    compilar_site(args.slug, args.preset)

if __name__ == "__main__":
    main()
