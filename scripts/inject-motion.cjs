const fs = require('fs');

// Inject motion engine into cafe-shin and daldali
const motionJs = fs.readFileSync('referencias/motion-engine.js', 'utf8');
const motionTag = `\n<script>\n/* Aholic Motion Engine v2.0 */\n${motionJs}\n</script>`;

const metaTags = `\n    <meta name="ah-brand" content="CAFÉ SHIN">\n    <meta name="ah-sub" content="Café Franco-Coréen • Paris 10e">`;

const cssVars = `
    <style id="ah-motion-vars">
        :root {
            --ah-accent: #E0A96D;
            --ah-bg: #111413;
            --ah-text: #F5EFEB;
            --ah-font-display: 'League Spartan', sans-serif;
            --ah-font-body: 'Playfair Display', serif;
            --ah-preloader-bg: #111413;
            --ah-preloader-text: #F5EFEB;
        }
    </style>`;

const files = [
    { path: 'sites/cafe-shin/index.html', brand: 'CAFÉ SHIN', sub: 'Café Franco-Coréen • Paris 10e', accent: '#E0A96D', bg: '#111413', text: '#F5EFEB' },
    { path: 'sites/cafe-shin/cafe-shin.html', brand: 'CAFÉ SHIN', sub: 'Café Franco-Coréen • Paris 10e', accent: '#E0A96D', bg: '#111413', text: '#F5EFEB' },
    { path: 'sites/daldali-coffee-paris/index.html', brand: 'DALDALI', sub: 'Café Coréen • Paris 9e', accent: '#8EA68B', bg: '#1C2B22', text: '#F7F5F0' },
];

for (const f of files) {
    if (!fs.existsSync(f.path)) {
        console.log(`Skipping ${f.path} (not found)`);
        continue;
    }

    let html = fs.readFileSync(f.path, 'utf8');

    // Skip if already has motion engine v2
    if (html.includes('AholicMotionEngine')) {
        console.log(`${f.path}: motion engine already present`);
        continue;
    }

    // Add meta tags after <head>
    if (!html.includes('ah-brand')) {
        html = html.replace(
            /<head>/,
            `<head>\n    <meta name="ah-brand" content="${f.brand}">\n    <meta name="ah-sub" content="${f.sub}">`
        );
    }

    // Add CSS vars for motion engine
    const cssVarBlock = `\n    <style id="ah-color-vars">
        :root {
            --ah-accent: ${f.accent};
            --ah-bg: ${f.bg};
            --ah-text: ${f.text};
            --ah-font-display: 'League Spartan', sans-serif;
            --ah-preloader-bg: ${f.bg};
            --ah-preloader-text: ${f.text};
        }
    </style>`;
    
    if (!html.includes('ah-color-vars')) {
        html = html.replace('</head>', cssVarBlock + '\n</head>');
    }

    // Inject motion engine before </body>
    html = html.replace('</body>', motionTag + '\n</body>');

    fs.writeFileSync(f.path, html, 'utf8');
    console.log(`✅ Motion Engine injetado: ${f.path}`);
}
