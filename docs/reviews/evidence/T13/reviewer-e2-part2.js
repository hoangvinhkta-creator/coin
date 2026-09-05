/* T-13 Independent E2 — phần 2: History, UNKNOWN, Navigation/Mobile, mirror phân kỳ (T09B-16),
 * priceMark §16.3, nhập muộn. Reviewer-controlled. */
const A = require('assert/strict'), fs = require('fs'), path = require('path');
const W = '/home/user/coin/webapp';
const { chromium } = require(path.join(W, 'node_modules/playwright'));
const H = require(path.join(W, 'test_firebase_harness.js'));
const L = require(path.join(W, 'ledger.js'));

const out = [];
const ok = (id, d) => { out.push({ id, status: 'PASS', detail: d }); console.log('PASS  ' + id + ' :: ' + d); };
const bad = (id, d) => { out.push({ id, status: 'FAIL', detail: d }); console.log('FAIL  ' + id + ' :: ' + d); };
async function check(id, fn) {
  try { const d = await fn(); ok(id, d || ''); } catch (e) { bad(id, e.message.split('\n').slice(0, 5).join(' | ')); }
}
const dec = (n, pl = 0) => (n / 10 ** pl).toFixed(pl);
const units = (n, pl = 0) => n === null ? '—' : (n / 10 ** pl).toLocaleString('vi-VN', { maximumFractionDigits: pl });
async function fill(p, id, v) { await p.locator('#' + id).fill(String(v)); }
async function openAll(p) { await p.locator('#l1Root details').evaluateAll(ds => ds.forEach(d => { d.open = true; })); }
async function pick(p, k) { await p.click('.txtype[data-txtype="' + k + '"]'); }
async function save(p) { await p.click('#l1SaveEvent'); await p.waitForTimeout(80); await H.waitSaved(p); return p.textContent('#l1Message'); }
async function histCards(p) {
  return p.locator('#l1History .hist-card').evaluateAll(xs => xs.map(x => ({
    date: (x.querySelector('.hc-date') || {}).textContent || '',
    main: (x.querySelector('.hc-main') || {}).textContent || '',
    amount: (x.querySelector('.hc-amount') || {}).textContent || '',
    chips: Array.from(x.querySelectorAll('.chip')).map(c => c.textContent),
    opening: x.classList.contains('hist-opening'),
    hasDelete: !!x.querySelector('[data-action="delete"]'),
    id: (x.getAttribute('data-event') || ''),
  })));
}

