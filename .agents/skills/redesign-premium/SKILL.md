---
name: redesign-premium
description: Esta skill deve ser usada ao redesenhar o site de um cliente prospectado — criar uma versão nova, premium e de alta conversão da página existente, mantendo conteúdo, logo e paleta do cliente. Acione quando o usuário disser "redesenhar site", "melhorar página", "refazer o site do cliente" ou pedir para redesenhar (skill redesign-premium).
---

# Criação e Redesign Premium de Páginas (Alta Conversão)

Criar uma presença digital impecável para o cliente — seja **Redesenhando um site fraco** ou **Criando o Primeiro Site Oficial do Zero** (para quem só tem Instagram/Google Maps). O cliente precisa ver a página e sentir que o negócio dele foi elevado ao padrão mais alto do mercado.

## Regras Invioláveis de Construção

1. **Informações 100% Reais:** Todos os dados (nome, serviços, depoimentos 5 estrelas, fotos, endereço, horários, WhatsApp) vêm de fontes reais (site antigo, Google Maps ou Instagram). Nunca invente fatos ou avaliações falsas.
2. **Design System Moderno e Limpo:**
   - **Framework:** HTML5 + Tailwind CSS (via CDN) + Lucide Icons + Google Fonts. Sem dependências pesadas de build.
   - **Tipografia:** Fonte premium moderna (*Plus Jakarta Sans*, *Outfit* ou *Inter* para corpo; *Playfair Display* opcional para nichos de luxo/médico/direito).
   - **Layout Bento Grid & Cards:** Seções organizadas em blocos elegantes com cantos arredondados (`rounded-2xl`), sombras suaves (`shadow-sm` / `shadow-xl`) e bordas sutis (`border border-slate-100`).
   - **Prova Social em Destaque:** Carrossel/grid de comentários e avaliações reais de 5 estrelas do Google Maps com a nota oficial e estrelas douradas.
   - **Conversão no WhatsApp:** Botão flutuante fixo no canto inferior direito com animação suave e botões de ação contextuais com mensagens pré-preenchidas (`https://wa.me/55DDDNUMERO?text=...`).
3. **Página Autocontida:** Arquivo único `sites/[slug]/[slug].html` ultra-rápido, abrindo em menos de 1 segundo.
4. **Responsividade Absoluta:** Perfeito em telas mobile (360px a 430px), tablets e desktops grandes. Zero rolagem horizontal.
5. **Editor e Comparador:** Todo lote gera a versão editável `sites/[slug]/[slug]-editor.html` e o comparador antes/depois (ou visualizador de lançamento) `comparar.html`.

## Estrutura da página (adaptar à profissão)

1. **Hero**: nome + especialidade, promessa clara em 1 linha, CTA primário (WhatsApp) visível sem rolar, foto do profissional/clínica.
2. **Prova social**: nota do Google em destaque ("5.0 ★ · 121 avaliações no Google") — é real e verificável. Citar 2-3 trechos de avaliações reais do Google Maps se coletados.
3. **Serviços/áreas de atuação**: cards clicáveis — cada card leva à âncora da seção detalhada ou direto ao WhatsApp com mensagem pré-preenchida (`https://wa.me/55DDDNUMERO?text=Olá! Vim pelo site e quero saber sobre [serviço]`).
4. **Sobre**: formação e credenciais reais (geram autoridade — nunca cortar).
5. **Oferta estruturada** (quando fizer sentido): transformar "agende uma consulta" em opções de engajamento (ex.: sessão pontual, acompanhamento 90 dias, plano semestral) — SEM preços, apenas nomes e o que incluem, todos levando ao WhatsApp. Só criar planos que sejam agrupamento óbvio do serviço já oferecido.
6. **Localização e contato**: endereço, mapa (iframe do Google Maps), horários, telefone, redes.
7. **Rodapé**: dados do profissional (registro de classe se existir no original).

## Copywriting (aprimorar sem inventar — reescrever é obrigatório)

O texto do site novo NUNCA é o texto do site velho colado. Reescreva tudo com técnica, dizendo apenas o que o cliente já diz/oferece:

- **Headline do hero = benefício, não rótulo.** "Nutrição esportiva em SP" é rótulo; "Seu treino merece resultados que aparecem" é headline (com o rótulo virando kicker/subtítulo pra SEO).
- **Estrutura PAS suave** ao longo da página: toque na dor real do público, mostre o caminho, apresente o serviço como solução — no tom do nicho, sem agressividade de lançamento.
- **Escaneabilidade**: ninguém lê parágrafo de 8 linhas. Quebre em blocos de 2-3 linhas, bullets com verbo, subtítulos que contam a história sozinhos (quem só lê os títulos entende a página).
- **1 CTA por dobra**, sempre orientado à ação e ao benefício ("Quero minha avaliação" > "Clique aqui"), todos pro WhatsApp com mensagem pré-preenchida contextual.
- **Prova social costurada**, não empilhada: nota do Google perto do CTA, citação real perto da seção a que se refere.
- **Microcopy**: legendas sob botões ("resposta em poucos minutos"), rótulos humanos em formulários e seções.
- Proibido: clichês vazios ("qualidade e compromisso", "excelência no atendimento") sem fato que os sustente; superlativos inventados; promessas de resultado que o cliente não faz.

