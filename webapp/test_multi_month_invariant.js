/* WP-C1 — CHECK-C1-06 / Subtask C1.7: bất biến kế toán TOTAL = AVAILABLE + RESERVED + DEPLOYED
 * qua chuỗi fill toàn phần -> fill một phần -> invalidation -> release, trải trên nhiều tháng.
 * Không sửa app_logic.js/engine.js — chỉ đọc, không vá.
 */
const { chromium } = require('playwright');
const path = require('path');

const DIR = __dirname;
const APP_FINAL = path.join(DIR, 'app_final.html');
const SEED_PATH = path.join(DIR, '..', 'demo', 'results3', 'live_seed.json');

let failures = 0;
function assert(cond, label) {
  if (!cond) { failures++; console.log('  ASSERT FAIL:', label); }
  else console.log('  ok:', label);
}

function poolTotal(x) { return x.a + x.r + x.d; }
function noNegative(x, label) {
  const neg = x.a < -1e-6 || x.r < -1e-6 || x.d < -1e-6;
  assert(!neg, label + ' không âm (a=' + x.a + ' r=' + x.r + ' d=' + x.d + ')');
  return !neg;
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 1200, height: 1000 } });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  p.on('console', m => { if (m.type() === 'error' && !/ERR_CONNECTION|font/i.test(m.text())) errs.push(m.text()); });

  await p.goto('file://' + APP_FINAL);
  await p.waitForTimeout(300);
  await p.setInputFiles('#seedFile', SEED_PATH);
  await p.waitForTimeout(900);

  const readState = () => p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));

  // --- Tháng 1 (2026-06): nạp vốn, tạo ladder cap = toàn bộ Smart available ---
  await p.click('[data-tab="entry"]');
  await p.fill('#cbMonth', '2026-06');
  await p.fill('#cbAmt', '10000000');
  await p.click('#cbAdd');
  await p.waitForTimeout(250);

  let st = await readState();
  console.log('--- Sau contribution tháng 1 (2026-06) ---');
  assert(poolTotal(st.months['2026-06'].smart) - 3000000 < 1e-6 &&
    poolTotal(st.months['2026-06'].smart) - 3000000 > -1e-6, 'TOTAL smart tháng 1 = 3.000.000 đúng bằng 30% contribution');
  noNegative(st.months['2026-06'].smart, 'smart pool tháng 1');

  await p.click('[data-tab="ladder"]');
  await p.waitForTimeout(150);
  await p.fill('#ldAnchor', '480');
  await p.fill('#ldCap', '3000000');
  await p.click('#ldAdd');
  await p.waitForTimeout(300);
  console.log('ldMsg:', (await p.textContent('#ldMsg')).trim());

  st = await readState();
  const ladderId = st.ladders[st.ladders.length - 1].id;
  console.log('--- Sau tạo ladder (reserve toàn bộ Smart tháng 1) ---');
  console.log('  smart pool:', JSON.stringify(st.months['2026-06'].smart));
  assert(Math.abs(poolTotal(st.months['2026-06'].smart) - 3000000) < 1e-6, 'TOTAL smart tháng 1 vẫn = 3.000.000 sau reserve (a->r, không đổi tổng)');
  noNegative(st.months['2026-06'].smart, 'smart pool tháng 1 sau reserve');

  // --- Đổi VND -> USDT qua P2P để có kho USDT thực thi lệnh mua ---
  await p.click('[data-tab="entry"]');
  await p.fill('#p2pVnd', '5000000');
  await p.fill('#p2pUsdt', '196.5');
  await p.fill('#p2pFee', '0');
  await p.click('#p2pAdd');
  await p.waitForTimeout(250);
  console.log('p2pMsg:', (await p.textContent('#p2pMsg')).trim());

  // --- Fill toàn phần zone 0 ---
  const zoneOpts = await p.$$eval('#buyZone option', o => o.map(x => x.value));
  const s0 = zoneOpts.filter(v => v.endsWith('|0'))[0];
  await p.click('[data-tab="entry"]');
  await p.selectOption('#buyZone', s0);
  await p.fill('#buyUsdt', '38.91');
  await p.fill('#buyPrice', '203.99');
  await p.fill('#buyRec', '203.99');
  await p.fill('#buyVndRate', '25445');
  await p.click('#buyAdd');
  await p.waitForTimeout(300);
  console.log('buyMsg (fill toàn phần zone 0):', (await p.textContent('#buyMsg')).trim());

  st = await readState();
  console.log('--- Sau fill toàn phần zone 0 ---');
  console.log('  smart pool:', JSON.stringify(st.months['2026-06'].smart));
  assert(Math.abs(poolTotal(st.months['2026-06'].smart) - 3000000) < 1e-6, 'TOTAL smart tháng 1 vẫn = 3.000.000 sau fill toàn phần (r->d, không đổi tổng)');
  noNegative(st.months['2026-06'].smart, 'smart pool tháng 1 sau fill toàn phần');

  // --- Fill một phần zone 1 ---
  const s1 = zoneOpts.filter(v => v.endsWith('|1'))[0];
  await p.click('[data-tab="ladder"]');
  await p.waitForTimeout(100);
  await p.click('[data-tab="entry"]');
  await p.selectOption('#buyZone', s1);
  await p.fill('#buyUsdt', '10');
  await p.fill('#buyPrice', '200');
  await p.fill('#buyVndRate', '25445');
  await p.click('#buyAdd');
  await p.waitForTimeout(300);
  console.log('buyMsg (fill một phần zone 1):', (await p.textContent('#buyMsg')).trim());

  st = await readState();
  console.log('--- Sau fill một phần zone 1 ---');
  console.log('  smart pool:', JSON.stringify(st.months['2026-06'].smart));
  assert(Math.abs(poolTotal(st.months['2026-06'].smart) - 3000000) < 1e-6, 'TOTAL smart tháng 1 vẫn = 3.000.000 sau fill một phần');
  noNegative(st.months['2026-06'].smart, 'smart pool tháng 1 sau fill một phần');

  // --- Sang tháng 2 (2026-07): nạp vốn mới -> currentMonth() chuyển sang tháng 2 ---
  await p.click('[data-tab="entry"]');
  await p.fill('#cbMonth', '2026-07');
  await p.fill('#cbAmt', '8000000');
  await p.click('#cbAdd');
  await p.waitForTimeout(250);

  st = await readState();
  console.log('--- Sau contribution tháng 2 (2026-07) — currentMonth() giờ là tháng 2 ---');
  console.log('  smart tháng 1:', JSON.stringify(st.months['2026-06'].smart));
  console.log('  smart tháng 2:', JSON.stringify(st.months['2026-07'].smart));
  assert(Math.abs(poolTotal(st.months['2026-06'].smart) - 3000000) < 1e-6, 'TOTAL smart tháng 1 không đổi khi tháng 2 mở ra');
  assert(Math.abs(poolTotal(st.months['2026-07'].smart) - 2400000) < 1e-6, 'TOTAL smart tháng 2 = 30% của 8.000.000');
  noNegative(st.months['2026-06'].smart, 'smart pool tháng 1');
  noNegative(st.months['2026-07'].smart, 'smart pool tháng 2');
  const month1_reservedBeforeInvalidation = st.months['2026-06'].smart.r;
  const month2_beforeInvalidation = JSON.parse(JSON.stringify(st.months['2026-07'].smart));

  // --- Invalidation: 2 daily close liên tiếp trên invalidation price -> release tự động ---
  // Việc release này chạy trong ngữ cảnh tháng 2 đang là currentMonth() — đây chính là kịch
  // bản thật (không thao túng thủ công) mà V-01 mô tả: ladder thuộc tháng 1 nhưng release
  // chạy theo currentMonth() = tháng 2.
  const inv = st.ladders.filter(l => l.id === ladderId)[0].invalidation_price;
  console.log('invalidation price:', inv);
  await p.click('[data-tab="entry"]');
  await p.waitForTimeout(100);
  for (const d of ['2026-08-30', '2026-08-31']) {
    await p.fill('#pxDate', d);
    await p.fill('#pxEth', String(inv * 1.02));
    await p.fill('#pxBtc', '350000');
    await p.fill('#pxVol', '100000');
    await p.click('#pxAdd');
    await p.waitForTimeout(250);
  }

  st = await readState();
  const L = st.ladders.filter(x => x.id === ladderId)[0];
  console.log('--- Sau invalidation + release tự động ---');
  console.log('  ladder status:', L.status, '| zones:', L.zones.map(z => z.index + ':' + z.status).join(','));
  console.log('  smart tháng 1 (2026-06):', JSON.stringify(st.months['2026-06'].smart));
  console.log('  smart tháng 2 (2026-07):', JSON.stringify(st.months['2026-07'].smart));

  const total1After = poolTotal(st.months['2026-06'].smart);
  const total2After = poolTotal(st.months['2026-07'].smart);
  noNegative(st.months['2026-06'].smart, 'smart pool tháng 1 sau invalidation/release');
  noNegative(st.months['2026-07'].smart, 'smart pool tháng 2 sau invalidation/release');
  assert(Math.abs(total1After - 3000000) < 1e-6, 'TOTAL smart tháng 1 (tự thân, a+r+d) vẫn = 3.000.000 sau release — không tiền nào bị nhân bản/mất theo phép cộng thô');
  assert(Math.abs(total2After - poolTotal(month2_beforeInvalidation)) < 1e-6, 'TOTAL smart tháng 2 (tự thân, a+r+d) không đổi — phần release chỉ dịch chuyển RESERVED<->AVAILABLE trong nội bộ tháng 2, không đổi tổng của tháng 2');

  const zoneOpen = L.zones.filter(z => z.status !== 'EXECUTED');
  const expectedRelease = zoneOpen.reduce((s, z) => s + Math.max(0, z.target_vnd - (z.filled_vnd || 0)), 0);
  console.log('  reserved còn kẹt ở tháng 1 sau release (phải về 0 nếu đúng):', st.months['2026-06'].smart.r);
  console.log('  reserved tháng 1 TRƯỚC release:', month1_reservedBeforeInvalidation);

  const month1_r_stuck = st.months['2026-06'].smart.r > 1e-6;

  console.log('\n--- KẾT LUẬN CHECK-C1-06 (bất biến kế toán đa tháng) ---');
  console.log('Bất biến thô "TOTAL(tháng) = A+R+D không đổi trừ contribution mới, không pool âm" GIỮ ĐÚNG ' +
    'ở CẢ HAI tháng qua toàn bộ chuỗi full-fill -> partial-fill -> contribution tháng mới -> invalidation -> release.');
  if (month1_r_stuck) {
    console.log('NHƯNG bất biến thô này KHÔNG đủ để phát hiện lỗi V-01: reserved còn lại của tháng 1 (' +
      st.months['2026-06'].smart.r + ' đ, phần chưa fill của zone 1+2 bị invalidate/cancel) không hề ' +
      'giảm sau khi ladder đã INVALIDATED — nó vẫn cộng đúng vào TOTAL tháng 1 (nên phép kiểm TOTAL ' +
      'không phát hiện ra gì bất thường) nhưng về nghiệp vụ đó là vốn KẸT VĨNH VIỄN, không dùng lại ' +
      'được cho ladder mới. Nguyên nhân: releaseLadder() (app_logic.js:302-322) ghi `take = ' +
      'Math.min(open, m.smart.r)` với `m = month(currentMonth())` — currentMonth() lúc này là tháng 2 ' +
      '(2026-07), và tháng 2 có `smart.r = 0` (không có ladder riêng đang reserve) nên `take = 0`: KHÔNG ' +
      'gì được release, ở CẢ HAI tháng. So sánh với ca kiểm thử V-01 riêng (test_v01_v02_v03.js), khi ' +
      'tháng bị trả nhầm CÓ sẵn reserved thật (ví dụ từ một ladder riêng của chính nó), `take` khớp ' +
      'dương và vốn bị CHUYỂN NHẦM sang `smart.a` của tháng đó thay vì tháng 1 — tuỳ tình trạng reserved ' +
      'của tháng đang là currentMonth() tại thời điểm release, hậu quả là KẸT VỐN (ca này) hoặc CHUYỂN ' +
      'NHẦM POOL (ca V-01 riêng) — cả hai đều là hệ quả trực tiếp của cùng một root cause: releaseLadder() ' +
      'dùng currentMonth() thay vì tháng gốc của ladder.');
  } else {
    console.log('Không quan sát thấy dấu hiệu kẹt vốn/lệch tháng trong lần chạy này.');
  }

  assert(errs.length === 0, 'không có page error trong toàn bộ kịch bản: ' + errs.join('; '));
  await ctx.close(); await b.close();

  if (failures > 0) {
    console.log('\n' + failures + ' assertion(s) FAILED.');
    process.exit(1);
  }
  console.log('\nTất cả assertion PASS. Bất biến TOTAL=A+R+D + non-negative giữ đúng qua toàn bộ kịch bản đa tháng (E1).');
})();
