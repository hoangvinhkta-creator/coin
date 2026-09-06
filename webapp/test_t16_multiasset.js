/* T-16 — sổ đa tài sản (BTC/ETH/ADA), SELL đúng, CASH DEPOSIT/WITHDRAW, migration v2 -> v3.
 * Phong cách theo test_l1_fixes.js của T-15: dữ liệu tái lập viết tay, oracle không sinh từ derive().
 */
'use strict';
const { test } = require('node:test');
const A = require('node:assert/strict');
const L = require(process.env.T12_LEDGER_MODULE || './ledger');

const instant = '2026-09-06T00:00:00.000Z';
const clone = x => JSON.parse(JSON.stringify(x));
const version = (over = {}) => Object.assign({ id: 'plan-1', effectiveFrom: '2025-10', asset: 'ETH', monthlyBudgetVnd: 20000000, scheduleDays: [8, 18, 28], carryPolicy: 'CAPPED_CARRY', carryCapMonths: 1 }, over);
const plan = (versions = [version()], startMonth = '2025-10') => ({ startMonth, versions });
const opening = (over = {}) => Object.assign({ asOf: '2025-10-08', assets: [], usdt: { qty: 0, costVnd: 0 }, vnd: { qty: 0 }, reserveVnd: 0, note: 'T-16' }, over);
const event = (seq, businessDate, fields) => Object.assign({ id: 'event-' + seq, seq, businessDate, createdAt: instant, updatedAt: instant, note: '' }, fields);
const cash = (seq, date, type, vndAmount) => event(seq, date, { kind: 'CASH', type, vndAmount });
const p2pIn = (seq, date, vndAmount, usdtAmount) => event(seq, date, { kind: 'TREASURY', dir: 'VND_TO_USDT', vndAmount, usdtAmount });
const p2pOut = (seq, date, vndAmount, usdtAmount) => event(seq, date, { kind: 'TREASURY', dir: 'USDT_TO_VND', vndAmount, usdtAmount });
const trade = (seq, date, side, symbol, usdtNotional, feeUsdt, qty, source = 'EXTRA') => event(seq, date, { kind: 'TRADE', side, symbol, source, usdtNotional, feeUsdt, qty });
const state = (o, p, events) => ({ schema: L.SCHEMA, rev: 0, nextSeq: Math.max(0, ...events.map(e => e.seq)) + 1, plan: clone(p), openingPosition: o === null ? null : clone(o), events: clone(events) });
const derive = (s, asOf) => L.derive(s.openingPosition, s.plan, s.events, asOf);

