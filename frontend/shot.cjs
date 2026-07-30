const { chromium } = require('playwright');
const path = require('path');
const outDir = 'C:/Users/julia/AppData/Local/Temp/claude/c--Users-julia-OneDrive-Documents-GitHub-PrismaTest/5945b9be-f2e6-4a4a-a625-68085beac540/scratchpad/shots';
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://localhost:5173/app/professor.html', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(500);
  await page.click('.avbtn[data-dd="dd-user"]');
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(outDir, 'menu-conta.png'), fullPage: false });
  await page.click('#dd-user a[data-modal="conta"]');
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(outDir, 'modal-conta.png'), fullPage: false });
  console.log('OK');
  await browser.close();
})();
