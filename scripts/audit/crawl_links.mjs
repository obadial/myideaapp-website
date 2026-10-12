// Parcourt le site comme un visiteur : part de l'accueil, suit chaque lien interne,
// dans les 3 langues (localStorage), et relève l'adresse de chaque lien telle que le
// navigateur la résout (a.href). Écrit {page: [liens]} en JSON.
// node --experimental-websocket crawl_links.mjs <base> <sortie.json>
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
const [base, out] = process.argv.slice(2);
const PORT = String(9700 + Math.floor(Math.random() * 200));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--remote-debugging-port=' + PORT, '--user-data-dir=/private/tmp/claude-501/crawl-' + PORT, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let t; for (let i = 0; i < 60; i++) { try { t = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json(); if (t.find(x => x.type === 'page')) break; } catch {} await sleep(200); }
const ws = new WebSocket(t.find(x => x.type === 'page').webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = new Map();
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); setTimeout(() => pend.has(i) && (pend.delete(i), r({})), 10000); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable');
const origin = new URL(base).origin;
const norm = u => { const x = new URL(u); x.hash = ''; x.search = ''; return x.href; };
const seen = new Set(), queue = [base + '/'], result = {};
while (queue.length) {
  const page = queue.shift();
  if (seen.has(page)) continue;
  seen.add(page);
  for (const lang of ['fr', 'en', 'es']) {
    await send('Page.navigate', { url: page });
    await sleep(300);
    await send('Runtime.evaluate', { expression: `localStorage.setItem('mia_lang','${lang}')` });
    await send('Page.reload', {});
    await sleep(900);
    const r = await send('Runtime.evaluate', { expression: `JSON.stringify([location.href, [...document.querySelectorAll('a[href]')].map(a => [a.href, a.getAttribute('href'), (a.innerText || a.getAttribute('aria-label') || '').trim().slice(0, 40)])])`, returnByValue: true });
    const v = r.result?.result?.value; if (!v) continue;
    const [final, links] = JSON.parse(v);
    for (const [abs, raw, label] of links) {
      (result[page] ??= []).push({ lang, abs, raw, label });
      if (abs.startsWith(origin) && /(\/|\.html)$/.test(new URL(abs).pathname)) {
        const n = norm(abs); if (!seen.has(n) && !queue.includes(n)) queue.push(n);
      }
    }
  }
  process.stderr.write('.');
}
writeFileSync(out, JSON.stringify(result));
console.log(`${seen.size} pages parcourues`);
ws.close(); chrome.kill();