/* ============ 1. Migration v2 -> v3 ============ */
const v2State = () => ({
  schema: L.SCHEMA_V2, rev: 4, nextSeq: 4,
  plan: { startMonth: '2025-10', versions: [{ id: 'plan-1', effectiveFrom: '2025-10', asset: 'ETH', monthlyBudgetVnd: 20000000, scheduleDays: [8, 18, 28], carryPolicy: 'CAPPED_CARRY', carryCapMonths: 1 }] },
  openingPosition: { asOf: '2025-10-08', assets: [{ symbol: 'ETH', qty: 50000000, costUsdt: 1200000000, costVnd: 30000000 }], usdt: { qty: 200000000, costVnd: 5000000 }, vnd: { qty: 100000000 }, reserveVnd: 0, note: 'v2' },
  events: [p2pIn(1, '2025-10-09', 25000000, 1000000000), trade(2, '2025-10-10', 'BUY', 'ETH', 600000000, 600000, 25000000, 'PLAN'), event(3, '2025-10-11', { kind: 'PRICE', symbol: 'ETH', priceUsdt: 2400000000, usdVndRate: null })]
});
test('T16-1 migrate v2 -> v3: oracle độc lập khớp tuyệt đối, nội dung sổ không đổi ngoài nhãn schema', () => {
  const src = v2State();
  A.throws(() => L.canonical(src), /Schema không hỗ trợ/, 'sổ v2 KHÔNG tự động được nhận là v3');
  const r = L.migrateV3(src, { today: '2025-10-31' });
  A.equal(r.ok, true, JSON.stringify(r.errors));
  A.equal(r.state.schema, L.SCHEMA);
  // Oracle: replay v2 độc lập (deltas.before) phải trùng derive() v3 (deltas.after), tolerance 0.
  for (const [k, v] of Object.entries(r.deltas)) A.deepEqual(v.after, v.before, 'oracle ' + k);
  A.equal(r.deltas.ethQty.after, 75000000);
  A.equal(r.deltas.ethCostVnd.after, 45015000);   // 30.000.000 + 600,6/1.200 × 30.000.000
  // Ngoài `schema`, sổ không đổi một byte.
  const a = clone(src), b = clone(r.state); a.schema = b.schema = null;
  A.deepEqual(b, a);
  // derive() sau migrate cho đúng holdings ETH cũ.
  const d = derive(r.state, '2025-10-31');
  A.equal(d.holdings.ETH.qty, 75000000); A.equal(d.holdings.ETH.costUsdt, 1800600000); A.equal(d.holdings.ETH.costVnd, 45015000);
  A.deepEqual(Object.keys(d.holdings), ['ETH']);
});
test('T16-2 migrateV3 từ chối đầu vào không phải v2 và sổ v2 dị dạng', () => {
  A.equal(L.migrateV3(state(opening(), plan(), []), { today: '2025-10-31' }).ok, false);        // đã là v3
  A.equal(L.migrateV3(null, { today: '2025-10-31' }).ok, false);
  const noDate = L.migrateV3(v2State(), {}); A.equal(noDate.ok, false); A.match(noDate.errors[0], /ngày hôm nay/);
  const doctored = v2State(); doctored.openingPosition.assets.push({ symbol: 'BTC', qty: 1, costUsdt: 1, costVnd: 1 });
  const r = L.migrateV3(doctored, { today: '2025-10-31' });
  A.equal(r.ok, false); A.match(r.errors.join('|'), /v2 chỉ có tối đa một tài sản ETH/);
});

/* ============ 2. Whitelist tài sản ============ */
test('T16-3 openingCheck nhận BTC/ETH/ADA, từ chối symbol lạ và symbol trùng', () => {
  const three = opening({ assets: [
    { symbol: 'BTC', qty: 5000000, costUsdt: 300000000, costVnd: 7500000 },
    { symbol: 'ETH', qty: 20000000, costUsdt: 400000000, costVnd: 10000000 },
    { symbol: 'ADA', qty: 100000000, costUsdt: 50000000, costVnd: 1250000 },
  ] });
  A.doesNotThrow(() => L.canonical(state(three, plan(), [])));
  for (const bad of ['DOGE', 'eth', 'USDT', '']) {
    const o = opening({ assets: [{ symbol: bad, qty: 1, costUsdt: 1, costVnd: 1 }] });
    A.throws(() => L.canonical(state(o, plan(), [])), /không được hỗ trợ|không hợp lệ/, 'symbol ' + JSON.stringify(bad));
  }
  const dup = opening({ assets: [{ symbol: 'BTC', qty: 1, costUsdt: 1, costVnd: 1 }, { symbol: 'BTC', qty: 2, costUsdt: 2, costVnd: 2 }] });
  A.throws(() => L.canonical(state(dup, plan(), [])), /Trùng tài sản/);
  // Giữ nguyên luật cũ: giá vốn khi lượng bằng 0 vẫn bị từ chối.
  A.throws(() => L.canonical(state(opening({ assets: [{ symbol: 'ADA', qty: 0, costUsdt: 0, costVnd: 5 }] }), plan(), [])), /lượng bằng 0/);
});
test('T16-4 eventCheck TRADE/PRICE nhận BTC/ETH/ADA, từ chối symbol lạ', () => {
  for (const sym of L.ASSETS) {
    A.doesNotThrow(() => L.canonical(state(opening(), plan(), [
      p2pIn(1, '2025-10-08', 50000000, 2000000000),
      trade(2, '2025-10-09', 'BUY', sym, 100000000, 0, 1000000, 'EXTRA'),
      event(3, '2025-10-10', { kind: 'PRICE', symbol: sym, priceUsdt: 100000000, usdVndRate: null }),
    ])), sym);
  }
  A.throws(() => L.canonical(state(opening(), plan(), [trade(1, '2025-10-09', 'BUY', 'DOGE', 100000000, 0, 1000000)])), /không được hỗ trợ/);
  A.throws(() => L.canonical(state(opening(), plan(), [event(1, '2025-10-09', { kind: 'PRICE', symbol: 'DOGE', priceUsdt: 1, usdVndRate: null })])), /không được hỗ trợ/);
});

