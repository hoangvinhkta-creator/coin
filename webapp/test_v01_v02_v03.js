/* WP-C1 — CHECK-C1-03/04/05: kết luận E1 cho V-01, V-02, V-03 bằng ca kiểm thử chạy thật
 * trên app_final.html đã build. Không sửa app_logic.js/engine.js — chỉ đọc, không vá.
 * Mỗi khối in ra XÁC NHẬN hoặc BÁC BỎ kèm số liệu — không để lửng.
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

async function newPage(b) {
  const ctx = await b.newContext({ viewport: { width: 1200, height: 1000 } });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  p.on('console', m => { if (m.type() === 'error' && !/ERR_CONNECTION|font/i.test(m.text())) errs.push(m.text()); });
  await p.goto('file://' + APP_FINAL);
  await p.waitForTimeout(300);
  return { ctx, p, errs };
}

async function readState(p) {
  return p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));
}

/* ---------------------------------------------------------------------- */
/* V-02 — Mức unlock có giới hạn số vốn được reserve hay không (CHECK-C1-04) */
/* ---------------------------------------------------------------------- */
async function testV02(b) {
  console.log('\n=== V-02 — unlock vs reserve ===');
  const { ctx, p, errs } = await newPage(b);

  await p.setInputFiles('#seedFile', SEED_PATH);
  await p.waitForTimeout(900);
  const chips = (await p.textContent('#stateChips')).replace(/\s+/g, ' ').trim();
  console.log('  chips sau khi nạp seed:', chips);
  const unlockMatch = chips.match(/Smart unlock ([\d.]+)%/);
  const smartUnlockPct = unlockMatch ? parseFloat(unlockMatch[1]) : NaN;
  console.log('  Smart unlock hiện tại:', smartUnlockPct, '%');
  assert(Number.isFinite(smartUnlockPct), 'đọc được Smart unlock % từ UI');

  await p.click('[data-tab="entry"]');
  await p.fill('#cbMonth', '2026-06');
  await p.fill('#cbAmt', '10000000');
  await p.click('#cbAdd');
  await p.waitForTimeout(250);

  let st = await readState(p);
  const smartAvailBefore = st.months['2026-06'].smart.a;
  console.log('  Smart available sau contribution:', smartAvailBefore, '(30% của 10.000.000)');

  // Cố ý reserve 100% available trong khi unlock < 100% (thực tế đo được ở trên).
  await p.click('[data-tab="ladder"]');
  await p.waitForTimeout(150);
  await p.fill('#ldAnchor', '480');
  await p.fill('#ldCap', String(smartAvailBefore));
  await p.click('#ldAdd');
  await p.waitForTimeout(300);
  const ldMsg = (await p.textContent('#ldMsg')).trim();
  console.log('  ldMsg:', ldMsg);

  st = await readState(p);
  const reservedAfter = st.months['2026-06'].smart.r;
  const availAfter = st.months['2026-06'].smart.a;
  console.log('  smart pool sau reserve — a:', availAfter, 'r:', reservedAfter);

  const reserveExceededUnlock = smartUnlockPct < 99.95 && reservedAfter >= smartAvailBefore - 1e-6;
  console.log('  --- KẾT LUẬN V-02 ---');
  if (reserveExceededUnlock) {
    console.log('  XÁC NHẬN: reserveFor() cho reserve 100% available (' + reservedAfter +
      ' đ) trong khi Smart unlock chỉ ' + smartUnlockPct +
      '% — không có giới hạn nào áp theo mức unlock. reserveFor() (app_logic.js:289-297) ' +
      'chỉ so sánh với `m.smart.a`, không tham chiếu `view.smartUnlock` ở bất kỳ đâu trong ' +
      'createLadder()/reserveFor().');
  } else {
    console.log('  BÁC BỎ: reserve bị chặn hoặc giới hạn đúng theo mức unlock đo được.');
  }
  assert(errs.length === 0, 'không có page error trong kịch bản V-02: ' + errs.join('; '));
  await ctx.close();
  return { smartUnlockPct, reservedAfter, smartAvailBefore, confirmed: reserveExceededUnlock };
}

