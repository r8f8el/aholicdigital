#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza o banco prospector.db e os scripts embutidos do dashboard com os novos Instagrams e fotos reais.
"""

import os
import sys
import json
import sqlite3
import re

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(RAIZ, "prospector.db")
INDEX_PATH = os.path.join(RAIZ, "index.html")
DASH_PATH = os.path.join(RAIZ, "dashboard.html")
SITES_DIR = os.path.join(RAIZ, "sites")

ATUALIZACOES = [
    {
        "slug": "pedro-olavo-arquitetura",
        "instagram": "@pedroolavostudio"
    },
    {
        "slug": "izadora-loureiro-arquitetura",
        "instagram": "@arq.izadora"
    },
    {
        "slug": "trellis-arquitetura",
        "instagram": "@trellis_arquitetura"
    },
    {
        "slug": "lorena-capuci-arquitetura",
        "instagram": "@lorenacapuci"
    },
    {
        "slug": "cristyan-miranda-arquitetura",
        "instagram": "@cristyanmirandaarquiteto"
    }
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for item in ATUALIZACOES:
    slug = item["slug"]
    insta = item["instagram"]
    pasta_assets = os.path.join(SITES_DIR, slug, "assets")
    fotos = []
    if os.path.exists(pasta_assets):
        fotos = [f for f in sorted(os.listdir(pasta_assets)) if f.endswith(".jpg")]

    cursor.execute("""
        UPDATE leads 
        SET obs = ?
        WHERE slug = ?
    """, (f"Instagram oficial: {insta} • {len(fotos)} fotos reais baixadas do Instagram e Maps", slug))
    print(f"Atualizado DB: {slug} -> {insta} ({len(fotos)} fotos)")

conn.commit()
conn.close()

# Atualiza index.html e dashboard.html
for arq_path in [INDEX_PATH, DASH_PATH]:
    if not os.path.exists(arq_path):
        continue
    with open(arq_path, "r", encoding="utf-8") as f:
        content = f.read()

    m = re.search(r'<script id="dados"[^>]*>([\s\S]*?)</script>', content)
    if m:
        data = json.loads(m.group(1))
        lista_leads = data.get("leads", []) if isinstance(data, dict) else data
        for l in lista_leads:
            if not isinstance(l, dict):
                continue
            for item in ATUALIZACOES:
                if l.get("slug") == item["slug"]:
                    l["instagram"] = item["instagram"]
                    pasta_assets = os.path.join(SITES_DIR, item["slug"], "assets")
                    if os.path.exists(pasta_assets):
                        l["fotos_reais"] = [f for f in sorted(os.listdir(pasta_assets)) if f.endswith(".jpg")]
        novo_json = json.dumps(data, ensure_ascii=False)
        content = content[:m.start()] + f'<script id="dados" type="application/json">{novo_json}</script>' + content[m.end():]
        with open(arq_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Atualizado: {os.path.basename(arq_path)}")

print("Sincronização concluída com sucesso!")