/* ============ 3. Kế hoạch: đơn tài sản, không hardcode ETH ============ */
test('T16-5 planCheck nhận kế hoạch BTC/ADA; từ chối hai version khác asset', () => {
  for (const sym of L.ASSETS) A.doesNotThrow(() => L.canonical(state(opening(), plan([version({ asset: sym })]), [])), sym);
  const mixed = plan([version({ asset: 'BTC' }), version({ id: 'plan-2', effectiveFrom: '2025-12', asset: 'ETH' })]);
  A.throws(() => L.canonical(state(opening(), mixed, [])), /chỉ nhắm MỘT tài sản/);
  A.throws(() => L.canonical(state(opening(), plan([version({ asset: 'DOGE' })]), [])), /Tài sản kế hoạch không được hỗ trợ/);
  // Hai version CÙNG asset thì vẫn hợp lệ (đường thay ngân sách bình thường).
  A.doesNotThrow(() => L.canonical(state(opening(), plan([version({ asset: 'ADA' }), version({ id: 'plan-2', effectiveFrom: '2025-12', asset: 'ADA', monthlyBudgetVnd: 30000000 })]), [])));
});

/* ============ 4. derive() đa tài sản ============ */
test('T16-6 hai holding tách biệt, không entry rỗng cho symbol không ai chạm tới', () => {
  const o = opening({ assets: [
    { symbol: 'BTC', qty: 5000000, costUsdt: 300000000, costVnd: 7500000 },
    { symbol: 'ETH', qty: 20000000, costUsdt: 400000000, costVnd: 10000000 },
  ], usdt: { qty: 2000000000, costVnd: 50000000 } });
  const s = state(o, plan(), [
    trade(1, '2025-10-09', 'BUY', 'BTC', 200000000, 0, 2000000, 'EXTRA'),
    trade(2, '2025-10-10', 'BUY', 'ETH', 100000000, 0, 4000000, 'PLAN'),
  ]);
  const d = derive(s, '2025-10-31');
  A.deepEqual(Object.keys(d.holdings).sort(), ['BTC', 'ETH'], 'ADA không được tạo entry rỗng');
  // BTC: 200 USDT rút từ pool 2.000 USDT / 50.000.000 ₫ -> 5.000.000 ₫
  A.equal(d.holdings.BTC.qty, 7000000); A.equal(d.holdings.BTC.costUsdt, 500000000); A.equal(d.holdings.BTC.costVnd, 12500000);
  // ETH: 100 USDT rút từ pool còn 1.800 USDT / 45.000.000 ₫ -> 2.500.000 ₫
  A.equal(d.holdings.ETH.qty, 24000000); A.equal(d.holdings.ETH.costUsdt, 500000000); A.equal(d.holdings.ETH.costVnd, 12500000);
  A.equal(d.usdt.qty, 1700000000); A.equal(d.usdt.costVnd, 42500000);
  A.ok(d.holdings.ETH.avgCostVnd && d.holdings.BTC.avgCostVnd, 'mỗi holding có ratio giá vốn riêng');
});
test('T16-7 PRICE của một symbol chỉ định giá symbol đó', () => {
  const o = opening({ assets: [
    { symbol: 'BTC', qty: 5000000, costUsdt: 300000000, costVnd: 7500000 },
    { symbol: 'ETH', qty: 20000000, costUsdt: 400000000, costVnd: 10000000 },
  ] });
  const s = state(o, plan(), [
    event(1, '2025-10-31', { kind: 'PRICE', symbol: 'BTC', priceUsdt: 60000000000, usdVndRate: 26000 }),
    event(2, '2025-10-31', { kind: 'PRICE', symbol: 'ETH', priceUsdt: 2400000000, usdVndRate: null }),
  ]);
  const d = derive(s, '2025-10-31');
  A.equal(d.valuation.BTC.usdt, 3000000000);        // 0,05 BTC × 60.000 USDT
  A.equal(d.valuation.BTC.vnd, 78000000);           // 3.000 USDT × 26.000
  A.equal(d.valuation.ETH.usdt, 480000000);         // 0,2 ETH × 2.400 USDT
  A.equal(d.valuation.ETH.vnd, null, 'không tỷ giá -> không bịa');
  A.equal(d.valuation.ADA, undefined);
  // PRICE quá hạn (cũ hơn 1 ngày) không định giá.
  A.deepEqual(Object.keys(derive(s, '2025-11-05').valuation), []);
});

