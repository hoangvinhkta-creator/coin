/* E1 tổng hợp T-12; oracle đóng băng trong test_t12_fixtures.js, không tự sinh expected. */
'use strict';
const { test } = require('node:test');
const A = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');
const L = require(process.env.T12_LEDGER_MODULE || './ledger');
const F = require('./test_t12_fixtures');
const get = (o, p) => p.split('.').reduce((a, k) => a[k], o);
const derive = (s, asOfDate = '2026-02-20') => L.derive(s.openingPosition, s.plan, s.events, asOfDate);
const meta = { id: 'new-id', instant: F.instant, today: '2026-01-09' };
function fixtureState(sc) {
  if (sc.state) return F.copy(sc.state);
  const r = L.migrate(sc.legacy, sc.confirmation, meta); A.equal(r.ok, true, JSON.stringify(r)); return r.state;
}
for (const sc of F.scenarios) test(sc.id + ' oracle số nguyên tolerance=0', () => {
  const s = fixtureState(sc), before = JSON.stringify(s);
  for (const ev of sc.evaluations) {
    const d = derive(s, ev.asOfDate);
    for (const [key, expected] of Object.entries(ev.expected)) A.deepEqual(get(d, key), expected, sc.id + ' ' + key);
    for (const [key, expected] of Object.entries(ev.ratios || {})) {
      const r = get(d, key); A.equal(BigInt(r.numerator) * BigInt(expected[1]), BigInt(expected[0]) * BigInt(r.denominator), key);
    }
  }
  if (sc.instant) A.equal(L.clock(sc.instant).today, sc.evaluations[0].asOfDate);
  A.equal(JSON.stringify(s), before);
});
test('INV-1 canonical allowlist, không durable derived, bỏ derivedSnapshot', () => {
  const s = F.copy(F.scenarios[3].state), d = derive(s);
  A.deepEqual(L.canonical(Object.assign({}, s, { derivedSnapshot: { costVnd: 99, holdings: 99 } })), s);
  for (const key of ['price', 'rate', 'avgCostVnd', 'ethQty', 'costUsdt', 'costVnd', 'treasury', 'reserveBalance', 'invested', 'remaining', 'next']) {
    A.throws(() => L.canonical(Object.assign({}, s, { [key]: 42 })));
  }
  const polluted = F.copy(s); polluted.events[0].rate = 99; A.throws(() => L.canonical(polluted));
  A.equal('holdings' in JSON.parse(JSON.stringify(s)), false); A.ok(d.holdings.ETH);
});
test('INV-2 150 hoán vị + hai process TZ cho cùng ledger', () => {
  const s = F.copy(F.scenarios[6].state), expected = derive(s); let seed = 871;
  for (let n = 0; n < 150; n++) {
    const p = F.copy(s); for (let i = p.events.length - 1; i > 0; i--) { seed = (seed * 16807) % 2147483647; const j = seed % (i + 1); [p.events[i], p.events[j]] = [p.events[j], p.events[i]]; }
    A.deepEqual(derive(p), expected);
  }
  const script = "const L=require('./ledger'),F=require('./test_t12_fixtures'),s=F.scenarios[6].state;process.stdout.write(JSON.stringify(L.derive(s.openingPosition,s.plan,s.events,'2026-02-20')))";
  const outputs = ['UTC', 'America/Los_Angeles'].map(TZ => execFileSync(process.execPath, ['-e', script], { cwd: __dirname, env: { ...process.env, TZ }, encoding: 'utf8' }));
  A.equal(outputs[0], outputs[1]); A.deepEqual(JSON.parse(outputs[0]), expected);
});
test('INV-3 WAC conservation, pool drain, SELL ETH/USDT và ROUND_VND', () => {
  const o = F.copy(F.opening); o.usdt = { qty: 3000000, costVnd: 10 };
  const s = F.state(o, F.plan(), [F.buy(1, '2026-01-02', 1000000, 1000), F.buy(2, '2026-01-03', 2000000, 2000)]);
  const d = derive(s); A.equal(d.eventEffects['event-1'].vndRelieved, 3); A.equal(d.eventEffects['event-2'].vndRelieved, 7);
  A.equal(d.usdt.costVnd, 0); A.equal(d.usdt.qty, 0); A.equal(d.holdings.ETH.costVnd, 30000010); A.equal(d.realizedFxVnd, 0);
  const sell = F.event(1, '2026-01-02', { kind: 'TRADE', side: 'SELL', symbol: 'ETH', source: 'EXTRA', qty: 25000000, usdtNotional: 700000000, feeUsdt: 1000000 });
  const sold = derive(F.state(F.opening, F.plan(), [sell]));
  A.equal(sold.holdings.ETH.qty, 25000000); A.equal(sold.holdings.ETH.costUsdt, 600000000); A.equal(sold.holdings.ETH.costVnd, 15000000);
  A.equal(sold.usdt.qty, 899000000); A.equal(sold.usdt.costVnd, 22475000);
  const sale = F.event(1, '2026-01-02', { kind: 'TREASURY', dir: 'USDT_TO_VND', vndAmount: 5100000, usdtAmount: 200000000 });
  const p = derive(F.state(F.opening, F.plan(), [sale])); A.equal(p.usdt.qty, 0); A.equal(p.usdt.costVnd, 0); A.equal(p.realizedFxVnd, 100000);
  A.equal(L.round(5, 2), 3); A.equal(L.round(4, 2), 2);
  A.equal(L.round(9000000000000000n * 8999999999999999n, 9000000000000000n), 8999999999999999);
});
test('INV-4 prefix deficit ghi event đầu tiên dù cuối sổ dương; reserve WITHDRAW', () => {
  const s = F.state(F.opening, F.plan(), [F.buy(1, '2026-01-02', 300000000, 10000000), F.p2p(2, '2026-01-03', 10000000, 400000000)]);
  const d = derive(s); A.ok(d.flags.includes('LEDGER_INCONSISTENT')); A.equal(d.firstOffendingEventId, 'event-1'); A.equal(d.firstOffendingBusinessDate, '2026-01-02'); A.equal(d.usdt.qty, 300000000); A.equal(d.holdings.ETH.costUsdt, 1500000000); A.equal(d.holdings.ETH.costVnd, null);
  const w = F.event(1, '2026-01-02', { kind: 'RESERVE', type: 'WITHDRAW', vndAmount: 1 });
  const c = F.event(2, '2026-01-03', { kind: 'RESERVE', type: 'CONTRIBUTE', vndAmount: 10 });
  const r = derive(F.state(F.opening, F.plan(), [w, c])); A.equal(r.reserve.balance, 9); A.equal(r.firstOffendingEventId, 'event-1');
});
test('INV-5 integer schema, boundary validation và decimal nhập chính xác', () => {
  const s = F.copy(F.scenarios[3].state);
  A.equal(L.decimal('0.000001', 6), 1); A.equal(L.decimal('0.00000001', 8), 1); A.throws(() => L.decimal('0.0000001', 6));
  for (const value of [0.1, -1, NaN, Infinity, 9000000000000001]) { const p = F.copy(s); p.events[0].vndAmount = value; A.throws(() => L.canonical(p)); }
  for (const key of ['costUsdt', 'costVnd']) { const p = F.copy(s); p.openingPosition.assets[0][key] = null; A.doesNotThrow(() => L.canonical(p)); }
  A.equal(L.dateValid('2026-02-29'), false); A.equal(L.dateValid('2028-02-29'), true);
});
test('INV-6 metadata không đi vào tiền và SC-08 một clock canonical', () => {
  const s = F.copy(F.scenarios[6].state), expected = derive(s);
  s.events.forEach((e, i) => { e.createdAt = '2001-01-0' + (i + 1) + 'T00:00:00Z'; e.updatedAt = '2099-12-31T23:59:59Z'; });
  A.deepEqual(derive(s), expected); A.equal(L.clock('2026-02-28T18:30:00Z').today, '2026-03-01');
});
test('INV-7 từ chối event trước opening và sửa opening vượt event', () => {
  const s = F.copy(F.scenarios[3].state); s.events[0].businessDate = '2025-12-31'; A.throws(() => L.canonical(s), /trước số dư/);
  const good = F.copy(F.scenarios[3].state), o = F.copy(F.opening); o.asOf = '2026-02-01'; A.throws(() => L.update(good, { type: 'opening', value: o }, meta));
});
test('INV-8 P2P chỉ chuyển tài sản tiền tệ, không đầu tư', () => {
  const before = derive(F.scenarios[0].state), after = derive(F.scenarios[1].state);
  A.deepEqual(after.holdings, before.holdings); A.equal(after.month.investedThisMonthVnd, 0); A.equal(after.month.planInvestedVnd, 0);
});
test('INV-9 EXTRA/RESERVE cách ly plan/carry ở hai thời điểm', () => {
  const s = F.copy(F.scenarios[9].state), p = F.copy(s); p.events = p.events.filter(e => e.kind === 'TRADE' && e.source === 'PLAN');
  for (const asOf of ['2026-03-21', '2026-04-01']) {
    const a = derive(s, asOf), b = derive(p, asOf);
    for (const key of ['planInvestedVnd', 'remainingPlannedBudgetVnd', 'carryInVnd', 'carryOutVnd', 'nextPlannedDate', 'nextPlannedAmountVnd']) A.equal(a.month[key], b.month[key], key);
    if (asOf === '2026-04-01') A.equal(a.months['2026-03'].carryOutVnd, b.months['2026-03'].carryOutVnd);
  }
});
test('INV-10 PRICE không chạm tiền; không ENGINE trong module', () => {
  A.doesNotMatch(fs.readFileSync(path.join(__dirname, 'ledger.js'), 'utf8'), /\bENGINE\b|engine\.js/);
  const s = F.copy(F.scenarios[9].state), before = derive(s, '2026-03-21');
  for (const n of [1, 1000000, 9000000000000]) {
    const p = F.copy(s); p.events.push(F.event(6, '2026-03-21', { kind: 'PRICE', symbol: 'ETH', priceUsdt: n, usdVndRate: 999999 }));
    const after = derive(p, '2026-03-21');
    for (const k of ['holdings', 'usdt', 'vnd', 'reserve', 'month', 'months', 'realizedFxVnd']) A.deepEqual(after[k], before[k]);
  }
});
test('INV-11 null UNKNOWN lan truyền và không có kế hoạch', () => {
  const s = F.copy(F.scenarios[2].state); s.openingPosition.usdt.costVnd = null;
  const d = derive(s, '2026-01-06'); A.equal(d.holdings.ETH.costVnd, null); A.equal(d.holdings.ETH.costUsdt, 1800600000); A.equal(d.month.planInvestedVnd, null); A.equal(d.month.remainingPlannedBudgetVnd, null); A.equal(d.usdt.costVnd, null); A.ok(d.flags.includes('UNKNOWN_VND_BASIS'));
  const p = F.copy(s); p.plan.versions = []; A.equal(derive(p).month.monthlyBudgetVnd, null);
  const sale = F.event(1, '2026-01-02', { kind: 'TRADE', side: 'SELL', symbol: 'ETH', source: 'EXTRA', qty: 25000000, usdtNotional: 500000000, feeUsdt: 0 });
  const o = F.copy(F.opening); o.usdt = { qty: 0, costVnd: 0 }; A.equal(derive(F.state(o, F.plan(), [sale])).usdt.costVnd, null);
});
test('INV-12 M1/M2/M3/M4 migration nguyên tử, raw legacy giữ nguyên', async () => {
  for (const code of ['M-1', 'M-2', 'M-3', 'M-4']) {
    const raw = F.copy(F.legacy), c = F.copy(F.confirmation); let durable = JSON.stringify(raw), writes = 0;
    if (code === 'M-1') delete c.dates['trades[3]'];
    if (code === 'M-2') c.openingPosition.usdt.qty = 0;
    if (code === 'M-3') raw.eth = 1;
    if (code === 'M-4') raw.ladders = [{ zones: [{ filled_vnd: 1 }] }];
    durable = JSON.stringify(raw); const before = durable;
    const r = await L.destructive(raw, () => L.migrate(raw, c, meta), { snapshot: () => {}, confirm: () => true, commit: state => { writes++; durable = JSON.stringify(state); } });
    A.equal(r.ok, false); A.ok(r.errors.some(x => x.startsWith(code))); A.equal(writes, 0); A.equal(durable, before);
  }
  const r = L.migrate(F.legacy, F.confirmation, meta); A.equal(r.ok, true); A.deepEqual(r.state.LEGACY_ARCHIVE.raw, F.legacy); A.ok(r.warnings.includes('W-1')); A.equal(r.deltas.costVnd.actual, null);
  A.ok(r.state.events.every(e => e.source === 'EXTRA' && !('vndRate' in e) && !('price' in e)));
});
test('INV-13 SPLIT_VND 80 ngân sách × n1..12, phần cuối nhận dư', () => {
  let seed = 733; for (let i = 0; i < 80; i++) { seed = seed * 16807 % 2147483647; const amount = seed;
    for (let n = 1; n <= 12; n++) { const a = L.split(amount, n); A.equal(a.reduce((a, b) => a + b, 0), amount); A.ok(a.every(Number.isInteger)); A.equal(a.length, n); }
  }
  A.deepEqual(L.split(20000000, 3), [6666667, 6666667, 6666666]);
});
test('INV-14 snapshot trước import/wipe/migration/delete, cả hủy/lỗi', async () => {
  for (const name of ['import', 'wipe', 'migration', 'delete']) for (const outcome of ['accept', 'cancel', 'fail']) {
    const calls = [], s = F.copy(F.scenarios[0].state), before = JSON.stringify(s);
    await L.destructive(s, () => { calls.push(name); return outcome === 'fail' ? { ok: false, errors: ['forced'] } : { ok: true, state: s }; }, {
      snapshot: raw => { calls.push('snapshot'); A.equal(JSON.stringify(raw), before); }, confirm: () => { calls.push('confirm'); return outcome !== 'cancel'; }, commit: () => calls.push('commit')
    });
    A.deepEqual(calls, outcome === 'cancel' ? ['snapshot', 'confirm'] : outcome === 'fail' ? ['snapshot', 'confirm', name] : ['snapshot', 'confirm', name, 'commit']);
  }
  let called = false; await A.rejects(L.destructive(F.scenarios[0].state, () => { called = true; }, { snapshot: () => { throw Error('storage full'); }, confirm: () => true })); A.equal(called, false);
});
test('INV-15 20 edits giữ id/seq; delete/create không reuse', () => {
  let s = F.copy(F.scenarios[3].state), original = F.copy(s.events[1]);
  for (let i = 0; i < 20; i++) { const value = F.copy(original); value.qty += i; s = L.update(s, { type: 'event', id: original.id, value }, { ...meta, instant: '2026-02-20T00:00:00Z' }); A.equal(s.events[1].id, original.id); A.equal(s.events[1].seq, original.seq); A.equal(s.events[1].createdAt, original.createdAt); }
  s = L.update(s, { type: 'delete', id: original.id }, meta); s = L.update(s, { type: 'event', value: original }, { ...meta, id: 'new-uuid' });
  A.equal(s.events.at(-1).id, 'new-uuid'); A.equal(s.events.at(-1).seq, 5); A.equal(s.events.some(e => e.id === original.id), false);
});
test('SC-05/06/07 qua update thật khớp fixture replay', () => {
  let s = F.copy(F.scenarios[3].state), a = F.copy(F.scenarios[4].action);
  s = L.update(s, a, { ...meta, instant: '2026-02-20T00:00:00Z' }); A.deepEqual(derive(s), derive(F.scenarios[4].state));
  s = L.update(F.scenarios[3].state, { type: 'delete', id: 'event-3' }, meta); A.deepEqual(derive(s), derive(F.scenarios[5].state));
  s = L.update(F.scenarios[3].state, { type: 'event', value: F.scenarios[6].state.events[4] }, { ...meta, id: 'event-5' }); A.deepEqual(derive(s), derive(F.scenarios[6].state));
});
test('Calendar plan versions, clamp tháng nhuận, next amount biết được', () => {
  const s = F.state(null, F.plan('2028-02')); s.plan.versions[0].scheduleDays = [28, 29, 30, 31];
  const d = derive(s, '2028-02-28'); A.deepEqual(d.month.plannedPerSlot, [10000000, 10000000]); A.equal(d.month.nextPlannedDate, '2028-02-28'); A.equal(d.month.nextPlannedAmountVnd, 10000000);
  const later = derive(s, '2028-02-29'); A.equal(later.month.nextPlannedAmountVnd, 20000000);
  A.equal(derive(F.state(null, F.plan('2026-01')), '2026-01-31').month.nextPlannedAmountVnd, 6666667);
});
test('CHECK-T12-10 SC-12 báo chỉ số legacy, lý do W1 và đường sửa explicit', () => {
  const r = L.migrate(F.legacy, F.confirmation, meta);
  A.ok(Array.isArray(r.unknownBasis), 'cần báo cáo từng giao dịch UNKNOWN');
  const row = r.unknownBasis.find(x => x.legacyIndex === 'trades[3]');
  A.ok(row); A.match(row.reason, /USDT/); A.match(row.correction, /openingPosition.usdt.costVnd/);
});
test('CHECK-T12-06 đổi schedule chỉ bằng version về sau', () => {
  const s = F.copy(F.scenarios[3].state), p = F.copy(s.plan); p.versions[0].scheduleDays = [1, 15];
  A.throws(() => L.update(s, { type: 'plan', value: p }, { ...meta, today: '2026-03-21' }), /version|lịch/i);
  const q = F.copy(s.plan); q.versions.push({ ...q.versions[0], id: 'plan-2', effectiveFrom: '2026-04', scheduleDays: [1, 15] });
  const updated = L.update(s, { type: 'plan', value: q }, { ...meta, today: '2026-03-21' });
  A.deepEqual(derive(s, '2026-02-05').month, derive(updated, '2026-02-05').month);
});
test('Migration P2P hai chân actual gồm fee; đối chiếu VND/cost và float delta', () => {
  const raw = F.copy(F.legacy); raw.trades = []; raw.eth = 0; raw.costUsdt = 0;
  raw.p2p = [{ ts: F.instant, dir: 'VND_TO_USDT', vnd: 2500000, usdt: 100, fee: 1000, rate: 999 }, { ts: F.instant, dir: 'USDT_TO_VND', vnd: 1300000, usdt: 50, fee: 2000, rate: 1 }];
  raw.treasury = { vnd: 1797000, usdt: 50 };
  const c = { contributions: 'opening', plan: F.plan(), openingPosition: { asOf: '2026-01-01', assets: [], usdt: { qty: 0, costVnd: 0 }, vnd: { qty: 3000000 }, reserveVnd: 0, note: 'VND nạp đã xác nhận tổng hợp' }, dates: { 'p2p[0]': { businessDate: '2026-01-02', order: 1 }, 'p2p[1]': { businessDate: '2026-01-03', order: 2 } } };
  const r = L.migrate(raw, c, meta); A.equal(r.ok, true, JSON.stringify(r)); A.equal(r.state.events[0].vndAmount, 2501000); A.equal(r.state.events[1].vndAmount, 1298000);
  A.equal(derive(r.state).usdt.costVnd, 1250500); A.equal(r.deltas.vnd.deltaUnits, 0);
});
