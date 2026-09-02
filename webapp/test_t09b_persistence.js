/* T-09B — Completion Gate FROZEN (2026-09-02, DEC-021): 16 REQUIRED check, chạy qua ĐƯỜNG SẢN
 * PHẨM THẬT (UI -> app_logic -> Firebase SDK -> Cloud Firestore -> nạp lại), trên
 * app_final.html đã build, phục vụ qua HTTP như Firebase Hosting, với Firebase Emulator Suite
 * (Auth + Firestore) và ĐÚNG firestore.rules của repo. Không gọi hàm nội bộ của app.
 *
 * Bằng chứng "phía Firebase" (CHECK-01/02/10/12/15/16) được đọc ĐỘC LẬP với app: Node ->
 * REST API của emulator (test_firebase_harness.getDoc), không qua promise của SDK trong trang.
 *
 * Phạm vi trong file này: CHECK-T09B-01..08, 10, 11, 12, 14, 15, 16.
 *   CHECK-T09B-09 = ba bộ test kế toán (test_t09a_accounting.js, test_multi_month_invariant.js,
 *                   test_v01_v02_v03.js) chạy trên state ĐÃ đi qua Firestore — test_helpers.readState.
 *   CHECK-T09B-13 = `npm --prefix webapp test` + `git diff --stat` engine.js = 0.
 *
 * Giới hạn trung thực: emulator là bản Firebase chạy cục bộ (rules engine, Auth, wire protocol
 * thật) — KHÔNG phải project Firebase thật của chủ dự án. Production reachability trên project
 * thật/Firebase Hosting thật không suy ra được từ file này.
 */
const { chromium } = require('playwright');
const fs = require('fs');
const os = require('os');
const path = require('path');
const H = require('./test_firebase_harness.js');
const T = require('./test_helpers.js');

let checks = 0, failures = 0;
const results = {};   // CHECK-ID -> { pass, fails }
let current = null;
function assert(cond, label) {
  checks++;
  if (!cond) { failures++; if (current) results[current].fails++; console.log('  ASSERT FAIL:', label); }
  else console.log('  ok:', label);
}
function begin(id, title) {
  current = id;
  results[id] = { fails: 0, title };
  console.log('\n=== ' + id + ' — ' + title + ' ===');
}
function end() {
  const r = results[current];
  r.pass = r.fails === 0;
  console.log('  => ' + current + ': ' + (r.pass ? 'PASS' : 'FAIL (' + r.fails + ' assert)'));
  current = null;
}
const near = (a, b, tol) => Math.abs(a - b) <= (tol === undefined ? 1e-6 : tol);
const same = (a, b) => Object.is(a, b) || (a === null && b === null);
const banners = (p) => p.textContent('#banners').then((t) => t.replace(/\s+/g, ' '));
const chip = (p) => p.textContent('#saveChip').then((t) => t.trim());
const rulesReadOnly = (uid) => H.rulesWithUid(uid).replace(/allow read, create, update: if isCoinDcaOwner\(\);/g, 'allow read: if isCoinDcaOwner();');

/* Ghi sổ qua UI thật: một lệnh nạp vốn nhỏ. Trả msg. */
async function uiContribute(p, mk, amt) {
  await p.click('[data-tab="entry"]');
  await p.fill('#cbMonth', mk);
  await p.fill('#cbAmt', String(amt));
  await p.click('#cbAdd');
  await p.waitForTimeout(150);
  return (await p.textContent('#cbMsg')).trim();
}
async function uiBuy(p, usdt, price, rate) {
  await p.click('[data-tab="entry"]');
  await p.selectOption('#buyZone', '');
  await p.selectOption('#buySrc', 'MANUAL');
  await p.fill('#buyUsdt', String(usdt));
  await p.fill('#buyPrice', String(price));
  await p.fill('#buyRec', '');
  await p.fill('#buyVndRate', rate === undefined ? '' : String(rate));
  await p.click('#buyAdd');
  await p.waitForTimeout(150);
  return (await p.textContent('#buyMsg')).trim();
}
async function uiPrice(p, d, e, b, v) {
  await p.click('[data-tab="entry"]');
  await p.fill('#pxDate', d);
  await p.fill('#pxEth', String(e));
  await p.fill('#pxBtc', String(b));
  await p.fill('#pxVol', String(v));
  await p.click('#pxAdd');
  await p.waitForTimeout(150);
  return (await p.textContent('#pxMsg')).trim();
}
const mirror = (p) => p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));

/** Bất biến kế toán T-09A đo trên một state (dùng cho trước/sau round-trip). */
function invariants(st, label) {
  Object.keys(st.months).forEach((mk) => {
    const m = st.months[mk];
    const tot = T.poolTotal(m.base) + T.poolTotal(m.smart) + m.oppAdded;
    assert(near(tot, m.contribution, 1e-3), label + ' — ' + mk + ': TOTAL = A+R+D (' + tot + ') = contribution ' + m.contribution);
    [m.base, m.smart].forEach((x) => assert(x.a >= -1e-6 && x.r >= -1e-6 && x.d >= -1e-6, label + ' — ' + mk + ' pool không âm'));
    const need = st.ladders.filter((L) => L.status === 'ACTIVE' && L.type === 'SMART' && L.month === mk)
      .reduce((s, L) => s + L.zones.reduce((t, z) => t + Math.max(0, z.target_vnd - (z.filled_vnd || 0)), 0), 0);
    assert(m.smart.r >= need - 1e-6, label + ' — ' + mk + ': reserved đủ backing ladder ACTIVE của tháng');
  });
  assert(near(T.poolTotal(st.oppFund), Object.values(st.months).reduce((s, m) => s + m.oppAdded, 0), 1e-3), label + ' — oppFund = Σ oppAdded');
}