/* ============ 5. Ranh giới đơn-tài-sản của kế hoạch ============ */
test('T16-8 mua coin khác KHÔNG lọt vào ngân sách của kế hoạch ETH', () => {
  const o = opening({ usdt: { qty: 2000000000, costVnd: 50000000 } });
  const s = state(o, plan(), [
    trade(1, '2025-10-08', 'BUY', 'ETH', 400000000, 0, 20000000, 'PLAN'),   // 10.000.000 ₫
    trade(2, '2025-10-09', 'BUY', 'BTC', 400000000, 0, 1000000, 'EXTRA'),   // KHÔNG vào kế hoạch ETH
  ]);
  const d = derive(s, '2025-10-31');
  A.equal(d.holdings.BTC.costVnd, 10000000, 'BTC vẫn được ghi nhận đầy đủ ở tầng nắm giữ');
  A.equal(d.month.planInvestedVnd, 10000000, 'chỉ phần ETH theo kế hoạch');
  A.equal(d.month.investedThisMonthVnd, 10000000, 'đã đầu tư của kế hoạch cũng chỉ tính coin của kế hoạch');
  A.equal(d.month.remainingPlannedBudgetVnd, 10000000);
  // BTC gắn source PLAN bị chặn NGAY Ở VALIDATION, không chỉ ở derive.
  const bad = state(o, plan(), [trade(1, '2025-10-09', 'BUY', 'BTC', 400000000, 0, 1000000, 'PLAN')]);
  A.throws(() => L.canonical(bad), /nguồn PLAN phải đúng tài sản của kế hoạch \(ETH\)/);
  A.throws(() => derive(bad, '2025-10-31'), /nguồn PLAN phải đúng tài sản của kế hoạch/);
  // Và kế hoạch BTC thì ngược lại: BTC vào ngân sách, ETH thì không.
  const btcPlan = state(o, plan([version({ asset: 'BTC' })]), [
    trade(1, '2025-10-08', 'BUY', 'BTC', 400000000, 0, 1000000, 'PLAN'),
    trade(2, '2025-10-09', 'BUY', 'ETH', 400000000, 0, 20000000, 'EXTRA'),
  ]);
  const db = derive(btcPlan, '2025-10-31');
  A.equal(db.month.planInvestedVnd, 10000000); A.equal(db.month.investedThisMonthVnd, 10000000);
});

