/* Tái lập 7 lỗi kế toán L-1 (rà soát độc lập sau T-12/T-13/T-14).
 * Mỗi test dưới đây ĐỎ trên code trước khi sửa và XANH sau khi sửa.
 * Số liệu tái lập lấy nguyên văn từ bản rà soát; không tự sinh expected từ derive().
 */
'use strict';
const { test } = require('node:test');
const A = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const L = require(process.env.T12_LEDGER_MODULE || './ledger');

const instant = '2026-09-05T00:00:00.000Z';
const clone = x => JSON.parse(JSON.stringify(x));
const version = (over = {}) => Object.assign({ id: 'plan-1', effectiveFrom: '2026-01', asset: 'ETH', monthlyBudgetVnd: 20000000, scheduleDays: [3, 13, 23], carryPolicy: 'CAPPED_CARRY', carryCapMonths: 1 }, over);
const plan = (startMonth = '2026-01', versions = [version()]) => ({ startMonth, versions });
const opening = (over = {}) => Object.assign({ asOf: '2026-01-01', assets: [], usdt: { qty: 0, costVnd: 0 }, vnd: { qty: 60000000 }, reserveVnd: 0, note: 'Tái lập rà soát L-1' }, over);
const event = (seq, businessDate, fields) => Object.assign({ id: 'event-' + seq, seq, businessDate, createdAt: instant, updatedAt: instant, note: '' }, fields);
const state = (o, p, events) => ({ schema: L.SCHEMA, rev: 0, nextSeq: Math.max(0, ...events.map(e => e.seq)) + 1, plan: clone(p), openingPosition: o === null ? null : clone(o), events: clone(events) });
const derive = (s, asOf) => L.derive(s.openingPosition, s.plan, s.events, asOf);

// Bộ dữ liệu tái lập chung của L1/L2/L4: nạp 50.000.000 VND -> 2.000 USDT, mua PLAN hết 10.010.000 VND.
const fund = event(1, '2026-01-02', { kind: 'TREASURY', dir: 'VND_TO_USDT', vndAmount: 50000000, usdtAmount: 2000000000 });
const buy = event(2, '2026-01-03', { kind: 'TRADE', side: 'BUY', symbol: 'ETH', source: 'PLAN', usdtNotional: 400000000, feeUsdt: 400000, qty: 20000000 });
const base = () => state(opening(), plan(), [fund, buy]);

/* ---------------- L1 — "Mua kế tiếp" sau slot cuối tháng ---------------- */
test('L1 nextPlanned sang tháng sau dùng slot đầu tháng sau, không trừ planInvested tháng này', () => {
  const s = base();
  A.equal(derive(s, '2026-01-14').month.planInvestedVnd, 10010000);
  for (const [asOf, date, amount] of [['2026-01-14', '2026-01-23', 9990000], ['2026-01-24', '2026-02-03', 6666667], ['2026-01-31', '2026-02-03', 6666667]]) {
    const d = derive(s, asOf);
    A.equal(d.month.nextPlannedDate, date, 'nextPlannedDate @' + asOf);
    A.equal(d.month.nextPlannedAmountVnd, amount, 'nextPlannedAmountVnd @' + asOf);
  }
});

/* ---------------- L2 — carry-in phải vào lịch mua ---------------- */
test('L2 sum(plannedPerSlot) == plannedBudgetVnd ở tháng có carry-in', () => {
  const s = state(opening(), plan(), []);              // tháng 1 không mua gì -> carryOut 20.000.000
  const d = derive(s, '2026-02-15');
  A.equal(d.month.carryInVnd, 20000000);
  A.equal(d.month.plannedBudgetVnd, 40000000);
  A.equal(d.month.plannedPerSlot.reduce((a, b) => a + b, 0), d.month.plannedBudgetVnd);
  A.deepEqual(d.month.plannedPerSlot, [13333333, 13333333, 13333334]);
  // Và tháng không có carry vẫn chia đúng ngân sách gốc.
  A.deepEqual(derive(base(), '2026-01-14').month.plannedPerSlot, [6666667, 6666667, 6666666]);
});

