#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Biblioteca única de temas da Aholic.

O dashboard e o gerador leem e gravam a mesma pasta:

  temas/<id>/theme.json
  temas/<id>/casca.html
  temas/<id>/preview.html

Cada tema guarda nome, nicho, prévia e o HTML (além dos tokens e metadados
que já existiam nos presets). Arquétipos, presets visuais, presets dinâmicos
e os HTML de referencias/templates/ entram nesse catálogo sem descarte.

Um HTML novo em referencias/templates/ (exceto capa-*.html) é incorporado
na primeira listagem. Um tema salvo pelo dashboard ou pelo editor fica no
catálogo e volta a aparecer para os dois.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

PLACEHOLDERS = [
    "NOME_EMPRESA",
    "NOME_LEAD",
    "NICHO",
    "CIDADE",
    "WHATSAPP_NUMERO",
    "WHATSAPP_LINK",
    "TELEFONE_VISUAL",
    "LOGO_HTML",
    "FOTO_HERO",
    "FOTO_ESPECIALISTA",
    "GALERIA_FOTOS_HTML",
    "AVALIACOES_NOTA",
    "AVALIACOES_QTD",
    "ENDERECO",
    "BIO_INSTAGRAM",
]

MOTORES = {"template", "quiet-luxury", "swiss-precision"}

# Campos que o servidor controla. O cliente não reescreve caminho de arquivo
# nem apaga um HTML salvo mandando a lista antiga do navegador.
PROTEGIDOS = {
    "html",
    "preview",
    "html_geracao",
    "html_referencia",
    "html_personalizado",
    "fontes",
    "aliases",
    "arquetipo",
    "referencia_local",
    "paleta_arquetipo",
}

# Ligações que os três arquivos antigos não declaravam entre si.
LIGACAO_ARQUETIPO = {
    "quiet_luxury": {
        "tema_id": "editorial-atelier",
        "aliases": ["quiet-luxury", "estetica-luxo", "quiet_luxury"],
        "motor": "quiet-luxury",
    },
    "swiss_tech": {
        "tema_id": "instrumento-digital",
        "aliases": ["swiss-precision", "odonto-tech", "swiss-tech", "swiss_tech"],
        "motor": "swiss-precision",
    },
    "monografia_editorial": {
        "tema_id": "lumina-luxury-refined",
        "aliases": ["monografia-editorial", "monografia_editorial", "lumina-luxury"],
        "motor": "template",
    },
    "warm_organic": {
        "tema_id": "modern-organic-editorial",
        "aliases": ["warm-organic", "warm_organic"],
        "motor": "template",
    },
    "dark_authority": {
        "tema_id": "dark-authority",
        "aliases": ["dark_authority"],
        "motor": "template",
    },
}

ALIASES_EXTRAS = {
    "cinematic-3d-spatial": ["cinema-3d-spatial"],
}

REGRAS_NICHO = [
    (["advoc", "jurid", "tribut", "peric", "auditor", "financ"], "dark-authority"),
    (["odont", "dent", "implant", "sorriso", "orofacial"], "instrumento-digital"),
    (["estet", "dermato", "cirurg", "harmoniz", "beleza"], "editorial-atelier"),
    (["psico", "terap", "neuro", "acolh"], "normal-is-boring"),
    (["nutri", "esport"], "modern-organic-editorial"),
    (["spa", "yoga", "bem-estar", "wellness"], "softly-wellness"),
    (["arquit", "interio", "decor"], "lumina-luxury-refined"),
    (["engen", "obra", "industrial", "roaster"], "warm-industrial"),
    (["barbear", "academ", "tatuag", "crossfit"], "brutalismo-comercial"),
    (["cafe", "café", "cafeter", "restaur", "gastro", "padaria", "bakery"], "cinema-local"),
    (["cinema", "spatial", "audiovis"], "cinematic-3d-spatial"),
]

