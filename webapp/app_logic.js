/* App logic — state, accounting, render, persistence.
 * Accounting theo Strategy §8: TOTAL = AVAILABLE + RESERVED + DEPLOYED, không âm,
 * không double reservation. Mọi dịch chuyển ghi vào ledger (Data Model §6).
 */
(function () {
  "use strict";

  var E = ENGINE;
  var $ = function (id) { return document.getElementById(id); };
  var STORE_STATE = "ethdca-tracker-state-v1";
  var STORE_SEED = "ethdca-tracker-seed-v1";

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

  function readJSON(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    var t = (el.textContent || "").trim();
    if (!t || t === "null") return null;
    try { return JSON.parse(t); } catch (e) { return null; }
  }

  var state = readJSON("app-state") || emptyState();
  var seed = readJSON("app-seed");
  var dirty = false;
  var canPublish = false;

  // localStorage mirror thắng nếu mới hơn (bảo vệ khi publish thất bại)
  try {
    var ls = localStorage.getItem(STORE_STATE);
    if (ls) {
      var cand = JSON.parse(ls);
      if (cand && typeof cand.rev === "number" && cand.rev > (state.rev || 0)) {
        state = cand;
        dirty = true;
      }
    }
    if (!seed) {
      var lsSeed = localStorage.getItem(STORE_SEED);
      if (lsSeed) seed = JSON.parse(lsSeed);
    }
  } catch (e) { /* private mode */ }

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

  function poolFor(src) {
    var m = month(currentMonth());
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

    var pool = poolFor(ref ? ref.L.type : src);
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

  function reserveFor(type, vnd) {
    var mk = currentMonth(), m = month(mk);
    if (type === "SMART") {
      if (vnd > m.smart.a + 1e-6) return false;
      m.smart.a -= vnd; m.smart.r += vnd; return true;
    }
    if (vnd > state.oppFund.a + 1e-6) return false;
    state.oppFund.a -= vnd; state.oppFund.r += vnd; return true;
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
    var mk = currentMonth(), m = month(mk);
    if (L.type === "SMART") {
      var take = Math.min(open, m.smart.r);
      m.smart.r -= take; m.smart.a += take;
    } else {
      var t2 = Math.min(open, state.oppFund.r);
      state.oppFund.r -= t2; state.oppFund.a += t2;
    }
    ledger({ pool: L.type, type: "RELEASE", vnd: open, reason: "LADDER_RELEASE" });
  }

  function createLadder(type, anchor, capVnd) {
    if (!view) return { err: "Chưa có dữ liệu giá — nạp seed ở tab Thiết lập." };
    var sp = type === "SMART" ? view.smartSpacing : view.oppSpacing;
    if (!Number.isFinite(sp)) return { err: "Chưa đủ lịch sử để tính ADR30." };
    if (!reserveFor(type, capVnd)) return { err: "Không đủ vốn available trong pool." };
    var L = E.buildLadder(type, anchor, sp, capVnd, view.score.oscore);
    L.id = "L" + (state.ladders.length + 1) + "-" + Date.now().toString(36);
    L.created = new Date().toISOString();
    state.ladders.push(L);
    ledger({ pool: type, type: "RESERVE", vnd: capVnd, reason: type + "_LADDER" });
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
    renderBanners();
    renderDash();
    renderLadder();
    renderZonePicker();
    renderHistory();
    renderSetup();
    $("saveChip").textContent = dirty ? "Chưa lưu" : "Đã lưu";
    $("saveChip").className = "savechip " + (dirty ? "dirty" : "ok");
    $("saveBtn").disabled = !dirty;
    $("foot").textContent = "ETH DCA OS " + ((seed && seed.strategy_version) || "V2.1.5") +
      " · rev " + (state.rev || 0) +
      (seed ? " · seed " + (seed.dataset_hash || "").slice(0, 10) : " · chưa có seed");
  }

  function renderBanners() {
    var out = "";
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

  /* ---------------- persistence ---------------- */

  function touch() {
    state.rev = (state.rev || 0) + 1;
    dirty = true;
    try { localStorage.setItem(STORE_STATE, JSON.stringify(state)); } catch (e) { /* ignore */ }
    render();
  }

  /** atob chỉ xử lý latin1; template có tiếng Việt nên phải giải mã qua UTF-8. */
  function b64ToStr(b64) {
    var bin = atob(b64);
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder("utf-8").decode(bytes);
  }

  /** Dựng lại tài liệu đầy đủ để tự publish.
   *  Trang mang theo base64 của chính template nó; ta giải mã, chèn lại đúng blob đó
   *  (để lần lưu sau vẫn dùng được) rồi nhét state/seed hiện tại vào.
   *  Dùng hàm thay thế để chuỗi JSON chứa "$&" không bị hiểu là pattern. */
  function pageHTML() {
    var el = document.getElementById("page-template");
    var b64 = el && el.textContent ? el.textContent.trim() : "";
    if (!b64) return null;
    var tpl;
    try { tpl = b64ToStr(b64); } catch (e) { return null; }
    var safe = function (o) {
      return JSON.stringify(o === undefined ? null : o).replace(/<\//g, "<\\/");
    };
    return tpl
      .replace("__TEMPLATE__", function () { return b64; })
      .replace("__STATE__", function () { return safe(state); })
      .replace("__SEED__", function () { return safe(seed); });
  }

  async function save() {
    var btn = $("saveBtn");
    btn.disabled = true;
    var chip = $("saveChip");
    chip.textContent = "Đang lưu…";
    chip.className = "savechip";
    try {
      var artifact = canPublish ? await window.claude.use("artifact") : null;
      if (!artifact) {
        chip.textContent = "Chỉ lưu trên máy";
        chip.className = "savechip dirty";
        btn.disabled = false;
        return;
      }
      var html = pageHTML();
      if (!html) throw new Error("no template");
      try { sessionStorage.setItem(STORE_STATE, JSON.stringify(state)); } catch (e) { /* ignore */ }
      await artifact.publish(html);
      dirty = false;
      chip.textContent = "Đã lưu";
      chip.className = "savechip ok";
    } catch (err) {
      var code = err && err.code;
      if (code === "conflict") {
        chip.textContent = "Có bản mới hơn — trang đang tải lại";
      } else if (code === "not_writer" || code === "not_granted" || code === "not_declared") {
        chip.textContent = "Chỉ xem — lưu trên máy";
        canPublish = false;
      } else {
        chip.textContent = "Lưu thất bại — dữ liệu vẫn ở máy";
      }
      chip.className = "savechip dirty";
      btn.disabled = false;
    }
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

  function num(id) {
    var v = parseFloat($(id).value);
    return Number.isFinite(v) ? v : NaN;
  }
  function msg(id, text, cls) {
    $(id).textContent = text;
    $(id).className = "formmsg" + (cls ? " " + cls : "");
  }

  $("pxAdd").addEventListener("click", function () {
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
    var s;
    try { s = JSON.parse(text); } catch (e) { return msg("seedMsg", "File không phải JSON.", "err"); }
    if (!s || !s.history || !s.history.length) {
      return msg("seedMsg", "Thiếu khoá 'history' — cần file từ `ethdca export-live`.", "err");
    }
    seed = s;
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

  $("expBtn").addEventListener("click", async function () {
    var blob = JSON.stringify({ state: state, seed: seed }, null, 1);
    var dl = null;
    try { dl = await window.claude.use("downloads"); } catch (e) { dl = null; }
    if (dl) {
      try {
        await dl.save({ filename: "ethdca-tracker.json", data: blob });
        return msg("dataMsg", "Đã tải về.", "ok");
      } catch (e) { /* rơi xuống nhánh dưới */ }
    }
    msg("dataMsg", "Trình duyệt không cho tải — sao chép thủ công từ console.", "err");
    console.log(blob);
  });

  $("impBtn").addEventListener("click", function () { $("impFile").click(); });
  $("impFile").addEventListener("change", function (e) {
    var f = e.target.files[0];
    if (!f) return;
    f.text().then(function (t) {
      var o;
      try { o = JSON.parse(t); } catch (err) { return msg("dataMsg", "JSON không hợp lệ.", "err"); }
      if (!o || !o.state) return msg("dataMsg", "Thiếu khoá 'state'.", "err");
      state = o.state;
      if (o.seed) seed = o.seed;
      msg("dataMsg", "Đã nạp lại dữ liệu.", "ok");
      touch();
    });
  });

  $("wipeBtn").addEventListener("click", function () {
    if (!window.confirm("Xóa toàn bộ giao dịch, ladder và sổ vốn? Không hoàn tác được.")) return;
    state = emptyState();
    try { localStorage.removeItem(STORE_STATE); } catch (e) { /* ignore */ }
    msg("dataMsg", "Đã xóa dữ liệu.", "ok");
    touch();
  });

  // mặc định ngày/tháng = hôm nay
  var today = new Date().toISOString().slice(0, 10);
  $("pxDate").value = today;
  $("pxDate").max = today;
  $("cbMonth").value = today.slice(0, 7);

  render();

  (async function () {
    try {
      var a = await window.claude.use("artifact");
      canPublish = !!a;
    } catch (e) { canPublish = false; }
    if (!canPublish) {
      $("saveBtn").title = "Không lưu lên đám mây được — dữ liệu vẫn giữ trong trình duyệt";
    }
  })();
})();
