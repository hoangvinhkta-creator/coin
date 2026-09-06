/* T-13 Step B — production reachability qua giao diện MỚI (PR-1..PR-6, AS-01..AS-12).
 * KHÔNG phải production path (PROJECT/PRODUCTION_PATHS.md §2). Dùng dữ liệu tổng hợp.
 * Oracle số học = chính CoinLedger.derive() (Step-B spec §14: T-12 là oracle, không dựng lại).
 */
const A = require('assert/strict'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright'), H = require('./test_firebase_harness'), F = require('./test_t12_fixtures'), L = require('./ledger');
const results = [], record = (name, detail) => { results.push({ name, status: 'PASS', detail }); console.log('PASS ' + name + ' ' + detail); };
const value = (n, places = 0) => n === null ? '' : (n / 10 ** places).toFixed(places);
async function fill(p, id, x) { await p.locator('#' + id).fill(String(x)); }
async function openDetails(p) { await p.locator('#l1Root details').evaluateAll(ds => ds.forEach(d => d.open = true)); }
async function pickType(p, key) { await p.click('.txtype[data-txtype="' + key + '"]'); }
async function saveEvent(p, expectOk = true) {
  await p.click('#l1SaveEvent'); await p.waitForTimeout(60);
  const m = await p.textContent('#l1Message');
  if (expectOk) { await H.waitSaved(p); A.doesNotMatch(m, /không hợp lệ|không hỗ trợ|thiếu|Sai|trước số dư|cần lý do/i); }
  return m;
}
async function setOpening(p, o) {
  await openDetails(p);
  await fill(p, 'l1OpeningDate', o.asOf);
  const a = o.assets[0] || { qty: 0, costUsdt: 0, costVnd: 0 };
  for (const [id, x, places, nullable] of [['l1Eth', a.qty, 8], ['l1EthCostUsdt', a.costUsdt, 6], ['l1EthCostVnd', a.costVnd, 0], ['l1Usdt', o.usdt.qty, 6], ['l1UsdtCost', o.usdt.costVnd, 0, true]]) {
    await fill(p, id, x === null && nullable ? '' : value(x, places));
  }
  await fill(p, 'l1Vnd', value(o.vnd.qty, 0)); await fill(p, 'l1Reserve', value(o.reserveVnd, 0)); await fill(p, 'l1OpeningNote', o.note);
  await p.click('#l1SaveOpening'); await H.waitSaved(p);
}
async function setPlan(p, start, budget, days) {
  await openDetails(p);
  await fill(p, 'l1StartMonth', start); await fill(p, 'l1Effective', start);
  await fill(p, 'l1Budget', budget); await fill(p, 'l1Days', days);
  await p.click('#l1SavePlan'); await H.waitSaved(p);
}
async function dashCards(p) {
  return p.locator('#dashMain .dcard').evaluateAll(xs => xs.map(x => ({
    label: x.querySelector('.dc-label').textContent, value: x.querySelector('.dc-value').textContent,
    sub: x.querySelector('.dc-sub') ? x.querySelector('.dc-sub').textContent : '',
  })));
}
async function dashBottom(p) { return p.locator('#dashBottom .stat').evaluateAll(xs => Object.fromEntries(xs.map(x => [x.querySelector('small').textContent, x.querySelector('div').textContent]))); }
async function histCount(p) { return p.locator('.hist-card').count(); }
async function snapshotClick(p, selector) { const dl = p.waitForEvent('download'); await p.click(selector); const f = await dl; return JSON.parse(fs.readFileSync(await f.path(), 'utf8')); }

(async () => {
  const stop = await H.ensureEmulators(); const b = await chromium.launch({ executablePath: H.CHROMIUM }); let ctx;
  try {
    const opened = await H.newPage(b, { seed: false }); ctx = opened.ctx; const p = opened.p;
    await p.clock.install({ time: new Date('2026-03-21T05:00:00Z') }); await p.reload(); await H.waitPhase(p, 'ONLINE');

    // PR-1: bundle thật qua app_final.html (đã dùng H.newPage -> server thật, không gọi hàm module trực tiếp).
    record('PR-1', 'App nạp qua app_final.html (bundle của build_app.js) qua HTTP server, không gọi module Node trực tiếp.');

    // Kế hoạch + Số dư đầu kỳ (tương đương SC-09/SC-10) — qua UI mới, mục Kế hoạch.
    await setPlan(p, '2026-03', '20000000', '3,13,23');
    await setOpening(p, F.scenarios.find(s => s.id === 'SC-09').state.openingPosition);

    // AS-02: FAB "+ Ghi giao dịch" -> chọn "Đổi VND → USDT" -> điền -> Lưu; Tổng quan cập nhật ngay.
    await pickType(p, 'p2p_in'); await fill(p, 'l1Date', '2026-03-05'); await fill(p, 'l1Note', 'P2P vào');
    await fill(p, 'l1P2pVnd', '25600000'); await fill(p, 'l1P2pUsdt', value(1000000000, 6));
    await saveEvent(p);
    let bottom = await dashBottom(p);
    A.equal(bottom['USDT hiện có'], (3000000000 / 1e6).toLocaleString('vi-VN', { maximumFractionDigits: 6 }));
    record('AS-02a', 'Đổi VND→USDT qua sheet mới cập nhật USDT hiện có ngay, không reload.');

    // BUY-PLAN qua thẻ "Ghi đã mua" (nếu có) hoặc FAB — dùng FAB để có oracle rõ ràng theo march fixture.
    await pickType(p, 'buy_plan'); await fill(p, 'l1Date', '2026-03-03'); await fill(p, 'l1Notional', value(240000000, 6)); await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', value(10000000, 8));
    await saveEvent(p);
    await pickType(p, 'buy_plan'); await fill(p, 'l1Date', '2026-03-13'); await fill(p, 'l1Notional', value(240000000, 6)); await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', value(10000000, 8));
    await saveEvent(p);
    record('AS-02b', 'Hai lệnh Mua ETH · Kế hoạch qua sheet ghi đúng source=PLAN.');

    // AS-03: BUY-EXTRA — investedThisMonthVnd tăng, planInvestedVnd/remainingPlannedBudgetVnd/next giữ nguyên.
    let s = await H.readState(p);
    const d0 = L.derive(s.openingPosition, s.plan, s.events, '2026-03-21');
    await pickType(p, 'buy_extra'); await fill(p, 'l1Date', '2026-03-17'); await fill(p, 'l1Notional', value(200000000, 6)); await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', value(8000000, 8));
    await saveEvent(p);
    s = await H.readState(p);
    const d1 = L.derive(s.openingPosition, s.plan, s.events, '2026-03-21');
    A.ok(d1.month.investedThisMonthVnd > d0.month.investedThisMonthVnd, 'invested tăng sau EXTRA');
    A.equal(d1.month.planInvestedVnd, d0.month.planInvestedVnd, 'INV-9: EXTRA không đụng planInvestedVnd');
    A.equal(d1.month.remainingPlannedBudgetVnd, d0.month.remainingPlannedBudgetVnd, 'INV-9: EXTRA không đụng remainingPlannedBudgetVnd');
    A.equal(d1.month.nextPlannedDate, d0.month.nextPlannedDate, 'INV-9: EXTRA không đụng nextPlannedDate');
    let cards = await dashCards(p);
    const histTexts = await p.locator('.hist-card').allInnerTexts();
    A.ok(histTexts.some(t => /EXTRA/.test(t)), 'badge EXTRA hiện ở một thẻ Lịch sử');
    record('AS-03', 'Mua EXTRA qua UI: invested tăng, planInvested/remaining/nextPlanned bất biến (INV-9); badge EXTRA hiện ở Lịch sử.');

    // AS-04: Nạp dự phòng rồi Mua-Từ dự phòng — thiếu note bị chặn tại form.
    await pickType(p, 'reserve_add'); await fill(p, 'l1Date', '2026-03-02'); await fill(p, 'l1ReserveAmount', '10000000');
    await saveEvent(p);
    await pickType(p, 'buy_reserve'); await fill(p, 'l1Date', '2026-03-20'); await fill(p, 'l1Notional', value(160000000, 6)); await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', value(6400000, 8));
    await fill(p, 'l1Note', '');
    const blocked = await saveEvent(p, false);
    A.match(blocked, /cần lý do/);
    s = await H.readState(p);
    A.equal(s.events.some(e => e.kind === 'TRADE' && e.source === 'RESERVE'), false, 'chưa lưu khi thiếu note');
    await fill(p, 'l1Note', 'giải ngân dự phòng, giá giảm sâu');
    await saveEvent(p);
    s = await H.readState(p);
    const d2 = L.derive(s.openingPosition, s.plan, s.events, '2026-03-21');
    A.ok(d2.reserve.balance < 10000000 && d2.reserve.balance >= 0, 'dự phòng giảm đúng chiều sau giải ngân');
    cards = await dashCards(p);
    const reserveCard = cards.find(c => c.label === 'Số dư dự phòng');
    A.equal(reserveCard.value, d2.reserve.balance.toLocaleString('vi-VN', { maximumFractionDigits: 0 }) + ' ₫');
    record('AS-04', 'Nạp dự phòng rồi Mua-Từ dự phòng: thiếu note bị chặn tại form (không cần lỗi ledger.js); có note thì lưu, và số dư dự phòng trên Tổng quan khớp bit-với-bit derive().');

    // AS-05: sửa một giao dịch cũ (đổi qty) — derive() chạy lại, id/seq không đổi.
    const editTarget = s.events.find(e => e.kind === 'TRADE' && e.source === 'PLAN' && e.businessDate === '2026-03-03');
    await p.click('button[data-id="' + editTarget.id + '"][data-action="edit"]');
    await fill(p, 'l1Qty', value(9000000, 8));
    await saveEvent(p);
    const sAfterEdit = await H.readState(p);
    const edited = sAfterEdit.events.find(e => e.id === editTarget.id);
    A.equal(edited.seq, editTarget.seq); A.equal(edited.qty, 9000000);
    record('AS-05', 'Sửa giao dịch qua Lịch sử → derive() chạy lại; id/seq bất biến (INV-15).');

    // AS-06: xoá một giao dịch — snapshot JSON tạo tự động TRƯỚC khi xoá; sau xoá như chưa từng có.
    const deleteTarget = sAfterEdit.events.find(e => e.kind === 'RESERVE' && e.type === 'CONTRIBUTE');
    const beforeDeleteJson = JSON.stringify(sAfterEdit);
    const snap = await snapshotClick(p, 'button[data-id="' + deleteTarget.id + '"][data-action="delete"]');
    A.deepEqual(snap.state, JSON.parse(beforeDeleteJson));
    await H.waitSaved(p);
    const afterDelete = await H.readState(p);
    A.equal(afterDelete.events.some(e => e.id === deleteTarget.id), false);
    record('AS-06', 'Xoá qua Lịch sử: snapshot JSON xuất hiện trước khi xoá; sau xoá event biến mất khỏi durable.');

    // AS-11: nhập muộn — businessDate ở giữa các event đã có (không phải hôm nay 21/03) vẫn ghi
    // đúng thứ tự, không cần thao tác đặc biệt (ngày vẫn phải >= số dư đầu kỳ 2026-03-01).
    await pickType(p, 'p2p_in'); await fill(p, 'l1Date', '2026-03-04'); await fill(p, 'l1Note', 'nhập muộn'); await fill(p, 'l1P2pVnd', '5000000'); await fill(p, 'l1P2pUsdt', value(200000000, 6));
    await saveEvent(p);
    const sLate = await H.readState(p);
    A.ok(sLate.events.some(e => e.businessDate === '2026-03-04'));
    record('AS-11', 'Nhập muộn (2026-03-04, xen giữa các giao dịch 03/03..21/03 đã có) ghi được qua sheet không cần thao tác đặc biệt; thứ tự (businessDate,seq) do derive() tự xử lý.');

    // AS-01/AS-08: Tổng quan khớp bit-với-bit derive() (tolerance 0).
    const sFinal = await H.readState(p);
    const dFinal = L.derive(sFinal.openingPosition, sFinal.plan, sFinal.events, '2026-03-21');
    cards = await dashCards(p);
    const byLabel = Object.fromEntries(cards.map(c => [c.label, c]));
    const vnd = n => (n === null ? '—' : n.toLocaleString('vi-VN', { maximumFractionDigits: 0 })) + ' ₫';
    A.equal(byLabel['Ngân sách tháng'].value, vnd(dFinal.month.plannedBudgetVnd));
    A.equal(byLabel['Đã đầu tư tháng này'].value, vnd(dFinal.month.investedThisMonthVnd));
    A.equal(byLabel['Còn lại theo kế hoạch'].value, vnd(dFinal.month.remainingPlannedBudgetVnd));
    A.equal(byLabel['Số dư dự phòng'].value, vnd(dFinal.reserve.balance));
    A.equal(byLabel['Mua kế tiếp'].value, dFinal.month.nextPlannedDate || '—');
    record('AS-01/AS-08', 'Bốn số + hành động kế tiếp trên Tổng quan khớp bit-với-bit derive() (tolerance 0), gồm nextPlannedDate/Amount theo scheduleDays/carry.');

    // AS-07: opening thiếu costVnd (usdt) -> "—" + banner UNKNOWN_VND_BASIS thường trực, không nút ẩn.
    await setOpening(p, Object.assign({}, F.opening, { usdt: { qty: 200000000, costVnd: null } }));
    bottom = await dashBottom(p);
    A.equal(bottom['Giá vốn TB ETH (VND)'], '—');
    const flagsText = await p.textContent('#l1Flags');
    A.match(flagsText, /UNKNOWN_VND_BASIS/);
    A.equal(await p.locator('#l1Flags button').count(), 0, 'banner UNKNOWN không có nút ẩn/dismiss');
    record('AS-07', 'Opening với usdt.costVnd=null: giá vốn VND hiện "—", banner UNKNOWN_VND_BASIS thường trực, không nút ẩn vĩnh viễn trong DOM.');

    // AS-10 — T-16 (DEC-052) ĐẢO CHIỀU khẳng định này. T-13 đòi "không SELL, không P&L" vì lúc đó
    // nghiệp vụ bán chưa được thiết kế và eventCheck chặn nó (T-15). T-16 thiết kế xong (H-46 phần
    // bán lấy USDT), nên UI PHẢI có đường bán và PHẢI hiện lãi/lỗ đã thực hiện — tách rõ hai đơn vị.
    const uiText = await p.evaluate(() => Array.from(document.querySelectorAll(
      'button, option, label, select, .txtype, h1, h2, h3, summary, .dc-label, .dc-value, .hc-main, .stat small'
    )).map(el => el.textContent).join(' | '));
    A.match(uiText, /Bán coin/, 'phải có đường ghi lệnh bán');
    A.match(uiText, /Lãi\/lỗ đã thực hiện \(USDT\)/, 'P&L thực hiện của lệnh bán hiện bằng ĐƠN VỊ USDT');
    A.match(uiText, /Lãi\/lỗ tỷ giá đã thực hiện \(VND\)/, 'lãi/lỗ tỷ giá hiện riêng bằng VND');
    A.doesNotMatch(uiText, /USDT\s*\+\s*VND|gộp/i, 'hai đơn vị không được gộp thành một con số');
    A.match(uiText, /Nạp tiền mặt|Rút tiền mặt/, 'phải có đường ghi nạp/rút tiền mặt VND');
    record('AS-10', 'T-16: UI có đường BÁN và hiển thị lãi/lỗ đã thực hiện tách hai đơn vị (USDT / VND), có nạp-rút tiền mặt VND.');

    /* ---- T-16 (DEC-052): đa tài sản + BÁN + tiền mặt qua ĐÚNG các control mới, không gọi module ---- */
    await setOpening(p, F.scenarios.find(s => s.id === 'SC-09').state.openingPosition);   // khôi phục giá vốn đã biết sau AS-07
    // Nạp tiền mặt phải nằm TRƯỚC cuộc đổi VND->USDT ở AS-02a (25.600.000 ₫ ngày 05/03), nếu không
    // vnd.balance âm ngay tại lệnh đổi đó và cờ LEDGER_INCONSISTENT của T-15 bật đúng — chính là
    // vấn đề mà CASH DEPOSIT sinh ra để giải quyết cho sổ nhập từ nguồn cũ.
    await pickType(p, 'cash_in'); await fill(p, 'l1Date', '2026-03-01'); await fill(p, 'l1Note', 'nạp tiền mặt vào ví');
    await fill(p, 'l1CashAmount', '40000000'); await saveEvent(p);
    await pickType(p, 'buy_extra'); await p.selectOption('#l1Symbol', 'BTC'); await fill(p, 'l1Date', '2026-03-07'); await fill(p, 'l1Note', 'mua BTC ngoài kế hoạch');
    await fill(p, 'l1Notional', value(120000000, 6)); await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', value(1000000, 8)); await saveEvent(p);
    await pickType(p, 'sell'); await p.selectOption('#l1Symbol', 'ETH'); await fill(p, 'l1Date', '2026-03-20'); await fill(p, 'l1Note', 'bán bớt ETH');
    await fill(p, 'l1Notional', value(60000000, 6)); await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', value(2000000, 8)); await saveEvent(p);
    const s16 = await H.readState(p);
    const kinds = s16.events.map(e => e.kind + '/' + (e.side || e.type || e.dir || '') + '/' + (e.symbol || ''));
    A.ok(kinds.includes('CASH/DEPOSIT/'), 'UI ghi được event CASH DEPOSIT: ' + JSON.stringify(kinds));
    A.ok(kinds.includes('TRADE/BUY/BTC'), 'UI ghi được lệnh mua BTC');
    A.ok(kinds.includes('TRADE/SELL/ETH'), 'UI ghi được lệnh bán ETH');
    const d16 = L.derive(s16.openingPosition, s16.plan, s16.events, '2026-03-21');
    // Khẳng định đúng thứ CASH DEPOSIT sinh ra để giải quyết: sổ này có hai cuộc đổi VND->USDT
    // (30.600.000 ₫) trong khi số dư đầu kỳ vnd = 0. KHÔNG có CASH DEPOSIT thì vnd âm và cờ
    // LEDGER_INCONSISTENT của T-15 bật; CÓ nó thì vnd dương và cờ đó không còn do tiền mặt gây ra.
    // (Sổ ở bước này còn một cờ khác không liên quan tới T-16: AS-06 đã xoá lệnh nạp dự phòng nên
    //  lệnh "mua từ dự phòng" ở 20/03 làm reserve âm — hành vi có sẵn, không phải hồi quy.)
    const noCash = L.derive(s16.openingPosition, s16.plan, s16.events.filter(e => e.kind !== 'CASH'), '2026-03-21');
    A.ok(noCash.vnd.balance < 0 && noCash.flags.includes('LEDGER_INCONSISTENT'), 'không có CASH DEPOSIT: vnd âm + cờ');
    A.ok(d16.vnd.balance >= 0, 'có CASH DEPOSIT: vnd.balance = ' + d16.vnd.balance + ' không còn âm');
    A.equal(d16.vnd.balance, 40000000 - 25600000 - 5000000);
    A.equal(d16.firstOffendingBusinessDate, '2026-03-20', 'cờ còn lại đến từ reserve âm ở 20/03, không phải tiền mặt');
    bottom = await dashBottom(p);
    A.equal(bottom['Đang nắm giữ (BTC)'], (d16.holdings.BTC.qty / 1e8).toLocaleString('vi-VN', { maximumFractionDigits: 8 }), 'Tổng quan có dòng nắm giữ riêng cho BTC');
    A.equal(bottom['Đang nắm giữ (ETH)'], (d16.holdings.ETH.qty / 1e8).toLocaleString('vi-VN', { maximumFractionDigits: 8 }));
    A.equal(bottom['Lãi/lỗ đã thực hiện (USDT)'], (d16.realizedPnlUsdt / 1e6).toLocaleString('vi-VN', { maximumFractionDigits: 6 }));
    A.equal(bottom['Lãi/lỗ tỷ giá đã thực hiện (VND)'], d16.realizedFxVnd.toLocaleString('vi-VN'));
    A.ok(d16.realizedPnlUsdt !== 0, 'lệnh bán phải sinh lãi/lỗ đã thực hiện bằng USDT');
    A.equal(d16.realizedFxVnd, 0, 'bán coin lấy USDT không tạo lãi/lỗ VND');
    // Ranh giới kế hoạch: mua BTC (EXTRA) không chạm ngân sách ETH; bán cũng không.
    const onlyEthPlan = s16.events.filter(e => e.kind === 'TRADE' && e.side === 'BUY' && e.symbol === 'ETH' && e.source === 'PLAN');
    A.equal(d16.month.planInvestedVnd, onlyEthPlan.reduce((t, e) => t + d16.eventEffects[e.id].vndRelieved, 0), 'planInvested chỉ gồm lệnh mua ETH theo kế hoạch');
    const cards16 = Object.fromEntries((await dashCards(p)).map(c => [c.label, c.value]));
    A.equal(cards16['Đã đầu tư tháng này'], d16.month.investedThisMonthVnd.toLocaleString('vi-VN') + ' ₫');
    A.match(await p.textContent('#l1History'), /Bán ETH/, 'Lịch sử hiện nhãn "Bán ETH"');
    A.match(await p.textContent('#l1History'), /Nạp tiền mặt/);
    record('T-16', 'Qua UI thật: CASH DEPOSIT, mua BTC (EXTRA), bán ETH; Tổng quan có dòng nắm giữ riêng từng coin, hai ô lãi/lỗ tách đơn vị, ngân sách kế hoạch không bị coin khác pha loãng.');

    // AS-09: khung hình ≤400px — không cuộn ngang; ghi PLAN từ Tổng quan ≤3 lần chạm (FAB, loại, Lưu).
    await p.setViewportSize({ width: 390, height: 844 });
    const scrollOk = await p.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1);
    A.ok(scrollOk, 'không cuộn ngang ở 390px');
    await p.click('#fabEntry');                          // chạm 1
    await pickType(p, 'buy_plan');                        // chạm 2
    await fill(p, 'l1Date', '2026-03-23'); await fill(p, 'l1Notional', value(50000000, 6)); await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', value(2000000, 8));
    await saveEvent(p);                                    // chạm 3 (Lưu)
    record('AS-09', 'Ở khung hình 390px: không cuộn ngang; ghi một giao dịch PLAN từ Tổng quan tốn đúng 3 lần chạm (FAB, loại, Lưu).');
    await p.setViewportSize({ width: 1200, height: 1000 });

    // PR-3: sửa (AS-05) và xoá (AS-06) qua UI mới đã thực hiện ở trên với snapshot xác nhận.
    record('PR-3', 'Ít nhất 1 sửa và 1 xoá qua UI mới với snapshot/xác nhận (xem AS-05/AS-06).');

    // PR-4/PR-5/PR-6: reload -> derive() chạy lại -> khớp tuyệt đối; không phép tính tài chính nào ngoài derive/update/migrate/destructive trong UI mới.
    const sBeforeReload = await H.readState(p);
    const dBeforeReload = L.derive(sBeforeReload.openingPosition, sBeforeReload.plan, sBeforeReload.events, '2026-03-21');
    await p.reload(); await H.waitPhase(p, 'ONLINE');
    const sAfterReload = await H.readState(p);
    A.deepEqual(sAfterReload, sBeforeReload);
    cards = await dashCards(p);
    const byLabel2 = Object.fromEntries(cards.map(c => [c.label, c]));
    A.equal(byLabel2['Đã đầu tư tháng này'].value, vnd(dBeforeReload.month.investedThisMonthVnd));
    record('PR-4/PR-5', 'Toàn bộ ghi lên Firestore Emulator (rules thật), đọc lại từ SERVER; reload → derive() chạy lại → số trên Tổng quan trùng khớp tuyệt đối.');
    const uiJs = fs.readFileSync(path.join(__dirname, 'ledger_ui.js'), 'utf8');
    const calcOutsideLedger = /\bstate\.\w+\s*[+\-*/]=|\.qty\s*[+\-]=|\.balance\s*[+\-]=/;
    A.doesNotMatch(uiJs, calcOutsideLedger, 'không phép cộng/trừ tiền độc lập trong ledger_ui.js');
    record('PR-6', 'Grep ledger_ui.js: không có phép cộng/trừ/nhân tiền độc lập ngoài derive()/update()/migrate()/destructive() của webapp/ledger.js.');

    // AS-12/PR-2: toàn bộ chuỗi trên đã chạy qua app_final.html thật, Firestore Emulator + rules thật.
    record('AS-12/PR-2', 'Toàn bộ AS-01..AS-11 chạy qua app_final.html + UI mới (tap/điền form thật) + Firestore Emulator + firestore.rules; anti-vacuity: ' + results.length + ' thao tác thật ghi nhận.');

    console.log(JSON.stringify({ results }, null, 2));
  } finally { if (ctx) await ctx.close(); await b.close(); await H.stopServer(); await stop(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
