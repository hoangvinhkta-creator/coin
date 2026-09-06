/* T-14 bước C — CHECK-T14-06 (export có timestamp + schemaVersion + chỉ nguồn sự thật),
 * CHECK-T14-07 (preview + validate TRƯỚC khi ghi), CHECK-T14-08 (backup dị dạng bị từ chối,
 * không mutate), CHECK-T14-09 (snapshot tự động trước khi ghi đè), CHECK-T14-10 (restore hợp lệ
 * tái tạo ĐÚNG trạng thái tài chính canonical). Ánh xạ C-AS-08…C-AS-11.
 * KHÔNG phải production path (PROJECT/PRODUCTION_PATHS.md §2). Dữ liệu TỔNG HỢP.
 *
 * Chạy trên app thật (app_final.html) + Firebase SDK thật + Auth/Firestore Emulator + rules thật
 * của repo. "Không mutate" được đo bằng cách so bản durable phía Firebase (đọc qua REST của
 * emulator, độc lập với SDK trong trang) TRƯỚC và SAU thao tác thất bại: phải trùng từng byte.
 * Oracle tài chính là chính `CoinLedger.derive()` (T-12) chạy trong Node trên bản durable —
 * KHÔNG dựng lại phép tính nào ở đây.
 */
const fs = require('fs');
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

const value = (n, places = 0) => (n === null ? '' : (n / 10 ** places).toFixed(places));
const fill = (p, id, x) => p.locator('#' + id).fill(String(x));
const openDetails = (p) => p.locator('#l1Root details').evaluateAll((ds) => ds.forEach((d) => { d.open = true; }));
const j = (x) => JSON.stringify(H.canon(x));
const TODAY = '2026-03-21';

async function uiSetPlan(p, start) {
  await openDetails(p);
  await fill(p, 'l1StartMonth', start); await fill(p, 'l1Effective', start);
  await fill(p, 'l1Budget', 20000000); await fill(p, 'l1Days', '3,13,23');
  await p.click('#l1SavePlan'); await H.waitSaved(p);
}
async function uiSetOpening(p, o) {
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
  await p.click('#l1SaveEvent'); await H.waitSaved(p);
}
async function dash(p) {
  return {
    cards: await p.locator('#dashMain .dcard').evaluateAll((xs) => xs.map((x) => [
      x.querySelector('.dc-label') ? x.querySelector('.dc-label').textContent : '',
      x.querySelector('.dc-value') ? x.querySelector('.dc-value').textContent : ''])),
    bottom: await p.locator('#dashBottom .stat').evaluateAll((xs) => xs.map((x) => [x.querySelector('small').textContent, x.querySelector('div').textContent])),
    summary: await p.locator('#l1Summary .stat').evaluateAll((xs) => xs.map((x) => [x.querySelector('small').textContent, x.querySelector('div').textContent])),
  };
}
const derivedOf = (s) => { const c = L.canonical(s); return L.derive(c.openingPosition, c.plan, c.events, TODAY); };

/** Thay `window.confirm` để QUAN SÁT (không mock mã app): ghi lại nội dung #l1Message tại đúng
 *  thời điểm hộp thoại bật lên -> chứng minh preview hiện TRƯỚC khi hỏi xác nhận. */
async function armConfirm(p, answer) {
  await p.evaluate((ans) => {
    window.__confirmLog = [];
    window.confirm = function (text) {
      window.__confirmLog.push({ text: text, messageAtConfirmTime: document.getElementById('l1Message').textContent });
      return ans;
    };
  }, answer);
}
const confirmLog = (p) => p.evaluate(() => window.__confirmLog || []);
/** Nạp file backup qua đúng input `#l1Import`; trả về { download|null, message }. */
async function importFile(p, name, body, expectDownload) {
  const dl = expectDownload ? p.waitForEvent('download', { timeout: 15000 }) : null;
  await p.setInputFiles('#l1Import', { name, mimeType: 'application/json', buffer: Buffer.from(body) });
  let file = null;
  if (dl) { const d = await dl; file = { name: d.suggestedFilename(), json: JSON.parse(fs.readFileSync(await d.path(), 'utf8')) }; }
  else await p.waitForTimeout(1200);          // đủ để mọi đường ghi/tải xuống kịp xảy ra nếu có
  return { file, message: (await p.textContent('#l1Message')).trim() };
}