TEMPLATES_CONHECIDOS = {
    "lumina-luxury-refined": {
        "nome": "Lumina Luxury Refined",
        "nicho": "Arquitetura de alto padrão",
        "descricao": "Arquitetura em obsidiana e champanhe, com Cinzel e muito espaço negativo. HTML de referência em referencias/templates/lumina-luxury-refined.html.",
        "tags": ["arquitetura", "luxo", "obsidiana", "champagne", "template"],
        "nichos_recomendados": ["Arquitetura de Alto Padrão", "Design de Interiores", "Engenharia Conceito"],
        "nichos_evitar": ["Comércio Popular", "Serviços de Emergência"],
        "composicao": "obsidian-editorial",
        "navegacao": "fixed-serif-header",
        "densidade": "baixa",
        "tipografia": {
            "display": "Cinzel",
            "body": "Plus Jakarta Sans",
            "labels": "JetBrains Mono",
            "escala": "extrema",
        },
        "paleta": {
            "estilo": "obsidiana-e-champagne",
            "sugestoes": {
                "fundo": "#0B0C0E",
                "superficie": "#131518",
                "texto": "#F5F2EB",
                "texto_secundario": "#E5DFD3",
                "acento": "#C5A880",
                "linha": "rgba(255, 255, 255, 0.08)",
            },
        },
    },
    "modern-organic-editorial": {
        "nome": "Modern Organic Editorial",
        "nicho": "Nutrição e bem-estar",
        "descricao": "Editorial orgânico em creme e sálvia, com DM Serif Display e Inter. HTML de referência em referencias/templates/modern-organic-editorial.html.",
        "tags": ["organico", "nutricao", "creme", "sage", "template"],
        "nichos_recomendados": ["Nutrição", "Nutrição Esportiva", "Medicina Integrativa", "Bem-estar"],
        "nichos_evitar": ["Advocacia Criminal", "Oficinas"],
        "composicao": "organic-editorial",
        "navegacao": "soft-top-bar",
        "densidade": "baixa",
        "tipografia": {
            "display": "DM Serif Display",
            "body": "Inter",
            "labels": "Inter",
            "escala": "moderada",
        },
        "paleta": {
            "estilo": "creme-sage-carvao",
            "sugestoes": {
                "fundo": "#F7F5EB",
                "superficie": "#F0EDE1",
                "texto": "#202A2D",
                "texto_secundario": "#5C675B",
                "acento": "#9EA682",
                "linha": "rgba(32, 42, 45, 0.12)",
            },
        },
    },
    "normal-is-boring": {
        "nome": "Normal is Boring",
        "nicho": "Psicologia e neurodesenvolvimento",
        "descricao": "Editorial de psicologia em linho e carvão, com Playfair Display. HTML de referência em referencias/templates/normal-is-boring.html.",
        "tags": ["psicologia", "editorial", "linho", "template"],
        "nichos_recomendados": ["Psicologia", "Neurodesenvolvimento", "Terapia", "Psicanálise"],
        "nichos_evitar": ["Oficinas Mecânicas", "Varejo Agressivo"],
        "composicao": "editorial-manifesto",
        "navegacao": "chapter-index",
        "densidade": "baixa",
        "tipografia": {
            "display": "Playfair Display",
            "body": "Plus Jakarta Sans",
            "labels": "JetBrains Mono",
            "escala": "extrema",
        },
        "paleta": {
            "estilo": "linho-e-carvao",
            "sugestoes": {
                "fundo": "#FAF9F6",
                "superficie": "#FFFFFF",
                "texto": "#0A0A0A",
                "texto_secundario": "#7A766E",
                "acento": "#5F7666",
                "linha": "#E5E2D9",
            },
        },
    },
}


def _agora():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalizar_id(valor):
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = texto.encode("ascii", "ignore").decode()
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    if not texto or texto in {".", ".."} or len(texto) > 80:
        raise ValueError("Informe um id de tema válido (letras, números e hífen).")
    return texto


def fonte_principal(texto, padrao="Inter"):
    if not texto:
        return padrao
    parte = str(texto).split("/")[0]
    parte = re.split(r"[\(\[]", parte)[0]
    parte = re.sub(r"\b\d{3}\b", "", parte)
    parte = re.sub(r"[^A-Za-z0-9 \-]", "", parte).strip(" ,.-")
    return parte or padrao


def _cor(valor, padrao):
    if not valor:
        return padrao
    achado = re.search(r"#[0-9A-Fa-f]{6}", str(valor))
    if achado:
        return achado.group(0)
    curto = re.search(r"#[0-9A-Fa-f]{3}\b", str(valor))
    if not curto:
        return padrao
    h = curto.group(0)[1:]
    return "#" + "".join(ch * 2 for ch in h)


def _luma(hex_cor):
    h = _cor(hex_cor, "#FFFFFF")
    r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _eh_documento_html(valor):
    if not isinstance(valor, str):
        return False
    amostra = valor.lstrip()[:200].lower()
    return amostra.startswith("<!doctype") or amostra.startswith("<html") or amostra.startswith("<head") or amostra.startswith("<body") or amostra.startswith("<!--")


def aplicar_placeholders(html, contexto):
    def trocar(match):
        chave = match.group(1)
        if chave in contexto and contexto[chave] is not None:
            return str(contexto[chave])
        return match.group(0)

    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", trocar, html or "")


def templatizar_html(html, lead):
    """Troca os dados do lead por marcadores, para o mesmo desenho servir a outro cliente."""
    if not html:
        return html
    html = re.sub(
        r"<!-- PROSPECTOR-EDITOR-START -->.*?<!-- PROSPECTOR-EDITOR-END -->",
        "",
        html,
        flags=re.S,
    )
    substituicoes = []
    nome = (lead or {}).get("nome") or ""
    cidade = (lead or {}).get("cidade") or ""
    telefone = (lead or {}).get("telefone") or ""
    whatsapp = re.sub(r"\D", "", str((lead or {}).get("whatsapp") or ""))
    endereco = (lead or {}).get("endCliente") or (lead or {}).get("endereco") or ""
    nicho = (lead or {}).get("nicho") or ""
    if len(nome) >= 4:
        substituicoes.append((nome, "{{NOME_EMPRESA}}"))
    if len(cidade) >= 3:
        substituicoes.append((cidade, "{{CIDADE}}"))
    if len(telefone) >= 8:
        substituicoes.append((telefone, "{{TELEFONE_VISUAL}}"))
    if len(whatsapp) >= 10:
        substituicoes.append((whatsapp, "{{WHATSAPP_NUMERO}}"))
    if len(endereco) >= 8:
        substituicoes.append((endereco, "{{ENDERECO}}"))
    if len(nicho) >= 4:
        substituicoes.append((nicho, "{{NICHO}}"))
    substituicoes.sort(key=lambda par: len(par[0]), reverse=True)
    for origem, destino in substituicoes:
        html = html.replace(origem, destino)
    return html


