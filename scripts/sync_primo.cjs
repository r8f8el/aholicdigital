const fs = require('fs');

const lead = {
  id: 14,
  nome: 'Primo Games',
  nicho: 'Games, Consoles & Assistência Técnica',
  cidade: 'Goiânia - GO',
  nota: 4.7,
  avaliacoes: 476,
  whatsapp: '(62) 99644-3118',
  siteAntigo: null,
  motivo: 'Mais de 28 anos de tradição gamer em Goiânia (Camelódromo de Campinas 1). 112k no Instagram, consoles PS5/Switch/Xbox, trocas e assistência técnica. Sem site oficial moderno.',
  status: 'site_pronto',
  urlNova: 'sites/primo-games/index.html',
  urlEditor: 'sites/primo-games/primo-games.html',
  dataProposta: new Date().toISOString().split('T')[0],
  preset: 'warm-industrial',
  tipo: 'Do Zero'
};

const dashboardPath = 'dashboard.html';
if (fs.existsSync(dashboardPath)) {
  let html = fs.readFileSync(dashboardPath, 'utf8');
  
  if (!html.includes('Primo Games')) {
    html = html.replace(/const LEADS_INICIAIS = \[([\s\S]*?)\];/, (match, p1) => {
      return `const LEADS_INICIAIS = [${p1.trim()},\n  ${JSON.stringify(lead, null, 2)}\n];`;
    });
    fs.writeFileSync(dashboardPath, html, 'utf8');
    console.log('✅ Lead #14 (Primo Games) adicionado ao dashboard.html');
  } else {
    console.log('ℹ️ Lead #14 já consta no dashboard.html');
  }
}
