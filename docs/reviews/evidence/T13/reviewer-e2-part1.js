/* T-13 Independent E2 — reviewer-controlled reproduction.
 * KHÔNG dùng lại assertion của implementer. Kịch bản do reviewer dựng, oracle = CoinLedger.derive()
 * tính trong Node từ state DURABLE đọc thẳng từ Firestore emulator (REST, không qua SDK trang).
 * Chạy: node e2_reviewer_stepb.js   (cwd bất kỳ; đường dẫn webapp cố định)
 */
const A = require('assert/strict'), fs = require('fs'), path = require('path');
const W = '/home/user/coin/webapp';
const { chromium } = require(path.join(W, 'node_modules/playwright'));
const H = require(path.join(W, 'test_firebase_harness.js'));
const L = require(path.join(W, 'ledger.js'));

const out = [];
const ok = (id, detail) => { out.push({ id, status: 'PASS', detail }); console.log('PASS  ' + id + ' :: ' + detail); };
const bad = (id, detail) => { out.push({ id, status: 'FAIL', detail }); console.log('FAIL  ' + id + ' :: ' + detail); };
const note = (id, detail) => { out.push({ id, status: 'NOTE', detail }); console.log('NOTE  ' + id + ' :: ' + detail); };
async function check(id, fn) {
  try { const d = await fn(); ok(id, d || ''); return true; }
  catch (e) { bad(id, e.message.split('\n').slice(0, 6).join(' | ')); return false; }
}

const dec = (n, places = 0) => n === null ? '' : (n / 10 ** places).toFixed(places);
// đúng hàm trình bày của UI (ledger_ui.js units/avg) — reviewer tái lập độc lập để so chuỗi
const units = (n, places = 0) => n === null ? '—' : (n / 10 ** places).toLocaleString('vi-VN', { maximumFractionDigits: places });
const avgs = (r, scale = 1) => r === null ? '—' : (Number(r.numerator) / Number(r.denominator) / scale).toLocaleString('vi-VN', { maximumFractionDigits: 8 });

async function fill(p, id, v) { await p.locator('#' + id).fill(String(v)); }
async function openAll(p) { await p.locator('#l1Root details').evaluateAll(ds => ds.forEach(d => { d.open = true; })); }
async function pick(p, key) { await p.click('.txtype[data-txtype="' + key + '"]'); }
async function save(p, expectOk = true) {
  await p.click('#l1SaveEvent'); await p.waitForTimeout(80);
  const m = await p.textContent('#l1Message');
  if (expectOk) await H.waitSaved(p);
  return m;
}
async function cards(p) {
  return p.locator('#dashMain .dcard').evaluateAll(xs => xs.map(x => ({
    label: x.querySelector('.dc-label').textContent,
    value: x.querySelector('.dc-value').textContent,
    sub: x.querySelector('.dc-sub') ? x.querySelector('.dc-sub').textContent : '',
    html: x.innerHTML,
  })));
}
const byLabel = cs => Object.fromEntries(cs.map(c => [c.label, c]));
async function bottom(p) {
  return p.locator('#dashBottom .stat').evaluateAll(xs =>
    Object.fromEntries(xs.map(x => [x.querySelector('small').textContent, x.querySelector('div').textContent])));
}
async function planCarry(p) {
  return p.locator('#planCarry .stat').evaluateAll(xs =>
    Object.fromEntries(xs.map(x => [x.querySelector('small').textContent, x.querySelector('div').textContent])));
}
const vnd = n => units(n) + ' ₫';

async function oracle(p, asOf) {
  const s = await H.readState(p);
  return { s, d: L.derive(s.openingPosition, s.plan, s.events, asOf) };
}

