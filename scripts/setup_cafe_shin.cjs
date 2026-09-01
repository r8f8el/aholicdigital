const fs = require('fs');
let html = fs.readFileSync('sites/cafe-shin/raw_draft.html', 'utf8');

// Ensure base tag and image fallback script is present
const baseScript = `
    <script>
        (function() {
            if (window.location.protocol.startsWith('http') && !window.location.pathname.endsWith('/')) {
                const base = document.createElement('base');
                base.href = window.location.pathname.endsWith('.html') 
                    ? window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/') + 1)
                    : window.location.pathname + '/';
                document.head.prepend(base);
            }
        })();
    </script>
`;

if (!html.includes('window.location.pathname')) {
    html = html.replace('<head>', '<head>' + baseScript);
}

// Write to index.html
fs.writeFileSync('sites/cafe-shin/index.html', html, 'utf8');
fs.writeFileSync('sites/cafe-shin/cafe-shin.html', html, 'utf8');

// Also create editor version
let editorHtml = html.replace('<body', '<body class="pt-12"');
const editorBar = `
    <div style="position:fixed;top:0;left:0;right:0;height:48px;background:#111;color:#fff;display:flex;align-items:center;justify-content:between;padding:0 20px;z-index:999999;font-family:sans-serif;font-size:13px;border-bottom:1px solid #333;">
        <div><strong>Modo Editor Visual</strong> • Apocalypse Coffee / Café Shin</div>
        <div style="display:flex;gap:10px;">
            <button onclick="alert('Salvo com sucesso!')" style="background:#22c55e;color:#000;border:none;padding:6px 14px;border-radius:20px;font-weight:bold;cursor:pointer;">Salvar</button>
            <a href="index.html" style="color:#aaa;text-decoration:none;padding:6px 12px;border:1px solid #444;border-radius:20px;">Ver Site</a>
        </div>
    </div>
`;
editorHtml = editorHtml.replace(/<body[^>]*>/, '$&' + editorBar);
fs.writeFileSync('sites/cafe-shin/cafe-shin-editor.html', editorHtml, 'utf8');

console.log('Successfully written index.html, cafe-shin.html, and cafe-shin-editor.html');
