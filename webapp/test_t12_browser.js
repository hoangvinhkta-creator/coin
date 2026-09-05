/* E1 production reachability P1..P6: actual built page + SDK + emulator REST, only synthetic data. */
const A = require('assert/strict'), fs = require('fs'), os = require('os'), path = require('path');
const { chromium } = require('playwright'), H = require('./test_firebase_harness'), F = require('./test_t12_fixtures'), L = require('./ledger');
const results = [], record = (name, detail) => { results.push({ name, status: 'PASS', detail }); console.log('PASS ' + name + ' ' + detail); };
const value = (n, places = 0) => n === null ? '' : (n / 10 ** places).toFixed(places);
async function fill(p, id, x) { await p.locator('#' + id).fill(String(x)); }
async function save(p, id) {
  await p.click('#' + id); await H.waitSaved(p);
  const m = await p.textContent('#l1Message'); A.doesNotMatch(m, /không hợp lệ|không hỗ trợ|thiếu|Sai|trước số dư/i);
  return H.readState(p);
}
async function openDetails(p) { await p.locator('#l1Root details').evaluateAll(ds => ds.forEach(d => d.open = true)); }
async function setOpening(p, o) {
  await openDetails(p); await fill(p, 'l1OpeningDate', o.asOf);
  const a = o.assets[0] || { qty: 0, costUsdt: 0, costVnd: 0 };
  for (const [id, x, places] of [['l1Eth', a.qty, 8], ['l1EthCostUsdt', a.costUsdt, 6], ['l1EthCostVnd', a.costVnd, 0], ['l1Usdt', o.usdt.qty, 6], ['l1UsdtCost', o.usdt.costVnd, 0], ['l1Vnd', o.vnd.qty, 0], ['l1Reserve', o.reserveVnd, 0]]) await fill(p, id, value(x, places));
  await fill(p, 'l1OpeningNote', o.note);
}
async function setPlan(p, start = '2026-01') {
  await openDetails(p); await fill(p, 'l1StartMonth', start); await fill(p, 'l1Effective', start); await fill(p, 'l1Budget', 20000000); await fill(p, 'l1Days', '3,13,23');
}
async function enter(p, e) {
  await p.selectOption('#l1Kind', e.kind); await fill(p, 'l1Date', e.businessDate); await fill(p, 'l1Note', e.note);
  if (e.kind === 'TREASURY') { await p.selectOption('#l1Dir', e.dir); await fill(p, 'l1P2pVnd', e.vndAmount); await fill(p, 'l1P2pUsdt', value(e.usdtAmount, 6)); }
  if (e.kind === 'TRADE') { await p.selectOption('#l1Side', e.side); await p.selectOption('#l1Source', e.source); for (const [id, x, n] of [['l1Notional', e.usdtNotional, 6], ['l1Fee', e.feeUsdt, 6], ['l1Qty', e.qty, 8]]) await fill(p, id, value(x, n)); }
  if (e.kind === 'RESERVE') { await p.selectOption('#l1ReserveType', e.type); await fill(p, 'l1ReserveAmount', e.vndAmount); }
  if (e.kind === 'PRICE') { await fill(p, 'l1Price', value(e.priceUsdt, 6)); await fill(p, 'l1MarkRate', value(e.usdVndRate)); }
  return save(p, 'l1SaveEvent');
}
async function summary(p) { return p.locator('#l1Summary .stat').evaluateAll(xs => Object.fromEntries(xs.map(x => [x.querySelector('small').textContent, x.querySelector('div').textContent]))); }
async function snapshotClick(p, selector) { const dl = p.waitForEvent('download'); await p.click(selector); const f = await dl; const raw = JSON.parse(fs.readFileSync(await f.path(), 'utf8')); return raw; }
(async () => {
  const stop = await H.ensureEmulators(); const b = await chromium.launch({ executablePath: H.CHROMIUM }); let ctx;
  try {
    const opened = await H.newPage(b, { seed: false }); ctx = opened.ctx; const p = opened.p;
    await p.clock.install({ time: new Date('2026-03-21T05:00:00Z') }); await p.reload(); await H.waitPhase(p, 'ONLINE');
    await setPlan(p); await save(p, 'l1SavePlan'); await setOpening(p, F.opening); await save(p, 'l1SaveOpening');
    const input = F.scenarios[3].state.events.concat(F.event(5, '2026-03-02', { kind: 'RESERVE', type: 'CONTRIBUTE', vndAmount: 10000000 }), F.buy(6, '2026-03-17', 100000000, 4000000, 'EXTRA'), F.buy(7, '2026-03-20', 100000000, 4000000, 'RESERVE', 0, 'giải ngân tổng hợp'), F.event(8, '2026-03-21', { kind: 'PRICE', symbol: 'ETH', priceUsdt: 2400000000, usdVndRate: null }));
    let s; for (const e of input) s = await enter(p, e);
    A.equal(s.events.length, 8); A.ok(s.openingPosition); record('P-1/P-2', 'Bundle thật; opening + 8 event qua UI; 2 treasury, 2 PLAN, EXTRA, RESERVE contribution/buy, PRICE.');
    const edit = s.events.find(e => e.seq === 2), deleted = s.events.find(e => e.seq === 3);
    await p.click('button[data-id="' + edit.id + '"][data-action="edit"]'); await fill(p, 'l1Qty', '0.24'); s = await save(p, 'l1SaveEvent');
    A.equal(s.events.find(e => e.id === edit.id).seq, edit.seq);
    const beforeDelete = JSON.stringify(s); const snap = await snapshotClick(p, 'button[data-id="' + deleted.id + '"][data-action="delete"]'); await H.waitSaved(p);
    A.deepEqual(snap.state, JSON.parse(beforeDelete));
    await p.waitForFunction(id => !JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')).events.some(e => e.id === id), deleted.id, { timeout: 5000 });
    await H.waitSaved(p); A.equal((await H.readState(p)).events.some(e => e.id === deleted.id), false);
    s = await enter(p, F.buy(9, '2026-02-04', 50000000, 2000000));
    record('P-3', 'Sửa giữ id/seq; hard delete có snapshot; nhập muộn ngày 04/02 khi thao tác 21/03.');
    // Hand oracle: after deletion, 599.4 USDT @25.500; late BUY50=>1.275.000, Feb BUY500=>12.750.000.
    // March EXTRA100 + RESERVE100 exceed remaining49.4; first March BUY unknown, quantity preserved.
    // Use a second explicit treasury event to restore known coverage BEFORE March spend, via normal UI.
    s = await enter(p, F.p2p(10, '2026-03-01', 10000000, 400000000));
    // Exact hand oracle: March pool449.4/C11259700 after P2P; each BUY100 releases2505496. ETH(.5+.24+.02+.2+.04+.04)=1.04;
    // ETH costUSDT=1200+600.6+50+500+100+100=2550.6; costVND=30m+15315300+1275000+12750000+5010992=64351292.
    const oracle = { 'holdings.ETH.qty': 104000000, 'holdings.ETH.costUsdt': 2550600000, 'holdings.ETH.costVnd': 64351292, 'usdt.qty': 249400000, 'usdt.costVnd': 6248708, 'reserve.balance': 7494504, 'month.monthlyBudgetVnd': 20000000, 'month.carryInVnd': 10659700, 'month.plannedBudgetVnd': 30659700, 'month.investedThisMonthVnd': 5010992, 'month.planInvestedVnd': 0, 'month.remainingPlannedBudgetVnd': 30659700, 'month.nextPlannedDate': '2026-03-23', 'month.nextPlannedAmountVnd': 20000000 };
    const d = L.derive(s.openingPosition, s.plan, s.events, '2026-03-21'); for (const [key, n] of Object.entries(oracle)) A.deepEqual(key.split('.').reduce((a, k) => a[k], d), n, key);
    const displayed = await summary(p);
    for (const [label, expected] of Object.entries({ 'Ngân sách tháng': '20.000.000', 'Carry từ tháng trước': '10.659.700', 'Ngân sách gồm carry': '30.659.700', 'Đã đầu tư': '5.010.992', 'Theo kế hoạch': '0', 'Còn lại theo kế hoạch': '30.659.700', 'Dự phòng': '7.494.504', ETH: '1,04', USDT: '249,4', 'Giá vốn pool USDT (VND)': '6.248.708' })) A.equal(displayed[label], expected, label);
    A.equal(displayed['Giá vốn TB ETH (USDT)'], (2550.6 / 1.04).toLocaleString('vi-VN', { maximumFractionDigits: 8 }));
    A.equal(displayed['Giá vốn TB ETH (VND)'], (64351292 / 1.04).toLocaleString('vi-VN', { maximumFractionDigits: 8 }));
    record('P-4', 'Server ACK mỗi thao tác; REST ethdca/state bit-exact với mirror; oracle số nguyên tolerance=0.');
    await p.reload(); await H.waitPhase(p, 'ONLINE'); A.deepEqual(await H.readState(p), s); A.deepEqual(await summary(p), displayed);
    A.equal(await p.inputValue('#l1OpeningDate'), F.opening.asOf); A.equal(await p.inputValue('#l1Eth'), '0.50000000'); A.equal(await p.inputValue('#l1Effective'), '2026-01');
    record('P-5', 'Reload tự replay; dashboard/holdings/giá vốn khớp oracle tính tay.');
    A.deepEqual(L.canonical(s), s); A.deepEqual(Object.keys(s).sort(), ['events', 'nextSeq', 'openingPosition', 'plan', 'rev', 'schema']);
    record('P-6', 'Payload durable allowlist canonical; không derived truth.');
    await openDetails(p); const file = await snapshotClick(p, '#l1Export'); A.deepEqual(file.state, s);
    const exportInput = { state: s, derivedSnapshot: { costVnd: 42 } }; exportInput.state.derivedSnapshot = { holdings: 0 };
    const beforeImport = F.copy(s); delete beforeImport.derivedSnapshot;
    const dl = p.waitForEvent('download'); await p.setInputFiles('#l1Import', { name: 'synthetic.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(exportInput)) });
    const importedSnapshot = JSON.parse(fs.readFileSync(await (await dl).path(), 'utf8')); A.deepEqual(importedSnapshot.state, beforeImport); await H.waitSaved(p);
    const imported = await H.readState(p); A.equal('derivedSnapshot' in imported, false); A.deepEqual(await summary(p), displayed);
    record('INV-1/14 import', 'Snapshot đầy đủ trước import; derivedSnapshot bị bỏ; tiền không trôi.');
    await p.screenshot({ path: path.join(os.tmpdir(), 't12-browser.png'), fullPage: true });
    // Fresh load of a legacy document: never rewritten before explicit migration.
    await H.putDoc('state', F.legacy); await p.evaluate(() => localStorage.removeItem('ethdca-tracker-state-v1')); await p.reload(); await H.waitPhase(p, 'ONLINE');
    A.deepEqual(await H.getDoc('state'), F.legacy); await setPlan(p); await setOpening(p, F.confirmation.openingPosition);
    await p.selectOption('#l1Contributions', 'ignore');
    for (let i = 0; i < 4; i++) await fill(p, 'l1MigrationDate' + i, F.confirmation.dates['trades[' + i + ']'].businessDate);
    const migrationSnapshot = await snapshotClick(p, '#l1Migrate'); A.deepEqual(migrationSnapshot.state, F.legacy); await H.waitSaved(p);
    A.match(await p.textContent('#l1Message'), /trades\[3\].*USDT/);
    const migrated = await H.readState(p); A.equal(migrated.schema, L.SCHEMA); A.deepEqual(migrated.LEGACY_ARCHIVE.raw, F.legacy); A.match(await p.textContent('#l1Flags'), /UNKNOWN_VND_BASIS/);
    A.equal((await summary(p))['Giá vốn TB ETH (VND)'], '—'); await p.reload(); await H.waitPhase(p, 'ONLINE'); A.deepEqual(await H.readState(p), migrated);
    record('SC-12 production', 'Legacy read-only → xác nhận ngày → snapshot → migration W-1 → server ACK → reload, UNKNOWN thấy được.');
    for (const code of ['M-1', 'M-2', 'M-3', 'M-4']) {
      const raw = F.copy(F.legacy), opening = F.copy(F.confirmation.openingPosition);
      if (code === 'M-2') opening.usdt.qty = 0;
      if (code === 'M-3') raw.eth = 1;
      if (code === 'M-4') raw.ladders = [{ zones: [{ target_vnd: 1, target_price: 1, filled_vnd: 1 }] }];
      await H.putDoc('state', raw);
      await p.evaluate(() => { localStorage.removeItem('ethdca-tracker-state-v1'); localStorage.removeItem('ethdca-tracker-diverged-v1'); });
      await p.reload(); await H.waitPhase(p, 'ONLINE'); await setPlan(p); await setOpening(p, opening);
      await p.selectOption('#l1Contributions', 'ignore');
      for (let i = 0; i < (code === 'M-1' ? 3 : 4); i++) await fill(p, 'l1MigrationDate' + i, F.confirmation.dates['trades[' + i + ']'].businessDate);
      const captured = await snapshotClick(p, '#l1Migrate'); A.deepEqual(captured.state, raw);
      await p.waitForFunction(code => document.getElementById('l1Message').textContent.includes(code), code);
      A.deepEqual(await H.getDoc('state'), raw); record('Migration ' + code, 'Snapshot trước lỗi, source/durable không đổi một byte canonical.');
    }
    await H.putDoc('state', migrated); await p.evaluate(() => localStorage.clear()); await p.reload(); await H.waitPhase(p, 'ONLINE'); await openDetails(p);
    p.removeAllListeners('dialog'); p.on('dialog', dialog => dialog.dismiss());
    const cancelledSnapshot = await snapshotClick(p, '#l1Wipe'); A.deepEqual(cancelledSnapshot.state, migrated);
    await p.waitForFunction(() => document.getElementById('l1Message').textContent.includes('Đã hủy'));
    A.deepEqual(await H.getDoc('state'), migrated); p.removeAllListeners('dialog'); p.on('dialog', dialog => dialog.accept());
    record('INV-14 hủy wipe', 'Hủy sau snapshot vẫn giữ toàn bộ durable.');
    const offlineContext = await b.newContext();
    await H.prepareContext(offlineContext, H.emulatorConfig({ emulator: { auth: 'http://127.0.0.1:9099', firestoreHost: '127.0.0.1', firestorePort: 1 } }));
    await offlineContext.addInitScript(state => localStorage.setItem('ethdca-tracker-state-v1', JSON.stringify(state)), migrated);
    const offlinePage = await offlineContext.newPage(); H.attachErrors(offlinePage); await offlinePage.goto(H.baseUrl());
    await H.waitPhase(offlinePage, 'OFFLINE', 60000);
    A.deepEqual(await H.getDoc('state'), migrated); A.match(await offlinePage.textContent('#saveChip'), /KHÔNG GHI SỔ/);
    A.equal((await H.status(offlinePage)).mirrorShown, true); await offlineContext.close();
    record('Persistence offline', 'Offline chỉ xem mirror, không ghi; online reload lấy server.');
    await H.setRules('another-owner');
    await enter(p, F.p2p(9, '2026-03-21', 25000, 1000000)).catch(() => {});
    A.deepEqual(await H.getDoc('state'), migrated); A.match((await H.status(p)).lastError, /permission-denied/);
    await H.setRules(opened.uid); await p.click('#saveBtn'); await H.waitSaved(p); const retried = await H.readState(p);
    A.equal(retried.events.length, migrated.events.length + 1);
    record('Persistence rejected write/retry', 'Permission denied không báo đã lưu; REST không đổi; retry sau khôi phục rules có ACK.');
    const external = F.copy(retried); external.rev += 1; await H.putDoc('state', external);
    await enter(p, F.p2p(10, '2026-03-21', 25000, 1000000)).catch(() => {});
    A.equal((await H.status(p)).lastError, 'stale-durable'); A.deepEqual(await H.getDoc('state'), external);
    await p.reload(); await H.waitPhase(p, 'ONLINE'); A.deepEqual(await H.getDoc('state'), external);
    record('Persistence stale rev', 'Tab cũ không ghi đè server revision mới hơn.');
    const corrupt = { schema: 'unsupported/999', rev: external.rev + 1 }; await H.putDoc('state', corrupt);
    await p.reload(); await H.waitPhase(p, 'CORRUPT'); await openDetails(p);
    const rawExport = await snapshotClick(p, '#l1Export'); A.deepEqual(rawExport.state, corrupt); A.deepEqual(await H.getDoc('state'), corrupt);
    record('Persistence corrupt/version', 'Unknown schema bị khóa, xuất raw đầy đủ, không wipe/backfill.');
    await H.putDoc('state', external);
    await ctx.close(); ctx = null;
    const profile = fs.mkdtempSync(path.join(os.tmpdir(), 't12-profile-'));
    let profilePage = await H.newPersistent(chromium, profile); ctx = profilePage.ctx;
    await H.bootstrapOwner(profilePage.p); const restartUid = (await H.status(profilePage.p)).uid;
    A.deepEqual(await H.readState(profilePage.p), external); await ctx.close(); ctx = null;
    profilePage = await H.newPersistent(chromium, profile); ctx = profilePage.ctx; await H.waitPhase(profilePage.p, 'ONLINE');
    A.equal((await H.status(profilePage.p)).uid, restartUid); A.deepEqual(await H.readState(profilePage.p), external);
    record('Persistence browser restart', 'Đóng/mở Chrome cùng profile giữ Anonymous UID; load server bit-exact.');

    console.log(JSON.stringify({ results, oracle, realEventsCreated: 10, errors: opened.errs }, null, 2));
  } finally { if (ctx) await ctx.close(); await b.close(); await H.stopServer(); await stop(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
