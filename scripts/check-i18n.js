#!/usr/bin/env node
/**
 * Vérifie la cohérence des traductions du site.
 *
 * Trois régressions sont possibles et invisibles à l'œil nu :
 *   1. une clé traduite dans une langue et pas dans une autre — le texte
 *      français du HTML reste alors affiché sans que rien ne signale l'écart ;
 *   2. une clé référencée dans une page mais absente du dictionnaire — elle ne
 *      sera jamais traduite, quelle que soit la langue choisie ;
 *   3. une page légale à qui il manque un bloc de langue.
 *
 * Usage : node scripts/check-i18n.js   (code de sortie 1 si un problème reste)
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const src = fs.readFileSync(path.join(ROOT, 'js/i18n.js'), 'utf8');
const start = src.indexOf('const TRANSLATIONS');
const T = eval(
  src.slice(start, src.indexOf('\n};', start) + 3).replace('const TRANSLATIONS', 'globalThis.__T') + '; __T'
);

const langs = Object.keys(T);
const all = new Set(langs.flatMap((l) => Object.keys(T[l])));
const problems = [];

// 1. Parité entre langues
for (const l of langs) {
  const missing = [...all].filter((k) => T[l][k] === undefined);
  if (missing.length) problems.push(`${l} : ${missing.length} clé(s) manquante(s) → ${missing.slice(0, 8).join(', ')}`);
}

// 2. Clés référencées dans les pages
const htmls = [];
(function walk(dir) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    if (fs.statSync(p).isDirectory()) {
      if (!['node_modules', '.git', 'assets', 'fonts'].includes(f)) walk(p);
    } else if (f.endsWith('.html')) htmls.push(p);
  }
})(ROOT);

const ATTRS = /data-i18n(?:-href|-content|-placeholder)?="([^"]+)"/g;
const used = new Set();
for (const p of htmls) {
  for (const m of fs.readFileSync(p, 'utf8').matchAll(ATTRS)) used.add(m[1]);
}
used.delete('true'); // data-i18n-app porte un nom d'app, pas une clé

const undefinedKeys = [...used].filter((k) => !all.has(k) && !/^[A-Z]/.test(k));
if (undefinedKeys.length) problems.push(`${undefinedKeys.length} clé(s) utilisée(s) mais absente(s) du dictionnaire : ${undefinedKeys.join(', ')}`);

const unused = [...all].filter((k) => !used.has(k));

// 3. Pages légales : un bloc par langue
for (const p of htmls.filter((f) => /\/(privacy|terms)\.html$/.test(f))) {
  const html = fs.readFileSync(p, 'utf8');
  if (!html.includes('legal-content')) continue;
  const blocks = [...html.matchAll(/data-legal-content="([a-z-]+)"/g)].map((m) => m[1]);
  const missing = langs.filter((l) => !blocks.includes(l));
  if (missing.length) problems.push(`${path.relative(ROOT, p)} : bloc légal manquant → ${missing.join(', ')}`);
}

console.log(`Langues : ${langs.join(', ')} — ${all.size} clés, ${htmls.length} pages`);
if (unused.length) console.log(`  (info) ${unused.length} clé(s) définie(s) mais jamais utilisée(s) : ${unused.slice(0, 10).join(', ')}${unused.length > 10 ? '…' : ''}`);

if (problems.length) {
  console.error('\n✗ Problèmes détectés :');
  problems.forEach((p) => console.error('   ' + p));
  process.exit(1);
}
console.log('✓ Traductions cohérentes.');
