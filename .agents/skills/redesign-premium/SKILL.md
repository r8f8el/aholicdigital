---
name: redesign-premium
description: Esta skill deve ser usada ao redesenhar o site de um cliente prospectado — criar uma versão nova, premium e de alta conversão da página existente, mantendo conteúdo, logo e paleta do cliente. Acione quando o usuário disser "redesenhar site", "melhorar página", "refazer o site do cliente", "criar site" ou pedir para redesenhar (skill redesign-premium).
---

# Criação e Redesign Premium de Páginas v2.0 (Motor Automático + Motion Engine)

Criar uma presença digital impecável para o cliente — seja **Redesenhando um site fraco** ou **Criando o Primeiro Site Oficial do Zero**. O resultado deve incluir: fotos reais do cliente, cores extraídas da identidade visual e animações cinematográficas em todo site.

---

## ⚡ Geração Automática em 1 Comando (OBRIGATÓRIO)

**Sempre use o `aholic-generator.py` como ponto de entrada.**

```bash
# Exemplo completo (com fotos do Maps + Instagram + paleta da logo)
python scripts/aholic-generator.py \
  --slug "nome-do-cliente" \
  --preset auto \
  --instagram "@instagram_do_cliente" \
  --maps "https://maps.app.goo.gl/..." \
  --info '{"nome":"Nome Cliente","nicho":"Cafeteria","cidade":"São Paulo","nota":4.9,"avaliacoes":120,"telefone":"(11) 99999-9999","whatsapp":"11999999999","endereco":"Rua X, 123","horarios":"Seg-Sex 8h-18h","servicos":["Especialidade 1","Especialidade 2"]}'

# Listar presets disponíveis
python scripts/aholic-generator.py --list

# Sem fotos automáticas (apenas HTML + cores do preset)
python scripts/aholic-generator.py --slug "slug" --preset "cinema-local" --no-photos
```

O gerador automaticamente:
1. **Extrai fotos reais** do Google Maps e Instagram público (via Playwright)
2. **Lê a logo** e extrai a paleta de cores da identidade visual do cliente
3. **Adapta o preset** às cores reais do negócio (primary, accent, bg, text)
4. **Injeta o Motion Engine** (`referencias/motion-engine.js`): preloader cinematográfico, cursor magnético, scroll reveal, counters animados, parallax e marquee
5. **Gera os 3 arquivos padrão**: `index.html`, `[slug].html`, `[slug]-editor.html`
6. **Publica automaticamente** via `git push → Vercel`

---

## 🎨 Presets Disponíveis (`referencias/presets-dinamicos.json`)

| Preset | Nichos | Fontes | Modo |
|---|---|---|---|
| `editorial-atelier` | Arquitetura, Dermato, Luxo, Spa | Newsreader + Inter | Dark |
| `cinema-local` | Cafeteria, Restaurante, Gastronomia | League Spartan + Playfair | Dark |
| `cartaz-modular` | Psicologia, Nutrição, Bem-estar | Plus Jakarta Sans | Light |
| `instrumento-digital` | Odontologia, Saúde, Clínica | Plus Jakarta Sans + Inter | Light |
| `brutalismo-comercial` | Barbearia, Academia, Streetwear | League Spartan | Dark |
| `arquivo-vivo` | Advocacia, Consultoria | JetBrains Mono + Inter | Dark |

> **`--preset auto`** seleciona o preset correto baseado no nicho automaticamente.

---

## 🎬 Motion Engine Padrão (`referencias/motion-engine.js`)

Todo site gerado pelo `aholic-generator.py` já inclui automaticamente:

- **Preloader Cinematic Curtain**: cortinas se abrem revelando o site com o nome do cliente
- **Scroll Reveal**: elementos entram suavemente ao rolar a página (stagger escalonado)
- **Cursor Magnético**: cursor personalizado na cor `--ah-accent` do cliente
- **Contadores Animados**: números sobem suavemente ao entrar na viewport
- **Parallax em Imagens**: profundidade de scroll nas fotos
- **Marquee Infinita**: faixa de informações animada
- **Float Badge Bounce**: badge de avaliação flutuante animado
- **Header Shadow**: header ganha sombra ao rolar

Para adicionar manualmente a um site existente:
```html
<script src="/referencias/motion-engine.js"></script>
<!-- ou inline (copie o conteúdo do arquivo) -->
```

Configuração via `meta` tags ou atributos `data-ah-*`:
```html
<meta name="ah-brand" content="Nome do Cliente">
<meta name="ah-sub" content="Nicho • Cidade">
```

---

## 📸 Extração de Fotos (`scripts/extrair-fotos.py`)

```bash
# Extrai fotos do Maps e Instagram
python scripts/extrair-fotos.py \
  --slug "cafe-shin" \
  --maps "https://maps.app.goo.gl/..." \
  --instagram "cafeshinparis" \
  --max 8
```

Salva em `sites/[slug]/assets/fotos/` e cria `assets/fotos.json` com catálogo.

---

## 🎨 Extração de Paleta (`referencias/color-extractor.py`)

```bash
# Extrai paleta da logo
python referencias/color-extractor.py --slug "cafe-shin" --url "https://..." 
# ou
python referencias/color-extractor.py --slug "cafe-shin" --img "sites/cafe-shin/assets/logo.png"
```

Gera `sites/[slug]/assets/paleta.json` com:
- `tokens`: variáveis CSS `--ah-*` prontas para uso
- `css_vars`: bloco `:root{}` completo para colar no `<style>`
- `contrast_check`: verificação WCAG AA automática

---

## 🛑 Diretrizes Anti-Slop (Padrão Estúdio)

1. **PROIBIDO** gradientes neon clichês sem justificativa de marca
2. **PROIBIDO** textos genéricos de IA ("Revolucione sua jornada", "Embarque em uma experiência")
3. **PROIBIDO** fotos de banco de imagem de pessoas: usar fotos REAIS do Maps/Instagram do cliente
4. **OBRIGATÓRIO** informações 100% reais: endereço, horários, avaliações reais do Google Maps, WhatsApp no formato `wa.me/55DDDNUMERO`

---

## 🚀 Deploy Automático (Vercel)

O `aholic-generator.py` faz o deploy automaticamente. Para deploy manual:

```bash
git add .
git commit -m "feat([slug]): site premium com motion engine — [Nome do Cliente]"
git push origin main
```

URL de produção: `https://aholicdigital.vercel.app/sites/[slug]/index.html`

---

## 📋 Checklist Final

- [ ] `aholic-generator.py` executado com `--instagram` e/ou `--maps`
- [ ] Fotos reais baixadas (verificar `sites/[slug]/assets/fotos/`)
- [ ] Paleta extraída da logo (verificar `sites/[slug]/assets/paleta.json`)
- [ ] Motion Engine presente no HTML gerado
- [ ] WhatsApp e Instagram funcionando nos botões
- [ ] Deploy na Vercel confirmado
- [ ] Dashboard atualizado com o novo lead
