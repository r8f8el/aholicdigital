---
name: redesign-premium
description: Esta skill deve ser usada ao redesenhar o site de um cliente prospectado — criar uma versão nova, premium e de alta conversão da página existente, mantendo conteúdo, logo e paleta do cliente. Acione quando o usuário disser "redesenhar site", "melhorar página", "refazer o site do cliente", "criar site" ou pedir para redesenhar (skill redesign-premium).
---

# Criação e Redesign Premium de Páginas (Alta Conversão & Anti-Slop)

Criar uma presença digital impecável para o cliente — seja **Redesenhando um site fraco** ou **Criando o Primeiro Site Oficial do Zero** (para quem só tem Instagram/Google Maps). O cliente precisa ver a página e sentir que o negócio dele foi elevado ao padrão de estúdio de design de elite.

---

## 🛑 Etapa 0: Briefing & Presets de Direção Visual (Anti-Slop)

Antes de gerar qualquer linha de código HTML, a IA **DEVE verificar ou consultar a Direção Criativa**:

1. 🎨 **Preset de Direção Visual (`referencias/presets-visuais.json`):**
   - Verificar se o lead já possui um `creative_direction_card` gerado no dashboard.
   - Caso não possua, selecionar ou sugerir o preset mais adequado entre os 6 disponíveis:
     - 🏛️ **Editorial de Atelier** (Asymmetrical editorial, serifa nobre, respiro amplo — Arquitetura/Dermato/Luxo).
     - ⚡ **Brutalismo Comercial** (Heavy grid, tipografia display pesada, alto contraste — Barbearias/Academias/Streetwear).
     - 🗂️ **Arquivo Vivo** (Index matrix, monospace labels, dados técnicos — Advocacia/Consultoria/Perícias).
     - 🎬 **Cinema Local** (Full-bleed dark luxury, vídeo/fotos imersivas — Rejuvenescimento/Spas/Alta Gastronomia).
     - 🎨 **Cartaz Modular** (Color-blocks harmônicos, pílula flutuante, acolhedor — Psicologia/Nutrição/Bem-estar).
     - 📐 **Instrumento Digital** (Swiss design, precisão cirúrgica, confiança — Odonto Digital/Tecnologia Médica).
   - **Regra de Diversidade:** Nunca repetir a mesma receita nos últimos 3 sites do mesmo nicho sem autorização explícita.
2. 📸 **Instagram / Google Maps do Cliente:** Extrair fotos reais, logo e tom de voz autêntico.
3. 🎯 **Serviço Carro-Chefe:** Procedimento ou serviço principal a ser destacado no Hero e no botão de WhatsApp.

---

## 🚫 Diretrizes Rígidas Anti-Slop (Padrão Estúdio)

1. **PROIBIDO Gradientes Neon Clichês:** Nada de fundos roxo/ciano cyberpunk sem justificativa de marca.
2. **PROIBIDO Textos Robóticos de IA:** Nunca usar frases como "Revolucione sua jornada", "Embarque em uma experiência única", "Descubra a excelência". A copy deve ser humana, direta, focada no benefício real e nas dores do paciente/cliente.
3. **PROIBIDO Pessoas Artificiais de IA:** Usar fotos REAIS do Instagram/Google Maps do estabelecimento ou fotografia editorial limpa e natural.
4. **Informações 100% Reais:** Endereço, horários, depoimentos 5 estrelas reais do Google Maps e número de WhatsApp no formato correto (`55DDDNUMERO`).

---

## 🛠️ Design System e Especificações Técnicas

- **Framework:** HTML5 + Tailwind CSS (via CDN) + Lucide Icons + Google Fonts. Sem dependências pesadas de build.
- **Tipografia:** Fonte do arquétipo escolhido (ex: *Newsreader* + *Inter* para luxo; *Plus Jakarta Sans* para tecnologia).
- **Layout Bento Grid & Cards:** Seções organizadas em blocos elegantes com cantos arredondados (`rounded-2xl`), sombras suaves (`shadow-sm` / `shadow-xl`) e bordas sutis (`border border-slate-100` ou `border-stone-200/60`).
- **Prova Social em Destaque:** Nota real do Google Maps em destaque com estrelas douradas e depoimentos reais.
- **Conversão no WhatsApp:** Botão flutuante fixo no canto inferior direito e botões de ação contextuais (`https://wa.me/55DDDNUMERO?text=Olá! Vim pelo site e gostaria de agendar uma avaliação para [Serviço]`).
- **Página Autocontida:** Arquivo único `sites/[slug]/[slug].html` ultra-rápido, abrindo em menos de 1 segundo.
- **Editor e Comparador:** Gerar a versão editável `sites/[slug]/[slug]-editor.html` e atualizar o comparador antes/depois `comparar.html`.

---

## 📋 Checklist Final de Entrega

- [ ] Instagram do cliente consultado e fotos reais aplicadas
- [ ] Arquétipo de design respeitado (cores, tipografia e espaçamento alinhados a `referencias/catalogo-design.json`)
- [ ] Zero texto de preenchimento ou clichês de IA
- [ ] Todos os botões e CTAs com link direto para o WhatsApp no formato correto
- [ ] 100% responsivo no mobile (360px a 430px) sem rolagem horizontal
- [ ] `[slug]-editor.html` gerado e `comparar.html` atualizado
