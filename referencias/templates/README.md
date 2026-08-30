# Presets & Templates de Sites da Aholic

Esta pasta foi projetada para receber novos templates e presets de sites criados pela AHOLIC DIGITAL.

## Como adicionar um novo Preset HTML

Basta salvar um arquivo `.html` nesta pasta com o nome do preset (ex: `luxo-minimalista.html`, `dark-impacto.html`).
O gerador automático (`scripts/gerar-site-lead.py`) irá reconhecê-lo dinamicamente no menu e injetar os dados do lead minerado usando as seguintes variáveis:

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
