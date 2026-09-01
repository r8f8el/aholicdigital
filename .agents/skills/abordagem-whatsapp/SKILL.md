---
name: abordagem-whatsapp
description: Esta skill deve ser usada ao enviar a primeira abordagem comercial via WhatsApp para um lead prospectado — mensagem personalizada com link do novo site, rapport e sem preço. Acione quando o usuário disser "mandar no whatsapp", "abordar pelo zap", "enviar mensagem", "falar com o cliente" ou pedir para abordar por WhatsApp (skill abordagem-whatsapp).
---

# Abordagem Comercial por WhatsApp

O WhatsApp é o canal nº 1 de conversão no Brasil. A taxa de abertura é 98% (vs. 20% do e-mail). A abordagem deve parecer uma **mensagem pessoal de alguém que já fez algo pelo destinatário**, nunca uma propaganda em massa.

## Princípios

1. **Personalização extrema.** A primeira linha DEVE conter o nome do profissional e um fato real verificável (nota no Google, CASACOR, especialidade, número de avaliações). Mensagem genérica = bloqueio imediato.
2. **Prova antes do pedido.** O trabalho JÁ está feito e no ar. O link é a proposta. Não pedir nada antes de entregar valor.
3. **Zero preço.** Preço só na conversa que a resposta abre. Nunca antecipar valores na primeira mensagem.
4. **Respeito ao tempo.** Mensagem curta e direta. Máximo 4 parágrafos curtos (80-120 palavras total). Profissional ocupado não lê textão de desconhecido.
5. **Sem urgência falsa.** Sem "últimas vagas", "promoção por tempo limitado". Um único CTA: dar uma olhada no link e dizer o que achou.
6. **Horário comercial.** Enviar entre 9h-17h em dias úteis. Nunca à noite, nunca no fim de semana.

## Estrutura da Mensagem

```
Olá [Nome], tudo bem? 👋

[Elogio específico e verificável — ex: "Vi que sua clínica tem nota 5.0 no Google com 28 avaliações incríveis" ou "Acompanhei seu projeto do Spa Itá na CASACOR Tocantins — trabalho sensacional!"]

[Observação sobre a ausência de site / problema do site atual — ex: "Notei que você ainda não tem um site oficial à altura do seu trabalho" ou "Percebi que seu site atual não está otimizado para captar clientes pelo celular"]

Desenvolvi uma página exclusiva e personalizada para [Nome do Negócio] — já está no ar para você ver:
👉 [LINK DO SITE]

*Sem compromisso nenhum!* Se gostar, me conta o que achou. 😊

[Nome do Usuário]
[Cargo/Título — ex: "Designer de Sites de Alto Padrão"]
[WhatsApp do usuário]
```

## Variações por Tipo de Lead

### Lead "Do Zero" (sem site próprio)
- Ênfase: "Você tem um trabalho incrível, mas sem uma vitrine digital à altura."
- Prova: Mostrar que só existe no Instagram/Google Maps e que está perdendo clientes que buscam no Google.
- Link: direto para o site novo.

### Lead "Redesign" (site fraco existente)
- Ênfase: "Dei uma olhada no seu site atual e achei que você merece algo muito melhor."
- Prova: Citar 1-2 problemas objetivos (lento no mobile, sem botão de WhatsApp, visual datado).
- Link: para a página-capa de proposta (antes/depois) ou direto para o site novo.

## Geração da Mensagem

1. Ler dados do lead no `prospector.db` ou `leads.md`: nome, nicho, nota, avaliações, WhatsApp, motivo, URL do site novo.
2. Ler dados do usuário no `prospector-config.json`: nome, cargo, WhatsApp.
3. Montar a mensagem personalizada seguindo a estrutura acima.
4. Gerar o link `wa.me/` pronto para clicar:
   ```
   https://wa.me/[WHATSAPP_DO_LEAD]?text=[MENSAGEM_URL_ENCODED]
   ```
5. Exibir a mensagem formatada e o link para o usuário revisar.
6. Atualizar o status do lead para `proposta` no banco/leads.md e no dashboard.

## Follow-up (3 dias úteis sem resposta)

Se o lead não responder em 3 dias úteis, gerar UMA mensagem de follow-up:

```
Oi [Nome], tudo bem? 😊

Só passando pra saber se conseguiu dar uma olhada na página que preparei para [Nome do Negócio]:
👉 [LINK]

Fique à vontade pra me dizer o que achou — sem compromisso nenhum!

Abraço,
[Nome do Usuário]
```

**Regras do follow-up:**
- Apenas 1 follow-up por lead. Nunca insistir mais de uma vez.
- Se não responder após o follow-up, marcar como `sem_resposta` e seguir para o próximo lead.
- Nunca enviar follow-up no mesmo dia da mensagem original.

## Checklist Anti-Bloqueio

- [ ] Mensagem 100% personalizada (nome + fato real do lead)
- [ ] Sem links encurtados (bit.ly etc.) — usar URL completa do domínio oficial
- [ ] Sem emojis em excesso (máximo 3-4 no total)
- [ ] Sem CAIXA ALTA no corpo da mensagem
- [ ] Sem palavras-gatilho de spam: "grátis", "promoção", "desconto", "oferta", "imperdível"
- [ ] Enviada em horário comercial (9h-17h, dias úteis)
- [ ] WhatsApp do lead no formato internacional correto: `55DDDNUMERO` (sem espaços, sem +)

## Depois do Envio

- Registrar no banco/`leads.md`: status `proposta`, data da proposta, canal `whatsapp`.
- Atualizar o dashboard (skill `dashboard-leads`).
- Sugerir ao usuário agendar o follow-up em 3 dias úteis se não houver resposta.
