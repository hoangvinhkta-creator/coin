/* T-09A — bất biến kế toán vốn của app web, chạy qua ĐƯỜNG SẢN PHẨM THẬT
 * (UI -> app_logic -> engine -> state đã lưu), trên app_final.html đã build.
 *
 * Sáu bất biến bắt buộc:
 *   A. Pool ownership isolation      — release/deploy của ladder này không đụng pool khác
 *   B. Active backing preservation   — vốn đang backing ladder ACTIVE không tự thành available
 *   C. Release upper bound           — released <= reserve hợp lệ của ĐÚNG owner
 *   D. Conservation                  — không tự sinh/mất vốn ngoài transition hợp lệ
 *   E. Multi-month                   — nhiều tháng không làm ownership nhập nhằng
 *   F. Existing valid behavior       — kịch bản sạch một tháng không đổi hành vi
 *
 * Ca kiểm thử KHÔNG hard-code con số của counterexample WP-C1: mọi hạn mức được so với
 * oracle tính lại từ CHÍNH engine.js dùng chung (test_helpers.readUnlock).
 */
const { chromium } = require('playwright');
const H = require('./test_helpers.js');

let failures = 0, checks = 0;
function assert(cond, label) {
  checks++;
  if (!cond) { failures++; console.log('  ASSERT FAIL:', label); }
  else console.log('  ok:', label);
}
const near = (a, b, tol) => Math.abs(a - b) <= (tol === undefined ? 1e-6 : tol);
function noNegative(x, label) {
  assert(x.a >= -1e-6 && x.r >= -1e-6 && x.d >= -1e-6,
    label + ' không âm (a=' + x.a + ' r=' + x.r + ' d=' + x.d + ')');
}
/** D — bảo toàn: mỗi pool tự thân giữ nguyên tổng trừ khi có contribution mới. */
function conservation(st, expected, label) {
  Object.keys(expected).forEach(function (mk) {
    const m = st.months[mk];
    assert(m && near(H.poolTotal(m.smart), expected[mk]),
      label + ' — TOTAL smart ' + mk + ' = ' + expected[mk] +
      ' (đo được ' + (m ? H.poolTotal(m.smart) : 'thiếu tháng') + ')');
    if (m) noNegative(m.smart, label + ' — smart ' + mk);
  });
}
/** B/C — vốn reserved của một tháng phải >= tổng cam kết chưa fill của các ladder ACTIVE
 *  thuộc CHÍNH tháng đó. */
function backingOk(st, mk, label) {
  const need = (st.ladders || [])
    .filter(L => L.status === 'ACTIVE' && L.type === 'SMART' && (L.month || null) === mk)
    .reduce((s, L) => s + L.zones.reduce(
      (t, z) => t + Math.max(0, z.target_vnd - (z.filled_vnd || 0)), 0), 0);
  const have = st.months[mk] ? st.months[mk].smart.r : 0;
  assert(have >= need - 1e-6,
    label + ' — reserved tháng ' + mk + ' (' + have + ') đủ backing cho ladder ACTIVE của ' +
    'chính tháng đó (' + need + ')');
}