/* ------------------------------------------------------------------ */
/* Dựng sổ có đủ mọi lớp MUST_PERSIST qua UI thật (context bền = 1 profile) */
/* ------------------------------------------------------------------ */
async function buildLedger(p) {
  const unlock = await T.pushDeclineDays(p, 12);           // extraDays[] 12 phần tử
  assert(unlock.smartUnlock > 0, 'dựng được Smart unlock > 0 qua nhập giá thật');
  await T.contribute(p, '2026-05', 10000000);               // months A
  await T.contribute(p, '2026-06', 10000000);               // months B = currentMonth
  await p.fill('#p2pVnd', '5000000'); await p.fill('#p2pUsdt', '196.5'); await p.fill('#p2pFee', '0');
  await p.click('#p2pAdd'); await p.waitForTimeout(150);    // p2p[]
  const cap = 3000000 * unlock.smartUnlock;
  const la = await T.makeLadder(p, 'SMART', 480, cap * 0.6);   // ladder LA (2026-06), ACTIVE
  assert(!!la.ladder && la.ladder.month === '2026-06', 'LA tạo được, mang ladder.month = 2026-06: ' + la.msg);
  const lb = await T.makeLadder(p, 'SMART', 470, cap * 0.3);   // ladder LB, sẽ huỷ
  assert(!!lb.ladder, 'LB tạo được: ' + lb.msg);
  const rate = 25445;
  const z0 = la.ladder.zones[0], z1 = la.ladder.zones[1];
  await p.click('[data-tab="entry"]');
  await p.selectOption('#buyZone', la.ladder.id + '|0');   // fill toàn phần zone 0 (có recPrice)
  await p.fill('#buyUsdt', (z0.target_vnd / rate * 1.001).toFixed(4));
  await p.fill('#buyPrice', '203.99'); await p.fill('#buyRec', '204'); await p.fill('#buyVndRate', String(rate));
  await p.click('#buyAdd'); await p.waitForTimeout(150);
  await p.selectOption('#buyZone', la.ladder.id + '|1');   // fill một phần zone 1
  await p.fill('#buyUsdt', (z1.target_vnd / 2 / rate).toFixed(4));
  await p.fill('#buyPrice', '200'); await p.fill('#buyRec', ''); await p.fill('#buyVndRate', String(rate));
  await p.click('#buyAdd'); await p.waitForTimeout(150);
  await uiBuy(p, 5, 199.5);                                 // mua thủ công, không recPrice, không vndRate
  await T.cancelLadder(p, lb.ladder.id);                    // LB CANCELLED -> released_vnd > 0, ledger RELEASE
  const st = await T.readState(p);
  console.log('  sổ dựng xong: rev', st.rev, '| months', Object.keys(st.months).join(','), '| ladders', st.ladders.length,
    '| trades', st.trades.length, '| p2p', st.p2p.length, '| ledger', st.ledger.length, '| extraDays', st.extraDays.length);
  return st;
}

