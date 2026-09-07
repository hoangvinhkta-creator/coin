/* T-14 bước C — CHECK-T14-01 (Google Sign-In thay Anonymous), CHECK-T14-11 (bằng chứng
 * multi-device/mirror-reconcile chạy lại được qua UI Step B — hấp thụ `H-49`) và CHECK-T14-12
 * (production reachability). Ánh xạ C-AS-01/02/03/05/06/07/14.
 * KHÔNG phải production path (PROJECT/PRODUCTION_PATHS.md §2). Dữ liệu TỔNG HỢP.
 *
 * Đường chạy: app_final.html do build_app.js sinh ra -> phục vụ qua HTTP như Firebase Hosting ->
 * Firebase SDK compat THẬT -> Firebase Auth Emulator + Firestore Emulator với ĐÚNG
 * `firestore.rules` của repo. Không mock SDK, không mock rules, không gọi hàm nội bộ của app.
 * Bằng chứng "phía Firebase" đọc ĐỘC LẬP qua REST của emulator (Node), không qua promise SDK.
 *
 * Bộ này THAY THẾ vai trò của `test_t09b_persistence.js` trên đường L-1: sáu file test V2.1.5
 * (gồm file đó) đòi `#seedFile` trong `#tab-setup` — bề mặt đã bị Step-B spec §12
 * (`REMOVE_FROM_L1_PATH`) gỡ hợp lệ ở T-13, nên chúng không còn chạy lại được (`H-49`). Các kịch
 * bản dưới đây phủ đúng hành vi mà `CHECK-T09B-01/02/03/04/10/12/16` bảo vệ, nhưng đo trên UI
 * Step B hiện hành và trên danh tính Google của bước C.
 *
 * GIỚI HẠN TRUNG THỰC (không che):
 *  - Emulator là bản Firebase chạy cục bộ (rules engine, Auth, wire protocol thật), KHÔNG phải
 *    project Firebase thật của chủ dự án — cùng giới hạn đã ghi ở `T-09B`/`T-12`/`T-13`.
 *  - `signInWithPopup()` bắt buộc nạp `https://apis.google.com/js/api.js`; sandbox này chặn toàn
 *    bộ mạng ra ngoài nên CỬA SỔ popup không hoàn tất được ở đây. PR-AUTH-1 kiểm chính điều đó:
 *    app gọi thật đường popup và FAIL CLOSED khi môi trường chặn. Phiên đăng nhập dùng cho các
 *    kịch bản còn lại được cấp qua đúng SDK thật bằng `GoogleAuthProvider.credential()` +
 *    `signInWithCredential()` — cơ chế test provider chính thức của Emulator Suite mà Step-C
 *    spec §15 cho phép — nên UID vẫn là UID federated `google.com` thật do Auth Emulator ký.
 */
const fs = require('fs');
const os = require('os');
const path = require('path');
const { chromium } = require('playwright');
const H = require('./test_firebase_harness.js');
const F = require('./test_t12_fixtures.js');
const L = require('./ledger.js');

let checks = 0, failures = 0, current = null;
const results = {};
function assert(cond, label) {
  checks++;
  if (!cond) { failures++; if (current) results[current].fails++; console.log('  ASSERT FAIL:', label); }
  else console.log('  ok:', label);
}
function begin(id, title) { current = id; results[id] = { fails: 0, title }; console.log('\n=== ' + id + ' — ' + title + ' ==='); }
function end() { const r = results[current]; r.pass = r.fails === 0; console.log('  => ' + current + ': ' + (r.pass ? 'PASS' : 'FAIL (' + r.fails + ' assert)')); current = null; }

