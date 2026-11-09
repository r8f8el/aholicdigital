# Aholic Digital

Painel local para acompanhar leads e gerar a página que será mostrada ao cliente. A biblioteca de temas fica em `temas/`. Cada tema é uma pasta:

- `temas/<id>/theme.json` — nome, nicho, tokens e metadados
- `temas/<id>/casca.html` — HTML que o gerador preenche com os dados do lead
- `temas/<id>/preview.html` — prévia do visual

Os arquivos em `referencias/` (presets, arquétipos e templates) são a origem histórica. O painel e o gerador não escolhem tema por eles.

`sites/` guarda as páginas geradas. Não é código do produto. Scripts feitos para um cliente só estão em `jobs/clientes/`. O motor antigo de geração está em `jobs/geradores/`, só como histórico.

## Subir o painel

É preciso Python 3.11 ou mais recente. Não há pacote pip para o painel.

No Windows, dê duplo clique em `iniciar-dashboard.bat` ou, na pasta do repositório:

```bat
py dashboard-server.py
```

Abra http://localhost:8765 . Enquanto esse servidor estiver ligado, a lista de leads vem do SQLite (`prospector.db`) e o selo do painel fica **SQLite Local**. O Supabase só entra se o servidor local não responder e a URL e a chave tiverem sido salvas em Configurações.

Na aba Presets Visuais, o que você salvar passa a existir em `temas/<id>/` e reaparece depois de recarregar a página.

## Gerar um site

O atalho é `gerar-site.bat`. Ele chama um único script:

```bat
py scripts\gerar-site-lead.py --list-temas
py scripts\gerar-site-lead.py --slug slug-do-lead --preset editorial-atelier
```

`--preset auto` usa a direção criativa gravada no lead ou, se não houver, um tema da biblioteca compatível com o nicho. Um id que não existe, ou um tema sem casca, encerra com erro e não grava HTML. `scripts\aholic-generator.py` e `scripts\aholic-generator-template.py` também terminam nesse mesmo script.

A página sai em `sites\<slug>\index.html`. Sem foto do lead, a casca não inventa imagem de banco. Sem WhatsApp, o gerador não coloca telefone fictício.

## Dependências

O painel e o gerador não instalam nada. Quem for minerar no Google Maps ou no Instagram instala o que está em `requirements.txt` (`playwright`). Os scripts Node não têm dependência externa; o `package.json` só registra isso.

A sessão do Instagram fica em `config/instagram_session.json` e não entra no Git.
