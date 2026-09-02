const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const dir = 'sites/bacoffee-cafeteria/assets/fotos';

// High-quality café/coffee shop photos that match the BAC Coffee aesthetic:
// warm, artisanal, beige/green tones, brunch, specialty coffee
const images = {
    'hero.jpg':      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1600&q=85&fit=crop',
    'interior.jpg':  'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1200&q=85&fit=crop',
    'coffee01.jpg':  'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=1200&q=85&fit=crop',
    'coffee02.jpg':  'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=1200&q=85&fit=crop',
    'toast.jpg':     'https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=1200&q=85&fit=crop',
    'brunch.jpg':    'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?w=1200&q=85&fit=crop',
    'cappuccino.jpg':'https://images.unsplash.com/photo-1534778101976-62847782c213?w=1200&q=85&fit=crop',
    'ambiente.jpg':  'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1200&q=85&fit=crop',
    'sobremesa.jpg': 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=1200&q=85&fit=crop',
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
    console.log('📸 Baixando fotos para BAC Coffee...\n');
    for (const [name, url] of Object.entries(images)) {
        await download(url, path.join(dir, name));
    }
    console.log('\n✅ Download concluído!');
}

run();