/* ------------------------------------------------------------------ */
/* CA 1 — A + B + C + D + E: release đa tháng (counterexample V-01)     */
/* ------------------------------------------------------------------ */
async function caseMultiMonthRelease(b) {
  console.log('\n=== CA 1 — release đa tháng: ownership isolation / active backing / upper bound ===');
  const { ctx, p, errs } = await H.newPage(b);

  const unlock = await H.pushDeclineDays(p, 12);
  console.log('  OSCORE sau chuỗi ngày giảm:', unlock.oscore.toFixed(3),
    '| Smart unlock:', (unlock.smartUnlock * 100).toFixed(3) + '%');
  assert(unlock.smartUnlock > 0, 'dựng được trạng thái có Smart unlock > 0 qua đường nhập giá thật');

  // BA tháng, ladder nằm ở tháng KHÔNG phải key lớn nhất (yêu cầu của WP-C1 CHECK-C1-03).
  await H.contribute(p, '2026-05', 10000000);   // tháng A
  const capA = 3000000 * unlock.smartUnlock;
  const la = await H.makeLadder(p, 'SMART', 480, capA);
  console.log('  ldMsg (LA, tháng A 2026-05, cap =', capA.toFixed(2), '):', la.msg);
  assert(!!la.ladder && la.ladder.status === 'ACTIVE', 'LA được tạo ở tháng A');
  assert(la.ladder.month === '2026-05', 'LA mang tháng sở hữu tường minh = 2026-05 (thực tế: ' +
    la.ladder.month + ')');
  const idA = la.ladder.id;

  await H.contribute(p, '2026-06', 10000000);   // tháng B
  const capB = 3000000 * unlock.smartUnlock;
  const lb = await H.makeLadder(p, 'SMART', 480, capB);
  console.log('  ldMsg (LB, tháng B 2026-06):', lb.msg);
  assert(!!lb.ladder && lb.ladder.month === '2026-06', 'LB mang tháng sở hữu = 2026-06');
  const idB = lb.ladder.id;

  await H.contribute(p, '2026-07', 10000000);   // tháng C — nay là currentMonth()
  let st = await H.readState(p);
  const beforeA = JSON.parse(JSON.stringify(st.months['2026-05'].smart));
  const beforeB = JSON.parse(JSON.stringify(st.months['2026-06'].smart));
  const beforeC = JSON.parse(JSON.stringify(st.months['2026-07'].smart));
  console.log('  trước huỷ LA — A:', JSON.stringify(beforeA), 'B:', JSON.stringify(beforeB),
    'C:', JSON.stringify(beforeC));
  assert(near(beforeA.r, capA), 'reserve của LA nằm ở tháng A');
  assert(near(beforeC.r, 0), 'tháng C (currentMonth) chưa reserve gì');

  // Huỷ LA trong khi currentMonth() = tháng C và tháng B đang có reserve thật backing LB.
  await H.cancelLadder(p, idA);
  st = await H.readState(p);
  const afterA = st.months['2026-05'].smart;
  const afterB = st.months['2026-06'].smart;
  const afterC = st.months['2026-07'].smart;
  console.log('  sau huỷ LA  — A:', JSON.stringify(afterA), 'B:', JSON.stringify(afterB),
    'C:', JSON.stringify(afterC));

  // A — ownership isolation
  assert(near(afterA.r, 0), 'A: reserved tháng A về 0 sau khi LA bị huỷ (không kẹt vốn)');
  assert(near(afterA.a, beforeA.a + capA), 'A: vốn của LA quay về available của CHÍNH tháng A');
  assert(near(afterB.a, beforeB.a) && near(afterB.r, beforeB.r),
    'A: pool tháng B KHÔNG bị đụng tới bởi release của ladder tháng A');
  assert(near(afterC.a, beforeC.a) && near(afterC.r, beforeC.r),
    'A: pool tháng C (currentMonth) KHÔNG nhận nhầm vốn của tháng A');

  // B — active backing preservation
  const LB = st.ladders.filter(x => x.id === idB)[0];
  assert(LB.status === 'ACTIVE', 'B: LB vẫn ACTIVE');
  backingOk(st, '2026-06', 'B');
  backingOk(st, '2026-05', 'B');

  // C — release upper bound: ledger ghi đúng số thực chuyển, không vượt reserve của owner
  const rel = st.ledger.filter(e => e.type === 'RELEASE');
  console.log('  ledger RELEASE:', JSON.stringify(rel));
  assert(rel.length === 1 && rel[0].month === '2026-05',
    'C: đúng một bút toán RELEASE, ghi nhận tháng sở hữu 2026-05');
  assert(near(rel[0].vnd, capA), 'C: RELEASE ghi đúng số thực sự dịch chuyển (' + capA + ')');
  assert(rel[0].shortfall === undefined, 'C: không có shortfall — reserve của owner đủ');

  // D — conservation
  conservation(st, { '2026-05': 3000000, '2026-06': 3000000, '2026-07': 3000000 }, 'D');

  // C (biên trên) — huỷ lại/invalidate lại không release thêm lần nữa
  const before2 = JSON.parse(JSON.stringify(st.months['2026-05'].smart));
  await p.evaluate(() => { }); // no-op
  await H.pushDeclineDays(p, 1);
  st = await H.readState(p);
  assert(near(H.poolTotal(st.months['2026-05'].smart), 3000000) &&
    near(st.months['2026-05'].smart.a, before2.a) && near(st.months['2026-05'].smart.r, before2.r),
    'C: ladder đã CANCELLED không release lần thứ hai');

  assert(errs.length === 0, 'không có page error: ' + errs.join('; '));
  await ctx.close();
}

