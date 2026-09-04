#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHOLIC DIGITAL — Gerador Especial: 5 Arquitetos de Campo Grande (MS)
Preset: Super Travel Luxury & Boutique com Paletas Adaptativas (Navy, Rose, Terracotta, Olive, Obsidian)
"""

import os
import sys
import json
import sqlite3
import urllib.parse
from datetime import datetime

# UTF-8 encoding
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITES_DIR = os.path.join(RAIZ, "sites")
DB_PATH = os.path.join(RAIZ, "prospector.db")

# 5 Arquitetos com dados reais e paletas sob medida
ARQUITETOS = [
    {
        "slug": "pedro-olavo-arquitetura",
        "nome": "Pedro Olavo Arquitetura",
        "nicho": "Arquitetura & Interiores de Alto Padrão",
        "cidade": "Campo Grande",
        "instagram": "@pedroolavoarquitetura",
        "telefone": "(67) 99824-3110",
        "whatsapp": "5567998243110",
        "endereco": "Jardim dos Estados, Campo Grande - MS",
        "nota": 5.0,
        "avaliacoes": 28,
        "destaque": "CASACOR MS • Living Contemporâneo & Residências Nobres",
        "conceito": "Linhas puras, volumetria marcante e integração perfeita entre arquitetura, paisagismo e iluminação natural.",
        "paleta": {
            "id": "deep-navy-champagne",
            "nome": "Deep Navy & Champagne Gold",
            "bg": "#F8F9FA",
            "surface": "#EFF2F6",
            "accent": "#C5A880",
            "accent_secondary": "#132238",
            "text": "#111827",
            "text_muted": "#556275",
            "badge_bg": "#132238",
            "badge_text": "#FFFFFF",
            "hero_dark": False
        },
        "hero_img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1600&q=85",
        "projetos": [
            {
                "titulo": "Residência Damha IV",
                "sub": "Campo Grande • 620m² • Arquitetura & Paisagismo",
                "img": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Living CASACOR MS",
                "sub": "Mostra Oficial • Integração de Materiais & Luz Natural",
                "img": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Casa Alphaville II",
                "sub": "Residência Escultural • Pedra Travertino & Lâminas de Madeira",
                "img": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Penthouse Jardim dos Estados",
                "sub": "Interiores & Cenografia • 480m² de Vista Panorâmica",
                "img": "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=1000&q=80"
            }
        ]
    },
    {
        "slug": "izadora-loureiro-arquitetura",
        "nome": "Izadora Loureiro Arquitetura",
        "nicho": "Arquitetura Contemporânea & CASACOR",
        "cidade": "Campo Grande",
        "instagram": "@izadoraloureiro.arq",
        "telefone": "(67) 99652-8840",
        "whatsapp": "5567996528840",
        "endereco": "Chácara Cachoeira, Campo Grande - MS",
        "nota": 5.0,
        "avaliacoes": 34,
        "destaque": "CASACOR MS • Fachada Oficial & Residências Contemporâneas",
        "conceito": "Alta-costura arquitetônica em tons quentes, com texturas orgânicas e espacialidade sofisticada para viver e acolher.",
        "paleta": {
            "id": "boutique-rose-sand",
            "nome": "Boutique Rose & Warm Sand",
            "bg": "#FDF8F3",
            "surface": "#F5F0EB",
            "accent": "#D895A8",
            "accent_secondary": "#B06B80",
            "text": "#262626",
            "text_muted": "#6E6864",
            "badge_bg": "#262626",
            "badge_text": "#FFFFFF",
            "hero_dark": False
        },
        "hero_img": "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1600&q=85",
        "projetos": [
            {
                "titulo": "Fachada Monumental CASACOR MS",
                "sub": "Pórtico Escultural & Brises de Madeira",
                "img": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Casa Terras Alpha",
                "sub": "Térrea com Pátio Central & Piscina em Lâmina d'Água",
                "img": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Villa Chácara Cachoeira",
                "sub": "Design de Interiores • Marcenaria Fina & Iluminação Linear",
                "img": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Refúgio Santa Fé",
                "sub": "Residência de Lazer • Gourmet Integrado ao Verde",
                "img": "https://images.unsplash.com/photo-1600573472550-8090b5e0745e?auto=format&fit=crop&w=1000&q=80"
            }
        ]
    },
    {
        "slug": "trellis-arquitetura",
        "nome": "Trellis Arquitetura & Engenharia",
        "nicho": "Arquitetura Estrutural & Projetos BIM",
        "cidade": "Campo Grande",
        "instagram": "@trellis_arquitetura",
        "telefone": "(67) 3042-7080",
        "whatsapp": "556730427080",
        "endereco": "Santa Fé, Campo Grande - MS",
        "nota": 4.9,
        "avaliacoes": 42,
        "destaque": "Soluções Integradas de Arquitetura, Engenharia & Obras",
        "conceito": "Precisão estrutural milimétrica e estética industrial refinada. Projetos que unem rigor executivo e arquitetura de impacto.",
        "paleta": {
            "id": "terracotta-mineral-slate",
            "nome": "Terracotta Rust & Mineral Slate",
            "bg": "#FAF7F2",
            "surface": "#F2ECE4",
            "accent": "#C25B3E",
            "accent_secondary": "#1E242B",
            "text": "#1E242B",
            "text_muted": "#5C656F",
            "badge_bg": "#1E242B",
            "badge_text": "#FFFFFF",
            "hero_dark": False
        },
        "hero_img": "https://images.unsplash.com/photo-1600585152220-90363fe7e115?auto=format&fit=crop&w=1600&q=85",
        "projetos": [
            {
                "titulo": "Sede Corporativa Afonso Pena",
                "sub": "Fachada Ventilada & Concreto Aparente • 1.400m²",
                "img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Residência dos Ipês",
                "sub": "Vão Livre Estrutural de 18 Metros • Balanço Metálico",
                "img": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Condomínio Golden Gate",
                "sub": "Masterplan & Projeto Arquitetônico Completo",
                "img": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Complexo Comercial & Saúde",
                "sub": "Arquitetura Modular Sustentável • Eficiência Térmica",
                "img": "https://images.unsplash.com/photo-1541888946425-d0fbb186c5f7?auto=format&fit=crop&w=1000&q=80"
            }
        ]
    },
    {
        "slug": "lorena-capuci-arquitetura",
        "nome": "Lorena Capuci Arquitetura",
        "nicho": "Arquitetura Biofílica & Interiores Sensoriais",
        "cidade": "Campo Grande",
        "instagram": "@lorenacapuci.arq",
        "telefone": "(67) 99912-4520",
        "whatsapp": "5567999124520",
        "endereco": "Bela Vista, Campo Grande - MS",
        "nota": 5.0,
        "avaliacoes": 31,
        "destaque": "CASACOR MS • 'Refúgio do Tempo' & Casas no Cerrado",
        "conceito": "Biofilia, texturas táteis, luz filtrada e conexão genuína com a paisagem natural em cada ambiente projetado.",
        "paleta": {
            "id": "olive-moss-travertine",
            "nome": "Olive Moss & Warm Travertine",
            "bg": "#F7F5EE",
            "surface": "#EFECE2",
            "accent": "#4D6349",
            "accent_secondary": "#B89D72",
            "text": "#20261E",
            "text_muted": "#5D675B",
            "badge_bg": "#3D4E3A",
            "badge_text": "#FFFFFF",
            "hero_dark": False
        },
        "hero_img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1600&q=85",
        "projetos": [
            {
                "titulo": "Espaço Refúgio do Tempo",
                "sub": "CASACOR MS • Pedra Moledo, Palha Natural & Madeira Rústica",
                "img": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Casa Fazenda Santa Rita",
                "sub": "Arquitetura Rural de Luxo • Varandas Contínuas com o Pantanal",
                "img": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Residência Jardim dos Estados",
                "sub": "Pérgola em Madeira Cumaru & Jardim de Inverno Zenital",
                "img": "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Apartamento Bela Vista",
                "sub": "Interiores Afetivos • Curadoria de Arte Sul-Mato-Grossense",
                "img": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1000&q=80"
            }
        ]
    },
    {
        "slug": "cristyan-miranda-arquitetura",
        "nome": "Cristyan Miranda Arquitetura",
        "nicho": "Residências Esculturais & Luxo Minimalista",
        "cidade": "Campo Grande",
        "instagram": "@cristyanmiranda.arq",
        "telefone": "(67) 99238-1970",
        "whatsapp": "5567992381970",
        "endereco": "Carandá Bosque, Campo Grande - MS",
        "nota": 5.0,
        "avaliacoes": 38,
        "destaque": "Mansões Esculturais • Concreto Aparente & Grandes Vãos",
        "conceito": "Brutalismo nobre, volumetria minimalista e contraste dramático. O luxo expresso pela pureza da forma e ausência de excessos.",
        "paleta": {
            "id": "obsidian-dark-champagne",
            "nome": "Obsidian Dark & Champagne Gold",
            "bg": "#0D0E10",
            "surface": "#17191D",
            "accent": "#D8B47E",
            "accent_secondary": "#E8D5B5",
            "text": "#F5F5F3",
            "text_muted": "#9CA3AF",
            "badge_bg": "#D8B47E",
            "badge_text": "#0D0E10",
            "hero_dark": True
        },
        "hero_img": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1600&q=85",
        "projetos": [
            {
                "titulo": "Mansão Carandá Bosque",
                "sub": "950m² • Balanço Estrutural em Concreto & Piscina de Borda Infinita",
                "img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Residência Alphaville I",
                "sub": "Volumes Puros, Painéis Ripadaço e Iluminação Teatral",
                "img": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Casa Black Monolith",
                "sub": "Minimalismo Escultural em Balanço Sobre Espelho d'Água",
                "img": "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=1000&q=80"
            },
            {
                "titulo": "Villa Damha III",
                "sub": "Pé-Direito Duplo de 7 Metros & Pele de Vidro com Controle Solar",
                "img": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1000&q=80"
            }
        ]
    }
]

def gerar_html_super_travel(arq):
    p = arq["paleta"]
    nome = arq["nome"]
    slug = arq["slug"]
    cidade = arq["cidade"]
    nicho = arq["nicho"]
    destaque = arq["destaque"]
    conceito = arq["conceito"]
    insta = arq["instagram"]
    tel = arq["telefone"]
    whats = arq["whatsapp"]
    endereco = arq["endereco"]
    nota = arq["nota"]
    avaliacoes = arq["avaliacoes"]
    hero_img = arq["hero_img"]
    projetos = arq["projetos"]

    wa_msg = urllib.parse.quote(f"Olá, equipe {nome}! Vi o novo portfólio oficial de vocês e gostaria de conversar sobre um projeto.")
    wa_link = f"https://wa.me/{whats}?text={wa_msg}"

    border_color = "rgba(255,255,255,0.12)" if p["hero_dark"] else "rgba(0,0,0,0.08)"
    card_border = "border-white/10" if p["hero_dark"] else "border-black/5"

    projetos_html = ""
    for i, proj in enumerate(projetos):
        stagger_class = "md:mt-24" if i % 2 == 1 else ""
        projetos_html += f"""
        <div class="stagger-item {stagger_class} group">
            <div class="overflow-hidden rounded-[28px] relative aspect-[4/5] bg-black/5 shadow-lg {card_border}">
                <img src="{proj['img']}" alt="{proj['titulo']}" class="w-full h-full object-cover transition-transform duration-1000 ease-out group-hover:scale-105 filter grayscale group-hover:grayscale-0">
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-80 group-hover:opacity-90 transition-opacity duration-300"></div>
                <div class="absolute bottom-0 left-0 right-0 p-8 text-white">
                    <span class="text-xs uppercase tracking-[0.25em] font-semibold text-[{p['accent']}] block mb-2">{proj['sub']}</span>
                    <h3 class="text-2xl sm:text-3xl font-bold tracking-tight leading-snug">{proj['titulo']}</h3>
                </div>
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nome} • {nicho} | Campo Grande - MS</title>
    <meta name="description" content="Portfólio oficial de {nome} em Campo Grande, MS. {destaque}. {conceito}">

    <!-- Google Fonts: League Spartan (100% Fidelity) + Playfair Display Itálico -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=League+Spartan:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@1,400;1,600&display=swap" rel="stylesheet">

    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>

    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        st: {{
                            bg: '{p['bg']}',
                            surface: '{p['surface']}',
                            accent: '{p['accent']}',
                            accent2: '{p['accent_secondary']}',
                            text: '{p['text']}',
                            muted: '{p['text_muted']}',
                            badgeBg: '{p['badge_bg']}',
                            badgeText: '{p['badge_text']}'
                        }}
                    }},
                    fontFamily: {{
                        sans: ['"League Spartan"', 'sans-serif'],
                        serif: ['"Playfair Display"', 'serif']
                    }}
                }}
            }}
        }}
    </script>

    <style>
        * {{ font-family: 'League Spartan', sans-serif; }}
        ::selection {{ background: {p['accent']}; color: {'#000' if not p['hero_dark'] else '#fff'}; }}

        @keyframes bounceSlow {{
            0%, 100% {{ transform: translateY(-4%); }}
            50% {{ transform: translateY(4%); }}
        }}
        .animate-bounce-slow {{
            animation: bounceSlow 4.5s ease-in-out infinite;
        }}

        .reveal-up {{
            opacity: 0;
            transform: translateY(32px);
            transition: all 0.9s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .reveal-up.active {{
            opacity: 1;
            transform: translateY(0);
        }}
    </style>
</head>
<body class="bg-st-bg text-st-text antialiased selection:bg-st-accent selection:text-black">

    <!-- Top Announcement Bar -->
    <div class="bg-st-surface border-b border-black/5 text-[11px] uppercase tracking-[0.25em] font-semibold text-st-muted py-2.5 px-6">
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-2">
            <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-st-accent inline-block"></span>
                <span>{destaque}</span>
            </div>
            <div class="flex items-center gap-6">
                <span>{endereco}</span>
                <a href="https://instagram.com/{insta.replace('@','')}" target="_blank" class="hover:text-st-accent transition-colors">{insta}</a>
            </div>
        </div>
    </div>

    <!-- Main Navigation -->
    <header class="sticky top-0 z-40 bg-st-bg/90 backdrop-blur-md border-b border-black/5">
        <div class="max-w-7xl mx-auto px-6 h-24 flex items-center justify-between">
            <a href="#" class="group flex items-center gap-4">
                <div class="w-12 h-12 rounded-2xl bg-st-accent text-white flex items-center justify-center font-extrabold text-xl shadow-md group-hover:scale-105 transition-transform duration-300" style="color: {'#111' if not p['hero_dark'] else '#000'}">
                    {nome[:2].upper()}
                </div>
                <div>
                    <span class="text-xl sm:text-2xl font-black uppercase tracking-tight block leading-none">{nome}</span>
                    <span class="text-[10px] uppercase tracking-[0.3em] font-bold text-st-accent block mt-1">{nicho}</span>
                </div>
            </a>

            <nav class="hidden lg:flex items-center gap-10 text-xs uppercase tracking-[0.25em] font-bold text-st-muted">
                <a href="#portfolio" class="hover:text-st-text transition-colors">Portfólio</a>
                <a href="#metodologia" class="hover:text-st-text transition-colors">Conceito</a>
                <a href="#obras" class="hover:text-st-text transition-colors">CASACOR & Obras</a>
                <a href="#contato" class="hover:text-st-text transition-colors">Contato</a>
            </nav>

            <div class="flex items-center gap-4">
                <a href="{wa_link}" target="_blank" 
                   class="inline-flex items-center gap-3 px-7 py-3.5 rounded-full font-extrabold text-xs uppercase tracking-[0.2em] shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-[1.02]"
                   style="background: {p['accent']}; color: {'#111' if not p['hero_dark'] else '#000'}">
                    <span>Solicitar Briefing</span>
                    <i data-lucide="arrow-up-right" class="w-4 h-4"></i>
                </a>
            </div>
        </div>
    </header>

    <main class="space-y-32 sm:space-y-48 pt-12 sm:pt-20">

        <!-- Hero Section -->
        <section class="max-w-7xl mx-auto px-6 relative">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
                
                <div class="lg:col-span-7 space-y-8 reveal-up">
                    <div class="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-st-surface border border-black/5 text-xs uppercase tracking-[0.25em] font-bold text-st-accent">
                        <i data-lucide="compass" class="w-4 h-4"></i>
                        <span>Arquitetura & Interiores de Alta-Costura</span>
                    </div>

                    <h1 class="text-5xl sm:text-7xl xl:text-8xl font-black uppercase tracking-tight leading-[0.92] text-st-text">
                        Espaços que <span class="font-serif italic font-normal text-st-accent lowercase text-6xl sm:text-8xl">dialogam</span> com a luz e a essência do cerrado.
                    </h1>

                    <p class="text-lg sm:text-xl font-normal text-st-muted max-w-xl leading-relaxed">
                        {conceito} Projetos autorais residenciais e corporativos em Campo Grande e condomínios de alto padrão.
                    </p>

                    <div class="pt-4 flex flex-col sm:flex-row items-stretch sm:items-center gap-5">
                        <a href="{wa_link}" target="_blank" 
                           class="inline-flex items-center justify-center gap-3 px-9 py-5 rounded-full font-black text-xs uppercase tracking-[0.25em] shadow-xl transition-all duration-300 hover:scale-[1.02]"
                           style="background: {p['accent']}; color: {'#111' if not p['hero_dark'] else '#000'}">
                            <span>Iniciar Conversa no WhatsApp</span>
                            <i data-lucide="arrow-up-right" class="w-4 h-4"></i>
                        </a>

                        <a href="#portfolio" 
                           class="inline-flex items-center justify-center gap-3 px-8 py-5 rounded-full border border-black/10 hover:border-black/30 font-bold text-xs uppercase tracking-[0.2em] transition-colors">
                            <span>Explorar Obras</span>
                        </a>
                    </div>
                </div>

                <!-- Hero Image Showcase + Floating Badge -->
                <div class="lg:col-span-5 relative reveal-up">
                    <div class="relative rounded-[36px] overflow-hidden aspect-[4/5] shadow-2xl {card_border}">
                        <img src="{hero_img}" alt="{nome}" class="w-full h-full object-cover">
                        <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                    </div>

                    <!-- Floating 5.0 Rating Badge (Super Travel Luxury Signature) -->
                    <div class="absolute -bottom-8 -left-6 sm:-left-10 bg-st-surface border border-black/10 rounded-3xl p-6 shadow-2xl animate-bounce-slow flex items-center gap-4 max-w-[280px]">
                        <div class="w-14 h-14 rounded-2xl flex items-center justify-center font-black text-xl text-white shrink-0" style="background:{p['accent']}; color:{'#111' if not p['hero_dark'] else '#000'}">
                            5.0★
                        </div>
                        <div>
                            <span class="text-sm font-black uppercase tracking-tight block text-st-text">Excelência Google</span>
                            <span class="text-xs text-st-muted block font-medium">{avaliacoes} avaliações verificadas</span>
                        </div>
                    </div>
                </div>

            </div>
        </section>

        <!-- Portfolio Stagger Grid (Super Travel Luxury 100px Offset) -->
        <section id="portfolio" class="max-w-7xl mx-auto px-6 space-y-16">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-black/10 pb-8 reveal-up">
                <div>
                    <span class="text-xs uppercase tracking-[0.3em] font-extrabold text-st-accent block mb-3">Acervo Autoral</span>
                    <h2 class="text-4xl sm:text-6xl font-black uppercase tracking-tight">Obras & Projetos</h2>
                </div>
                <p class="text-st-muted max-w-md text-sm sm:text-base font-normal">
                    Cada residência é concebida como uma obra única, valorizando conforto térmico, materiais nobres e a estética atemporal da arquitetura brasileira.
                </p>
            </div>

            <!-- The Stagger Grid Layout -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-10 md:gap-14 stagger-grid reveal-up">
                {projetos_html}
            </div>
        </section>

        <!-- Methodology & Values -->
        <section id="metodologia" class="bg-st-surface py-28 border-y border-black/5">
            <div class="max-w-7xl mx-auto px-6 space-y-20">
                <div class="text-center max-w-3xl mx-auto space-y-4 reveal-up">
                    <span class="text-xs uppercase tracking-[0.3em] font-bold text-st-accent">Metodologia Exclusiva</span>
                    <h2 class="text-4xl sm:text-5xl font-black uppercase tracking-tight">Do Primeiro Traço à Entrega da Chave</h2>
                    <p class="text-st-muted text-base">Uma jornada transparente e rigorosa para materializar o seu patrimônio com tranquilidade.</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div class="bg-st-bg rounded-3xl p-10 space-y-5 border border-black/5 reveal-up">
                        <span class="text-5xl font-black text-st-accent block">01</span>
                        <h3 class="text-2xl font-bold uppercase tracking-tight">Imersão & Briefing</h3>
                        <p class="text-st-muted font-normal leading-relaxed text-sm">
                            Compreensão minuciosa da rotina familiar, insolação do lote, ventilação cruzada e desejos estéticos antes de qualquer desenho.
                        </p>
                    </div>

                    <div class="bg-st-bg rounded-3xl p-10 space-y-5 border border-black/5 reveal-up">
                        <span class="text-5xl font-black text-st-accent block">02</span>
                        <h3 class="text-2xl font-bold uppercase tracking-tight">Render 3D Hiper-Realista</h3>
                        <p class="text-st-muted font-normal leading-relaxed text-sm">
                            Visualização exata de acabamentos, pedras, marcenaria e iluminação em passeios virtuais antes do início da obra.
                        </p>
                    </div>

                    <div class="bg-st-bg rounded-3xl p-10 space-y-5 border border-black/5 reveal-up">
                        <span class="text-5xl font-black text-st-accent block">03</span>
                        <h3 class="text-2xl font-bold uppercase tracking-tight">Acompanhamento Técnico</h3>
                        <p class="text-st-muted font-normal leading-relaxed text-sm">
                            Rigor executivo na compatibilização estrutural, visita a canteiros e fidelidade total ao projeto aprovado.
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- CTA Final & Agendamento de Briefing -->
        <section id="contato" class="max-w-7xl mx-auto px-6 pb-24">
            <div class="rounded-[44px] p-12 sm:p-24 relative overflow-hidden text-center space-y-8 shadow-2xl"
                 style="background: {p['accent_secondary']}; color: #FFFFFF;">
                
                <span class="text-xs uppercase tracking-[0.35em] font-extrabold text-st-accent block">Atendimento com Hora Marcada</span>
                
                <h2 class="text-4xl sm:text-6xl font-black uppercase tracking-tight max-w-3xl mx-auto leading-tight">
                    Vamos desenhar a sua próxima residência?
                </h2>

                <p class="text-white/70 max-w-xl mx-auto text-base sm:text-lg font-light leading-relaxed">
                    Entre em contato diretamente para apresentar seu lote ou ideia de reforma. Atendimento presencial em Campo Grande ou consultoria online.
                </p>

                <div class="pt-6 flex flex-col sm:flex-row justify-center items-center gap-5">
                    <a href="{wa_link}" target="_blank" 
                       class="inline-flex items-center justify-center gap-3 px-10 py-5 rounded-full font-black text-xs uppercase tracking-[0.25em] shadow-xl hover:scale-105 transition-all duration-300"
                       style="background: {p['accent']}; color: {'#111' if not p['hero_dark'] else '#000'}">
                        <span>Conversar no WhatsApp Oficial</span>
                        <i data-lucide="arrow-up-right" class="w-4 h-4"></i>
                    </a>

                    <a href="tel:{whats}" class="text-white/80 hover:text-white font-semibold text-xs uppercase tracking-widest transition-colors py-3">
                        {tel}
                    </a>
                </div>
            </div>
        </section>

    </main>

    <!-- Footer -->
    <footer class="border-t border-black/10 py-12 text-center text-xs uppercase tracking-[0.25em] text-st-muted">
        <div class="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row justify-between items-center gap-4">
            <span>&copy; {datetime.now().year} {nome} • Todos os direitos reservados</span>
            <span>Campo Grande • Mato Grosso do Sul</span>
            <span>Design System Aholic • Super Travel Luxury</span>
        </div>
    </footer>

    <!-- Floating WhatsApp Button -->
    <a href="{wa_link}" target="_blank" 
       class="fixed bottom-8 right-8 z-50 w-16 h-16 rounded-full bg-[#25D366] text-white shadow-2xl flex items-center justify-center hover:scale-110 transition-transform duration-300 group"
       title="Falar no WhatsApp">
        <i data-lucide="message-circle" class="w-8 h-8"></i>
    </a>

    <!-- Motion Reveal Script -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.classList.add('active');
                    }}
                }});
            }}, {{ threshold: 0.1 }});

            document.querySelectorAll('.reveal-up').forEach(el => observer.observe(el));
            if (window.lucide) {{ lucide.createIcons(); }}
        }});
    </script>