def _esc(texto):
    return (
        str(texto or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def gerar_shell(tema):
    """HTML de geração do tema, com a paleta e a tipografia dele e marcadores do lead."""
    pal = ((tema.get("paleta") or {}).get("sugestoes") or {})
    fundo = _cor(pal.get("fundo"), "#F7F5F2")
    superficie = _cor(pal.get("superficie"), "#FFFFFF")
    texto = _cor(pal.get("texto"), "#1C1917")
    mudo = _cor(pal.get("texto_secundario"), "#78716C")
    acento = _cor(pal.get("acento"), "#1C1917")
    linha = pal.get("linha") or "rgba(0,0,0,0.12)"
    if not isinstance(linha, str) or "<" in linha or ">" in linha or ";" in linha:
        linha = "rgba(0,0,0,0.12)"
    tipo = tema.get("tipografia") or {}
    display = fonte_principal(tipo.get("display"), "Newsreader")
    body = fonte_principal(tipo.get("body"), "Inter")
    tinta_botao = "#1A1A1A" if _luma(acento) > 0.62 else "#FFFFFF"
    escuro = _luma(fundo) < 0.45
    densidade = tema.get("densidade") or "media"
    folga = {"baixa": "88px", "alta": "48px"}.get(densidade, "64px")
    familia_display = display.replace(" ", "+")
    familia_body = body.replace(" ", "+")
    nome = _esc(tema.get("nome") or tema.get("id"))
    composicao = _esc(tema.get("composicao") or "editorial")
    tema_id = _esc(tema.get("id") or "")
    marcadores = ", ".join("{{" + item + "}}" for item in PLACEHOLDERS)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{{{NOME_EMPRESA}}}} | {{{{NICHO}}}}</title>
  <meta name="description" content="{{{{NOME_EMPRESA}}}} — {{{{NICHO}}}} em {{{{CIDADE}}}}.">
  <!--
    Tema Aholic: {tema_id}
    Marcadores preenchidos pelo gerador: {marcadores}
  -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family={familia_display}:wght@500;600;700&family={familia_body}:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --fundo: {fundo};
      --superficie: {superficie};
      --texto: {texto};
      --mudo: {mudo};
      --acento: {acento};
      --linha: {linha};
      --tinta-botao: {tinta_botao};
      --display: "{display}", Georgia, serif;
      --body: "{body}", "Segoe UI", sans-serif;
      --folga: {folga};
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--fundo);
      color: var(--texto);
      font-family: var(--body);
      font-size: 16px;
      line-height: 1.6;
    }}
    img {{ max-width: 100%; display: block; }}
    a {{ color: inherit; }}
    .barra {{
      display: flex; justify-content: space-between; align-items: center; gap: 16px;
      padding: 18px 7vw; border-bottom: 1px solid var(--linha);
      position: sticky; top: 0; background: var(--fundo);
    }}
    .marca {{ display: flex; align-items: center; gap: 12px; text-decoration: none; font-weight: 600; }}
    .monograma {{
      width: 42px; height: 42px; display: grid; place-items: center;
      border: 1px solid var(--linha); border-radius: 50%; font-family: var(--display);
    }}
    .marca small {{ display: block; color: var(--mudo); font-weight: 500; letter-spacing: .14em; text-transform: uppercase; font-size: 10px; }}
    .cta {{
      background: var(--acento); color: var(--tinta-botao); text-decoration: none;
      padding: 12px 18px; border-radius: 999px; font-weight: 600; font-size: 14px;
    }}
    .hero {{ display: grid; grid-template-columns: 1.1fr .9fr; gap: 40px; align-items: center; padding: var(--folga) 7vw; }}
    .selo {{ letter-spacing: .16em; text-transform: uppercase; font-size: 11px; color: var(--mudo); margin: 0 0 14px; }}
    h1 {{ font-family: var(--display); font-weight: 600; font-size: clamp(40px, 6vw, 76px); line-height: .95; letter-spacing: -.03em; margin: 0 0 16px; }}
    .hero p {{ max-width: 38rem; color: var(--mudo); margin: 0 0 22px; }}
    .foto {{ min-height: 420px; background: var(--superficie) center/cover no-repeat; border-radius: 18px; }}
    .grade {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; padding: 0 7vw  var(--folga); }}
    .card {{ background: var(--superficie); border: 1px solid var(--linha); border-radius: 16px; padding: 22px; }}
    .card span {{ display: block; font-size: 12px; letter-spacing: .14em; text-transform: uppercase; color: var(--mudo); margin-bottom: 8px; }}
    .card h2 {{ font-family: var(--display); font-size: 28px; margin: 0; font-weight: 600; }}
    .galeria {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; padding: 0 7vw var(--folga); }}
    .galeria figure {{ margin: 0; }}
    .galeria img {{ width: 100%; height: 240px; object-fit: cover; border-radius: 12px; }}
    .bio {{ margin: 0 7vw var(--folga); padding: 28px; border-top: 1px solid var(--linha); border-bottom: 1px solid var(--linha); font-family: var(--display); font-size: clamp(22px, 3vw, 34px); line-height: 1.25; }}
    footer {{ display: flex; justify-content: space-between; gap: 18px; flex-wrap: wrap; padding: 28px 7vw 48px; color: var(--mudo); font-size: 14px; }}
    @media (max-width: 860px) {{
      .hero, .grade, .galeria {{ grid-template-columns: 1fr; }}
      .barra {{ padding: 14px 20px; }}
      .hero, .grade, .galeria, .bio, footer {{ padding-left: 20px; padding-right: 20px; }}
    }}
  </style>
