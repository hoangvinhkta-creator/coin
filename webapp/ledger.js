/* CoinDCA L-1. Integer ledger; derived values never cross the durable boundary. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CoinLedger = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const SCHEMA = 'coindca.ledger/2', LIMIT = 9000000000000000;
  const clone = x => JSON.parse(JSON.stringify(x));
  const fail = message => { throw new Error(message); };
  function integer(x, nullable = false, signed = false) {
    if (x === null && nullable) return x;
    if (!Number.isSafeInteger(x) || Math.abs(x) > LIMIT || (!signed && x < 0)) fail('Số nguyên vượt miền hợp lệ');
    return x;
  }
  function exact(x) { return integer(Number(x), false, true); }
  function add(a, b) { return a === null || b === null ? null : exact(BigInt(a) + BigInt(b)); }
  function sub(a, b) { return a === null || b === null ? null : exact(BigInt(a) - BigInt(b)); }
  function round(n, d) {
    n = BigInt(n); d = BigInt(d);
    if (d <= 0n) fail('Mẫu số không dương');
    const sign = n < 0n ? -1n : 1n;
    n *= sign;
    return exact(sign * ((2n * n + d) / (2n * d)));
  }
  function portion(qty, cost, total) {
    return cost === null || total <= 0 || qty > total ? null : round(BigInt(qty) * BigInt(cost), total);
  }
  // Ratios retain their exact integer numerator/denominator; decimal conversion is display only.
  function ratio(cost, qty, scale) {
    return cost === null || qty <= 0 ? null : { numerator: (BigInt(cost) * BigInt(scale)).toString(), denominator: String(qty) };
  }
  function decimal(text, places) {
    const m = /^(\d+)(?:\.(\d+))?$/.exec(String(text).trim());
    if (!m || (m[2] || '').length > places) fail('Sai độ chính xác số nhập');
    return integer(Number(BigInt(m[1]) * 10n ** BigInt(places) + BigInt((m[2] || '').padEnd(places, '0') || '0')));
  }
  function monthValid(m) { return typeof m === 'string' && /^\d{4}-(0[1-9]|1[0-2])$/.test(m) && m.slice(0, 4) !== '0000'; }
  function daysInMonth(m) {
    const y = +m.slice(0, 4), n = +m.slice(5);
    return n === 2 ? (y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0) ? 29 : 28) : [4, 6, 9, 11].includes(n) ? 30 : 31;
  }
  function dateValid(d) {
    return typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d) && monthValid(d.slice(0, 7)) && +d.slice(8) >= 1 && +d.slice(8) <= daysInMonth(d.slice(0, 7));
  }
  function nextMonth(m) {
    const n = +m.slice(5), y = +m.slice(0, 4);
    return n === 12 ? String(y + 1).padStart(4, '0') + '-01' : m.slice(0, 5) + String(n + 1).padStart(2, '0');
  }
  function previousDay(d) {
    if (+d.slice(8) > 1) return d.slice(0, 8) + String(+d.slice(8) - 1).padStart(2, '0');
    const m = +d.slice(5, 7), y = +d.slice(0, 4);
    const p = m === 1 ? String(y - 1).padStart(4, '0') + '-12' : d.slice(0, 5) + String(m - 1).padStart(2, '0');
    return p + '-' + daysInMonth(p);
  }
  // The sole L-1 system-clock boundary. Inject an instant for reproducible acceptance tests.
  function clock(instant) {
    const now = instant === undefined ? new Date() : new Date(instant);
    return { instant: now.toISOString(), today: new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Ho_Chi_Minh', year: 'numeric', month: '2-digit', day: '2-digit' }).format(now) };
  }
  function split(amount, count) {
    integer(amount); if (!Number.isInteger(count) || count < 1 || count > 31) fail('Số mốc không hợp lệ');
    const each = round(amount, count), out = Array(count - 1).fill(each);
    out.push(exact(BigInt(amount) - BigInt(each) * BigInt(count - 1)));
    return out;
  }
  function keys(o, allowed) {
    if (!o || typeof o !== 'object' || Array.isArray(o)) fail('Thiếu đối tượng');
    for (const k of Object.keys(o)) if (!allowed.split(' ').includes(k)) fail('Trường không canonical: ' + k);
  }
  function planCheck(plan) {
    keys(plan, 'versions startMonth');
    if (!monthValid(plan.startMonth) || !Array.isArray(plan.versions)) fail('Kế hoạch không hợp lệ');
    const ids = new Set(), months = new Set();
    for (const p of plan.versions) {
      keys(p, 'id effectiveFrom asset monthlyBudgetVnd scheduleDays carryPolicy carryCapMonths');
      if (!p.id || ids.has(p.id) || !monthValid(p.effectiveFrom) || months.has(p.effectiveFrom) || p.asset !== 'ETH') fail('Version kế hoạch không hợp lệ');
      ids.add(p.id); months.add(p.effectiveFrom); integer(p.monthlyBudgetVnd);
      if (p.carryPolicy !== 'CAPPED_CARRY' || p.carryCapMonths !== 1) fail('Chỉ CAPPED_CARRY cap 1 được duyệt');
      if (!Array.isArray(p.scheduleDays) || !p.scheduleDays.length || p.scheduleDays.some((d, i, a) => !Number.isInteger(d) || d < 1 || d > 31 || (i > 0 && d <= a[i - 1]))) fail('Lịch không hợp lệ');
    }
  }
  function openingCheck(o) {
    if (o === null) return;
    keys(o, 'asOf assets usdt vnd reserveVnd note');
    if (!dateValid(o.asOf) || !Array.isArray(o.assets) || o.assets.length > 1) fail('Số dư đầu kỳ không hợp lệ');
    for (const a of o.assets) {
      keys(a, 'symbol qty costUsdt costVnd'); if (a.symbol !== 'ETH') fail('Chỉ ETH');
      integer(a.qty); integer(a.costUsdt, true); integer(a.costVnd, true);
      if (!a.qty && (a.costUsdt || a.costVnd)) fail('Giá vốn khi lượng bằng 0');
    }
    keys(o.usdt, 'qty costVnd'); integer(o.usdt.qty); integer(o.usdt.costVnd, true);
    if (!o.usdt.qty && o.usdt.costVnd) fail('Giá vốn khi pool rỗng');
    if (o.vnd) { keys(o.vnd, 'qty'); integer(o.vnd.qty); }
    if (o.reserveVnd !== undefined) integer(o.reserveVnd);
    if (typeof o.note !== 'string') fail('Thiếu ghi chú đầu kỳ');
  }
  function eventCheck(e, opening) {
    const common = 'id seq kind businessDate createdAt updatedAt note ';
    const fields = { TREASURY: 'dir vndAmount usdtAmount counterparty', TRADE: 'side symbol usdtNotional feeUsdt qty source', RESERVE: 'type vndAmount', PRICE: 'symbol priceUsdt usdVndRate' };
    if (!e || !fields[e.kind]) fail('Loại event không hợp lệ');
    keys(e, common + fields[e.kind]); integer(e.seq);
    if (!e.id || typeof e.id !== 'string' || !e.seq || !dateValid(e.businessDate)) fail('ID/seq/ngày không hợp lệ');
    if (opening && e.businessDate < opening.asOf) fail('Ngày giao dịch trước số dư đầu kỳ');
    if (typeof e.note !== 'string' || ![e.createdAt, e.updatedAt].every(s => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}T.*Z$/.test(s))) fail('Metadata không hợp lệ');
    if (e.kind === 'TREASURY') {
      if (!['VND_TO_USDT', 'USDT_TO_VND'].includes(e.dir)) fail('Chiều P2P sai');
      integer(e.vndAmount); integer(e.usdtAmount); if (!e.usdtAmount || !e.vndAmount) fail('P2P phải dương');
    } else if (e.kind === 'TRADE') {
      if (!['BUY', 'SELL'].includes(e.side) || e.symbol !== 'ETH' || !['PLAN', 'EXTRA', 'RESERVE'].includes(e.source)) fail('Trade sai');
      integer(e.qty); integer(e.usdtNotional); integer(e.feeUsdt);
      if (!e.qty || !e.usdtNotional || (e.side === 'SELL' && e.feeUsdt > e.usdtNotional)) fail('Lượng/phí không hợp lệ');
      if (e.source === 'RESERVE' && !e.note.trim()) fail('Giải ngân dự phòng cần lý do');
    } else if (e.kind === 'RESERVE') {
      if (!['CONTRIBUTE', 'WITHDRAW'].includes(e.type)) fail('Loại dự phòng sai');
      integer(e.vndAmount); if (!e.vndAmount) fail('Số tiền phải dương');
    } else {
      if (e.symbol !== 'ETH') fail('Chỉ ETH'); integer(e.priceUsdt); integer(e.usdVndRate, true);
    }
  }
  function empty(startMonth) {
    if (!monthValid(startMonth)) fail('Thiếu tháng bắt đầu');
    return { schema: SCHEMA, rev: 0, nextSeq: 1, plan: { startMonth, versions: [] }, openingPosition: null, events: [] };
  }
  function canonical(input) {
    const s = clone(input); delete s.derivedSnapshot;
    keys(s, 'schema rev nextSeq plan openingPosition events LEGACY_ARCHIVE RESEARCH_ONLY');
    if (s.schema !== SCHEMA) fail('Schema không hỗ trợ');
    integer(s.rev); integer(s.nextSeq); planCheck(s.plan); openingCheck(s.openingPosition);
    if (!Array.isArray(s.events)) fail('Thiếu events');
    const ids = new Set(), seqs = new Set();
    for (const e of s.events) {
      eventCheck(e, s.openingPosition);
      if (ids.has(e.id) || seqs.has(e.seq) || e.seq >= s.nextSeq) fail('ID/seq trùng hoặc high watermark sai');
      ids.add(e.id); seqs.add(e.seq);
    }
    return s;
  }
  function derive(openingPosition, plan, events, asOfDate) {
    openingCheck(openingPosition); planCheck(plan); if (!dateValid(asOfDate)) fail('asOfDate sai');
    const ordered = events.slice().sort((a, b) => a.businessDate.localeCompare(b.businessDate) || a.seq - b.seq);
    const ids = new Set(), seqs = new Set();
    for (const e of ordered) { eventCheck(e, openingPosition); if (ids.has(e.id) || seqs.has(e.seq)) fail('Event trùng'); ids.add(e.id); seqs.add(e.seq); }
    const o = openingPosition, eth = clone(o && o.assets[0] || { qty: 0, costUsdt: 0, costVnd: 0 });
    delete eth.symbol;
    const usdt = clone(o ? o.usdt : { qty: 0, costVnd: 0 });
    let vnd = o && o.vnd ? o.vnd.qty : 0, reserve = o && o.reserveVnd !== undefined ? o.reserveVnd : 0, realizedFxVnd = 0;
    const flags = new Set(), eventEffects = {}, invested = {}, planSpent = {};
    let firstOffendingEventId = null, firstOffendingBusinessDate = null;
    function inconsistent(e) { flags.add('LEDGER_INCONSISTENT'); if (!firstOffendingEventId) { firstOffendingEventId = e.id; firstOffendingBusinessDate = e.businessDate; } }
    function release(out, e) {
      const relieved = portion(out, usdt.costVnd, usdt.qty);
      if (out > usdt.qty) inconsistent(e);
      usdt.qty = sub(usdt.qty, out); usdt.costVnd = sub(usdt.costVnd, relieved);
      if (usdt.qty === 0) { realizedFxVnd = add(realizedFxVnd, usdt.costVnd); usdt.costVnd = 0; }
      return relieved;
    }
    for (const e of ordered) {
      const m = e.businessDate.slice(0, 7); let relieved = 0;
      if (e.businessDate > asOfDate) flags.add('FUTURE_DATED_EVENTS');
      if (e.kind === 'TREASURY') {
        if (e.dir === 'VND_TO_USDT') { usdt.qty = add(usdt.qty, e.usdtAmount); usdt.costVnd = add(usdt.costVnd, e.vndAmount); vnd = sub(vnd, e.vndAmount); }
        else { relieved = release(e.usdtAmount, e); vnd = add(vnd, e.vndAmount); realizedFxVnd = add(realizedFxVnd, sub(e.vndAmount, relieved)); }
      } else if (e.kind === 'TRADE' && e.side === 'BUY') {
        const out = add(e.usdtNotional, e.feeUsdt); relieved = release(out, e);
        eth.qty = add(eth.qty, e.qty); eth.costUsdt = add(eth.costUsdt, out); eth.costVnd = add(eth.costVnd, relieved);
        invested[m] = add(invested[m] === undefined ? 0 : invested[m], relieved);
        if (e.source === 'PLAN') planSpent[m] = add(planSpent[m] === undefined ? 0 : planSpent[m], relieved);
        if (e.source === 'RESERVE') reserve = sub(reserve, relieved);
      } else if (e.kind === 'TRADE') {
        const proceeds = sub(e.usdtNotional, e.feeUsdt), basis = usdt.costVnd === null || usdt.qty <= 0 ? null : round(BigInt(proceeds) * BigInt(usdt.costVnd), usdt.qty);
        const relievedUsdt = portion(e.qty, eth.costUsdt, eth.qty); relieved = portion(e.qty, eth.costVnd, eth.qty);
        if (e.qty > eth.qty) inconsistent(e);
        eth.qty = sub(eth.qty, e.qty); eth.costUsdt = sub(eth.costUsdt, relievedUsdt); eth.costVnd = sub(eth.costVnd, relieved);
        if (eth.qty === 0) { eth.costUsdt = 0; eth.costVnd = 0; }
        usdt.qty = add(usdt.qty, proceeds); usdt.costVnd = add(usdt.costVnd, basis);
      } else if (e.kind === 'RESERVE') reserve = e.type === 'CONTRIBUTE' ? add(reserve, e.vndAmount) : sub(reserve, e.vndAmount);
      if (reserve !== null && reserve < 0) inconsistent(e);
      eventEffects[e.id] = { vndRelieved: relieved, usdtQty: usdt.qty, usdtCostVnd: usdt.costVnd, ethQty: eth.qty };
    }
    const currentMonth = asOfDate.slice(0, 7), months = {};
    const versions = plan.versions.slice().sort((a, b) => a.effectiveFrom.localeCompare(b.effectiveFrom));
    const versionFor = m => m < plan.startMonth ? null : versions.filter(p => p.effectiveFrom <= m).slice(-1)[0];
    let start = plan.startMonth;
    if (o && o.asOf.slice(0, 7) > start) start = o.asOf.slice(0, 7);
    let carry = 0;
    function buildMonth(m, incoming) {
      const p = versionFor(m), spent = planSpent[m] === undefined ? 0 : planSpent[m];
      const budget = p ? p.monthlyBudgetVnd : null, cin = !p || incoming === null ? null : Math.min(incoming, budget);
      const planned = add(budget, cin), remaining = planned === null || spent === null ? null : Math.max(0, sub(planned, spent));
      return { monthlyBudgetVnd: budget, carryInVnd: cin, plannedBudgetVnd: planned, investedThisMonthVnd: invested[m] === undefined ? 0 : invested[m], planInvestedVnd: spent, remainingPlannedBudgetVnd: remaining, carryOutVnd: m < currentMonth ? remaining : null };
    }
    for (let m = start; m <= currentMonth; m = nextMonth(m)) {
      months[m] = buildMonth(m, carry); carry = months[m].carryOutVnd;
    }
    const month = months[currentMonth] || buildMonth(currentMonth, 0);
    // No future month can finalize carry or consume current-month budget.
    for (const m of Object.keys(invested).filter(m => m > currentMonth).sort()) months[m] = buildMonth(m, null);
    let nextPlannedDate = null, nextPlannedAmountVnd = null, plannedPerSlot = [];
    const p = versionFor(currentMonth);
    function slots(p, m) { return [...new Set(p.scheduleDays.map(d => Math.min(d, daysInMonth(m))))].map(d => m + '-' + String(d).padStart(2, '0')); }
    if (p) {
      const dates = slots(p, currentMonth); plannedPerSlot = split(p.monthlyBudgetVnd, dates.length);
      let cumulative = 0;
      for (let i = 0; i < dates.length; i++) {
        cumulative = add(cumulative, plannedPerSlot[i]);
        if (dates[i] >= asOfDate && month.planInvestedVnd !== null && cumulative > month.planInvestedVnd) {
          nextPlannedDate = dates[i]; nextPlannedAmountVnd = month.remainingPlannedBudgetVnd === null ? null : Math.min(Math.max(0, sub(cumulative, month.planInvestedVnd)), month.remainingPlannedBudgetVnd); break;
        }
      }
      if (!nextPlannedDate && month.planInvestedVnd !== null) {
        const nm = nextMonth(currentMonth), np = versionFor(nm);
        if (np) { const dates = slots(np, nm); nextPlannedDate = dates[0]; const cumulative = split(np.monthlyBudgetVnd, dates.length)[0]; nextPlannedAmountVnd = month.remainingPlannedBudgetVnd === null ? null : Math.min(Math.max(0, sub(cumulative, month.planInvestedVnd)), month.remainingPlannedBudgetVnd); }
      }
    }
    Object.assign(month, { nextPlannedDate, nextPlannedAmountVnd, plannedPerSlot });
    eth.avgCostUsdt = ratio(eth.costUsdt, eth.qty, 100000000); eth.avgCostVnd = ratio(eth.costVnd, eth.qty, 100000000);
    usdt.avgVnd = ratio(usdt.costVnd, usdt.qty, 1000000);
    if ([usdt.costVnd, eth.costVnd, reserve, ...Object.values(invested)].some(x => x === null)) flags.add('UNKNOWN_VND_BASIS');
    const mark = ordered.filter(e => e.kind === 'PRICE' && e.businessDate <= asOfDate).slice(-1)[0];
    const valuation = mark && mark.businessDate >= previousDay(asOfDate) ? { usdt: round(BigInt(eth.qty) * BigInt(mark.priceUsdt), 100000000), businessDate: mark.businessDate } : null;
    return { holdings: { ETH: eth }, usdt, vnd: { balance: vnd }, reserve: { balance: reserve }, currentMonth, month, months, eventEffects, realizedFxVnd, valuation, flags: [...flags].sort(), firstOffendingEventId, firstOffendingBusinessDate };
  }
  function update(state, action, meta) {
    const s = canonical(state);
    if (action.type === 'opening') s.openingPosition = clone(action.value);
    else if (action.type === 'plan') s.plan = clone(action.value);
    else if (action.type === 'delete') { if (!s.events.some(e => e.id === action.id)) fail('Event không tồn tại'); s.events = s.events.filter(e => e.id !== action.id); }
    else if (action.type === 'event') {
      const old = action.id ? s.events.find(e => e.id === action.id) : null;
      if (action.id && !old) fail('Event không tồn tại');
      const e = Object.assign({}, action.value, { id: old ? old.id : meta.id, seq: old ? old.seq : s.nextSeq++, createdAt: old ? old.createdAt : meta.instant, updatedAt: meta.instant });
      if (old) s.events[s.events.indexOf(old)] = e; else s.events.push(e);
    } else fail('Thao tác không hỗ trợ');
    return canonical(s);
  }
  function migrate(legacy, confirmation, meta, seed) {
    if (!legacy || legacy.schema !== 'ethdca.tracker/1') fail('Schema legacy không hỗ trợ');
    const errors = [], deltas = {}; let candidate = null;
    try {
      if (!confirmation || !['opening', 'ignore'].includes(confirmation.contributions)) fail('M-1: cần chọn cách xử lý contribution');
      if ((legacy.ladders || []).some(l => (l.zones || []).some(z => z.filled_vnd > 0))) fail('M-4: zone đã phát tác');
      candidate = empty(confirmation.plan.startMonth); candidate.plan = clone(confirmation.plan); candidate.openingPosition = clone(confirmation.openingPosition);
      const rows = (legacy.p2p || []).map((r, i) => ({ r, key: 'p2p[' + i + ']', kind: 'TREASURY' })).concat((legacy.trades || []).map((r, i) => ({ r, key: 'trades[' + i + ']', kind: 'TRADE' })));
      for (const { r, key, kind } of rows) {
        const c = confirmation.dates && confirmation.dates[key];
        if (!c || !dateValid(c.businessDate) || !Number.isSafeInteger(c.order)) fail('M-1: xác nhận ngày/thứ tự ' + key);
      }
      rows.sort((a, b) => confirmation.dates[a.key].order - confirmation.dates[b.key].order);
      if (new Set(rows.map(x => confirmation.dates[x.key].order)).size !== rows.length) fail('M-1: thứ tự bị trùng');
      for (const { r, key, kind } of rows) {
        const seq = candidate.nextSeq++, base = { id: meta.id + '-' + seq, seq, kind, businessDate: confirmation.dates[key].businessDate, createdAt: meta.instant, updatedAt: meta.instant, note: 'Migration ' + key };
        const scaled = (n, scale) => integer(Math.round(n * scale)); // explicit legacy float quantization, reported below
        const e = kind === 'TREASURY' ? Object.assign(base, { dir: r.dir, vndAmount: scaled(r.dir === 'VND_TO_USDT' ? r.vnd + (r.fee || 0) : r.vnd - (r.fee || 0), 1), usdtAmount: scaled(r.usdt, 1000000) }) : Object.assign(base, { side: 'BUY', symbol: 'ETH', usdtNotional: scaled(r.usdt, 1000000), feeUsdt: scaled(r.fee || 0, 1000000), qty: scaled(r.eth, 100000000), source: 'EXTRA' });
        candidate.events.push(e);
      }
      candidate = canonical(candidate);
      const d = derive(candidate.openingPosition, candidate.plan, candidate.events, meta.today);
      if (Object.values(d.eventEffects).some(e => e.usdtQty < 0 || e.ethQty < 0)) fail('M-2: âm số lượng trong replay');
      const comparisons = { eth: [d.holdings.ETH.qty, legacy.eth, 100000000], usdt: [d.usdt.qty, legacy.treasury.usdt, 1000000], vnd: [d.vnd.balance, legacy.treasury.vnd, 1], costUsdt: [d.holdings.ETH.costUsdt, legacy.costUsdt, 1000000] };
      for (const [k, [actual, old, scale]] of Object.entries(comparisons)) {
        if (actual === null || typeof old !== 'number' || !Number.isFinite(old)) fail('M-3: thiếu oracle ' + k);
        deltas[k] = { deltaUnits: actual - old * scale, legacyRounded: Math.round(old * scale), actual };
        if (Math.abs(deltas[k].deltaUnits) > 1) errors.push('M-3: lệch ' + k);
      }
      deltas.costVnd = { actual: d.holdings.ETH.costVnd, legacy: legacy.costVnd, deltaVnd: d.holdings.ETH.costVnd === null ? null : d.holdings.ETH.costVnd - legacy.costVnd };
      if (errors.length) return { ok: false, errors, deltas };
      candidate.LEGACY_ARCHIVE = { label: 'LEGACY_ARCHIVE — READ ONLY', raw: clone(legacy) };
      candidate.RESEARCH_ONLY = { extraDays: clone(legacy.extraDays || []), history: clone(seed && seed.history || []) };
      return { ok: true, state: candidate, deltas, warnings: d.flags.includes('UNKNOWN_VND_BASIS') ? ['W-1', 'UNKNOWN_VND_BASIS'] : [] };
    } catch (e) { errors.push(e.message); return { ok: false, errors, deltas }; }
  }
  // Hooks are production snapshot/confirmation/persistence adapters, not an alternate write path.
  async function destructive(current, operation, hooks) {
    await hooks.snapshot(clone(current));
    if (!await hooks.confirm()) return { ok: false, cancelled: true };
    const result = await operation();
    if (!result.ok) return result;
    await hooks.commit(canonical(result.state));
    return result;
  }
  return Object.freeze({ SCHEMA, LIMIT, clone, integer, round, decimal, ratio, clock, split, dateValid, nextMonth, empty, canonical, derive, update, migrate, destructive });
});
