/* E2 INDEPENDENT — reviewer-controlled restore/derive semantics against real webapp/ledger.js.
   Reviewer-chosen synthetic state; no implementer fixture, no implementer assertion reused. */
const fs = require('fs');
const path = require('path').join(__dirname, '..', '..', '..', '..', 'webapp', 'ledger.js');
let L;
(function () {
  const src = fs.readFileSync(path, 'utf8');
  const mod = { exports: {} };
  const define = (f) => { L = f(); };
  define.amd = true;
  new Function('module', 'exports', 'define', 'window', 'globalThis', src)(mod, mod.exports, define, {}, globalThis);
  if (!L) L = mod.exports;
})();

let pass = 0, fail = 0;
const check = (label, cond, extra) => {
  if (cond) { pass++; console.log('  ok   | ' + label); }
  else { fail++; console.log('  FAIL | ' + label + (extra ? ' :: ' + extra : '')); }
};
console.log('ledger.js SCHEMA = ' + L.SCHEMA);

// ---- Reviewer-built synthetic canonical ledger (scaled ints: VND x1, USDT x1e6, ETH x1e8) ----
let n = 0;
const meta = () => ({ id: 'e2-' + (++n), today: '2026-04-15', instant: '2026-04-15T09:00:00.000Z' });
let s = L.empty('2026-03');
s = L.update(s, { type: 'opening', value: {
  asOf: '2026-03-01',
  assets: [{ symbol: 'ETH', qty: 125000000, costUsdt: 3100500000, costVnd: 81000000 }],
  usdt: { qty: 540250000, costVnd: 13600000 },
  vnd: { qty: 27500000 }, reserveVnd: 4000000, note: 'e2 synthetic opening' } }, meta());
s = L.update(s, { type: 'plan', value: { startMonth: '2026-03', versions: [
  { id: 'e2-plan-v1', effectiveFrom: '2026-03', asset: 'ETH', monthlyBudgetVnd: 9000000,
    scheduleDays: [3, 17], carryPolicy: 'CAPPED_CARRY', carryCapMonths: 1 } ] } }, meta());
s = L.update(s, { type: 'event', value: { kind: 'TREASURY', businessDate: '2026-03-04', note: 'e2 p2p',
  dir: 'VND_TO_USDT', vndAmount: 8500000, usdtAmount: 331250000, counterparty: 'e2-cp' } }, meta());
s = L.update(s, { type: 'event', value: { kind: 'TRADE', businessDate: '2026-03-05', note: 'e2 buy',
  side: 'BUY', symbol: 'ETH', usdtNotional: 300000000, feeUsdt: 300000, qty: 11500000, source: 'PLAN' } }, meta());
s = L.update(s, { type: 'event', value: { kind: 'RESERVE', businessDate: '2026-03-06', note: 'e2 reserve',
  type: 'CONTRIBUTE', vndAmount: 1500000 } }, meta());
s = L.update(s, { type: 'event', value: { kind: 'PRICE', businessDate: '2026-04-01', note: 'e2 price',
  symbol: 'ETH', priceUsdt: 2900000000, usdVndRate: 26000 } }, meta());
s = L.canonical(s);

const D1 = L.derive(s.openingPosition, s.plan, s.events, '2026-04-15');
console.log('\n--- Reviewer synthetic ledger derived once (authoritative baseline) ---');
console.log('  ETH qty=' + D1.holdings.ETH.qty + '  costVnd=' + D1.holdings.ETH.costVnd +
            '  USDT qty=' + D1.usdt.qty + '  VND=' + D1.vnd.balance + '  reserve=' + D1.reserve.balance);

console.log('\n--- A. Backup round-trip is bit-exact and derive() is identical ---');
const backup = { schemaVersion: s.schema, exportedAt: '2026-04-15T09:00:00.000Z', state: s, seed: null,
  derivedSnapshot: { _meta: 'INFORMATIONAL — NOT IMPORTED', ethQty: '999999', vndBalance: '999999999' } };
const wire = JSON.parse(JSON.stringify(backup));                 // serialise exactly as a file would
const restored = L.canonical(wire.state);
check('restored canonical state is byte-identical to original', JSON.stringify(restored) === JSON.stringify(s));
const D2 = L.derive(restored.openingPosition, restored.plan, restored.events, '2026-04-15');
check('derive() after restore is byte-identical (tolerance 0)', JSON.stringify(D2) === JSON.stringify(D1));

console.log('\n--- B. derivedSnapshot can never become restore authority ---');
const poisoned = JSON.parse(JSON.stringify(s));
poisoned.derivedSnapshot = { ethQty: 999999999, vndBalance: 999999999 };
const cleaned = L.canonical(poisoned);
check('canonical() drops derivedSnapshot from restored state', cleaned.derivedSnapshot === undefined);
check('state with derivedSnapshot restores byte-identically', JSON.stringify(cleaned) === JSON.stringify(s));
const D3 = L.derive(cleaned.openingPosition, cleaned.plan, cleaned.events, '2026-04-15');
check('poisoned backup derives the SAME money as clean backup', JSON.stringify(D3) === JSON.stringify(D1));
const hardReject = (label, mutate) => {
  const bad = JSON.parse(JSON.stringify(s)); mutate(bad);
  let threw = false; try { L.canonical(bad); } catch (e) { threw = true; }
  check(label, threw);
};
hardReject('injected top-level `holdings` is REJECTED (not silently kept)', b => { b.holdings = { ETH: { qty: 999999999 } }; });
hardReject('injected top-level `derived` is REJECTED', b => { b.derived = { vnd: 999999999 }; });

console.log('\n--- C. Malformed payloads are rejected by the SAME T-12 validation ---');
const rejects = (label, mutate) => {
  const bad = JSON.parse(JSON.stringify(s));
  mutate(bad);
  let threw = false;
  try { const c = L.canonical(bad); L.derive(c.openingPosition, c.plan, c.events, '2026-04-15'); } catch (e) { threw = true; }
  check(label, threw);
};
rejects('wrong schema string rejected',            b => { b.schema = 'coindca.ledger/999'; });
rejects('missing events array rejected',           b => { delete b.events; });
rejects('out-of-domain numeric field rejected',     b => { b.events[0].vndAmount = 9e18; });
rejects('event with unknown kind rejected',        b => { b.events[0].kind = 'SELL_ETH_SECRET'; });
  rejects('non-canonical extra field rejected',      b => { b.events[0].bonusVnd = 500000; });
rejects('non-object payload rejected',             b => { b.openingPosition = 'not-an-object'; });

console.log('\n--- D. Cancelled/failed restore performs no mutation ---');
(async () => {
  let committed = null, snapped = null;
  const r1 = await L.destructive(s, () => ({ ok: true, state: L.empty('2026-05') }),
    { snapshot: v => { snapped = v; }, commit: v => { committed = v; }, confirm: () => false });
  check('cancelled confirm -> ok:false, cancelled:true', r1.ok === false && r1.cancelled === true);
  check('cancelled confirm -> NOTHING committed', committed === null);
  check('snapshot taken BEFORE confirm (recovery always possible)', snapped !== null && JSON.stringify(snapped) === JSON.stringify(s));

  committed = null;
  const r2 = await L.destructive(s, () => ({ ok: false, errors: ['validate failed'] }),
    { snapshot: () => {}, commit: v => { committed = v; }, confirm: () => true });
  check('failed operation -> NOTHING committed', r2.ok === false && committed === null);

  console.log('\n=== E2 INDEPENDENT RESTORE SEMANTICS: pass=' + pass + ' fail=' + fail + ' ===');
  process.exit(fail === 0 ? 0 : 1);
})();