/* ============ 6. CASH ============ */
test('T16-9 CASH DEPOSIT/WITHDRAW đổi đúng vnd.balance và không chạm gì khác', () => {
  const o = opening({ assets: [{ symbol: 'ETH', qty: 20000000, costUsdt: 400000000, costVnd: 10000000 }], usdt: { qty: 100000000, costVnd: 2500000 }, vnd: { qty: 1000000 }, reserveVnd: 500000 });
  const d = derive(state(o, plan(), [cash(1, '2025-10-08', 'DEPOSIT', 50000000), cash(2, '2025-10-09', 'WITHDRAW', 20000000)]), '2025-10-31');
  A.equal(d.vnd.balance, 31000000);                                   // 1tr + 50tr − 20tr
  A.equal(d.usdt.qty, 100000000); A.equal(d.usdt.costVnd, 2500000);
  A.equal(d.holdings.ETH.costVnd, 10000000); A.equal(d.reserve.balance, 500000);
  A.deepEqual(d.flags, []);
  A.throws(() => L.canonical(state(o, plan(), [event(1, '2025-10-08', { kind: 'CASH', type: 'ĐỔI', vndAmount: 1 })])), /Loại tiền mặt sai/);
  A.throws(() => L.canonical(state(o, plan(), [cash(1, '2025-10-08', 'DEPOSIT', 0)])), /phải dương/);
});
test('T16-10 WITHDRAW vượt số dư vẫn bật LEDGER_INCONSISTENT (bảo vệ T-15 giữ nguyên)', () => {
  const d = derive(state(opening({ vnd: { qty: 1000000 } }), plan(), [cash(1, '2025-10-08', 'WITHDRAW', 2000000)]), '2025-10-31');
  A.equal(d.vnd.balance, -1000000);
  A.ok(d.flags.includes('LEDGER_INCONSISTENT'));
  A.equal(d.firstOffendingEventId, 'event-1');
});
test('T16-11 chính vấn đề đã phát hiện: CASH DEPOSIT rồi VND_TO_USDT cùng số tiền -> vnd 0, KHÔNG cờ', () => {
  const s = state(opening({ vnd: { qty: 0 } }), plan(), [cash(1, '2025-10-08', 'DEPOSIT', 50000000), p2pIn(2, '2025-10-08', 50000000, 2000000000)]);
  const d = derive(s, '2025-10-31');
  A.equal(d.vnd.balance, 0);
  A.deepEqual(d.flags, [], 'sổ nhập từ nguồn cũ không còn bị cờ vnd âm bắn oan');
  A.equal(d.usdt.qty, 2000000000); A.equal(d.usdt.costVnd, 50000000);
  // Chứng minh cờ vẫn bắn khi THẬT SỰ thiếu nguồn tiền: bỏ CASH DEPOSIT đi.
  const noCash = state(opening({ vnd: { qty: 0 } }), plan(), [p2pIn(2, '2025-10-08', 50000000, 2000000000)]);
  A.ok(derive(noCash, '2025-10-31').flags.includes('LEDGER_INCONSISTENT'));
});