/* ------------------------------------------------------------------ */
/* CA 2 — A + D: deploy (fill zone) rút vốn từ tháng sở hữu ladder      */
/* ------------------------------------------------------------------ */
async function caseCrossMonthDeploy(b) {
  console.log('\n=== CA 2 — fill zone khi currentMonth() đã sang tháng khác ===');
  const { ctx, p, errs } = await H.newPage(b);
  const unlock = await H.pushDeclineDays(p, 12);

  await H.contribute(p, '2026-05', 10000000);
  const cap = 3000000 * unlock.smartUnlock;
  const la = await H.makeLadder(p, 'SMART', 480, cap);
  assert(!!la.ladder, 'tạo được ladder tháng A: ' + la.msg);
  const zone0 = la.ladder.id + '|0';
  const target0 = la.ladder.zones[0].target_vnd;

  await H.contribute(p, '2026-06', 10000000);   // currentMonth() -> tháng B

  // P2P đổi VND sang USDT để có kho thực thi.
  await p.click('[data-tab="entry"]');
  await p.fill('#p2pVnd', '5000000');
  await p.fill('#p2pUsdt', '196.5');
  await p.fill('#p2pFee', '0');
  await p.click('#p2pAdd');
  await p.waitForTimeout(200);

  let st = await H.readState(p);
  const bA = JSON.parse(JSON.stringify(st.months['2026-05'].smart));
  const bB = JSON.parse(JSON.stringify(st.months['2026-06'].smart));

  // Fill TOÀN PHẦN zone 0 của ladder tháng A, trong khi currentMonth() = tháng B.
  const rate = 25445;
  await p.click('[data-tab="entry"]');
  await p.selectOption('#buyZone', zone0);
  // +0,1% USDT để phần VND quy đổi chắc chắn phủ hết target sau khi làm tròn 4 chữ số;
  // app chỉ trừ tối đa `remaining` nên phần dư không làm sai sổ.
  await p.fill('#buyUsdt', (target0 / rate * 1.001).toFixed(4));
  await p.fill('#buyPrice', '203.99');
  await p.fill('#buyRec', '203.99');
  await p.fill('#buyVndRate', String(rate));
  await p.click('#buyAdd');
  await p.waitForTimeout(300);
  console.log('  buyMsg:', (await p.textContent('#buyMsg')).trim());

  st = await H.readState(p);
  assert(st.ladders[0].zones[0].status === 'EXECUTED', 'zone 0 EXECUTED sau fill toàn phần');
  const aA = st.months['2026-05'].smart, aB = st.months['2026-06'].smart;
  console.log('  A:', JSON.stringify(aA), '| B:', JSON.stringify(aB));
  assert(aA.d > bA.d + 1e-6, 'A: DEPLOYED tăng ở tháng SỞ HỮU ladder (2026-05)');
  assert(near(aA.r + aA.d, bA.r + bA.d), 'A: dịch chuyển thuần RESERVED -> DEPLOYED trong tháng A');
  assert(near(aB.a, bB.a) && near(aB.r, bB.r) && near(aB.d, bB.d),
    'A: pool tháng B (currentMonth) không bị đụng khi fill zone của ladder tháng A');
  conservation(st, { '2026-05': 3000000, '2026-06': 3000000 }, 'D');

  // Huỷ ladder sau khi đã fill một phần: chỉ phần chưa fill được trả về, đúng tháng A.
  const openBefore = st.ladders[0].zones
    .reduce((s, z) => s + Math.max(0, z.target_vnd - (z.filled_vnd || 0)), 0);
  await H.cancelLadder(p, la.ladder.id);
  st = await H.readState(p);
  const cA = st.months['2026-05'].smart;
  assert(near(cA.a, aA.a + openBefore), 'C: chỉ phần CHƯA fill (' + openBefore +
    ') được trả về available tháng A');
  assert(near(cA.d, aA.d), 'C: phần đã deploy không bị trả lại');
  assert(near(cA.r, 0), 'C: không còn reserved kẹt ở tháng A');
  conservation(st, { '2026-05': 3000000, '2026-06': 3000000 }, 'D');
  assert(errs.length === 0, 'không có page error: ' + errs.join('; '));
  await ctx.close();
}