/* ---------------- lái UI Step B (không gọi hàm nội bộ) ---------------- */
const value = (n, places = 0) => (n === null ? '' : (n / 10 ** places).toFixed(places));
const fill = (p, id, x) => p.locator('#' + id).fill(String(x));
const openDetails = (p) => p.locator('#l1Root details').evaluateAll((ds) => ds.forEach((d) => { d.open = true; }));
async function uiSetPlan(p, start) {
  await H.goTab(p, 'plan');                     // T-18: Kế hoạch nay là tab riêng
  await openDetails(p);
  await fill(p, 'l1StartMonth', start); await fill(p, 'l1Effective', start);
  await fill(p, 'l1Budget', 20000000); await fill(p, 'l1Days', '3,13,23');
  await p.click('#l1SavePlan'); await H.waitSaved(p);
}
async function uiSetOpening(p, o) {
  await H.goTab(p, 'plan');
  await openDetails(p);
  await fill(p, 'l1OpeningDate', o.asOf);
  const a = o.assets[0] || { qty: 0, costUsdt: 0, costVnd: 0 };
  for (const [id, x, places] of [['l1Eth', a.qty, 8], ['l1EthCostUsdt', a.costUsdt, 6], ['l1EthCostVnd', a.costVnd, 0],
    ['l1Usdt', o.usdt.qty, 6], ['l1UsdtCost', o.usdt.costVnd, 0], ['l1Vnd', o.vnd.qty, 0], ['l1Reserve', o.reserveVnd, 0]]) {
    await fill(p, id, value(x, places));
  }
  await fill(p, 'l1OpeningNote', o.note);
  await p.click('#l1SaveOpening'); await H.waitSaved(p);
}
async function uiEvent(p, e) {
  await openDetails(p);
  await p.selectOption('#l1Kind', e.kind);
  await fill(p, 'l1Date', e.businessDate); await fill(p, 'l1Note', e.note || '');
  if (e.kind === 'TREASURY') {
    await p.selectOption('#l1Dir', e.dir);
    await fill(p, 'l1P2pVnd', e.vndAmount); await fill(p, 'l1P2pUsdt', value(e.usdtAmount, 6));
  }
  if (e.kind === 'TRADE') {
    await p.selectOption('#l1Side', e.side); await p.selectOption('#l1Source', e.source);
    await fill(p, 'l1Notional', value(e.usdtNotional, 6)); await fill(p, 'l1Fee', value(e.feeUsdt, 6)); await fill(p, 'l1Qty', value(e.qty, 8));
  }
  await p.click('#l1SaveEvent');
  await H.waitSaved(p);
  return (await p.textContent('#l1Message')).trim();
}
/** Ảnh chụp TOÀN BỘ số liệu người dùng nhìn thấy — mọi thẻ dashboard + tóm tắt + cờ. */
async function ui(p) {
  return {
    cards: await p.locator('#dashMain .dcard').evaluateAll((xs) => xs.map((x) => [
      x.querySelector('.dc-label') ? x.querySelector('.dc-label').textContent : '',
      x.querySelector('.dc-value') ? x.querySelector('.dc-value').textContent : '',
      x.querySelector('.dc-sub') ? x.querySelector('.dc-sub').textContent : ''])),
    bottom: await p.locator('#dashBottom .stat').evaluateAll((xs) => xs.map((x) => [
      x.querySelector('small').textContent, x.querySelector('div').textContent])),
    summary: await p.locator('#l1Summary .stat').evaluateAll((xs) => xs.map((x) => [
      x.querySelector('small').textContent, x.querySelector('div').textContent])),
    flags: (await p.textContent('#l1Flags')).trim(),
    history: await p.locator('.hist-card[data-event]').count(),   // thẻ số dư đầu kỳ không mang data-event
  };
}
/** derive() tính ĐỘC LẬP trong Node trên bản durable đọc thẳng từ emulator (oracle T-12). */
async function durableDerived(asOf) {
  const d = await H.getDoc('state');
  if (!d) return null;
  const c = L.canonical(d);
  return { state: d, derived: L.derive(c.openingPosition, c.plan, c.events, asOf) };
}
const j = (x) => JSON.stringify(H.canon(x));
const TODAY = '2026-03-21';

