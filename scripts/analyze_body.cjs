const fs = require('fs');
const html = fs.readFileSync('sites/cafe-shin/raw_draft.html', 'utf8');

// Check head scripts/styles
console.log('Total length:', html.length);
const bodyMatch = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
if (bodyMatch) {
    console.log('Body length:', bodyMatch[1].length);
}
