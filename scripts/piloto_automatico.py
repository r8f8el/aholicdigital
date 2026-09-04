#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHOLIC DIGITAL — Piloto Automático Noturno & Mineração Contínua
Esteira 100% autônoma: Minera no Maps -> Baixa fotos -> Gera sites Anti-Slop -> Atualiza Dashboard -> Deploy Vercel

Uso CLI:
  python scripts/piloto_automatico.py --modo 1 --nicho "estetica" --cidade "Goiania" --limite 5
  python scripts/piloto_automatico.py --modo 2   (Gera todos os pendentes no banco)
  python scripts/piloto_automatico.py --modo 3   (Modo Noturno com lista pré-configurada)
"""

import os
import sys
import json
import sqlite3
import subprocess
import argparse
from datetime import datetime

# Garante saída UTF-8 no Windows
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

# Adiciona pasta de scripts ao path para importar gerar-site-lead
sys.path.insert(0, PASTA_SCRIPTS)
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("gerar_site_lead", os.path.join(PASTA_SCRIPTS, "gerar-site-lead.py"))
    gerar_site_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gerar_site_module)
    compilar_site = gerar_site_module.compilar_site
except Exception as e:
    compilar_site = None

def detectar_python():
    """Detecta o interpretador Python funcional."""
    candidatos = [
        r"C:\Users\rafae\AppData\Local\Programs\Python\Python313\python.exe",
        sys.executable,
        "py",
        "python"
    ]
    for c in candidatos:
        if c and os.path.exists(c):
            return c
    return sys.executable or "python"

def minerar_leads(nicho, cidade, limite=5, visible=False):
    """Chama o minerador de leads."""
    print("\n" + "="*65)
    print(f"🔍 [1/4] MINERANDO LEADS: '{nicho}' em '{cidade}' (Meta: {limite} leads)")
    print("="*65)
    
    python_exe = detectar_python()
    script_miner = os.path.join(PASTA_SCRIPTS, "minerar-leads.py")
    
    cmd = [python_exe, script_miner, "--nicho", nicho, "--cidade", cidade, "--limite", str(limite)]
    if visible:
        cmd.append("--visible")
        
    try:
        res = subprocess.run(cmd, cwd=RAIZ)
        return res.returncode == 0
    except Exception as e:
        print(f"[-] Erro ao executar minerador: {e}")
        return False

def buscar_leads_pendentes():
    """Busca todos os leads com status 'novo' ou sem site gerado."""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT slug, nome, nicho, cidade, status, urlNova 
        FROM leads 
        WHERE status = 'novo' OR urlNova IS NULL OR urlNova = ''
        ORDER BY rowid DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def gerar_sites_pendentes(preset="auto"):
    """Gera sites para todos os leads que estão aguardando."""
    pendentes = buscar_leads_pendentes()
    print("\n" + "="*65)
    print(f"⚡ [2/4] GERANDO SITES ANTI-SLOP ({len(pendentes)} leads pendentes)")
    print("="*65)

    if not pendentes:
        print("ℹ️ Nenhum lead pendente de site no banco. Tudo atualizado!")
        return 0

    sucessos = 0
    for idx, lead in enumerate(pendentes, 1):
        slug = lead['slug']
        nome = lead['nome']
        print(f"\n[{idx}/{len(pendentes)}] Processando: {nome} ({slug})...")
        try:
            if compilar_site:
                ok = compilar_site(slug, preset)
            else:
                python_exe = detectar_python()
                script_gerar = os.path.join(PASTA_SCRIPTS, "gerar-site-lead.py")
                res = subprocess.run([python_exe, script_gerar, "--slug", slug, "--preset", preset], cwd=RAIZ)
                ok = res.returncode == 0

            if ok:
                sucessos += 1
                print(f"  ✅ Site de {nome} gerado com sucesso!")
            else:
                print(f"  ❌ Falha ao compilar site de {nome}.")
        except Exception as err:
            print(f"  ❌ Erro inesperado ao gerar {slug}: {err}")

    print(f"\n📊 Total de sites gerados nesta rodada: {sucessos}/{len(pendentes)}")
    return sucessos

def sincronizar_dashboard():
    """Sincroniza os dados do SQLite com index.html e dashboard.html mantendo UTF-8 limpo."""
    print("\n" + "="*65)
    print("🔄 [3/4] SINCRONIZANDO DASHBOARD COM SUPABASE & LOCAL")
    print("="*65)
    
    if not os.path.exists(DB_PATH):
        print("[-] prospector.db não encontrado.")
        return False

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY rowid DESC")
    rows = cursor.fetchall()
    conn.close()

    leads_list = []
    for r in rows:
        d = dict(r)
        
        # Detectar versões salvas na pasta
        versoes = []
        lead_slug = d.get('slug')
        pasta_lead = os.path.join(SITES_DIR, lead_slug)
        caminho_index = os.path.join(pasta_lead, "index.html")
        if os.path.exists(caminho_index):
            versoes.append({
                "numero": 1,
                "nome_estilo": "Modern Organic / Luxury",
                "descricao": "Versão Anti-Slop de Alta Conversão Aholic",
                "arquivo": f"sites/{lead_slug}/index.html",
                "criado_em": d.get('atualizado') or datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ativo": 1
            })

        # Tratar direcaoCriativa
        direcao = d.get('direcaoCriativa')
        if direcao and isinstance(direcao, str):
            try:
                direcao = json.loads(direcao)
            except Exception:
                pass

        item = {
            "slug": d.get("slug"),
            "nome": d.get("nome"),
            "nicho": d.get("nicho"),
            "cidade": d.get("cidade"),
            "nota": float(d.get("nota") or 5.0),
            "avaliacoes": int(d.get("avaliacoes") or 0),
            "email": d.get("email") or "",
            "telefone": d.get("telefone") or "",
            "whatsapp": d.get("whatsapp") or "",
            "siteAntigo": d.get("siteAntigo"),
            "motivo": d.get("motivo") or "",
            "status": d.get("status") or "novo",
            "urlNova": d.get("urlNova") or (f"sites/{lead_slug}/index.html" if os.path.exists(caminho_index) else ""),
            "dataProposta": d.get("dataProposta") or datetime.now().strftime("%Y-%m-%d"),
            "valor": float(d.get("valor") or 1800.0),
            "manutencao": float(d.get("manutencao") or 150.0),
            "pago": int(d.get("pago") or 0),
            "contratoStatus": d.get("contratoStatus") or "pendente",
            "contratoEm": d.get("contratoEm"),
            "docCliente": d.get("docCliente"),
            "endCliente": d.get("endCliente"),
            "obs": d.get("obs") or "",
            "direcaoCriativa": direcao,
            "versoes": versoes
        }
        leads_list.append(item)

    payload = {
        "atualizado": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "leads": leads_list
    }
    novo_json = json.dumps(payload, ensure_ascii=False)

    for arquivo_html in ["index.html", "dashboard.html"]:
        caminho = os.path.join(RAIZ, arquivo_html)
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                html = f.read()

            tag_ini = '<script id="dados" type="application/json">'
            tag_fim = '</script>'
            if tag_ini in html:
                p1 = html.index(tag_ini) + len(tag_ini)
                p2 = html.index(tag_fim, p1)
                html_atualizado = html[:p1] + novo_json + html[p2:]
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(html_atualizado)
                print(f"  ✅ {arquivo_html} sincronizado com {len(leads_list)} leads!")

    return True

def deploy_git():
    """Realiza commit e push automático para a Vercel/GitHub."""
    print("\n" + "="*65)
    print("🚀 [4/4] ENVIANDO ATUALIZAÇÕES PARA O GITHUB & VERCEL")
    print("="*65)
    try:
        subprocess.run(["git", "add", "."], cwd=RAIZ, check=True)
        msg = f"feat(autopilot): {datetime.now().strftime('%d/%m/%Y %H:%M')} novos sites gerados"
        subprocess.run(["git", "commit", "-m", msg], cwd=RAIZ)
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=RAIZ)
        if push_res.returncode == 0:
            print("🎉 Deploy concluído com sucesso! Sites ao vivo na Vercel.")
            return True
        else:
            print("⚠️ Não foi possível sincronizar com o GitHub remoto agora.")
            return False
    except Exception as e:
        print(f"[-] Erro no git deploy: {e}")
        return False

def modo_noturno():
    """Executa fila contínua de nichos e cidades de alto valor."""
    alvos = [
        ("estetica", "Goiania", 5),
        ("nutricao", "Florianopolis", 5),
        ("arquitetura", "Campinas", 5),
        ("odontologia", "Caldas Novas", 5),
        ("cafeteria", "Curitiba", 5),
    ]
    print("\n" + "#"*65)
    print("🌙 INICIANDO MODO NOTURNO — PILOTO AUTOMÁTICO AHOLIC")
    print(f"Total de alvos programados: {len(alvos)}")
    print("#"*65)

    for i, (nicho, cid, qtd) in enumerate(alvos, 1):
        print(f"\n>>> Rodada {i}/{len(alvos)}: {nicho.upper()} em {cid.upper()} (Limite: {qtd})")
        minerar_leads(nicho, cid, qtd, visible=False)
        gerar_sites_pendentes()
        sincronizar_dashboard()
        deploy_git()

    print("\n" + "#"*65)
    print("🏁 MODO NOTURNO FINALIZADO COM SUCESSO!")
    print("Todos os sites foram gerados e sincronizados com a Vercel.")
    print("#"*65)

def main():
    parser = argparse.ArgumentParser(description="Piloto Automático Aholic Sites")
    parser.add_argument("--modo", type=int, default=1, choices=[1, 2, 3], 
                        help="1: Minerar + Gerar + Deploy | 2: Gerar Pendentes | 3: Modo Noturno")
    parser.add_argument("--nicho", type=str, default="estetica")
    parser.add_argument("--cidade", type=str, default="Caldas Novas")
    parser.add_argument("--limite", type=int, default=5)
    parser.add_argument("--preset", type=str, default="auto")
    parser.add_argument("--no-deploy", action="store_true", help="Pular o push do git")
    args = parser.parse_args()

    if args.modo == 1:
        minerar_leads(args.nicho, args.cidade, args.limite)
        gerar_sites_pendentes(args.preset)
        sincronizar_dashboard()
        if not args.no_deploy:
            deploy_git()
    elif args.modo == 2:
        gerar_sites_pendentes(args.preset)
        sincronizar_dashboard()
        if not args.no_deploy:
            deploy_git()
    elif args.modo == 3:
        modo_noturno()

if __name__ == "__main__":
    main()