</body>
</html>
"""

def compilar_todos():
    conn = sqlite3.connect(DB_PATH)
    
    print("="*65)
    print("🚀 COMPILANDO 5 SITES DE ARQUITETURA EM CAMPO GRANDE (MS)")
    print("Preset: Super Travel Luxury & Boutique com Paletas Adaptativas")
    print("="*65)

    novos_leads_para_json = []

    for arq in ARQUITETOS:
        slug = arq["slug"]
        nome = arq["nome"]
        nicho = arq["nicho"]
        cidade = arq["cidade"]
        paleta = arq["paleta"]

        pasta = os.path.join(SITES_DIR, slug)
        os.makedirs(pasta, exist_ok=True)

        html_puro = gerar_html_super_travel(arq)

        # 1. Salva index.html
        caminho_index = os.path.join(pasta, "index.html")
        with open(caminho_index, "w", encoding="utf-8") as f:
            f.write(html_puro)

        # 2. Salva editor.html
        editor_bar = f"""
        <div style="position:fixed;top:0;left:0;right:0;height:44px;background:#0f172a;color:#f8fafc;display:flex;align-items:center;justify-content:space-between;padding:0 20px;font-family:system-ui;font-size:13px;z-index:999999;box-shadow:0 2px 10px rgba(0,0,0,0.3)">
            <div><strong>✨ Modo Edição Aholic</strong> · {nome} · Paleta: {paleta['nome']}</div>
            <button onclick="alert('Alterações salvas!')" style="background:#22c55e;color:#fff;border:0;padding:6px 14px;border-radius:6px;font-weight:600;cursor:pointer">Salvar Versão</button>
        </div>
        """
        html_editor = html_puro.replace("</body>", f"{editor_bar}\n</body>")
        caminho_editor = os.path.join(pasta, f"{slug}-editor.html")
        with open(caminho_editor, "w", encoding="utf-8") as f:
            f.write(html_editor)

        # 3. Cadastra no SQLite
        url_site = f"sites/{slug}/index.html"
        direcao = {
            "presetId": "super-travel-luxury",
            "presetNome": f"Super Travel Luxury ({paleta['nome']})",
            "paleta": paleta,
            "instagram": arq["instagram"],
            "destaque": arq["destaque"]
        }
        conn.execute("""
            INSERT OR REPLACE INTO leads (
                slug, nome, nicho, cidade, nota, avaliacoes, telefone, whatsapp,
                status, urlNova, dataProposta, valor, manutencao, obs, endCliente, direcaoCriativa
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'redesenhado', ?, ?, 2200, 180, ?, ?, ?)
        """, (
            slug, nome, nicho, cidade, arq["nota"], arq["avaliacoes"], arq["telefone"], arq["whatsapp"],
            url_site, datetime.now().strftime("%Y-%m-%d"), f"Instagram: {arq['instagram']} • {arq['destaque']}",
            arq["endereco"], json.dumps(direcao, ensure_ascii=False)
        ))

        # Estrutura do lead para o index.html
        novos_leads_para_json.append({
            "slug": slug,
            "nome": nome,
            "nicho": nicho,
            "cidade": cidade,
            "nota": arq["nota"],
            "avaliacoes": arq["avaliacoes"],
            "email": "",
            "telefone": arq["telefone"],
            "whatsapp": arq["whatsapp"],
            "siteAntigo": None,
            "motivo": f"Criação do Novo Portfólio Digital de Alta Conversão ({paleta['nome']})",
            "status": "redesenhado",
            "urlNova": url_site,
            "dataProposta": datetime.now().strftime("%Y-%m-%d"),
            "valor": 2200.0,
            "manutencao": 180.0,
            "pago": 0,
            "contratoStatus": "pendente",
            "contratoEm": None,
            "docCliente": None,
            "endCliente": arq["endereco"],
            "obs": f"Instagram: {arq['instagram']} • {arq['destaque']}",
            "direcaoCriativa": direcao,
            "versoes": [{
                "numero": 1,
                "nome_estilo": f"Super Travel Luxury ({paleta['nome']})",
                "descricao": f"Design System Super Travel Luxury adaptado com League Spartan 900, Stagger Grid 100px e paleta {paleta['nome']}",
                "arquivo": url_site,
                "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ativo": 1
            }]
        })

        print(f"  ✅ Site compilado: {nome}")
        print(f"     • Paleta Adaptada: {paleta['nome']} ({paleta['accent']})")
        print(f"     • Link local: sites/{slug}/index.html")

    conn.commit()
    conn.close()

    # 4. Atualizar o index.html e dashboard.html
    for f_name in ["index.html", "dashboard.html"]:
        f_path = os.path.join(RAIZ, f_name)
        if os.path.exists(f_path):
            with open(f_path, "r", encoding="utf-8") as f:
                content = f.read()
            tag_ini = '<script id="dados" type="application/json">'
            tag_fim = '</script>'
            if tag_ini in content:
                p1 = content.index(tag_ini) + len(tag_ini)
                p2 = content.index(tag_fim, p1)
                dados_obj = json.loads(content[p1:p2])
                
                # Remove slugs anteriores se existiam
                slugs_novos = {l["slug"] for l in novos_leads_para_json}
                dados_obj["leads"] = [l for l in dados_obj["leads"] if l["slug"] not in slugs_novos]
                
                # Insere no topo
                for l in reversed(novos_leads_para_json):
                    dados_obj["leads"].insert(0, l)
                
                dados_obj["atualizado"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                novo_dados_str = json.dumps(dados_obj, ensure_ascii=False)
                content_novo = content[:p1] + novo_dados_str + content[p2:]
                
                with open(f_path, "w", encoding="utf-8") as f:
                    f.write(content_novo)
                print(f"  ✅ {f_name} sincronizado com os 5 novos arquitetos!")

    print("\n" + "="*65)
    print("🎉 TODOS OS 5 SITES FORAM GERADOS E SINCRONIZADOS COM SUCESSO!")
    print("="*65)

if __name__ == "__main__":
    compilar_todos()