/* ============ 7. SELL ============ */
// Ca tính TAY: 100tr tiền mặt -> 50tr đổi 2.000 USDT -> 2 lệnh mua ETH -> bán 0,08 ETH.
const sellCase = () => state(opening(), plan(), [
  cash(1, '2025-10-08', 'DEPOSIT', 100000000),
  p2pIn(2, '2025-10-08', 50000000, 2000000000),
  trade(3, '2025-10-08', 'BUY', 'ETH', 400000000, 400000, 20000000, 'PLAN'),
  trade(4, '2025-10-18', 'BUY', 'ETH', 300000000, 300000, 12000000, 'PLAN'),
  trade(5, '2025-10-28', 'SELL', 'ETH', 250000000, 250000, 8000000, 'EXTRA'),
]);
test('T16-12 SELL — ca cụ thể tính tay', () => {
  const d = derive(sellCase(), '2025-10-31');
  // Giá vốn giải phóng: USDT 700.700.000/4 = 175.175.000 · VND 17.517.500/4 = 4.379.375
  A.equal(d.holdings.ETH.qty, 24000000);
  A.equal(d.holdings.ETH.costUsdt, 525525000);
  A.equal(d.holdings.ETH.costVnd, 13138125);
  A.equal(d.usdt.qty, 1549050000);                 // 1.299,3 + 249,75 USDT
  A.equal(d.usdt.costVnd, 36861875);               // 32.482.500 + 4.379.375 CHUYỂN sang
  A.equal(d.realizedPnlUsdt, 74575000);            // 249,75 − 175,175 = 74,575 USDT
  A.equal(d.realizedFxVnd, 0, 'bán coin lấy USDT KHÔNG tạo lãi/lỗ VND');
  A.equal(d.vnd.balance, 50000000);
  A.deepEqual(d.flags, []);
  // Bán không chạm kế hoạch: planInvested vẫn là tổng hai lệnh mua.
  A.equal(d.month.planInvestedVnd, 17517500);
  A.equal(d.eventEffects['event-5'].vndRelieved, 4379375);
  A.equal(d.eventEffects['event-5'].symbol, 'ETH');
  A.equal(d.eventEffects['event-5'].holdingQty, 24000000);
});
test('T16-13 SELL chỉ CHUYỂN giá vốn: tổng giá vốn VND không đổi trước/sau lệnh bán', () => {
  const withSell = sellCase(), withoutSell = clone(withSell);
  withoutSell.events = withoutSell.events.filter(e => e.side !== 'SELL');
  const totalVnd = d => Object.values(d.holdings).reduce((t, h) => t + h.costVnd, 0) + d.usdt.costVnd + d.realizedFxVnd;
  A.equal(totalVnd(derive(withoutSell, '2025-10-31')), 50000000);
  A.equal(totalVnd(derive(withSell, '2025-10-31')), 50000000);
  // Bán CẠN sạch một holding: giá vốn về đúng 0, không còn dư.
  const all = clone(withSell); all.events[4].qty = 32000000;
  const d = derive(all, '2025-10-31');
  A.equal(d.holdings.ETH.qty, 0); A.equal(d.holdings.ETH.costUsdt, 0); A.equal(d.holdings.ETH.costVnd, 0);
  A.equal(totalVnd(d), 50000000);
  // Bán quá số đang giữ: fail-closed như cũ.
  const over = clone(withSell); over.events[4].qty = 99000000;
  const bad = derive(over, '2025-10-31');
  A.ok(bad.flags.includes('LEDGER_INCONSISTENT')); A.equal(bad.firstOffendingEventId, 'event-5');
});