## Barra de qualidade estrutural (o "profissional de verdade")

A página pronta deve parecer feita por um estúdio de design — teste honesto: colocada ao lado de um template premium do nicho (clínicas/consultórios de alto padrão), ela não pode dever nada. Isso significa: grid consistente (mesmo espaçamento entre TODAS as seções), alinhamento impecável, alternância de ritmo entre seções (fundo claro/escuro/acento, largura cheia/contida), imagens com tratamento coerente (mesmo raio de borda, mesma temperatura), tipografia com no máximo 2 famílias e escala harmônica, e nenhuma seção "órfã" que pareça colada de outro site.

## Sistema de 5 Arquétipos Visuais (Variedade e Personalidade por Cliente)

Para evitar que todos os sites pareçam iguais, a IA deve escolher (ou alternar) entre **5 Arquétipos de Design Profissionais**, adaptando as cores, tipografia e layout ao nicho e perfil do cliente:

1. **🏛️ Arquétipo Editorial / Quiet Luxury (Elegância Atemporal):**
   - *Ideal para:* Estética facial avançada, dermatologia, cirurgia plástica, consultorias de luxo.
   - *Tipografia:* Serifada editorial (*Newsreader*, *Playfair Display*) + *Inter*.
   - *Paleta:* Linho *off-white* (`#FBFBFA`), grafite profundo (`#18181B`), acentos em areia/champagne.
   - *Layout:* Asimétrico, respiro amplo, estilo revista de alta costura.

2. **⚡ Arquétipo Swiss Precision / High-Tech (Moderno & Cirúrgico):**
   - *Ideal para:* Odontologia digital, implantes guiados, ortodontia invisível, laboratórios e tecnologia médica.
   - *Tipografia:* 100% Sans geométrica precisa (*Plus Jakarta Sans*, *Geist*, *Inter*).
   - *Paleta:* Branco puro (`#FFFFFF`) e cinza técnico (`#F1F5F9`), azul marinho profundo (`#0F172A`) e detalhes em azul aço (`#2563EB`).
   - *Layout:* Grids rigorosos, micro-badges técnicos, dados em destaque, linhas de precisão.

3. **🌿 Arquétipo Warm Organic / Wellness (Acolhedor & Humano):**
   - *Ideal para:* Nutricionistas, psicólogos, bem-estar, spas, medicina integrativa e pediatria.
   - *Tipografia:* Serifada suave (*Lora*) ou Sans humanista (*Outfit*, *DM Sans*).
   - *Paleta:* Tons de terra suaves (bege quente `#F5F2EB`, verde sálvia sutil `#E2E8E4`, terracota leve).
   - *Layout:* Formas orgânicas, cantos arredondados generosos, tom acolhedor e empático.

4. **⚖️ Arquétipo Dark Authority & Contemporary (Sóbrio & Poderoso):**
   - *Ideal para:* Advogados especialistas, peritos, contabilidade consultiva, estética automotiva premium.
   - *Tipografia:* Tipografia imponente de alto contraste (*Cinzel* / *Plus Jakarta Sans* peso 700).
   - *Paleta:* Carvão profundo (`#111827`), grafite fosco e toques de bronze antigo (`#9A7B56`).
   - *Layout:* Hierarquia direta, foco em autoridade jurídica e segurança institucional.

5. **🎨 Arquétipo Vibrant Boutique (Arrojado & Expressivo):**
   - *Ideal para:* Arquitetura moderna, interiores, gastronomia conceito, eventos e estúdios criativos.
   - *Tipografia:* Títulos display com personalidade + tipografia contrastante.
   - *Paleta:* Cores ricas (verde esmeralda, terracota queimado, mostarda suave sobre fundo claro).
   - *Layout:* Bento grids dinâmicos com fotografias em destaque e ritmo visual alegre.

## Checklist final (obrigatório antes de entregar)

- [ ] Zero texto placeholder / lorem ipsum
- [ ] Todos os links e CTAs apontam para contato REAL do cliente
- [ ] Número do WhatsApp no formato wa.me correto (55 + DDD + número)
- [ ] Responsivo verificado em 360, 375, 768, 1024, 1280 e 1440px — zero rolagem horizontal e zero quebra em TODAS
- [ ] Título e meta description preenchidos com nome + especialidade + cidade
- [ ] Comparação com o original: todo conteúdo importante do site antigo está presente
- [ ] Logo e fotos ORIGINAIS do cliente presentes na página nova
- [ ] `[slug]-editor.html` gerado e `comparar.html` atualizado

## Editor visual e comparador

A camada de edição visual (para gerar `[slug]-editor.html`) está em `references/editor-visual.md` — injetar o script exatamente como documentado lá. O comparador antes/depois está em `references/comparador-template.html` — substituir `__CLIENTES__` pelo array JSON e salvar como `comparar.html` na raiz da pasta conectada (mesclando com clientes existentes).
