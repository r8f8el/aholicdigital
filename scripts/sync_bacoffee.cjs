const fs = require('fs');

const lead = {
  id: 13,
  nome: 'BACOFFEE Cafeteria',
  nicho: 'Cafeteria Artesanal & Brunch',
  cidade: 'Guarulhos - SP',
  nota: 4.7,
  avaliacoes: 260,
  whatsapp: '(11) 91360-3173',
  siteAntigo: null,
  motivo: 'Eleita Melhor Cafeteria de GRU (Maia). Cafés de micro lote, brunch de domingo e toasts artesanais. Sem site oficial próprio.',
  status: 'site_pronto',
  urlNova: 'sites/bacoffee-cafeteria/index.html',
  urlEditor: 'sites/bacoffee-cafeteria/bacoffee-cafeteria.html',
  dataProposta: new Date().toISOString().split('T')[0],
  preset: 'editorial-atelier',
  tipo: 'Do Zero'
};

const dashboardPath = 'dashboard.html';
if (fs.existsSync(dashboardPath)) {
  let html = fs.readFileSync(dashboardPath, 'utf8');
  
  // Check if lead 13 already in leads array
  if (!html.includes('BACOFFEE Cafeteria')) {
    html = html.replace(/const LEADS_INICIAIS = \[([\s\S]*?)\];/, (match, p1) => {
      return `const LEADS_INICIAIS = [${p1.trim()},\n  ${JSON.stringify(lead, null, 2)}\n];`;
    });
    fs.writeFileSync(dashboardPath, html, 'utf8');
    console.log('✅ Lead #13 adicionado ao dashboard.html');
  } else {
    console.log('ℹ️ Lead #13 já consta no dashboard.html');
  }
}