/* ------------------------------------------------------------------ */
/* CA 3 — V-02: unlock chặn reserve (biên trên chính xác)               */
/* ------------------------------------------------------------------ */
async function caseUnlockBound(b) {
  console.log('\n=== CA 3 — unlock giới hạn reserve (Strategy §12) ===');
  const { ctx, p, errs } = await H.newPage(b);

  // 3a. unlock = 0 (OSCORE thật của seed) — reserve phải bị TỪ CHỐI hoàn toàn.
  const u0 = await H.readUnlock(p);
  console.log('  unlock ban đầu:', (u0.smartUnlock * 100).toFixed(3) + '% (OSCORE ' +
    u0.oscore.toFixed(3) + ')');
  assert(u0.smartUnlock === 0, 'seed cho Smart unlock = 0 — đúng tiền đề counterexample V-02');
  await H.contribute(p, '2026-06', 10000000);
  let st = await H.readState(p);
  const avail = st.months['2026-06'].smart.a;
  const r0 = await H.makeLadder(p, 'SMART', 480, avail);
  console.log('  ldMsg (cap = 100% available, unlock 0%):', r0.msg);
  assert(/unlock/i.test(r0.msg), 'V-02: bị từ chối với lý do vượt phần đã unlock');
  st = await H.readState(p);
  assert((st.ladders || []).length === 0, 'V-02: không ladder nào được tạo');
  assert(near(st.months['2026-06'].smart.a, avail) && near(st.months['2026-06'].smart.r, 0),
    'V-02: pool không bị đụng tới khi reserve bị từ chối (fail closed, không side effect)');

  // 3b. unlock cục bộ > 0 nhưng < 100% — kiểm ĐÚNG biên trên.
  const u1 = await H.pushDeclineDays(p, 3);
  console.log('  unlock sau 3 ngày giảm:', (u1.smartUnlock * 100).toFixed(4) + '%');
  assert(u1.smartUnlock > 0 && u1.smartUnlock < 1,
    'dựng được trạng thái unlock cục bộ (0 < unlock < 1): ' + u1.smartUnlock);
  const total = 3000000;
  const capExact = total * u1.smartUnlock;
  const over = await H.makeLadder(p, 'SMART', 480, capExact * 1.01);
  console.log('  ldMsg (cap = 101% hạn mức):', over.msg);
  assert(/unlock/i.test(over.msg), 'biên trên: cap vượt 1% hạn mức bị từ chối');
  st = await H.readState(p);
  assert((st.ladders || []).length === 0, 'biên trên: không ladder nào được tạo khi vượt');

  const okL = await H.makeLadder(p, 'SMART', 480, capExact * 0.999);
  console.log('  ldMsg (cap = 99,9% hạn mức):', okL.msg);
  assert(!!okL.ladder, 'biên trên: cap ngay dưới hạn mức được chấp nhận');
  st = await H.readState(p);
  const m = st.months['2026-06'].smart;
  assert(m.r <= capExact + 1e-6, 'C: reserved (' + m.r + ') không vượt phần đã unlock (' +
    capExact + ')');

  // 3c. hạn mức trừ dần phần ĐÃ reserve — reserve lần hai không được vượt phần còn lại.
  const remain = Math.max(0, capExact - m.r - m.d);
  const second = await H.makeLadder(p, 'SMART', 480, remain * 1.05 + 1);
  console.log('  ldMsg (reserve lần hai vượt phần còn lại):', second.msg);
  assert(/unlock/i.test(second.msg),
    'hạn mức unlock trừ đi phần đã reserve/deploy trong tháng (capital.py::smart_reservable)');
  st = await H.readState(p);
  assert(st.months['2026-06'].smart.r <= capExact + 1e-6,
    'C: tổng reserved vẫn không vượt phần đã unlock sau hai lần thử');
  conservation(st, { '2026-06': 3000000 }, 'D');
  assert(errs.length === 0, 'không có page error: ' + errs.join('; '));
  await ctx.close();
}

