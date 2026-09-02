/* WP-C1 — kiểm tra vòng đời zone và bất biến TOTAL = A + R + D trong MỘT tháng.
 * BẢO TRÌ T-09B (2026-09-02): trang chạy trên Firebase (harness emulator); state đọc từ bản
 * DURABLE đã đối chiếu với bộ nhớ trang. Kịch bản GIỮ NGUYÊN.
 * BẢO TRÌ T-09A (2026-09-02): thêm MỘT bước tiền đề — nhập chuỗi ngày giảm giá qua đúng UI
 * "Nhập số liệu" để mở Smart unlock. Trước T-09A, kịch bản reserve 100% Smart available khi
 * Smart unlock = 0%, tức đúng hành vi mà V-02 tố cáo là SAI (Strategy §12). Sau bản vá,
 * thao tác đó bị TỪ CHỐI, nên tiền đề là bắt buộc để kịch bản còn dựng được. Các bước và
 * assertion phía sau GIỮ NGUYÊN.
 */
const { chromium } = require('playwright');
const path = require('path');
const H = require('./test_helpers.js');

// __dirname thay vì cwd: test phải chạy đúng bất kể được gọi từ đâu — F-027.
const DIR = __dirname;
const APP_FINAL = path.join(DIR, 'app_final.html');
const SEED_PATH = path.join(DIR, '..', 'demo', 'results3', 'live_seed.json');

(async () => {
  const stopEmu = await H.ensureEmulators();
  const b = await chromium.launch({ executablePath: H.CHROMIUM });
  const { ctx, p, errs } = await H.newPage(b);

  const unlock0 = await H.pushDeclineDays(p, 12);
  console.log('-- Smart unlock sau tiền đề T-09A:', (unlock0.smartUnlock * 100).toFixed(2) + '%');

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

  let st = await H.readState(p);
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
  st = await H.readState(p);
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
  st = await H.readState(p);
  L = st.ladders[0];
  console.log('-- ladder after 2 closes above inv:', L.status, '| zones:', L.zones.map(z=>z.status).join(','));
  console.log('-- smart a/r/d after release:', Math.round(st.months['2026-06'].smart.a), Math.round(st.months['2026-06'].smart.r), Math.round(st.months['2026-06'].smart.d));
  console.log('-- total after release:', Math.round(st.months['2026-06'].smart.a + st.months['2026-06'].smart.r + st.months['2026-06'].smart.d));

  await p.click('[data-tab="history"]'); await p.waitForTimeout(200);
  console.log('-- trade rows:', await p.$$eval('#tradeTable tbody tr', r=>r.length));
  await p.screenshot({path: path.join(DIR, 'app-zone.png'), fullPage:true});
  await ctx.close(); await b.close(); await stopEmu();
  console.log(errs.length ? '\nERRORS:\n'+errs.join('\n') : '\nno errors');
  if (errs.length) process.exit(1);
})();