/* ---------------------------------------------------------------------- */
/* V-03 — INVALID có chặn tạo action mới hay không (CHECK-C1-05) */
/* ---------------------------------------------------------------------- */
async function testV03(b) {
  console.log('\n=== V-03 — INVALID vs tạo ladder ===');
  const { ctx, p, errs } = await newPage(b);

  // KHÔNG nạp seed — nhập tay 5 ngày (dưới ngưỡng cần cho mọi sub-factor: S7 cần i>=7,
  // R(rsi14) cần n>14 → với n=5 cả 8 sub-factor đều NaN => data_quality = INVALID
  // (engine.js:190, factorScores). ADR30 (cần 30 ngày) cũng NaN ở vùng này — đây chính là
  // điều cần đo: guard nào thực sự chặn, và INVALID có được kiểm tra RIÊNG hay không.
  await p.click('[data-tab="entry"]');
  const days = [
    ['2026-08-20', '4200', '96000', '150000'],
    ['2026-08-21', '4210', '96200', '151000'],
    ['2026-08-22', '4195', '95900', '149500'],
    ['2026-08-23', '4230', '96500', '152000'],
    ['2026-08-24', '4250', '96800', '153000'],
  ];
  for (const [d, e, bp, v] of days) {
    await p.fill('#pxDate', d);
    await p.fill('#pxEth', e);
    await p.fill('#pxBtc', bp);
    await p.fill('#pxVol', v);
    await p.click('#pxAdd');
    await p.waitForTimeout(150);
  }
  const chips = (await p.textContent('#stateChips')).replace(/\s+/g, ' ').trim();
  console.log('  chips sau 5 ngày nhập tay:', chips);
  const isInvalid = /INVALID/.test(chips);
  assert(isInvalid, 'data_quality hiển thị INVALID với 5 ngày lịch sử');

  // Nạp vốn Smart để available > 0 — nếu không, mọi block sẽ do "không đủ vốn", không đo
  // được guard nào đang thực sự chặn.
  await p.fill('#cbMonth', '2026-08');
  await p.fill('#cbAmt', '10000000');
  await p.click('#cbAdd');
  await p.waitForTimeout(250);
  let st = await readState(p);
  console.log('  Smart available trước khi thử tạo ladder:', st.months['2026-08'].smart.a);

  await p.click('[data-tab="ladder"]');
  await p.waitForTimeout(150);
  await p.fill('#ldAnchor', '4200');
  await p.fill('#ldCap', '1000000');
  await p.click('#ldAdd');
  await p.waitForTimeout(300);
  const ldMsg = (await p.textContent('#ldMsg')).trim();
  console.log('  ldMsg:', ldMsg);

  st = await readState(p);
  const ladderCreated = (st.ladders || []).length > 0;
  console.log('  ladder được tạo:', ladderCreated, '| tổng số ladder:', (st.ladders || []).length);

  console.log('  --- KẾT LUẬN V-03 ---');
  if (ladderCreated) {
    console.log('  XÁC NHẬN: ladder được tạo thành công dù data_quality = INVALID — createLadder() ' +
      '(app_logic.js:324-335) không có bất kỳ điều kiện nào kiểm tra `view.score.data_quality`.');
  } else {
    console.log('  BÁC BỎ (về mặt hành vi quan sát được): ladder KHÔNG được tạo khi INVALID. ' +
      'Message thực tế: "' + ldMsg + '". LƯU Ý QUAN TRỌNG: đọc app_logic.js:324-335 xác nhận ' +
      'createLadder() không hề kiểm tra `data_quality` một cách tường minh — block quan sát được ' +
      'ở đây đến từ guard `!Number.isFinite(sp)` (ADR30 cần 30 ngày liên tục, engine.js smartSpacing), ' +
      'guard này TÌNH CỜ trùng với vùng INVALID (INVALID cần <7 ngày lịch sử để mọi sub-factor NaN, ' +
      'ADR30 cần >=30 ngày — hai điều kiện không giao nhau theo toán học của engine.js, nên INVALID ' +
      'và "đủ dữ liệu để tính spacing" không bao giờ cùng đúng). Hành vi hiện tại AN TOÀN nhưng ' +
      'KHÔNG PHẢI do một kiểm tra INVALID tường minh — đây là HARDENING finding, không phải lý do ' +
      'để hạ kết luận BÁC BỎ.');
  }
  assert(errs.length === 0, 'không có page error trong kịch bản V-03: ' + errs.join('; '));
  await ctx.close();
  return { isInvalid, ladderCreated, ldMsg };
}

