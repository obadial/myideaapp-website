// node --experimental-websocket shot.mjs <out_dir> <locale> <width> <height> <url...>
// Capture chaque URL avec un stockage vidé et navigator.language = locale.
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
const [outDir, locale, W, H, ...urls] = process.argv.slice(2);
const PORT = String(9400 + Math.floor(Math.random() * 500));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--remote-debugging-port=' + PORT,
   '--user-data-dir=/private/tmp/claude-501/shot-' + PORT, '--lang=' + locale, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let t; for (let i = 0; i < 60; i++) { try { t = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json(); if (t.find(x => x.type === 'page')) break; } catch {} await sleep(200); }
const ws = new WebSocket(t.find(x => x.type === 'page').webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = new Map();
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); setTimeout(() => pend.has(i) && (pend.delete(i), r({})), 10000); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: +W, height: +H, deviceScaleFactor: 1, mobile: +W < 600 });
await send('Network.enable');
await send('Network.setUserAgentOverride', { userAgent: 'Mozilla/5.0 (Macintosh) Chrome/154 Safari/537.36', acceptLanguage: locale, platform: 'MacIntel' });
await send('Emulation.setLocaleOverride', { locale });
for (const u of urls) {
  await send('Storage.clearDataForOrigin', { origin: new URL(u).origin, storageTypes: 'all' });
  await send('Page.navigate', { url: u });
  await sleep(1800);
  const info = await send('Runtime.evaluate', { expression: `JSON.stringify({lang: document.documentElement.lang, nav: navigator.language, suggest: document.querySelector('.lang-suggest')?.innerText || null})`, returnByValue: true });
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  const name = u.replace(/^https?:\/\/[^/]+\//, '').replace(/[\/.]+/g, '_') || 'home';
  if (shot.result) writeFileSync(`${outDir}/${locale}_${W}_${name}.png`, Buffer.from(shot.result.data, 'base64'));
  console.log(locale, W, u, info.result?.result?.value);
}
ws.close(); chrome.kill();
