const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const dir = 'sites/primo-games/assets/fotos';

// High-impact gaming photography for Primo Games (Consoles, PS5, Switch, Xbox, Retro, Setup, Maintenance, Controllers)
const images = {
    'hero-ps5.jpg':     'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=1600&q=85&fit=crop',
    'store-gaming.jpg': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1200&q=85&fit=crop',
    'switch.jpg':       'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=1200&q=85&fit=crop',
    'xbox.jpg':         'https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=1200&q=85&fit=crop',
    'retro.jpg':        'https://images.unsplash.com/photo-1551103782-8ab07afd45c1?w=1200&q=85&fit=crop',
    'controller.jpg':   'https://images.unsplash.com/photo-1592840496694-26d035b52b48?w=1200&q=85&fit=crop',
    'pc-gamer.jpg':     'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=1200&q=85&fit=crop',
    'assistencia.jpg':  'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=1200&q=85&fit=crop',
    'setup.jpg':        'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1200&q=85&fit=crop',
};

function download(url, dest) {
    return new Promise((resolve) => {
        const proto = url.startsWith('https') ? https : http;
        const file = fs.createWriteStream(dest);
        proto.get(url, (res) => {
            if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                file.close();
                download(res.headers.location, dest).then(resolve);
                return;
            }
            res.pipe(file);
            file.on('finish', () => {
                file.close();
                const size = fs.statSync(dest).size;
                console.log(`✅ ${path.basename(dest)} (${Math.round(size/1024)}KB)`);
                resolve(true);
            });
        }).on('error', (err) => {
            console.log(`⚠️  Falha: ${path.basename(dest)} — ${err.message}`);
            resolve(false);
        });
    });
}

async function run() {
    console.log('🎮 Baixando fotos de alta definição para Primo Games...\n');
    for (const [name, url] of Object.entries(images)) {
        await download(url, path.join(dir, name));
    }
    console.log('\n✅ Download concluído!');
}

run();
