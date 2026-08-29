# Regra de Ouro: Retenção Integral de Inspirações, Presets e Código (Anti-AI Slop)

Esta regra é de cumprimento OBRIGATÓRIO em todas as interações onde o usuário enviar inspirações visuais, links de referência, designs systems ou trechos de código para criação/redesign de sites.

---

## 1. O Princípio Anti-AI Slop (Sem Estética Genérica de IA)
Templates padrão de inteligência artificial geram layouts previsíveis e desprovidos de identidade (cards genéricos flutuantes, gradientes lilás/azul neon descontextualizados, sombras difusas pesadas e falta de ritmo visual).

Para criar sites autorais de altíssimo padrão com o impacto de marcas como **Karla Barros**, **Super Travel Luxury**, **Raw Form Brutalism**, **Cinema 3D Spatial** e **Editorial Atelier**, **TODAS as características de assinatura visual DEVEM ser guardadas e aplicadas sem simplificação ou compressão excessiva.**

---

## 2. Protocolo de Extração de Inspiração e Presets
Sempre que o usuário enviar um código, URL ou descrição de inspiração:

### A. Extração Obrigatória dos 5 Pilares de Assinatura Técnica:
1. **Tipografia Pura & Pesos Específicos**:
   - Fontes exatas (ex: *League Spartan 900*, *Clash Display 700*, *Anton*, *Newsreader Serif*, *Plus Jakarta Sans*, *JetBrains Mono*).
   - Regras de contraste (ex: títulos maiúsculos com tracking ultracompacto `-0.05em` e **1 palavra em itálico minúsculo** para quebrar o ritmo editorial).
2. **Composição & Ritmo de Grid**:
   - Offsets deliberados (ex: `.stagger-grid .stagger-item:nth-child(even) { margin-top: 100px; }`).
   - Assimetria intencional, caixas de manifesto, cartazes verticais e linhas de 1px.
3. **Microinterações, Transições & Curvas Bezier**:
   - Curvas de easing de alta-costura: `cubic-bezier(0.16, 1, 0.3, 1)`.
   - Transições de imagem: `filter: grayscale(100%)` -> `filter: grayscale(0%)` + `transform: scale(1.08)` em `1.0s`.
   - Transição suave de preenchimento de cor em cards (ex: `0.7s` com inversão de contraste no hover).
4. **Componentes Proprietários de Assinatura**:
   - Selo flutuante de concierge / autoridade com animação contínua lenta (`@keyframes bounce-slow 4s ease-in-out infinite`).
   - Círculo de ação no hover dos cards com zoom e texto (*"VER PROJETO ↗"*).
   - Ticker marquee infinito em alta velocidade, blocos com manchas gradientes em `mix-blend-mode: multiply` ou janelas interativas estilo macOS.
5. **Paleta Harmônica & Superfícies**:
   - Cores primárias, superfícies, fundos linho/dusty/obsidiana e cores de acento com seus códigos Hex precisos.

---

## 3. Armazenamento e Persistência nos Presets
Ao salvar um preset em `referencias/presets-visuais.json` ou no painel:
- **NÃO** guardar apenas rótulos genéricos.
- Armazenar o campo `blueprint_prompt` e `codigo_css` contendo os snippets reais de CSS e classes que a IA deve replicar.
- O botão **"📋 Copiar Prompt"** do painel deve sempre fornecer a diretriz técnica completa com código CSS, regras de microinteração e restrições anti-slop expressas.

---

## 4. Checklist Obrigatório ao Construir Qualquer Site:
- [ ] O site possui a curva bezier de transição suave do preset?
- [ ] As imagens possuem o tratamento de assinatura (ex: Grayscale para Cor + Zoom suave)?
- [ ] A quebra de grid (Stagger offset ou modularidade) foi aplicada?
- [ ] O selo flutuante ou elemento de impacto do Hero foi incluído?
- [ ] O site está livre de layouts genéricos de IA (*Anti-AI Slop*)?
