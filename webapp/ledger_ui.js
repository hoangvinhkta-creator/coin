/* CoinDCA L-1 Step B (T-13): Dashboard + Nhập giao dịch/Lịch sử/Kế hoạch/Cài đặt.
 * Mọi con số hiển thị đến từ MỘT lệnh gọi CoinLedger.derive() mỗi lần render(); mọi ghi dữ
 * liệu đi qua CoinLedger.update()/migrate()/destructive() (Step-B spec §0, T-13 §11).
 * Các id/hành vi dưới đây được giữ nguyên so với adapter T-12 để `test_t12_browser.js`
 * (Completion Gate CHECK-T13-12) tiếp tục chạy nguyên văn: l1Kind, l1Date, l1Note, l1P2pVnd,
 * l1P2pUsdt, l1Dir, l1Side, l1Source, l1Notional, l1Fee, l1Qty, l1ReserveType, l1ReserveAmount,
 * l1Price, l1MarkRate, l1OpeningDate, l1Eth and friends, l1Usdt and friends, l1Vnd, l1Reserve,
 * l1OpeningNote, l1StartMonth, l1Effective, l1Budget, l1Days, the l1Save buttons,
 * l1DeleteOpening, l1CancelEdit, l1Export, l1Import, l1Wipe, l1Migrate, l1Contributions,
 * l1MigrationDate fields, l1History, l1Summary, l1Flags, l1Message, l1Root. Vì vậy Sheet
 * "+ Ghi giao dịch" (Step-B spec §5) ở đây mở sẵn (không đóng theo mặc định) thay vì modal ẩn
 * — quyết định ghi lại trong docs/reviews/T13-IMPLEMENTATION-REPORT.md.
 * T-14 (bước C, DEC-049) chỉ thêm lớp backup/restore quanh CÙNG cơ chế đã có
 * (download/L.destructive/commit): export mang timestamp + schemaVersion; restore có
 * preview/validate dry-run TRƯỚC khi ghi và snapshot riêng cho nhánh restore. KHÔNG có phép tính
 * tài chính nào mới ở đây — `CoinLedger.canonical/derive` vẫn là thẩm quyền duy nhất.
 */
