const fs = require('fs');

const files = ['dashboard.html', 'index.html'];

const leadDaldali = {
    slug: 'daldali-coffee-paris',
    nome: 'DALDALI | Café & Pâtisserie Coréenne',
    nicho: 'Cafeteria & Pâtisserie',
    cidade: 'Paris (9e / Pigalle)',
    nota: 4.9,
    avaliacoes: 48,
    email: 'contact@daldali.fr',
    telefone: '',
    whatsapp: '',
    siteAntigo: null,
    motivo: 'Cafeteria artesanal franco-coreana em Pigalle (Paris 9e) sem site oficial.',
    status: 'site_pronto',
    urlNova: 'sites/daldali-coffee-paris/index.html',
    dataProposta: '2026-09-01',
    valor: 2400.0,
    manutencao: 190.0,
    pago: 0,
    contratoStatus: 'pendente',
    contratoEm: null,
    docCliente: null,
    endCliente: '23 Rue Marguerite de Rochechouart, 75009 Paris',
    obs: 'Especialidade em Yakgwa de mel e matcha cerimonial. Estilo Super Travel Luxury com tema verde floresta das paredes do café.'
};

const leadCafeShin = {
    slug: 'cafe-shin',
    nome: 'Apocalypse Coffee Roasters | Café Shin',
    nicho: 'Torrefação Especial & Grãos Orgânicos',
    cidade: 'Superdesign Roastery',
    nota: 4.9,
    avaliacoes: 62,
    email: 'contact@apocalypsecoffee.com',
    telefone: '',
    whatsapp: '',
    siteAntigo: 'apocalypsecoffee.com',
    motivo: 'Torrefação artesanal de cafés orgânicos especiais. Design importado via Superdesign.',
    status: 'site_pronto',
    urlNova: 'sites/cafe-shin/index.html',
    dataProposta: '2026-09-01',
    valor: 2200.0,
    manutencao: 180.0,
    pago: 0,
    contratoStatus: 'pendente',
    contratoEm: null,
    docCliente: null,
    endCliente: 'Online / Global Roastery',
    obs: 'Design importado do Superdesign (Draft 5b241203-69b7-47f1-9fb2-c073f47850bf). Assinatura de café, notas sensoriais e rastreabilidade.'
};

for (const f of files) {
    if (fs.existsSync(f)) {
        let html = fs.readFileSync(f, 'utf8');
        const match = html.match(/<script id="dados" type="application\/json">([\s\S]*?)<\/script>/);
        if (match) {
            let obj = JSON.parse(match[1]);
            obj.leads = obj.leads.filter(l => l.slug !== 'daldali-coffee-paris' && l.slug !== 'cafe-shin');
            obj.leads.unshift(leadDaldali);
            obj.leads.unshift(leadCafeShin);
            obj.atualizado = new Date().toISOString().replace('T', ' ').substring(0, 16);
            
            const newScript = `<script id="dados" type="application/json">${JSON.stringify(obj)}</script>`;
            html = html.replace(/<script id="dados" type="application\/json">[\s\S]*?<\/script>/, newScript);
            fs.writeFileSync(f, html, 'utf8');
            console.log(`OK: ${f} atualizado com sucesso!`);
        }
    }
}