</head>
<body data-tema="{tema_id}" data-escuro="{str(escuro).lower()}">
  <header class="barra">
    <a class="marca" href="#topo">{{{{LOGO_HTML}}}}<span>{{{{NOME_EMPRESA}}}}<small>{composicao}</small></span></a>
    <a class="cta" href="{{{{WHATSAPP_LINK}}}}">Chamar no WhatsApp</a>
  </header>
  <main id="topo">
    <section class="hero">
      <div>
        <p class="selo">{{{{CIDADE}}}} · {nome}</p>
        <h1>{{{{NOME_EMPRESA}}}}</h1>
        <p>{{{{BIO_INSTAGRAM}}}}</p>
        <a class="cta" href="{{{{WHATSAPP_LINK}}}}">Agendar com {{{{NOME_EMPRESA}}}}</a>
      </div>
      <div class="foto" style="background-image:url('{{{{FOTO_HERO}}}}')" role="img" aria-label="{{{{NOME_EMPRESA}}}}"></div>
    </section>
    <section class="grade">
      <article class="card"><span>01</span><h2>{{{{NICHO}}}}</h2></article>
      <article class="card"><span>02</span><h2>{{{{AVALIACOES_NOTA}}}} · {{{{AVALIACOES_QTD}}}} avaliações</h2></article>
      <article class="card"><span>03</span><h2>{{{{TELEFONE_VISUAL}}}}</h2></article>
    </section>
    <section class="galeria">{{{{GALERIA_FOTOS_HTML}}}}</section>
    <p class="bio">{{{{NICHO}}}} em {{{{CIDADE}}}}.</p>
  </main>
  <footer>
    <div>{{{{ENDERECO}}}}</div>
    <div>{{{{WHATSAPP_NUMERO}}}}</div>
  </footer>
