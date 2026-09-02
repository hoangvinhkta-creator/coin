const { chromium } = require('playwright');
const path = require('path');

// __dirname thay vì cwd: test phải chạy đúng bất kể được gọi từ đâu — F-027.
const DIR = __dirname;
const APP_FINAL = path.join(DIR, 'app_final.html');
const SEED_PATH = path.join(DIR, '..', 'demo', 'results3', 'live_seed.json');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await (await b.newContext({viewport:{width:1200,height:1000}})).newPage();
  const errs = [];
  p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  p.on('console', m => { if (m.type()==='error' && !/ERR_CONNECTION|font/i.test(m.text())) errs.push(m.text()); });
  await p.goto('file://' + APP_FINAL);
  await p.waitForTimeout(300);
  await p.setInputFiles('#seedFile', SEED_PATH);
  await p.waitForTimeout(800);

  await p.click('[data-tab="entry"]');
  await p.fill('#cbMonth','2026-06'); await p.fill('#cbAmt','10000000'); await p.click('#cbAdd');
  await p.waitForTimeout(200);
  await p.fill('#p2pVnd','5000000'); await p.fill('#p2pUsdt','196.5'); await p.click('#p2pAdd');
  await p.waitForTimeout(200);

  await p.click('[data-tab="ladder"]');
  await p.fill('#ldCap','3000000'); await p.click('#ldAdd');
  await p.waitForTimeout(300);

  await p.click('[data-tab="entry"]');
  await p.waitForTimeout(200);
  const opts = await p.$$eval('#buyZone option', o => o.map(x => x.textContent.trim()));
  console.log('-- zone options:', JSON.stringify(opts));

  // chọn zone S0 và mua đúng phần còn lại
  const s0 = await p.$$eval('#buyZone option', o => o.map(x=>x.value).filter(v=>v.endsWith('|0'))[0]);
  await p.selectOption('#buyZone', s0);
  // S0 target = 990.000 VND, rate 25445 -> ~38.91 USDT
  await p.fill('#buyUsdt','38.91'); await p.fill('#buyPrice','203.99');
  await p.fill('#buyRec','203.99'); await p.fill('#buyVndRate','25445');
  await p.click('#buyAdd'); await p.waitForTimeout(300);
  console.log('-- buy msg:', (await p.textContent('#buyMsg')).trim());

  let st = await p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));
  let L = st.ladders[0];
  console.log('-- zone statuses:', L.zones.map(z=>z.index+':'+z.status+'/'+Math.round(z.filled_vnd||0)).join(' '));
  console.log('-- smart pool a/r/d:', Math.round(st.months['2026-06'].smart.a), Math.round(st.months['2026-06'].smart.r), Math.round(st.months['2026-06'].smart.d));
  console.log('-- total preserved:', Math.round(st.months['2026-06'].smart.a + st.months['2026-06'].smart.r + st.months['2026-06'].smart.d), '(expect 3000000)');

  // mua thiếu -> PARTIALLY_FILLED
  const s1 = await p.$$eval('#buyZone option', o => o.map(x=>x.value).filter(v=>v.endsWith('|1'))[0]);
  await p.selectOption('#buyZone', s1);
  await p.fill('#buyUsdt','10'); await p.fill('#buyPrice','200'); await p.fill('#buyVndRate','25445');
  await p.click('#buyAdd'); await p.waitForTimeout(300);
  console.log('-- partial msg:', (await p.textContent('#buyMsg')).trim());
  st = await p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));
  L = st.ladders[0];
  console.log('-- after partial:', L.zones.map(z=>z.index+':'+z.status+'/'+Math.round(z.filled_vnd||0)).join(' '));
  console.log('-- smart a/r/d:', Math.round(st.months['2026-06'].smart.a), Math.round(st.months['2026-06'].smart.r), Math.round(st.months['2026-06'].smart.d));
  console.log('-- total:', Math.round(st.months['2026-06'].smart.a + st.months['2026-06'].smart.r + st.months['2026-06'].smart.d));

  // bullish invalidation: 2 daily close trên invalidation price
  const inv = L.invalidation_price;
  console.log('-- invalidation price:', inv.toFixed(2));
  for (const d of ['2026-06-30','2026-07-01']) {
    await p.fill('#pxDate', d);
    await p.fill('#pxEth', String(inv * 1.02));
    await p.fill('#pxBtc', '350000'); await p.fill('#pxVol','100000');
    await p.click('#pxAdd'); await p.waitForTimeout(250);
  }
  st = await p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));
  L = st.ladders[0];
  console.log('-- ladder after 2 closes above inv:', L.status, '| zones:', L.zones.map(z=>z.status).join(','));
  console.log('-- smart a/r/d after release:', Math.round(st.months['2026-06'].smart.a), Math.round(st.months['2026-06'].smart.r), Math.round(st.months['2026-06'].smart.d));
  console.log('-- total after release:', Math.round(st.months['2026-06'].smart.a + st.months['2026-06'].smart.r + st.months['2026-06'].smart.d));

  await p.click('[data-tab="history"]'); await p.waitForTimeout(200);
  console.log('-- trade rows:', await p.$$eval('#tradeTable tbody tr', r=>r.length));
  await p.screenshot({path: path.join(DIR, 'app-zone.png'), fullPage:true});
  await b.close();
  console.log(errs.length ? '\nERRORS:\n'+errs.join('\n') : '\nno errors');
})();
