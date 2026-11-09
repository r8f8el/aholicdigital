# Biblioteca de temas

O dashboard (`dashboard-server.py`) e o gerador (`scripts/gerar-site-lead.py`) leem e gravam só este catálogo:

- `catalogo.json` — nome, nicho, prévia, caminhos do HTML, tokens e o restante dos metadados
- `html/<id>.html` — modelo com marcadores `{{NOME_EMPRESA}}`, `{{NICHO}}`, `{{CIDADE}}`, `{{WHATSAPP_LINK}}` e os outros listados no catálogo

Os presets visuais, os presets dinâmicos, os cinco arquétipos e os HTML de `referencias/templates/` foram mapeados para cá. Os arquivos antigos continuam no repositório como origem; a lista que o produto usa é esta.

Salvar um preset no dashboard, salvar uma cópia na prévia ou usar **Salvar tema na biblioteca** no editor do site grava o tema aqui. Ele volta na aba Presets Visuais e em `gerar-site.bat` / `--list-temas`.

Um `.html` novo em `referencias/templates/` (exceto `capa-*.html`) entra na biblioteca na próxima listagem. Se não tiver marcadores, fica como prévia e a geração usa o modelo em `html/`.