/* ---- property test: chuỗi ngẫu nhiên hợp lệ CASH/TREASURY/BUY/SELL trên 3 coin ---- */
test('T16-14 property: 60 chuỗi ngẫu nhiên giữ bảo toàn giá vốn VND và số dư tiền mặt', () => {
  let seed = 20251008;
  const rnd = n => (seed = (seed * 16807) % 2147483647) % n;
  for (let iter = 0; iter < 60; iter++) {
    const events = [];
    let vnd = 0, poolQty = 0, poolCost = 0, seq = 1, day = 1;
    const held = { BTC: 0, ETH: 0, ADA: 0 };
    let cashIn = 0, cashOut = 0, vndIn = 0, vndOut = 0;
    for (let n = 0; n < 12; n++) {
      const date = '2025-11-' + String(Math.min(30, day++)).padStart(2, '0');
      const pick = rnd(6);
      if (pick === 0 || vnd === 0 && poolQty === 0) {                       // CASH DEPOSIT
        const v = (rnd(90) + 10) * 1000000;
        events.push(cash(seq++, date, 'DEPOSIT', v)); vnd += v; cashIn += v;
      } else if (pick === 1 && vnd > 1000000) {                             // CASH WITHDRAW
        const v = Math.max(1, rnd(Math.floor(vnd / 1000000))) * 1000000;
        events.push(cash(seq++, date, 'WITHDRAW', v)); vnd -= v; cashOut += v;
      } else if (pick === 2 && vnd >= 1000000) {                            // VND -> USDT
        const v = Math.max(1, rnd(Math.floor(vnd / 1000000))) * 1000000, u = Math.round(v / 25) ;
        events.push(p2pIn(seq++, date, v, u)); vnd -= v; poolQty += u; poolCost += v; vndIn += v;
      } else if (pick === 3 && poolQty >= 1000000) {                        // USDT -> VND
        const u = Math.max(1000000, rnd(poolQty)), v = Math.round(u * 24);
        events.push(p2pOut(seq++, date, v, u)); vnd += v; vndOut += v;
        const r = Math.round((u * poolCost) / poolQty); poolQty -= u; poolCost -= r;
      } else if (pick === 4 && poolQty >= 10000000) {                       // BUY
        const sym = L.ASSETS[rnd(3)], u = Math.max(1000000, rnd(Math.floor(poolQty / 2))), q = u * 2;
        events.push(trade(seq++, date, 'BUY', sym, u, 0, q, 'EXTRA')); held[sym] += q;
        const r = Math.round((u * poolCost) / poolQty); poolQty -= u; poolCost -= r;
      } else {                                                              // SELL nếu có gì để bán
        const owned = L.ASSETS.filter(x => held[x] > 1000);
        if (!owned.length) { n--; day--; continue; }
        const sym = owned[rnd(owned.length)], q = Math.max(1000, rnd(held[sym]));
        const u = Math.max(1000, Math.round(q / 3));
        events.push(trade(seq++, date, 'SELL', sym, u, 0, q, 'EXTRA')); held[sym] -= q; poolQty += u;
      }
    }
    if (!events.length) continue;
    const s = state(opening({ asOf: '2025-11-01' }), plan([version({ effectiveFrom: '2025-11' })], '2025-11'), events);
    const d = derive(s, '2025-11-30');
    A.deepEqual(d.flags, [], 'chuỗi #' + iter + ' phải hợp lệ: ' + JSON.stringify(d.flags));

    // (1) Số dư tiền mặt = nạp − rút − đổi ra USDT + đổi về VND.
    A.equal(d.vnd.balance, cashIn - cashOut - vndIn + vndOut, 'vnd.balance chuỗi #' + iter);

    // (2) Bảo toàn giá vốn VND. Giá vốn vào hệ = opening + Σ VND_TO_USDT; ra khỏi hệ = giá vốn
    //     giải phóng cho các lệnh USDT_TO_VND (eventEffects.vndRelieved) + phần quét đáy pool.
    const relievedOut = events.filter(e => e.kind === 'TREASURY' && e.dir === 'USDT_TO_VND')
      .reduce((t, e) => t + d.eventEffects[e.id].vndRelieved, 0);
    const fxFromSwaps = events.filter(e => e.kind === 'TREASURY' && e.dir === 'USDT_TO_VND')
      .reduce((t, e) => t + e.vndAmount - d.eventEffects[e.id].vndRelieved, 0);
    const drain = d.realizedFxVnd - fxFromSwaps;
    A.equal(drain, 0, 'chuỗi hợp lệ không bao giờ quét đáy pool (portion trả đúng toàn bộ giá vốn) #' + iter);
    const remaining = Object.values(d.holdings).reduce((t, h) => t + h.costVnd, 0) + d.usdt.costVnd;
    A.equal(remaining + relievedOut + drain, vndIn, 'bảo toàn giá vốn VND chuỗi #' + iter);

    // (3) CASH không bao giờ chạm giá vốn hay pool.
    const noCash = clone(s); noCash.events = noCash.events.filter(e => e.kind !== 'CASH');
    const dn = derive(noCash, '2025-11-30');
    A.equal(Object.values(dn.holdings).reduce((t, h) => t + h.costVnd, 0) + dn.usdt.costVnd, remaining, 'CASH không chạm giá vốn #' + iter);
  }
});
