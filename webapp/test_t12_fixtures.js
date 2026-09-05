/* T12_GOLDEN_ACCOUNTING_BASELINE — dữ liệu tổng hợp, oracle từ spec §19 + DEC-044/045.
 * Các phép dựng dưới đây chỉ sao chép input. Không import derive/ledger để sinh expected.
 * Giá trị tiền nguyên dùng micro-USDT và 1e-8 ETH; tolerance của mọi oracle = 0.
 */
'use strict';
const copy = x => JSON.parse(JSON.stringify(x));
const instant = '2026-09-05T00:00:00.000Z';
const plan = (start = '2026-01') => ({ startMonth: start, versions: [{ id: 'plan-1', effectiveFrom: start, asset: 'ETH', monthlyBudgetVnd: 20000000, scheduleDays: [3, 13, 23], carryPolicy: 'CAPPED_CARRY', carryCapMonths: 1 }] });
const opening = { asOf: '2026-01-01', assets: [{ symbol: 'ETH', qty: 50000000, costUsdt: 1200000000, costVnd: 30000000 }], usdt: { qty: 200000000, costVnd: 5000000 }, vnd: { qty: 100000000 }, reserveVnd: 0, note: 'Số dư tổng hợp SC-01; VND 100 triệu chỉ phục vụ P2P tổng hợp.' };
function event(seq, date, fields) { return Object.assign({ id: 'event-' + seq, seq, businessDate: date, createdAt: instant, updatedAt: instant, note: '' }, fields); }
const p2p = (seq, date, vndAmount, usdtAmount) => event(seq, date, { kind: 'TREASURY', dir: 'VND_TO_USDT', vndAmount, usdtAmount });
const buy = (seq, date, usdtNotional, qty, source = 'PLAN', feeUsdt = 0, note = '') => Object.assign(event(seq, date, { kind: 'TRADE', side: 'BUY', symbol: 'ETH', usdtNotional, qty, feeUsdt, source }), { note });
const state = (o = opening, p = plan(), events = []) => ({ schema: 'coindca.ledger/2', rev: 0, nextSeq: Math.max(0, ...events.map(e => e.seq)) + 1, plan: copy(p), openingPosition: copy(o), events: copy(events) });
const a = p2p(1, '2026-01-05', 25600000, 1000000000);
const b = buy(2, '2026-01-06', 600000000, 25000000, 'PLAN', 600000);
const c = p2p(3, '2026-02-03', 13100000, 500000000);
const d = buy(4, '2026-02-05', 500000000, 20000000);
const four = [a, b, c, d];
const marchOpening = { asOf: '2026-03-01', assets: [{ symbol: 'ETH', qty: 0, costUsdt: 0, costVnd: 0 }], usdt: { qty: 2000000000, costVnd: 50000000 }, vnd: { qty: 0 }, reserveVnd: 0, note: 'Pool tổng hợp 25.000 VND/USDT cho SC-09/10/11' };
const march = [buy(1, '2026-03-03', 240000000, 10000000), buy(2, '2026-03-13', 240000000, 10000000), buy(3, '2026-03-17', 200000000, 8000000, 'EXTRA')];
const reserve = event(4, '2026-03-02', { kind: 'RESERVE', type: 'CONTRIBUTE', vndAmount: 10000000 });
const reserveBuy = buy(5, '2026-03-20', 160000000, 6400000, 'RESERVE', 0, 'giải ngân dự phòng, giá giảm sâu');
const legacy = { schema: 'ethdca.tracker/1', rev: 4, months: {}, oppFund: { a: 0, r: 0, d: 0 }, treasury: { vnd: 0, usdt: 340 }, eth: 0.275, costUsdt: 660, costVnd: 0, ladders: [], p2p: [], ledger: [{ type: 'ETH_BUY', vnd: 0 }], extraDays: [{ date: '2026-01-01', price: 2400 }], trades: [0, 1, 2, 3].map(i => ({ ts: '2026-01-0' + (6 + i) + 'T00:00:00Z', src: 'BASE', usdt: i === 3 ? 300 : 120, price: 2400, eth: i === 3 ? 0.125 : 0.05, fee: 0, vndRate: null, vndCost: 0, recPrice: null, shortfallBps: null, zone: null })) };
const confirmation = { contributions: 'ignore', plan: plan(), openingPosition: { asOf: '2026-01-01', assets: [], usdt: { qty: 1000000000, costVnd: null }, vnd: { qty: 0 }, reserveVnd: 0, note: 'Owner tổng hợp xác nhận lượng USDT đầu kỳ, chưa biết VND basis' }, dates: Object.fromEntries([0, 1, 2, 3].map(i => ['trades[' + i + ']', { businessDate: '2026-01-0' + (6 + i), order: i + 1 }])) };
const scenarios = [
  { id: 'SC-01', state: state(), evaluations: [{ asOfDate: '2026-01-01', expected: { 'holdings.ETH.qty': 50000000, 'holdings.ETH.costUsdt': 1200000000, 'holdings.ETH.costVnd': 30000000, 'usdt.qty': 200000000, 'usdt.costVnd': 5000000, 'month.investedThisMonthVnd': 0, 'month.planInvestedVnd': 0 }, ratios: { 'holdings.ETH.avgCostUsdt': ['120000000000000000', '50000000'], 'holdings.ETH.avgCostVnd': ['3000000000000000', '50000000'], 'usdt.avgVnd': ['5000000000000', '200000000'] } }] },
  { id: 'SC-02', state: state(opening, plan(), [a]), evaluations: [{ asOfDate: '2026-01-05', expected: { 'usdt.qty': 1200000000, 'usdt.costVnd': 30600000, 'holdings.ETH.qty': 50000000, 'holdings.ETH.costVnd': 30000000, 'month.investedThisMonthVnd': 0 }, ratios: { 'usdt.avgVnd': ['30600000000000', '1200000000'] } }] },
  { id: 'SC-03', state: state(opening, plan(), [a, b]), evaluations: [{ asOfDate: '2026-01-06', expected: { 'holdings.ETH.qty': 75000000, 'holdings.ETH.costUsdt': 1800600000, 'holdings.ETH.costVnd': 45315300, 'usdt.qty': 599400000, 'usdt.costVnd': 15284700, 'eventEffects.event-2.vndRelieved': 15315300, 'month.investedThisMonthVnd': 15315300, 'month.remainingPlannedBudgetVnd': 4684700 }, ratios: { 'holdings.ETH.avgCostUsdt': ['180060000000000000', '75000000'], 'holdings.ETH.avgCostVnd': ['4531530000000000', '75000000'] } }] },
  { id: 'SC-04', state: state(opening, plan(), four), evaluations: [{ asOfDate: '2026-02-05', expected: { 'holdings.ETH.qty': 95000000, 'holdings.ETH.costUsdt': 2300600000, 'holdings.ETH.costVnd': 58224478, 'eventEffects.event-3.usdtQty': 1099400000, 'eventEffects.event-3.usdtCostVnd': 28384700, 'eventEffects.event-4.vndRelieved': 12909178, 'usdt.qty': 599400000, 'usdt.costVnd': 15475522, 'month.carryInVnd': 4684700, 'month.plannedBudgetVnd': 24684700, 'month.planInvestedVnd': 12909178, 'month.remainingPlannedBudgetVnd': 11775522 }, ratios: { 'usdt.avgVnd': ['15475522000000', '599400000'], 'holdings.ETH.avgCostVnd': ['5822447800000000', '95000000'] } }] },
  { id: 'SC-05', state: state(opening, plan(), four.map(e => e.id === 'event-2' ? Object.assign({}, e, { qty: 24000000, updatedAt: '2026-02-20T00:00:00Z' }) : e)), action: { type: 'event', id: 'event-2', value: Object.assign({}, b, { qty: 24000000 }) }, evaluations: [{ asOfDate: '2026-02-20', expected: { 'holdings.ETH.qty': 94000000, 'holdings.ETH.costUsdt': 2300600000, 'holdings.ETH.costVnd': 58224478, 'usdt.qty': 599400000, 'usdt.costVnd': 15475522 }, ratios: { 'holdings.ETH.avgCostUsdt': ['230060000000000000', '94000000'], 'holdings.ETH.avgCostVnd': ['5822447800000000', '94000000'] } }] },
  { id: 'SC-06', state: state(opening, plan(), [a, b, d]), deletedId: 'event-3', evaluations: [{ asOfDate: '2026-02-20', expected: { 'eventEffects.event-4.vndRelieved': 12750000, 'holdings.ETH.costVnd': 58065300, 'usdt.qty': 99400000, 'usdt.costVnd': 2534700 } }] },
  { id: 'SC-07', state: state(opening, plan(), four.concat(buy(5, '2026-02-04', 100000000, 4000000))), evaluations: [{ asOfDate: '2026-02-20', expected: { 'eventEffects.event-5.vndRelieved': 2581836, 'eventEffects.event-4.vndRelieved': 12909178, 'usdt.qty': 499400000, 'month.investedThisMonthVnd': 15491014, 'month.planInvestedVnd': 15491014 } }] },
  { id: 'SC-08', instant: '2026-02-28T18:30:00Z', state: state(Object.assign({}, marchOpening, { asOf: '2026-02-01' }), plan('2026-02'), [buy(1, '2026-03-01', 240000000, 10000000)]), evaluations: [{ asOfDate: '2026-03-01', expected: { currentMonth: '2026-03', 'month.investedThisMonthVnd': 6000000, 'months.2026-02.carryOutVnd': 20000000, 'month.carryInVnd': 20000000 } }] },
  { id: 'SC-09', state: state(marchOpening, plan('2026-03'), march), evaluations: [
    { asOfDate: '2026-03-18', expected: { 'month.investedThisMonthVnd': 17000000, 'month.planInvestedVnd': 12000000, 'month.remainingPlannedBudgetVnd': 8000000, 'month.nextPlannedDate': '2026-03-23', 'month.nextPlannedAmountVnd': 8000000, 'month.plannedPerSlot': [6666667, 6666667, 6666666], 'month.carryOutVnd': null } },
    { asOfDate: '2026-04-01', expected: { 'months.2026-03.carryOutVnd': 8000000, 'month.carryInVnd': 8000000 } }
  ] },
  { id: 'SC-10', state: state(marchOpening, plan('2026-03'), march.concat(reserve, reserveBuy)), evaluations: [
    { asOfDate: '2026-03-21', expected: { 'reserve.balance': 6000000, 'month.investedThisMonthVnd': 21000000, 'month.planInvestedVnd': 12000000, 'month.remainingPlannedBudgetVnd': 8000000, 'month.carryOutVnd': null } },
    { asOfDate: '2026-04-01', expected: { 'months.2026-03.carryOutVnd': 8000000, 'month.carryInVnd': 8000000, 'reserve.balance': 6000000 } }
  ] },
  { id: 'SC-11', state: state(marchOpening, plan('2026-03'), march.concat(buy(4, '2026-04-03', 200000000, 8000000))), evaluations: [{ asOfDate: '2026-03-15', expected: { 'month.investedThisMonthVnd': 17000000, 'holdings.ETH.qty': 36000000, 'months.2026-04.planInvestedVnd': 5000000, 'month.carryOutVnd': null, flags: ['FUTURE_DATED_EVENTS'] } }] },
  { id: 'SC-12', legacy, confirmation, evaluations: [{ asOfDate: '2026-01-09', expected: { 'holdings.ETH.qty': 27500000, 'holdings.ETH.costUsdt': 660000000, 'holdings.ETH.costVnd': null, 'usdt.qty': 340000000, 'usdt.costVnd': null, flags: ['UNKNOWN_VND_BASIS'] } }] }
];
module.exports = { scenarios, copy, plan, state, opening, event, p2p, buy, legacy, confirmation, instant };