(async () => {
  const stop = await H.ensureEmulators();
  const b = await chromium.launch({ executablePath: H.CHROMIUM });
  let ctx = null;
  const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), 't14-profile-'));
  try {
    /* ---------- PR-AUTH-0 — mã production không còn Anonymous Auth ---------- */
    begin('PR-AUTH-0', 'app_logic.js: KHÔNG còn signInAnonymously(); đăng nhập qua GoogleAuthProvider');
    const logic = fs.readFileSync(path.join(__dirname, 'app_logic.js'), 'utf8');
    assert(!/signInAnonymously\s*\(/.test(logic), 'không còn lệnh gọi signInAnonymously() nào trong app_logic.js');
    assert(/new firebase\.auth\.GoogleAuthProvider\(\)/.test(logic), 'dùng firebase.auth.GoogleAuthProvider()');
    assert(/signInWithPopup\(/.test(logic), 'đăng nhập qua signInWithPopup()');
    assert(/onAuthStateChanged\(/.test(logic), 'một điểm vào danh tính duy nhất: onAuthStateChanged');
    const built = fs.readFileSync(H.APP_FINAL, 'utf8');
    assert(!/signInAnonymously\s*\(/.test(built), 'bản build app_final.html cũng không còn signInAnonymously()');
    end();

    /* ---------- Mở app lần đầu: SIGNED_OUT, khoá ghi ---------- */
    const opened = await H.newPage(b, { seed: false, bootstrap: false });
    ctx = opened.ctx;
    const p = opened.p;
    await p.clock.install({ time: new Date(TODAY + 'T05:00:00Z') });
    await p.reload();

    begin('C-AS-02', 'Chưa đăng nhập -> KHÔNG đọc/ghi được dữ liệu tài chính CoinDCA');
    let st = await H.waitPhase(p, 'SIGNED_OUT');
    assert(st.phase === 'SIGNED_OUT', 'phase = SIGNED_OUT khi chưa có phiên Google nào');
    assert(st.uid === null, 'không có UID nào được gán');
    assert(/CHƯA ĐĂNG NHẬP/.test(await p.textContent('#banners')), 'banner "CHƯA ĐĂNG NHẬP" hiện rõ');
    assert(await p.locator('[data-auth="signin"]').first().isVisible(), 'nút "Đăng nhập bằng Google" có mặt');
    assert(await p.locator('#saveBtn').isDisabled(), 'nút lưu bị khoá — không ghi sổ');
    assert((await H.getDoc('state')) === null, 'phía Firebase: không document nào được tạo bởi phiên chưa đăng nhập');
    end();

    /* ---------- PR-AUTH-1 — nút bấm thật đi vào đường popup Google, fail closed ---------- */
    begin('PR-AUTH-1', 'Nút bấm chạy THẬT signInWithPopup(GoogleAuthProvider); môi trường chặn -> FAIL CLOSED');
    const attempt = await H.popupAttempt(p);
    assert(attempt.gapi === true,
      'SDK thật sự khởi động đường popup Google (yêu cầu apis.google.com/js/api.js) — không phải nhánh giả');
    assert(attempt.phase === 'AUTH_FAILED' || attempt.phase === 'ONLINE',
      'kết cục xác định: AUTH_FAILED (sandbox chặn mạng) hoặc ONLINE (môi trường có mạng) — thấy ' + attempt.phase);
    if (attempt.phase === 'AUTH_FAILED') {
      assert(await p.locator('#saveBtn').isDisabled(), 'popup thất bại -> vẫn khoá ghi sổ (fail closed)');
      assert((await H.getDoc('state')) === null, 'popup thất bại -> không ghi gì lên Firebase');
      console.log('    (môi trường sandbox chặn apis.google.com — chi tiết: ' + attempt.detail + ')');
    }
    end();

    /* ---------- C-AS-01 — Owner đăng nhập Google, rules nhận đúng UID ---------- */
    begin('C-AS-01', 'Owner đăng nhập Google -> UID tài khoản Google -> rules cho truy cập');
    await p.reload();
    await H.waitPhase(p, 'SIGNED_OUT');
    const ownerUid = await H.googleSignIn(p);
    st = await H.waitPhase(p, ['UNRECOGNIZED', 'ONLINE']);
    assert(st.uid === ownerUid, 'app dùng đúng UID phiên Google vừa đăng nhập (' + ownerUid + ')');
    assert(st.phase === 'UNRECOGNIZED', 'rules còn OWNER_UID_REQUIRED -> app từ chối, không im lặng coi là sổ trống');
    assert(/KHÔNG PHẢI CHỦ SỞ HỮU/.test(await p.textContent('#banners')), 'banner nói đúng lý do: UID không phải chủ sở hữu');
    await H.setRules(ownerUid);            // đúng thao tác Owner deploy rules
    await p.reload();
    st = await H.waitPhase(p, 'ONLINE');
    assert(st.uid === ownerUid, 'tải lại: phiên Google được khôi phục, cùng UID, KHÔNG phải đăng nhập lại');
    assert(st.email === H.OWNER_EMAIL, 'email tài khoản Google hiển thị đúng: ' + st.email);
    end();

    /* ---------- C-AS-05 — ghi qua UI -> server ACK -> reload -> khớp chính xác ---------- */
    begin('C-AS-05', 'Owner ghi qua UI Step B -> máy chủ xác nhận -> tải lại -> khớp chính xác');
    await uiSetPlan(p, '2026-03');
    await uiSetOpening(p, F.opening);
    await uiEvent(p, F.p2p(1, '2026-03-05', 25600000, 1000000000));
    await uiEvent(p, F.buy(2, '2026-03-13', 600000000, 25000000, 'PLAN', 600000));
    const before = await ui(p);
    const durable = await durableDerived(TODAY);
    const mem = await p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));
    assert(j(durable.state) === j(mem), 'bản durable phía Firebase khớp BIT-EXACT với bản trong trang');
    assert(durable.state.events.length === 2 && !!durable.state.openingPosition, 'durable có đủ 2 giao dịch + số dư đầu kỳ');
    assert(before.history === 2, 'UI hiển thị đúng 2 giao dịch trong Lịch sử');
    await p.reload(); await H.waitPhase(p, 'ONLINE');
    assert(j(await ui(p)) === j(before), 'tải lại: TOÀN BỘ số liệu hiển thị khớp từng ký tự');
    const after = await durableDerived(TODAY);
    assert(j(after.derived) === j(durable.derived), 'derive() trên bản durable sau reload trùng khít (tolerance 0)');
    end();

    /* ---------- CHECK-T14-01 — đăng xuất/đăng nhập lại cùng tài khoản ---------- */
    begin('CHECK-T14-01', 'Đăng xuất -> đăng nhập lại cùng tài khoản Google -> đúng UID, đúng sổ cũ');
    await H.googleSignOut(p);
    st = await H.status(p);
    assert(st.phase === 'SIGNED_OUT' && st.uid === null, 'sau đăng xuất: SIGNED_OUT, không còn UID');
    assert(st.durableRev === null && st.rev === 0, 'sổ bị xoá khỏi bộ nhớ trang (không rò rỉ sang phiên sau)');
    assert(j(await H.getDoc('state')) === j(durable.state), 'đăng xuất KHÔNG chạm nguồn bền — Firestore giữ nguyên');
    const uid2 = await H.googleSignIn(p);
    await H.waitPhase(p, 'ONLINE');
    assert(uid2 === ownerUid, 'đăng nhập lại cho ĐÚNG UID cũ (UID là của tài khoản Google, không của phiên)');
    assert(j(await ui(p)) === j(before), 'sổ cũ hiện lại y hệt sau khi đăng nhập lại');
    end();

    /* ---------- C-AS-03 (đường sản phẩm) — tài khoản Google khác bị từ chối ---------- */
    begin('C-AS-03', 'Tài khoản Google KHÁC đăng nhập -> bị từ chối, không thấy và không ghi được sổ');
    await H.googleSignOut(p);
    const otherUid = await H.googleSignIn(p, { sub: H.OTHER_SUB, email: H.OTHER_EMAIL });
    st = await H.waitPhase(p, 'UNRECOGNIZED');
    assert(otherUid !== ownerUid, 'UID tài khoản khác khác hẳn UID Owner');
    assert(st.phase === 'UNRECOGNIZED', 'phase = UNRECOGNIZED (không phải "sổ trống")');
    assert(st.durableRev === null, 'không nạp được bất kỳ dữ liệu tài chính nào của Owner');
    assert(await p.locator('#saveBtn').isDisabled(), 'khoá ghi sổ hoàn toàn');
    assert(j(await H.getDoc('state')) === j(durable.state), 'nguồn bền của Owner không bị chạm');
    await H.googleSignOut(p);
    await H.googleSignIn(p); await H.waitPhase(p, 'ONLINE');
    end();

    /* ---------- C-AS-07 — mirror cũ/lệch KHÔNG ghi đè sự thật máy chủ (hấp thụ CHECK-T09B-16) ---------- */
    begin('C-AS-07', 'localStorage mới hơn nguồn bền -> KHÔNG âm thầm thắng; server vẫn là sự thật');
    const fake = JSON.parse(JSON.stringify(durable.state));
    fake.rev = durable.state.rev + 5;
    fake.events = fake.events.slice(0, 1);          // sổ KHÁC HẲN: thiếu một giao dịch
    await p.evaluate((v) => localStorage.setItem('ethdca-tracker-state-v1', JSON.stringify(v)), fake);
    await p.reload(); st = await H.waitPhase(p, 'ONLINE');
    assert(st.diverged === true, 'app phát hiện phân kỳ và CHỜ người dùng chọn');
    assert(st.durableRev === durable.state.rev, 'app đứng trên bản BỀN, không trên mirror');
    assert(j(await ui(p)) === j(before), 'số liệu hiển thị = bản của máy chủ, không phải bản mirror lệch');
    assert(j(await H.getDoc('state')) === j(durable.state), 'phía Firebase: KHÔNG bị mirror ghi đè');
    assert(await p.locator('#saveBtn').isDisabled(), 'trong lúc chờ chọn: khoá ghi');
    await p.click('[data-pdiv="drop"]');
    await p.waitForFunction(() => window.ETHDCA_DEBUG.status().diverged === false, null, { timeout: 5000 });
    assert(j(await H.getDoc('state')) === j(durable.state), 'chọn "Bỏ bản trên máy" -> nguồn bền vẫn nguyên');
    end();

    /* ---------- Ghi xung đột: revision cũ hơn không ghi đè bản mới hơn ---------- */
    begin('T14-CONFLICT', 'Ghi xung đột (một nơi khác vừa ghi) -> từ chối ghi đè, không mất dữ liệu máy chủ');
    const external = JSON.parse(JSON.stringify(durable.state));
    external.rev += 1;
    await H.putDoc('state', external);
    await uiEvent(p, F.buy(3, '2026-03-17', 100000000, 4000000, 'EXTRA')).catch(() => {});
    await p.waitForFunction(() => window.ETHDCA_DEBUG.status().lastError === 'stale-durable', null, { timeout: 15000 }).catch(() => {});
    assert((await H.status(p)).lastError === 'stale-durable', 'app báo đúng lỗi stale-durable');
    assert(j(await H.getDoc('state')) === j(external), 'phía Firebase: bản mới hơn KHÔNG bị tab cũ ghi đè');
    assert(/ĐÃ ĐỔI Ở NƠI KHÁC/.test(await p.textContent('#banners')), 'banner nói rõ nguồn bền đã đổi ở nơi khác');
    end();

    /* ---------- Nguồn bền hỏng -> fail closed, không ghi đè ---------- */
    begin('T14-CORRUPT', 'Bản durable không hợp lệ -> không trở thành sổ, không bị ghi đè');
    const corrupt = { schema: 'unsupported/999', rev: external.rev + 1 };
    await H.putDoc('state', corrupt);
    await p.evaluate(() => localStorage.removeItem('ethdca-tracker-state-v1'));
    await p.reload(); st = await H.waitPhase(p, 'CORRUPT');
    assert(st.phase === 'CORRUPT', 'phase = CORRUPT');
    assert(await p.locator('#saveBtn').isDisabled(), 'khoá ghi sổ');
    assert(j(await H.getDoc('state')) === j(corrupt), 'bản hỏng được GIỮ NGUYÊN để cứu, không bị wipe/backfill');
    await H.putDoc('state', durable.state);
    end();

    /* ---------- Rules từ chối ghi -> hiện rõ, không báo "đã lưu" ---------- */
    begin('T14-WRITE-DENIED', 'Rules từ chối ghi -> app KHÔNG báo đã lưu; nguồn bền không đổi');
    await p.reload(); await H.waitPhase(p, 'ONLINE');
    await H.setRules('SOMEONE_ELSE_UID');
    await openDetails(p);
    await p.selectOption('#l1Kind', 'TRADE'); await p.selectOption('#l1Side', 'BUY'); await p.selectOption('#l1Source', 'EXTRA');
    await fill(p, 'l1Date', '2026-03-18'); await fill(p, 'l1Note', 'ghi khi bị từ chối');
    await fill(p, 'l1Notional', value(100000000, 6)); await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', value(4000000, 8));
    await p.click('#l1SaveEvent');
    await p.waitForFunction(() => /permission-denied/i.test(String(window.ETHDCA_DEBUG.status().lastError || '')), null, { timeout: 15000 });
    assert(/permission-denied/i.test((await H.status(p)).lastError), 'lỗi permission-denied hiện trong trạng thái');
    assert(!/Đã lưu bền/.test(await p.textContent('#saveChip')), 'chip KHÔNG báo "Đã lưu bền"');
    assert(j(await H.getDoc('state')) === j(durable.state), 'nguồn bền không đổi một byte nào');
    await H.setRules(ownerUid);
    end();

    /* ---------- C-AS-06 — hồ sơ trình duyệt hoàn toàn mới ---------- */
    begin('C-AS-06', 'Trình duyệt/hồ sơ MỚI, localStorage trống -> đăng nhập -> ĐÚNG sổ đó');
    await ctx.close(); ctx = null;
    const fresh = await H.newPersistent(chromium, profileDir);
    ctx = fresh.ctx;
    const q = fresh.p;
    await q.clock.install({ time: new Date(TODAY + 'T05:00:00Z') });
    await q.reload();
    let qs = await H.waitPhase(q, 'SIGNED_OUT');
    assert(qs.phase === 'SIGNED_OUT', 'hồ sơ mới: chưa có phiên nào — KHÔNG tự coi là chủ sở hữu mới');
    const emptyLS = await q.evaluate(() => localStorage.getItem('ethdca-tracker-state-v1'));
    assert(emptyLS === null, 'hồ sơ mới thật sự trống localStorage (không thừa hưởng gì)');
    const uid3 = await H.googleSignIn(q);
    qs = await H.waitPhase(q, 'ONLINE');
    assert(uid3 === ownerUid, 'CÙNG tài khoản Google trên hồ sơ mới -> CÙNG UID (danh tính không gắn thiết bị)');
    assert(j(await ui(q)) === j(before), 'hồ sơ mới tải ĐÚNG sổ cũ từ máy chủ — không hiện trạng thái rỗng');
    assert(qs.durableRev === durable.state.rev, 'đứng đúng trên rev bền của máy chủ');
    end();

    /* ---------- Đóng/mở lại cùng hồ sơ: phiên Google được khôi phục ---------- */
    begin('T14-RESTART', 'Đóng hẳn trình duyệt, mở lại cùng hồ sơ -> phiên Google còn, không phải đăng nhập lại');
    await ctx.close(); ctx = null;
    const again = await H.newPersistent(chromium, profileDir);
    ctx = again.ctx;
    const r = again.p;
    await r.clock.install({ time: new Date(TODAY + 'T05:00:00Z') });
    await r.reload();
    const rs = await H.waitPhase(r, 'ONLINE');
    assert(rs.uid === ownerUid, 'mở lại: vào thẳng ONLINE với đúng UID, không qua màn đăng nhập');
    assert(j(await ui(r)) === j(before), 'số liệu khớp chính xác sau khi mở lại trình duyệt');
    assert(j(await H.getDoc('state')) === j(durable.state), 'nguồn bền vẫn nguyên sau toàn bộ kịch bản');
    end();

    /* ---------- Xoá sạch localStorage + sessionStorage trên hồ sơ đang đăng nhập ---------- */
    begin('T14-CLEAR-STORAGE', 'Xoá localStorage + sessionStorage -> vẫn khôi phục đủ sổ từ Firestore');
    await r.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await r.reload();
    await H.waitPhase(r, 'ONLINE');
    assert(j(await ui(r)) === j(before), 'mất toàn bộ bộ nhớ cục bộ KHÔNG mất sổ và KHÔNG mất quyền sở hữu');
    end();

    console.log('\n=== errors console/pageerror (phải rỗng) ===');
    console.log(' ', JSON.stringify(opened.errs.concat(fresh.errs, again.errs)));
    assert(opened.errs.concat(fresh.errs, again.errs).length === 0, 'không có pageerror/console error nào trong toàn bộ phiên');
  } finally {
    if (ctx) await ctx.close();
    await b.close(); await H.stopServer(); await stop();
  }

  const order = ['PR-AUTH-0', 'C-AS-02', 'PR-AUTH-1', 'C-AS-01', 'C-AS-05', 'CHECK-T14-01', 'C-AS-03',
    'C-AS-07', 'T14-CONFLICT', 'T14-CORRUPT', 'T14-WRITE-DENIED', 'C-AS-06', 'T14-RESTART', 'T14-CLEAR-STORAGE'];
  console.log('\n=== TỔNG KẾT test_t14_persistence ===');
  order.forEach((id) => console.log('  ' + id + ': ' + (results[id] && results[id].pass ? 'PASS' : 'FAIL') + ' — ' + (results[id] || {}).title));
  console.log('assertion đã chạy:', checks, '| FAIL:', failures);
  if (failures > 0) { console.log('T-14 PERSISTENCE: FAIL'); process.exit(1); }
  console.log('T-14 PERSISTENCE: PASS — CHECK-T14-01 + CHECK-T14-11 + CHECK-T14-12 (C-AS-01/02/03/05/06/07/14)');
})().catch((e) => { console.error(e); process.exit(1); });