</body>
</html>
"""


class Biblioteca:
    def __init__(self, raiz):
        self.raiz = Path(raiz).resolve()
        self.pasta = self.raiz / "temas"
        self.caminho = self.pasta

    def _tem_pastas(self):
        return self.pasta.exists() and any(self.pasta.glob("*/theme.json"))

    def garantir(self):
        if not self._tem_pastas():
            self.reindexar(preservar_personalizados=False)
        return self

    def listar(self):
        self.garantir()
        temas = self._temas()
        novos = self._templates_ausentes(temas)
        if novos:
            for tema in novos:
                self._materializar_html(tema)
            temas = temas + novos
            self._gravar_catalogo(temas)
        return temas

    def resolver(self, id_ou_alias):
        if not id_ou_alias or str(id_ou_alias).strip().lower() == "auto":
            return None
        chave = str(id_ou_alias).strip().lower().replace("_", "-")
        bruto = str(id_ou_alias).strip().lower()
        for tema in self.listar():
            if tema.get("id") == bruto or tema.get("id") == chave:
                return tema
            aliases = [str(a).lower() for a in tema.get("aliases") or []]
            if bruto in aliases or chave in aliases or bruto.replace("_", "-") in aliases:
                return tema
        return None

    def escolher(self, nicho):
        n = (nicho or "").lower()
        temas = [t for t in self.listar() if t.get("ativo") is not False]
        melhor = None
        melhor_score = 0
        for tema in temas:
            score = self._pontuar(tema, n)
            if score > melhor_score:
                melhor, melhor_score = tema, score
        if melhor and melhor_score >= 8:
            return melhor["id"]
        for chaves, tid in REGRAS_NICHO:
            if n and any(k in n for k in chaves):
                tema = self.resolver(tid)
                if tema and tema.get("ativo") is not False:
                    return tema["id"]
        return None

    def salvar(self, dados, html=None):
        if not isinstance(dados, dict):
            raise ValueError("Tema inválido.")
        dados = dict(dados)
        documento = html if _eh_documento_html(html) else None
        if documento is None and _eh_documento_html(dados.get("html")):
            documento = dados.get("html")
        tid = normalizar_id(dados.get("id") or dados.get("nome"))
        nome = str(dados.get("nome") or "").strip()
        if not nome:
            raise ValueError("Informe o nome do tema.")
        if documento is not None and len(documento) > 1_500_000:
            raise ValueError("O HTML do tema passa de 1,5 MB.")
        motor_pedido = dados.get("motor") if dados.get("motor") in MOTORES else None
        dados.pop("html", None)
        dados.pop("motor", None)
        for chave in PROTEGIDOS:
            dados.pop(chave, None)

        self.garantir()
        temas = self._temas()
        idx = next((i for i, t in enumerate(temas) if t.get("id") == tid), None)
        existente = dict(temas[idx]) if idx is not None else None
        base = dict(existente or {})
        base.update(dados)
        base["id"] = tid
        base["nome"] = nome
        if "ativo" in dados:
            base["ativo"] = bool(dados.get("ativo"))
        else:
            base["ativo"] = True if existente is None else bool(existente.get("ativo", True))
        if not base.get("nicho"):
            recs = base.get("nichos_recomendados") or []
            base["nicho"] = recs[0] if recs else "Geral"
        if "descricao" not in base or base.get("descricao") is None:
            base["descricao"] = ""
        base["atualizado_em"] = _agora()
        base.setdefault("criado_em", base["atualizado_em"])
        base["aliases"] = list((existente or {}).get("aliases") or [])
        for chave in ("arquetipo", "referencia_local", "paleta_arquetipo", "fontes", "html_referencia"):
            if existente and existente.get(chave) and not base.get(chave):
                base[chave] = existente.get(chave)
        if existente and existente.get("fontes"):
            base["fontes"] = list(existente["fontes"])
        else:
            base["fontes"] = list(base.get("fontes") or ["dashboard"])
        if "dashboard" not in base["fontes"] and documento:
            base["fontes"] = base["fontes"] + ["dashboard"]

        personalizado = bool(existente and existente.get("html_personalizado"))
        if documento is not None:
            rel = self._gravar_documento(tid, documento)
            base["html"] = rel
            base["html_geracao"] = rel
            base["preview"] = rel
            base["html_personalizado"] = True
            base["motor"] = "template"
        else:
            base["html_personalizado"] = personalizado
            if existente and existente.get("motor") in MOTORES:
                base["motor"] = existente["motor"]
            elif motor_pedido:
                base["motor"] = motor_pedido
            else:
                base["motor"] = "template"
            if not personalizado:
                self._materializar_html(base)
            else:
                for chave in ("html", "preview", "html_geracao", "html_referencia"):
                    if existente and existente.get(chave):
                        base[chave] = existente[chave]
        self._atualizar_tokens(base)
        if idx is None:
            temas.append(base)
        else:
            temas[idx] = base
        self._gravar_catalogo(temas)
        self._sincronizar_legado(base)
        return base

    def salvar_de_site(self, slug, nome_tema, html, lead):
        documento = templatizar_html(html or "", lead or {})
        if not _eh_documento_html(documento):
            raise ValueError("O editor não enviou um HTML.")
        nicho = (lead or {}).get("nicho") or ""
        dados = {
            "id": normalizar_id(nome_tema or slug or "tema-salvo"),
            "nome": (nome_tema or slug or "Tema salvo").strip(),
            "descricao": "Tema salvo a partir do site {0}.".format(slug or "editor"),
            "nicho": nicho or "Geral",
            "nichos_recomendados": [nicho] if nicho else [],
            "origem": "sites/{0}".format(slug) if slug else "editor",
            "tags": ["salvo", "editor"],
            "ativo": True,
            "composicao": "salvo-no-editor",
            "densidade": "media",
        }
        return self.salvar(dados, html=documento)

    def renderizar(self, tema, contexto):
        if not tema:
            return ""
        html = self.ler_html_geracao(tema)
        if not html:
            return ""
        return aplicar_placeholders(html, contexto or {})

    def ler_html_geracao(self, tema):
        if tema.get("html_personalizado"):
            return self._ler_rel(tema.get("html"))
        bruto = self._ler_rel(tema.get("html"))
        if bruto and "{{NOME_EMPRESA}}" in bruto:
            return bruto
        gerado = self._ler_rel(tema.get("html_geracao"))
        if gerado:
            return gerado
        return bruto

    def ler_preview(self, tema):
        return self._ler_rel(tema.get("preview")) or self.ler_html_geracao(tema) or gerar_shell(tema)

    def como_preset_dinamico(self, tema):
        tokens = tema.get("tokens") or {}
        pal = ((tema.get("paleta") or {}).get("sugestoes") or {})
        fonts = tokens.get("fonts") or {}
        display = fonts.get("display") or fonte_principal((tema.get("tipografia") or {}).get("display"))
        body = fonts.get("body") or fonte_principal((tema.get("tipografia") or {}).get("body"))
        defaults = tokens.get("defaults") or {
            "--ah-primary": pal.get("acento") or "#1C1917",
            "--ah-accent": pal.get("acento") or "#1C1917",
            "--ah-bg": pal.get("fundo") or "#FBFBFA",
            "--ah-surface": pal.get("superficie") or "#FFFFFF",
            "--ah-text": pal.get("texto") or "#18181B",
            "--ah-text-muted": pal.get("texto_secundario") or "#71717A",
        }
        nichos = tokens.get("nichos")
        if not nichos:
            nichos = [str(n).lower() for n in (tema.get("nichos_recomendados") or [])]
        return {
            "name": tema.get("nome"),
            "nichos": nichos,
            "fonts": {"display": display, "body": body},
            "dark": bool(tokens.get("dark", _luma(pal.get("fundo") or "#FFFFFF") < 0.45)),
            "defaults": defaults,
            "motion": tokens.get("motion") or {},
            "layout": tokens.get("layout") or tema.get("composicao") or "",
            "description": tema.get("descricao") or "",
        }

    def reindexar(self, preservar_personalizados=True):
        antigo = {}
        if preservar_personalizados and self._tem_pastas():
            for tema in self._temas():
                antigo[tema.get("id")] = tema
        temas = self._construir_de_fontes()
        ids = {t["id"] for t in temas}
        if preservar_personalizados:
            for tid, tema in antigo.items():
                if tema.get("html_personalizado"):
                    temas = [tema if t["id"] == tid else t for t in temas]
                    if tid not in ids:
                        temas.append(tema)
                        ids.add(tid)
                elif tid not in ids:
                    temas.append(tema)
                    ids.add(tid)
        for tema in temas:
            if not tema.get("html_personalizado"):
                self._materializar_html(tema)
        self._gravar_catalogo(temas)
        return temas

    def _construir_de_fontes(self):
        visuais = self._ler_json("referencias/presets-visuais.json", [])
        dinamicos = self._ler_json("referencias/presets-dinamicos.json", {})
        catalogo = self._ler_json("referencias/catalogo-design.json", {})
        if not isinstance(visuais, list):
            visuais = []
        if not isinstance(dinamicos, dict):
            dinamicos = {}
        arquetipos = (catalogo or {}).get("arquetipos") or {}
        temas = []
        for preset in visuais:
            if not isinstance(preset, dict) or not preset.get("id"):
                continue
            tema = dict(preset)
            din = dinamicos.get(preset["id"]) or {}
            tema["nicho"] = (preset.get("nichos_recomendados") or ["Geral"])[0]
            tema["tokens"] = self._tokens_de_dinamico(din, tema)
            tema["fontes"] = ["presets-visuais"] + (["presets-dinamicos"] if din else [])
            tema["aliases"] = list(ALIASES_EXTRAS.get(preset["id"], []))
            tema["motor"] = "template"
            tema["html_personalizado"] = False
            tema["arquetipo"] = None
            temas.append(tema)

        ids = {t["id"] for t in temas}
        for stem, meta in TEMPLATES_CONHECIDOS.items():
            if stem in ids:
                continue
            tema = dict(meta)
            tema["id"] = stem
            tema["origem"] = "referencias/templates/{0}.html".format(stem)
            tema["fontes"] = ["templates"]
            tema["aliases"] = []
            tema["motor"] = "template"
            tema["html_personalizado"] = False
            tema["arquetipo"] = None
            tema["tokens"] = self._tokens_de_dinamico({}, tema)
            ref = self.raiz / "referencias" / "templates" / "{0}.html".format(stem)
            if ref.exists():
                tema["html_referencia"] = "referencias/templates/{0}.html".format(stem)
            temas.append(tema)
            ids.add(stem)

        for aid, arq in arquetipos.items():
            if not isinstance(arq, dict):
                continue
            lig = dict(LIGACAO_ARQUETIPO.get(aid) or {})
            tema_id = arq.get("tema_id") or lig.get("tema_id")
            if not tema_id:
                continue
            tema_id = normalizar_id(tema_id)
            motor = lig.get("motor") or "template"
            aliases = list(lig.get("aliases") or [])
            if tema_id not in ids:
                paleta = _paleta_de_arquetipo(arq)
                tema = {
                    "id": tema_id,
                    "nome": re.sub(r"^[^\w]+", "", arq.get("nome") or tema_id).strip() or tema_id,
                    "descricao": arq.get("nome") or "",
                    "nicho": (arq.get("nichos") or ["Geral"])[0],
                    "nichos_recomendados": list(arq.get("nichos") or []),
                    "tipografia": {
                        "display": (arq.get("tipografia") or {}).get("titulos") or "Inter",
                        "body": (arq.get("tipografia") or {}).get("corpo") or "Inter",
                        "labels": "JetBrains Mono",
                    },
                    "paleta": paleta,
                    "fontes": ["catalogo-design"],
                    "aliases": [],
                    "motor": motor,
                    "html_personalizado": False,
                    "ativo": True,
                    "origem": "referencias/catalogo-design.json",
                }
                tema["tokens"] = self._tokens_de_dinamico({}, tema)
                temas.append(tema)
                ids.add(tema_id)
            for tema in temas:
                if tema["id"] != tema_id:
                    continue
                tema["arquetipo"] = aid
                tema["motor"] = motor
                atuais = list(tema.get("aliases") or [])
                for alias in aliases:
                    if alias not in atuais and alias != tema_id:
                        atuais.append(alias)
                tema["aliases"] = atuais
                if arq.get("referencia_local"):
                    tema["referencia_local"] = arq["referencia_local"]
                tema["paleta_arquetipo"] = _paleta_de_arquetipo(arq)
                fontes = list(tema.get("fontes") or [])
                if "catalogo-design" not in fontes:
                    fontes.append("catalogo-design")
                tema["fontes"] = fontes
                break
        return temas

    def _materializar_html(self, tema):
        tid = tema["id"]
        pasta = self.pasta / tid
        pasta.mkdir(parents=True, exist_ok=True)
        casca = gerar_shell(tema)
        (pasta / "casca.html").write_text(casca, encoding="utf-8", newline="\n")
        preview = casca
        if tema.get("html_referencia"):
            origem = self._caminho_seguro(tema["html_referencia"])
            if origem.exists():
                preview = origem.read_text(encoding="utf-8", errors="replace")
        (pasta / "preview.html").write_text(preview, encoding="utf-8", newline="\n")
        tema["html"] = "temas/{0}/casca.html".format(tid)
        tema["html_geracao"] = tema["html"]
        tema["preview"] = "temas/{0}/preview.html".format(tid)
        return tema

    def _templates_ausentes(self, temas):
        pasta = self.raiz / "referencias" / "templates"
        if not pasta.exists():
            return []
        referencias = set()
        ids = set()
        aliases = set()
        for tema in temas:
            ids.add(tema.get("id"))
            aliases.update(str(a).lower() for a in tema.get("aliases") or [])
            for chave in ("html", "preview", "html_referencia", "html_geracao"):
                if tema.get(chave):
                    referencias.add(str(tema[chave]).replace("\\", "/"))
        novos = []
        for arq in sorted(pasta.glob("*.html")):
            if arq.name.startswith("capa-"):
                continue
            rel = "referencias/templates/{0}".format(arq.name)
            if rel in referencias or arq.stem in ids or arq.stem.lower() in aliases:
                continue
            titulo = _titulo_html(arq.read_text(encoding="utf-8", errors="replace"))
            tema = {
                "id": normalizar_id(arq.stem),
                "nome": titulo or arq.stem.replace("-", " ").title(),
                "descricao": "Template HTML incorporado de {0}.".format(rel),
                "nicho": "Geral",
                "nichos_recomendados": ["Geral"],
                "origem": rel,
                "fontes": ["templates"],
                "aliases": [],
                "motor": "template",
                "html_personalizado": False,
                "html_referencia": rel,
                "ativo": True,
                "tags": ["template"],
                "tipografia": {"display": "Newsreader", "body": "Inter", "labels": "JetBrains Mono"},
                "paleta": {
                    "estilo": "template",
                    "sugestoes": {
                        "fundo": "#F7F5F2",
                        "superficie": "#FFFFFF",
                        "texto": "#1C1917",
                        "texto_secundario": "#78716C",
                        "acento": "#1C1917",
                    },
                },
            }
            tema["tokens"] = self._tokens_de_dinamico({}, tema)
            novos.append(tema)
        return novos

    def _atualizar_tokens(self, tema):
        tokens = dict(tema.get("tokens") or {})
        pal = ((tema.get("paleta") or {}).get("sugestoes") or {})
        defaults = dict(tokens.get("defaults") or {})
        if pal.get("acento"):
            defaults["--ah-primary"] = pal["acento"]
            defaults["--ah-accent"] = pal["acento"]
        if pal.get("fundo"):
            defaults["--ah-bg"] = pal["fundo"]
        if pal.get("superficie"):
            defaults["--ah-surface"] = pal["superficie"]
        if pal.get("texto"):
            defaults["--ah-text"] = pal["texto"]
        if pal.get("texto_secundario"):
            defaults["--ah-text-muted"] = pal["texto_secundario"]
        fonts = dict(tokens.get("fonts") or {})
        tipo = tema.get("tipografia") or {}
        if tipo.get("display"):
            fonts["display"] = fonte_principal(tipo.get("display"))
        if tipo.get("body"):
            fonts["body"] = fonte_principal(tipo.get("body"))
        fonts.setdefault("display", "Inter")
        fonts.setdefault("body", "Inter")
        tokens["fonts"] = fonts
        tokens["defaults"] = defaults
        tokens["layout"] = tokens.get("layout") or tema.get("composicao") or ""
        tokens["dark"] = _luma(pal.get("fundo") or "#FFFFFF") < 0.45
        if not tokens.get("nichos"):
            tokens["nichos"] = [str(n).lower() for n in (tema.get("nichos_recomendados") or [])]
        tema["tokens"] = tokens

    def _tokens_de_dinamico(self, din, tema):
        if din:
            return {
                "name": din.get("name"),
                "nichos": din.get("nichos") or [],
                "fonts": din.get("fonts") or {},
                "dark": din.get("dark"),
                "defaults": din.get("defaults") or {},
                "motion": din.get("motion") or {},
                "layout": din.get("layout") or "",
                "description": din.get("description") or "",
            }
        copia = dict(tema)
        copia["tokens"] = {}
        self._atualizar_tokens(copia)
        return copia["tokens"]

    def _sincronizar_legado(self, tema):
        visual = self.raiz / "referencias" / "presets-visuais.json"
        if visual.exists():
            try:
                lista = json.loads(visual.read_text(encoding="utf-8"))
            except Exception:
                lista = None
            if isinstance(lista, list):
                proj = self._projetar_visual(tema)
                achou = False
                for i, item in enumerate(lista):
                    if isinstance(item, dict) and item.get("id") == tema["id"]:
                        lista[i] = proj
                        achou = True
                        break
                if not achou:
                    lista.append(proj)
                self._atomic_json(visual, lista)
        dinamico = self.raiz / "referencias" / "presets-dinamicos.json"
        if dinamico.exists():
            try:
                mapa = json.loads(dinamico.read_text(encoding="utf-8"))
            except Exception:
                mapa = None
            if isinstance(mapa, dict):
                mapa[tema["id"]] = self.como_preset_dinamico(tema)
                self._atomic_json(dinamico, mapa)

    def _projetar_visual(self, tema):
        proj = {}
        for chave, valor in tema.items():
            if chave in {
                "tokens", "html_geracao", "html_referencia", "paleta_arquetipo",
                "fontes", "atualizado_em", "criado_em",
            }:
                continue
            proj[chave] = valor
        return proj

    def _pontuar(self, tema, nicho):
        if not nicho:
            return 0
        score = 0
        for item in tema.get("nichos_recomendados") or []:
            il = str(item).lower().strip()
            if not il:
                continue
            if il == nicho:
                score += 40
            elif il in nicho or nicho in il:
                score += 12
            else:
                for token in re.split(r"[^a-z0-9áéíóúãõâêôç]+", il):
                    if len(token) >= 5 and token in nicho:
                        score += 5
        for item in tema.get("nichos_evitar") or []:
            il = str(item).lower()
            if il and (il in nicho or nicho in il):
                score -= 12
        if tema.get("ativo") is False:
            score -= 100
        return score

    def _gravar_documento(self, tid, documento):
        rel = "temas/{0}/casca.html".format(tid)
        caminho = self._caminho_seguro(rel)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(documento, encoding="utf-8", newline="\n")
        (caminho.parent / "preview.html").write_text(documento, encoding="utf-8", newline="\n")
        return rel

    def _gravar_catalogo(self, temas):
        self.pasta.mkdir(parents=True, exist_ok=True)
        diretrizes = self._ler_json("temas/diretrizes.json", {})
        if not isinstance(diretrizes, dict) or not diretrizes.get("diretrizes_anti_slop"):
            bruto = self._ler_json("referencias/catalogo-design.json", {})
            diretrizes = {
                "descricao": "A biblioteca viva é a pasta temas/<id>/. Os JSON em referencias/ são a origem histórica.",
                "diretrizes_anti_slop": bruto.get("diretrizes_anti_slop") or [],
                "placeholders": PLACEHOLDERS,
            }
        diretrizes["atualizado_em"] = _agora()
        diretrizes["placeholders"] = PLACEHOLDERS
        self._atomic_json(self.pasta / "diretrizes.json", diretrizes)
        mantidos = set()
        for ordem, tema in enumerate(temas):
            tema = dict(tema)
            tema["ordem"] = ordem
            tema["html"] = "temas/{0}/casca.html".format(tema["id"])
            tema["html_geracao"] = tema["html"]
            tema["preview"] = "temas/{0}/preview.html".format(tema["id"])
            pasta = self.pasta / tema["id"]
            pasta.mkdir(parents=True, exist_ok=True)
            self._atomic_json(pasta / "theme.json", tema)
            mantidos.add(tema["id"])
            temas[ordem] = tema
        for pasta in list(self.pasta.iterdir()):
            if pasta.is_dir() and pasta.name not in mantidos and (pasta / "theme.json").exists():
                shutil.rmtree(pasta)

    def _temas(self):
        if not self.pasta.exists():
            return []
        temas = []
        for pasta in self.pasta.iterdir():
            arquivo = pasta / "theme.json"
            if not pasta.is_dir() or not arquivo.exists():
                continue
            try:
                tema = json.loads(arquivo.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(tema, dict) and tema.get("id"):
                temas.append(tema)
        temas.sort(key=lambda t: (t.get("ordem", 9999), t.get("id") or ""))
        return temas

    def _ler_json(self, rel, padrao):
        caminho = self.raiz / rel
        if not caminho.exists():
            return padrao
        try:
            return json.loads(caminho.read_text(encoding="utf-8"))
        except Exception:
            return padrao

    def _ler_rel(self, rel):
        caminho = self._caminho_seguro(rel) if rel else None
        if not caminho or not caminho.exists() or not caminho.is_file():
            return ""
        return caminho.read_text(encoding="utf-8")

    def _caminho_seguro(self, rel):
        if not rel or not isinstance(rel, str):
            raise ValueError("Caminho de tema inválido.")
        limpo = rel.replace("\\", "/").lstrip("/")
        if not limpo or ".." in limpo.split("/"):
            raise ValueError("Caminho de tema inválido.")
        caminho = (self.raiz / limpo).resolve()
        caminho.relative_to(self.raiz)
        return caminho

    def _atomic_json(self, caminho, obj):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        tmp = caminho.with_suffix(caminho.suffix + ".tmp")
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(tmp, caminho)


def _paleta_de_arquetipo(arq):
    p = arq.get("paleta") or {}
    return {
        "estilo": "arquetipo",
        "sugestoes": {
            "fundo": _cor(p.get("fundo"), "#FBFBFA"),
            "superficie": _cor(p.get("superficie"), "#FFFFFF"),
            "texto": _cor(p.get("texto_principal") or p.get("texto"), "#18181B"),
            "texto_secundario": _cor(p.get("texto_secundario"), "#71717A"),
            "acento": _cor(p.get("acento"), "#C5A880"),
        },
    }


def _titulo_html(html):
    achado = re.search(r"<title>(.*?)</title>", html or "", flags=re.I | re.S)
    if not achado:
        return ""
    titulo = re.sub(r"\s+", " ", achado.group(1)).strip()
    titulo = re.split(r"[|•·]", titulo)[0].strip()
    return titulo[:80]


def main():
    import argparse
    import sys

    if sys.platform.startswith("win"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raiz = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Biblioteca única de temas da Aholic")
    parser.add_argument("--list", action="store_true", help="Lista os temas do catálogo")
    parser.add_argument("--reindex", action="store_true", help="Reconstrói o catálogo a partir dos presets, arquétipos e templates, preservando HTML salvo")
    args = parser.parse_args()
    bib = Biblioteca(raiz)
    if args.reindex or not bib._tem_pastas():
        temas = bib.reindexar(preservar_personalizados=bib._tem_pastas())
        print("Temas gravados em {0} ({1} temas).".format(bib.pasta, len(temas)))
    if args.list or not args.reindex:
        for tema in bib.listar():
            estado = "HTML salvo" if tema.get("html_personalizado") else tema.get("motor") or "template"
            print("{0:32}  {1}  —  {2}  [{3}]".format(tema["id"], tema.get("nome"), tema.get("nicho") or "Geral", estado))


if __name__ == "__main__":
    main()