/* ------------------------------------------------------------------ */
/* CA 4 — F: kịch bản sạch một tháng không đổi hành vi                  */
/* ------------------------------------------------------------------ */
async function caseSingleMonthUnchanged(b) {
  console.log('\n=== CA 4 — kịch bản sạch một tháng (không được đổi hành vi) ===');
  const { ctx, p, errs } = await H.newPage(b);
  const unlock = await H.pushDeclineDays(p, 12);

  await H.contribute(p, '2026-06', 10000000);
  const cap = 3000000 * unlock.smartUnlock;
  const l = await H.makeLadder(p, 'SMART', 480, cap);
  assert(!!l.ladder, 'tạo ladder trong tháng hiện hành: ' + l.msg);
  let st = await H.readState(p);
  assert(near(st.months['2026-06'].smart.r, cap), 'reserve đúng số vào tháng hiện hành');
  conservation(st, { '2026-06': 3000000 }, 'F/D');

  await p.click('[data-tab="entry"]');
  await p.fill('#p2pVnd', '5000000');
  await p.fill('#p2pUsdt', '196.5');
  await p.fill('#p2pFee', '0');
  await p.click('#p2pAdd');
  await p.waitForTimeout(200);

  // fill toàn phần zone 0 rồi fill một phần zone 1 — cùng chuỗi WP-C1 đã kiểm.
  const rate = 25445;
  const z0 = l.ladder.zones[0], z1 = l.ladder.zones[1];
  await p.selectOption('#buyZone', l.ladder.id + '|0');
  await p.fill('#buyUsdt', (z0.target_vnd / rate * 1.001).toFixed(4));
  await p.fill('#buyPrice', '203.99');
  await p.fill('#buyVndRate', String(rate));
  await p.click('#buyAdd');
  await p.waitForTimeout(250);
  await p.selectOption('#buyZone', l.ladder.id + '|1');
  await p.fill('#buyUsdt', (z1.target_vnd / 2 / rate).toFixed(4));
  await p.fill('#buyPrice', '200');
  await p.fill('#buyVndRate', String(rate));
  await p.click('#buyAdd');
  await p.waitForTimeout(250);

  st = await H.readState(p);
  const L = st.ladders[0];
  console.log('  zones:', L.zones.map(z => z.index + ':' + z.status).join(','));
  assert(L.zones[0].status === 'EXECUTED', 'F: zone 0 EXECUTED sau fill toàn phần');
  assert(L.zones[1].status === 'PARTIALLY_FILLED', 'F: zone 1 PARTIALLY_FILLED sau fill một phần');
  conservation(st, { '2026-06': 3000000 }, 'F/D');
  backingOk(st, '2026-06', 'F/B');

  await H.cancelLadder(p, L.id);
  st = await H.readState(p);
  const m = st.months['2026-06'].smart;
  console.log('  sau huỷ:', JSON.stringify(m));
  assert(near(m.r, 0), 'F: toàn bộ phần chưa fill được trả về available, không kẹt');
  conservation(st, { '2026-06': 3000000 }, 'F/D');
  assert(errs.length === 0, 'không có page error: ' + errs.join('; '));
  await ctx.close();
}

/* ------------------------------------------------------------------ */
(async () => {
  const b = await chromium.launch({ executablePath: H.CHROMIUM });
  try {
    await caseMultiMonthRelease(b);
    await caseCrossMonthDeploy(b);
    await caseUnlockBound(b);
    await caseSingleMonthUnchanged(b);
  } finally {
    await b.close();
  }
  console.log('\n=== TỔNG KẾT T-09A ===');
  console.log('assertion đã chạy:', checks, '| FAIL:', failures);
  if (failures > 0) { console.log('T-09A INVARIANTS: FAIL'); process.exit(1); }
  console.log('T-09A INVARIANTS: PASS (A ownership · B backing · C upper bound · D conservation · ' +
    'E multi-month · F existing behavior)');
})();