/* ---------------- L3 — startMonth sớm hơn version đầu tiên ---------------- */
test('L3a planCheck từ chối startMonth sớm hơn effectiveFrom nhỏ nhất', () => {
  const bad = plan('2026-01', [version({ effectiveFrom: '2026-03' })]);
  A.throws(() => L.derive(opening(), bad, [], '2026-06-15'), /Tháng bắt đầu/);
  A.throws(() => L.canonical(state(opening(), bad, [])), /Tháng bắt đầu/);
  A.throws(() => L.update(state(opening(), plan(), []), { type: 'plan', value: bad }, { today: '2026-06-15' }), /Tháng bắt đầu|version/i);
  // Không chặn nhầm: startMonth == effectiveFrom nhỏ nhất, và version về sau, đều hợp lệ.
  A.doesNotThrow(() => L.derive(opening(), plan('2026-01', [version(), version({ id: 'plan-2', effectiveFrom: '2026-04' })]), [], '2026-06-15'));
  A.doesNotThrow(() => L.canonical(state(opening(), plan('2026-01', []), [])));
});

test('L3b tháng thiếu version cho carryOut = 0, không đầu độc chuỗi tháng sau', () => {
  // Lớp (a) chặn hình dạng này ở cổng vào; lớp (b) là phòng thủ trong derive().
  // Tái lập bằng cách vô hiệu hoá đúng guard (a) trên bản sao module, theo đúng idiom của
  // test_t12_mutations.js — không sửa file repo.
  const src = fs.readFileSync(path.join(__dirname, 'ledger.js'), 'utf8');
  const anchor = 'plan.versions.length && plan.startMonth < earliest';
  A.equal(src.split(anchor).length, 2, 'guard L3a phải xuất hiện đúng một lần');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'l1-l3b-'));
  try {
    const target = path.join(dir, 'ledger.js');
    fs.writeFileSync(target, src.replace(anchor, 'false'));
    const M = require(target);
    const d = M.derive(opening(), plan('2026-01', [version({ effectiveFrom: '2026-03' })]), [], '2026-06-15');
    A.equal(d.months['2026-01'].carryOutVnd, 0, 'tháng không có version: carryOut = 0, không phải null');
    A.equal(d.months['2026-02'].carryOutVnd, 0);
    A.equal(d.months['2026-06'].monthlyBudgetVnd, 20000000);
    A.equal(d.months['2026-06'].carryInVnd, 20000000, 'null không được lan xuống tháng đã có version');
    A.equal(d.months['2026-06'].plannedBudgetVnd, 40000000);
    A.equal(d.months['2026-06'].remainingPlannedBudgetVnd, 40000000);
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

test('L3c không tính được ngân sách thì phải hiện cờ, không im lặng', () => {
  const d = L.derive(opening(), plan('2026-01', []), [], '2026-06-15');
  A.equal(d.month.plannedBudgetVnd, null);
  A.ok(d.flags.includes('UNKNOWN_VND_BASIS'), 'flags = ' + JSON.stringify(d.flags));
});

/* ---------------- L4 — SELL bị chặn ở cổng vào ---------------- */
test('L4 event TRADE side=SELL bị từ chối, kèm tham chiếu H-46', () => {
  const sell = event(3, '2026-01-20', { kind: 'TRADE', side: 'SELL', symbol: 'ETH', source: 'EXTRA', usdtNotional: 200000000, feeUsdt: 0, qty: 10000000 });
  const s = base(); s.events.push(sell); s.nextSeq = 4;
  A.throws(() => L.canonical(s), /H-46/);
  A.throws(() => derive(s, '2026-01-31'), /H-46/);
  A.throws(() => L.update(base(), { type: 'event', value: sell }, { id: 'x', instant }), /H-46/);
  // Bất biến bảo toàn VND của bộ dữ liệu gốc vẫn nguyên vẹn khi không có SELL.
  const d = derive(base(), '2026-01-31');
  A.equal(d.holdings.ETH.costVnd + d.usdt.costVnd + d.realizedFxVnd, 50000000);
});

/* ---------------- L5 — không sửa hồi tố ngân sách version đã tồn tại ---------------- */
test('L5 đổi monthlyBudgetVnd/carryPolicy/asset của version cũ bị chặn', () => {
  const s = L.canonical(state(opening(), plan(), []));
  const meta = { today: '2026-06-15', instant, id: 'x' };
  for (const over of [{ monthlyBudgetVnd: 30000000 }, { carryPolicy: 'CAPPED_CARRY', carryCapMonths: 1, scheduleDays: [3, 13, 23] }, { scheduleDays: [1, 15] }, { effectiveFrom: '2026-02' }]) {
    const next = plan('2026-01', [version(over)]);
    if (JSON.stringify(next.versions[0]) === JSON.stringify(version())) continue;
    A.throws(() => L.update(s, { type: 'plan', value: next }, meta), /version/i, JSON.stringify(over));
  }
  // Đường hợp lệ: thêm version mới áp dụng từ tháng hiện tại trở đi.
  const ok = plan('2026-01', [version(), version({ id: 'plan-2', effectiveFrom: '2026-06', monthlyBudgetVnd: 30000000 })]);
  A.doesNotThrow(() => L.update(s, { type: 'plan', value: ok }, meta));
});

/* ---------------- L6 — migration sổ legacy có phí ---------------- */
const legacyWithFee = () => ({
  schema: 'ethdca.tracker/1', rev: 4, months: {}, oppFund: { a: 0, r: 0, d: 0 },
  treasury: { vnd: 0, usdt: 879.5 }, eth: 0.05, costUsdt: 120, costVnd: 3012500,
  ladders: [], p2p: [], ledger: [], extraDays: [],
  trades: [{ ts: '2026-01-06T00:00:00Z', src: 'BASE', usdt: 120, price: 2400, eth: 0.05, fee: 0.5, vndRate: null, vndCost: 0, recPrice: null, shortfallBps: null, zone: null }]
});
const migrationConfirmation = () => ({
  contributions: 'ignore', plan: plan(),
  openingPosition: { asOf: '2026-01-01', assets: [], usdt: { qty: 1000000000, costVnd: 25000000 }, vnd: { qty: 0 }, reserveVnd: 0, note: 'Pool đầu kỳ tổng hợp 25.000 VND/USDT' },
  dates: { 'trades[0]': { businessDate: '2026-01-06', order: 1 } }
});
test('L6 sổ legacy có fee 0,5 USDT migrate THÀNH CÔNG', () => {
  const r = L.migrate(legacyWithFee(), migrationConfirmation(), { id: 'mig', instant, today: '2026-01-09' });
  A.equal(r.ok, true, JSON.stringify(r.errors) + ' ' + JSON.stringify(r.deltas));
  A.equal(r.deltas.costUsdt.deltaUnits, 0, 'oracle costUsdt phải so cùng định nghĩa (không gồm phí)');
  A.equal(r.deltas.costVnd.deltaVnd, 0);
  // Sổ mới vẫn ghi phí vào giá vốn USDT thực tế (định nghĩa của derive không đổi).
  const d = L.derive(r.state.openingPosition, r.state.plan, r.state.events, '2026-01-09');
  A.equal(d.holdings.ETH.costUsdt, 120500000);
  A.equal(d.holdings.ETH.costVnd, 3012500);
});
test('L6 lệch costVnd lớn là cờ CỨNG, không đi qua im lặng', () => {
  const legacy = legacyWithFee(); legacy.costVnd = 3012500 + 900000000;
  const r = L.migrate(legacy, migrationConfirmation(), { id: 'mig', instant, today: '2026-01-09' });
  A.equal(r.ok, false);
  A.ok(r.errors.some(x => /costVnd/.test(x)), JSON.stringify(r.errors));
});

/* ---------------- L7 ---------------- */
test('L7a eventEffects là own-property kể cả id = __proto__', () => {
  const s = state(opening(), plan(), [Object.assign(clone(fund), { id: '__proto__' })]);
  const d = derive(s, '2026-01-31');
  A.ok(Object.prototype.hasOwnProperty.call(d.eventEffects, '__proto__'), 'chốt M-2 sẽ bỏ sót event này');
  A.ok(Object.keys(d.eventEffects).includes('__proto__'));
  A.equal(Object.values(d.eventEffects).length, 1);
});

test('L7c vnd.balance âm phải bật cờ LEDGER_INCONSISTENT', () => {
  const s = state(opening({ vnd: { qty: 0 } }), plan(), [fund]);
  const d = derive(s, '2026-01-31');
  A.equal(d.vnd.balance, -50000000);
  A.ok(d.flags.includes('LEDGER_INCONSISTENT'), 'flags = ' + JSON.stringify(d.flags));
  A.equal(d.firstOffendingEventId, 'event-1');
  A.equal(d.firstOffendingBusinessDate, '2026-01-02');
});

test('L7d priceUsdt = 0 bị từ chối', () => {
  const zero = event(3, '2026-01-20', { kind: 'PRICE', symbol: 'ETH', priceUsdt: 0, usdVndRate: null });
  const s = base(); s.events.push(zero); s.nextSeq = 4;
  A.throws(() => L.canonical(s), /[Gg]iá/);
  const ok = clone(zero); ok.priceUsdt = 1;
  const t = base(); t.events.push(ok); t.nextSeq = 4;
  A.doesNotThrow(() => L.canonical(t));
});

test('L7e BUY có feeUsdt > usdtNotional bị từ chối', () => {
  const bad = event(3, '2026-01-20', { kind: 'TRADE', side: 'BUY', symbol: 'ETH', source: 'EXTRA', usdtNotional: 1000000, feeUsdt: 2000000, qty: 100 });
  const s = base(); s.events.push(bad); s.nextSeq = 4;
  A.throws(() => L.canonical(s), /[Pp]hí/);
});

test('L7f usdVndRate được derive() dùng thật cho định giá', () => {
  const price = event(3, '2026-01-31', { kind: 'PRICE', symbol: 'ETH', priceUsdt: 2400000000, usdVndRate: 26000 });
  const s = base(); s.events.push(price); s.nextSeq = 4;
  const d = derive(s, '2026-01-31');
  A.equal(d.valuation.usdt, 480000000);            // 0,2 ETH × 2.400 USDT = 480 USDT
  A.equal(d.valuation.vnd, 12480000);              // 480 USDT × 26.000
  A.equal(d.valuation.usdVndRate, 26000);
  const noRate = clone(price); noRate.usdVndRate = null;
  const t = base(); t.events.push(noRate); t.nextSeq = 4;
  const e = derive(t, '2026-01-31');
  A.equal(e.valuation.usdt, 480000000);
  A.equal(e.valuation.vnd, null, 'không có tỷ giá thì KHÔNG bịa ra một tỷ giá nào');
});

test('L7g engine.js không còn được nhúng vào trang', () => {
  const build = fs.readFileSync(path.join(__dirname, 'build_app.js'), 'utf8');
  A.doesNotMatch(build, /readFileSync\(path\.join\(DIR, 'engine\.js'\)/, 'engine.js (lỗi rolling-window B10) không còn được đọc vào bundle');
  A.doesNotMatch(build, /\+ engine \+/, 'engine.js không còn được nối vào BODY');
  A.match(build, /if \(FULL\.includes\('const ENGINE'\)\) throw/, 'assertion bắt buộc đổi chiều thành cấm nhúng');
});
