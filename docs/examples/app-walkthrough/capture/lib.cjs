// Playwright from the project, else the global install.
const { chromium } = (() => { try { return require('playwright'); } catch { return require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright'); } })();
const SEED = require('./seed.cjs');
const OUT = __dirname + '/png';
require('fs').mkdirSync(OUT, { recursive: true });
const APP = process.env.APP_URL || 'http://localhost:3000/';
// The app's IndexedDB database name (see its src/lib/kv.ts).
const APP_DB = process.env.APP_DB || 'app';
// Strip the app's name from every screen: the brand word in the top bar / sidebar / login, and any text node with it.
// The name to keep off every screen, e.g. BRAND="Acme Works" node capture.cjs (each word is scrubbed too).
const BRAND = (process.env.BRAND || '').trim();
const WORDS = BRAND ? [BRAND, ...BRAND.split(/\s+/).filter((w) => w.length > 3)] : [];
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const BRAND_RE = WORDS.length ? new RegExp(WORDS.map(esc).join('|'), 'gi') : null;
const SCRUB = (words) => {
  const re = words.length ? new RegExp(words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'gi') : null;
  try { sessionStorage.setItem('splash_seen', '1'); } catch {}
  const css = document.createElement('style');
  css.textContent = '.font-brand{display:none!important}';
  const scrub = (root) => {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n; while ((n = w.nextNode())) if (re && re.test(n.nodeValue)) { re.lastIndex = 0; n.nodeValue = n.nodeValue.replace(re, '').replace(/\s{2,}/g, ' '); }
  };
  const start = () => { document.head.appendChild(css); scrub(document.body); new MutationObserver(() => scrub(document.body)).observe(document.body, { subtree: true, childList: true, characterData: true }); };
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
};
async function launch(who = 'a1', { lang = 'en', viewport = { width: 390, height: 844 }, mutate } = {}) {
  const browser = await chromium.launch({ args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream', '--use-file-for-fake-video-capture=' + __dirname + '/cam.y4m'] });
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: 2, isMobile: true, hasTouch: true, geolocation: { latitude: 28.6508, longitude: 77.2663 }, permissions: ['geolocation', 'camera'] });
  await ctx.addInitScript(SCRUB, WORDS);
  // Take the app's name out of the code that makes PDFs, file names and WhatsApp text (case-sensitive: code ids are lowercase).
  await ctx.route((url) => url.href.startsWith(APP), async (route) => {
    const resp = await route.fetch(); const ct = resp.headers()['content-type'] || '';
    if (!/javascript|json|html|css/.test(ct)) return route.fulfill({ response: resp });
    let body = await resp.text();
    if (BRAND) {
      // Phrases first (so sentences still read), then the bare name and its words. Case-sensitive on
      // purpose: code identifiers are lowercase and must not change.
      const full = esc(BRAND), under = esc(BRAND.replace(/\s+/g, '_')), upper = esc(BRAND.toUpperCase());
      body = body.replace(new RegExp(' from ' + full, 'g'), '').replace(new RegExp(full + ' - ', 'g'), '').replace(new RegExp(upper + ' {2}· {2}', 'g'), '')
        .replace(new RegExp('Close ' + full + '\\?', 'g'), 'Close the app?').replace(new RegExp(under + '_', 'g'), '')
        .replace(new RegExp(full, 'g'), '').replace(new RegExp(upper, 'g'), '');
      for (const w of WORDS.slice(1)) body = body.replace(new RegExp(esc(w) + '_', 'g'), '').replace(new RegExp('\\b' + esc(w) + '\\b', 'g'), 'App');
    }
    return route.fulfill({ response: resp, body });
  });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => console.log('PAGEERROR', e.message));
  await page.goto(APP); await page.waitForTimeout(2000);
  let seed = who ? SEED(who) : {};
  if (lang) seed.language = lang;
  if (mutate) seed = mutate(seed) || seed;
  await page.evaluate(([seed, lang, db]) => new Promise((res) => { localStorage.clear(); if (lang) localStorage.setItem('language', lang);
    const r = indexedDB.open(db, 1); r.onupgradeneeded = () => r.result.createObjectStore('kv');
    r.onsuccess = () => { const tx = r.result.transaction('kv', 'readwrite'); const st = tx.objectStore('kv'); st.clear(); for (const [k, v] of Object.entries(seed)) st.put(v, k); tx.oncomplete = res; }; }), [seed, lang, APP_DB]);
  await page.reload(); await page.waitForTimeout(2500);
  return { browser, page };
}
async function snap(page, name, { full = false, wait = 600 } = {}) {
  await page.waitForTimeout(wait);
  const txt = await page.evaluate(() => document.body.innerText);
  if (BRAND_RE && BRAND_RE.test(txt)) { BRAND_RE.lastIndex = 0; console.log('!! BRAND LEAK in', name); }
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: full });
  console.log('snap', name);
}
const tap = async (page, loc, w = 700) => { await loc.click(); await page.waitForTimeout(w); };
const text = (page) => page.evaluate(() => document.body.innerText);
module.exports = { launch, snap, tap, text, OUT };
