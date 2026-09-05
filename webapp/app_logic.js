/* App logic — persistence + wiring for CoinLedgerUI (CoinDCA L-1).
 * Persistence (T-09B, DEC-019/020/021): nguồn bền duy nhất là Cloud Firestore; localStorage
 * chỉ là mirror/cache — xem khối "persistence" bên dưới. KHÔNG đổi ở T-13 (Step B chỉ tiêu
 * thụ CoinLedger.derive/update/migrate/destructive qua CoinLedgerUI — xem ledger_ui.js).
 * V2.1.5 (OSCORE/ladder/pool/seed-nạp-tay) đã bị gỡ khỏi đường L-1 tại T-13 theo
 * Step-B spec §12 REMOVE_FROM_L1_PATH; `engine.js` giữ nguyên nội dung, không còn được UI này
 * gọi tới (O-11).
 */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var STORE_STATE = "ethdca-tracker-state-v1";
  var STORE_SEED = "ethdca-tracker-seed-v1";
  // Bản mirror MỚI HƠN nguồn bền, cất riêng chờ người dùng chọn (CHECK-T09B-16) — không bao giờ
  // tự trở thành sổ chính thức.
  var STORE_STASH = "ethdca-tracker-state-v1.local-diverged";

  /* ---------------- state ---------------- */

  // T-09B (DEC-020): nguồn sự thật DUY NHẤT của sổ là Cloud Firestore (`ethdca/state`,
  // `ethdca/seed`). Trang khởi động với sổ rỗng và mọi thao tác ghi bị khoá cho tới khi
  // initPersistence() nạp xong bản bền. Trang không còn nhúng state; localStorage/sessionStorage
  // chỉ là mirror/cache và KHÔNG được tự thắng bản bền (CHECK-T09B-16).
  var state = CoinLedger.empty(CoinLedger.clock().today.slice(0, 7));
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

  /* ---------------- formatting (dùng chung cho renderPersistence) ---------------- */

  var esc = function (s) {
    return String(s === null || s === undefined ? "" : s).replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  };
  var shortTs = function (t) { return String(t).slice(0, 16).replace("T", " "); };

  function stat(k, v, s, color) {
    return '<div class="stat"><p class="k">' + esc(k) + '</p><span class="v"' +
      (color ? ' style="color:' + color + '"' : "") + ">" + esc(v) + "</span>" +
      (s ? '<p class="s">' + esc(s) + "</p>" : "") + "</div>";
  }

  /* ---------------- render ---------------- */

  function render() {
    CoinLedgerUI.mount({ state: function () { return state; }, seed: function () { return seed; },
      raw: function () { return P.rawDurable; },
      canWrite: function () { return P.phase === "ONLINE" && !P.saving && !P.diverged; },
      commit: function (next) {
        next = CoinLedger.canonical(next);
        CoinLedger.derive(next.openingPosition, next.plan, next.events, CoinLedger.clock().today);
        next.rev = Math.max(state.rev || 0, P.durableRev || 0);
        state = next; touch();
      }
    });
    renderPersistence(); CoinLedgerUI.render();
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
  function poolTotal(p) { return p.a + p.r + p.d; }
  function isPool(p) {
    return !!p && typeof p === "object" && !Array.isArray(p) &&
      isNum(p.a) && isNum(p.r) && isNum(p.d) && p.a >= -EPS && p.r >= -EPS && p.d >= -EPS;
  }

  /** Kiểm tra một bản durable TRƯỚC khi nó được phép trở thành sổ kế toán (CHECK-T09B-12).
   *  Chỉ kiểm schema + bất biến kế toán đo được trên state đã lưu. KHÔNG sửa, KHÔNG backfill
   *  (`ladders[].month` được phép vắng — historical state giữ nguyên, CHECK-T09B-15).
   *  Nhánh legacy (`ethdca.tracker/1`) được giữ nguyên dù T-13 đã gỡ UI ghi state đó khỏi
   *  đường L-1: một document Firestore cũ vẫn phải nhận diện đúng để luồng migration
   *  (`ledger_ui.js`) chạy được (O-8/O-12 — không đổi ranh giới persistence ở T-13). */
  function validateState(o) {
    if (o && o.schema === CoinLedger.SCHEMA) {
      try { var c = CoinLedger.canonical(o);
        CoinLedger.derive(c.openingPosition, c.plan, c.events, CoinLedger.clock().today);
        return { ok: true }; }
      catch (e) { return { ok: false, reason: e.message }; }
    }
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
    if (P.phase !== "ONLINE" || !fb.db || state.schema !== CoinLedger.SCHEMA) return;
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
      P.lastAck = CoinLedger.clock().instant;
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
    $("banners").innerHTML = persistenceBanners();
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
        "<strong>Không ghi sổ.</strong> Nếu đây là lần thiết lập đầu tiên: chép UID này (mục Cài đặt) vào " +
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
        "để cứu: <em>Tải về JSON</em> ở mục Cài đặt sẽ tải bản thô. <strong>Không ghi sổ.</strong>");
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
          "Lịch sử giá tham chiếu đang dùng lấy từ bộ nhớ trình duyệt, chưa có trên Firestore. Sẽ được ghi cùng " +
          "lần lưu kế tiếp — hoặc bấm <strong>Lưu lại</strong>.");
      }
      if (P.durableRev === null && !state.rev) {
        out += b("warn", "SỔ MỚI",
          "Chưa có bản bền nào trên Firestore cho UID này. Thao tác đầu tiên sẽ tạo. Có dữ liệu cũ? " +
          "<em>Nạp lại từ JSON</em> ở mục Cài đặt.");
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
    if (!P.diverged || !hooksCanWrite()) return;
    if (P.diverged.schema !== CoinLedger.SCHEMA) return;
    P.diverged = CoinLedger.canonical(P.diverged);
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
  function hooksCanWrite() { return P.phase === "ONLINE" && !P.saving && !P.diverged; }

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
      state = raw.schema === CoinLedger.SCHEMA ? CoinLedger.canonical(raw) : raw;
      P.durableRev = raw.rev;
    } else {
      state = CoinLedger.empty(CoinLedger.clock().today.slice(0, 7));
      P.durableRev = null;
    }
    if (snapSeed.exists && validSeed(snapSeed.data())) {
      seed = snapSeed.data();
      P.seedDurable = true;
      try { localStorage.setItem(STORE_SEED, JSON.stringify(seed)); } catch (e) { /* ignore */ }
    } else {
      // Seed là dữ liệu tham chiếu (tầng 2, không phải tiền): nếu nguồn bền chưa có, dùng bản
      // mirror và ghi lên ở lần lưu kế tiếp. Bản seed bền không hợp lệ (nếu có) bị bỏ qua, không ghi đè
      // cho tới khi có seed mới.
      var ls = readLS(STORE_SEED);
      if (validSeed(ls)) { seed = ls; P.seedPending = true; P.seedGen++; }
    }
    reconcileMirror();
    setPhase("ONLINE", "");
  }

  /* ---------------- wiring ---------------- */

  $("saveBtn").addEventListener("click", save);
  $("banners").addEventListener("click", function (e) {
    var b = e.target && e.target.closest ? e.target.closest("[data-pdiv]") : null;
    if (!b) return;
    if (b.getAttribute("data-pdiv") === "push") pushDiverged(); else dropDiverged();
  });
  $("fbCopyUid").addEventListener("click", function () {
    var msgEl = $("fbMsg");
    if (!P.uid) { msgEl.textContent = "Chưa có UID."; msgEl.className = "formmsg err"; return; }
    var done = function () { msgEl.textContent = "Đã chép UID: " + P.uid; msgEl.className = "formmsg ok"; };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(P.uid).then(done, function () { msgEl.textContent = "UID: " + P.uid; msgEl.className = "formmsg ok"; });
    } else { msgEl.textContent = "UID: " + P.uid; msgEl.className = "formmsg ok"; }
  });

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