/* ---------------------------------------------------------------------- */
/* V-01 — Release vốn có trả nhầm pool đa tháng hay không (CHECK-C1-03) */
/* ---------------------------------------------------------------------- */
async function testV01(b) {
  console.log('\n=== V-01 — release đa tháng có trả đúng pool không ===');
  const { ctx, p, errs } = await newPage(b);

  await p.setInputFiles('#seedFile', SEED_PATH);
  await p.waitForTimeout(900);

  // Tháng A = 2026-06: nạp vốn rồi tạo ladder LA — reserve đến từ pool của CHÍNH tháng A.
  await p.click('[data-tab="entry"]');
  await p.fill('#cbMonth', '2026-06');
  await p.fill('#cbAmt', '10000000');
  await p.click('#cbAdd');
  await p.waitForTimeout(250);

  await p.click('[data-tab="ladder"]');
  await p.waitForTimeout(150);
  await p.fill('#ldAnchor', '480');
  await p.fill('#ldCap', '1000000');
  await p.click('#ldAdd');
  await p.waitForTimeout(300);
  console.log('  ldMsg (tạo ladder LA, tháng A):', (await p.textContent('#ldMsg')).trim());

  let st = await readState(p);
  const monthA_afterReserve = JSON.parse(JSON.stringify(st.months['2026-06'].smart));
  console.log('  Tháng A (2026-06) sau reserve LA — a:', monthA_afterReserve.a, 'r:', monthA_afterReserve.r);
  assert(monthA_afterReserve.r >= 1000000 - 1e-6, 'reserve 1.000.000 đã trừ vào tháng A (2026-06)');
  const ladderIdA = st.ladders[st.ladders.length - 1].id;

  // Tháng B = 2026-07 mới hơn — nạp vốn RỒI tạo ladder LB CỦA RIÊNG tháng B, để tháng B có
  // reserved (r) thật của chính nó. currentMonth() (key lớn nhất) giờ trỏ về tháng B.
  await p.click('[data-tab="entry"]');
  await p.fill('#cbMonth', '2026-07');
  await p.fill('#cbAmt', '10000000');
  await p.click('#cbAdd');
  await p.waitForTimeout(250);

  await p.click('[data-tab="ladder"]');
  await p.waitForTimeout(150);
  await p.fill('#ldAnchor', '480');
  await p.fill('#ldCap', '2000000');
  await p.click('#ldAdd');
  await p.waitForTimeout(300);
  console.log('  ldMsg (tạo ladder LB, tháng B):', (await p.textContent('#ldMsg')).trim());

  st = await readState(p);
  const monthB_beforeReleaseA = JSON.parse(JSON.stringify(st.months['2026-07'].smart));
  console.log('  Tháng B (2026-07) sau reserve LB (trước khi huỷ LA) — a:', monthB_beforeReleaseA.a,
    'r:', monthB_beforeReleaseA.r, '(currentMonth() giờ trỏ về đây vì key lớn hơn)');
  const ladderIdB = st.ladders[st.ladders.length - 1].id;

  // Hủy LA (ladder của THÁNG A) -> cancelLadder() -> releaseLadder(LA), hàm dùng currentMonth()
  // thay vì tháng gốc của LA. LB (ladder RIÊNG của tháng B, vẫn ACTIVE) không hề bị đụng tới
  // theo thiết kế — nhưng vì releaseLadder(LA) ghi vào pool của currentMonth(), nó sẽ cộng/trừ
  // đúng vào pool đang backing cho LB.
  await p.click('[data-cancel="' + ladderIdA + '"]', { force: true });
  await p.waitForTimeout(300);

  st = await readState(p);
  const monthA_afterRelease = st.months['2026-06'].smart;
  const monthB_afterRelease = st.months['2026-07'].smart;
  const ladderA = st.ladders.filter(x => x.id === ladderIdA)[0];
  const ladderB = st.ladders.filter(x => x.id === ladderIdB)[0];
  console.log('  Tháng A (2026-06) SAU khi huỷ LA — a:', monthA_afterRelease.a, 'r:', monthA_afterRelease.r,
    '| LA.status:', ladderA.status);
  console.log('  Tháng B (2026-07) SAU khi huỷ LA — a:', monthB_afterRelease.a, 'r:', monthB_afterRelease.r,
    '| LB.status:', ladderB.status, '(LB KHÔNG hề bị huỷ hay đụng tới trong kịch bản)');

  const releasedVnd = monthA_afterReserve.r; // 1.000.000, ladder LA cancel ngay, chưa fill gì
  const monthA_stuck = Math.abs(monthA_afterRelease.r - monthA_afterReserve.r) < 1e-6 &&
    monthA_afterRelease.a < monthA_afterReserve.a + releasedVnd - 1e-6;
  const monthB_stolen = monthB_afterRelease.a >= monthB_beforeReleaseA.a + releasedVnd - 1e-6 &&
    monthB_afterRelease.r <= monthB_beforeReleaseA.r - releasedVnd + 1e-6;

  console.log('  --- KẾT LUẬN V-01 ---');
  if (monthB_stolen && monthA_stuck) {
    console.log('  XÁC NHẬN: huỷ ladder LA (thuộc tháng A, 2026-06) đã CỘNG ' + releasedVnd +
      ' đ vào `smart.a` của tháng B (2026-07) và TRỪ ' + releasedVnd + ' đ khỏi `smart.r` của tháng B — ' +
      'phần vốn đó thực ra đang BACKING cho ladder LB (ladder RIÊNG, vẫn ACTIVE, của chính tháng B), ' +
      'không liên quan gì tới LA. releaseLadder() (app_logic.js:302-322) dùng `mk = currentMonth()` ' +
      '(app_logic.js:124-127 — trả về key lớn nhất trong state.months) thay vì tháng LA thực sự được ' +
      'reserve ra. Hậu quả kép: (1) reserved của tháng A cho LA (' + monthA_afterReserve.r +
      ' đ) bị KẸT VĨNH VIỄN — LA đã CANCELLED, zones đã released_vnd nhưng `smart.r` tháng A không hề ' +
      'giảm; (2) reserved thật của LB bị RÚT NHẦM sang available, làm LB thiếu vốn backing dù vẫn ' +
      'ACTIVE. Đây đúng là lỗi "trả nhầm pool" mà V-01 nêu, và nghiêm trọng hơn: nó còn làm hỏng sổ ' +
      'của MỘT LADDER KHÁC đang hoạt động bình thường ở tháng bị trả nhầm vào.');
  } else {
    console.log('  BÁC BỎ: vốn release quay đúng về tháng A; tháng B/LB không bị ảnh hưởng. Số liệu: ' +
      JSON.stringify({ monthA_afterReserve, monthA_afterRelease, monthB_beforeReleaseA, monthB_afterRelease }));
  }
  assert(errs.length === 0, 'không có page error trong kịch bản V-01: ' + errs.join('; '));
  await ctx.close();
  return { monthA_afterReserve, monthA_afterRelease, monthB_beforeReleaseA, monthB_afterRelease, confirmed: monthB_stolen && monthA_stuck };
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const v02 = await testV02(b);
  const v03 = await testV03(b);
  const v01 = await testV01(b);
  await b.close();

  console.log('\n=== TÓM TẮT E1 ===');
  console.log('V-01 (release đa tháng sai pool):', v01.confirmed ? 'XÁC NHẬN' : 'BÁC BỎ');
  console.log('V-02 (unlock không giới hạn reserve):', v02.confirmed ? 'XÁC NHẬN' : 'BÁC BỎ');
  console.log('V-03 (INVALID không chặn tạo ladder):', v03.ladderCreated ? 'XÁC NHẬN' : 'BÁC BỎ (hành vi quan sát được — xem ghi chú kiến trúc ở trên)');

  if (failures > 0) {
    console.log('\n' + failures + ' assertion(s) FAILED — xem chi tiết ở trên.');
    process.exit(1);
  }
  console.log('\nTất cả assertion kỹ thuật PASS. Kết luận trên là bằng chứng E1 chạy thật.');
})();
