/* App logic — state, accounting, render, persistence.
 * Accounting theo Strategy §8: TOTAL = AVAILABLE + RESERVED + DEPLOYED, không âm,
 * không double reservation. Mọi dịch chuyển ghi vào ledger (Data Model §6).
 * Persistence (T-09B, DEC-019/020/021): nguồn bền duy nhất là Cloud Firestore; localStorage
 * chỉ là mirror/cache — xem khối "persistence" bên dưới.
 */
(function () {
  "use strict";

  var E = ENGINE;
  var $ = function (id) { return document.getElementById(id); };
  var STORE_STATE = "ethdca-tracker-state-v1";
  var STORE_SEED = "ethdca-tracker-seed-v1";
  // Bản mirror MỚI HƠN nguồn bền, cất riêng chờ người dùng chọn (CHECK-T09B-16) — không bao giờ
  // tự trở thành sổ chính thức.
  var STORE_STASH = "ethdca-tracker-state-v1.local-diverged";

  /* ---------------- state ---------------- */

  function emptyState() {
    return {
      schema: "ethdca.tracker/1",
      rev: 0,
      months: {},          // "YYYY-MM" -> {contribution, base:{a,r,d}, smart:{...}, opp:{...}}
      oppFund: { a: 0, r: 0, d: 0 },   // Opportunity Fund xuyên tháng
      treasury: { vnd: 0, usdt: 0 },
      eth: 0,
      costUsdt: 0,         // tổng USDT đã bỏ ra mua ETH (không gồm phí)
      costVnd: 0,          // tổng VND quy đổi tương ứng
      ladders: [],
      trades: [],
      p2p: [],
      ledger: [],
      extraDays: [],       // giá người dùng nhập thêm sau seed
    };
  }

  // T-09B (DEC-020): nguồn sự thật DUY NHẤT của sổ là Cloud Firestore (`ethdca/state`,
  // `ethdca/seed`). Trang khởi động với sổ rỗng và mọi thao tác ghi bị khoá cho tới khi
  // initPersistence() nạp xong bản bền. Trang không còn nhúng state; localStorage/sessionStorage
  // chỉ là mirror/cache và KHÔNG được tự thắng bản bền (CHECK-T09B-16).
  var state = emptyState();
  var seed = null;

  /** Trạng thái persistence — EPHEMERAL, không bao giờ được ghi lên nguồn bền. */
  var P = {
    phase: "INIT",       // INIT | UNCONFIGURED | AUTH_FAILED | UNRECOGNIZED | OFFLINE | CORRUPT | ONLINE
    detail: "",          // mã lỗi / lý do của phase hiện tại
    uid: null,
    projectId: null,
    durableRev: null,    // rev của bản state đã được máy chủ xác nhận (null = chưa có bản bền)
    seedDurable: false,  // seed trong bộ nhớ đã nằm trên nguồn bền
    seedPending: false,  // seed trong bộ nhớ đang chờ ghi lên
    seedGen: 0,          // đếm số lần nạp seed, để ack không xoá nhầm cờ của một seed mới hơn
    saving: false,       // đang có lệnh ghi chưa được trả lời
    resave: false,       // có thay đổi mới trong lúc lệnh ghi đang chờ -> ghi lại sau
    unconfirmed: false,  // lệnh ghi quá hạn ackTimeoutMs mà máy chủ chưa trả lời
    lastError: null,     // lỗi ghi gần nhất (null = lần ghi gần nhất thành công)
    staleRev: undefined, // rev đang có trên máy chủ khi lệnh ghi bị từ chối vì stale-durable
    lastAck: null,       // thời điểm máy chủ xác nhận gần nhất
    rawDurable: null,    // bản durable thô khi CORRUPT — giữ nguyên để cứu, không bao giờ ghi đè
    diverged: null,      // bản mirror mới hơn nguồn bền, chờ người dùng chọn (CHECK-T09B-16)
    mirrorShown: false,  // OFFLINE: đang hiển thị bản mirror CHƯA xác nhận, chỉ để xem
  };
  var fb = { auth: null, db: null };

  var DEFAULT_CFG = {
    base_pct: 0.5, smart_pct: 0.3, opportunity_pct: 0.2, opportunity_cap_months: 4,
    smart_spacing_factor: 2.0, smart_spacing_min: 0.04, smart_spacing_max: 0.12,
    opportunity_spacing_multiplier: 1.25, opportunity_daily_limit_pct: 0.2,
    opportunity_activate_score: 68, opportunity_suspend_score: 62,
    cooldown_hours: 48, cooldown_override_pct: 0.07, max_zones_per_cycle: 2,
    score_weights: [50, 30, 20], accounting_timezone: "Asia/Ho_Chi_Minh",
  };
  function cfg() { return (seed && seed.config) || DEFAULT_CFG; }

  /* ---------------- derived market view ---------------- */

  var view = null;
  function recompute() {
    var hist = [];
    if (seed && seed.history) hist = seed.history.slice();
    (state.extraDays || []).forEach(function (d) { hist.push(d); });
    // khử trùng ngày, giữ bản nhập sau cùng
    var map = new Map();
    hist.forEach(function (r) { map.set(r.d, r); });
    hist = Array.from(map.values()).sort(function (a, b) {
      return a.d < b.d ? -1 : (a.d > b.d ? 1 : 0);
    });
    if (!hist.length) { view = null; return; }
    var ind = E.computeIndicators(hist);
    var last = ind[ind.length - 1];
    var s = E.scoreForDay(last, cfg().score_weights);
    var prev = ind.length > 1 ? ind[ind.length - 2] : null;
    view = {
      hist: hist, ind: ind, last: last, score: s, prev: prev,
      smartUnlock: E.smartUnlock(s.oscore),
      oppUnlock: E.opportunityUnlock(s.oscore),
      multiplier: E.scoreMultiplier(s.oscore),
      smartSpacing: Number.isFinite(last.adr30) ? E.smartSpacing(last.adr30, s.oscore, cfg()) : NaN,
    };
    view.oppSpacing = Number.isFinite(view.smartSpacing)
      ? E.opportunitySpacing(view.smartSpacing, cfg()) : NaN;
    view.regime = deriveRegime(ind, s.oscore);
  }

  /** Regime nhãn hiển thị. Return24H cần nến 15m nên ở đây dùng daily return làm xấp xỉ
   *  — app ghi rõ điều đó thay vì giả vờ là con số của spec. */
  function deriveRegime(ind, oscore) {
    var n = ind.length, last = ind[n - 1];
    var r7 = last.return7;
    var r1 = n > 1 ? last.close / ind[n - 2].close - 1 : NaN;
    if (Number.isFinite(oscore) && oscore >= 75 &&
        ((Number.isFinite(r7) && r7 <= -0.15) || (Number.isFinite(r1) && r1 <= -0.10))) {
      return { name: "CRASH", approx: true };
    }
    if ((Number.isFinite(r7) && r7 <= -0.10) || (Number.isFinite(r1) && r1 <= -0.07)) {
      return { name: "STRESSED", approx: true };
    }
    return { name: "NORMAL", approx: true };
  }

  /* ---------------- month + pools ---------------- */

  function monthKey(d) {
    d = d || new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0");
  }
  function currentMonth() {
    var keys = Object.keys(state.months).sort();
    return keys.length ? keys[keys.length - 1] : monthKey();
  }

  /** T-09A / V-01 — tháng kế toán SỞ HỮU vốn của một ladder.
   *  Vốn được reserve từ pool của `currentMonth()` TẠI THỜI ĐIỂM TẠO, nên mọi dịch chuyển
   *  sau đó (deploy khi fill zone, release khi cancel/invalidate/expire) phải quay về ĐÚNG
   *  tháng đó — không phải tháng đang là `currentMonth()` lúc dịch chuyển xảy ra. */
  function ladderMonth(L) {
    if (L && typeof L.month === "string" && L.month) return L.month;
    // Ladder tạo TRƯỚC T-09A không mang trường `month`. Suy ra từ dấu thời gian tạo nếu
    // tháng đó thật sự có sổ; nếu không thì rơi về currentMonth(). Cả hai nhánh suy luận
    // đều được BÁO HIỆN bằng banner (renderBanners) — Owner Acceptance điểm 9: sai tiền
    // phải fail visibly.
    var guess = L && L.created ? monthKey(new Date(L.created)) : null;
    if (guess && state.months[guess]) return guess;
    return currentMonth();
  }
  /** Ladder chưa có tháng sở hữu tường minh — tháng của chúng là SUY LUẬN, không phải sự kiện. */
  function inferredMonthLadders() {
    return (state.ladders || []).filter(function (L) {
      return !(typeof L.month === "string" && L.month);
    });
  }
  function month(k) {
    if (!state.months[k]) {
      state.months[k] = {
        contribution: 0,
        base: { a: 0, r: 0, d: 0 },
        smart: { a: 0, r: 0, d: 0 },
        oppAdded: 0, oppOverflow: 0,
      };
    }
    return state.months[k];
  }
  var poolTotal = function (p) { return p.a + p.r + p.d; };

  function ledger(entry) {
    state.ledger.push(Object.assign({ ts: new Date().toISOString() }, entry));
  }

  /* ---------------- actions ---------------- */

  function addContribution(mk, amount) {
    var c = cfg();
    var m = month(mk);
    var base = amount * c.base_pct;
    var smart = amount * c.smart_pct;
    var opp = amount * c.opportunity_pct;

    m.contribution += amount;
    m.base.a += base;
    m.smart.a += smart;

    // Opportunity cap = contribution Opp hằng tháng × opportunity_cap_months
    var cap = opp * c.opportunity_cap_months;
    var fundTotal = state.oppFund.a + state.oppFund.r + state.oppFund.d;
    var headroom = Math.max(0, cap - fundTotal);
    var toFund = Math.min(opp, headroom);
    var overflow = opp - toFund;
    state.oppFund.a += toFund;
    m.oppAdded += toFund;
    if (overflow > 0) { m.smart.a += overflow; m.oppOverflow += overflow; }

    state.treasury.vnd += amount;

    ledger({ pool: "BASE", type: "CONTRIBUTION", vnd: base, reason: "CONTRIBUTION", month: mk });
    ledger({ pool: "SMART", type: "CONTRIBUTION", vnd: smart + overflow,
             reason: overflow > 0 ? "CAP_OVERFLOW_TO_SMART" : "CONTRIBUTION", month: mk });
    if (toFund > 0) {
      ledger({ pool: "OPPORTUNITY", type: "CONTRIBUTION", vnd: toFund,
               reason: "CONTRIBUTION", month: mk });
    }
    return { base: base, smart: smart, oppAdded: toFund, overflow: overflow };
  }

  function addP2P(dir, vnd, usdt, fee) {
    var rate = dir === "VND_TO_USDT" ? (vnd + fee) / usdt : vnd / usdt;
    if (dir === "VND_TO_USDT") {
      if (vnd + fee > state.treasury.vnd + 1e-6) return { err: "Không đủ VND trong kho." };
      state.treasury.vnd -= (vnd + fee);
      state.treasury.usdt += usdt;
    } else {
      if (usdt > state.treasury.usdt + 1e-6) return { err: "Không đủ USDT trong kho." };
      state.treasury.usdt -= usdt;
      state.treasury.vnd += (vnd - fee);
    }
    state.p2p.push({
      ts: new Date().toISOString(), dir: dir, vnd: vnd, usdt: usdt, fee: fee,
      rate: rate,
    });
    ledger({ pool: "TREASURY", type: dir === "VND_TO_USDT" ? "P2P_BUY" : "P2P_SELL",
             vnd: dir === "VND_TO_USDT" ? -(vnd + fee) : (vnd - fee),
             usdt: dir === "VND_TO_USDT" ? usdt : -usdt, reason: "P2P", rate: rate });
    return { rate: rate };
  }

  function poolFor(src, mk) {
    var m = month(mk || currentMonth());
    if (src === "BASE") return m.base;
    if (src === "SMART") return m.smart;
    if (src === "OPPORTUNITY") return state.oppFund;
    return null;
  }

  function findZone(zoneKey) {
    if (!zoneKey) return null;
    var parts = zoneKey.split("|");
    var L = state.ladders.filter(function (x) { return x.id === parts[0]; })[0];
    if (!L) return null;
    var z = L.zones[parseInt(parts[1], 10)];
    return z ? { L: L, z: z } : null;
  }

  /** zoneKey (tùy chọn): "ladderId|zoneIndex" — khi có, tiền đi từ RESERVED sang DEPLOYED
   *  và zone chuyển EXECUTED / PARTIALLY_FILLED. Không có thì trừ thẳng AVAILABLE. */
  function addBuy(src, usdt, price, recPrice, fee, vndRate, zoneKey) {
    if (usdt + fee > state.treasury.usdt + 1e-6) return { err: "Không đủ USDT trong kho." };
    var ref = findZone(zoneKey);
    if (ref && ref.L.status !== "ACTIVE") return { err: "Ladder không còn ACTIVE." };

    var ethAmt = usdt / price;
    var vndCost = vndRate ? usdt * vndRate : 0;

    state.treasury.usdt -= (usdt + fee);
    state.eth += ethAmt;
    state.costUsdt += usdt;
    state.costVnd += vndCost;

    // T-09A / V-01: fill một zone rút vốn từ pool của tháng SỞ HỮU ladder, không phải
    // tháng đang là currentMonth() lúc ghi lệnh mua.
    var pool = poolFor(ref ? ref.L.type : src,
                       ref ? ladderMonth(ref.L) : currentMonth());
    var deducted = 0;
    var zoneNote = null;

    if (ref) {
      // Phần chưa fill của zone; tiền đã nằm ở RESERVED từ lúc tạo ladder.
      var remaining = Math.max(0, ref.z.target_vnd - (ref.z.filled_vnd || 0));
      var amount = vndCost > 0 ? Math.min(vndCost, remaining) : remaining;
      deducted = Math.min(amount, pool ? pool.r : 0);
      if (pool) { pool.r -= deducted; pool.d += deducted; }
      ref.z.filled_vnd = (ref.z.filled_vnd || 0) + deducted;
      // Strategy §8: chỉ phần đã fill chuyển RESERVED -> DEPLOYED; phần dư vẫn RESERVED.
      ref.z.status = ref.z.filled_vnd >= ref.z.target_vnd - 1e-6
        ? "EXECUTED" : "PARTIALLY_FILLED";
      zoneNote = ref.L.type + " zone " + ref.z.index + " → " + ref.z.status;
      if (ref.L.zones.every(function (z) {
        return z.status === "EXECUTED" || z.status === "CANCELLED";
      })) ref.L.status = "COMPLETED";
    } else if (vndCost > 0 && pool) {
      deducted = Math.min(vndCost, pool.a);
      pool.a -= deducted; pool.d += deducted;
    }

    var shortfallBps = (recPrice && recPrice > 0) ? (price / recPrice - 1) * 10000 : null;
    state.trades.push({
      ts: new Date().toISOString(), src: ref ? ref.L.type : src, usdt: usdt, price: price,
      recPrice: recPrice || null, eth: ethAmt, fee: fee, vndRate: vndRate || null,
      vndCost: vndCost, shortfallBps: shortfallBps,
      zone: ref ? ref.L.type + "-" + ref.z.index : null,
    });
    ledger({ pool: ref ? ref.L.type : src, type: "ETH_BUY", vnd: -deducted,
             usdt: -(usdt + fee), eth: ethAmt,
             reason: ref ? ref.L.type + "_ZONE_" + ref.z.index : "ETH_BUY", price: price });
    return { eth: ethAmt, shortfallBps: shortfallBps, deducted: deducted, zoneNote: zoneNote };
  }

  function addDay(d, e, b, v) {
    state.extraDays = (state.extraDays || []).filter(function (x) { return x.d !== d; });
    state.extraDays.push({ d: d, e: e, b: b, v: v });
    state.extraDays.sort(function (x, y) { return x.d < y.d ? -1 : 1; });
    // hai daily close liên tiếp trên invalidation price -> ladder INVALIDATED (Strategy §18.2)
    state.ladders.forEach(function (L) {
      if (L.status !== "ACTIVE") return;
      if (e > L.invalidation_price) {
        L.consecutive_invalidation_closes = (L.consecutive_invalidation_closes || 0) + 1;
        if (L.consecutive_invalidation_closes >= 2) {
          L.status = "INVALIDATED";
          L.zones.forEach(function (z) { if (z.status === "ACTIVE") z.status = "CANCELLED"; });
          releaseLadder(L);
        }
      } else {
        L.consecutive_invalidation_closes = 0;
      }
    });
  }

  /** T-09A / V-02 — Strategy §12 "Không được reserve vốn chưa unlock".
   *  Cùng công thức với `capital.py::smart_reservable` (bản Python là chuẩn):
   *      unlocked(tháng) − (đã reserve + đã deploy TRONG THÁNG), kẹp trên bởi available.
   *  `view` chưa có (chưa nạp seed) hoặc unlock không hữu hạn => 0: fail closed. */
  function smartReservable(m) {
    if (!view || !Number.isFinite(view.smartUnlock)) return 0;
    var unlocked = poolTotal(m.smart) * view.smartUnlock;
    return Math.max(0, Math.min(m.smart.a, unlocked - m.smart.r - m.smart.d));
  }
  /** Đối ứng cho Opportunity Fund (xuyên tháng) — phần unlock của
   *  `capital.py::opportunity_reservable`. Hysteresis §5 và daily limit §11 KHÔNG được cài
   *  ở app; xem khối DEFERRED_BY_MINIMAL_FIX trong `docs/tasks/T-09A-*.md`. */
  function oppReservable() {
    if (!view || !Number.isFinite(view.oppUnlock)) return 0;
    var f = state.oppFund;
    var unlocked = poolTotal(f) * view.oppUnlock;
    return Math.max(0, Math.min(f.a, unlocked - f.r - f.d));
  }

  /** Trả về {ok, mk, cap, reason}. `mk` là tháng bị trừ vốn — người gọi PHẢI ghi nó lên
   *  ladder để release/deploy sau này quay về đúng chỗ (V-01). */
  function reserveFor(type, vnd) {
    var mk = currentMonth(), m = month(mk);
    var pool = type === "SMART" ? m.smart : state.oppFund;
    var cap = type === "SMART" ? smartReservable(m) : oppReservable();
    if (vnd > pool.a + 1e-6) return { ok: false, mk: mk, cap: cap, reason: "AVAILABLE" };
    if (vnd > cap + 1e-6) return { ok: false, mk: mk, cap: cap, reason: "UNLOCK" };
    pool.a -= vnd; pool.r += vnd;
    return { ok: true, mk: mk, cap: cap };
  }

  /** Strategy §8: cancel / invalidation / expiry trả TOÀN BỘ phần còn lại về AVAILABLE —
   *  gồm cả phần chưa fill của zone PARTIALLY_FILLED, không chỉ zone ACTIVE/CANCELLED.
   *  Zone giữ nguyên trạng thái lịch sử (Product §8). */
  function releaseLadder(L) {
    var RELEASABLE = ["ACTIVE", "CANCELLED", "PARTIALLY_FILLED", "SUSPENDED", "TRIGGERED"];
    var open = 0;
    L.zones.forEach(function (z) {
      if (RELEASABLE.indexOf(z.status) === -1) return;
      var rem = Math.max(0, z.target_vnd - (z.filled_vnd || 0));
      open += rem;
      z.released_vnd = (z.released_vnd || 0) + rem;
      z.target_vnd = z.filled_vnd || 0;   // phần còn lại không còn là cam kết vốn
    });
    if (open <= 0) return;
    // T-09A / V-01: pool nhận lại vốn là pool của tháng SỞ HỮU ladder.
    var mk = ladderMonth(L), m = month(mk);
    var take;
    if (L.type === "SMART") {
      take = Math.min(open, m.smart.r);
      m.smart.r -= take; m.smart.a += take;
    } else {
      take = Math.min(open, state.oppFund.r);
      state.oppFund.r -= take; state.oppFund.a += take;
    }
    // Ghi đúng số THỰC SỰ dịch chuyển, không ghi `open`. Chênh lệch (nếu có) là dấu hiệu sổ
    // không nhất quán và phải nhìn thấy được trong ledger.
    var short = open - take > 1e-6 ? open - take : 0;
    var ent = { pool: L.type, type: "RELEASE", vnd: take, month: mk, ladder: L.id,
                reason: short ? "LADDER_RELEASE_SHORTFALL" : "LADDER_RELEASE" };
    if (short) ent.shortfall = short;   // hiện trên cột Reason của bảng Sổ vốn
    ledger(ent);
  }

  function createLadder(type, anchor, capVnd) {
    if (!view) return { err: "Chưa có dữ liệu giá — nạp seed ở tab Thiết lập." };
    var sp = type === "SMART" ? view.smartSpacing : view.oppSpacing;
    if (!Number.isFinite(sp)) return { err: "Chưa đủ lịch sử để tính ADR30." };
    var rs = reserveFor(type, capVnd);
    if (!rs.ok) {
      if (rs.reason === "AVAILABLE") return { err: "Không đủ vốn available trong pool." };
      var u = type === "SMART" ? view.smartUnlock : view.oppUnlock;
      return { err: "Vượt phần đã unlock (" + pct(u, 1) + "): tối đa " + vnd(rs.cap) +
                    " ₫ được reserve lúc này (Strategy §12)." };
    }
    var L = E.buildLadder(type, anchor, sp, capVnd, view.score.oscore);
    L.id = "L" + (state.ladders.length + 1) + "-" + Date.now().toString(36);
    L.created = new Date().toISOString();
    L.month = rs.mk;   // T-09A / V-01: khoá tháng sở hữu vốn ngay tại lúc reserve
    state.ladders.push(L);
    ledger({ pool: type, type: "RESERVE", vnd: capVnd, reason: type + "_LADDER",
             month: rs.mk, ladder: L.id });
    return { ladder: L };
  }

  function cancelLadder(id) {
    var L = state.ladders.filter(function (x) { return x.id === id; })[0];
    if (!L || L.status !== "ACTIVE") return;
    L.status = "CANCELLED";
    L.zones.forEach(function (z) { if (z.status === "ACTIVE") z.status = "CANCELLED"; });
    releaseLadder(L);
  }

  /* ---------------- formatting ---------------- */

  var nf = function (v, d) {
    if (!Number.isFinite(v)) return "—";
    return v.toLocaleString("vi-VN", { minimumFractionDigits: d === undefined ? 2 : d,
                                       maximumFractionDigits: d === undefined ? 2 : d });
  };
  var vnd = function (v) {
    if (!Number.isFinite(v)) return "—";
    return Math.round(v).toLocaleString("vi-VN");
  };
  var usd = function (v, d) {
    return Number.isFinite(v) ? "$" + nf(v, d) : "—";
  };
  var pct = function (v, d) {
    return Number.isFinite(v) ? (v * 100).toFixed(d === undefined ? 1 : d) + "%" : "—";
  };
  var esc = function (s) {
    return String(s === null || s === undefined ? "" : s).replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  };
  var shortTs = function (t) { return String(t).slice(0, 16).replace("T", " "); };

  /* ---------------- render ---------------- */

  function renderZonePicker() {
    var sel = $("buyZone");
    var keep = sel.value;
    var open = openZones();
    var px = view ? view.last.close : NaN;
    sel.innerHTML = '<option value="">— không gắn zone —</option>' +
      open.sort(function (a, b) { return b.z.target_price - a.z.target_price; })
        .map(function (o) {
          var remain = Math.max(0, o.z.target_vnd - (o.z.filled_vnd || 0));
          var isHit = Number.isFinite(px) && px <= o.z.target_price;
          return '<option value="' + esc(o.L.id + "|" + o.z.index) + '">' +
            (isHit ? "● " : "") + o.L.type.charAt(0) + o.z.index + " @ " +
            nf(o.z.target_price) + " · " + vnd(remain) + " ₫</option>";
        }).join("");
    if (keep) sel.value = keep;
  }

  function render() {
    recompute();
    renderPersistence();   // gồm cả renderBanners()
    renderDash();
    renderLadder();
    renderZonePicker();
    renderHistory();
    renderSetup();
    $("foot").textContent = "ETH DCA OS " + ((seed && seed.strategy_version) || "V2.1.5") +
      " · rev " + (state.rev || 0) +
      (seed ? " · seed " + (seed.dataset_hash || "").slice(0, 10) : " · chưa có seed");
  }

  function renderBanners() {
    var out = persistenceBanners();   // T-09B: trạng thái nguồn bền luôn đứng đầu
    out += '<div class="banner warn"><span class="mk">CHƯA QUA VERDICT</span><p>' +
      "Implementation Plan §9 chỉ cho phép dựng app sau khi backtest cho verdict BUILD. " +
      "Verdict chưa được chạy trên dữ liệu thật, nên hãy coi mọi khuyến nghị ở đây là " +
      "<strong>công cụ ghi chép và tính toán</strong>, không phải tín hiệu đã được chứng thực." +
      "</p></div>";
    if (!seed) {
      out += '<div class="banner bad"><span class="mk">THIẾU DỮ LIỆU</span><p>' +
        "Chưa nạp lịch sử giá. Sang tab <strong>Thiết lập</strong> và nạp " +
        "<code>live_seed.json</code> — không có 365 ngày lịch sử thì không tính được OSCORE." +
        "</p></div>";
    } else if (view) {
      var p = E.checkParity(seed);
      if (!p.ok) {
        out += '<div class="banner bad"><span class="mk">LỆCH ENGINE</span><p>' +
          "OSCORE tính trong trình duyệt lệch khỏi bản Python ở " + p.mismatches.length +
          " ngày (lệch lớn nhất " + p.worst.toExponential(2) + "). Không tin số trên trang này " +
          "cho tới khi tìm ra nguyên nhân.</p></div>";
      }
      if (view.score.data_quality !== "GOOD") {
        out += '<div class="banner ' + (view.score.data_quality === "INVALID" ? "bad" : "warn") +
          '"><span class="mk">' + view.score.data_quality + "</span><p>" +
          view.score.missing_count + " sub-factor thiếu dữ liệu. Theo Strategy §3, phần thiếu " +
          "đóng góp 0 và score <strong>không</strong> được chuẩn hóa lên — nên OSCORE hiện " +
          "thấp hơn thực tế, không cao hơn.</p></div>";
      }
      var staleDays = daysSince(view.last.d);
      if (staleDays >= 2) {
        out += '<div class="banner warn"><span class="mk">DỮ LIỆU CŨ</span><p>' +
          "Giá mới nhất là ngày " + esc(view.last.d) + " (" + staleDays + " ngày trước). " +
          "Nhập giá đóng cửa mới ở tab <strong>Nhập số liệu</strong>.</p></div>";
      }
    }
    // Ngoài nhánh seed: huỷ ladder KHÔNG cần `view`, nên cảnh báo tháng sở hữu suy luận phải
    // hiện kể cả khi chưa nạp seed.
    var legacyL = inferredMonthLadders();
    if (legacyL.length) {
      out += '<div class="banner warn"><span class="mk">THÁNG SỞ HỮU SUY LUẬN</span><p>' +
        legacyL.length + " ladder được tạo trước bản vá kế toán T-09A nên không ghi tháng " +
        "sở hữu vốn. App đang <strong>suy luận</strong> tháng đó từ thời điểm tạo (" +
        esc(legacyL.map(function (L) { return L.id + "→" + ladderMonth(L); }).join(", ")) +
        "). Hãy đối chiếu với sổ trước khi hủy hoặc để chúng invalidate — nếu sai, vốn sẽ " +
        "được trả về nhầm tháng.</p></div>";
    }
    $("banners").innerHTML = out;
  }

  function daysSince(dstr) {
    var t = Date.parse(dstr + "T00:00:00Z");
    if (!Number.isFinite(t)) return 0;
    return Math.floor((Date.now() - t) / 86400000);
  }

  function renderDash() {
    if (!view) {
      $("osVal").textContent = "—";
      $("stateChips").innerHTML = "";
      $("factorBars").innerHTML = "";
      $("subGrid").innerHTML = "";
      $("marketStats").innerHTML = '<p class="empty" style="grid-column:1/-1">Chưa có dữ liệu giá.</p>';
      $("actionBox").innerHTML = "";
      $("portfolioStats").innerHTML = "";
      $("treasuryStats").innerHTML = "";
      $("poolBars").innerHTML = "";
      return;
    }
    var s = view.score, L = view.last, c = cfg();

    $("osVal").textContent = Number.isFinite(s.oscore) ? s.oscore.toFixed(1) : "—";
    $("osVal").style.color = s.oscore >= 68 ? "var(--pass)"
      : (s.oscore >= 35 ? "var(--ink)" : "var(--muted)");

    var dqCls = s.data_quality === "GOOD" ? "g" : (s.data_quality === "DEGRADED" ? "y" : "r");
    var rgCls = view.regime.name === "CRASH" ? "r"
      : (view.regime.name === "STRESSED" ? "y" : "n");
    $("stateChips").innerHTML =
      '<span class="chip ' + rgCls + '">' + view.regime.name + "</span>" +
      '<span class="chip ' + dqCls + '">' + s.data_quality + "</span>" +
      '<span class="chip n">Smart unlock ' + pct(view.smartUnlock) + "</span>" +
      '<span class="chip n">Opp unlock ' + pct(view.oppUnlock) + "</span>";

    var factors = [
      ["Price Location", s.price_location_score, c.score_weights[0]],
      ["Market Stress", s.market_stress_score, c.score_weights[1]],
      ["Relative Value", s.relative_value_score, c.score_weights[2]],
    ];
    $("factorBars").innerHTML = factors.map(function (f) {
      var w = Number.isFinite(f[1]) ? (f[1] / f[2]) * 100 : 0;
      return '<div class="fbar"><span class="fl">' + f[0] + "</span>" +
        '<div class="ftrack"><div class="ffill" style="width:' + Math.max(0, Math.min(100, w)) +
        '%"></div></div><span class="fv">' + nf(f[1], 1) + " / " + f[2] + "</span></div>";
    }).join("");

    $("subGrid").innerHTML = E.SUB_NAMES.map(function (k) {
      var v = s.sub[k];
      return '<div class="sub"><div class="k">' + k + '</div><div class="v">' +
        (Number.isFinite(v) ? v.toFixed(2) : "—") + "</div></div>";
    }).join("");

    var chg = view.prev ? L.close / view.prev.close - 1 : NaN;
    $("marketStats").innerHTML =
      stat("ETH", usd(L.close), (Number.isFinite(chg) ? (chg >= 0 ? "+" : "") + pct(chg, 2) : "") +
        " · " + esc(L.d)) +
      stat("Drawdown 365d", pct(L.dd365, 1), "đỉnh " + usd(L.high365, 0)) +
      stat("MA200", usd(L.ma200, 0), "tỷ lệ " + nf(L.ma_ratio, 3)) +
      stat("RSI14", nf(L.rsi14, 1), "return7 " + pct(L.return7, 1)) +
      stat("ADR30", pct(L.adr30, 2), "spacing " + pct(view.smartSpacing, 1)) +
      stat("ETH/BTC", nf(L.ethbtc, 6), "pct180 " + pct(L.ethbtc_percentile180, 0));

    renderAction();

    var avgUsdt = state.eth > 0 ? state.costUsdt / state.eth : NaN;
    var avgVnd = state.eth > 0 && state.costVnd > 0 ? state.costVnd / state.eth : NaN;
    var mv = state.eth * L.close;
    var pnl = Number.isFinite(mv) && state.costUsdt > 0 ? mv - state.costUsdt : NaN;
    $("portfolioStats").innerHTML =
      stat("ETH nắm giữ", nf(state.eth, 6), state.trades.length + " lệnh mua") +
      stat("Giá trị thị trường", usd(mv, 2), "theo giá " + esc(L.d)) +
      stat("Vốn đã bỏ", usd(state.costUsdt, 2),
        state.costVnd > 0 ? vnd(state.costVnd) + " ₫" : "chưa ghi tỷ giá") +
      stat("PnL", Number.isFinite(pnl) ? (pnl >= 0 ? "+" : "") + usd(pnl, 2) : "—",
        Number.isFinite(pnl) && state.costUsdt > 0
          ? pct(pnl / state.costUsdt, 1) : "—",
        Number.isFinite(pnl) ? (pnl >= 0 ? "var(--pass)" : "var(--fail)") : null) +
      stat("Giá vốn TB", usd(avgUsdt, 2),
        Number.isFinite(avgVnd) ? vnd(avgVnd) + " ₫/ETH" : "—");

    $("treasuryStats").innerHTML =
      stat("VND available", vnd(state.treasury.vnd) + " ₫", "chưa đổi sang USDT") +
      stat("USDT available", usd(state.treasury.usdt), "sẵn sàng thực thi") +
      stat("ETH holdings", nf(state.eth, 6), "đã xác nhận mua") +
      stat("Opportunity Fund", vnd(poolTotal(state.oppFund)) + " ₫",
        "available " + vnd(state.oppFund.a));

    var mk = currentMonth(), m = state.months[mk];
    if (!m) {
      $("poolBars").innerHTML = '<p class="empty">Chưa nạp vốn tháng nào.</p>';
    } else {
      $("poolBars").innerHTML =
        poolBar("Base " + mk, m.base) +
        poolBar("Smart " + mk, m.smart) +
        poolBar("Opportunity Fund", state.oppFund);
    }
  }

  function stat(k, v, s, color) {
    return '<div class="stat"><p class="k">' + esc(k) + '</p><span class="v"' +
      (color ? ' style="color:' + color + '"' : "") + ">" + esc(v) + "</span>" +
      (s ? '<p class="s">' + esc(s) + "</p>" : "") + "</div>";
  }

  function poolBar(label, p) {
    var t = poolTotal(p);
    var w = function (x) { return t > 0 ? (x / t) * 100 : 0; };
    return '<div class="pool"><div class="ph"><span>' + esc(label) + "</span><b>" +
      vnd(t) + " ₫</b></div><div class=\"ptrack\">" +
      '<div class="pseg dep" style="width:' + w(p.d) + '%"></div>' +
      '<div class="pseg res" style="width:' + w(p.r) + '%"></div>' +
      '<div class="pseg avl" style="width:' + w(p.a) + '%"></div></div>' +
      '<div class="plegend"><span>A ' + vnd(p.a) + "</span><span>R " + vnd(p.r) +
      "</span><span>D " + vnd(p.d) + "</span></div></div>";
  }

  /** Tỷ giá VND/USDT tham chiếu: lấy từ giao dịch P2P mua gần nhất. */
  function lastP2PRate() {
    for (var i = state.p2p.length - 1; i >= 0; i--) {
      if (state.p2p[i].dir === "VND_TO_USDT" && state.p2p[i].rate > 0) return state.p2p[i].rate;
    }
    return null;
  }

  function openZones() {
    var out = [];
    state.ladders.forEach(function (Ld) {
      if (Ld.status !== "ACTIVE") return;
      Ld.zones.forEach(function (z) {
        if (z.status === "ACTIVE" || z.status === "PARTIALLY_FILLED") out.push({ L: Ld, z: z });
      });
    });
    return out;
  }

  function renderAction() {
    var L = view.last;
    var box = $("actionBox");
    var open = openZones();
    var hit = open.filter(function (o) { return L.close <= o.z.target_price; })
      .sort(function (a, b) { return b.z.target_price - a.z.target_price; });

    if (hit.length) {
      var top = hit[0];
      var remainVnd = Math.max(0, top.z.target_vnd - (top.z.filled_vnd || 0));
      var rate = lastP2PRate();
      // Cần bao nhiêu USDT: quy đổi phần VND còn lại theo tỷ giá P2P gần nhất.
      var needUsdt = rate ? remainVnd / rate : null;
      var enough = needUsdt === null
        ? state.treasury.usdt > 0
        : state.treasury.usdt + 1e-6 >= needUsdt;
      box.className = "action " + (enough ? "go" : "fund");
      box.innerHTML = '<div class="ah">' +
        (enough ? "READY TO BUY" : "FUNDING REQUIRED") + "</div><div class=\"ab\">" +
        '<div class="big">' + top.L.type + " zone " + top.z.index + " · " +
        vnd(remainVnd) + " ₫" +
        (needUsdt !== null ? ' <span style="font-size:15px;color:var(--muted)">≈ $' +
          nf(needUsdt) + "</span>" : "") + "</div>" +
        '<p class="why">Giá ' + nf(L.close) + " đã chạm mục tiêu " + nf(top.z.target_price) +
        ". " + (enough
          ? "Thực hiện lệnh trên sàn rồi ghi lại ở tab Nhập số liệu, nhớ chọn đúng zone."
          : "Kho USDT còn $" + nf(state.treasury.usdt) +
            (needUsdt !== null ? ", thiếu $" + nf(Math.max(0, needUsdt - state.treasury.usdt)) : "") +
            " — cần một giao dịch P2P trước.") +
        " Zone chỉ chuyển sang EXECUTED sau khi bạn xác nhận đã mua thật.</p></div>";
      return;
    }
    var openZonesList = open;

    var next = openZonesList.sort(function (a, b) {
      return b.z.target_price - a.z.target_price;
    })[0];
    box.className = "action wait";
    box.innerHTML = '<div class="ah">WAIT</div><div class="ab">' +
      (next
        ? '<div class="big">Zone kế: ' + nf(next.z.target_price) + "</div>" +
          '<p class="why">Còn ' + pct(next.z.target_price / L.close - 1, 2) +
          " so với giá hiện tại (" + next.L.type + " zone " + next.z.index + ")." +
          " Không có zone nào bị chạm — không hành động.</p>"
        : '<div class="big">Không có zone đang mở</div>' +
          '<p class="why">Tạo ladder ở tab Ladder khi muốn đặt vùng mua, hoặc chờ' +
          " điều kiện chiến lược. Base schedule vẫn chạy độc lập với OSCORE.</p>") +
      "</div>";
  }

  function renderLadder() {
    var c = cfg();
    $("spMin").textContent = pct(c.smart_spacing_min, 0);
    $("spMax").textContent = pct(c.smart_spacing_max, 0);
    var mk = currentMonth(), m = state.months[mk];
    $("ldCapHint").textContent = m
      ? "Smart available " + vnd(m.smart.a) + " ₫ · Opp " + vnd(state.oppFund.a) + " ₫"
      : "Chưa nạp vốn tháng nào";
    if (view && !$("ldAnchor").value) $("ldAnchor").placeholder = nf(view.last.close);

    var act = state.ladders.filter(function (L) { return L.status === "ACTIVE"; });
    var others = state.ladders.filter(function (L) { return L.status !== "ACTIVE"; });
    if (!state.ladders.length) {
      $("ladderList").innerHTML = '<div class="card"><p class="empty" style="padding:8px">' +
        "Chưa có ladder nào.</p></div>";
      return;
    }
    var px = view ? view.last.close : NaN;
    $("ladderList").innerHTML = act.concat(others).map(function (L) {
      var rows = L.zones.map(function (z) {
        var dist = Number.isFinite(px) ? z.target_price / px - 1 : NaN;
        var isHit = Number.isFinite(px) && px <= z.target_price && z.status === "ACTIVE";
        return '<tr' + (isHit ? ' class="hit"' : "") + "><td class=\"mono\">" +
          L.type.charAt(0) + z.index + '</td><td class="num">' + nf(z.target_price) +
          '</td><td class="num">' + (Number.isFinite(dist) ? pct(dist, 2) : "—") +
          '</td><td class="num">' + vnd(z.target_vnd) + '</td><td class="num">' +
          pct(z.allocation_pct, 0) + '</td><td class="mono">' + z.status + "</td></tr>";
      }).join("");
      return '<div class="card" style="margin-bottom:12px">' +
        '<div style="display:flex;justify-content:space-between;align-items:baseline;' +
        'gap:12px;flex-wrap:wrap;margin-bottom:10px">' +
        "<div><strong>" + L.type + "</strong> <span class=\"mono\" style=\"color:var(--muted);" +
        'font-size:12px">anchor ' + nf(L.anchor_price) + " · spacing " + pct(L.spacing_pct, 2) +
        " · invalidation " + nf(L.invalidation_price) + "</span></div>" +
        '<div style="display:flex;gap:8px;align-items:center">' +
        '<span class="chip ' + (L.status === "ACTIVE" ? "g" : "n") + '">' + L.status + "</span>" +
        (L.status === "ACTIVE"
          ? '<button class="sm danger" data-cancel="' + esc(L.id) + '">Hủy</button>' : "") +
        "</div></div>" +
        '<div class="scroller"><table><thead><tr><th>Zone</th><th class="num">Target</th>' +
        '<th class="num">Cách giá</th><th class="num">Vốn VND</th><th class="num">%</th>' +
        "<th>Status</th></tr></thead><tbody>" + rows + "</tbody></table></div></div>";
    }).join("");

    Array.prototype.forEach.call(document.querySelectorAll("[data-cancel]"), function (b) {
      b.addEventListener("click", function () {
        if (!canWrite("ldMsg")) return;
        cancelLadder(b.getAttribute("data-cancel"));
        touch();
      });
    });
  }

  function renderHistory() {
    $("tradeTable").innerHTML = state.trades.length
      ? '<table><thead><tr><th>Thời điểm</th><th>Nguồn</th><th>Zone</th>' +
        '<th class="num">USDT</th>' +
        '<th class="num">Giá khớp</th><th class="num">Khuyến nghị</th>' +
        '<th class="num">Shortfall</th><th class="num">ETH</th></tr></thead><tbody>' +
        state.trades.slice().reverse().map(function (t) {
          return "<tr><td class=\"mono\">" + esc(shortTs(t.ts)) + '</td><td class="mono">' +
            esc(t.src) + '</td><td class="mono">' + esc(t.zone || "—") +
            '</td><td class="num">' + nf(t.usdt) + '</td><td class="num">' +
            nf(t.price) + '</td><td class="num">' + (t.recPrice ? nf(t.recPrice) : "—") +
            '</td><td class="num"' +
            (Number.isFinite(t.shortfallBps)
              ? ' style="color:' + (t.shortfallBps > 0 ? "var(--fail)" : "var(--pass)") + '"' : "") +
            ">" + (Number.isFinite(t.shortfallBps)
              ? (t.shortfallBps >= 0 ? "+" : "") + t.shortfallBps.toFixed(0) + " bps" : "—") +
            '</td><td class="num">' + nf(t.eth, 6) + "</td></tr>";
        }).join("") + "</tbody></table>"
      : '<p class="empty">Chưa có lệnh mua nào.</p>';

    $("p2pTable").innerHTML = state.p2p.length
      ? '<table><thead><tr><th>Thời điểm</th><th>Chiều</th><th class="num">VND</th>' +
        '<th class="num">USDT</th><th class="num">Phí</th>' +
        '<th class="num">Tỷ giá thực</th></tr></thead><tbody>' +
        state.p2p.slice().reverse().map(function (p) {
          return "<tr><td class=\"mono\">" + esc(shortTs(p.ts)) + '</td><td class="mono">' +
            esc(p.dir) + '</td><td class="num">' + vnd(p.vnd) + '</td><td class="num">' +
            nf(p.usdt) + '</td><td class="num">' + vnd(p.fee) + '</td><td class="num">' +
            vnd(p.rate) + "</td></tr>";
        }).join("") + "</tbody></table>"
      : '<p class="empty">Chưa có giao dịch P2P nào.</p>';

    $("ledgerTable").innerHTML = state.ledger.length
      ? '<table><thead><tr><th>Thời điểm</th><th>Pool</th><th>Loại</th>' +
        '<th class="num">VND</th><th class="num">USDT</th><th>Reason</th></tr></thead><tbody>' +
        state.ledger.slice().reverse().slice(0, 200).map(function (l) {
          return "<tr><td class=\"mono\">" + esc(shortTs(l.ts)) + '</td><td class="mono">' +
            esc(l.pool) + '</td><td class="mono">' + esc(l.type) + '</td><td class="num">' +
            (Number.isFinite(l.vnd) ? vnd(l.vnd) : "—") + '</td><td class="num">' +
            (Number.isFinite(l.usdt) ? nf(l.usdt) : "—") + '</td><td class="mono">' +
            esc(l.reason) + "</td></tr>";
        }).join("") + "</tbody></table>"
      : '<p class="empty">Sổ vốn trống.</p>';
  }

  function renderSetup() {
    if (seed && view) {
      var p = E.checkParity(seed);
      $("parityBox").innerHTML = '<div class="stats">' +
        stat("Ngày đối chiếu", String(p.checked), "so với score Python trong seed") +
        stat("Lệch lớn nhất", p.checked ? p.worst.toExponential(2) : "—",
          p.worstDay ? "ngày " + p.worstDay : "") +
        stat("Kết quả", p.ok ? "KHỚP" : "LỆCH",
          p.ok ? "hai bản cài đặt đồng thuận" : p.mismatches.length + " ngày lệch",
          p.ok ? "var(--pass)" : "var(--fail)") +
        "</div>";
    } else {
      $("parityBox").innerHTML = '<p class="empty">Chưa có seed để đối chiếu.</p>';
    }

    var c = cfg();
    $("cfgTable").innerHTML = "<table><thead><tr><th>Tham số</th><th class=\"num\">Giá trị</th>" +
      "</tr></thead><tbody>" +
      Object.keys(c).sort().map(function (k) {
        var v = c[k];
        return "<tr><td class=\"mono\">" + esc(k) + '</td><td class="num">' +
          esc(Array.isArray(v) ? v.join(" / ") : v) + "</td></tr>";
      }).join("") + "</tbody></table>";
  }

  /* ---------------- persistence (T-09B — DEC-019/020/021) ----------------
   *
   * Nguồn bền DUY NHẤT: Cloud Firestore, hai document `ethdca/state` (sổ kế toán, MUST_PERSIST
   * tầng 1) và `ethdca/seed` (dữ liệu tham chiếu, tầng 2). localStorage chỉ là mirror/cache.
   *
   * Save flow:  touch() -> rev += 1 -> mirror localStorage (best-effort) -> persist() ghi lên
   *             Firestore và CHỜ máy chủ xác nhận. UI chỉ báo "Đã lưu bền" khi promise của
   *             set() resolve — cache cục bộ của SDK KHÔNG phải xác nhận (CHECK-T09B-10).
   * Load flow:  initPersistence() — init SDK -> Anonymous Auth -> đọc từ SERVER (không lấy
   *             cache) -> validateState() -> ONLINE, hoặc một phase lỗi hiện rõ + khoá ghi sổ.
   * Không có retry policy nhiều tầng, circuit breaker, queue bền hay đồng bộ realtime —
   * công cụ cá nhân tần suất thấp (DEC-021).
   */

  function touch() {
    state.rev = (state.rev || 0) + 1;
    mirror();
    render();
    persist();
  }

  function mirror() {
    try { localStorage.setItem(STORE_STATE, JSON.stringify(state)); } catch (e) { /* private mode */ }
  }
  function readLS(key) {
    try {
      var t = localStorage.getItem(key);
      return t ? JSON.parse(t) : null;
    } catch (e) { return null; }
  }
  /** Bản ghi lên nguồn bền = đúng bản JSON mà mirror đã dùng: bỏ `undefined` (Firestore từ chối),
   *  không thêm/không đổi trường nào — không "chuẩn hoá" state (§12 T-09A). */
  function plain(o) { return JSON.parse(JSON.stringify(o === undefined ? null : o)); }
  function errCode(e) {
    if (!e) return "unknown";
    return String(e.code || e.message || e).slice(0, 120);
  }
  function isNum(x) { return typeof x === "number" && Number.isFinite(x); }
  var EPS = 1e-6;
  function isPool(p) {
    return !!p && typeof p === "object" && !Array.isArray(p) &&
      isNum(p.a) && isNum(p.r) && isNum(p.d) && p.a >= -EPS && p.r >= -EPS && p.d >= -EPS;
  }

  /** Kiểm tra một bản durable TRƯỚC khi nó được phép trở thành sổ kế toán (CHECK-T09B-12).
   *  Chỉ kiểm schema + bất biến kế toán đo được trên state đã lưu. KHÔNG sửa, KHÔNG backfill
   *  (`ladders[].month` được phép vắng — historical state giữ nguyên, CHECK-T09B-15). */
  function validateState(o) {
    var bad = function (r) { return { ok: false, reason: r }; };
    if (!o || typeof o !== "object" || Array.isArray(o)) return bad("không phải object");
    if (o.schema !== "ethdca.tracker/1") {
      return bad("thiếu hoặc sai `schema` (" + JSON.stringify(o.schema === undefined ? null : o.schema) + ")");
    }
    if (!isNum(o.rev) || o.rev < 0 || Math.floor(o.rev) !== o.rev) return bad("`rev` không hợp lệ");
    if (!o.months || typeof o.months !== "object" || Array.isArray(o.months)) return bad("`months` sai kiểu");
    var tol = function (c) { return 1e-6 * Math.max(1, Math.abs(c)) + 1e-6; };
    var oppAddedSum = 0;
    var keys = Object.keys(o.months);
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i], m = o.months[k];
      if (!/^\d{4}-\d{2}$/.test(k)) return bad("khoá tháng `" + k + "` không phải YYYY-MM");
      if (!m || typeof m !== "object" || Array.isArray(m)) return bad("`months." + k + "` sai kiểu");
      if (!isNum(m.contribution) || m.contribution < -EPS) return bad("`months." + k + ".contribution` không hợp lệ");
      if (!isNum(m.oppAdded) || !isNum(m.oppOverflow) || m.oppAdded < -EPS || m.oppOverflow < -EPS) {
        return bad("`months." + k + ".oppAdded/oppOverflow` không hợp lệ");
      }
      if (!isPool(m.base) || !isPool(m.smart)) {
        return bad("pool base/smart tháng " + k + " thiếu a/r/d, không hữu hạn hoặc âm");
      }
      // TOTAL = AVAILABLE + RESERVED + DEPLOYED với TOTAL biết trước: contribution được chia
      // trọn vào base + smart + Opportunity (Strategy §8; phần Opp overflow đã nằm trong smart),
      // và mọi thao tác sau đó chỉ dịch chuyển giữa a/r/d nên tổng này là bất biến.
      var total = poolTotal(m.base) + poolTotal(m.smart) + m.oppAdded;
      if (Math.abs(total - m.contribution) > tol(m.contribution)) {
        return bad("tháng " + k + ": TOTAL = A+R+D bị vi phạm (base+smart+oppAdded = " + total +
                   " ≠ contribution " + m.contribution + ")");
      }
      oppAddedSum += m.oppAdded;
    }
    if (!isPool(o.oppFund)) return bad("`oppFund` thiếu a/r/d, không hữu hạn hoặc âm");
    if (Math.abs(poolTotal(o.oppFund) - oppAddedSum) > tol(oppAddedSum)) {
      return bad("Opportunity Fund: TOTAL = A+R+D bị vi phạm (" + poolTotal(o.oppFund) +
                 " ≠ Σ oppAdded " + oppAddedSum + ")");
    }
    if (!o.treasury || typeof o.treasury !== "object" || !isNum(o.treasury.vnd) || !isNum(o.treasury.usdt)) {
      return bad("`treasury` không hợp lệ");
    }
    if (!isNum(o.eth) || o.eth < -EPS) return bad("`eth` không hợp lệ");
    if (!isNum(o.costUsdt) || !isNum(o.costVnd) || o.costUsdt < -EPS || o.costVnd < -EPS) {
      return bad("`costUsdt`/`costVnd` không hợp lệ");
    }
    var arrs = ["ladders", "trades", "p2p", "ledger", "extraDays"];
    for (var a = 0; a < arrs.length; a++) {
      if (!Array.isArray(o[arrs[a]])) return bad("`" + arrs[a] + "` không phải mảng");
    }
    for (var j = 0; j < o.ladders.length; j++) {
      var L = o.ladders[j];
      if (!L || typeof L !== "object" || !Array.isArray(L.zones)) return bad("ladder #" + j + " thiếu `zones`");
      if (L.month !== undefined && L.month !== null && typeof L.month !== "string") {
        return bad("ladder #" + j + " `month` sai kiểu");
      }
      for (var z = 0; z < L.zones.length; z++) {
        var Z = L.zones[z];
        if (!Z || typeof Z !== "object" || !isNum(Z.target_vnd) || !isNum(Z.target_price)) {
          return bad("ladder #" + j + " zone #" + z + " thiếu target_vnd/target_price");
        }
        if (Z.filled_vnd !== undefined && !isNum(Z.filled_vnd)) return bad("ladder #" + j + " zone #" + z + " `filled_vnd` không hợp lệ");
        if (Z.released_vnd !== undefined && !isNum(Z.released_vnd)) return bad("ladder #" + j + " zone #" + z + " `released_vnd` không hợp lệ");
      }
    }
    return { ok: true };
  }
  function validSeed(s) { return !!s && typeof s === "object" && Array.isArray(s.history) && s.history.length > 0; }

  function unsaved() { return P.durableRev !== state.rev || P.seedPending; }
  function expectedRevLabel() { return P.durableRev === null ? "chưa có" : P.durableRev; }
  function phaseLabel() {
    return ({
      INIT: "đang kết nối", UNCONFIGURED: "chưa cấu hình Firebase", AUTH_FAILED: "xác thực thất bại",
      UNRECOGNIZED: "không nhận diện thiết bị", OFFLINE: "không đọc được nguồn bền",
      CORRUPT: "nguồn bền không hợp lệ", ONLINE: "đã kết nối",
    })[P.phase] || P.phase;
  }
  /** Mọi thao tác ghi sổ đều đi qua đây: chỉ được ghi khi nguồn bền đã nạp xong (fail closed). */
  function canWrite(msgId) {
    if (P.phase === "ONLINE") return true;
    if (msgId) msg(msgId, "Không ghi sổ — nguồn bền: " + phaseLabel() + ". Xem banner đầu trang.", "err");
    return false;
  }
  function setPhase(phase, detail) {
    P.phase = phase;
    P.detail = detail || "";
    render();
  }

  function fbCfg() { return window.ETHDCA_FIREBASE_CONFIG || {}; }
  function configured(c) {
    // Bốn giá trị Firebase Console cấp cho một Web app; thiếu/để "REQUIRED" = chưa thiết lập.
    var need = ["apiKey", "authDomain", "projectId", "appId"];
    for (var i = 0; i < need.length; i++) {
      var v = c[need[i]];
      if (typeof v !== "string" || !v || v === "REQUIRED") return false;
    }
    return true;
  }

  /** Ghi state (và seed nếu đang chờ) lên Firestore; chỉ khi máy chủ xác nhận mới đổi
   *  durableRev. Lệnh ghi chồng nhau được gộp: bản mới nhất được ghi lại sau khi lệnh hiện
   *  tại kết thúc (resave). */
  function persist() {
    if (P.phase !== "ONLINE" || !fb.db) return;
    if (P.saving) { P.resave = true; return; }
    P.saving = true; P.resave = false; P.lastError = null; P.unconfirmed = false;
    var snap = plain(state);
    var rev = snap.rev;
    var seedSnap = P.seedPending && seed ? plain(seed) : null;
    var gen = P.seedGen;
    var expected = P.durableRev;   // bản bền mà trang này đang đứng trên (null = chưa có)
    renderPersistence();
    // Ghi có điều kiện: chỉ ghi đè khi bản trên máy chủ vẫn đúng là bản trang này đã nạp/ghi
    // lần cuối. Một tab/thiết bị khác đã ghi trước -> từ chối (stale-durable), KHÔNG ghi đè
    // bản mới hơn — cùng nguyên tắc CHECK-T09B-16 áp cho bản trong bộ nhớ của tab cũ.
    var ref = fb.db.doc("ethdca/state");
    var work = fb.db.runTransaction(function (tx) {
      return tx.get(ref).then(function (cur) {
        var serverRev = cur.exists ? cur.data().rev : null;
        if (serverRev !== expected) {
          var e = new Error("stale-durable");
          e.code = "stale-durable";
          e.serverRev = serverRev;
          throw e;
        }
        tx.set(ref, snap);
        if (seedSnap) tx.set(fb.db.doc("ethdca/seed"), seedSnap);
      });
    });
    var limit = isNum(fbCfg().ackTimeoutMs) ? fbCfg().ackTimeoutMs : 15000;
    var timer = setTimeout(function () {
      if (P.saving) { P.unconfirmed = true; renderPersistence(); }
    }, limit);
    work.then(function () {
      clearTimeout(timer);
      P.durableRev = rev;
      P.lastAck = new Date().toISOString();
      if (seedSnap && gen === P.seedGen) { P.seedPending = false; P.seedDurable = true; }
    }, function (err) {
      clearTimeout(timer);
      P.lastError = errCode(err);
      P.staleRev = err && err.code === "stale-durable" ? err.serverRev : undefined;
    }).then(function () {
      P.saving = false; P.unconfirmed = false;
      if (P.resave) persist(); else renderPersistence();
    });
  }

  /** Nút "Lưu lại": ghi lại bản hiện tại khi lần trước thất bại/chưa xác nhận. */
  function save() { persist(); }

  function renderPersistence() {
    var chip = $("saveChip"), btn = $("saveBtn");
    var text, cls;
    if (P.phase === "INIT") { text = "Đang kết nối nguồn bền…"; cls = ""; }
    else if (P.phase !== "ONLINE") { text = "KHÔNG GHI SỔ — " + phaseLabel(); cls = "dirty"; }
    else if (P.saving && P.unconfirmed) { text = "CHƯA XÁC NHẬN — máy chủ chưa trả lời"; cls = "dirty"; }
    else if (P.saving) { text = "Đang lưu lên Firestore…"; cls = ""; }
    else if (P.lastError) { text = "CHƯA LƯU — " + P.lastError; cls = "dirty"; }
    else if (unsaved()) { text = "CHƯA LƯU"; cls = "dirty"; }
    else if (P.durableRev === null) { text = "Chưa có bản bền — sổ trống"; cls = ""; }
    else { text = "Đã lưu bền · rev " + P.durableRev; cls = "ok"; }
    chip.textContent = text;
    chip.className = "savechip " + cls;
    btn.disabled = !(P.phase === "ONLINE" && !P.saving && unsaved());

    $("fbBox").innerHTML =
      stat("Trạng thái", phaseLabel(), P.detail ? String(P.detail).slice(0, 90) : "",
        P.phase === "ONLINE" ? "var(--pass)" : (P.phase === "INIT" ? null : "var(--fail)")) +
      stat("Project", P.projectId || "—", "Cloud Firestore · ethdca/state + ethdca/seed") +
      stat("UID thiết bị này", P.uid || "—", "Firebase Anonymous Auth") +
      stat("Bản bền", P.durableRev === null ? "chưa có" : "rev " + P.durableRev,
        (P.lastAck ? "xác nhận " + shortTs(P.lastAck) : "") +
        (seed ? (P.seedDurable ? " · seed bền" : " · seed CHƯA bền") : "")) ;
    renderBanners();
  }

  function persistenceBanners() {
    var b = function (cls, mk, body) {
      return '<div class="banner ' + cls + '"><span class="mk">' + mk + "</span><p>" + body + "</p></div>";
    };
    var out = "";
    if (P.phase === "INIT") {
      out += b("warn", "ĐANG KẾT NỐI NGUỒN BỀN", "Chưa nạp sổ từ Cloud Firestore. Mọi thao tác ghi tạm khoá.");
    } else if (P.phase === "UNCONFIGURED") {
      out += b("bad", "CHƯA CẤU HÌNH FIREBASE",
        "<code>webapp/firebase_config.js</code> còn giá trị <code>REQUIRED</code>. App không có nguồn bền nên " +
        "<strong>không ghi sổ</strong>. Điền cấu hình từ Firebase Console rồi build + deploy lại " +
        "(xem <code>webapp/README.md</code>).");
    } else if (P.phase === "AUTH_FAILED") {
      out += b("bad", "KHÔNG XÁC THỰC ĐƯỢC",
        "Firebase Anonymous Auth thất bại: <code>" + esc(P.detail) + "</code>. Kiểm tra đã bật " +
        "<em>Anonymous</em> trong Authentication → Sign-in method, và mạng tới Firebase. " +
        "<strong>Không ghi sổ.</strong>");
    } else if (P.phase === "UNRECOGNIZED") {
      out += b("bad", "KHÔNG NHẬN DIỆN ĐƯỢC THIẾT BỊ/TRÌNH DUYỆT NÀY",
        "UID hiện tại <code>" + esc(P.uid || "—") + "</code> không được <code>firestore.rules</code> cho phép " +
        "(<code>" + esc(P.detail) + "</code>). Đây <strong>không</strong> phải lỗi mạng và <strong>không</strong> " +
        "phải sổ trống: bản bền (nếu có) vẫn nguyên trên Firestore, chỉ không đọc được từ đây. " +
        "<strong>Không ghi sổ.</strong> Nếu đây là lần thiết lập đầu tiên: chép UID này (tab Thiết lập) vào " +
        "<code>firestore.rules</code> rồi deploy lại rules. Nếu bạn vừa đổi máy/trình duyệt/cửa sổ riêng tư: " +
        "giới hạn V1 (H-23) — dùng <em>Tải về JSON</em> ở máy cũ và <em>Nạp lại từ JSON</em> ở đây.");
    } else if (P.phase === "OFFLINE") {
      out += b("bad", "KHÔNG ĐỌC ĐƯỢC NGUỒN BỀN",
        "Không lấy được sổ từ Cloud Firestore: <code>" + esc(P.detail) + "</code>. " +
        "<strong>Không ghi sổ.</strong> " +
        (P.mirrorShown
          ? "Số liệu đang hiển thị là <strong>bản mirror trên máy, CHƯA xác nhận từ nguồn bền</strong> — chỉ để xem, " +
            "không phải sổ chính thức."
          : "Không có bản mirror nào trên máy để xem tạm.") +
        " Tải lại trang khi có mạng.");
    } else if (P.phase === "CORRUPT") {
      out += b("bad", "NGUỒN BỀN KHÔNG HỢP LỆ",
        "Bản <code>ethdca/state</code> trên Firestore không qua được kiểm tra sổ: " + esc(P.detail) + ". " +
        "App <strong>không</strong> nạp nó làm sổ kế toán và <strong>không ghi đè</strong> — bản đó được giữ nguyên " +
        "để cứu: <em>Tải về JSON</em> ở tab Thiết lập sẽ tải bản thô. <strong>Không ghi sổ.</strong>");
    } else if (P.phase === "ONLINE") {
      if (P.lastError === "stale-durable" && !P.saving) {
        out += b("bad", "NGUỒN BỀN ĐÃ ĐỔI Ở NƠI KHÁC",
          "Firestore đang ở " + (P.staleRev === null ? "trạng thái chưa có bản nào" : "rev " + esc(P.staleRev)) +
          ", không còn là bản trang này đã nạp (rev " + esc(expectedRevLabel()) + ") — một tab hoặc thiết bị khác " +
          "vừa ghi. Thay đổi gần nhất ở đây (rev " + esc(state.rev) + ") <strong>KHÔNG được ghi đè lên</strong> và " +
          "<strong>chưa được lưu bền</strong>. Nếu cần giữ nó: <em>Tải về JSON</em> ngay, rồi tải lại trang để " +
          "lấy bản mới nhất và nhập lại.");
      } else if (P.lastError && !P.saving) {
        out += b("bad", "GHI THẤT BẠI",
          "Thay đổi gần nhất (rev " + esc(state.rev) + ") <strong>chưa được lưu bền</strong>: <code>" +
          esc(P.lastError) + "</code>. Bản trên máy vẫn còn trong trình duyệt này. Bấm <strong>Lưu lại</strong>, " +
          "hoặc <em>Tải về JSON</em> để giữ một bản độc lập.");
      }
      if (P.saving && P.unconfirmed) {
        out += b("warn", "CHƯA XÁC NHẬN",
          "Máy chủ chưa xác nhận bản rev " + esc(state.rev) + " (mất mạng?). Lệnh ghi vẫn đang chờ — " +
          "<strong>đừng đóng trang</strong> cho tới khi hiện \"Đã lưu bền\".");
      }
      if (P.diverged) {
        out += b("warn", "BẢN TRÊN MÁY MỚI HƠN NGUỒN BỀN",
          "localStorage có rev " + esc(P.diverged.rev) + ", Firestore có " +
          (P.durableRev === null ? "chưa có bản nào" : "rev " + esc(P.durableRev)) +
          ". App đang dùng <strong>nguồn bền</strong>; bản trên máy được cất riêng, chưa mất. Bạn chọn: " +
          '<button class="sm" data-pdiv="push">Đẩy bản trên máy lên nguồn bền</button> ' +
          '<button class="sm danger" data-pdiv="drop">Bỏ bản trên máy</button>');
      }
      if (seed && P.seedPending && !P.saving) {
        out += b("warn", "SEED CHƯA BỀN",
          "Lịch sử giá đang dùng lấy từ bộ nhớ trình duyệt, chưa có trên Firestore. Sẽ được ghi cùng lần " +
          "lưu kế tiếp — hoặc bấm <strong>Lưu lại</strong>.");
      }
      if (P.durableRev === null && !state.rev) {
        out += b("warn", "SỔ MỚI",
          "Chưa có bản bền nào trên Firestore cho UID này. Thao tác đầu tiên sẽ tạo. Có dữ liệu cũ? " +
          "<em>Nạp lại từ JSON</em> ở tab Thiết lập.");
      }
    }
    return out;
  }

  /** CHECK-T09B-16: mirror KHÔNG bao giờ âm thầm thắng nguồn bền. Mirror mới hơn được cất riêng
   *  và chờ người dùng chọn tường minh; mirror cũ hơn/bằng bị thay bằng bản bền. */
  function reconcileMirror() {
    var m = readLS(STORE_STATE);
    var stash = readLS(STORE_STASH);
    var base = P.durableRev === null ? 0 : P.durableRev;
    if (m && isNum(m.rev) && m.rev > base && validateState(m).ok) {
      P.diverged = m;
      try { localStorage.setItem(STORE_STASH, JSON.stringify(m)); } catch (e) { /* ignore */ }
    } else if (stash && isNum(stash.rev) && stash.rev > base && validateState(stash).ok) {
      P.diverged = stash;
    } else {
      P.diverged = null;
      try { localStorage.removeItem(STORE_STASH); } catch (e) { /* ignore */ }
    }
    mirror();
  }
  function pushDiverged() {
    if (!P.diverged || !canWrite("dataMsg")) return;
    state = P.diverged;
    P.diverged = null;
    try { localStorage.removeItem(STORE_STASH); } catch (e) { /* ignore */ }
    touch();   // rev của bản đẩy lên > durableRev, và chỉ bền khi máy chủ xác nhận
  }
  function dropDiverged() {
    P.diverged = null;
    try { localStorage.removeItem(STORE_STASH); } catch (e) { /* ignore */ }
    renderPersistence();
  }

  /** OFFLINE: cho xem bản mirror (nếu qua được kiểm tra) nhưng ĐÁNH DẤU chưa xác nhận và khoá ghi. */
  function showMirrorReadOnly() {
    var m = readLS(STORE_STATE);
    if (m && validateState(m).ok) { state = m; P.mirrorShown = true; }
    var s = readLS(STORE_SEED);
    if (validSeed(s)) seed = s;
  }

  async function initPersistence() {
    var c = fbCfg();
    if (!configured(c)) { setPhase("UNCONFIGURED", "firebase_config.js"); return; }
    if (typeof firebase === "undefined" || !firebase.auth || !firebase.firestore) {
      setPhase("OFFLINE", "Firebase SDK không nạp được (mạng bị chặn?)");
      return;
    }
    try {
      firebase.initializeApp({
        apiKey: c.apiKey, authDomain: c.authDomain, projectId: c.projectId, appId: c.appId,
      });
      fb.auth = firebase.auth();
      fb.db = firebase.firestore();
      if (c.emulator) {
        fb.auth.useEmulator(c.emulator.auth, { disableWarnings: true });
        fb.db.useEmulator(c.emulator.firestoreHost, c.emulator.firestorePort);
      }
      P.projectId = c.projectId;
    } catch (e) { setPhase("OFFLINE", errCode(e)); return; }

    try {
      var cred = await fb.auth.signInAnonymously();   // dùng lại session Anonymous đã có, nếu còn
      P.uid = cred.user.uid;
    } catch (e) { setPhase("AUTH_FAILED", errCode(e)); return; }

    var snapState, snapSeed;
    try {
      // `source: "server"`: KHÔNG chấp nhận cache của SDK làm bản bền — offline thì phải lỗi rõ.
      snapState = await fb.db.doc("ethdca/state").get({ source: "server" });
      snapSeed = await fb.db.doc("ethdca/seed").get({ source: "server" });
    } catch (e) {
      var code = errCode(e);
      if (/permission-denied/i.test(code)) { setPhase("UNRECOGNIZED", code); return; }
      showMirrorReadOnly();
      setPhase("OFFLINE", code);
      return;
    }

    if (snapState.exists) {
      var raw = snapState.data();
      var v = validateState(raw);
      if (!v.ok) { P.rawDurable = raw; setPhase("CORRUPT", v.reason); return; }
      state = raw;
      P.durableRev = raw.rev;
    } else {
      state = emptyState();
      P.durableRev = null;
    }
    if (snapSeed.exists && validSeed(snapSeed.data())) {
      seed = snapSeed.data();
      P.seedDurable = true;
      try { localStorage.setItem(STORE_SEED, JSON.stringify(seed)); } catch (e) { /* ignore */ }
    } else {
      // Seed là dữ liệu tham chiếu (tầng 2, không phải tiền): nếu nguồn bền chưa có, dùng bản
      // mirror và ghi lên ở lần lưu kế tiếp. Bản seed bền không hợp lệ (nếu có) bị bỏ qua, không ghi đè
      // cho tới khi người dùng nạp seed mới.
      var ls = readLS(STORE_SEED);
      if (validSeed(ls)) { seed = ls; P.seedPending = true; P.seedGen++; }
    }
    reconcileMirror();
    setPhase("ONLINE", "");
  }

  /* ---------------- wiring ---------------- */

  Array.prototype.forEach.call(document.querySelectorAll("nav.tabs button"), function (b) {
    b.addEventListener("click", function () {
      Array.prototype.forEach.call(document.querySelectorAll("nav.tabs button"), function (x) {
        x.setAttribute("aria-selected", String(x === b));
      });
      Array.prototype.forEach.call(document.querySelectorAll(".panel"), function (p) {
        p.classList.toggle("on", p.id === "tab-" + b.getAttribute("data-tab"));
      });
    });
  });

  $("saveBtn").addEventListener("click", save);
  $("banners").addEventListener("click", function (e) {
    var b = e.target && e.target.closest ? e.target.closest("[data-pdiv]") : null;
    if (!b) return;
    if (b.getAttribute("data-pdiv") === "push") pushDiverged(); else dropDiverged();
  });
  $("fbCopyUid").addEventListener("click", function () {
    if (!P.uid) return msg("fbMsg", "Chưa có UID.", "err");
    var done = function () { msg("fbMsg", "Đã chép UID: " + P.uid, "ok"); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(P.uid).then(done, function () { msg("fbMsg", "UID: " + P.uid, "ok"); });
    } else msg("fbMsg", "UID: " + P.uid, "ok");
  });

  function num(id) {
    var v = parseFloat($(id).value);
    return Number.isFinite(v) ? v : NaN;
  }
  function msg(id, text, cls) {
    $(id).textContent = text;
    $(id).className = "formmsg" + (cls ? " " + cls : "");
  }

  $("pxAdd").addEventListener("click", function () {
    if (!canWrite("pxMsg")) return;
    var d = $("pxDate").value, e = num("pxEth"), b = num("pxBtc"), v = num("pxVol");
    if (!d) return msg("pxMsg", "Chọn ngày.", "err");
    if (!Number.isFinite(e) || e <= 0) return msg("pxMsg", "Giá ETH không hợp lệ.", "err");
    if (!Number.isFinite(b) || b <= 0) return msg("pxMsg", "Giá BTC không hợp lệ.", "err");
    if (!Number.isFinite(v) || v < 0) return msg("pxMsg", "Volume không hợp lệ.", "err");
    if (d > new Date().toISOString().slice(0, 10)) {
      return msg("pxMsg", "Không nhập ngày tương lai — chỉ nến đã đóng.", "err");
    }
    addDay(d, e, b, v);
    msg("pxMsg", "Đã thêm " + d + ".", "ok");
    ["pxEth", "pxBtc", "pxVol"].forEach(function (i) { $(i).value = ""; });
    touch();
  });

  $("cbAdd").addEventListener("click", function () {
    if (!canWrite("cbMsg")) return;
    var mk = $("cbMonth").value, a = num("cbAmt");
    if (!mk) return msg("cbMsg", "Chọn tháng.", "err");
    if (!Number.isFinite(a) || a <= 0) return msg("cbMsg", "Số tiền không hợp lệ.", "err");
    var r = addContribution(mk, a);
    msg("cbMsg", "Base " + vnd(r.base) + " · Smart " + vnd(r.smart) +
      " · Opp " + vnd(r.oppAdded) +
      (r.overflow > 0 ? " (overflow " + vnd(r.overflow) + " sang Smart)" : ""), "ok");
    $("cbAmt").value = "";
    touch();
  });

  $("p2pAdd").addEventListener("click", function () {
    if (!canWrite("p2pMsg")) return;
    var dir = $("p2pDir").value, v = num("p2pVnd"), u = num("p2pUsdt");
    var f = Number.isFinite(num("p2pFee")) ? num("p2pFee") : 0;
    if (!Number.isFinite(v) || v <= 0) return msg("p2pMsg", "VND không hợp lệ.", "err");
    if (!Number.isFinite(u) || u <= 0) return msg("p2pMsg", "USDT không hợp lệ.", "err");
    var r = addP2P(dir, v, u, f);
    if (r.err) return msg("p2pMsg", r.err, "err");
    msg("p2pMsg", "Tỷ giá thực hiện " + vnd(r.rate) + " ₫/USDT.", "ok");
    ["p2pVnd", "p2pUsdt"].forEach(function (i) { $(i).value = ""; });
    touch();
  });

  $("buyAdd").addEventListener("click", function () {
    if (!canWrite("buyMsg")) return;
    var src = $("buySrc").value, u = num("buyUsdt"), p = num("buyPrice");
    var rec = num("buyRec"), f = Number.isFinite(num("buyFee")) ? num("buyFee") : 0;
    var rate = num("buyVndRate");
    if (!Number.isFinite(u) || u <= 0) return msg("buyMsg", "USDT không hợp lệ.", "err");
    if (!Number.isFinite(p) || p <= 0) return msg("buyMsg", "Giá khớp không hợp lệ.", "err");
    var r = addBuy(src, u, p, Number.isFinite(rec) ? rec : null, f,
                   Number.isFinite(rate) ? rate : null, $("buyZone").value || null);
    if (r.err) return msg("buyMsg", r.err, "err");
    msg("buyMsg", "Đã ghi " + nf(r.eth, 6) + " ETH" +
      (Number.isFinite(r.shortfallBps)
        ? " · shortfall " + (r.shortfallBps >= 0 ? "+" : "") + r.shortfallBps.toFixed(0) + " bps"
        : "") + (r.zoneNote ? " · " + r.zoneNote : ""), "ok");
    $("buyZone").value = "";
    ["buyUsdt", "buyPrice", "buyRec"].forEach(function (i) { $(i).value = ""; });
    touch();
  });

  $("ldAdd").addEventListener("click", function () {
    if (!canWrite("ldMsg")) return;
    var t = $("ldType").value;
    var a = num("ldAnchor");
    if (!Number.isFinite(a)) a = view ? view.last.close : NaN;
    var cap = num("ldCap");
    if (!Number.isFinite(a) || a <= 0) return msg("ldMsg", "Anchor không hợp lệ.", "err");
    if (!Number.isFinite(cap) || cap <= 0) return msg("ldMsg", "Vốn không hợp lệ.", "err");
    var r = createLadder(t, a, cap);
    if (r.err) return msg("ldMsg", r.err, "err");
    msg("ldMsg", "Đã tạo ladder " + t + " với spacing " + pct(r.ladder.spacing_pct, 2) + ".", "ok");
    $("ldCap").value = ""; $("ldAnchor").value = "";
    touch();
  });

  function loadSeed(text) {
    if (!canWrite("seedMsg")) return;
    var s;
    try { s = JSON.parse(text); } catch (e) { return msg("seedMsg", "File không phải JSON.", "err"); }
    if (!validSeed(s)) {
      return msg("seedMsg", "Thiếu khoá 'history' — cần file từ `ethdca export-live`.", "err");
    }
    seed = s;
    P.seedPending = true; P.seedDurable = false; P.seedGen++;   // ghi lên ethdca/seed ở touch() dưới
    try { localStorage.setItem(STORE_SEED, JSON.stringify(s)); } catch (e) { /* ignore */ }
    var p = E.checkParity(s);
    msg("seedMsg", "Đã nạp " + s.history.length + " ngày. Đối chiếu engine: " +
      (p.ok ? "khớp (lệch tối đa " + p.worst.toExponential(1) + ")"
            : "LỆCH ở " + p.mismatches.length + " ngày"), p.ok ? "ok" : "err");
    touch();
  }

  var sd = $("seedDrop");
  ["dragenter", "dragover"].forEach(function (ev) {
    sd.addEventListener(ev, function (e) { e.preventDefault(); sd.classList.add("over"); });
  });
  ["dragleave", "drop"].forEach(function (ev) {
    sd.addEventListener(ev, function (e) { e.preventDefault(); sd.classList.remove("over"); });
  });
  sd.addEventListener("drop", function (e) {
    var f = e.dataTransfer && e.dataTransfer.files[0];
    if (f) f.text().then(loadSeed);
  });
  $("seedPick").addEventListener("click", function () { $("seedFile").click(); });
  $("seedFile").addEventListener("change", function (e) {
    var f = e.target.files[0];
    if (f) f.text().then(loadSeed);
  });

  $("expBtn").addEventListener("click", function () {
    // CORRUPT: tải bản durable THÔ để cứu (không phải state trong bộ nhớ, vốn đang rỗng).
    var payload = P.phase === "CORRUPT"
      ? { rawDurable: P.rawDurable, note: "Bản ethdca/state thô không qua kiểm tra: " + P.detail }
      : { state: state, seed: seed };
    var text = JSON.stringify(payload, null, 1);
    try {
      var url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
      var a = document.createElement("a");
      a.href = url;
      a.download = P.phase === "CORRUPT" ? "ethdca-tracker-RAW-DURABLE.json" : "ethdca-tracker.json";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
      msg("dataMsg", "Đã tải về " + a.download + (P.mirrorShown ? " (bản mirror, CHƯA xác nhận từ nguồn bền)." : "."), "ok");
    } catch (e) {
      msg("dataMsg", "Trình duyệt không cho tải — sao chép thủ công từ console.", "err");
      console.log(text);
    }
  });

  $("impBtn").addEventListener("click", function () { $("impFile").click(); });
  $("impFile").addEventListener("change", function (e) {
    var f = e.target.files[0];
    if (!f) return;
    f.text().then(function (t) {
      if (!canWrite("dataMsg")) return;
      var o;
      try { o = JSON.parse(t); } catch (err) { return msg("dataMsg", "JSON không hợp lệ.", "err"); }
      if (!o || !o.state) return msg("dataMsg", "Thiếu khoá 'state'.", "err");
      var v = validateState(o.state);
      if (!v.ok) return msg("dataMsg", "File không qua được kiểm tra sổ: " + v.reason, "err");
      state = o.state;
      // rev không được lùi so với bản bền — nếu không, lần mở sau sẽ coi bản này là cũ hơn.
      state.rev = Math.max(state.rev || 0, P.durableRev === null ? 0 : P.durableRev);
      if (validSeed(o.seed)) {
        seed = o.seed;
        P.seedPending = true; P.seedDurable = false; P.seedGen++;
        try { localStorage.setItem(STORE_SEED, JSON.stringify(seed)); } catch (err) { /* ignore */ }
      }
      msg("dataMsg", "Đã nạp lại dữ liệu — đang ghi lên nguồn bền.", "ok");
      touch();
    });
  });

  $("wipeBtn").addEventListener("click", function () {
    if (!canWrite("dataMsg")) return;
    if (!window.confirm("Xóa toàn bộ giao dịch, ladder và sổ vốn — kể cả bản bền trên Firestore? " +
                        "Không hoàn tác được.")) return;
    var rev = state.rev || 0;
    state = emptyState();
    state.rev = Math.max(rev, P.durableRev === null ? 0 : P.durableRev);
    msg("dataMsg", "Đã xóa dữ liệu — đang ghi lên nguồn bền.", "ok");
    touch();
  });

  // mặc định ngày/tháng = hôm nay
  var today = new Date().toISOString().slice(0, 10);
  $("pxDate").value = today;
  $("pxDate").max = today;
  $("cbMonth").value = today.slice(0, 7);

  // Có mạng trở lại: ghi lại bản đang chờ (vẫn qua transaction có điều kiện rev).
  window.addEventListener("online", function () {
    if (P.phase === "ONLINE" && !P.saving && unsaved() && P.lastError !== "stale-durable") persist();
  });
  // Không đóng trang khi còn lệnh ghi chưa được máy chủ xác nhận — mất tab là mất bản đó.
  window.addEventListener("beforeunload", function (e) {
    if (P.phase === "ONLINE" && (P.saving || unsaved())) { e.preventDefault(); e.returnValue = ""; }
  });

  // Chỉ ĐỌC — cho console/bộ test biết trạng thái persistence mà không đụng state.
  window.ETHDCA_DEBUG = {
    status: function () {
      return {
        phase: P.phase, detail: P.detail, uid: P.uid, projectId: P.projectId,
        rev: state.rev, durableRev: P.durableRev, saving: P.saving, unconfirmed: P.unconfirmed,
        lastError: P.lastError, staleRev: P.staleRev, seedPending: P.seedPending, seedDurable: P.seedDurable,
        diverged: !!P.diverged, mirrorShown: P.mirrorShown, hasSeed: !!seed,
      };
    },
  };

  render();           // khung trống + banner "đang kết nối"; mọi thao tác ghi đang khoá
  initPersistence();  // Firebase init -> Anonymous Auth -> đọc bản bền -> validate -> ONLINE
})();