(async () => {
  const stop = await H.ensureEmulators();
  const b = await chromium.launch({ executablePath: H.CHROMIUM });
  let ctx = null;
  try {
    const opened = await H.newPage(b, { seed: false });
    ctx = opened.ctx;
    const p = opened.p;
    await p.clock.install({ time: new Date(TODAY + 'T05:00:00Z') });
    await p.reload(); await H.waitPhase(p, 'ONLINE');

    await uiSetPlan(p, '2026-03');
    await uiSetOpening(p, F.opening);
    await uiEvent(p, F.p2p(1, '2026-03-05', 25600000, 1000000000));
    await uiEvent(p, F.buy(2, '2026-03-13', 600000000, 25000000, 'PLAN', 600000));
    await uiEvent(p, F.buy(3, '2026-03-17', 100000000, 4000000, 'EXTRA'));
    const golden = await H.getDoc('state');
    const goldenDerived = derivedOf(golden);
    const goldenDash = await dash(p);

    /* ---------- CHECK-T14-06 / C-AS-08 ---------- */
    begin('CHECK-T14-06', 'Export mang timestamp + schemaVersion + CHỈ nguồn sự thật canonical');
    await openDetails(p);
    const dl = p.waitForEvent('download');
    await p.click('#l1Export');
    const d = await dl;
    const backupName = d.suggestedFilename();
    const backup = JSON.parse(fs.readFileSync(await d.path(), 'utf8'));
    assert(/^coindca-ledger-\d{4}-\d{2}-\d{2}T[\d-]+Z\.json$/.test(backupName), 'tên file mang thời điểm xuất: ' + backupName);
    assert(backup.schemaVersion === L.SCHEMA, 'schemaVersion === CoinLedger.SCHEMA (' + backup.schemaVersion + ')');
    assert(typeof backup.exportedAt === 'string' && !Number.isNaN(Date.parse(backup.exportedAt)) && /T.*Z$/.test(backup.exportedAt),
      'exportedAt là ISO 8601 hợp lệ: ' + backup.exportedAt);
    assert(backupName === 'coindca-ledger-' + backup.exportedAt.replace(/[:.]/g, '-') + '.json',
      'timestamp trong tên file khớp CHÍNH XÁC exportedAt (không đọc đồng hồ lần thứ hai)');
    assert(j(backup.state) === j(golden), 'khối `state` khớp BIT-EXACT bản durable phía Firebase');
    assert(JSON.stringify(Object.keys(backup.state).sort()) === JSON.stringify(['events', 'nextSeq', 'openingPosition', 'plan', 'rev', 'schema']),
      'state chỉ chứa allowlist canonical — không trường dẫn xuất nào');
    assert(backup.derivedSnapshot && backup.derivedSnapshot._meta === 'INFORMATIONAL — NOT IMPORTED',
      'khối tham khảo mang nhãn `_meta: "INFORMATIONAL — NOT IMPORTED"`');
    assert(backup.derivedSnapshot.holdings.ETH.qty === goldenDerived.holdings.ETH.qty, 'khối tham khảo đúng số liệu derive() hiện tại (chỉ để người đọc)');
    end();

    /* ---------- CHECK-T14-08 / C-AS-10 — dị dạng: từ chối, KHÔNG mutate ---------- */
    begin('CHECK-T14-08', 'Backup dị dạng -> từ chối TRƯỚC mọi mutation bền; state hiện tại bit-for-bit không đổi');
    const lsBefore = await p.evaluate(() => localStorage.getItem('coindca-last-snapshot'));
    const mirrorBefore = await p.evaluate(() => localStorage.getItem('ethdca-tracker-state-v1'));
    const badSchema = JSON.parse(JSON.stringify(backup)); badSchema.schemaVersion = 'coindca.ledger/999'; badSchema.state.schema = 'coindca.ledger/999';
    const badField = JSON.parse(JSON.stringify(backup)); badField.state.events[0].vndAmount = 'không phải số';
    const badMissing = JSON.parse(JSON.stringify(backup)); delete badMissing.state.events;
    const cases = [
      ['schemaVersion sai', JSON.stringify(badSchema)],
      ['trường bắt buộc hỏng kiểu', JSON.stringify(badField)],
      ['thiếu mảng events', JSON.stringify(badMissing)],
      ['không phải JSON', '{ this is not json'],
    ];
    await armConfirm(p, true);              // kể cả khi người dùng bấm OK, dị dạng vẫn không được ghi
    for (const [label, body] of cases) {
      const r = await importFile(p, 'malformed.json', body, false);
      assert(/TỪ CHỐI KHÔI PHỤC/.test(r.message), label + ': app báo TỪ CHỐI KHÔI PHỤC — ' + r.message.slice(0, 90));
      assert(j(await H.getDoc('state')) === j(golden), label + ': bản durable phía Firebase KHÔNG đổi một byte');
    }
    assert((await confirmLog(p)).length === 0, 'không hộp thoại xác nhận nào bật lên cho file dị dạng (dừng trước cả bước hỏi)');
    assert((await p.evaluate(() => localStorage.getItem('coindca-last-snapshot'))) === lsBefore, 'localStorage[coindca-last-snapshot] không đổi');
    assert((await p.evaluate(() => localStorage.getItem('ethdca-tracker-state-v1'))) === mirrorBefore, 'mirror localStorage không đổi');
    assert(j(await dash(p)) === j(goldenDash), 'số liệu trên màn hình không đổi');
    end();

    /* ---------- CHECK-T14-07 — preview + validate TRƯỚC dialog xác nhận ---------- */
    begin('CHECK-T14-07', 'Xem trước (schemaVersion / số event / khoảng ngày / validate) hiện TRƯỚC hộp thoại xác nhận');
    await armConfirm(p, false);            // người dùng HỦY -> phải không có mutation nào
    const cancelled = await importFile(p, 'valid.json', JSON.stringify(backup), true);
    const log = await confirmLog(p);
    assert(log.length === 1, 'đúng một hộp thoại xác nhận được bật');
    const seen = log[0].messageAtConfirmTime;
    assert(/XEM TRƯỚC KHÔI PHỤC/.test(seen), 'tại thời điểm hỏi xác nhận, #l1Message đã hiện bản tóm tắt');
    assert(seen.indexOf('schemaVersion ' + L.SCHEMA) > 0, 'tóm tắt nêu schemaVersion');
    assert(/3 giao dịch/.test(seen), 'tóm tắt nêu số lượng giao dịch');
    assert(/2026-03-05 → 2026-03-17/.test(seen), 'tóm tắt nêu khoảng ngày min → max');
    assert(/validate PASS/.test(seen), 'tóm tắt nêu KẾT QUẢ VALIDATE');
    assert(/exportedAt|xuất lúc/.test(seen), 'tóm tắt nêu thời điểm xuất của file');
    assert(/coindca-before-restore-/.test(log[0].text), 'hộp thoại nói rõ đã xuất bản snapshot trước thao tác');
    assert(/Đã hủy khôi phục/.test(cancelled.message), 'hủy -> app báo đã hủy');
    assert(j(await H.getDoc('state')) === j(golden), 'hủy -> nguồn bền không đổi');
    end();

    /* ---------- CHECK-T14-09 / C-AS-11 — snapshot trước khi ghi đè ---------- */
    begin('CHECK-T14-09', 'Snapshot `coindca-before-restore-<ISO>` được tạo TRƯỚC khi ghi đè');
    assert(cancelled.file.name === 'coindca-before-restore-' + cancelled.file.json.snapshotAt.replace(/[:.]/g, '-') + '.json',
      'tên file snapshot riêng cho nhánh restore, timestamp khớp snapshotAt: ' + cancelled.file.name);
    assert(j(cancelled.file.json.state) === j(golden), 'snapshot chứa ĐÚNG state hiện tại trước khi ghi');
    assert(cancelled.file.json.reason === 'BEFORE_RESTORE', 'snapshot ghi rõ ngữ cảnh BEFORE_RESTORE');
    assert(typeof cancelled.file.json.snapshotAt === 'string' && !Number.isNaN(Date.parse(cancelled.file.json.snapshotAt)), 'snapshotAt là ISO 8601');
    const lsSnap = JSON.parse(await p.evaluate(() => localStorage.getItem('coindca-last-snapshot')));
    assert(j(lsSnap.state) === j(golden), "localStorage['coindca-last-snapshot'] cũng giữ đúng state trước khi ghi");
    assert(lsSnap.reason === 'BEFORE_RESTORE', "localStorage['coindca-last-snapshot'].reason = BEFORE_RESTORE");
    end();

    /* ---------- CHECK-T14-10 / C-AS-09 — restore hợp lệ tái tạo ĐÚNG trạng thái ---------- */
    begin('CHECK-T14-10', 'backup hợp lệ -> sổ bị xoá -> restore -> ACK -> reload -> derive() y hệt');
    await armConfirm(p, true);
    await p.click('#l1Wipe');                                   // sổ về rỗng qua đúng UI
    await H.waitSaved(p);
    const wiped = await H.getDoc('state');
    assert(wiped.events.length === 0 && wiped.openingPosition === null, 'trạng thái xuất phát: sổ RỖNG trên nguồn bền');
    assert(j(await dash(p)) !== j(goldenDash), 'màn hình đã khác hẳn trước khi khôi phục');

    await armConfirm(p, true);
    const restored = await importFile(p, backupName, JSON.stringify(backup), true);
    assert(/Đã khôi phục từ backup/.test(restored.message), 'app báo đã khôi phục: ' + restored.message.slice(0, 80));
    await H.waitSaved(p);                                        // ACK của máy chủ, không phải cache SDK
    await p.reload(); await H.waitPhase(p, 'ONLINE');            // reload -> derive() lại từ nguồn bền

    const back = await H.getDoc('state');
    const backDerived = derivedOf(back);
    assert(j(backDerived) === j(goldenDerived), 'derive() sau khôi phục TRÙNG KHÍT bản gốc (tolerance 0)');
    assert(j(await dash(p)) === j(goldenDash), 'toàn bộ số liệu dashboard/tóm tắt hiển thị y hệt trước khi hỏng');
    const strip = (s) => { const c = JSON.parse(JSON.stringify(s)); delete c.rev; return c; };
    assert(j(strip(back)) === j(strip(golden)), 'state canonical khớp bản gốc (trừ `rev` — bộ đếm ghi bền, không phải số liệu tài chính)');
    assert(!('derivedSnapshot' in back), 'khối derivedSnapshot của file backup KHÔNG được nhập vào nguồn bền');
    assert(back.rev >= wiped.rev, 'rev tiến lên đúng chuỗi ghi bền, không quay lui');
    end();

    /* ---------- C-AS-09 phần 2 — file có derivedSnapshot BÊN TRONG state cũng bị bỏ ---------- */
    begin('C-AS-09b', 'derivedSnapshot lọt vào trong `state` cũng bị bỏ vô điều kiện, tiền không trôi');
    const poisoned = JSON.parse(JSON.stringify(backup));
    poisoned.state.derivedSnapshot = { holdings: 0, costVnd: 42 };
    await armConfirm(p, true);
    await importFile(p, 'poisoned.json', JSON.stringify(poisoned), true);
    await H.waitSaved(p);
    const afterPoison = await H.getDoc('state');
    assert(!('derivedSnapshot' in afterPoison), 'nguồn bền không chứa derivedSnapshot');
    assert(j(derivedOf(afterPoison)) === j(goldenDerived), 'derive() vẫn cho đúng số cũ — không đồng nào trôi');
    end();

    console.log('\n=== errors console/pageerror (phải rỗng) ===');
    console.log(' ', JSON.stringify(opened.errs));
    assert(opened.errs.length === 0, 'không có pageerror/console error nào');
  } finally {
    if (ctx) await ctx.close();
    await b.close(); await H.stopServer(); await stop();
  }

  const order = ['CHECK-T14-06', 'CHECK-T14-08', 'CHECK-T14-07', 'CHECK-T14-09', 'CHECK-T14-10', 'C-AS-09b'];
  console.log('\n=== TỔNG KẾT test_t14_backup_restore ===');
  order.forEach((id) => console.log('  ' + id + ': ' + (results[id] && results[id].pass ? 'PASS' : 'FAIL') + ' — ' + (results[id] || {}).title));
  console.log('assertion đã chạy:', checks, '| FAIL:', failures);
  if (failures > 0) { console.log('T-14 BACKUP/RESTORE: FAIL'); process.exit(1); }
  console.log('T-14 BACKUP/RESTORE: PASS — CHECK-T14-06..10 (C-AS-08/09/10/11)');
})().catch((e) => { console.error(e); process.exit(1); });
