# Presets & Templates de Sites da Aholic

Esta pasta foi projetada para receber novos templates e presets de sites criados pela AHOLIC DIGITAL.

## Como adicionar um novo Preset HTML

Salve um arquivo `.html` nesta pasta com o nome do tema (ex: `luxo-minimalista.html`).
Na próxima listagem, o dashboard e o gerador incorporam o arquivo na biblioteca `referencias/biblioteca/catalogo.json`.

Se o HTML tiver os marcadores abaixo, o gerador troca pelos dados do lead. Se for uma página fechada, sem marcadores, ela fica como prévia e a geração usa um modelo com as cores do tema — até alguém salvar um HTML próprio na biblioteca.

Marcadores:

- `{{NOME_EMPRESA}}` ou `{{NOME_LEAD}}`: Nome do cliente / clínica / especialista
- `{{NICHO}}`: Nicho de atuação (ex: Estética Avançada, Odontologia)
- `{{CIDADE}}`: Cidade do estabelecimento
- `{{WHATSAPP_NUMERO}}`: Número limpo (ex: 5564993368698)
- `{{WHATSAPP_LINK}}`: Link pronto para wa.me com mensagem inicial personalizada
- `{{TELEFONE_VISUAL}}`: Telefone formatado (ex: (64) 99336-8698)
- `{{LOGO_HTML}}`: Elemento HTML pronto da logo (ou insígnia monograma elegante)
- `{{FOTO_HERO}}`: Caminho relativo para a foto principal
- `{{FOTO_ESPECIALISTA}}`: Foto de perfil ou especialista
- `{{GALERIA_FOTOS_HTML}}`: Grade com fotos reais do feed do Instagram com hover zoom
- `{{AVALIACOES_NOTA}}`: Nota no Google (ex: 4.9 ou 5.0)
- `{{AVALIACOES_QTD}}`: Contagem de avaliações no Google
- `{{ENDERECO}}`: Endereço físico completo
- `{{BIO_INSTAGRAM}}`: Bio ou texto descritivo extraído das redes