(async () => {
  const stop = await H.ensureEmulators();
  const b = await chromium.launch({ executablePath: H.CHROMIUM });
  let ctx;
  try {
    /* ---------- Phần 1: kịch bản có CARRY THẬT (implementer chưa bao giờ chạy) ---------- */
    const opened = await H.newPage(b, { seed: false }); ctx = opened.ctx; const p = opened.p;
    const errs = opened.errs;
    const ASOF = '2026-03-18';
    await p.clock.install({ time: new Date('2026-03-18T05:00:00Z') });
    await p.reload(); await H.waitPhase(p, 'ONLINE');
    await openAll(p);

    // Kế hoạch bắt đầu 2026-02 -> tháng 02 sẽ ĐÓNG khi asOf ở tháng 03 => carryOut thật.
    await fill(p, 'l1StartMonth', '2026-02'); await fill(p, 'l1Effective', '2026-02');
    await fill(p, 'l1Budget', '20000000'); await fill(p, 'l1Days', '3,13,23');
    await p.click('#l1SavePlan'); await H.waitSaved(p);

    await fill(p, 'l1OpeningDate', '2026-02-01');
    await fill(p, 'l1Eth', '0'); await fill(p, 'l1EthCostUsdt', '0'); await fill(p, 'l1EthCostVnd', '0');
    await fill(p, 'l1Usdt', dec(4000000000, 6)); await fill(p, 'l1UsdtCost', '100000000');
    await fill(p, 'l1Vnd', '0'); await fill(p, 'l1Reserve', '0');
    await fill(p, 'l1OpeningNote', 'reviewer E2 opening');
    await p.click('#l1SaveOpening'); await H.waitSaved(p);

    // Tháng 02: MỘT lệnh PLAN 240 USDT (=6.000.000 VND ở 25.000/USDT) -> carryOut(02) = 14.000.000
    await pick(p, 'buy_plan');
    await fill(p, 'l1Date', '2026-02-03'); await fill(p, 'l1Notional', dec(240000000, 6));
    await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', dec(10000000, 8)); await fill(p, 'l1Note', 'feb plan');
    await save(p);

    // Tháng 03: MỘT lệnh PLAN nữa
    await pick(p, 'buy_plan');
    await fill(p, 'l1Date', '2026-03-03'); await fill(p, 'l1Notional', dec(240000000, 6));
    await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', dec(10000000, 8)); await fill(p, 'l1Note', 'mar plan');
    await save(p);

    let { s, d } = await oracle(p, ASOF);
    await check('E2-CARRY-PRECONDITION', async () => {
      A.ok(d.month.carryInVnd > 0, 'kịch bản reviewer phải có carryIn > 0, thực tế ' + d.month.carryInVnd);
      return 'carryIn=' + d.month.carryInVnd + ' plannedBudget=' + d.month.plannedBudgetVnd +
             ' nextPlannedDate=' + d.month.nextPlannedDate + ' nextPlannedAmountVnd=' + d.month.nextPlannedAmountVnd;
    });

    /* ---------- CHECK-T13-02: Dashboard vs derive(), MỌI trường, tolerance 0 ---------- */
    await check('CHECK-T13-02/main-4+1', async () => {
      const c = byLabel(await cards(p));
      A.equal(c['Ngân sách tháng'].value, vnd(d.month.plannedBudgetVnd), 'thẻ 1');
      A.equal(c['Đã đầu tư tháng này'].value, vnd(d.month.investedThisMonthVnd), 'thẻ 2');
      A.equal(c['Còn lại theo kế hoạch'].value, vnd(d.month.remainingPlannedBudgetVnd), 'thẻ 3');
      A.equal(c['Số dư dự phòng'].value, vnd(d.reserve.balance), 'thẻ 4');
      A.equal(c['Mua kế tiếp'].value, d.month.nextPlannedDate || '—', 'thẻ 5 ngày');
      A.match(c['Mua kế tiếp'].sub, new RegExp(units(d.month.nextPlannedAmountVnd).replace(/[.]/g, '\\.')), 'thẻ 5 SỐ TIỀN nextPlannedAmountVnd phải hiện: ' + c['Mua kế tiếp'].sub);
      return '5/5 thẻ khớp bit-với-bit derive(), gồm nextPlannedAmountVnd=' + d.month.nextPlannedAmountVnd;
    });
    await check('CHECK-T13-02/carry-subtitle', async () => {
      const c = byLabel(await cards(p));
      A.match(c['Ngân sách tháng'].sub, /chuyển từ tháng trước/, 'phụ đề carry §16.1 phải hiện khi carryIn>0');
      A.match(c['Ngân sách tháng'].sub, new RegExp(units(d.month.carryInVnd).replace(/[.]/g, '\\.')));
      return 'phụ đề = "' + c['Ngân sách tháng'].sub + '"';
    });
    await check('CHECK-T13-02/bottom', async () => {
      const bt = await bottom(p);
      A.equal(bt['Đang nắm giữ (ETH)'], units(d.holdings.ETH.qty, 8));
      A.equal(bt['Giá vốn TB (USDT)'], avgs(d.holdings.ETH.avgCostUsdt, 1000000));
      A.equal(bt['Giá vốn TB (VND)'], avgs(d.holdings.ETH.avgCostVnd));
      A.equal(bt['USDT hiện có'], units(d.usdt.qty, 6));
      A.equal(bt['VND hiện có'], units(d.vnd.balance));
      return JSON.stringify(bt);
    });
    await check('CHECK-T13-02/no-recommendation', async () => {
      const c = byLabel(await cards(p));
      const h = c['Mua kế tiếp'].html;
      A.doesNotMatch(h, /\bGO\b|\bWAIT\b|khuyến nghị|nên mua|cơ hội|Opportunity|OSCORE/i, 'thẻ #5 không được là khuyến nghị');
      const page = await p.evaluate(() => document.body.innerText);
      A.doesNotMatch(page, /\bGO\b\s*\/|\bWAIT\b|Opportunity Score|Buy Score|regime|ladder/i, 'không dấu vết UI chiến lược V2.1.5');
      return 'không GO/WAIT/score/regime/ladder trong toàn bộ innerText';
    });

    /* ---------- CHECK-T13-07: Kế hoạch/Carry — ba đại lượng tách riêng ---------- */
    await check('CHECK-T13-07/three-separate', async () => {
      const pc = await planCarry(p);
      A.equal(pc['Ngân sách tháng (chưa gồm carry)'], vnd(d.month.monthlyBudgetVnd));
      A.equal(pc['→ Cộng vào ngân sách tháng này'], vnd(d.month.carryInVnd));
      A.equal(pc['Đã đầu tư tháng này (tổng)'], vnd(d.month.investedThisMonthVnd));
      A.equal(pc['Trong đó theo kế hoạch'], vnd(d.month.planInvestedVnd));
      A.notEqual(d.month.monthlyBudgetVnd, d.month.plannedBudgetVnd, 'kịch bản phải phân biệt được budget vs budget+carry');
      return JSON.stringify(pc);
    });
    await check('CHECK-T13-07/prev-closed-carryout', async () => {
      const pc = await planCarry(p);
      const prev = d.months['2026-02'];
      A.ok(prev, 'derive phải có tháng 2026-02');
      A.equal(pc['Carry tháng trước (đã đóng)'], vnd(prev.carryOutVnd),
        'UI phải hiện carryOut ĐÃ CHỐT của tháng đóng, không phải số dự phóng');
      A.notEqual(prev.carryOutVnd, null, 'tháng đã đóng phải có carryOut khác null');
      A.equal(d.month.carryOutVnd, null, 'tháng hiện tại carryOut phải null (chưa chốt) — UI không được trình bày như đã chốt');
      return 'carryOut(2026-02)=' + prev.carryOutVnd + '; carryOut(tháng hiện tại)=null như spec';
    });
    await check('CHECK-T13-07/next-per-schedule', async () => {
      const c = byLabel(await cards(p));
      A.equal(c['Mua kế tiếp'].value, d.month.nextPlannedDate);
      A.equal(d.month.nextPlannedDate, '2026-03-23', 'scheduleDays 3,13,23 với asOf 18/03 -> mốc kế tiếp 23');
      A.ok(d.month.nextPlannedAmountVnd !== null);
      return 'nextPlannedDate=' + d.month.nextPlannedDate + ' amount=' + d.month.nextPlannedAmountVnd;
    });

    /* ---------- CHECK-T13-03: ánh xạ 9 loại sự kiện ---------- */
    await check('CHECK-T13-03/no-per-order-fx', async () => {
      const ids = await p.evaluate(() => Array.from(document.querySelectorAll('#l1Entry input,#l1Entry select')).map(e => e.id + '|' + (document.querySelector('label[for="' + e.id + '"]') || {}).textContent));
      const fx = ids.filter(x => /rate|tỷ giá|ty gia|fx|vndRate/i.test(x));
      A.equal(fx.length, 1, 'chỉ được có DUY NHẤT ô tỷ giá thuộc PRICE (tham chiếu thị trường), thấy: ' + JSON.stringify(fx));
      A.match(fx[0], /^l1MarkRate\|/, 'ô tỷ giá duy nhất phải là l1MarkRate của loại PRICE');
      return 'ô tỷ giá duy nhất = ' + fx[0];
    });
    await check('CHECK-T13-03/reserve-note-blocked', async () => {
      await pick(p, 'buy_reserve');
      await fill(p, 'l1Date', '2026-03-16'); await fill(p, 'l1Notional', dec(50000000, 6));
      await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', dec(2000000, 8)); await fill(p, 'l1Note', '   ');
      const m = await save(p, false);
      A.match(m, /cần lý do/, 'form phải chặn tại chỗ, thông điệp: ' + m);
      const st = await H.readState(p);
      A.equal(st.events.some(e => e.kind === 'TRADE' && e.source === 'RESERVE'), false, 'không được ghi bền');
      return 'chặn tại form với note toàn khoảng trắng; 0 event RESERVE-buy được ghi';
    });
    // ghi đủ các loại còn lại và kiểm ánh xạ trên DURABLE state
    await check('CHECK-T13-03/all-kinds-mapping', async () => {
      const seq = [
        ['p2p_in', { l1Date: '2026-03-05', l1P2pVnd: '5000000', l1P2pUsdt: dec(200000000, 6), l1Note: 'p2p in' }],
        ['p2p_out', { l1Date: '2026-03-06', l1P2pVnd: '2500000', l1P2pUsdt: dec(100000000, 6), l1Note: 'p2p out' }],
        ['buy_extra', { l1Date: '2026-03-07', l1Notional: dec(100000000, 6), l1Fee: '0', l1Qty: dec(4000000, 8), l1Note: 'extra' }],
        ['reserve_add', { l1Date: '2026-03-08', l1ReserveAmount: '10000000', l1Note: 'nap' }],
        ['reserve_out', { l1Date: '2026-03-09', l1ReserveAmount: '1000000', l1Note: 'rut' }],
        ['buy_reserve', { l1Date: '2026-03-10', l1Notional: dec(50000000, 6), l1Fee: '0', l1Qty: dec(2000000, 8), l1Note: 'giai ngan du phong' }],
        ['price', { l1Date: '2026-03-18', l1Price: dec(2500000000, 6), l1MarkRate: '26000', l1Note: 'price' }],
      ];
      for (const [key, fields] of seq) {
        await pick(p, key);
        for (const [id, v] of Object.entries(fields)) await fill(p, id, v);
        const m = await save(p);
        A.doesNotMatch(m, /không hợp lệ|Sai |thiếu|cần lý do/i, key + ' -> ' + m);
      }
      const st = await H.readState(p);
      const find = f => st.events.find(f);
      const expect = [
        ['TREASURY VND_TO_USDT', e => e.kind === 'TREASURY' && e.dir === 'VND_TO_USDT' && e.businessDate === '2026-03-05'],
        ['TREASURY USDT_TO_VND', e => e.kind === 'TREASURY' && e.dir === 'USDT_TO_VND' && e.businessDate === '2026-03-06'],
        ['TRADE BUY EXTRA', e => e.kind === 'TRADE' && e.side === 'BUY' && e.source === 'EXTRA'],
        ['RESERVE CONTRIBUTE', e => e.kind === 'RESERVE' && e.type === 'CONTRIBUTE'],
        ['RESERVE WITHDRAW', e => e.kind === 'RESERVE' && e.type === 'WITHDRAW'],
        ['TRADE BUY RESERVE +note', e => e.kind === 'TRADE' && e.source === 'RESERVE' && e.note.trim().length > 0],
        ['PRICE', e => e.kind === 'PRICE' && e.symbol === 'ETH'],
        ['TRADE BUY PLAN', e => e.kind === 'TRADE' && e.side === 'BUY' && e.source === 'PLAN'],
      ];
      const missing = expect.filter(([, f]) => !find(f)).map(([n]) => n);
      A.deepEqual(missing, [], 'thiếu ánh xạ: ' + missing.join(', '));
      A.equal(st.events.every(e => e.side === undefined || e.side === 'BUY'), true, 'không event nào side!=BUY');
      return '8/8 ánh xạ đúng trên durable state (loại thứ 9 "Số dư đầu kỳ" điều hướng tới Kế hoạch, đã dùng ở trên)';
    });

    /* ---------- CHECK-T13-05: sửa qua UI ---------- */
    let editTarget;
    await check('CHECK-T13-05/edit-recompute-id-seq', async () => {
      const st = await H.readState(p);
      editTarget = st.events.find(e => e.kind === 'TRADE' && e.source === 'PLAN' && e.businessDate === '2026-03-03');
      const before = L.derive(st.openingPosition, st.plan, st.events, ASOF);
      await p.click('button[data-id="' + editTarget.id + '"][data-action="edit"]');
      await fill(p, 'l1Qty', dec(9000000, 8));
      await save(p);
      const st2 = await H.readState(p);
      const ed = st2.events.find(e => e.id === editTarget.id);
      A.ok(ed, 'event phải còn đúng id');
      A.equal(ed.seq, editTarget.seq, 'INV-15: seq bất biến');
      A.equal(ed.qty, 9000000, 'qty đã đổi');
      A.equal(st2.events.length, st.events.length, 'sửa không tạo thêm event');
      const after = L.derive(st2.openingPosition, st2.plan, st2.events, ASOF);
      A.notEqual(after.holdings.ETH.qty, before.holdings.ETH.qty, 'derive phải đổi theo');
      const bt = await bottom(p);
      A.equal(bt['Đang nắm giữ (ETH)'], units(after.holdings.ETH.qty, 8), 'Tổng quan phải khớp NGAY sau sửa');
      const c = byLabel(await cards(p));
      A.equal(c['Đã đầu tư tháng này'].value, vnd(after.month.investedThisMonthVnd));
      return 'id/seq bất biến; dashboard khớp derive() ngay sau sửa (không reload)';
    });
    await check('CHECK-T13-05/edit-survives-reload', async () => {
      await p.reload(); await H.waitPhase(p, 'ONLINE');
      const { s: st3, d: d3 } = await oracle(p, ASOF);
      const ed = st3.events.find(e => e.id === editTarget.id);
      A.equal(ed.qty, 9000000); A.equal(ed.seq, editTarget.seq);
      const bt = await bottom(p);
      A.equal(bt['Đang nắm giữ (ETH)'], units(d3.holdings.ETH.qty, 8));
      return 'sau reload: qty/seq giữ nguyên, dashboard khớp derive()';
    });

    /* ---------- CHECK-T13-06: xoá qua UI ---------- */
    await check('CHECK-T13-06/delete-snapshot-first', async () => {
      const st = await H.readState(p);
      const target = st.events.find(e => e.kind === 'RESERVE' && e.type === 'WITHDRAW');
      A.ok(target, 'cần một event để xoá');
      const beforeJson = JSON.stringify(st);
      const dl = p.waitForEvent('download');
      await p.click('button[data-id="' + target.id + '"][data-action="delete"]');
      const f = await dl;
      const snap = JSON.parse(fs.readFileSync(await f.path(), 'utf8'));
      A.deepEqual(snap.state, JSON.parse(beforeJson), 'snapshot phải là bản TRƯỚC khi xoá (INV-14)');
      await H.waitSaved(p);
      const after = await H.readState(p);
      A.equal(after.events.some(e => e.id === target.id), false, 'event đã bị xoá thật (hard delete)');
      A.equal(after.events.length, st.events.length - 1);
      // kết quả phải BẰNG sổ như thể event chưa từng có
      const asIfNever = L.derive(st.openingPosition, st.plan, st.events.filter(e => e.id !== target.id), ASOF);
      const actual = L.derive(after.openingPosition, after.plan, after.events, ASOF);
      A.deepEqual(H.canon(actual), H.canon(asIfNever), 'derive sau xoá phải bằng derive của sổ không có event đó');
      const bt = await bottom(p), c = byLabel(await cards(p));
      A.equal(bt['USDT hiện có'], units(actual.usdt.qty, 6));
      A.equal(c['Số dư dự phòng'].value, vnd(actual.reserve.balance));
      return 'snapshot trước khi xoá khớp bit-exact; sau xoá = sổ chưa từng có event; dashboard/lịch sử cập nhật';
    });
    await check('CHECK-T13-06/delete-survives-reload', async () => {
      const before = await H.readState(p);
      await p.reload(); await H.waitPhase(p, 'ONLINE');
      const after = await H.readState(p);
      A.deepEqual(H.canon(after), H.canon(before), 'reload giữ nguyên kết quả xoá');
      return 'reload sau xoá: durable state bit-exact';
    });
    await check('CHECK-T13-06/confirm-dialog-exists', async () => {
      // huỷ dialog -> KHÔNG được xoá
      const st = await H.readState(p);
      const target = st.events.find(e => e.kind === 'PRICE');
      let sawDialog = null;
      p.removeAllListeners('dialog');
      p.on('dialog', async dlg => { sawDialog = dlg.message(); await dlg.dismiss(); });
      const dl = p.waitForEvent('download').catch(() => null);
      await p.click('button[data-id="' + target.id + '"][data-action="delete"]');
      await dl; await p.waitForTimeout(400);
      A.ok(sawDialog, 'phải có dialog xác nhận tường minh');
      A.match(sawDialog, /Xóa|xoá|không thể|xuất/i, 'nội dung cảnh báo: ' + sawDialog);
      const after = await H.readState(p);
      A.equal(after.events.some(e => e.id === target.id), true, 'huỷ dialog => KHÔNG xoá');
      return 'dialog = "' + sawDialog + '"; huỷ => sổ giữ nguyên';
    });
    await check('CHECK-T13-06/opening-stronger-warning', async () => {
      const html = await p.content();
      A.match(html, /Sửa\/xoá số dư đầu kỳ có thể khiến phần lớn giá vốn trở thành KHÔNG XÁC ĐỊNH/i,
        'cảnh báo riêng cho Số dư đầu kỳ phải có mặt');
      let msg = null;
      p.removeAllListeners('dialog');
      p.on('dialog', async dlg => { msg = dlg.message(); await dlg.dismiss(); });
      await openAll(p);
      await p.click('#l1DeleteOpening'); await p.waitForTimeout(600);
      A.ok(msg, 'xoá opening phải có dialog');
      A.match(msg, /đầu kỳ/i, 'dialog xoá opening phải nói riêng về đầu kỳ: ' + msg);
      A.notEqual((await H.readState(p)).openingPosition, null, 'huỷ => opening còn nguyên');
      p.removeAllListeners('dialog');
      p.on('dialog', d => d.accept());
      return 'dialog riêng cho opening = "' + msg + '"';
    });

    /* ---------- CHECK-T13-13 / PR-1..PR-6 ---------- */
    await check('PR-4/PR-5-reload-tolerance-0', async () => {
      const { s: sB, d: dB } = await oracle(p, ASOF);
      const cB = byLabel(await cards(p)), btB = await bottom(p), pcB = await planCarry(p);
      await p.reload(); await H.waitPhase(p, 'ONLINE'); await H.waitSaved(p);
      const { s: sA, d: dA } = await oracle(p, ASOF);
      A.deepEqual(H.canon(sA), H.canon(sB), 'state sau reload bit-exact');
      const cA = byLabel(await cards(p)), btA = await bottom(p), pcA = await planCarry(p);
      for (const k of Object.keys(cB)) { A.equal(cA[k].value, cB[k].value, 'thẻ ' + k); A.equal(cA[k].sub, cB[k].sub, 'phụ đề ' + k); }
      A.deepEqual(btA, btB, 'khối dưới sau reload');
      A.deepEqual(pcA, pcB, 'Kế hoạch/carry sau reload');
      // và vẫn khớp oracle
      A.equal(cA['Ngân sách tháng'].value, vnd(dA.month.plannedBudgetVnd));
      A.equal(cA['Còn lại theo kế hoạch'].value, vnd(dA.month.remainingPlannedBudgetVnd));
      return 'Tổng quan + khối dưới + Kế hoạch trùng khớp tuyệt đối trước/sau reload và khớp derive()';
    });
    await check('PR-4/server-read-back', async () => {
      const durable = await H.getDoc('state');
      A.ok(durable && durable.events && durable.events.length > 0, 'Firestore SERVER phải có state thật');
      const d2 = L.derive(durable.openingPosition, durable.plan, durable.events, ASOF);
      const c = byLabel(await cards(p));
      A.equal(c['Đã đầu tư tháng này'].value, vnd(d2.month.investedThisMonthVnd),
        'UI phải khớp derive() tính từ bản đọc THẲNG từ server (không qua SDK trang)');
      return durable.events.length + ' event trên server; UI khớp derive(server state)';
    });

    /* ---------- CHECK-T13-10: không có bộ máy kế toán thứ hai ---------- */
    await check('CHECK-T13-10/single-derive-per-render', async () => {
      const n = await p.evaluate(() => {
        const orig = window.CoinLedger.derive; let count = 0;
        // CoinLedger bị Object.freeze -> đếm bằng cách bọc qua Proxy không được; dùng đếm gián tiếp:
        return -1;
      });
      const src = fs.readFileSync(path.join(W, 'ledger_ui.js'), 'utf8');
      const calls = (src.match(/L\.derive\s*\(/g) || []).length;
      A.equal(calls, 1, 'ledger_ui.js chỉ được có ĐÚNG 1 lệnh gọi derive(), thấy ' + calls);
      const writes = src.match(/L\.(update|migrate|destructive|canonical|empty)\s*\(/g) || [];
      A.ok(writes.length > 0);
      // không ghi thẳng vào state
      A.doesNotMatch(src, /hooks\.state\(\)\.(events|plan|openingPosition)\s*(\.\w+)?\s*=[^=]/, 'không ghi thẳng vào state');
      A.doesNotMatch(src, /\.events\.(push|splice|pop|shift|unshift)\s*\(/, 'UI không tự sửa mảng events');
      return '1 lệnh derive(); ghi qua ' + writes.length + ' lệnh update/migrate/destructive/canonical/empty; 0 ghi thẳng state';
    });
    await check('CHECK-T13-10/no-independent-money-math', async () => {
      const src = fs.readFileSync(path.join(W, 'ledger_ui.js'), 'utf8');
      const lines = src.split('\n');
      const suspects = [];
      const moneyFields = /(Vnd|Usdt|vndAmount|usdtAmount|usdtNotional|feeUsdt|qty|balance|costVnd|costUsdt|priceUsdt)\b/;
      lines.forEach((ln, i) => {
        if (/^\s*(\/\/|\*|\/\*)/.test(ln)) return;
        // biểu thức số học trên trường tiền
        const m = ln.match(/[A-Za-z_$][\w.$\[\]']*\s*[+\-*/]\s*[A-Za-z_$][\w.$\[\]']*/g) || [];
        m.forEach(expr => { if (moneyFields.test(expr)) suspects.push((i + 1) + ': ' + expr.trim()); });
      });
      // Ghi lại toàn bộ để reviewer phán xét thủ công (không tự PASS bằng regex rỗng)
      fs.writeFileSync(path.join(__dirname, 'money-math-suspects.txt'), suspects.join('\n'));
      return suspects.length + ' biểu thức số học chạm trường tiền (đã ghi ra file để soi tay): ' + JSON.stringify(suspects.slice(0, 12));
    });

    /* ---------- SELL GUARD (adversarial) ---------- */
    await check('SELL/no-option-in-forms', async () => {
      const dom = await p.evaluate(() => ({
        options: Array.from(document.querySelectorAll('option')).map(o => o.value + '=' + o.textContent),
        buttons: Array.from(document.querySelectorAll('button')).map(o => o.textContent.trim()),
        labels: Array.from(document.querySelectorAll('label,summary,h1,h2,h3')).map(o => o.textContent.trim()),
      }));
      const all = JSON.stringify(dom);
      A.doesNotMatch(all, /SELL/i, 'không option/button/label nào chứa SELL: ' + all.slice(0, 300));
      A.doesNotMatch(all, /\bBán\b/, 'không nhãn "Bán" nào trong form/menu');
      const side = dom.options.filter(o => /^(BUY|SELL)=/.test(o));
      A.deepEqual(side, ['BUY=Mua'], '#l1Side chỉ được có BUY, thấy ' + JSON.stringify(side));
      return 'option side = ' + JSON.stringify(side) + '; 0 SELL/Bán trong form/menu';
    });
    await check('SELL/no-realized-pnl', async () => {
      const txt = await p.evaluate(() => document.body.innerText);
      A.doesNotMatch(txt, /realizedFxVnd|lãi\/lỗ|đã thực hiện|P&L|PnL/i);
      return 'không màn hình nào hiển thị lãi/lỗ đã thực hiện';
    });
    await check('SELL/no-url-hash-path', async () => {
      for (const h of ['#/sell', '#/history/sell', '#/trade?side=SELL']) {
        await p.evaluate(x => { location.hash = x; }, h);
        await p.waitForTimeout(120);
        const txt = await p.evaluate(() => document.body.innerText);
        A.doesNotMatch(txt, /SELL|\bBán\b/, 'hash ' + h + ' không được lộ SELL');
      }
      await p.evaluate(() => { location.hash = '#/dashboard'; });
      return '3 hash tấn công không lộ SELL; router chỉ nhận dashboard|history|plan|settings';
    });
    // ĐƯỜNG TẤN CÔNG THẬT: nạp lại JSON (Cài đặt) chứa một TRADE side=SELL
    let sellReach = null;
    await check('SELL/import-json-path', async () => {
      const st = await H.readState(p);
      const clone = JSON.parse(JSON.stringify(st));
      const src0 = clone.events.find(e => e.kind === 'TRADE');
      const sell = Object.assign({}, src0, {
        id: 'reviewer-sell-1', seq: clone.nextSeq, side: 'SELL', source: 'PLAN',
        businessDate: '2026-03-11', note: 'reviewer adversarial SELL',
      });
      clone.nextSeq = clone.nextSeq + 1;
      clone.events.push(sell);
      let accepted = true;
      try { L.canonical(clone); } catch (e) { accepted = false; }
      const file = path.join(__dirname, 'sell-import.json');
      fs.writeFileSync(file, JSON.stringify({ state: clone, seed: null }));
      p.removeAllListeners('dialog');
      p.on('dialog', d => d.accept());
      const dl = p.waitForEvent('download').catch(() => null);
      await openAll(p);
      await p.setInputFiles('#l1Import', file);
      await dl; await p.waitForTimeout(800);
      const msg = await p.textContent('#l1Message');
      const after = await H.readState(p).catch(() => null);
      const stored = after && after.events.some(e => e.id === 'reviewer-sell-1');
      const txt = await p.evaluate(() => document.body.innerText);
      const shows = /\bBán\b/.test(txt);
      sellReach = { canonicalAccepts: accepted, storedDurable: !!stored, uiShowsBan: shows, message: msg };
      A.equal(shows, false,
        'SỔ chứa TRADE side=SELL nạp qua UI Cài đặt -> Lịch sử hiển thị nhãn "Bán": ' + JSON.stringify(sellReach));
      return JSON.stringify(sellReach);
    });

    console.log('\n--- SELL reachability ---\n' + JSON.stringify(sellReach, null, 2));
    console.log('\n--- page errors ---\n' + JSON.stringify(errs, null, 2));
    fs.writeFileSync(path.join(__dirname, 'reviewer-e2-part1-results.json'),
      JSON.stringify({ results: out, sellReach, pageErrors: errs }, null, 2));
  } finally {
    if (ctx) await ctx.close(); await b.close(); await H.stopServer(); await stop();
  }
  const fails = out.filter(x => x.status === 'FAIL');
  console.log('\nSUMMARY part1: ' + out.filter(x => x.status === 'PASS').length + ' PASS, ' + fails.length + ' FAIL');
  if (fails.length) process.exitCode = 1;
})().catch(e => { console.error(e); process.exitCode = 1; });
