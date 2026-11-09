#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testa a biblioteca única: catálogo, salvamento e a API do dashboard."""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from biblioteca_temas import Biblioteca, templatizar_html  # noqa: E402


def teste_catalogo_do_repositorio():
    bib = Biblioteca(RAIZ)
    temas = bib.listar()
    ids = {t["id"] for t in temas}
    visuais = json.loads((RAIZ / "referencias" / "presets-visuais.json").read_text(encoding="utf-8"))
    faltando = [p["id"] for p in visuais if p["id"] not in ids]
    assert not faltando, faltando
    arquetipos = {t.get("arquetipo") for t in temas}
    for aid in ("quiet_luxury", "swiss_tech", "monografia_editorial", "warm_organic", "dark_authority"):
        assert aid in arquetipos, aid
    for stem in ("lumina-luxury-refined", "modern-organic-editorial", "normal-is-boring"):
        tema = bib.resolver(stem)
        assert tema, stem
        assert (RAIZ / tema["html"]).exists()
        assert (RAIZ / tema["html_geracao"]).exists()
        assert "{{NOME_EMPRESA}}" in (RAIZ / tema["html_geracao"]).read_text(encoding="utf-8")
    editorial = bib.resolver("quiet-luxury")
    assert editorial["id"] == "editorial-atelier"
    assert editorial["motor"] == "quiet-luxury"
    assert bib.resolver("swiss-precision")["id"] == "instrumento-digital"
    assert bib.resolver("warm-organic")["id"] == "modern-organic-editorial"
    assert bib.resolver("cinema-3d-spatial")["id"] == "cinematic-3d-spatial"
    assert bib.escolher("Odontologia digital") == "instrumento-digital"
    print("ok catálogo do repositório:", len(temas), "temas")


def teste_gerador_le_a_mesma_fonte():
    spec = importlib.util.spec_from_file_location("gerar_site_lead", RAIZ / "scripts" / "gerar-site-lead.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    lead = {
        "nome": "Atelier Teste",
        "nicho": "Cafeteria de bairro",
        "cidade": "Cidade Exemplo",
        "whatsapp": "5500000000000",
        "telefone": "(00) 00000-0000",
        "endCliente": "Rua Exemplo, 10",
        "nota": 4.9,
        "avaliacoes": 12,
        "obs": "Café de teste, sem cliente real.",
    }
    html, tema = mod.html_para_lead(lead, "cinema-local", None, [])
    assert tema["id"] == "cinema-local"
    assert "Atelier Teste" in html
    assert "{{NOME_EMPRESA}}" not in html
    assert "unsplash.com" not in html
    assert "99999" not in html
    luxo, tema_luxo = mod.html_para_lead(lead, "quiet-luxury", None, [])
    assert tema_luxo["id"] == "editorial-atelier"
    assert "Atelier Teste" in luxo
    assert "unsplash.com" not in luxo
    assert (RAIZ / "temas" / "editorial-atelier" / "theme.json").exists()
    assert (RAIZ / "temas" / "editorial-atelier" / "casca.html").exists()
    lead_direcao = dict(lead, nicho="Psicologia", direcaoCriativa={"presetId": "swiss-precision"})
    assert mod.resolver_preset_id(lead_direcao, "auto") == "instrumento-digital"
    sem_foto = mod.montar_contexto({"nome": "Sem Foto", "nicho": "Teste", "cidade": "Cidade"}, None, [])
    assert "99999" not in sem_foto["WHATSAPP_NUMERO"]
    assert sem_foto["FOTO_HERO"] == ""
    try:
        mod.html_para_lead(lead, "tema-que-nao-existe", None, [])
        raise AssertionError("tema inexistente deveria falhar")
    except mod.TemaIndisponivel as erro:
        assert "não existe" in str(erro)
    print("ok gerador")


