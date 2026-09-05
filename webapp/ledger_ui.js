/* Minimal L-1 adapter: existing document, persistence acknowledgements and page shell. */
(function () {
  'use strict';
  const L = window.CoinLedger, $ = id => document.getElementById(id);
  const escape = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const units = (n, places = 0) => n === null ? '—' : (n / 10 ** places).toLocaleString('vi-VN', { maximumFractionDigits: places });
  const avg = (r, scale = 1) => r === null ? '—' : (Number(r.numerator) / Number(r.denominator) / scale).toLocaleString('vi-VN', { maximumFractionDigits: 8 });
  const input = (id, label, type = 'text', value = '') => '<label>' + label + '<input id="' + id + '" type="' + type + '" value="' + escape(value) + '"></label>';
  const select = (id, label, choices) => '<label>' + label + '<select id="' + id + '">' + choices.map(([v, t]) => '<option value="' + v + '">' + t + '</option>').join('') + '</select></label>';
  const button = (id, label) => '<button type="button" id="' + id + '">' + label + '</button>';
  let hooks, mounted = false, editId = null, shownLegacy = null;
  function download(value, name) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
    const a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  function snapshot(value) {
    const payload = { state: value, seed: hooks.seed(), snapshotAt: L.clock().instant };
    localStorage.setItem('coindca-last-snapshot', JSON.stringify(payload));
    download(payload, 'coindca-before-change.json');
  }
  function writable() { if (!hooks.canWrite()) throw new Error('Nguồn bền chưa sẵn sàng hoặc đang lưu; xem trạng thái đầu trang.'); }
  function meta() { return Object.assign({ id: crypto.randomUUID() }, L.clock()); }
  function commit(value) { writable(); hooks.commit(value); }
  function message(text) { $('l1Message').textContent = text; }
  function run(fn) { return async () => { try { writable(); const result = await fn(); message(result || 'Đã cập nhật sổ; xem xác nhận lưu bền đầu trang.'); } catch (e) { message(e.message); } }; }
  function readNumber(id, places = 0, nullable = false) { const v = $(id).value.trim(); return !v && nullable ? null : L.decimal(v, places); }
  function openingInput() {
    return { asOf: $('l1OpeningDate').value, assets: [{ symbol: 'ETH', qty: readNumber('l1Eth', 8), costUsdt: readNumber('l1EthCostUsdt', 6, true), costVnd: readNumber('l1EthCostVnd', 0, true) }], usdt: { qty: readNumber('l1Usdt', 6), costVnd: readNumber('l1UsdtCost', 0, true) }, vnd: { qty: readNumber('l1Vnd') }, reserveVnd: readNumber('l1Reserve'), note: $('l1OpeningNote').value };
  }
  function planInput() {
    const current = hooks.state(), plan = current.schema === L.SCHEMA ? L.clone(current.plan) : { startMonth: $('l1StartMonth').value, versions: [] };
    plan.startMonth = $('l1StartMonth').value;
    const effectiveFrom = $('l1Effective').value, old = plan.versions.find(v => v.effectiveFrom === effectiveFrom);
    const p = { id: old ? old.id : crypto.randomUUID(), effectiveFrom, asset: 'ETH', monthlyBudgetVnd: readNumber('l1Budget'), scheduleDays: $('l1Days').value.split(',').map(x => Number(x.trim())), carryPolicy: 'CAPPED_CARRY', carryCapMonths: 1 };
    if (old) plan.versions[plan.versions.indexOf(old)] = p; else plan.versions.push(p);
    return plan;
  }
  async function destroy(label, operation) {
    writable();
    const result = await L.destructive(hooks.raw() || hooks.state(), operation, { snapshot, confirm: () => window.confirm(label + ' Bản đầy đủ đã được xuất trước thao tác này.'), commit });
    if (!result.ok) return result.cancelled ? 'Đã hủy; sổ giữ nguyên, snapshot vẫn có.' : (result.errors || ['Thao tác thất bại']).join('\n') + '\n' + JSON.stringify(result.deltas || {});
    return result.warnings ? result.warnings.join(', ') + '\nĐối chiếu: ' + JSON.stringify(result.deltas) : 'Đã cập nhật; chờ xác nhận lưu bền.';
  }
  function eventInput() {
    const kind = $('l1Kind').value, e = { kind, businessDate: $('l1Date').value, note: $('l1Note').value };
    if (kind === 'TREASURY') Object.assign(e, { dir: $('l1Dir').value, vndAmount: readNumber('l1P2pVnd'), usdtAmount: readNumber('l1P2pUsdt', 6), counterparty: $('l1Counterparty').value });
    if (kind === 'TRADE') Object.assign(e, { side: $('l1Side').value, symbol: 'ETH', source: $('l1Source').value, usdtNotional: readNumber('l1Notional', 6), feeUsdt: readNumber('l1Fee', 6), qty: readNumber('l1Qty', 8) });
    if (kind === 'RESERVE') Object.assign(e, { type: $('l1ReserveType').value, vndAmount: readNumber('l1ReserveAmount') });
    if (kind === 'PRICE') Object.assign(e, { symbol: 'ETH', priceUsdt: readNumber('l1Price', 6), usdVndRate: readNumber('l1MarkRate', 0, true) });
    return e;
  }
  function kindFields() { for (const k of ['TREASURY', 'TRADE', 'RESERVE', 'PRICE']) $('l1Fields' + k).hidden = $('l1Kind').value !== k; }
  function mount(h) {
    hooks = h;
    if (mounted) return; mounted = true;
    document.querySelectorAll('nav.tabs,.panel').forEach(x => { x.hidden = true; x.style.display = 'none'; });
    document.querySelector('header.top h1').textContent = 'CoinDCA L-1';
    document.querySelector('header.top .sub').textContent = 'Sổ giao dịch và kế hoạch DCA do bạn nhập.';
    const today = L.clock().today, month = today.slice(0, 7);
    $('l1Root').innerHTML = '<p class="note">Chỉ dùng dữ liệu tổng hợp cho T-12. Điều kiện dùng tiền thật và kiểm chứng E2 vẫn chưa hoàn tất.</p><div id="l1Flags" role="alert"></div><div class="stats" id="l1Summary"></div><p id="l1Message" role="status"></p>' +
      '<details><summary>Kế hoạch tháng</summary><div class="formgrid">' + input('l1StartMonth', 'Tháng bắt đầu', 'month', month) + input('l1Effective', 'Áp dụng từ tháng', 'month', month) + input('l1Budget', 'Ngân sách VND', 'text', '20000000') + input('l1Days', 'Các ngày mua, cách nhau bằng dấu phẩy', 'text', '3,13,23') + '</div>' + button('l1SavePlan', 'Lưu kế hoạch') + '</details>' +
      '<details><summary>Số dư đầu kỳ</summary><p>Để trống giá vốn khi chưa biết; số 0 có nghĩa là giá vốn bằng 0.</p><div class="formgrid">' + input('l1OpeningDate', 'Ngày đầu kỳ', 'date', today) + input('l1Eth', 'ETH đang có', 'text', '0') + input('l1EthCostUsdt', 'Tổng giá vốn ETH (USDT)') + input('l1EthCostVnd', 'Tổng giá vốn ETH (VND)') + input('l1Usdt', 'USDT đang có', 'text', '0') + input('l1UsdtCost', 'Tổng giá vốn USDT (VND)') + input('l1Vnd', 'VND đang có', 'text', '0') + input('l1Reserve', 'Dự phòng VND đầu kỳ', 'text', '0') + input('l1OpeningNote', 'Ghi chú đầu kỳ') + '</div>' + button('l1SaveOpening', 'Lưu số dư đầu kỳ') + button('l1DeleteOpening', 'Xóa số dư đầu kỳ') + '</details>' +
      '<details open id="l1Entry"><summary>Ghi / sửa giao dịch</summary><div class="formgrid">' + select('l1Kind', 'Loại', [['TREASURY', 'Đổi VND / USDT'], ['TRADE', 'Mua / bán ETH'], ['RESERVE', 'Đóng góp / rút dự phòng'], ['PRICE', 'Giá tham khảo']]) + input('l1Date', 'Ngày giao dịch', 'date', today) + input('l1Note', 'Ghi chú / lý do giải ngân dự phòng') + '</div>' +
      '<div id="l1FieldsTREASURY" class="formgrid">' + select('l1Dir', 'Chiều', [['VND_TO_USDT', 'VND → USDT'], ['USDT_TO_VND', 'USDT → VND']]) + input('l1P2pVnd', 'VND thực trả / nhận (đã gồm phí)') + input('l1P2pUsdt', 'USDT thực nhận / trả') + input('l1Counterparty', 'Đối tác (tùy chọn)') + '</div>' +
      '<div id="l1FieldsTRADE" class="formgrid">' + select('l1Side', 'Chiều giao dịch', [['BUY', 'Mua'], ['SELL', 'Bán']]) + select('l1Source', 'Nguồn', [['PLAN', 'Theo kế hoạch'], ['EXTRA', 'Mua thêm'], ['RESERVE', 'Dự phòng']]) + input('l1Notional', 'USDT khớp lệnh') + input('l1Fee', 'Phí USDT', 'text', '0') + input('l1Qty', 'Lượng ETH thực nhận / bán') + '</div>' +
      '<div id="l1FieldsRESERVE" class="formgrid">' + select('l1ReserveType', 'Thao tác dự phòng', [['CONTRIBUTE', 'Đóng góp'], ['WITHDRAW', 'Rút earmark']]) + input('l1ReserveAmount', 'Số tiền VND') + '</div>' +
      '<div id="l1FieldsPRICE" class="formgrid">' + input('l1Price', 'Giá ETH (USDT), chỉ định giá') + input('l1MarkRate', 'USDT/VND tham khảo (tùy chọn)') + '</div>' + button('l1SaveEvent', 'Lưu giao dịch') + button('l1CancelEdit', 'Hủy sửa') + '</details><h3>Lịch sử</h3><div id="l1History"></div>' +
      '<details><summary>Xuất / nhập / xóa sổ</summary>' + button('l1Export', 'Tải về JSON') + input('l1Import', 'Nạp JSON', 'file') + button('l1Wipe', 'Xóa sổ') + '</details><details id="l1Migration" hidden><summary>Chuyển sổ legacy</summary><p>Nhập kế hoạch và số dư đầu kỳ ở trên. Xác nhận ngày và thứ tự từng giao dịch bên dưới; ngày bấm nút cũ chỉ để tham khảo. Mọi trade cũ trở thành mua thêm.</p>' + select('l1Contributions', 'VND đóng góp cũ', [['', 'Chọn cách xử lý'], ['opening', 'Đã đưa vào VND đầu kỳ ở trên'], ['ignore', 'Bỏ bản ghi contribution']]) + '<div id="l1MigrationDates"></div>' + button('l1Migrate', 'Xác nhận và chuyển sổ') + '</details>';
    $('l1Kind').onchange = kindFields; kindFields();
    $('l1SavePlan').onclick = run(() => commit(L.update(hooks.state(), { type: 'plan', value: planInput() }, meta())));
    $('l1SaveOpening').onclick = run(() => commit(L.update(hooks.state(), { type: 'opening', value: openingInput() }, meta())));
    $('l1DeleteOpening').onclick = run(() => destroy('Xóa đầu kỳ có thể làm mất giá vốn đã biết.', () => ({ ok: true, state: L.update(hooks.state(), { type: 'opening', value: null }, meta()) })));
    $('l1SaveEvent').onclick = run(() => { const s = L.update(hooks.state(), { type: 'event', id: editId, value: eventInput() }, meta()); commit(s); editId = null; $('l1SaveEvent').textContent = 'Lưu giao dịch'; });
    $('l1CancelEdit').onclick = () => { editId = null; $('l1SaveEvent').textContent = 'Lưu giao dịch'; message('Đã hủy sửa.'); };
    $('l1Export').onclick = () => { try { download({ state: hooks.raw() || hooks.state(), seed: hooks.seed() }, 'coindca-ledger.json'); } catch (e) { message(e.message); } };
    $('l1Import').onchange = run(async () => { const file = $('l1Import').files[0]; if (!file) return; return destroy('Thay toàn bộ sổ từ file?', async () => { const o = JSON.parse(await file.text()); return { ok: true, state: L.canonical(o.state || o) }; }); });
    $('l1Wipe').onclick = run(() => destroy('Xóa toàn bộ sổ?', () => ({ ok: true, state: L.empty(L.clock().today.slice(0, 7)) })));
    $('l1Migrate').onclick = run(() => destroy('Chuyển sổ legacy sau khi đã xác nhận từng ngày?', () => {
      const dates = {}; document.querySelectorAll('[data-migration-key]').forEach(el => { dates[el.dataset.migrationKey] = { businessDate: el.value, order: Number($(el.id + 'Order').value) }; });
      return L.migrate(hooks.state(), { plan: planInput(), openingPosition: openingInput(), contributions: $('l1Contributions').value, dates }, meta(), hooks.seed());
    }));
    $('l1History').onclick = run(async () => {}); // replaced by row delegation below
    $('l1History').onclick = async ev => {
      const b = ev.target.closest('button[data-id]'); if (!b) return;
      await run(async () => {
        const e = hooks.state().events.find(e => e.id === b.dataset.id); if (!e) throw new Error('Event không còn tồn tại');
        if (b.dataset.action === 'delete') return destroy('Xóa giao dịch ' + e.businessDate + '?', () => ({ ok: true, state: L.update(hooks.state(), { type: 'delete', id: e.id }, meta()) }));
        editId = e.id; $('l1Kind').value = e.kind; $('l1Date').value = e.businessDate; $('l1Note').value = e.note;
        const fields = { dir: ['l1Dir', 0], vndAmount: [e.kind === 'RESERVE' ? 'l1ReserveAmount' : 'l1P2pVnd', 0], usdtAmount: ['l1P2pUsdt', 6], side: ['l1Side', 0], source: ['l1Source', 0], usdtNotional: ['l1Notional', 6], feeUsdt: ['l1Fee', 6], qty: ['l1Qty', 8], type: ['l1ReserveType', 0], priceUsdt: ['l1Price', 6], usdVndRate: ['l1MarkRate', 0], counterparty: ['l1Counterparty', 0] };
        for (const [key, [id, places]] of Object.entries(fields)) if (key in e) $(id).value = e[key] === null ? '' : typeof e[key] === 'number' ? (e[key] / 10 ** places).toFixed(places) : e[key];
        kindFields(); $('l1Entry').open = true; $('l1SaveEvent').textContent = 'Lưu sửa giao dịch'; return 'Đang sửa ' + e.id;
      })();
    };
  }
  function render() {
    if (!mounted) return;
    const s = hooks.state(), legacy = s.schema !== L.SCHEMA;
    $('l1Migration').hidden = !legacy;
    for (const id of ['l1SavePlan', 'l1SaveOpening', 'l1SaveEvent', 'l1DeleteOpening']) $(id).disabled = legacy;
    if (legacy) {
      $('l1Flags').textContent = 'LEGACY — CHỈ ĐỌC. Cần xác nhận migration trước khi ghi giao dịch L-1.';
      $('l1Summary').textContent = ''; $('l1History').textContent = 'Nguồn legacy được giữ nguyên; có thể xuất JSON đầy đủ.';
      if (shownLegacy !== s) {
        shownLegacy = s; let i = 0;
        $('l1MigrationDates').innerHTML = ['p2p', 'trades'].flatMap(k => s[k].map((r, n) => { const id = 'l1MigrationDate' + i++; return '<label>' + k + '[' + n + '] · thời điểm nhập cũ: ' + escape(r.ts) + '<input type="date" id="' + id + '" data-migration-key="' + k + '[' + n + ']"></label>' + input(id + 'Order', 'Thứ tự xác nhận', 'number', i); })).join('');
      }
      return;
    }
    const d = L.derive(s.openingPosition, s.plan, s.events, L.clock().today);
    $('l1Flags').textContent = d.flags.join(' · ') + (d.firstOffendingEventId ? ' · Event đầu tiên: ' + d.firstOffendingEventId + ' (' + d.firstOffendingBusinessDate + ')' : '');
    const values = [['Tháng', d.currentMonth], ['Ngân sách tháng', units(d.month.monthlyBudgetVnd)], ['Carry từ tháng trước', units(d.month.carryInVnd)], ['Ngân sách gồm carry', units(d.month.plannedBudgetVnd)], ['Đã đầu tư', units(d.month.investedThisMonthVnd)], ['Theo kế hoạch', units(d.month.planInvestedVnd)], ['Còn lại theo kế hoạch', units(d.month.remainingPlannedBudgetVnd)], ['Dự phòng', units(d.reserve.balance)], ['Mua kế tiếp', (d.month.nextPlannedDate || '—') + ' · ' + units(d.month.nextPlannedAmountVnd) + ' VND'], ['ETH', units(d.holdings.ETH.qty, 8)], ['Giá vốn TB ETH (USDT)', avg(d.holdings.ETH.avgCostUsdt, 1000000)], ['Giá vốn TB ETH (VND)', avg(d.holdings.ETH.avgCostVnd)], ['USDT', units(d.usdt.qty, 6)], ['Giá vốn pool USDT (VND)', units(d.usdt.costVnd)], ['VND', units(d.vnd.balance)]];
    $('l1Summary').innerHTML = values.map(([name, value]) => '<div class="stat"><small>' + name + '</small><div>' + escape(value) + '</div></div>').join('');
    $('l1History').innerHTML = s.events.slice().sort((a, b) => a.businessDate.localeCompare(b.businessDate) || a.seq - b.seq).map(e => '<p data-event="' + escape(e.id) + '">' + escape(e.businessDate + ' · ' + e.kind + ' · ' + (e.source || e.dir || e.type || '') + ' · ' + e.note) + (e.businessDate > L.clock().today ? ' [FUTURE_DATED_EVENTS]' : '') + ' · VND giải phóng: ' + units(d.eventEffects[e.id].vndRelieved) + ' <button data-id="' + escape(e.id) + '" data-action="edit">Sửa</button> <button data-id="' + escape(e.id) + '" data-action="delete">Xóa</button></p>').join('');
    $('foot').textContent = 'CoinDCA L-1 · rev ' + s.rev;
  }
  window.CoinLedgerUI = Object.freeze({ mount, render });
})();
