/* T-09A — helper dùng chung cho các ca kiểm thử kế toán chạy trên app_final.html.
 * KHÔNG phải production path (PROJECT/PRODUCTION_PATHS.md §2).
 *
 * BẢO TRÌ T-09B (2026-09-02): trang nay chạy trên Firebase (Hosting + Anonymous Auth + Cloud
 * Firestore) nên mọi ca kiểm thử đi qua `test_firebase_harness.js`: emulator thật, rules thật,
 * SDK thật. `readState()` KHÔNG còn đọc localStorage làm sự thật — nó chờ máy chủ xác nhận,
 * đọc bản DURABLE từ emulator qua REST (độc lập với SDK trong trang) và đối chiếu bit-exact
 * với bản trong bộ nhớ trang. Nhờ vậy ba bộ test kế toán T-09A chạy nguyên văn trên state
 * ĐÃ ĐI QUA Firebase (CHECK-T09B-09). Kịch bản và assertion kế toán GIỮ NGUYÊN.
 */
const FB = require('./test_firebase_harness.js');

const APP_FINAL = FB.APP_FINAL;
const SEED_PATH = FB.SEED_PATH;
const CHROMIUM = FB.CHROMIUM;

/** Trang mới = Owner mở app lần đầu trên trình duyệt mới (bootstrap rules với UID của trang),
 *  rồi nạp seed (trừ khi opts.seed === false). Trả { ctx, p, errs, uid }. */
async function newPage(b, opts) { return FB.newPage(b, opts); }

/** State đã round-trip qua Firestore, đã đối chiếu với bản trong bộ nhớ (ném lỗi nếu lệch). */
const readState = FB.readState;

/** Oracle độc lập với app_logic.js: tính lại unlock từ CHÍNH engine.js dùng chung, theo đúng
 *  lịch sử app đang thấy (seed + extraDays). Dùng để so hạn mức reserve mà không phải đọc
 *  con số đã làm tròn trên UI, và KHÔNG hard-code số. Đọc bản mirror (JSON của state trong
 *  bộ nhớ) — chỉ để tính oracle, không phải nguồn sự thật. */
const readUnlock = (p) => p.evaluate(() => {
  const seed = JSON.parse(localStorage.getItem('ethdca-tracker-seed-v1'));
  const st = JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')) || {};
  let hist = (seed && seed.history ? seed.history.slice() : []);
  (st.extraDays || []).forEach(d => hist.push(d));
  const map = new Map();
  hist.forEach(r => map.set(r.d, r));
  hist = Array.from(map.values()).sort((a, b) => (a.d < b.d ? -1 : (a.d > b.d ? 1 : 0)));
  const ind = ENGINE.computeIndicators(hist);
  const s = ENGINE.scoreForDay(ind[ind.length - 1], (seed.config || {}).score_weights || [50, 30, 20]);
  return {
    oscore: s.oscore,
    smartUnlock: ENGINE.smartUnlock(s.oscore),
    oppUnlock: ENGINE.opportunityUnlock(s.oscore),
  };
});

/** Đẩy OSCORE lên bằng ĐƯỜNG DÙNG THẬT (tab "Nhập số liệu" -> #pxAdd), không thao túng state.
 *  Chuỗi ngày giảm giá liên tiếp — trạng thái thị trường hoàn toàn dựng được từ nguồn
 *  canonical (seed DEMO trong repo + thao tác UI). Trả về unlock đo lại sau khi nhập. */
async function pushDeclineDays(p, n, startDate) {
  await p.click('[data-tab="entry"]');
  const st0 = await readState(p);
  const seedLast = await p.evaluate(() => {
    const seed = JSON.parse(localStorage.getItem('ethdca-tracker-seed-v1'));
    return seed.history[seed.history.length - 1];
  });
  const extra = (st0 && st0.extraDays) || [];
  const last = extra.length ? extra[extra.length - 1] : seedLast;
  let px = last.e, bt = last.b, vol = last.v;
  const t0 = Date.parse((startDate || last.d) + 'T00:00:00Z') + 86400000;
  for (let i = 0; i < n; i++) {
    const d = new Date(t0 + i * 86400000).toISOString().slice(0, 10);
    px *= 0.97; bt *= 0.995; vol *= 1.02;
    await p.fill('#pxDate', d);
    await p.fill('#pxEth', px.toFixed(6));
    await p.fill('#pxBtc', bt.toFixed(6));
    await p.fill('#pxVol', vol.toFixed(6));
    await p.click('#pxAdd');
    await p.waitForTimeout(40);
  }
  await FB.waitSaved(p);
  return readUnlock(p);
}

async function contribute(p, mk, amount) {
  await p.click('[data-tab="entry"]');
  await p.fill('#cbMonth', mk);
  await p.fill('#cbAmt', String(amount));
  await p.click('#cbAdd');
  await p.waitForTimeout(200);
}

async function makeLadder(p, type, anchor, cap) {
  await p.click('[data-tab="ladder"]');
  await p.waitForTimeout(120);
  await p.selectOption('#ldType', type);
  await p.fill('#ldAnchor', String(anchor));
  await p.fill('#ldCap', String(cap));
  await p.click('#ldAdd');
  await p.waitForTimeout(250);
  const msg = (await p.textContent('#ldMsg')).trim();
  const st = await readState(p);
  return { msg, state: st, ladder: (st.ladders || [])[(st.ladders || []).length - 1] };
}

async function cancelLadder(p, id) {
  await p.click('[data-tab="ladder"]');
  await p.waitForTimeout(120);
  await p.click('[data-cancel="' + id + '"]', { force: true });
  await p.waitForTimeout(250);
}

const poolTotal = (x) => x.a + x.r + x.d;

module.exports = {
  APP_FINAL, SEED_PATH, CHROMIUM,
  newPage, readState, readUnlock, pushDeclineDays,
  contribute, makeLadder, cancelLadder, poolTotal,
  // T-09B: harness Firebase (emulator, REST đối chứng, chờ xác nhận)
  ensureEmulators: FB.ensureEmulators, waitSaved: FB.waitSaved, waitPhase: FB.waitPhase,
  status: FB.status, getDoc: FB.getDoc,
};