def teste_salvamento_isolado():
    tmp = Path(tempfile.mkdtemp(prefix="aholic-bib-"))
    try:
        destino = tmp / "referencias"
        destino.mkdir()
        for nome in ("presets-visuais.json", "presets-dinamicos.json", "catalogo-design.json"):
            shutil.copy(RAIZ / "referencias" / nome, destino / nome)
        bib = Biblioteca(tmp)
        bib.reindexar(preservar_personalizados=False)
        antes = {t["id"] for t in bib.listar()}
        assert "editorial-atelier" in antes
        html = "<!DOCTYPE html><html><head><title>{{NOME_EMPRESA}}</title></head><body><h1>{{NOME_EMPRESA}}</h1><p>MARCA-SALVA</p></body></html>"
        salvo = bib.salvar({
            "id": "padaria-da-esquina",
            "nome": "Padaria da Esquina",
            "nicho": "Padaria artesanal",
            "nichos_recomendados": ["Padaria artesanal"],
            "descricao": "Tema de teste.",
            "ativo": True,
        }, html=html)
        assert salvo["html_personalizado"] is True
        assert salvo["motor"] == "template"
        de_novo = Biblioteca(tmp)
        tema = de_novo.resolver("padaria-da-esquina")
        assert tema and tema["nicho"] == "Padaria artesanal"
        assert "MARCA-SALVA" in de_novo.ler_html_geracao(tema)
        render = de_novo.renderizar(tema, {"NOME_EMPRESA": "Forno Teste"})
        assert "Forno Teste" in render and "MARCA-SALVA" in render and "{{NOME_EMPRESA}}" not in render
        assert de_novo.escolher("Padaria artesanal") == "padaria-da-esquina"
        de_novo.reindexar(preservar_personalizados=True)
        assert "MARCA-SALVA" in Biblioteca(tmp).ler_html_geracao(Biblioteca(tmp).resolver("padaria-da-esquina"))
        (destino / "templates").mkdir()
        (destino / "templates" / "tema-recem-chegado.html").write_text(
            "<!DOCTYPE html><html><head><title>Tema Recém Chegado</title></head><body>NOVO</body></html>",
            encoding="utf-8",
        )
        ids = {t["id"] for t in Biblioteca(tmp).listar()}
        assert "tema-recem-chegado" in ids
        print("ok salvamento isolado")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def teste_templatizar():
    html = "<h1>Clínica Exemplo</h1><p>de atendimento</p><p>Cidade Exemplo</p>"
    saida = templatizar_html(html, {"nome": "Clínica Exemplo", "cidade": "Cidade Exemplo"})
    assert "{{NOME_EMPRESA}}" in saida
    assert "{{CIDADE}}" in saida
    assert "de atendimento" in saida
    print("ok templatizar")


def teste_api_dashboard():
    tmp = Path(tempfile.mkdtemp(prefix="aholic-api-"))
    servidor = None
    env_antigo = os.environ.get("AHOLIC_RAIZ")
    try:
        destino = tmp / "referencias"
        destino.mkdir()
        for nome in ("presets-visuais.json", "presets-dinamicos.json", "catalogo-design.json"):
            shutil.copy(RAIZ / "referencias" / nome, destino / nome)
        os.environ["AHOLIC_RAIZ"] = str(tmp)
        spec = importlib.util.spec_from_file_location("dashboard_server_teste", RAIZ / "dashboard-server.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        servidor = mod.ThreadingHTTPServer(("127.0.0.1", 0), mod.App)
        porta = servidor.server_address[1]
        fio = threading.Thread(target=servidor.serve_forever, daemon=True)
        fio.start()
        base = "http://127.0.0.1:%d" % porta

        def pedir(caminho, metodo="GET", corpo=None):
            dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
            req = urllib.request.Request(base + caminho, data=dados, method=metodo)
            if dados is not None:
                req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=30) as resp:
                bruto = resp.read().decode("utf-8")
                tipo = resp.headers.get("Content-Type", "")
            if "application/json" in tipo:
                return json.loads(bruto)
            return bruto

        lista = pedir("/api/presets")
        assert isinstance(lista, list) and any(t["id"] == "editorial-atelier" for t in lista)
        html = "<!DOCTYPE html><html><body><h1>{{NOME_EMPRESA}}</h1><p>API-SALVA</p></body></html>"
        resp = pedir("/api/temas", "POST", {
            "id": "tema-via-api",
            "nome": "Tema via API",
            "nicho": "Floricultura",
            "nichos_recomendados": ["Floricultura"],
            "descricao": "Salvo pela API.",
            "html": html,
            "ativo": True,
        })
        assert resp["ok"] and resp["tema"]["id"] == "tema-via-api"
        de_novo = pedir("/api/presets")
        assert any(t["id"] == "tema-via-api" for t in de_novo)
        corpo = pedir("/api/temas/tema-via-api/html")
        assert "API-SALVA" in corpo and "{{NOME_EMPRESA}}" in corpo
        # Uma lista antiga do navegador não pode apagar o tema que acabou de entrar.
        pedir("/api/presets", "POST", [{"id": "editorial-atelier", "nome": "Editorial de Atelier", "ativo": True}])
        depois = pedir("/api/temas")
        ids = {t["id"] for t in depois["temas"]}
        assert "tema-via-api" in ids and "editorial-atelier" in ids
        pedir("/api/leads", "POST", {"slug": "lead-teste-tema", "nome": "Lead Teste", "nicho": "Floricultura"})
        pedido = pedir("/api/leads/lead-teste-tema", "PUT", {
            "direcaoCriativa": {"presetId": "tema-via-api", "presetNome": "Tema via API"}
        })
        assert pedido["ok"]
        leads = pedir("/api/leads")
        lead = next(l for l in leads if l["slug"] == "lead-teste-tema")
        assert isinstance(lead["direcaoCriativa"], dict)
        assert lead["direcaoCriativa"]["presetId"] == "tema-via-api"
        print("ok api do dashboard na porta", porta)
    finally:
        if servidor is not None:
            servidor.shutdown()
            servidor.server_close()
        if env_antigo is None:
            os.environ.pop("AHOLIC_RAIZ", None)
        else:
            os.environ["AHOLIC_RAIZ"] = env_antigo
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    teste_catalogo_do_repositorio()
    teste_gerador_le_a_mesma_fonte()
    teste_templatizar()
    teste_salvamento_isolado()
    teste_api_dashboard()
    print("todos os testes passaram")
