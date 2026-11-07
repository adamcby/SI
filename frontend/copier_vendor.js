// Copie les librairies front dans app/static/vendor pour un fonctionnement 100 % hors-ligne.
const fs = require('fs');
const path = require('path');
const dest = path.join(__dirname, '..', 'app', 'static', 'vendor');
fs.mkdirSync(dest, { recursive: true });
const fichiers = [
  ['alpinejs/dist/cdn.min.js', 'alpine.min.js'],
  ['chart.js/dist/chart.umd.js', 'chart.umd.min.js'],
  ['html2canvas/dist/html2canvas.min.js', 'html2canvas.min.js'],
  ['jszip/dist/jszip.min.js', 'jszip.min.js'],
  ['@fontsource-variable/inter/files/inter-latin-wght-normal.woff2', 'inter-latin-wght-normal.woff2'],
  ['@fontsource-variable/inter/files/inter-latin-ext-wght-normal.woff2', 'inter-latin-ext-wght-normal.woff2'],
];
for (const [src, nom] of fichiers) {
  fs.copyFileSync(path.join(__dirname, 'node_modules', src), path.join(dest, nom));
  console.log('copié :', nom);
}