(function () {
  'use strict';
  const L = window.CoinLedger, $ = id => document.getElementById(id);
  const escape = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const units = (n, places = 0) => n === null ? '—' : (n / 10 ** places).toLocaleString('vi-VN', { maximumFractionDigits: places });
  const avg = (r, scale = 1) => r === null ? '—' : (Number(r.numerator) / Number(r.denominator) / scale).toLocaleString('vi-VN', { maximumFractionDigits: 8 });
  const input = (id, label, type = 'text', value = '', numeric = false) => '<div class="field"><label for="' + id + '">' + label + '</label><input id="' + id + '" type="' + type + '"' + (numeric ? ' inputmode="decimal"' : '') + ' value="' + escape(value) + '"></div>';
  const select = (id, label, choices) => '<div class="field"><label for="' + id + '">' + label + '</label><select id="' + id + '">' + choices.map(([v, t]) => '<option value="' + v + '">' + t + '</option>').join('') + '</select></div>';
  const button = (id, label, cls = '') => '<button type="button" id="' + id + '"' + (cls ? ' class="' + cls + '"' : '') + '>' + label + '</button>';
  const symbolChoices = () => L.ASSETS.map(x => [x, x]);
  let hooks, mounted = false, editId = null, shownLegacy = null, lastFormState = null, currentTxType = null, returnAnchor = null;

  /* -------- 9 loại giao dịch của Step-B spec §5: 1 sheet, bước 1 chọn loại -------- */
  const TX_TYPES = [
    { key: 'opening', label: 'Số dư đầu kỳ', special: 'opening' },
    { key: 'p2p_in', label: 'Đổi VND → USDT', kind: 'TREASURY', dir: 'VND_TO_USDT' },
    { key: 'p2p_out', label: 'Đổi USDT → VND', kind: 'TREASURY', dir: 'USDT_TO_VND' },
    { key: 'buy_plan', label: 'Mua coin · Kế hoạch', kind: 'TRADE', side: 'BUY', source: 'PLAN' },
    { key: 'buy_extra', label: 'Mua coin · Ngoài kế hoạch', kind: 'TRADE', side: 'BUY', source: 'EXTRA' },
    { key: 'buy_reserve', label: 'Mua coin · Từ dự phòng', kind: 'TRADE', side: 'BUY', source: 'RESERVE', noteRequired: true },
    { key: 'sell', label: 'Bán coin', kind: 'TRADE', side: 'SELL', source: 'EXTRA' },
    { key: 'cash_in', label: 'Nạp tiền mặt (VND)', kind: 'CASH', ctype: 'DEPOSIT' },
    { key: 'cash_out', label: 'Rút tiền mặt (VND)', kind: 'CASH', ctype: 'WITHDRAW' },
    { key: 'reserve_add', label: 'Nạp dự phòng', kind: 'RESERVE', rtype: 'CONTRIBUTE' },
    { key: 'reserve_out', label: 'Rút dự phòng', kind: 'RESERVE', rtype: 'WITHDRAW' },
    { key: 'price', label: 'Giá tham chiếu', kind: 'PRICE' },
  ];

  function download(value, name) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
    const a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  /** Bản chụp cục bộ là lớp tiện lợi THỨ HAI; bản tải về mới là backup thật. Nếu localStorage
   *  đầy (QuotaExceededError) thì BÁO cho người dùng chứ không ném ra ngoài — ném ra sẽ làm hỏng
   *  L.destructive() và khoá luôn xoá/wipe/restore mà không nói lý do. */
  function keepLocal(key, payload) {
    try { localStorage.setItem(key, JSON.stringify(payload)); return true; }
    catch (e) { message('Cảnh báo: không lưu được bản chụp vào trình duyệt (' + (e && e.name ? e.name : 'lỗi lưu trữ') + '). Bản backup tải về vẫn được tạo; hãy giữ file đó.'); return false; }
  }
  function snapshot(value) {
    const payload = { state: value, seed: hooks.seed(), snapshotAt: L.clock().instant };
    keepLocal('coindca-last-snapshot', payload);
    download(payload, 'coindca-before-change.json');
  }

  /* ---- T-14 bước C: backup / recovery (Step-C spec §7, §8) ---- */

  // Thời điểm cho TÊN FILE: ':' và '.' không dùng được trên nhiều hệ tệp nên đổi thành '-'.
  // Nhận CHÍNH giá trị ISO 8601 đã ghi trong file (`exportedAt`/`snapshotAt`) chứ không đọc đồng
  // hồ lần thứ hai — tên file và nội dung phải nói cùng một thời điểm.
  function stamp(instant) { return String(instant).replace(/[:.]/g, '-'); }
  /** Nội dung file backup: CHỈ nguồn sự thật canonical (`state` + `seed`) cộng siêu dữ liệu nhận
   *  dạng. `derivedSnapshot` là khối THAM KHẢO cho người đọc, đánh dấu tường minh và KHÔNG bao
   *  giờ được import (INV-1; `L.canonical()` cũng tự xoá trường này nếu lọt vào state). */
  function exportPayload() {
    const st = hooks.raw() || hooks.state();
    // schemaVersion nói ĐÚNG schema của state đang xuất (kể cả bản durable hỏng đang được cứu),
    // không mượn L.SCHEMA để trông cho hợp lệ — file backup phải tự mô tả trung thực.
    const payload = { schemaVersion: st && st.schema !== undefined ? st.schema : null, exportedAt: L.clock().instant, state: st, seed: hooks.seed() };
    if (st && st.schema === L.SCHEMA) {
      try {
        const d = L.derive(st.openingPosition, st.plan, st.events, L.clock().today);
        payload.derivedSnapshot = { _meta: 'INFORMATIONAL — NOT IMPORTED', asOf: L.clock().today,
          holdings: Object.fromEntries(Object.entries(d.holdings).map(([sym, h]) => [sym, { qty: h.qty, costUsdt: h.costUsdt, costVnd: h.costVnd }])),
          usdtQty: d.usdt.qty, usdtCostVnd: d.usdt.costVnd, vndBalance: d.vnd.balance,
          reserveBalance: d.reserve.balance, realizedFxVnd: d.realizedFxVnd, realizedPnlUsdt: d.realizedPnlUsdt, flags: d.flags };
      } catch (e) { /* sổ chưa đủ dữ liệu để dẫn xuất — bỏ khối tham khảo, KHÔNG chặn backup */ }
    }
    return payload;
  }
  /** Đọc + kiểm một file backup mà KHÔNG chạm state hiện tại (dry-run, §8.2 mục 1/2).
   *  `ok:false` = từ chối TRƯỚC mọi mutation bền (không snapshot, không ghi Firestore). */
  function restorePreview(text) {
    const no = r => ({ ok: false, summary: 'TỪ CHỐI KHÔI PHỤC — ' + r + '. Sổ hiện tại giữ nguyên; không ghi gì.' });
    let o; try { o = JSON.parse(text); } catch (e) { return no('file không phải JSON hợp lệ (' + e.message + ')'); }
    const wrapped = o && typeof o === 'object' && !Array.isArray(o) && o.state !== undefined;
    const candidate = wrapped ? o.state : o;
    const declared = wrapped && o.schemaVersion !== undefined ? o.schemaVersion : (candidate && candidate.schema);
    if (declared !== L.SCHEMA || !candidate || candidate.schema !== L.SCHEMA) {
      return no('schemaVersion ' + JSON.stringify(declared === undefined ? null : declared) + ' không phải ' + L.SCHEMA);
    }
    let restored;
    try {
      restored = L.canonical(candidate);
      L.derive(restored.openingPosition, restored.plan, restored.events, L.clock().today);
    } catch (e) { return no('validate thất bại: ' + e.message); }
    const dates = restored.events.map(e => e.businessDate).sort();
    return { ok: true, state: restored,
      summary: 'XEM TRƯỚC KHÔI PHỤC — schemaVersion ' + declared + ' · ' + restored.events.length + ' giao dịch · ' +
        (dates.length ? dates[0] + ' → ' + dates[dates.length - 1] : 'chưa có giao dịch') + ' · validate PASS' +
        (wrapped && o.exportedAt ? ' · xuất lúc ' + o.exportedAt : '') };
  }
  /** Snapshot riêng của nhánh restore (§8.2 mục 3): tên khác snapshot "before-change" tổng quát
   *  để Owner nhận đúng ngữ cảnh khi cần dùng lại. Chạy TRƯỚC mọi lệnh ghi phá huỷ. */
  function restoreSnapshot(value) {
    const payload = { schemaVersion: value && value.schema !== undefined ? value.schema : null, snapshotAt: L.clock().instant,
      reason: 'BEFORE_RESTORE', state: value, seed: hooks.seed() };
    keepLocal('coindca-last-snapshot', payload);
    download(payload, 'coindca-before-restore-' + stamp(payload.snapshotAt) + '.json');
  }
  function writable() { if (!hooks.canWrite()) throw new Error('Nguồn bền chưa sẵn sàng hoặc đang lưu; xem trạng thái đầu trang.'); }
  function meta() { return Object.assign({ id: crypto.randomUUID() }, L.clock()); }
  function commit(value) { writable(); hooks.commit(value); }
  function message(text) { $('l1Message').textContent = text; }
  function run(fn) { return async () => { try { writable(); const result = await fn(); message(result || 'Đã cập nhật sổ; xem xác nhận lưu bền đầu trang.'); } catch (e) { message(e.message); } }; }
  function readNumber(id, places = 0, nullable = false) { const v = $(id).value.trim(); return !v && nullable ? null : L.decimal(v, places); }
  /** Số dư đầu kỳ nay có NHIỀU tài sản, nhưng form chỉ sửa MỘT dòng mỗi lần (dropdown chọn coin).
   *  Dòng đang sửa ghi đè entry cùng symbol trong sổ và giữ nguyên các coin khác; lượng 0 + giá vốn
   *  để trống = xoá coin đó khỏi số dư đầu kỳ. Ba ô nhập giữ nguyên id `l1Eth*` — hợp đồng id với
   *  test_t12_browser.js/test_stepb_ui.js (xem đầu file). */
  function openingInput() {
    const symbol = $('l1OpeningSymbol').value, current = hooks.state();
    const prior = current.schema === L.SCHEMA && current.openingPosition ? L.clone(current.openingPosition.assets) : [];
    const qty = readNumber('l1Eth', 8), costUsdt = readNumber('l1EthCostUsdt', 6, true), costVnd = readNumber('l1EthCostVnd', 0, true);
    const assets = prior.filter(a => a.symbol !== symbol);
    if (qty || costUsdt || costVnd) assets.push({ symbol, qty, costUsdt, costVnd });
    assets.sort((a, b) => a.symbol.localeCompare(b.symbol));
    return { asOf: $('l1OpeningDate').value, assets, usdt: { qty: readNumber('l1Usdt', 6), costVnd: readNumber('l1UsdtCost', 0, true) }, vnd: { qty: readNumber('l1Vnd') }, reserveVnd: readNumber('l1Reserve'), note: $('l1OpeningNote').value };
  }
  function fillOpeningAsset(o) {
    const symbol = $('l1OpeningSymbol').value;
    const a = (o && o.assets.find(x => x.symbol === symbol)) || { qty: 0, costUsdt: null, costVnd: null };
    for (const [id, amount, places] of [['l1Eth', a.qty, 8], ['l1EthCostUsdt', a.costUsdt, 6], ['l1EthCostVnd', a.costVnd, 0]]) $(id).value = amount === null ? '' : (amount / 10 ** places).toFixed(places);
  }
  function planInput() {
    const current = hooks.state(), plan = current.schema === L.SCHEMA ? L.clone(current.plan) : { startMonth: $('l1StartMonth').value, versions: [] };
    plan.startMonth = $('l1StartMonth').value;
    const effectiveFrom = $('l1Effective').value, old = plan.versions.find(v => v.effectiveFrom === effectiveFrom);
    // Kế hoạch là ĐƠN tài sản: version mới luôn theo asset của version đã có; dropdown chỉ quyết
    // định khi kế hoạch còn rỗng. planCheck() ép lại điều này ở tầng sổ, đây chỉ là UI cho khớp.
    const asset = plan.versions.length ? plan.versions[0].asset : $('l1PlanAsset').value;
    const p = { id: old ? old.id : crypto.randomUUID(), effectiveFrom, asset, monthlyBudgetVnd: readNumber('l1Budget'), scheduleDays: $('l1Days').value.split(',').map(x => Number(x.trim())), carryPolicy: 'CAPPED_CARRY', carryCapMonths: 1 };
    if (old) plan.versions[plan.versions.indexOf(old)] = p; else plan.versions.push(p);
    return plan;
  }
  async function destroy(label, operation) {
    writable();
    const result = await L.destructive(hooks.raw() || hooks.state(), operation, { snapshot, confirm: () => window.confirm(label + ' Bản đầy đủ đã được xuất trước thao tác này.'), commit });
    if (!result.ok) return result.cancelled ? 'Đã hủy; sổ giữ nguyên, snapshot vẫn có.' : (result.errors || ['Thao tác thất bại']).join('\n') + '\n' + JSON.stringify(result.deltas || {});
    return result.warnings ? result.warnings.join(', ') + '\nĐối chiếu: ' + JSON.stringify(result.deltas) + '\n' + (result.unknownBasis || []).map(x => x.legacyIndex + ': ' + x.reason + ' ' + x.correction).join('\n') : 'Đã cập nhật; chờ xác nhận lưu bền.';
  }
  function eventInput() {
    const kind = $('l1Kind').value, e = { kind, businessDate: $('l1Date').value, note: $('l1Note').value };
    if (kind === 'TREASURY') Object.assign(e, { dir: $('l1Dir').value, vndAmount: readNumber('l1P2pVnd'), usdtAmount: readNumber('l1P2pUsdt', 6), counterparty: $('l1Counterparty').value });
    if (kind === 'TRADE') Object.assign(e, { side: $('l1Side').value, symbol: $('l1Symbol').value, source: $('l1Source').value, usdtNotional: readNumber('l1Notional', 6), feeUsdt: readNumber('l1Fee', 6), qty: readNumber('l1Qty', 8) });
    if (kind === 'RESERVE') Object.assign(e, { type: $('l1ReserveType').value, vndAmount: readNumber('l1ReserveAmount') });
    if (kind === 'CASH') Object.assign(e, { type: $('l1CashType').value, vndAmount: readNumber('l1CashAmount') });
    if (kind === 'PRICE') Object.assign(e, { symbol: $('l1PriceSymbol').value, priceUsdt: readNumber('l1Price', 6), usdVndRate: readNumber('l1MarkRate', 0, true) });
    return e;
  }
  function kindFields() { for (const k of ['TREASURY', 'TRADE', 'RESERVE', 'CASH', 'PRICE']) $('l1Fields' + k).hidden = $('l1Kind').value !== k; }

  /* -------- điều hướng: 4 điểm đến trong MỘT tài liệu cuộn được, refresh-safe --------
   * (không display:none các section — history/plan/settings phải luôn tương tác được cho
   * test_t12_browser.js vốn không bao giờ bấm điều hướng trước khi thao tác trên form). */
  function routeTo(view, behavior) {
    const el = $('view-' + view); if (!el) return;
    el.scrollIntoView({ behavior: behavior || 'smooth', block: 'start' });
    document.querySelectorAll('#bottomNav button').forEach(b => b.setAttribute('aria-current', String(b.dataset.view === view)));
    if (location.hash !== '#/' + view) history.replaceState(null, '', '#/' + view);
  }
  function viewFromHash() { const m = /^#\/(dashboard|history|plan|settings)/.exec(location.hash); return m ? m[1] : 'dashboard'; }

  /* -------- sheet "+ Ghi giao dịch": bước 1 chọn loại, tự set kind/dir/side/source/type -------- */
  function applyType(key) {
    const t = TX_TYPES.find(x => x.key === key); if (!t) return;
    if (t.special === 'opening') {
      routeTo('plan');
      const det = $('l1OpeningDate').closest('details'); if (det) det.open = true;
      $('l1OpeningDate').scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    currentTxType = key;
    $('l1Kind').value = t.kind;
    if (t.dir) $('l1Dir').value = t.dir;
    if (t.side) $('l1Side').value = t.side;
    if (t.source) $('l1Source').value = t.source;
    if (t.rtype) $('l1ReserveType').value = t.rtype;
    if (t.ctype) $('l1CashType').value = t.ctype;
    kindFields();
    document.querySelectorAll('.txtype').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.txtype === key)));
    $('l1NoteHint').textContent = t.noteRequired ? 'Bắt buộc: ghi lý do giải ngân dự phòng ở ô Ghi chú trước khi lưu.' : '';
    $('l1Entry').open = true;
    $('l1Entry').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function openEntry(fromView) {
    returnAnchor = fromView || viewFromHash();
    $('l1Entry').open = true;
    $('l1Entry').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function closeEntryReturn() {
    if (returnAnchor) { const a = returnAnchor; returnAnchor = null; routeTo(a); }
  }

  /* -------- Lịch sử: filter (mặc định = không lọc gì, giữ nguyên tương thích test) --------
   * `#histFilterType` (select ẩn) vẫn là nguồn sự thật cho GIÁ TRỊ đang chọn — hợp đồng cũ cho
   * test cũ đang query trực tiếp phần tử này; bộ nút `.histtype` chỉ đồng bộ giá trị vào đó rồi
   * gọi render() lại (T-17, mục 3 của task). */
  const HIST_FILTERS = [
    ['all', 'Tất cả loại'], ['TREASURY', 'P2P VND/USDT'], ['PLAN', 'Mua · Kế hoạch'],
    ['EXTRA', 'Mua · Ngoài kế hoạch'], ['RESERVE_BUY', 'Mua · Dự phòng'], ['SELL', 'Bán coin'],
    ['CASH', 'Tiền mặt VND'], ['RESERVE', 'Dự phòng nạp/rút'], ['PRICE', 'Giá tham chiếu'],
  ];
  function matchesHistType(e, type) {
    if (type === 'all') return true;
    if (type === 'RESERVE_BUY') return e.kind === 'TRADE' && e.source === 'RESERVE';
    if (type === 'SELL') return e.kind === 'TRADE' && e.side === 'SELL';
    if (type === 'PLAN' || type === 'EXTRA') return e.kind === 'TRADE' && e.side === 'BUY' && e.source === type;
    return e.kind === type;
  }
  function filterHistory(events) {
    const type = $('histFilterType') ? $('histFilterType').value : 'all';
    const from = $('histFrom') ? $('histFrom').value : '';
    const to = $('histTo') ? $('histTo').value : '';
    const q = $('histSearch') ? $('histSearch').value.trim().toLowerCase() : '';
    return events.filter(e => {
      if (!matchesHistType(e, type)) return false;
      if (from && e.businessDate < from) return false;
      if (to && e.businessDate > to) return false;
      if (q && !(e.note || '').toLowerCase().includes(q)) return false;
      return true;
    });
  }
  /** Đếm trên TOÀN BỘ s.events, không phụ thuộc bộ lọc ngày/tìm-kiếm đang áp — chỉ đúng loại
   *  (task T-17 mục 3). Nút đang chọn lấy `aria-pressed` từ giá trị hiện tại của select ẩn. */
  function renderHistFilterButtons(events) {
    const current = $('histFilterType').value;
    $('histFilterTypes').innerHTML = HIST_FILTERS.map(([type, label]) => {
      const n = events.filter(e => matchesHistType(e, type)).length;
      return '<button type="button" class="histtype" data-histfilter="' + type + '" aria-pressed="' + String(type === current) + '">' + escape(label) + ' (' + n + ')</button>';
    }).join('');
  }
  const KIND_LABEL = e => {
    if (e.kind === 'TREASURY') return e.dir === 'VND_TO_USDT' ? 'Đổi VND → USDT' : 'Đổi USDT → VND';
    // T-16: SELL tới được trở lại (T-15 đã bỏ nhãn này vì lúc đó eventCheck chặn ở cổng vào).
    if (e.kind === 'TRADE') return (e.side === 'SELL' ? 'Bán ' : 'Mua ') + e.symbol + (e.source === 'RESERVE' ? ' · Dự phòng' : '');
    if (e.kind === 'RESERVE') return e.type === 'CONTRIBUTE' ? 'Nạp dự phòng' : 'Rút dự phòng';
    if (e.kind === 'CASH') return e.type === 'DEPOSIT' ? 'Nạp tiền mặt' : 'Rút tiền mặt';
    return 'Giá tham chiếu ' + e.symbol;
  };
  /** T-17 mục 4: icon/màu ngắn theo loại giao dịch, CHỈ thêm cạnh badge/chip cũ, không thay thế gì.
   *  RESERVE giữ nguyên như trước task này (không icon riêng) theo đúng yêu cầu task. */
  const KIND_BADGE = e => {
    if (e.kind === 'TRADE') return e.side === 'SELL'
      ? '<span class="hc-kind hc-kind-sell" title="Bán">↓</span>'
      : '<span class="hc-kind hc-kind-buy" title="Mua">↑</span>';
    if (e.kind === 'CASH') return '<span class="hc-kind hc-kind-cash" title="Tiền mặt">$</span>';
    if (e.kind === 'TREASURY') return '<span class="hc-kind hc-kind-treasury" title="Đổi VND/USDT">⇄</span>';
    if (e.kind === 'PRICE') return '<span class="hc-kind hc-kind-price" title="Giá tham chiếu">≈</span>';
    return '';
  };
  function renderHistoryCards(d, s) {
    const today = L.clock().today;
    renderHistFilterButtons(s.events);
    const events = s.events.slice().sort((a, b) => b.businessDate.localeCompare(a.businessDate) || b.seq - a.seq);
    const filtered = filterHistory(events);
    const rows = filtered.map(e => {
      const eff = d.eventEffects[e.id], unknown = eff && eff.vndRelieved === null;
      const badge = e.kind === 'TRADE' && e.source && e.source !== 'PLAN' ? '<span class="chip ' + (e.source === 'EXTRA' ? 'y' : 'n') + '">' + e.source + '</span>' : '';
      const future = e.businessDate > today ? '<span class="chip r">TƯƠNG LAI</span>' : '';
      const unk = unknown ? '<span class="chip y" title="Liên quan tới UNKNOWN_VND_BASIS">—</span>' : '';
      const amount = e.kind === 'TREASURY' ? units(e.vndAmount) + ' ₫ / ' + units(e.usdtAmount, 6) + ' USDT'
        : e.kind === 'TRADE' ? units(e.qty, 8) + ' ' + e.symbol + ' · ' + units(e.usdtNotional, 6) + ' USDT'
        : e.kind === 'RESERVE' || e.kind === 'CASH' ? units(e.vndAmount) + ' ₫'
        : units(e.priceUsdt, 6) + ' USDT/' + e.symbol;
      return '<div class="hist-card" data-event="' + escape(e.id) + '">' +
        '<div class="hc-top">' + KIND_BADGE(e) + '<span class="hc-date">' + escape(e.businessDate) + '</span>' + badge + future + unk + '</div>' +
        '<div class="hc-main">' + escape(KIND_LABEL(e)) + '</div>' +
        '<div class="hc-amount">' + amount + '</div>' +
        (e.note ? '<div class="hc-note">' + escape(e.note) + '</div>' : '') +
        '<div class="hc-actions">' +
          '<button type="button" class="sm" data-id="' + escape(e.id) + '" data-action="edit">Sửa</button> ' +
          '<button type="button" class="sm danger" data-id="' + escape(e.id) + '" data-action="delete">Xoá</button>' +
        '</div></div>';
    }).join('');
    const openingCard = s.openingPosition ? '<div class="hist-card hist-opening"><div class="hc-top"><span class="hc-date">' + escape(s.openingPosition.asOf) + '</span></div><div class="hc-main">Số dư đầu kỳ</div><div class="hc-actions"><button type="button" class="sm" id="histEditOpening">Sửa</button></div></div>' : '';
    $('l1History').innerHTML = openingCard + (rows || '<p class="empty">Không có giao dịch nào khớp bộ lọc.</p>');
    const oe = $('histEditOpening');
    if (oe) oe.onclick = () => applyType('opening');
  }

  function prevMonthKey(m) { const y = +m.slice(0, 4), mm = +m.slice(5); return mm === 1 ? (y - 1) + '-12' : y + '-' + String(mm - 1).padStart(2, '0'); }

  function renderDashMain(d) {
    const m = d.month;
    const pct = (m.plannedBudgetVnd && m.plannedBudgetVnd > 0 && m.remainingPlannedBudgetVnd !== null)
      ? Math.max(0, Math.min(100, 100 - (m.remainingPlannedBudgetVnd / m.plannedBudgetVnd) * 100)) : null;
    const budgetSub = m.carryInVnd > 0 ? 'Gồm ' + units(m.carryInVnd) + ' ₫ chuyển từ tháng trước' : '';
    const investedSub = m.planInvestedVnd !== null && m.investedThisMonthVnd !== m.planInvestedVnd
      ? 'Theo kế hoạch ' + units(m.planInvestedVnd) + ' ₫ · phần EXTRA/RESERVE xem ở Lịch sử' : '';
    $('dashMain').innerHTML = [
      '<div class="dcard"><div class="dc-label">Ngân sách tháng</div><div class="dc-value">' + units(m.plannedBudgetVnd) + ' ₫</div>' + (budgetSub ? '<div class="dc-sub">' + escape(budgetSub) + '</div>' : '') + '</div>',
      '<div class="dcard"><div class="dc-label">Đã đầu tư tháng này</div><div class="dc-value">' + units(m.investedThisMonthVnd) + ' ₫</div>' + (investedSub ? '<div class="dc-sub">' + escape(investedSub) + '</div>' : '') + '</div>',
      '<div class="dcard"><div class="dc-label">Còn lại theo kế hoạch</div><div class="dc-value">' + units(m.remainingPlannedBudgetVnd) + ' ₫</div>' + (pct !== null ? '<div class="dc-bar"><div class="dc-fill" style="width:' + pct.toFixed(1) + '%"></div></div>' : '') + '</div>',
      '<div class="dcard"><div class="dc-label">Số dư dự phòng</div><div class="dc-value">' + units(d.reserve.balance) + ' ₫</div></div>',
      '<div class="dcard dcard-next"><div class="dc-label">Mua kế tiếp</div><div class="dc-value">' + (m.nextPlannedDate || '—') + '</div>' +
        '<div class="dc-sub">' + (m.nextPlannedAmountVnd !== null ? units(m.nextPlannedAmountVnd) + ' ₫ theo lịch' : 'Chưa có lịch mua') + '</div>' +
        (m.nextPlannedDate ? button('dashBuyNext', 'Ghi đã mua', 'primary sm') : '') + '</div>',
    ].join('');
    const btn = $('dashBuyNext');
    if (btn) btn.onclick = () => {
      applyType('buy_plan');
      $('l1NoteHint').textContent = m.nextPlannedAmountVnd !== null ? 'Gợi ý theo kế hoạch: ' + units(m.nextPlannedAmountVnd) + ' ₫ — bạn tự điền USDT/ETH đã khớp thật.' : '';
    };
  }
  /** T-16: một khối dòng cho MỖI coin đang nắm giữ. Định giá cũng theo từng coin — mỗi coin dùng
   *  PRICE mới nhất CỦA CHÍNH NÓ (derive() lo phần đó, kể cả hạn dùng 1 ngày và usdVndRate). */
  function holdingRows(d, s, today) {
    const rows = [];
    for (const symbol of Object.keys(d.holdings).sort()) {
      const h = d.holdings[symbol];
      if (!h.qty) continue;
      const v = d.valuation[symbol];
      const lastPrice = s.events.filter(e => e.kind === 'PRICE' && e.symbol === symbol && e.businessDate <= today).sort((a, b) => a.businessDate.localeCompare(b.businessDate)).slice(-1)[0];
      rows.push(['Đang nắm giữ (' + symbol + ')', units(h.qty, 8)]);
      rows.push(['Giá vốn TB ' + symbol + ' (USDT)', avg(h.avgCostUsdt, 1000000)]);
      rows.push(['Giá vốn TB ' + symbol + ' (VND)', avg(h.avgCostVnd)]);
      rows.push(['Định giá ' + symbol, v
        ? units(v.usdt, 6) + ' USDT' + (v.vnd === null ? '' : ' ≈ ' + units(v.vnd) + ' ₫') + ' (' + v.businessDate + ')'
        : (lastPrice ? '— · giá gần nhất ' + lastPrice.businessDate : '—')]);
    }
    return rows;
  }
  const statCell = (k, v, cls) => '<div class="stat"><small>' + escape(k) + '</small><div' + (cls ? ' class="' + cls + '"' : '') + '>' + escape(v) + '</div></div>';
  /** T-17 mục 1: tách lưới `.stat` phẳng cũ thành 3 khối có tiêu đề. Con số/nhãn hiển thị
   *  KHÔNG đổi — chỉ đổi cách nhóm trực quan; #dashBottom vẫn là id container ngoài duy nhất
   *  (test_stepb_ui.js đọc `#dashBottom .stat` — descendant selector, không phụ thuộc độ sâu lồng). */
  function renderDashBottom(d, s) {
    const today = L.clock().today;
    const holdRows = holdingRows(d, s, today);
    const holdBlock = holdRows.length ? holdRows.map(([k, v]) => statCell(k, v)).join('') : '<p class="empty">Chưa có coin nào.</p>';
    const cashBlock = [['USDT hiện có', units(d.usdt.qty, 6)], ['VND hiện có', units(d.vnd.balance)]].map(([k, v]) => statCell(k, v)).join('');
    // HAI đơn vị khác nhau, KHÔNG bao giờ cộng chung: lãi/lỗ khi bán coin nằm ở pool USDT;
    // lãi/lỗ VND chỉ phát sinh khi USDT đổi ngược ra VND.
    const pnlCell = (k, n, places) => statCell(k, units(n, places), n > 0 ? 'chip g' : n < 0 ? 'chip r' : '');
    const pnlBlock = pnlCell('Lãi/lỗ đã thực hiện (USDT)', d.realizedPnlUsdt, 6) + pnlCell('Lãi/lỗ tỷ giá đã thực hiện (VND)', d.realizedFxVnd, 0);
    $('dashBottom').innerHTML =
      '<div class="dashgroup"><h3 class="dashgroup-title">Đang nắm giữ</h3><div class="stats">' + holdBlock + '</div></div>' +
      '<div class="dashgroup"><h3 class="dashgroup-title">Tiền mặt &amp; USDT</h3><div class="stats">' + cashBlock + '</div></div>' +
      '<div class="dashgroup"><h3 class="dashgroup-title">Lãi/lỗ đã thực hiện</h3><div class="stats">' + pnlBlock + '</div>' +
        '<p class="dashgroup-note">Hai đơn vị khác nhau, không cộng chung.</p></div>';
  }
  function renderPlanCarry(d) {
    const m = d.month, prevKey = prevMonthKey(d.currentMonth), prevCarry = d.months[prevKey] ? d.months[prevKey].carryOutVnd : undefined;
    $('planCarry').innerHTML = [
      ['Ngân sách tháng (chưa gồm carry)', units(m.monthlyBudgetVnd) + ' ₫'],
      ['Carry tháng trước (đã đóng)', prevCarry === undefined ? '—' : units(prevCarry) + ' ₫'],
      ['→ Cộng vào ngân sách tháng này', units(m.carryInVnd) + ' ₫'],
      ['Đã đầu tư tháng này (tổng)', units(m.investedThisMonthVnd) + ' ₫'],
      ['Trong đó theo kế hoạch', units(m.planInvestedVnd) + ' ₫'],
    ].map(([k, v]) => '<div class="stat"><small>' + k + '</small><div>' + escape(v) + '</div></div>').join('');
  }
  function flagsBanner(d) {
    const labels = { LEDGER_INCONSISTENT: 'Sổ có xung đột dữ liệu', FUTURE_DATED_EVENTS: 'Có giao dịch ghi ngày trong tương lai', UNKNOWN_VND_BASIS: 'Một số giá vốn VND chưa xác định — xem "—" ở Tổng quan/Lịch sử/Kế hoạch, sửa ở Kế hoạch → Số dư đầu kỳ' };
    if (!d.flags.length) return '';
    return d.flags.map(f => (labels[f] || f) + ' (' + f + ')').join(' · ') + (d.firstOffendingEventId ? ' · Event đầu tiên: ' + d.firstOffendingEventId + ' (' + d.firstOffendingBusinessDate + ')' : '');
  }

  function mount(h) {
    hooks = h;
    if (mounted) return; mounted = true;
    const today = L.clock().today, month = today.slice(0, 7);
    $('l1Root').innerHTML =
      '<section class="view-sec" id="view-dashboard">' +
        '<h2>Tổng quan</h2>' +
        '<div id="l1Flags" role="alert"></div>' +
        '<h3 class="dashgroup-title">Kế hoạch tháng này</h3>' +
        '<div class="dashmain" id="dashMain"></div>' +
        '<div class="dashbottom-groups" id="dashBottom"></div>' +
        '<details><summary>Thông số kỹ thuật (đối chiếu/kiểm thử)</summary><div class="stats" id="l1Summary"></div></details>' +
        '<p id="l1Message" role="status"></p>' +
      '</section>' +

      '<details open id="l1Entry">' +
        '<summary>+ Ghi giao dịch</summary>' +
        '<div class="txtypes">' + TX_TYPES.map(t => '<button type="button" class="txtype" data-txtype="' + t.key + '">' + t.label + '</button>').join('') + '</div>' +
        '<p id="l1NoteHint"></p>' +
        '<div class="txtech"><small class="hint">Chi tiết kỹ thuật (tự set theo loại đã chọn ở trên — vẫn sửa được):</small><div class="form">' +
          select('l1Kind', 'Loại', [['TREASURY', 'Đổi VND / USDT'], ['TRADE', 'Mua / bán coin'], ['CASH', 'Tiền mặt VND'], ['RESERVE', 'Dự phòng'], ['PRICE', 'Giá tham khảo']]) +
          input('l1Date', 'Ngày giao dịch (businessDate)', 'date', today) + input('l1Note', 'Ghi chú / lý do giải ngân dự phòng') + '</div>' +
        '<div id="l1FieldsTREASURY" class="form">' + select('l1Dir', 'Chiều', [['VND_TO_USDT', 'VND → USDT'], ['USDT_TO_VND', 'USDT → VND']]) + input('l1P2pVnd', 'VND thực trả / nhận (đã gồm phí)', 'text', '', true) + input('l1P2pUsdt', 'USDT thực nhận / trả', 'text', '', true) + input('l1Counterparty', 'Đối tác (tùy chọn)') + '</div>' +
        '<div id="l1FieldsTRADE" class="form">' + select('l1Symbol', 'Tài sản', symbolChoices()) + select('l1Side', 'Chiều', [['BUY', 'Mua'], ['SELL', 'Bán']]) + select('l1Source', 'Nguồn', [['PLAN', 'Theo kế hoạch'], ['EXTRA', 'Mua thêm'], ['RESERVE', 'Dự phòng']]) + input('l1Notional', 'USDT khớp lệnh', 'text', '', true) + input('l1Fee', 'Phí USDT', 'text', '0', true) + input('l1Qty', 'Lượng coin thực nhận / bán ra', 'text', '', true) + '<p class="hint">Nguồn “Theo kế hoạch” chỉ dùng được cho đúng coin của kế hoạch; mua coin khác hãy chọn “Mua thêm”.</p></div>' +
        '<div id="l1FieldsRESERVE" class="form">' + select('l1ReserveType', 'Thao tác dự phòng', [['CONTRIBUTE', 'Đóng góp'], ['WITHDRAW', 'Rút earmark']]) + input('l1ReserveAmount', 'Số tiền VND', 'text', '', true) + '</div>' +
        '<div id="l1FieldsCASH" class="form">' + select('l1CashType', 'Thao tác tiền mặt', [['DEPOSIT', 'Nạp vào ví'], ['WITHDRAW', 'Rút ra tiêu']]) + input('l1CashAmount', 'Số tiền VND', 'text', '', true) + '<p class="hint">Ghi việc BỎ TIỀN vào ví hoặc rút ra tiêu. Khác với “Đổi VND / USDT” — đó là một cuộc đổi hai chân, không phải tiền từ đâu vào.</p></div>' +
        '<div id="l1FieldsPRICE" class="form">' + select('l1PriceSymbol', 'Tài sản', symbolChoices()) + input('l1Price', 'Giá coin (USDT)', 'text', '', true) + input('l1MarkRate', 'USDT/VND để quy đổi định giá (tùy chọn)', 'text', '', true) + '</div>' +
        '<div class="formfoot">' + button('l1SaveEvent', 'Lưu giao dịch', 'primary') + button('l1CancelEdit', 'Hủy sửa') + '</div></div>' +
      '</details>' +

      '<section class="view-sec" id="view-history">' +
        '<h2>Lịch sử</h2>' +
        '<div class="histfilter">' +
          '<div class="histtypes" id="histFilterTypes"></div>' +
          /* T-17 mục 3: #histFilterType GIỮ NGUYÊN id/hành vi (value = nguồn sự thật cho loại đang
           * chọn) nhưng ẩn khỏi mắt — bộ nút .histtype ở trên đồng bộ giá trị vào đây rồi render()
           * lại. Không test nào đang selectOption trực tiếp phần tử này (đã soát test_t12_browser.js/
           * test_stepb_ui.js), nên đây là lựa chọn AN TOÀN nhất, không cần sửa test nào. */
          '<select id="histFilterType" hidden aria-hidden="true"><option value="all">Tất cả loại</option><option value="TREASURY">P2P VND/USDT</option><option value="PLAN">Mua · Kế hoạch</option><option value="EXTRA">Mua · Ngoài kế hoạch</option><option value="RESERVE_BUY">Mua · Dự phòng</option><option value="SELL">Bán coin</option><option value="CASH">Tiền mặt VND</option><option value="RESERVE">Dự phòng nạp/rút</option><option value="PRICE">Giá tham chiếu</option></select>' +
          '<div class="histfilter-row"><input type="date" id="histFrom" aria-label="Từ ngày"><input type="date" id="histTo" aria-label="Đến ngày">' +
          '<input type="text" id="histSearch" placeholder="Tìm theo ghi chú" aria-label="Tìm theo ghi chú"></div>' +
        '</div>' +
        '<div id="l1History"></div>' +
      '</section>' +

      '<section class="view-sec" id="view-plan">' +
        '<h2>Kế hoạch</h2>' +
        '<div class="stats" id="planCarry"></div>' +
        '<details><summary>Ngân sách &amp; lịch mua</summary><div class="form">' + input('l1StartMonth', 'Tháng bắt đầu', 'month', month) + select('l1PlanAsset', 'Coin của kế hoạch', symbolChoices()) + input('l1Effective', 'Áp dụng từ tháng', 'month', month) + input('l1Budget', 'Ngân sách VND', 'text', '20000000', true) + input('l1Days', 'Các ngày mua, cách nhau bằng dấu phẩy', 'text', '3,13,23') + '</div><p class="hint">Version đã lưu là bất biến: không đổi được ngân sách hay lịch của nó. Muốn đổi, hãy đặt \u201cÁp dụng từ tháng\u201d là tháng hiện tại hoặc muộn hơn để tạo version mới. \u201cTháng bắt đầu\u201d không được sớm hơn tháng áp dụng của version đầu tiên. Một kế hoạch chỉ nhắm MỘT coin: sau version đầu tiên, ô \u201cCoin của kế hoạch\u201d bị khoá theo coin đó.</p>' + button('l1SavePlan', 'Lưu kế hoạch', 'primary') + '</details>' +
        '<details><summary>Số dư đầu kỳ</summary><p class="hint">Để trống giá vốn khi chưa biết; số 0 nghĩa là giá vốn bằng 0. Mỗi lần lưu chỉ sửa MỘT coin (chọn ở ô Tài sản); các coin khác trong số dư đầu kỳ giữ nguyên. Lượng 0 và bỏ trống giá vốn = xoá coin đó khỏi số dư đầu kỳ.</p><div class="form">' + input('l1OpeningDate', 'Ngày đầu kỳ', 'date', today) + select('l1OpeningSymbol', 'Tài sản', symbolChoices()) + input('l1Eth', 'Lượng coin đang có', 'text', '0', true) + input('l1EthCostUsdt', 'Tổng giá vốn coin (USDT)', 'text', '', true) + input('l1EthCostVnd', 'Tổng giá vốn coin (VND)', 'text', '', true) + input('l1Usdt', 'USDT đang có', 'text', '0', true) + input('l1UsdtCost', 'Tổng giá vốn USDT (VND)', 'text', '', true) + input('l1Vnd', 'VND đang có', 'text', '0', true) + input('l1Reserve', 'Dự phòng VND đầu kỳ', 'text', '0', true) + input('l1OpeningNote', 'Ghi chú đầu kỳ') + '</div>' + button('l1SaveOpening', 'Lưu số dư đầu kỳ', 'primary') + button('l1DeleteOpening', 'Xóa số dư đầu kỳ', 'danger') + '<p class="hint">Sửa/xoá số dư đầu kỳ có thể khiến phần lớn giá vốn trở thành KHÔNG XÁC ĐỊNH.</p></details>' +
        '<details id="l1MigrationV3" hidden><summary>Nâng cấp sổ lên schema 3 (đa tài sản)</summary><p>Sổ đang ở <code>' + escape(L.SCHEMA_V2) + '</code>. Bản nâng cấp chỉ đổi nhãn schema; nội dung sổ được đối chiếu bằng một replay độc lập trước khi ghi, và bị từ chối nếu lệch dù một đồng.</p>' + button('l1MigrateV3', 'Đối chiếu và nâng cấp', 'primary') + '</details>' +
        '<details id="l1Migration" hidden><summary>Chuyển sổ legacy</summary><p>Nhập kế hoạch và số dư đầu kỳ ở trên. Xác nhận ngày và thứ tự từng giao dịch bên dưới; ngày bấm nút cũ chỉ để tham khảo. Mọi trade cũ trở thành mua thêm.</p>' + select('l1Contributions', 'VND đóng góp cũ', [['', 'Chọn cách xử lý'], ['opening', 'Đã đưa vào VND đầu kỳ ở trên'], ['ignore', 'Bỏ bản ghi contribution']]) + '<div id="l1MigrationDates"></div>' + button('l1Migrate', 'Xác nhận và chuyển sổ', 'primary') + '</details>' +
      '</section>';

    $('l1SettingsExtra').innerHTML =
      '<div class="card"><h3>Dữ liệu của bạn</h3><div class="formfoot" style="margin-top:0">' +
        button('l1Export', 'Tải về JSON') + input('l1Import', 'Nạp lại từ JSON', 'file') + button('l1Wipe', 'Xóa sổ', 'danger') + '</div></div>';

    // Mặc định của mọi ô chọn tài sản là ETH (coin duy nhất của sổ trước T-16); render() sẽ
    // đồng bộ ô của form giao dịch/giá theo coin của kế hoạch khi kế hoạch đã có version.
    for (const id of ['l1Symbol', 'l1PriceSymbol', 'l1OpeningSymbol', 'l1PlanAsset']) $(id).value = 'ETH';
    $('l1Kind').onchange = kindFields; kindFields();
    $('l1OpeningSymbol').onchange = () => { const st = hooks.state(); fillOpeningAsset(st.schema === L.SCHEMA ? st.openingPosition : null); };
    $('l1MigrateV3').onclick = run(() => destroy('Nâng cấp sổ lên ' + L.SCHEMA + '?', () => L.migrateV3(hooks.raw() || hooks.state(), meta())));
    $('l1SavePlan').onclick = run(() => commit(L.update(hooks.state(), { type: 'plan', value: planInput() }, meta())));
    $('l1SaveOpening').onclick = run(() => commit(L.update(hooks.state(), { type: 'opening', value: openingInput() }, meta())));
    $('l1DeleteOpening').onclick = run(() => destroy('Xóa đầu kỳ có thể làm mất giá vốn đã biết.', () => ({ ok: true, state: L.update(hooks.state(), { type: 'opening', value: null }, meta()) })));
    $('l1SaveEvent').onclick = run(() => {
      const value = eventInput();
      if (value.kind === 'TRADE' && value.source === 'RESERVE' && !value.note.trim()) throw new Error('Giải ngân dự phòng cần lý do — nhập ghi chú trước khi lưu.');
      const s = L.update(hooks.state(), { type: 'event', id: editId, value }, meta());
      commit(s); editId = null; currentTxType = null; $('l1SaveEvent').textContent = 'Lưu giao dịch';
      closeEntryReturn();
    });
    $('l1CancelEdit').onclick = () => { editId = null; currentTxType = null; $('l1SaveEvent').textContent = 'Lưu giao dịch'; document.querySelectorAll('.txtype').forEach(b => b.removeAttribute('aria-pressed')); message('Đã hủy sửa.'); };
    $('l1Export').onclick = () => { try { const p = exportPayload(); download(p, 'coindca-ledger-' + stamp(p.exportedAt) + '.json'); } catch (e) { message(e.message); } };
    // Khôi phục (§8.2): đọc file -> XEM TRƯỚC + validate dry-run -> (chỉ khi hợp lệ) snapshot ->
    // xác nhận dựa trên bản tóm tắt -> ghi nguyên tử qua L.destructive -> chờ máy chủ xác nhận.
    $('l1Import').onchange = async () => {
      const el = $('l1Import'), file = el.files[0];
      if (!file) return;
      try {
        writable();
        const preview = restorePreview(await file.text());
        message(preview.summary);                      // hiện TRƯỚC dialog xác nhận
        if (!preview.ok) return;                       // dừng trước mọi mutation bền
        const result = await L.destructive(hooks.raw() || hooks.state(), () => ({ ok: true, state: preview.state }),
          { snapshot: restoreSnapshot, commit,
            confirm: () => window.confirm('Thay TOÀN BỘ sổ bằng file này?\n' + preview.summary +
              '\nBản đầy đủ hiện tại đã được xuất ra coindca-before-restore-*.json trước thao tác này.') });
        message(result.ok ? 'Đã khôi phục từ backup; chờ xác nhận lưu bền. ' + preview.summary
          : (result.cancelled ? 'Đã hủy khôi phục; sổ giữ nguyên, snapshot vẫn có.'
            : (result.errors || ['Khôi phục thất bại']).join('\n')));
      } catch (e) { message(e.message); } finally { el.value = ''; }
    };
    $('l1Wipe').onclick = run(() => destroy('Xóa toàn bộ sổ?', () => ({ ok: true, state: L.empty(L.clock().today.slice(0, 7)) })));
    $('l1Migrate').onclick = run(() => destroy('Chuyển sổ legacy sau khi đã xác nhận từng ngày?', () => {
      const dates = {}; document.querySelectorAll('[data-migration-key]').forEach(el => { dates[el.dataset.migrationKey] = { businessDate: el.value, order: Number($(el.id + 'Order').value) }; });
      return L.migrate(hooks.state(), { plan: planInput(), openingPosition: openingInput(), contributions: $('l1Contributions').value, dates }, meta(), hooks.seed());
    }));
    $('l1History').onclick = async ev => {
      const b = ev.target.closest('button[data-id]'); if (!b) return;
      await run(async () => {
        const e = hooks.state().events.find(e => e.id === b.dataset.id); if (!e) throw new Error('Event không còn tồn tại');
        if (b.dataset.action === 'delete') return destroy('Xóa giao dịch ' + e.businessDate + '?', () => ({ ok: true, state: L.update(hooks.state(), { type: 'delete', id: e.id }, meta()) }));
        editId = e.id; $('l1Kind').value = e.kind; $('l1Date').value = e.businessDate; $('l1Note').value = e.note;
        const fields = { dir: ['l1Dir', 0], vndAmount: [e.kind === 'RESERVE' ? 'l1ReserveAmount' : e.kind === 'CASH' ? 'l1CashAmount' : 'l1P2pVnd', 0], usdtAmount: ['l1P2pUsdt', 6], side: ['l1Side', 0], symbol: [e.kind === 'PRICE' ? 'l1PriceSymbol' : 'l1Symbol', 0], source: ['l1Source', 0], usdtNotional: ['l1Notional', 6], feeUsdt: ['l1Fee', 6], qty: ['l1Qty', 8], type: [e.kind === 'CASH' ? 'l1CashType' : 'l1ReserveType', 0], priceUsdt: ['l1Price', 6], usdVndRate: ['l1MarkRate', 0], counterparty: ['l1Counterparty', 0] };
        for (const [key, [id, places]] of Object.entries(fields)) if (key in e) $(id).value = e[key] === null ? '' : typeof e[key] === 'number' ? (e[key] / 10 ** places).toFixed(places) : e[key];
        kindFields(); $('l1Entry').open = true; $('l1SaveEvent').textContent = 'Lưu sửa giao dịch';
        $('l1Entry').scrollIntoView({ behavior: 'smooth', block: 'start' });
        return 'Đang sửa ' + e.id;
      })();
    };
    document.querySelectorAll('.txtype').forEach(b => { b.onclick = () => applyType(b.dataset.txtype); });
    $('histFilterTypes').onclick = ev => {
      const b = ev.target.closest('button[data-histfilter]'); if (!b) return;
      $('histFilterType').value = b.dataset.histfilter;
      render();
    };
    for (const id of ['histFilterType', 'histFrom', 'histTo']) $(id).onchange = () => render();
    $('histSearch').oninput = () => render();

    document.querySelectorAll('#bottomNav button').forEach(b => { b.onclick = () => routeTo(b.dataset.view); });
    $('fabEntry').onclick = () => openEntry();
    window.addEventListener('hashchange', () => routeTo(viewFromHash(), 'auto'));
    routeTo(viewFromHash(), 'auto');
  }

  function render() {
    if (!mounted) return;
    const s = hooks.state(), legacy = s.schema !== L.SCHEMA, isV2 = s.schema === L.SCHEMA_V2;
    // T-16: HAI đường nâng cấp khác nhau. `ethdca.tracker/1` = sổ app cũ (migrate, cần xác nhận
    // từng ngày). `coindca.ledger/2` = sổ L-1 trước đa tài sản (migrateV3, chỉ đổi nhãn schema
    // nhưng vẫn phải qua oracle). Không đường nào tự chạy: cả hai đều do Owner bấm.
    $('l1Migration').hidden = !legacy || isV2;
    $('l1MigrationV3').hidden = !isV2;
    for (const id of ['l1SavePlan', 'l1SaveOpening', 'l1SaveEvent', 'l1DeleteOpening']) $(id).disabled = legacy;
    if (legacy) {
      $('l1Flags').textContent = isV2
        ? 'SỔ SCHEMA 2 — CHỈ ĐỌC. Nâng cấp lên ' + L.SCHEMA + ' (Kế hoạch → Nâng cấp sổ) trước khi ghi giao dịch mới.'
        : 'LEGACY — CHỈ ĐỌC. Cần xác nhận migration trước khi ghi giao dịch L-1.';
      $('l1Summary').textContent = ''; $('dashMain').innerHTML = ''; $('dashBottom').innerHTML = ''; $('planCarry').innerHTML = '';
      $('l1History').textContent = 'Nguồn hiện tại được giữ nguyên; có thể xuất JSON đầy đủ.';
      if (isV2) return;
      if (shownLegacy !== s) {
        shownLegacy = s; let i = 0;
        $('l1MigrationDates').innerHTML = ['p2p', 'trades'].flatMap(k => s[k].map((r, n) => { const id = 'l1MigrationDate' + i++; return '<label>' + k + '[' + n + '] · thời điểm nhập cũ: ' + escape(r.ts) + '<input type="date" id="' + id + '" data-migration-key="' + k + '[' + n + ']"></label>' + input(id + 'Order', 'Thứ tự xác nhận', 'number', i); })).join('');
      }
      return;
    }
    if (lastFormState !== s) {
      lastFormState = s;
      const p = s.plan.versions.slice().sort((a, b) => a.effectiveFrom.localeCompare(b.effectiveFrom)).slice(-1)[0];
      $('l1StartMonth').value = s.plan.startMonth;
      // Kế hoạch đơn tài sản: khi đã có version, ô coin khoá lại theo asset của kế hoạch.
      $('l1PlanAsset').value = s.plan.versions.length ? s.plan.versions[0].asset : $('l1PlanAsset').value;
      $('l1PlanAsset').disabled = s.plan.versions.length > 0;
      if (s.plan.versions.length) for (const id of ['l1Symbol', 'l1PriceSymbol']) $(id).value = s.plan.versions[0].asset;
      if (p) { $('l1Effective').value = p.effectiveFrom; $('l1Budget').value = p.monthlyBudgetVnd; $('l1Days').value = p.scheduleDays.join(','); }
      const o = s.openingPosition;
      if (o) {
        $('l1OpeningDate').value = o.asOf; $('l1OpeningNote').value = o.note;
        fillOpeningAsset(o);
        for (const [id, amount, places] of [['l1Usdt', o.usdt.qty, 6], ['l1UsdtCost', o.usdt.costVnd, 0], ['l1Vnd', o.vnd ? o.vnd.qty : 0, 0], ['l1Reserve', o.reserveVnd || 0, 0]]) $(id).value = amount === null ? '' : (amount / 10 ** places).toFixed(places);
      }
    }
    // MỘT lệnh gọi derive() cho toàn bộ Tổng quan/Lịch sử/Kế hoạch (CHECK-T13-10).
    const d = L.derive(s.openingPosition, s.plan, s.events, L.clock().today);
    $('l1Flags').textContent = flagsBanner(d);
    renderDashMain(d);
    renderDashBottom(d, s);
    renderPlanCarry(d);
    const values = [['Tháng', d.currentMonth], ['Ngân sách tháng', units(d.month.monthlyBudgetVnd)], ['Carry từ tháng trước', units(d.month.carryInVnd)], ['Ngân sách gồm carry', units(d.month.plannedBudgetVnd)], ['Đã đầu tư', units(d.month.investedThisMonthVnd)], ['Theo kế hoạch', units(d.month.planInvestedVnd)], ['Còn lại theo kế hoạch', units(d.month.remainingPlannedBudgetVnd)], ['Dự phòng', units(d.reserve.balance)], ['Mua kế tiếp', (d.month.nextPlannedDate || '—') + ' · ' + units(d.month.nextPlannedAmountVnd) + ' VND']]
      .concat(Object.keys(d.holdings).sort().flatMap(sym => [[sym, units(d.holdings[sym].qty, 8)], ['Giá vốn TB ' + sym + ' (USDT)', avg(d.holdings[sym].avgCostUsdt, 1000000)], ['Giá vốn TB ' + sym + ' (VND)', avg(d.holdings[sym].avgCostVnd)]]))
      .concat([['USDT', units(d.usdt.qty, 6)], ['Giá vốn pool USDT (VND)', units(d.usdt.costVnd)], ['VND', units(d.vnd.balance)], ['Lãi/lỗ đã thực hiện (USDT)', units(d.realizedPnlUsdt, 6)], ['Lãi/lỗ tỷ giá (VND)', units(d.realizedFxVnd)]]);
    $('l1Summary').innerHTML = values.map(([name, value]) => '<div class="stat"><small>' + name + '</small><div>' + escape(value) + '</div></div>').join('');
    renderHistoryCards(d, s);
    $('foot').textContent = 'CoinDCA L-1 · rev ' + s.rev;
  }
  window.CoinLedgerUI = Object.freeze({ mount, render });
})();
