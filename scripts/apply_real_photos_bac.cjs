const fs = require('fs');
const path = require('path');

const srcDir = 'C:\\Users\\rafae\\.gemini\\antigravity-ide\\brain\\b5361fdb-4d6b-4423-85cf-2f5285037eef';
const destDir = 'sites/bacoffee-cafeteria/assets/fotos';

const map = {
  'gmaps_photo_1_interior_1788310294965.png': 'hero.jpg',
  'gmaps_photo_1_interior_1788310294965.png': 'interior.jpg',
  'ig_post_2_coffee_pourover_1788310049588.png': 'coffee01.jpg',
  'ig_post_3_cookie_nutella_1788310111259.png': 'sobremesa.jpg',
  'gmaps_photo_2_customers_1788310456946.png': 'ambiente.jpg',
  'gmaps_photo_3_menu_1788311255583.png': 'brunch.jpg',
  'ig_post_1_clean_1788310000739.png': 'toast.jpg',
};

// Also copy hero separately
fs.copyFileSync(path.join(srcDir, 'gmaps_photo_1_interior_1788310294965.png'), path.join(destDir, 'hero.jpg'));
console.log('✅ hero.jpg (Real Google Maps Interior)');

for (const [srcName, destName] of Object.entries(map)) {
  const src = path.join(srcDir, srcName);
  const dest = path.join(destDir, destName);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, dest);
    console.log(`✅ ${destName} <- ${srcName}`);
  } else {
    console.log(`⚠️ Not found: ${srcName}`);
  }
}