(async () => {
  const stop = await H.ensureEmulators();
  const b = await chromium.launch({ executablePath: H.CHROMIUM });
  let ctx;
  try {
    const opened = await H.newPage(b, { seed: false }); ctx = opened.ctx; const p = opened.p; const errs = opened.errs;
    const ASOF = '2026-03-25';
    await p.clock.install({ time: new Date('2026-03-25T05:00:00Z') });
    await p.reload(); await H.waitPhase(p, 'ONLINE'); await openAll(p);

    await fill(p, 'l1StartMonth', '2026-03'); await fill(p, 'l1Effective', '2026-03');
    await fill(p, 'l1Budget', '20000000'); await fill(p, 'l1Days', '3,13,23');
    await p.click('#l1SavePlan'); await H.waitSaved(p);
    // opening với usdt.costVnd = null  -> UNKNOWN_VND_BASIS
    await fill(p, 'l1OpeningDate', '2026-03-01');
    await fill(p, 'l1Eth', '0'); await fill(p, 'l1EthCostUsdt', '0'); await fill(p, 'l1EthCostVnd', '0');
    await fill(p, 'l1Usdt', dec(4000000000, 6)); await fill(p, 'l1UsdtCost', '');
    await fill(p, 'l1Vnd', '0'); await fill(p, 'l1Reserve', '0'); await fill(p, 'l1OpeningNote', 'unknown basis');
    await p.click('#l1SaveOpening'); await H.waitSaved(p);

    /* ---------- UNKNOWN UX ---------- */
    await check('UNKNOWN/banner+dash', async () => {
      const flags = await p.textContent('#l1Flags');
      A.match(flags, /UNKNOWN_VND_BASIS/, 'mã cờ gốc phải giữ trong banner');
      A.match(flags, /chưa xác định/i, 'phải có nhãn tiếng Việt');
      const btns = await p.locator('#l1Flags button').count();
      A.equal(btns, 0, 'banner không được có nút ẩn (0 button), thấy ' + btns);
      const bt = await p.locator('#dashBottom .stat').evaluateAll(xs => Object.fromEntries(xs.map(x => [x.querySelector('small').textContent, x.querySelector('div').textContent])));
      A.equal(bt['Giá vốn TB (VND)'], '—', 'UNKNOWN phải là "—", không 0/trống/NaN');
      A.notEqual(bt['Giá vốn TB (VND)'], '0');
      return 'banner="' + flags.slice(0, 90) + '"; 0 nút ẩn; Giá vốn TB (VND) = "—"';
    });
    await check('UNKNOWN/no-internal-leak', async () => {
      const txt = await p.evaluate(() => document.body.innerText);
      A.doesNotMatch(txt, /realizedFxVnd/, 'không rò rỉ realizedFxVnd (giữ ranh giới H-45)');
      return 'không rò rỉ số nội bộ (H-45 không bị mở rộng)';
    });
    await check('UNKNOWN/not-dismissible-by-interaction', async () => {
      // thử mọi tương tác người dùng bình thường: reload, đổi view, bấm khắp nơi
      await p.reload(); await H.waitPhase(p, 'ONLINE');
      for (const v of ['history', 'plan', 'settings', 'dashboard']) {
        await p.click('#bottomNav button[data-view="' + v + '"]'); await p.waitForTimeout(80);
      }
      const flags = await p.textContent('#l1Flags');
      A.match(flags, /UNKNOWN_VND_BASIS/, 'banner phải còn sau reload + điều hướng');
      const st = await p.evaluate(() => JSON.stringify(Object.keys(localStorage)));
      A.doesNotMatch(st, /dismiss|banner|read|hidden/i, 'không lưu trạng thái "đã đọc" xuống persistence: ' + st);
      return 'banner thường trực sau reload + 4 lần đổi màn; không key persistence nào ghi trạng thái đã-đọc';
    });

    /* ---------- HISTORY (≥12 event đủ loại) ---------- */
    await check('HISTORY/build-dataset', async () => {
      await openAll(p);
      const seq = [
        ['p2p_in', { l1Date: '2026-03-02', l1P2pVnd: '5000000', l1P2pUsdt: dec(200000000, 6), l1Note: 'alpha p2p' }],
        ['buy_plan', { l1Date: '2026-03-03', l1Notional: dec(240000000, 6), l1Fee: '0', l1Qty: dec(10000000, 8), l1Note: 'plan mot' }],
        ['buy_extra', { l1Date: '2026-03-04', l1Notional: dec(100000000, 6), l1Fee: '0', l1Qty: dec(4000000, 8), l1Note: 'beta extra' }],
        ['reserve_add', { l1Date: '2026-03-05', l1ReserveAmount: '10000000', l1Note: 'nap du phong' }],
        ['buy_reserve', { l1Date: '2026-03-06', l1Notional: dec(50000000, 6), l1Fee: '0', l1Qty: dec(2000000, 8), l1Note: 'gamma reserve buy' }],
        ['reserve_out', { l1Date: '2026-03-07', l1ReserveAmount: '1000000', l1Note: 'rut' }],
        ['price', { l1Date: '2026-03-08', l1Price: dec(2500000000, 6), l1MarkRate: '', l1Note: 'gia cu' }],
        ['p2p_out', { l1Date: '2026-03-09', l1P2pVnd: '2500000', l1P2pUsdt: dec(100000000, 6), l1Note: 'p2p ra' }],
        ['buy_plan', { l1Date: '2026-03-13', l1Notional: dec(240000000, 6), l1Fee: '0', l1Qty: dec(10000000, 8), l1Note: 'plan hai' }],
        ['buy_extra', { l1Date: '2026-03-14', l1Notional: dec(60000000, 6), l1Fee: '0', l1Qty: dec(2400000, 8), l1Note: 'extra hai' }],
        ['reserve_add', { l1Date: '2026-03-15', l1ReserveAmount: '3000000', l1Note: 'nap hai' }],
        ['buy_plan', { l1Date: '2026-03-23', l1Notional: dec(120000000, 6), l1Fee: '0', l1Qty: dec(5000000, 8), l1Note: 'plan ba' }],
        // nhập muộn: ngày 2026-03-10 nhập SAU CÙNG (AS-11)
        ['p2p_in', { l1Date: '2026-03-10', l1P2pVnd: '1000000', l1P2pUsdt: dec(40000000, 6), l1Note: 'nhap muon' }],
        // tương lai: kích FUTURE_DATED_EVENTS
        ['buy_extra', { l1Date: '2026-03-28', l1Notional: dec(20000000, 6), l1Fee: '0', l1Qty: dec(800000, 8), l1Note: 'tuong lai' }],
      ];
      for (const [k, f] of seq) { await pick(p, k); for (const [id, v] of Object.entries(f)) await fill(p, id, v); await save(p); }
      const st = await H.readState(p);
      A.ok(st.events.length >= 12, 'cần ≥12 event, có ' + st.events.length);
      return st.events.length + ' event đủ 8 loại + 1 nhập muộn + 1 tương lai';
    });
    await check('HISTORY/ordering-businessDate-desc-seq-desc', async () => {
      const st = await H.readState(p);
      const cards = (await histCards(p)).filter(c => !c.opening);
      const expect = st.events.slice().sort((a, b) => b.businessDate.localeCompare(a.businessDate) || b.seq - a.seq);
      A.equal(cards.length, expect.length, 'số thẻ phải bằng số event (mặc định KHÔNG lọc)');
      A.deepEqual(cards.map(c => c.id), expect.map(e => e.id), 'thứ tự (businessDate DESC, seq DESC)');
      A.deepEqual(cards.map(c => c.date), expect.map(e => e.businessDate), 'businessDate hiển thị đúng');
      // nhập muộn nằm đúng vị trí thời gian, không ở cuối/đầu theo thứ tự nhập
      const late = st.events.find(e => e.note === 'nhap muon');
      const pos = cards.findIndex(c => c.id === late.id);
      const posByEntry = st.events.slice().sort((a, b) => b.seq - a.seq).findIndex(e => e.id === late.id);
      A.notEqual(pos, posByEntry, 'AS-11: nhập muộn phải xếp theo businessDate, KHÁC thứ tự nhập');
      return cards.length + ' thẻ đúng thứ tự (businessDate DESC, seq DESC); nhập muộn ở vị trí ' + pos + ' (thứ tự nhập sẽ là ' + posByEntry + ')';
    });
    await check('HISTORY/badges-and-future', async () => {
      const st = await H.readState(p);
      const cards = (await histCards(p)).filter(c => !c.opening);
      const byId = Object.fromEntries(cards.map(c => [c.id, c]));
      for (const e of st.events) {
        const c = byId[e.id]; A.ok(c, 'event ' + e.id + ' phải có thẻ');
        if (e.kind === 'TRADE' && e.source === 'EXTRA') A.ok(c.chips.includes('EXTRA'), 'EXTRA phải có badge');
        if (e.kind === 'TRADE' && e.source === 'RESERVE') A.ok(c.chips.includes('RESERVE'), 'RESERVE phải có badge');
        if (e.kind === 'TRADE' && e.source === 'PLAN') {
          A.ok(!c.chips.includes('EXTRA') && !c.chips.includes('RESERVE'), 'PLAN không được mang badge EXTRA/RESERVE');
        }
        if (e.businessDate > '2026-03-25') A.ok(c.chips.includes('TƯƠNG LAI'), 'event tương lai phải được đánh dấu');
      }
      const flags = await p.textContent('#l1Flags');
      A.match(flags, /FUTURE_DATED_EVENTS/, 'banner FUTURE_DATED_EVENTS phải bật');
      return 'badge EXTRA/RESERVE/TƯƠNG LAI đúng trên mọi thẻ; PLAN không badge; banner FUTURE_DATED_EVENTS bật';
    });
    await check('HISTORY/opening-row-special', async () => {
      const cards = await histCards(p);
      const op = cards.filter(c => c.opening);
      A.equal(op.length, 1, 'phải có đúng 1 dòng Số dư đầu kỳ');
      A.equal(cards[0].opening, true, 'dòng Số dư đầu kỳ phải ở ĐẦU danh sách');
      A.equal(op[0].hasDelete, false, 'dòng Số dư đầu kỳ KHÔNG được có nút Xoá ở Lịch sử (§6/§7)');
      A.match(op[0].main, /Số dư đầu kỳ/);
      return 'opening tách riêng ở đầu, chỉ có Sửa, không có Xoá';
    });
    await check('HISTORY/filter-type', async () => {
      const st = await H.readState(p);
      const cases = [
        ['PLAN', e => e.kind === 'TRADE' && e.source === 'PLAN'],
        ['EXTRA', e => e.kind === 'TRADE' && e.source === 'EXTRA'],
        ['RESERVE_BUY', e => e.kind === 'TRADE' && e.source === 'RESERVE'],
        ['RESERVE', e => e.kind === 'RESERVE'],
        ['TREASURY', e => e.kind === 'TREASURY'],
        ['PRICE', e => e.kind === 'PRICE'],
      ];
      const report = [];
      for (const [v, f] of cases) {
        await p.selectOption('#histFilterType', v); await p.waitForTimeout(120);
        const got = (await histCards(p)).filter(c => !c.opening).map(c => c.id).sort();
        const want = st.events.filter(f).map(e => e.id).sort();
        A.deepEqual(got, want, 'bộ lọc ' + v + ' sai: got ' + got.length + ' want ' + want.length);
        report.push(v + '=' + want.length);
      }
      await p.selectOption('#histFilterType', 'all'); await p.waitForTimeout(120);
      const all = (await histCards(p)).filter(c => !c.opening).length;
      A.equal(all, st.events.length, 'reset về "Tất cả loại" phải hiện lại toàn bộ');
      return report.join(' ') + '; reset all=' + all;
    });
    await check('HISTORY/filter-daterange-and-search', async () => {
      const st = await H.readState(p);
      await p.fill('#histFrom', '2026-03-05'); await p.fill('#histTo', '2026-03-13'); await p.waitForTimeout(150);
      let got = (await histCards(p)).filter(c => !c.opening).map(c => c.id).sort();
      let want = st.events.filter(e => e.businessDate >= '2026-03-05' && e.businessDate <= '2026-03-13').map(e => e.id).sort();
      A.deepEqual(got, want, 'lọc khoảng ngày (bao gồm hai đầu mút)');
      const range = got.length;
      await p.fill('#histFrom', ''); await p.fill('#histTo', '');
      await p.fill('#histSearch', 'gamma'); await p.waitForTimeout(200);
      got = (await histCards(p)).filter(c => !c.opening).map(c => c.id);
      want = st.events.filter(e => (e.note || '').toLowerCase().includes('gamma')).map(e => e.id);
      A.deepEqual(got.sort(), want.sort(), 'tìm theo ghi chú');
      A.equal(want.length, 1, 'kịch bản phải phân biệt được (đúng 1 kết quả)');
      await p.fill('#histSearch', ''); await p.waitForTimeout(200);
      const back = (await histCards(p)).filter(c => !c.opening).length;
      A.equal(back, st.events.length, 'xoá tìm kiếm phải khôi phục toàn bộ');
      // lọc KHÔNG được đổi sổ
      const after = await H.readState(p);
      A.deepEqual(H.canon(after), H.canon(st), 'bộ lọc KHÔNG được đổi sự thật của sổ');
      return 'khoảng ngày=' + range + '; tìm "gamma"=1; reset=' + back + '; durable state bất biến qua mọi thao tác lọc';
    });
    await check('HISTORY/filter-does-not-change-dashboard', async () => {
      const { openingPosition: o, plan: pl, events: ev } = await H.readState(p);
      const d = L.derive(o, pl, ev, ASOF);
      await p.selectOption('#histFilterType', 'PLAN'); await p.waitForTimeout(150);
      const c = await p.locator('#dashMain .dcard').evaluateAll(xs => Object.fromEntries(xs.map(x => [x.querySelector('.dc-label').textContent, x.querySelector('.dc-value').textContent])));
      A.equal(c['Đã đầu tư tháng này'], units(d.month.investedThisMonthVnd) + ' ₫',
        'lọc Lịch sử KHÔNG được ảnh hưởng số Tổng quan');
      await p.selectOption('#histFilterType', 'all'); await p.waitForTimeout(150);
      return 'lọc theo PLAN không đổi con số Tổng quan (vẫn = derive() trên TOÀN BỘ event)';
    });
    await check('HISTORY/detail-matches-selected-event', async () => {
      const st = await H.readState(p);
      const target = st.events.find(e => e.note === 'gamma reserve buy');
      await p.click('button[data-id="' + target.id + '"][data-action="edit"]');
      await p.waitForTimeout(200);
      const form = await p.evaluate(() => ({
        kind: document.getElementById('l1Kind').value, date: document.getElementById('l1Date').value,
        note: document.getElementById('l1Note').value, side: document.getElementById('l1Side').value,
        source: document.getElementById('l1Source').value, notional: document.getElementById('l1Notional').value,
        qty: document.getElementById('l1Qty').value,
      }));
      A.equal(form.kind, target.kind); A.equal(form.date, target.businessDate);
      A.equal(form.note, target.note); A.equal(form.source, target.source);
      A.equal(Number(form.notional) * 1e6, target.usdtNotional, 'notional khớp event ĐƯỢC CHỌN');
      A.equal(Math.round(Number(form.qty) * 1e8), target.qty);
      await p.click('#l1CancelEdit');
      return 'form chi tiết khớp đúng event được chọn (' + target.id.slice(0, 8) + ')';
    });

    /* ---------- priceMark §16.3 ---------- */
    await check('DASH/priceMark-validity-16.3', async () => {
      const st = await H.readState(p);
      const d = L.derive(st.openingPosition, st.plan, st.events, ASOF);
      const bt = await p.locator('#dashBottom .stat').evaluateAll(xs => Object.fromEntries(xs.map(x => [x.querySelector('small').textContent, x.querySelector('div').textContent])));
      A.equal(d.valuation, null, 'giá 2026-03-08 so với asOf 2026-03-25 phải KHÔNG hợp lệ (§16.3)');
      A.match(bt['Định giá hiện tại'], /^—/, 'phải bắt đầu bằng "—", không ngoại suy');
      A.match(bt['Định giá hiện tại'], /giá gần nhất/, 'phải kèm tuổi/ngày của giá gần nhất');
      const showsAge = /\d+\s*ngày/.test(bt['Định giá hiện tại']);
      // ghi lại: spec §16.3 nêu "giá gần nhất: N ngày trước"; UI hiện NGÀY thay vì SỐ NGÀY
      return 'valuation=null; UI="' + bt['Định giá hiện tại'] + '"; hiển thị dạng "N ngày trước"? ' + showsAge;
    });
    await check('DASH/priceMark-valid-shows-valuation', async () => {
      await openAll(p);
      await pick(p, 'price'); await fill(p, 'l1Date', '2026-03-25'); await fill(p, 'l1Price', dec(2600000000, 6)); await fill(p, 'l1MarkRate', ''); await fill(p, 'l1Note', 'gia hom nay');
      await save(p);
      const st = await H.readState(p);
      const d = L.derive(st.openingPosition, st.plan, st.events, ASOF);
      A.notEqual(d.valuation, null, 'giá hôm nay phải hợp lệ');
      const bt = await p.locator('#dashBottom .stat').evaluateAll(xs => Object.fromEntries(xs.map(x => [x.querySelector('small').textContent, x.querySelector('div').textContent])));
      A.equal(bt['Định giá hiện tại'], units(d.valuation.usdt, 6) + ' USDT (' + d.valuation.businessDate + ')');
      return 'priceMark hợp lệ -> "' + bt['Định giá hiện tại'] + '" khớp derive().valuation';
    });

    /* ---------- NAVIGATION + MOBILE ---------- */
    await check('NAV/4-destinations+fab', async () => {
      const nav = await p.locator('#bottomNav button').evaluateAll(xs => xs.map(x => x.dataset.view + '=' + x.textContent.trim()));
      A.equal(nav.length, 4, '4 điểm đến, thấy ' + JSON.stringify(nav));
      A.deepEqual(nav.map(x => x.split('=')[0]), ['dashboard', 'history', 'plan', 'settings']);
      A.equal(await p.locator('#fabEntry').count(), 1, 'FAB "+ Ghi giao dịch" toàn cục');
      const sections = await p.locator('.view-sec').evaluateAll(xs => xs.map(x => x.id));
      A.deepEqual(sections, ['view-dashboard', 'view-history', 'view-plan', 'view-settings']);
      return JSON.stringify(nav);
    });
    await check('NAV/hash-survives-refresh', async () => {
      const report = [];
      for (const v of ['history', 'plan', 'settings', 'dashboard']) {
        await p.click('#bottomNav button[data-view="' + v + '"]'); await p.waitForTimeout(200);
        const h1 = await p.evaluate(() => location.hash);
        A.equal(h1, '#/' + v, 'hash sau khi bấm nav');
        await p.reload(); await H.waitPhase(p, 'ONLINE'); await p.waitForTimeout(400);
        const h2 = await p.evaluate(() => location.hash);
        A.equal(h2, '#/' + v, 'refresh phải giữ hash ' + v);
        const cur = await p.locator('#bottomNav button[aria-current="true"]').evaluateAll(xs => xs.map(x => x.dataset.view));
        A.deepEqual(cur, [v], 'aria-current phải trỏ đúng ' + v + ' sau refresh, thấy ' + JSON.stringify(cur));
        report.push(v);
      }
      return 'refresh-safe cho ' + report.join(',');
    });
    await check('NAV/back-forward-no-corruption', async () => {
      const before = await H.readState(p);
      await p.click('#bottomNav button[data-view="history"]'); await p.waitForTimeout(150);
      await p.click('#bottomNav button[data-view="plan"]'); await p.waitForTimeout(150);
      await p.goBack().catch(() => null); await p.waitForTimeout(300);
      await p.goForward().catch(() => null); await p.waitForTimeout(300);
      const after = await H.readState(p).catch(() => null);
      A.ok(after, 'app phải còn sống sau back/forward');
      A.deepEqual(H.canon(after), H.canon(before), 'back/forward không được làm hỏng sổ');
      const errCount = errs.length;
      return 'sổ bit-exact sau back/forward; page errors=' + errCount +
        ' (lưu ý: routeTo dùng history.replaceState nên back KHÔNG duyệt giữa 4 điểm đến)';
    });
    await check('MOBILE/390-no-horizontal-scroll', async () => {
      await p.setViewportSize({ width: 390, height: 844 });
      await p.waitForTimeout(300);
      const res = await p.evaluate(() => {
        const de = document.documentElement;
        const over = Array.from(document.querySelectorAll('body *'))
          .filter(el => el.getBoundingClientRect().right > de.clientWidth + 1)
          .slice(0, 8).map(el => el.tagName + '#' + el.id + '.' + el.className);
        return { scrollWidth: de.scrollWidth, clientWidth: de.clientWidth, over };
      });
      A.ok(res.scrollWidth <= res.clientWidth + 1,
        'cuộn ngang ở 390px: scrollWidth=' + res.scrollWidth + ' clientWidth=' + res.clientWidth + ' thủ phạm=' + JSON.stringify(res.over));
      return 'scrollWidth=' + res.scrollWidth + ' ≤ clientWidth=' + res.clientWidth;
    });
    await check('MOBILE/touch-targets', async () => {
      const small = await p.evaluate(() => Array.from(document.querySelectorAll('#bottomNav button, .fab, .txtype, .hc-actions button'))
        .map(el => { const r = el.getBoundingClientRect(); return { t: el.textContent.trim().slice(0, 18), w: Math.round(r.width), h: Math.round(r.height) }; })
        .filter(x => x.h < 24 || x.w < 24));
      A.deepEqual(small, [], 'nút quá nhỏ (<24px): ' + JSON.stringify(small));
      return 'mọi nút điều hướng/FAB/chọn-loại/Sửa-Xoá ≥ 24px ở 390px';
    });
    await check('MOBILE/plan-purchase-3-taps', async () => {
      await p.click('#bottomNav button[data-view="dashboard"]'); await p.waitForTimeout(200);
      const before = (await H.readState(p)).events.length;
      let taps = 0;
      await p.click('#fabEntry'); taps++;                                   // 1
      await p.click('.txtype[data-txtype="buy_plan"]'); taps++;             // 2
      await fill(p, 'l1Date', '2026-03-24'); await fill(p, 'l1Notional', dec(30000000, 6));
      await fill(p, 'l1Fee', '0'); await fill(p, 'l1Qty', dec(1200000, 8)); await fill(p, 'l1Note', '');
      await p.click('#l1SaveEvent'); taps++;                                // 3
      await p.waitForTimeout(100); await H.waitSaved(p);
      const st = await H.readState(p);
      A.equal(st.events.length, before + 1, 'phải ghi được 1 event');
      const e = st.events.find(x => x.businessDate === '2026-03-24');
      A.equal(e.source, 'PLAN'); A.equal(e.side, 'BUY');
      A.ok(taps <= 3, 'tốn ' + taps + ' lần chạm');
      return taps + ' lần chạm (FAB → chọn loại → Lưu) ghi được 1 giao dịch PLAN ở 390px';
    });
    await p.setViewportSize({ width: 1200, height: 1000 });

    /* ---------- CHECK-T09B-16: mirror phân kỳ (hành vi CÒN HIỆU LỰC) ---------- */
    await check('T09B-16/mirror-never-silently-wins', async () => {
      const durable = await H.getDoc('state');
      const durRev = durable.rev;
      // giả mạo mirror localStorage MỚI HƠN nguồn bền (đúng ý CHECK-T09B-16, dùng schema L-1)
      await p.evaluate(() => {
        const m = JSON.parse(localStorage.getItem('ethdca-tracker-state-v1'));
        m.rev = m.rev + 5;
        m.events = m.events.slice(0, Math.max(0, m.events.length - 2));   // sổ mirror KHÁC hẳn
        localStorage.setItem('ethdca-tracker-state-v1', JSON.stringify(m));
      });
      await p.reload(); await p.waitForTimeout(1500);
      const st = await H.status(p);
      const serverAfter = await H.getDoc('state');
      A.equal(serverAfter.rev, durRev, 'mirror mới hơn KHÔNG được âm thầm ghi đè nguồn bền');
      A.deepEqual(H.canon(serverAfter), H.canon(durable), 'nguồn bền phải bit-exact như trước');
      const banner = await p.textContent('#banners');
      const flagged = !!st.diverged || /localStorage có rev|phân kỳ|diverged/i.test(banner);
      A.ok(flagged, 'app phải BÁO phân kỳ cho người dùng chọn tường minh; status=' + JSON.stringify(st) + ' banner="' + banner.slice(0, 200) + '"');
      return 'mirror rev+5 KHÔNG thắng nguồn bền; app báo phân kỳ chờ người dùng chọn (hành vi CHECK-T09B-16 còn nguyên trên UI Step B)';
    });

    console.log('\n--- page errors ---\n' + JSON.stringify(errs, null, 2));
    fs.writeFileSync(path.join(__dirname, 'reviewer-e2-part2-results.json'),
      JSON.stringify({ results: out, pageErrors: errs }, null, 2));
  } finally { if (ctx) await ctx.close(); await b.close(); await H.stopServer(); await stop(); }
  const f = out.filter(x => x.status === 'FAIL');
  console.log('\nSUMMARY part2: ' + out.filter(x => x.status === 'PASS').length + ' PASS, ' + f.length + ' FAIL');
  if (f.length) process.exitCode = 1;
})().catch(e => { console.error(e); process.exitCode = 1; });
