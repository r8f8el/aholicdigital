import fs from 'fs';

const SUPABASE_URL = 'https://gpignxwsxfbkelckrebd.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwaWdueHdzeGZia2VsY2tyZWJkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc4NjQ3OTcsImV4cCI6MjEwMzQ0MDc5N30.Ex2iAC0VoW9svg2rMKNwWU9rYz5FNTQaz6qa9GL97tU';

// Read dashboard.html
const content = fs.readFileSync('dashboard.html', 'utf8');
const match = content.match(/<script id="dados" type="application\/json">([\s\S]*?)<\/script>/);
if (!match) {
  console.error('Dados não encontrados no dashboard.html');
  process.exit(1);
}

const data = JSON.parse(match[1]);
console.log(`Total de leads locais para sincronizar: ${data.leads.length}`);

async function apiRequest(endpoint, method, payload) {
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/${endpoint}`, {
      method: method,
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
      },
      body: payload ? JSON.stringify(payload) : undefined
    });

    if (!res.ok) {
      const err = await res.text();
      console.error(`Erro ${res.status} em ${endpoint}:`, err);
      return null;
    } else {
      const text = await res.text();
      return text ? JSON.parse(text) : true;
    }
  } catch (e) {
    console.error(`Falha de conexão em ${endpoint}:`, e.message);
    return null;
  }
}

async function sync() {
  for (const lead of data.leads) {
    const row = {
      slug: lead.slug,
      nome: lead.nome,
      nicho: lead.nicho,
      cidade: lead.cidade,
      nota: lead.nota,
      avaliacoes: lead.avaliacoes,
      email: lead.email,
      telefone: lead.telefone,
      whatsapp: lead.whatsapp,
      site_antigo: lead.siteAntigo,
      motivo: lead.motivo,
      status: lead.status,
      url_nova: lead.urlNova,
      data_proposta: lead.dataProposta || null,
      valor: lead.valor,
      manutencao: lead.manutencao,
      pago: lead.pago || 0,
      contrato_status: lead.contratoStatus || 'pendente',
      contrato_em: lead.contratoEm || null,
      doc_cliente: lead.docCliente,
      end_cliente: lead.endCliente,
      obs: lead.obs
    };

    console.log(`Sincronizando lead: ${lead.slug} (${lead.nome})...`);
    // Upsert lead
    await apiRequest('leads?on_conflict=slug', 'POST', row);

    if (lead.versoes && lead.versoes.length > 0) {
      // First delete existing versions for this lead to avoid duplicates
      await apiRequest(`versoes_site?lead_slug=eq.${lead.slug}`, 'DELETE');

      for (const v of lead.versoes) {
        const vRow = {
          lead_slug: lead.slug,
          numero: v.numero,
          nome_estilo: v.nome_estilo,
          descricao: v.descricao,
          arquivo: v.arquivo,
          criado_em: v.criado_em,
          ativo: v.ativo === 1 || v.ativo === true ? true : false
        };
        await apiRequest('versoes_site', 'POST', vRow);
      }
    }
  }
  console.log('🎉 Todos os leads e versões foram sincronizados no Supabase Cloud com sucesso!');
}

sync();
