// Audit rendu : chaque page × FR/EN/ES × bureau/mobile via Chrome DevTools Protocol.
// node --experimental-websocket audit.mjs <base> <pages...>
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';

const [base, ...pages] = process.argv.slice(2);
const PORT = process.env.PORT || '9333';
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--remote-debugging-port='+PORT, '--user-data-dir=/private/tmp/claude-501/audit-chrome-'+PORT, 'about:blank'],
  { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let targets;
for (let i = 0; i < 50; i++) {
  try { targets = await (await fetch('http://127.0.0.1:'+PORT+'/json')).json(); if (targets.find(t => t.type === 'page')) break; } catch {}
  await sleep(200);
}
const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
let id = 0; const pending = new Map(); const events = [];
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } else events.push(d); };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); setTimeout(() => { if (pending.has(i)) { pending.delete(i); r({ timeout: method }); } }, 8000); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async expr => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result?.result?.value;
await send('Network.enable'); await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');

const PROBE = `(() => {
  const vis = el => { const s = getComputedStyle(el); return s.display !== 'none' && s.visibility !== 'hidden' && el.offsetParent !== null || el === document.body; };
  const out = {};
  out.lang = document.documentElement.lang;
  out.title = document.title;
  out.desc = document.querySelector('meta[name=description]')?.content || '';
  out.canonical = document.querySelector('link[rel=canonical]')?.href || '';
  out.robots = document.querySelector('meta[name=robots]')?.content || '';
  out.h1 = [...document.querySelectorAll('h1')].filter(vis).map(h => h.innerText.trim());
  out.ogImage = document.querySelector('meta[property="og:image"]')?.content || '';
  out.viewport = !!document.querySelector('meta[name=viewport]');
  out.overflow = document.documentElement.scrollWidth - window.innerWidth;
  out.wide = out.overflow > 2 ? [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.right > window.innerWidth + 2 && r.width > 0 && vis(e); }).slice(0, 4).map(e => e.tagName + '.' + [...e.classList].join('.') + ' w=' + Math.round(e.getBoundingClientRect().right)) : [];
  out.brokenImg = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && vis(i)).map(i => i.getAttribute('src'));
  out.noAlt = [...document.images].filter(i => !i.hasAttribute('alt')).map(i => i.getAttribute('src'));
  out.text = document.body.innerText;
  out.emptyLinks = [...document.querySelectorAll('a')].filter(a => vis(a) && !a.innerText.trim() && !a.querySelector('img,svg') && !a.getAttribute('aria-label')).length;
  out.badHref = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(h => h === '#' || h === '' || /undefined|null/.test(h));
  out.i18nMissing = [...document.querySelectorAll('[data-i18n]')].filter(e => vis(e) && /^[a-z0-9_]+$/.test(e.innerText.trim()) && e.innerText.trim() === e.dataset.i18n).map(e => e.dataset.i18n);
  return out;
})()`;

const results = [];
for (const page of pages) {
  for (const lang of ['fr', 'en', 'es']) {
    for (const [w, h, mobile] of [[1280, 900, false], [390, 844, true]]) {
      await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile });
      events.length = 0;
      await send('Page.navigate', { url: base + '/' + page });
      await sleep(400);
      await ev(`localStorage.setItem('mia_lang','${lang}')`);
      events.length = 0;
      await send('Page.reload', { ignoreCache: true });
      await sleep(1400);
      const r = await ev(PROBE) || {};
      const failed = events.filter(e => e.method === 'Network.responseReceived' && e.params.response.status >= 400).map(e => e.params.response.status + ' ' + e.params.response.url)
        .concat(events.filter(e => e.method === 'Network.loadingFailed' && !e.params.canceled).map(e => 'FAIL ' + e.params.errorText + ' ' + (e.params.requestId)));
      const errors = events.filter(e => e.method === 'Runtime.exceptionThrown').map(e => e.params.exceptionDetails.exception?.description?.split('\n')[0] || e.params.exceptionDetails.text)
        .concat(events.filter(e => e.method === 'Log.entryAdded' && e.params.entry.level === 'error').map(e => e.params.entry.text + ' ' + (e.params.entry.url || '')));
      results.push({ page, lang, w, ...r, failed: [...new Set(failed)], errors: [...new Set(errors)] });
    }
  }
  process.stderr.write('.');
}
writeFileSync(process.env.OUT, JSON.stringify(results));
ws.close(); chrome.kill();
