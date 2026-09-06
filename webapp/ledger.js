/* CoinDCA L-1. Integer ledger; derived values never cross the durable boundary. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CoinLedger = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  // T-16: sổ đa tài sản. v3 nới validation (assets/TRADE/PRICE nhận nhiều symbol, thêm kind CASH,
  // mở lại SELL); mọi tài liệu v2 hợp lệ vẫn là tài liệu v3 hợp lệ sau khi đổi nhãn — xem migrateV3().
  const SCHEMA = 'coindca.ledger/3', SCHEMA_V2 = 'coindca.ledger/2', LIMIT = 9000000000000000;
  // Danh sách CỐ ĐỊNH, khớp ba khối của sổ Excel nguồn. Không mở tuỳ ý.
  const ASSETS = ['BTC', 'ETH', 'ADA'];
  // Kế hoạch là ĐƠN tài sản: mọi version trong một plan phải cùng asset (planCheck ép điều đó),
  // nên version đầu tiên là nguồn duy nhất cho "asset của kế hoạch". Không thêm trường plan.asset:
  // một trường thứ hai chỉ tạo thêm chỗ để hai nguồn sự thật lệch nhau, và buộc đổi hình dạng sổ.
  const planAssetOf = plan => plan && Array.isArray(plan.versions) && plan.versions.length ? plan.versions[0].asset : null;
  const clone = x => JSON.parse(JSON.stringify(x));
  // Bản đồ tích luỹ dùng prototype null để id = '__proto__' là OWN-PROPERTY (nếu không, chốt M-2
  // của migration bỏ sót đúng event đó). `plain()` trả lại prototype thường ở biên public để
  // consumer/JSON/deepEqual vẫn thấy một object bình thường, own-property giữ nguyên.
  const plain = o => Object.defineProperties({}, Object.getOwnPropertyDescriptors(o));
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
      if (!p.id || ids.has(p.id) || !monthValid(p.effectiveFrom) || months.has(p.effectiveFrom)) fail('Version kế hoạch không hợp lệ');
      if (!ASSETS.includes(p.asset)) fail('Tài sản kế hoạch không được hỗ trợ: ' + p.asset + ' (chỉ ' + ASSETS.join('/') + ')');
      // T-16: đa tài sản ở tầng NẮM GIỮ, đơn tài sản ở tầng KẾ HOẠCH. Một plan nhắm đúng một coin
      // suốt vòng đời của nó; đổi coin = một kế hoạch khác, không phải một version mới.
      if (p.asset !== plan.versions[0].asset) fail('Một kế hoạch chỉ nhắm MỘT tài sản: version ' + p.id + ' là ' + p.asset + ' nhưng kế hoạch là ' + plan.versions[0].asset);
      ids.add(p.id); months.add(p.effectiveFrom); integer(p.monthlyBudgetVnd);
      if (p.carryPolicy !== 'CAPPED_CARRY' || p.carryCapMonths !== 1) fail('Chỉ CAPPED_CARRY cap 1 được duyệt');
      if (!Array.isArray(p.scheduleDays) || !p.scheduleDays.length || p.scheduleDays.some((d, i, a) => !Number.isInteger(d) || d < 1 || d > 31 || (i > 0 && d <= a[i - 1]))) fail('Lịch không hợp lệ');
    }
    // L-1 fix (a): startMonth trước version đầu tiên => mọi tháng ở giữa không có ngân sách và null lan xuống. Chặn ở cổng vào.
    const earliest = [...months].sort()[0];
    if (plan.versions.length && plan.startMonth < earliest) fail('Tháng bắt đầu ' + plan.startMonth + ' sớm hơn version kế hoạch đầu tiên (' + earliest + '): các tháng ở giữa không có ngân sách nào. Đặt tháng bắt đầu bằng ' + earliest + ', hoặc thêm một version áp dụng từ ' + plan.startMonth + '.');
  }
  function openingCheck(o) {
    if (o === null) return;
    keys(o, 'asOf assets usdt vnd reserveVnd note');
    if (!dateValid(o.asOf) || !Array.isArray(o.assets)) fail('Số dư đầu kỳ không hợp lệ');
    const symbols = new Set();
    for (const a of o.assets) {
      keys(a, 'symbol qty costUsdt costVnd');
      if (!ASSETS.includes(a.symbol)) fail('Tài sản không được hỗ trợ: ' + a.symbol + ' (chỉ ' + ASSETS.join('/') + ')');
      if (symbols.has(a.symbol)) fail('Trùng tài sản trong số dư đầu kỳ: ' + a.symbol); symbols.add(a.symbol);
      integer(a.qty); integer(a.costUsdt, true); integer(a.costVnd, true);
      if (!a.qty && (a.costUsdt || a.costVnd)) fail('Giá vốn khi lượng bằng 0');
    }
    keys(o.usdt, 'qty costVnd'); integer(o.usdt.qty); integer(o.usdt.costVnd, true);
    if (!o.usdt.qty && o.usdt.costVnd) fail('Giá vốn khi pool rỗng');
    if (o.vnd) { keys(o.vnd, 'qty'); integer(o.vnd.qty); }
    if (o.reserveVnd !== undefined) integer(o.reserveVnd);
    if (typeof o.note !== 'string') fail('Thiếu ghi chú đầu kỳ');
  }
  function eventCheck(e, opening, plan) {
    const common = 'id seq kind businessDate createdAt updatedAt note ';
    const fields = { TREASURY: 'dir vndAmount usdtAmount counterparty', TRADE: 'side symbol usdtNotional feeUsdt qty source', RESERVE: 'type vndAmount', CASH: 'type vndAmount', PRICE: 'symbol priceUsdt usdVndRate' };
    if (!e || !fields[e.kind]) fail('Loại event không hợp lệ');
    keys(e, common + fields[e.kind]); integer(e.seq);
    if (!e.id || typeof e.id !== 'string' || !e.seq || !dateValid(e.businessDate)) fail('ID/seq/ngày không hợp lệ');
    if (opening && e.businessDate < opening.asOf) fail('Ngày giao dịch trước số dư đầu kỳ');
    if (typeof e.note !== 'string' || ![e.createdAt, e.updatedAt].every(s => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}T.*Z$/.test(s))) fail('Metadata không hợp lệ');
    if (e.kind === 'TREASURY') {
      if (!['VND_TO_USDT', 'USDT_TO_VND'].includes(e.dir)) fail('Chiều P2P sai');
      integer(e.vndAmount); integer(e.usdtAmount); if (!e.usdtAmount || !e.vndAmount) fail('P2P phải dương');
    } else if (e.kind === 'TRADE') {
      // T-16: SELL mở lại cùng thiết kế P&L ở derive() (H-46 phần "bán lấy USDT").
      if (!['BUY', 'SELL'].includes(e.side) || !['PLAN', 'EXTRA', 'RESERVE'].includes(e.source)) fail('Trade sai');
      if (!ASSETS.includes(e.symbol)) fail('Tài sản không được hỗ trợ: ' + e.symbol + ' (chỉ ' + ASSETS.join('/') + ')');
      integer(e.qty); integer(e.usdtNotional); integer(e.feeUsdt);
      if (!e.qty || !e.usdtNotional || e.feeUsdt > e.usdtNotional) fail('Lượng/phí không hợp lệ');
      if (e.source === 'RESERVE' && !e.note.trim()) fail('Giải ngân dự phòng cần lý do');
      // Ranh giới đa tài sản / đơn kế hoạch, chặn NGAY Ở VALIDATION chứ không chỉ ở derive():
      // một lệnh mua coin khác không bao giờ được mang nhãn "theo kế hoạch" của coin này.
      const pa = planAssetOf(plan);
      if (e.source === 'PLAN' && pa !== null && e.symbol !== pa) fail('Giao dịch nguồn PLAN phải đúng tài sản của kế hoạch (' + pa + '), không phải ' + e.symbol + '. Mua tài sản khác hãy chọn nguồn EXTRA.');
    } else if (e.kind === 'RESERVE') {
      if (!['CONTRIBUTE', 'WITHDRAW'].includes(e.type)) fail('Loại dự phòng sai');
      integer(e.vndAmount); if (!e.vndAmount) fail('Số tiền phải dương');
    } else if (e.kind === 'CASH') {
      // T-16: TREASURY luôn có HAI chân (VND và USDT) — nó mô tả một cuộc ĐỔI tiền, không phải
      // tiền TỪ ĐÂU vào ví. CASH là từ vựng còn thiếu cho "bỏ tiền mặt vào ví"/"rút ra tiêu".
      if (!['DEPOSIT', 'WITHDRAW'].includes(e.type)) fail('Loại tiền mặt sai');
      integer(e.vndAmount); if (!e.vndAmount) fail('Số tiền phải dương');
    } else {
      if (!ASSETS.includes(e.symbol)) fail('Tài sản không được hỗ trợ: ' + e.symbol + ' (chỉ ' + ASSETS.join('/') + ')');
      integer(e.priceUsdt); integer(e.usdVndRate, true);
      if (!e.priceUsdt) fail('Giá tham chiếu phải dương'); if (e.usdVndRate !== null && !e.usdVndRate) fail('Tỷ giá USDT/VND phải dương hoặc bỏ trống');
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
      eventCheck(e, s.openingPosition, s.plan);
      if (ids.has(e.id) || seqs.has(e.seq) || e.seq >= s.nextSeq) fail('ID/seq trùng hoặc high watermark sai');
      ids.add(e.id); seqs.add(e.seq);
    }
    return s;
  }
  function derive(openingPosition, plan, events, asOfDate) {
    openingCheck(openingPosition); planCheck(plan); if (!dateValid(asOfDate)) fail('asOfDate sai');
    const ordered = events.slice().sort((a, b) => a.businessDate.localeCompare(b.businessDate) || a.seq - b.seq);
    const ids = new Set(), seqs = new Set();
    for (const e of ordered) { eventCheck(e, openingPosition, plan); if (ids.has(e.id) || seqs.has(e.seq)) fail('Event trùng'); ids.add(e.id); seqs.add(e.seq); }
    const o = openingPosition;
    // T-16: nắm giữ là BẢN ĐỒ theo symbol. Chỉ tạo entry cho symbol thật sự có mặt (số dư đầu kỳ
    // hoặc một event TRADE/PRICE) — giống cách `months` chỉ chứa tháng có dữ liệu.
    const holdings = Object.create(null);
    const holdingFor = symbol => holdings[symbol] || (holdings[symbol] = { qty: 0, costUsdt: 0, costVnd: 0 });
    for (const a of (o ? o.assets : [])) { const h = holdingFor(a.symbol); h.qty = a.qty; h.costUsdt = a.costUsdt; h.costVnd = a.costVnd; }
    const planAsset = planAssetOf(plan);
    const usdt = clone(o ? o.usdt : { qty: 0, costVnd: 0 });
    let vnd = o && o.vnd ? o.vnd.qty : 0, reserve = o && o.reserveVnd !== undefined ? o.reserveVnd : 0, realizedFxVnd = 0, realizedPnlUsdt = 0;
    // L-1 fix: id = '__proto__' phải là own-property, nếu không chốt M-2 của migration bỏ sót event đó.
    const flags = new Set(), eventEffects = Object.create(null), invested = Object.create(null), planSpent = Object.create(null);
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
      const h = e.symbol === undefined ? null : holdingFor(e.symbol);
      if (e.businessDate > asOfDate) flags.add('FUTURE_DATED_EVENTS');
      if (e.kind === 'TREASURY') {
        if (e.dir === 'VND_TO_USDT') { usdt.qty = add(usdt.qty, e.usdtAmount); usdt.costVnd = add(usdt.costVnd, e.vndAmount); vnd = sub(vnd, e.vndAmount); }
        else { relieved = release(e.usdtAmount, e); vnd = add(vnd, e.vndAmount); realizedFxVnd = add(realizedFxVnd, sub(e.vndAmount, relieved)); }
      } else if (e.kind === 'TRADE' && e.side === 'BUY') {
        const out = add(e.usdtNotional, e.feeUsdt); relieved = release(out, e);
        h.qty = add(h.qty, e.qty); h.costUsdt = add(h.costUsdt, out); h.costVnd = add(h.costVnd, relieved);
        // Ngân sách tháng là ngân sách của MỘT coin. Chỉ trade đúng asset của kế hoạch mới chạm
        // invested/planSpent; mua coin khác không bao giờ pha loãng con số kỷ luật DCA của coin này.
        if (planAsset !== null && e.symbol === planAsset) {
          invested[m] = add(invested[m] === undefined ? 0 : invested[m], relieved);
          if (e.source === 'PLAN') planSpent[m] = add(planSpent[m] === undefined ? 0 : planSpent[m], relieved);
        }
        if (e.source === 'RESERVE') reserve = sub(reserve, relieved);
      } else if (e.kind === 'TRADE') {
        // T-16 (H-46, phần "bán lấy USDT"): BÁN CHUYỂN giá vốn từ holding sang pool USDT, không
        // định giá lại pool theo giá trung bình của chính nó. Lãi/lỗ VND chỉ phát sinh khi USDT
        // đổi ngược ra VND (TREASURY USDT_TO_VND) — cơ chế đã có, không đổi. Chênh lệch của lượt
        // bán được ghi bằng ĐƠN VỊ USDT vào realizedPnlUsdt, không gộp với realizedFxVnd (VND).
        const proceeds = sub(e.usdtNotional, e.feeUsdt);
        const relievedUsdt = portion(e.qty, h.costUsdt, h.qty); relieved = portion(e.qty, h.costVnd, h.qty);
        if (e.qty > h.qty) inconsistent(e);
        h.qty = sub(h.qty, e.qty); h.costUsdt = sub(h.costUsdt, relievedUsdt); h.costVnd = sub(h.costVnd, relieved);
        if (h.qty === 0) { h.costUsdt = 0; h.costVnd = 0; }
        usdt.qty = add(usdt.qty, proceeds); usdt.costVnd = add(usdt.costVnd, relieved);
        realizedPnlUsdt = add(realizedPnlUsdt, sub(proceeds, relievedUsdt));
      } else if (e.kind === 'RESERVE') reserve = e.type === 'CONTRIBUTE' ? add(reserve, e.vndAmount) : sub(reserve, e.vndAmount);
      else if (e.kind === 'CASH') vnd = e.type === 'DEPOSIT' ? add(vnd, e.vndAmount) : sub(vnd, e.vndAmount);
      if ((reserve !== null && reserve < 0) || (vnd !== null && vnd < 0)) inconsistent(e);
      eventEffects[e.id] = { vndRelieved: relieved, usdtQty: usdt.qty, usdtCostVnd: usdt.costVnd, symbol: e.symbol === undefined ? null : e.symbol, holdingQty: h ? h.qty : null };
    }
    const currentMonth = asOfDate.slice(0, 7), months = Object.create(null);
    const versions = plan.versions.slice().sort((a, b) => a.effectiveFrom.localeCompare(b.effectiveFrom));
    const versionFor = m => m < plan.startMonth ? null : versions.filter(p => p.effectiveFrom <= m).slice(-1)[0];
    let start = plan.startMonth;
    if (o && o.asOf.slice(0, 7) > start) start = o.asOf.slice(0, 7);
    let carry = 0;
    function buildMonth(m, incoming) {
      const p = versionFor(m), spent = planSpent[m] === undefined ? 0 : planSpent[m];
      const budget = p ? p.monthlyBudgetVnd : null, cin = !p || incoming === null ? null : Math.min(incoming, budget);
      const planned = add(budget, cin), remaining = planned === null || spent === null ? null : Math.max(0, sub(planned, spent));
      // L-1 fix (b): tháng KHÔNG có version thì không có ngân sách để mang sang -> carryOut = 0.
      // null chỉ dành cho "chưa biết" (UNKNOWN_VND_BASIS), không được lan sang tháng đã có version.
      const out = p ? remaining : 0;
      return { monthlyBudgetVnd: budget, carryInVnd: cin, plannedBudgetVnd: planned, investedThisMonthVnd: invested[m] === undefined ? 0 : invested[m], planInvestedVnd: spent, remainingPlannedBudgetVnd: remaining, carryOutVnd: m < currentMonth ? out : null };
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
      // L-1 fix: chia theo plannedBudgetVnd (ngân sách + carryIn); chia theo ngân sách gốc thì tiền
      // carry không bao giờ lên lịch mua — đúng thứ CAPPED_CARRY sinh ra để giải quyết.
      const dates = slots(p, currentMonth); plannedPerSlot = month.plannedBudgetVnd === null ? [] : split(month.plannedBudgetVnd, dates.length);
      let cumulative = 0;
      for (let i = 0; i < plannedPerSlot.length; i++) {
        cumulative = add(cumulative, plannedPerSlot[i]);
        if (dates[i] >= asOfDate && month.planInvestedVnd !== null && cumulative > month.planInvestedVnd) {
          nextPlannedDate = dates[i]; nextPlannedAmountVnd = month.remainingPlannedBudgetVnd === null ? null : Math.min(Math.max(0, sub(cumulative, month.planInvestedVnd)), month.remainingPlannedBudgetVnd); break;
        }
      }
      if (!nextPlannedDate && month.planInvestedVnd !== null) {
        const nm = nextMonth(currentMonth), np = versionFor(nm);
        // Carry-in của tháng sau chưa chốt được (tháng này chưa đóng) nên dùng ngân sách gốc của tháng sau; không trừ planInvested và không cap bằng remaining của tháng này.
        if (np) { const nd = slots(np, nm); nextPlannedDate = nd[0]; nextPlannedAmountVnd = split(np.monthlyBudgetVnd, nd.length)[0]; }
      }
    }
    Object.assign(month, { nextPlannedDate, nextPlannedAmountVnd, plannedPerSlot });
    for (const h of Object.values(holdings)) { h.avgCostUsdt = ratio(h.costUsdt, h.qty, 100000000); h.avgCostVnd = ratio(h.costVnd, h.qty, 100000000); }
    usdt.avgVnd = ratio(usdt.costVnd, usdt.qty, 1000000);
    if ([usdt.costVnd, reserve, month.plannedBudgetVnd, ...Object.values(holdings).map(h => h.costVnd), ...Object.values(invested)].some(x => x === null)) flags.add('UNKNOWN_VND_BASIS');
    // L-1 fix (T-15): usdVndRate (tuỳ chọn, do Owner nhập trên chính event PRICE) chỉ dùng cho ĐỊNH
    // GIÁ hiển thị — không bao giờ chạm giá vốn. Không có tỷ giá thì vnd = null, không suy diễn.
    // T-16: định giá theo TỪNG symbol, mỗi symbol dùng PRICE mới nhất CỦA CHÍNH NÓ.
    const valuation = Object.create(null);
    for (const symbol of Object.keys(holdings)) {
      const mark = ordered.filter(e => e.kind === 'PRICE' && e.symbol === symbol && e.businessDate <= asOfDate).slice(-1)[0];
      if (!mark || mark.businessDate < previousDay(asOfDate)) continue;
      const usdtValue = round(BigInt(holdings[symbol].qty) * BigInt(mark.priceUsdt), 100000000);
      valuation[symbol] = { usdt: usdtValue, vnd: mark.usdVndRate === null || mark.usdVndRate === undefined ? null : round(BigInt(usdtValue) * BigInt(mark.usdVndRate), 1000000), usdVndRate: mark.usdVndRate === undefined ? null : mark.usdVndRate, businessDate: mark.businessDate };
    }
    return { holdings: plain(holdings), usdt, vnd: { balance: vnd }, reserve: { balance: reserve }, currentMonth, month, months: plain(months), eventEffects: plain(eventEffects), realizedFxVnd, realizedPnlUsdt, valuation: plain(valuation), flags: [...flags].sort(), firstOffendingEventId, firstOffendingBusinessDate };
  }
  function update(state, action, meta) {
    const s = canonical(state);
    if (action.type === 'opening') s.openingPosition = clone(action.value);
    else if (action.type === 'plan') {
      const next = clone(action.value); planCheck(next);
      // L-1 fix: version đã tồn tại là bất biến về MỌI trường quyết định tiền — không chỉ
      // effectiveFrom/scheduleDays. Đổi monthlyBudgetVnd của version cũ là sửa hồi tố ngân sách
      // tháng đã đóng, kéo theo carryOut tháng đó và carry-in mọi tháng sau.
      const FROZEN = ['effectiveFrom', 'asset', 'monthlyBudgetVnd', 'scheduleDays', 'carryPolicy', 'carryCapMonths'];
      for (const old of s.plan.versions) {
        const retained = next.versions.find(p => p.id === old.id);
        if (!retained || FROZEN.some(k => JSON.stringify(retained[k]) !== JSON.stringify(old[k]))) fail('Không đổi ngân sách/lịch của version cũ; thêm version mới áp dụng từ tháng thay đổi trở đi');
      }
      for (const p of next.versions.filter(p => !s.plan.versions.some(old => old.id === p.id))) {
        if (s.plan.versions.length && (!meta.today || p.effectiveFrom < meta.today.slice(0, 7))) fail('Version lịch mới chỉ áp dụng từ tháng thay đổi trở đi');
      }
      s.plan = next;
    }
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
      if (Object.values(d.eventEffects).some(e => e.usdtQty < 0 || e.holdingQty < 0)) fail('M-2: âm số lượng trong replay');
      // L-1 fix: app cũ cộng costUsdt KHÔNG gồm phí, derive() cộng usdtNotional + feeUsdt. Oracle
      // phải so cùng một định nghĩa, nếu không mọi sổ cũ có phí ≠ 0 đều kẹt vĩnh viễn ở LEGACY.
      const migratedFeeUsdt = candidate.events.reduce((t, e) => e.kind === 'TRADE' && e.side === 'BUY' ? add(t, e.feeUsdt) : t, 0);
      // T-16: holdings là bản đồ và chỉ chứa symbol thật sự có mặt — một sổ legacy không có trade
      // ETH nào sẽ KHÔNG có entry ETH. Sổ legacy `ethdca.tracker/1` chỉ có ETH nên vắng mặt = 0.
      const ethH = d.holdings.ETH || { qty: 0, costUsdt: 0, costVnd: 0 };
      const costUsdtExFee = sub(ethH.costUsdt, migratedFeeUsdt);
      const comparisons = { eth: [ethH.qty, legacy.eth, 100000000], usdt: [d.usdt.qty, legacy.treasury.usdt, 1000000], vnd: [d.vnd.balance, legacy.treasury.vnd, 1], costUsdt: [costUsdtExFee, legacy.costUsdt, 1000000] };
      for (const [k, [actual, old, scale]] of Object.entries(comparisons)) {
        if (actual === null || typeof old !== 'number' || !Number.isFinite(old)) fail('M-3: thiếu oracle ' + k);
        deltas[k] = { deltaUnits: actual - old * scale, legacyRounded: Math.round(old * scale), actual };
        if (Math.abs(deltas[k].deltaUnits) > 1) errors.push('M-3: lệch ' + k);
      }
      // L-1 fix: giá vốn VND lệch không còn "chỉ báo cáo" — nó là cờ CỨNG như bốn oracle kia.
      // actual === null là trạng thái UNKNOWN đã có W-1/UNKNOWN_VND_BASIS lo, không chặn ở đây.
      const legacyCostVnd = typeof legacy.costVnd === 'number' && Number.isFinite(legacy.costVnd) ? Math.round(legacy.costVnd) : null;
      deltas.costVnd = { actual: ethH.costVnd, legacy: legacy.costVnd, deltaVnd: ethH.costVnd === null || legacyCostVnd === null ? null : ethH.costVnd - legacyCostVnd };
      if (ethH.costVnd !== null && legacyCostVnd === null) errors.push('M-3: thiếu oracle costVnd');
      if (deltas.costVnd.deltaVnd !== null && Math.abs(deltas.costVnd.deltaVnd) > 1) errors.push('M-3: lệch costVnd');
      if (errors.length) return { ok: false, errors, deltas };
      candidate.LEGACY_ARCHIVE = { label: 'LEGACY_ARCHIVE — READ ONLY', raw: clone(legacy) };
      candidate.RESEARCH_ONLY = { extraDays: clone(legacy.extraDays || []), history: clone(seed && seed.history || []) };
      const unknownBasis = candidate.events.filter(e => e.kind === 'TRADE' && d.eventEffects[e.id].vndRelieved === null).map(e => ({
        legacyIndex: e.note.slice('Migration '.length), eventId: e.id,
        reason: 'USDT pool thiếu giá vốn VND đã biết; không suy tỷ giá từ legacy hay PRICE.',
        correction: 'Sửa openingPosition.usdt.costVnd tường minh hoặc bổ sung event TREASURY còn thiếu; không nhập FX riêng từng lệnh.'
      }));
      return { ok: true, state: candidate, deltas, unknownBasis, warnings: d.flags.includes('UNKNOWN_VND_BASIS') ? ['W-1', 'UNKNOWN_VND_BASIS'] : [] };
    } catch (e) { errors.push(e.message); return { ok: false, errors, deltas }; }
  }
  /* ---------- T-16: nâng cấp sổ v2 -> v3 ----------
   * v3 chỉ NỚI validation; mọi tài liệu v2 hợp lệ đã là tài liệu v3 hợp lệ sau khi đổi nhãn
   * `schema`. Vì vậy đây là migration HÌNH THỨC — và chính vì hình thức, nó phải chứng minh
   * được là hình thức, không được tin. Hai cổng chặn, cùng khuôn v1->v2: một oracle số học và
   * một oracle hình dạng. Không có đường nào tự động đổi dữ liệu mà không qua hàm này.
   */
  function guardV2(s) {
    keys(s, 'schema rev nextSeq plan openingPosition events LEGACY_ARCHIVE RESEARCH_ONLY');
    integer(s.rev); integer(s.nextSeq);
    if (!s.plan || !Array.isArray(s.plan.versions) || !Array.isArray(s.events)) fail('Sổ v2 không hợp lệ');
    if (s.plan.versions.some(p => p.asset !== 'ETH')) fail('Sổ v2 chỉ có kế hoạch ETH');
    const o = s.openingPosition;
    if (o && (!Array.isArray(o.assets) || o.assets.length > 1 || o.assets.some(a => a.symbol !== 'ETH'))) fail('Sổ v2 chỉ có tối đa một tài sản ETH');
    for (const e of s.events) {
      if (!['TREASURY', 'TRADE', 'RESERVE', 'PRICE'].includes(e.kind)) fail('Sổ v2 không có loại event ' + e.kind);
      if (e.kind === 'TRADE' && (e.side !== 'BUY' || e.symbol !== 'ETH')) fail('Sổ v2 chỉ có TRADE BUY ETH');
      if (e.kind === 'PRICE' && e.symbol !== 'ETH') fail('Sổ v2 chỉ có PRICE ETH');
    }
  }
  /** Replay ĐỘC LẬP theo ngữ nghĩa v2 (ETH-only, chỉ BUY): một vòng lặp riêng, KHÔNG gọi derive().
   *  Đây là oracle để đối chiếu — chỗ một lỗi migration sẽ nằm là ở duyệt/hình dạng, không phải ở
   *  bốn phép số nguyên dùng chung đã có mutation test riêng. */
  function v2Oracle(s) {
    const o = s.openingPosition;
    const a = o && o.assets[0] ? o.assets[0] : { qty: 0, costUsdt: 0, costVnd: 0 };
    const eth = { qty: a.qty, costUsdt: a.costUsdt, costVnd: a.costVnd };
    const pool = o ? { qty: o.usdt.qty, costVnd: o.usdt.costVnd } : { qty: 0, costVnd: 0 };
    let vnd = o && o.vnd ? o.vnd.qty : 0, reserve = o && o.reserveVnd !== undefined ? o.reserveVnd : 0, fx = 0;
    const take = out => {
      const r = portion(out, pool.costVnd, pool.qty);
      pool.qty = sub(pool.qty, out); pool.costVnd = sub(pool.costVnd, r);
      if (pool.qty === 0) { fx = add(fx, pool.costVnd); pool.costVnd = 0; }
      return r;
    };
    for (const e of s.events.slice().sort((x, y) => x.businessDate.localeCompare(y.businessDate) || x.seq - y.seq)) {
      if (e.kind === 'TREASURY' && e.dir === 'VND_TO_USDT') { pool.qty = add(pool.qty, e.usdtAmount); pool.costVnd = add(pool.costVnd, e.vndAmount); vnd = sub(vnd, e.vndAmount); }
      else if (e.kind === 'TREASURY') { const r = take(e.usdtAmount); vnd = add(vnd, e.vndAmount); fx = add(fx, sub(e.vndAmount, r)); }
      else if (e.kind === 'TRADE') { const out = add(e.usdtNotional, e.feeUsdt), r = take(out); eth.qty = add(eth.qty, e.qty); eth.costUsdt = add(eth.costUsdt, out); eth.costVnd = add(eth.costVnd, r); if (e.source === 'RESERVE') reserve = sub(reserve, r); }
      else if (e.kind === 'RESERVE') reserve = e.type === 'CONTRIBUTE' ? add(reserve, e.vndAmount) : sub(reserve, e.vndAmount);
    }
    return { ethQty: eth.qty, ethCostUsdt: eth.costUsdt, ethCostVnd: eth.costVnd, usdtQty: pool.qty, usdtCostVnd: pool.costVnd, vndBalance: vnd, reserveBalance: reserve, realizedFxVnd: fx };
  }
  function migrateV3(input, meta) {
    const errors = [], deltas = {};
    try {
      if (!input || input.schema !== SCHEMA_V2) fail('Chỉ nâng cấp được sổ ' + SCHEMA_V2 + ' (nhận: ' + (input && input.schema) + ')');
      if (!meta || !dateValid(meta.today)) fail('Thiếu ngày hôm nay để đối chiếu');
      const source = clone(input); delete source.derivedSnapshot;
      guardV2(source);
      const before = v2Oracle(source);
      const candidate = canonical(Object.assign(clone(source), { schema: SCHEMA }));
      const d = derive(candidate.openingPosition, candidate.plan, candidate.events, meta.today);
      const eth = d.holdings.ETH || { qty: 0, costUsdt: 0, costVnd: 0 };
      const after = { ethQty: eth.qty, ethCostUsdt: eth.costUsdt, ethCostVnd: eth.costVnd, usdtQty: d.usdt.qty, usdtCostVnd: d.usdt.costVnd, vndBalance: d.vnd.balance, reserveBalance: d.reserve.balance, realizedFxVnd: d.realizedFxVnd };
      for (const k of Object.keys(before)) {
        deltas[k] = { before: before[k], after: after[k] };
        if (JSON.stringify(before[k]) !== JSON.stringify(after[k])) errors.push('V3-1: lệch ' + k);
      }
      // Oracle hình dạng: ngoài đúng trường `schema`, không một byte nào của sổ được đổi.
      const x = clone(source), y = clone(candidate); x.schema = y.schema = null;
      if (JSON.stringify(x) !== JSON.stringify(y)) errors.push('V3-2: nội dung sổ bị đổi ngoài nhãn schema');
      if (errors.length) return { ok: false, errors, deltas };
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
  return Object.freeze({ SCHEMA, SCHEMA_V2, ASSETS: Object.freeze(ASSETS.slice()), LIMIT, clone, integer, round, decimal, ratio, clock, split, dateValid, nextMonth, empty, canonical, derive, update, migrate, migrateV3, destructive });
});