/* ------------------------------------------------------------------ */
(async () => {
  const stopEmu = await H.ensureEmulators();
  await H.clearFirestore(); await H.clearAuth(); await H.setRules('OWNER_UID_REQUIRED');
  await H.startServer();
  const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ethdca-profile-'));
  const b = await chromium.launch({ executablePath: H.CHROMIUM });
  const allErrs = [];
  let ctx, p, errs, uid, snapshot;

  /* ---------- Owner mở app lần đầu trên browser profile BỀN (thiết lập thật) ---------- */
  ({ ctx, p, errs } = await H.newPersistent(chromium, profileDir));
  const first = await H.waitPhase(p, ['UNRECOGNIZED', 'ONLINE']);
  console.log('lần mở đầu (rules còn OWNER_UID_REQUIRED):', first.phase, '| uid', first.uid);
  uid = first.uid;
  await H.setRules(uid);                       // = Owner chép UID vào firestore.rules và deploy rules
  await p.reload(); await H.waitPhase(p, 'ONLINE');
  await p.setInputFiles('#seedFile', H.SEED_PATH); await H.waitSaved(p);
  snapshot = await buildLedger(p);

  /* ---------- CHECK-T09B-01 — Firebase durable write thành công, có xác nhận máy chủ ---------- */
  begin('CHECK-T09B-01', 'Firebase durable write thành công (server ack, bản ghi tồn tại phía Firebase)');
  {
    const before = await H.status(p);
    const msg = await uiContribute(p, '2026-06', 1000);      // một thao tác làm đổi state
    const after = await H.waitSaved(p);
    assert(after.rev === before.rev + 1, 'rev tăng 1 sau thao tác (' + before.rev + ' -> ' + after.rev + ')');
    assert(after.durableRev === after.rev, 'durableRev = rev sau khi máy chủ xác nhận');
    assert((await chip(p)).startsWith('Đã lưu bền · rev ' + after.rev), 'UI báo "Đã lưu bền · rev N" đúng rev: ' + await chip(p));
    const doc = await H.getDoc('state');                     // ĐỘC LẬP: REST từ Node
    assert(doc !== null && doc.rev === after.rev, 'document ethdca/state tồn tại phía Firebase với rev ' + (doc && doc.rev));
    const seedDoc = await H.getDoc('seed');
    assert(seedDoc !== null && seedDoc.history.length === 420, 'document ethdca/seed tồn tại phía Firebase (420 ngày)');
    assert(H.diff(H.canon(doc), H.canon(await mirror(p))).length === 0, 'bản durable = bản trong bộ nhớ, bit-exact');
    snapshot = doc;
    console.log('  msg:', msg);
  }
  end();

  /* ---------- CHECK-T09B-02 — App load đúng state từ Firebase (phiên mới, so từng trường) ---------- */
  begin('CHECK-T09B-02', 'App load đúng state từ Firebase — so từng trường MUST_PERSIST tầng 1');
  {
    const p2 = await ctx.newPage(); const e2 = H.attachErrors(p2);
    await p2.goto(H.baseUrl()); await H.waitPhase(p2, 'ONLINE');
    const loaded = await mirror(p2);            // = JSON của state trong bộ nhớ trang mới
    const d = H.diff(H.canon(snapshot), H.canon(loaded));
    assert(d.length === 0, 'state nạp lên bằng đúng bản đã ghi ở CHECK-01 (0 lệch)' + (d.length ? ': ' + d.slice(0, 5).join('; ') : ''));
    ['schema', 'rev', 'months', 'oppFund', 'treasury', 'eth', 'costUsdt', 'costVnd', 'ladders', 'trades', 'p2p', 'ledger', 'extraDays']
      .forEach((k) => assert(H.canonJSON(snapshot[k]) === H.canonJSON(loaded[k]), 'trường ' + k + ' bằng nhau'));
    assert((await p2.textContent('#osVal')).trim() !== '—', 'seed nạp từ ethdca/seed -> OSCORE hiển thị');
    assert(e2.length === 0, 'không page error: ' + e2.join('; '));
    await p2.close();
  }
  end();

  /* ---------- CHECK-T09B-05..08 — bảo toàn từng lớp qua round-trip (durable vs bản gốc trong bộ nhớ) ---------- */
  // Bản gốc trong bộ nhớ = mirror JSON của trang đã dựng sổ (trước round-trip); durable = REST.
  const mem = await mirror(p);
  const dur = await H.getDoc('state');
  begin('CHECK-T09B-05', 'Purchase History (trades[]) bảo toàn — số phần tử, thứ tự, từng trường kể cả null');
  {
    assert(dur.trades.length === mem.trades.length && dur.trades.length >= 3, 'trades[] đủ ' + mem.trades.length + ' phần tử');
    const F = ['ts', 'src', 'usdt', 'price', 'recPrice', 'eth', 'fee', 'vndRate', 'vndCost', 'shortfallBps', 'zone'];
    mem.trades.forEach((t, i) => F.forEach((f) => assert(same(t[f], dur.trades[i][f]), 'trades[' + i + '].' + f + ' = ' + JSON.stringify(t[f]))));
    assert(mem.trades.some((t) => t.recPrice === null) && mem.trades.some((t) => t.zone === null) && mem.trades.some((t) => t.vndRate === null),
      'có phần tử với recPrice/zone/vndRate = null — null được giữ nguyên, không bị xoá');
  }
  end();
  begin('CHECK-T09B-06', 'Holdings / average cost bảo toàn — eth, costUsdt, costVnd bằng đúng bit');
  {
    ['eth', 'costUsdt', 'costVnd'].forEach((k) => assert(Object.is(mem[k], dur[k]), k + ' = ' + mem[k] + ' (Object.is)'));
    assert(mem.eth > 0 && mem.costUsdt > 0 && mem.costVnd > 0, 'holdings/cost khác 0 (ca kiểm có ý nghĩa)');
  }
  end();
  begin('CHECK-T09B-07', 'Accounting pools / reserve / release / available bảo toàn; TOTAL = A+R+D giữ nguyên');
  {
    Object.keys(mem.months).forEach((mk) => {
      const a = mem.months[mk], c = dur.months[mk];
      ['contribution', 'oppAdded', 'oppOverflow'].forEach((k) => assert(Object.is(a[k], c[k]), mk + '.' + k + ' = ' + a[k]));
      ['base', 'smart'].forEach((pl) => ['a', 'r', 'd'].forEach((k) => assert(Object.is(a[pl][k], c[pl][k]), mk + '.' + pl + '.' + k + ' = ' + a[pl][k])));
    });
    ['a', 'r', 'd'].forEach((k) => assert(Object.is(mem.oppFund[k], dur.oppFund[k]), 'oppFund.' + k + ' = ' + mem.oppFund[k]));
    ['vnd', 'usdt'].forEach((k) => assert(Object.is(mem.treasury[k], dur.treasury[k]), 'treasury.' + k + ' = ' + mem.treasury[k]));
    invariants(mem, 'trước'); invariants(dur, 'sau');
    assert(mem.months['2026-06'].smart.r > 0 && mem.months['2026-06'].smart.d > 0, 'ca có reserved > 0 và deployed > 0 (reserve/deploy/release đều đã xảy ra)');
  }
  end();
  begin('CHECK-T09B-08', 'Active ladders + ladder.month + zones (filled_vnd/released_vnd, kể cả 0) bảo toàn');
  {
    assert(dur.ladders.length === mem.ladders.length && mem.ladders.length === 2, 'ladders[] đủ 2 phần tử');
    mem.ladders.forEach((L, i) => {
      const D = dur.ladders[i];
      assert(typeof L.month === 'string' && Object.is(L.month, D.month), 'ladders[' + i + '].month = ' + L.month);
      ['id', 'type', 'created', 'status', 'anchor_price', 'spacing_pct', 'score_at_creation', 'eligible_capital_vnd', 'invalidation_price', 'consecutive_invalidation_closes']
        .forEach((k) => assert(same(L[k], D[k]), 'ladders[' + i + '].' + k + ' = ' + JSON.stringify(L[k])));
      L.zones.forEach((z, j) => ['index', 'target_price', 'allocation_pct', 'target_vnd', 'status', 'filled_vnd', 'released_vnd']
        .forEach((k) => assert(same(z[k], D.zones[j][k]) && ((k in z) === (k in D.zones[j])), 'ladders[' + i + '].zones[' + j + '].' + k + ' = ' + JSON.stringify(z[k]))));
    });
    const zeroFilled = mem.ladders.some((L) => L.zones.some((z) => z.filled_vnd === 0));
    assert(zeroFilled, 'có zone với filled_vnd: 0 — khoá giá trị 0 không bị xoá');
    assert(mem.ladders.some((L) => L.status === 'ACTIVE') && mem.ladders.some((L) => L.status === 'CANCELLED' && L.zones.some((z) => z.released_vnd > 0)),
      'có ladder ACTIVE và ladder CANCELLED với released_vnd > 0');
  }
  end();

  /* ---------- CHECK-T09B-04 — đóng hẳn trình duyệt, mở lại CÙNG profile (DEC-021 R2) ---------- */
  begin('CHECK-T09B-04', 'Đóng/mở lại trình duyệt cùng profile (IndexedDB còn) — state phục hồi, bất biến T-09A giữ');
  {
    allErrs.push(...errs);
    await ctx.close();                                        // đóng hẳn trình duyệt
    ({ ctx, p, errs } = await H.newPersistent(chromium, profileDir));   // mở lại cùng profile
    const st = await H.waitPhase(p, 'ONLINE');
    assert(st.uid === uid, 'cùng Anonymous UID sau khi mở lại: ' + st.uid);
    assert(st.rev === snapshot.rev && st.durableRev === snapshot.rev, 'rev nạp lên = rev bền ' + snapshot.rev);
    const loaded = await mirror(p);
    assert(H.diff(H.canon(snapshot), H.canon(loaded)).length === 0, 'state kế toán phục hồi đầy đủ, bit-exact');
    invariants(loaded, 'sau mở lại');
    assert((await p.textContent('#osVal')).trim() !== '—', 'seed phục hồi -> OSCORE hiển thị');
    // tiếp tục dùng được: một thao tác mới sau khi mở lại
    await uiContribute(p, '2026-06', 1000);
    const st2 = await H.waitSaved(p);
    assert(st2.rev === snapshot.rev + 1 && (await H.getDoc('state')).rev === st2.rev, 'tiếp tục ghi sổ được sau khi mở lại (rev ' + st2.rev + ' bền)');
    snapshot = await H.getDoc('state');
  }
  end();

  /* ---------- CHECK-T09B-03 — xoá sạch localStorage + sessionStorage, mở lại ---------- */
  begin('CHECK-T09B-03', 'Xoá localStorage + sessionStorage vẫn recover được state từ Firebase');
  {
    await p.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    assert(await p.evaluate(() => localStorage.length + sessionStorage.length) === 0, 'localStorage + sessionStorage trống');
    await p.reload();
    const st = await H.waitPhase(p, 'ONLINE');
    assert(st.uid === uid, 'identity (IndexedDB) còn nguyên: cùng UID');
    const loaded = await mirror(p);
    assert(loaded !== null && H.diff(H.canon(snapshot), H.canon(loaded)).length === 0, 'state kế toán phục hồi đầy đủ từ Firestore, bit-exact');
    assert((await p.textContent('#osVal')).trim() !== '—', 'seed phục hồi từ ethdca/seed');
    assert(!st.diverged, 'không có banner lệch bản (mirror đã bị xoá, nguồn bền là sự thật)');
  }
  end();

  /* ---------- CHECK-T09B-14 — workflow hằng ngày, không terminal ---------- */
  begin('CHECK-T09B-14', 'Workflow cá nhân: mở app, nhập giá đóng cửa, ghi giao dịch, đóng, mở lại — chỉ trình duyệt');
  {
    const st0 = await H.status(p);
    const lastDay = snapshot.extraDays[snapshot.extraDays.length - 1];
    const nextDay = new Date(Date.parse(lastDay.d + 'T00:00:00Z') + 86400000).toISOString().slice(0, 10);
    const m1 = await uiPrice(p, nextDay, (lastDay.e * 0.99).toFixed(4), (lastDay.b * 0.99).toFixed(4), 100000);
    assert(/Đã thêm/.test(m1), 'nhập giá đóng cửa qua UI: ' + m1);
    const m2 = await uiBuy(p, 3, 198.25, 25445);
    assert(/Đã ghi/.test(m2), 'ghi giao dịch qua UI: ' + m2);
    const st1 = await H.waitSaved(p);
    assert(st1.rev === st0.rev + 2, 'hai thao tác -> hai rev, đều đã bền');
    allErrs.push(...errs);
    await ctx.close();                                        // đóng trình duyệt
    ({ ctx, p, errs } = await H.newPersistent(chromium, profileDir));   // mở lại
    const st2 = await H.waitPhase(p, 'ONLINE');
    const loaded = await mirror(p);
    assert(st2.rev === st1.rev, 'mở lại: rev ' + st2.rev);
    assert(loaded.extraDays.some((d) => d.d === nextDay), 'giá đóng cửa vừa nhập còn nguyên');
    assert(loaded.trades.length === snapshot.trades.length + 1 && near(loaded.trades[loaded.trades.length - 1].usdt, 3), 'giao dịch vừa ghi còn nguyên trong Purchase History');
    await p.click('[data-tab="history"]');
    assert((await p.$$eval('#tradeTable tbody tr', (r) => r.length)) === loaded.trades.length, 'tab Lịch sử hiện đủ ' + loaded.trades.length + ' lệnh');
    snapshot = await H.getDoc('state');
  }
  end();

  /* ---------- CHECK-T09B-10 — write failure visible ---------- */
  begin('CHECK-T09B-10', 'Firebase write failure visible — rules từ chối ghi, và mất mạng');
  {
    // (a) rules từ chối ghi
    await H.setRules(uid, rulesReadOnly(uid));
    const revBefore = (await H.getDoc('state')).rev;
    await uiContribute(p, '2026-06', 1000);
    let st;
    for (let i = 0; i < 100; i++) { st = await H.status(p); if (!st.saving) break; await p.waitForTimeout(100); }
    assert(!st.saving && /permission-denied/.test(st.lastError || ''), 'lệnh ghi bị từ chối: lastError = ' + st.lastError);
    assert(st.durableRev === revBefore && st.rev === revBefore + 1, 'durableRev giữ ' + revBefore + ', rev cục bộ ' + st.rev);
    const c1 = await chip(p);
    assert(/^CHƯA LƯU/.test(c1) && !/Đã lưu/.test(c1), 'chip KHÔNG hàm ý đã lưu: "' + c1 + '"');
    assert(/GHI THẤT BẠI/.test(await banners(p)), 'banner "GHI THẤT BẠI" hiện');
    assert((await mirror(p)).rev === st.rev, 'bản local (rev ' + st.rev + ') vẫn còn trong localStorage để cứu');
    assert((await H.getDoc('state')).rev === revBefore, 'phía Firebase KHÔNG đổi (rev ' + revBefore + ')');
    assert(!(await p.isDisabled('#saveBtn')), 'nút Lưu lại được bật');
    // khôi phục rules -> Lưu lại -> bền
    await H.setRules(uid);
    await p.click('#saveBtn');
    const ok = await H.waitSaved(p);
    assert(ok.durableRev === revBefore + 1 && (await H.getDoc('state')).rev === revBefore + 1, 'Lưu lại thành công sau khi rules cho phép: rev ' + ok.durableRev + ' bền');
    assert(/Đã lưu bền/.test(await chip(p)) && !/GHI THẤT BẠI/.test(await banners(p)), 'chip về "Đã lưu bền", banner lỗi biến mất');

    // (b) mất mạng: máy chủ không trả lời -> sau ackTimeoutMs chip "CHƯA XÁC NHẬN"; SDK sau đó từ
    //     chối (unavailable) -> "CHƯA LƯU". Không lúc nào được hàm ý "đã lưu"; có mạng lại -> tự ghi lại.
    await ctx.setOffline(true);
    const r2 = (await H.getDoc('state')).rev;
    await uiContribute(p, '2026-06', 1000);
    const seen = new Set();
    for (let i = 0; i < 150; i++) {
      st = await H.status(p); seen.add(await chip(p));
      if ((st.saving && st.unconfirmed) || (!st.saving && st.lastError)) break;
      await p.waitForTimeout(100);
    }
    assert(st.durableRev === r2 && (st.unconfirmed || st.lastError), 'không ack: trạng thái visible (unconfirmed=' + st.unconfirmed + ', lastError=' + st.lastError + '), durableRev giữ ' + r2);
    assert([...seen].every((t) => !/Đã lưu/.test(t)), 'không lúc nào chip hàm ý đã lưu khi mất mạng: ' + JSON.stringify([...seen]));
    const c2 = await chip(p);
    assert(/CHƯA XÁC NHẬN|CHƯA LƯU/.test(c2), 'chip: "' + c2 + '"');
    assert(/CHƯA XÁC NHẬN|GHI THẤT BẠI/.test(await banners(p)), 'banner "CHƯA XÁC NHẬN"/"GHI THẤT BẠI" hiện');
    assert((await H.getDoc('state')).rev === r2, 'phía Firebase chưa nhận bản mới');
    assert((await mirror(p)).rev === r2 + 1, 'bản local (rev ' + (r2 + 1) + ') vẫn còn để cứu');
    await ctx.setOffline(false);
    const ok2 = await H.waitSaved(p, 60000);
    assert(ok2.durableRev === r2 + 1 && (await H.getDoc('state')).rev === r2 + 1, 'có mạng lại: tự ghi lại thành công, rev ' + ok2.durableRev + ' bền');
    snapshot = await H.getDoc('state');
  }
  end();

  /* ---------- CHECK-T09B-16 — mirror không âm thầm thắng nguồn bền ---------- */
  begin('CHECK-T09B-16', 'localStorage.rev > durable.rev — mirror không âm thầm thành sổ; chọn tường minh');
  {
    const durRev = snapshot.rev;
    const forge = async () => p.evaluate((n) => {
      const m = JSON.parse(localStorage.getItem('ethdca-tracker-state-v1'));
      m.rev = m.rev + n; m.treasury.vnd = m.treasury.vnd + 123456;
      localStorage.setItem('ethdca-tracker-state-v1', JSON.stringify(m));
      return m.rev;
    }, 5);
    const forgedRev = await forge();
    await p.reload();
    let st = await H.waitPhase(p, 'ONLINE');
    assert(st.rev === durRev && st.durableRev === durRev, 'sổ chính thức = nguồn bền (rev ' + durRev + '), KHÔNG phải mirror rev ' + forgedRev);
    assert(st.diverged, 'app đánh dấu có bản mirror mới hơn');
    assert(/BẢN TRÊN MÁY MỚI HƠN NGUỒN BỀN/.test(await banners(p)), 'banner lệch bản hiện, kèm hai nút chọn');
    assert((await mirror(p)).rev === durRev, 'mirror đã được thay bằng bản bền');
    const stash = await p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1.local-diverged')));
    assert(stash && stash.rev === forgedRev, 'bản mirror mới hơn được cất riêng (rev ' + forgedRev + '), không mất');
    // (a) người dùng chọn BỎ
    await p.click('[data-pdiv="drop"]');
    st = await H.status(p);
    assert(!st.diverged && (await p.evaluate(() => localStorage.getItem('ethdca-tracker-state-v1.local-diverged'))) === null, 'Bỏ bản trên máy: banner tắt, stash xoá');
    assert((await H.getDoc('state')).rev === durRev, 'nguồn bền không đổi');
    // (b) người dùng chọn ĐẨY LÊN — hành động tường minh
    const forgedRev2 = await forge();
    await p.reload(); await H.waitPhase(p, 'ONLINE');
    assert((await H.status(p)).diverged, 'lệch bản lại được phát hiện (rev ' + forgedRev2 + ')');
    const treasBefore = (await H.getDoc('state')).treasury.vnd;
    await p.click('[data-pdiv="push"]');
    const pushed = await H.waitSaved(p);
    const doc = await H.getDoc('state');
    assert(pushed.durableRev === forgedRev2 + 1 && doc.rev === forgedRev2 + 1, 'đẩy lên: bản bền nay là rev ' + doc.rev + ' (> ' + forgedRev2 + ')');
    assert(near(doc.treasury.vnd, treasBefore + 123456), 'nội dung bản trên máy đã thành bản bền (treasury +123456)');
    assert(!(await H.status(p)).diverged, 'banner tắt sau khi chọn');
    // (c') HAI TAB cùng profile: tab B stale ghi sau tab A -> bị từ chối, KHÔNG ghi đè bản mới hơn
    {
      const pB = await ctx.newPage(); H.attachErrors(pB);
      await pB.goto(H.baseUrl()); await H.waitPhase(pB, 'ONLINE');      // tab B nạp rev hiện tại
      await uiContribute(p, '2026-06', 1000);                            // tab A ghi -> rev+1 bền
      const sa = await H.waitSaved(p);
      await uiContribute(pB, '2026-06', 7777);                           // tab B (stale) ghi
      let sb;
      for (let i = 0; i < 100; i++) { sb = await H.status(pB); if (!sb.saving) break; await pB.waitForTimeout(100); }
      assert(sb.lastError === 'stale-durable' && sb.staleRev === sa.rev, 'tab stale bị từ chối: lastError=' + sb.lastError + ', máy chủ đang ở rev ' + sb.staleRev);
      const docA = await H.getDoc('state');
      assert(docA.rev === sa.rev && !docA.ledger.some((l) => l.vnd === 7777 * 0.5), 'phía Firebase vẫn là bản của tab A (rev ' + docA.rev + '), không bị tab stale ghi đè');
      assert(/NGUỒN BỀN ĐÃ ĐỔI Ở NƠI KHÁC/.test(await banners(pB)) && /^CHƯA LƯU/.test(await chip(pB)), 'tab B hiện rõ: không ghi đè, chưa lưu bền');
      await pB.close();
      snapshot = docA;
      var doc2 = docA;
    }
    // (c) mirror CŨ HƠN nguồn bền -> thay lặng lẽ bằng bản bền, không banner
    await p.reload(); await H.waitPhase(p, 'ONLINE');                    // tab A nạp lại bản mới nhất
    await p.evaluate(() => { const m = JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')); m.rev = 1; localStorage.setItem('ethdca-tracker-state-v1', JSON.stringify(m)); });
    await p.reload(); st = await H.waitPhase(p, 'ONLINE');
    assert(st.rev === doc2.rev && !st.diverged && (await mirror(p)).rev === doc2.rev, 'mirror cũ hơn bị thay bằng bản bền (rev ' + doc2.rev + '), không banner');
    snapshot = await H.getDoc('state');
  }
  end();

  /* ---------- CHECK-T09B-11 — read/auth failure visible ---------- */
  begin('CHECK-T09B-11', 'Firebase read failure visible — UID lạ bị rules từ chối; Firestore không với tới; Auth thất bại');
  {
    // (a) thiết bị/trình duyệt KHÁC (context mới => IndexedDB mới => UID mới) trong khi sổ đã tồn tại
    const other = await b.newContext(); await H.prepareContext(other);
    const q = await other.newPage(); const qe = H.attachErrors(q);
    await q.goto(H.baseUrl());
    const sq = await H.waitPhase(q, ['UNRECOGNIZED', 'ONLINE', 'OFFLINE', 'AUTH_FAILED']);
    assert(sq.phase === 'UNRECOGNIZED' && sq.uid !== uid, 'UID mới ' + sq.uid + ' -> phase UNRECOGNIZED (không phải ONLINE với sổ rỗng)');
    const bq = await banners(q);
    assert(/KHÔNG NHẬN DIỆN ĐƯỢC THIẾT BỊ\/TRÌNH DUYỆT NÀY/.test(bq), 'banner "KHÔNG NHẬN DIỆN ĐƯỢC THIẾT BỊ/TRÌNH DUYỆT NÀY"');
    assert(!/KHÔNG ĐỌC ĐƯỢC NGUỒN BỀN/.test(bq), 'không dùng chung thông điệp với lỗi mạng');
    assert(sq.rev === 0 && (await q.textContent('#osVal')).trim() === '—', 'không hiện sổ rỗng như sổ hợp lệ: chưa nạp gì');
    const mq = await uiContribute(q, '2026-06', 1000);
    assert(/Không ghi sổ/.test(mq) && (await H.status(q)).rev === 0, 'ghi sổ bị chặn: "' + mq + '"');
    assert((await H.getDoc('state')).rev === snapshot.rev, 'phía Firebase không đổi (sổ thật còn nguyên)');
    assert(/KHÔNG GHI SỔ/.test(await chip(q)), 'chip: ' + await chip(q));
    assert(qe.length === 0, 'không page error: ' + qe.join('; '));
    await other.close();

    // (b) Firestore không với tới được (Auth vẫn OK) trên profile của Owner -> OFFLINE, mirror chỉ để xem
    allErrs.push(...errs); await ctx.close();
    const deadFs = H.emulatorConfig({ emulator: { auth: 'http://127.0.0.1:9099', firestoreHost: '127.0.0.1', firestorePort: 1 } });
    ({ ctx, p, errs } = await H.newPersistent(chromium, profileDir, { config: deadFs }));
    const so = await H.waitPhase(p, ['OFFLINE', 'UNRECOGNIZED', 'ONLINE', 'AUTH_FAILED'], 60000);
    assert(so.phase === 'OFFLINE', 'phase OFFLINE (' + so.detail + ')');
    const bo = await banners(p);
    assert(/KHÔNG ĐỌC ĐƯỢC NGUỒN BỀN/.test(bo), 'banner đỏ "KHÔNG ĐỌC ĐƯỢC NGUỒN BỀN"');
    assert(so.mirrorShown && /CHƯA xác nhận từ nguồn bền/.test(bo), 'mirror hiển thị nhưng ĐÁNH DẤU chưa xác nhận');
    const mo = await uiContribute(p, '2026-06', 1000);
    assert(/Không ghi sổ/.test(mo) && (await H.status(p)).rev === so.rev, 'ghi sổ bị chặn khi OFFLINE');
    // SDK tự log "Could not reach Cloud Firestore backend" khi backend chết — đúng kịch bản này.
    allErrs.push(...errs.filter((e) => !/Could not reach Cloud Firestore backend/.test(e)));
    await ctx.close();

    // (c) Auth thất bại (không tới được Identity Toolkit) — trên context MỚI, vì profile đã có
    //     session Anonymous thì SDK dùng lại token đã cache mà không cần gọi Auth server (đúng).
    const deadAuth = H.emulatorConfig({ emulator: { auth: 'http://127.0.0.1:1', firestoreHost: '127.0.0.1', firestorePort: 8080 } });
    const fresh = await b.newContext(); await H.prepareContext(fresh, deadAuth);
    const qa = await fresh.newPage(); H.attachErrors(qa);
    await qa.goto(H.baseUrl());
    const sa = await H.waitPhase(qa, ['OFFLINE', 'UNRECOGNIZED', 'ONLINE', 'AUTH_FAILED'], 60000);
    assert(sa.phase === 'AUTH_FAILED', 'phase AUTH_FAILED (' + sa.detail + ')');
    assert(/KHÔNG XÁC THỰC ĐƯỢC/.test(await banners(qa)), 'banner "KHÔNG XÁC THỰC ĐƯỢC"');
    assert(/Không ghi sổ/.test(await uiContribute(qa, '2026-06', 1000)), 'ghi sổ bị chặn khi AUTH_FAILED');
    assert(/KHÔNG GHI SỔ/.test(await chip(qa)), 'chip: ' + await chip(qa));
    await fresh.close();

    // (d) chưa cấu hình Firebase (firebase_config.js còn REQUIRED) -> fail closed, không giả vờ có nguồn bền
    const unconf = await b.newContext();
    await H.prepareContext(unconf, H.emulatorConfig({ apiKey: 'REQUIRED', appId: 'REQUIRED' }));
    const qu = await unconf.newPage(); H.attachErrors(qu);
    await qu.goto(H.baseUrl());
    const su = await H.waitPhase(qu, ['UNCONFIGURED', 'OFFLINE', 'UNRECOGNIZED', 'ONLINE', 'AUTH_FAILED']);
    assert(su.phase === 'UNCONFIGURED', 'phase UNCONFIGURED khi config còn REQUIRED');
    assert(/CHƯA CẤU HÌNH FIREBASE/.test(await banners(qu)), 'banner "CHƯA CẤU HÌNH FIREBASE"');
    assert(/Không ghi sổ/.test(await uiContribute(qu, '2026-06', 1000)), 'ghi sổ bị chặn khi UNCONFIGURED');
    await unconf.close();

    // mở lại bình thường -> vẫn ONLINE với đúng sổ (các phase lỗi không làm hỏng gì)
    ({ ctx, p, errs } = await H.newPersistent(chromium, profileDir));
    const back = await H.waitPhase(p, 'ONLINE');
    assert(back.rev === snapshot.rev && H.diff(H.canon(snapshot), H.canon(await mirror(p))).length === 0, 'mở lại bình thường: sổ nguyên vẹn rev ' + back.rev);
  }
  end();

  /* ---------- CHECK-T09B-15 — historical state (ladder không có month) không bị backfill ---------- */
  begin('CHECK-T09B-15', 'Ladder không mang `month` (pre-T09A) sống sót round-trip; banner THÁNG SỞ HỮU SUY LUẬN vẫn hiện');
  {
    const legacy = JSON.parse(JSON.stringify(snapshot));
    legacy.ladders.forEach((L) => { delete L.month; });
    await H.putDoc('state', legacy);                          // sổ lịch sử dạng trước T-09A nằm trên Firestore
    await p.reload(); let st = await H.waitPhase(p, 'ONLINE');
    assert(st.rev === legacy.rev && !st.diverged, 'nạp được sổ lịch sử (không bị coi là corrupt)');
    assert(/THÁNG SỞ HỮU SUY LUẬN/.test(await banners(p)), 'banner "THÁNG SỞ HỮU SUY LUẬN" hiện');
    let m = await mirror(p);
    assert(m.ladders.every((L) => !('month' in L)), 'sau khi nạp: không ladder nào bị backfill month');
    await uiContribute(p, '2026-06', 1000);                    // một thao tác -> ghi lại lên Firestore
    st = await H.waitSaved(p);
    const doc = await H.getDoc('state');
    assert(doc.rev === legacy.rev + 1 && doc.ladders.every((L) => !('month' in L)), 'sau khi ghi lên lại: ladders[] vẫn KHÔNG có `month` (không backfill)');
    await p.reload(); await H.waitPhase(p, 'ONLINE');
    assert(/THÁNG SỞ HỮU SUY LUẬN/.test(await banners(p)), 'banner vẫn hiện sau round-trip');
    m = await mirror(p);
    assert(m.ladders.every((L) => !('month' in L)) && m.ladders.length === legacy.ladders.length, 'ladder lịch sử nguyên vẹn sau round-trip');
    // khôi phục sổ có month cho các ca sau
    await H.putDoc('state', snapshot);
  }
  end();

  /* ---------- CHECK-T09B-12 — corrupt / malformed durable state fail closed, không ghi đè ---------- */
  begin('CHECK-T09B-12', 'Durable state malformed/corrupt không thành accounting state; bản durable không bị ghi đè');
  {
    const cases = [];
    const a = JSON.parse(JSON.stringify(snapshot)); delete a.schema; cases.push(['(a) thiếu `schema`', a, /schema/]);
    const bb = JSON.parse(JSON.stringify(snapshot)); bb.months = ['2026-06']; cases.push(['(b) `months` sai kiểu (mảng)', bb, /months/]);
    const c = JSON.parse(JSON.stringify(snapshot)); c.months['2026-06'].smart.a += 250000; cases.push(['(c) đủ khoá nhưng TOTAL = A+R+D bị vi phạm', c, /TOTAL = A\+R\+D/]);
    const d = JSON.parse(JSON.stringify(snapshot)); d.months['2026-06'].smart.r = -1; d.months['2026-06'].smart.a += 1 + d.months['2026-06'].smart.r * 0; cases.push(['(d) reserved âm', d, /âm|không hợp lệ/]);
    for (const [label, bad, re] of cases) {
      await H.putDoc('state', bad);
      const before = H.canonJSON(await H.getDoc('state'));
      await p.reload();
      const st = await H.waitPhase(p, ['CORRUPT', 'ONLINE', 'OFFLINE']);
      assert(st.phase === 'CORRUPT', label + ': phase CORRUPT — ' + st.detail);
      assert(re.test(st.detail), label + ': lý do nêu đúng lỗi');
      assert(st.rev === 0 && (await p.textContent('#osVal')).trim() !== '', label + ': không nạp thành accounting state (rev 0)');
      const bn = await banners(p);
      assert(/NGUỒN BỀN KHÔNG HỢP LỆ/.test(bn) && /không ghi đè/.test(bn), label + ': banner đỏ, nói rõ không ghi đè');
      const mc = await uiContribute(p, '2026-06', 1000);
      assert(/Không ghi sổ/.test(mc), label + ': ghi sổ bị chặn');
      await p.click('#saveBtn', { force: true }).catch(() => {});
      await p.waitForTimeout(400);
      assert(H.canonJSON(await H.getDoc('state')) === before, label + ': bản durable KHÔNG bị ghi đè');
      assert(/KHÔNG GHI SỔ/.test(await chip(p)), label + ': chip "' + await chip(p) + '"');
    }
    await H.putDoc('state', snapshot);
    await p.reload(); const st = await H.waitPhase(p, 'ONLINE');
    assert(st.rev === snapshot.rev, 'khôi phục bản hợp lệ -> ONLINE lại bình thường');
  }
  end();

  allErrs.push(...errs);
  await ctx.close(); await b.close(); H.stopServer(); await stopEmu();
  try { fs.rmSync(profileDir, { recursive: true, force: true }); } catch (e) { /* ignore */ }

  console.log('\n=== TỔNG KẾT T-09B (file này) ===');
  const order = ['CHECK-T09B-01', 'CHECK-T09B-02', 'CHECK-T09B-03', 'CHECK-T09B-04', 'CHECK-T09B-05', 'CHECK-T09B-06',
    'CHECK-T09B-07', 'CHECK-T09B-08', 'CHECK-T09B-10', 'CHECK-T09B-11', 'CHECK-T09B-12', 'CHECK-T09B-14', 'CHECK-T09B-15', 'CHECK-T09B-16'];
  order.forEach((id) => console.log('  ' + id + ': ' + (results[id] ? (results[id].pass ? 'PASS' : 'FAIL') : 'NOT_TESTED') + ' — ' + (results[id] ? results[id].title : '')));
  console.log('  CHECK-T09B-09: xem test_t09a_accounting.js + test_multi_month_invariant.js + test_v01_v02_v03.js (readState = durable)');
  console.log('  CHECK-T09B-13: xem `npm --prefix webapp test` + `git diff --stat -- webapp/engine.js`');
  console.log('assertion đã chạy:', checks, '| FAIL:', failures, '| page errors:', allErrs.length);
  if (allErrs.length) console.log('PAGE ERRORS:\n  ' + allErrs.join('\n  '));
  if (failures > 0 || allErrs.length) { console.log('T-09B PERSISTENCE: FAIL'); process.exit(1); }
  console.log('T-09B PERSISTENCE: PASS (14/14 check trong file này, E1 trên Firebase Emulator Suite)');
})().catch((e) => { console.error('T-09B PERSISTENCE: ERROR', e); process.exit(1); });
