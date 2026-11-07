// Capture read-only screenshots of public pages for a case study.
//
// Run: node shoot.mjs <shots.json> <out-dir>
//
// shots.json is a list:
//   [{"url": "https://demo.example.com/", "file": "home-desktop.jpg", "width": 1440, "height": 900},
//    {"url": "https://demo.example.com/", "file": "home-phone.jpg", "width": 390, "height": 844, "dpr": 2,
//     "hide": ["[aria-label=\"Demo store notice\"]"], "wait": 2500}]
//
// Phones (width under 500) get isMobile and touch. Each page waits for network idle, then
// "wait" ms (default 2500), presses Escape once to close a promo popup, and hides the CSS
// selectors in "hide" (Next.js's dev overlay is always hidden). Only GET navigation happens:
// nothing is clicked or submitted.
//
// Needs Playwright with Chromium. It is loaded from the current directory's node_modules, then
// from a global install: `npm i -D playwright && npx playwright install chromium`.
import { createRequire } from 'node:module';
import { readFileSync, mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

const [, , shotsFile, outDir] = process.argv;
if (!shotsFile || !outDir) {
  console.error('usage: node shoot.mjs <shots.json> <out-dir>');
  process.exit(1);
}

// PLAYWRIGHT_MODULE may name a module path to load (e.g. a project's node_modules/playwright).
let chromium;
const requireHere = createRequire(join(process.cwd(), 'noop.js'));
for (const name of [process.env.PLAYWRIGHT_MODULE, 'playwright', '@playwright/test'].filter(Boolean)) {
  try {
    ({ chromium } = requireHere(name));
    break;
  } catch {
    try {
      ({ chromium } = await import(name));
      break;
    } catch {}
  }
}
if (!chromium) {
  console.error('Playwright not found. Run it from a project that has it, set PLAYWRIGHT_MODULE, or: npm i -D playwright && npx playwright install chromium');
  process.exit(1);
}

const shots = JSON.parse(readFileSync(shotsFile, 'utf8'));
mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch();
for (const s of shots) {
  const phone = (s.width ?? 1440) < 500;
  const ctx = await browser.newContext({
    viewport: { width: s.width ?? 1440, height: s.height ?? 900 },
    deviceScaleFactor: s.dpr ?? (phone ? 2 : 1),
    isMobile: phone,
    hasTouch: phone,
  });
  const page = await ctx.newPage();
  await page.goto(s.url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(s.wait ?? 2500);
  await page.keyboard.press('Escape').catch(() => {});
  const hide = ['nextjs-portal', ...(s.hide ?? [])].join(',');
  await page.addStyleTag({ content: `${hide}{display:none!important}` }).catch(() => {});
  await page.waitForTimeout(600);
  const file = resolve(outDir, s.file);
  await page.screenshot({ path: file, type: s.file.endsWith('.png') ? 'png' : 'jpeg', quality: s.file.endsWith('.png') ? undefined : 82 });
  console.log(`${s.url} -> ${file}`);
  await ctx.close();
}
await browser.close();
