# Central de Referências & Design System (Anti-Slop)

Esta pasta guarda os templates, diretrizes visuais e referências de design do ecossistema **Aholic Sites**.

## Como Usar com a IA

Ao pedir para criar ou redesenhar um site, a IDE sempre fará o briefing inteligente:
1. **Instagram do Cliente:** `@perfil` para extração de fotos reais, paleta e tom de voz.
2. **Estilo / Arquétipo:** Escolha um tema da biblioteca única em `biblioteca/catalogo.json` (os 5 arquétipos de `catalogo-design.json` estão mapeados lá) ou forneça uma URL / print de referência.
3. **Serviço Carro-Chefe:** Procedimento em destaque para o botão de conversão do WhatsApp.

## Arquivos e Pastas
- `biblioteca/catalogo.json`: catálogo único que o dashboard e o gerador leem. Cada tema tem nome, nicho, prévia e HTML.
- `catalogo-design.json`: arquétipos de origem, agora com `tema_id` apontando para a biblioteca.
- `estetica-e-saude/`: Templates e inspirações para estética, dermatologia e clínicas médicas.
- `arquitetura-e-interiores/`: Templates editoriais para arquitetura e design de alto padrão.
- `psicologia-e-bem-estar/`: Modelos acolhedores com paletas creme e orgânicas.
- `odonto/`: Modelos de tecnologia médica, implantes e odontologia digital.
- `advocacia/`: Modelos de autoridade e segurança jurídica.
