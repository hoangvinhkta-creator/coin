/* T-09B — harness kiểm thử persistence Firebase cho app_final.html.
 * KHÔNG phải production path (PROJECT/PRODUCTION_PATHS.md §2).
 *
 * Dựng đúng đường sản phẩm: trang build thật (build_app.js) được phục vụ qua HTTP như Firebase
 * Hosting; Firebase SDK compat THẬT (bản local cùng version với thẻ <script> gstatic trong
 * app_shell.html — môi trường agent chặn gstatic nên harness route URL đó về node_modules);
 * Firebase Auth + Cloud Firestore chạy trên Firebase Emulator Suite với ĐÚNG firestore.rules
 * của repo. Không mock SDK, không mock Firestore.
 *
 * Bằng chứng "phía Firebase" được đọc ĐỘC LẬP với app qua REST API của emulator (Node ->
 * emulator), không qua promise của SDK trong trang.
 */
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const ROOT = path.join(DIR, '..');
const APP_FINAL = path.join(DIR, 'app_final.html');
const SEED_PATH = path.join(ROOT, 'demo', 'results3', 'live_seed.json');
const RULES_PATH = path.join(ROOT, 'firestore.rules');
const CHROMIUM = process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium';
const SDK_VERSION = '12.18.0';   // phải khớp app_shell.html + package.json
const PROJECT = 'demo-ethdca';   // tiền tố demo-: emulator không cần project thật
const AUTH_HOST = '127.0.0.1', AUTH_PORT = 9099;
const FS_HOST = '127.0.0.1', FS_PORT = 8080;
const ACK_TIMEOUT_MS = 4000;

/* ---------------- emulator ---------------- */

function probe(port) {
  return new Promise((res) => {
    const rq = http.get({ host: '127.0.0.1', port, path: '/', timeout: 800 }, (r) => { r.resume(); res(true); });
    rq.on('error', () => res(false));
    rq.on('timeout', () => { rq.destroy(); res(false); });
  });
}

/** Khởi động emulator nếu chưa có ai chạy (ví dụ `firebase emulators:exec`). Trả về hàm dừng. */
async function ensureEmulators() {
  if (await probe(FS_PORT) && await probe(AUTH_PORT)) return async () => {};
  const bin = path.join(DIR, 'node_modules', '.bin', 'firebase');
  const log = fs.openSync(path.join(DIR, 'emulator-test.log'), 'w');
  const child = spawn(bin, ['emulators:start', '--only', 'auth,firestore', '--project', PROJECT],
    { cwd: ROOT, stdio: ['ignore', log, log], detached: true });
  const t0 = Date.now();
  while (Date.now() - t0 < 90000) {
    await new Promise((r) => setTimeout(r, 500));
    if (await probe(FS_PORT) && await probe(AUTH_PORT)) {
      console.log('[harness] emulators up in ' + ((Date.now() - t0) / 1000).toFixed(1) + 's ' +
        '(auth :' + AUTH_PORT + ', firestore :' + FS_PORT + ', rules = firestore.rules)');
      return async () => {
        try { process.kill(-child.pid, 'SIGTERM'); } catch (e) { /* đã dừng */ }
        await new Promise((r) => setTimeout(r, 1500));
        try { process.kill(-child.pid, 'SIGKILL'); } catch (e) { /* đã dừng */ }
      };
    }
    if (child.exitCode !== null) break;
  }
  throw new Error('emulators did not start — xem webapp/emulator-test.log');
}

/* ---------------- REST tới emulator (độc lập với SDK trong trang) ---------------- */

function rest(method, port, p, body, headers) {
  return new Promise((resolve, reject) => {
    const data = body === undefined ? null : JSON.stringify(body);
    const rq = http.request({
      host: '127.0.0.1', port, path: p, method,
      headers: Object.assign({ 'Content-Type': 'application/json' },
        data ? { 'Content-Length': Buffer.byteLength(data) } : {}, headers || {}),
    }, (r) => {
      let out = '';
      r.on('data', (c) => { out += c; });
      r.on('end', () => {
        let json = null;
        try { json = out ? JSON.parse(out) : null; } catch (e) { json = { raw: out }; }
        resolve({ status: r.statusCode, body: json });
      });
    });
    rq.on('error', reject);
    if (data) rq.write(data);
    rq.end();
  });
}
// "Bearer owner": emulator coi là admin (bỏ qua rules) — chỉ cho đọc/ghi đối chứng từ Node.
const ADMIN = { Authorization: 'Bearer owner' };
const DOCS = '/v1/projects/' + PROJECT + '/databases/(default)/documents';

function rulesWithUid(uid) {
  // /g: placeholder xuất hiện cả trong comment hướng dẫn lẫn trong isOwner().
  return fs.readFileSync(RULES_PATH, 'utf8').replace(/OWNER_UID_REQUIRED/g, uid);
}
/** Nạp firestore.rules của repo với owner UID thay vào chỗ OWNER_UID_REQUIRED
 *  (bước Owner làm bằng `firebase deploy --only firestore:rules`). */
async function setRules(uid, override) {
  const content = override !== undefined ? override : rulesWithUid(uid);
  const r = await rest('PUT', FS_PORT, '/emulator/v1/projects/' + PROJECT + ':securityRules',
    { rules: { files: [{ name: 'firestore.rules', content }] } });
  if (r.status !== 200) throw new Error('setRules failed: ' + r.status + ' ' + JSON.stringify(r.body));
  await new Promise((r2) => setTimeout(r2, 150));
}
async function clearFirestore() {
  const r = await rest('DELETE', FS_PORT, '/emulator/v1/projects/' + PROJECT + '/databases/(default)/documents');
  if (r.status !== 200) throw new Error('clearFirestore failed: ' + r.status);
}
async function clearAuth() {
  const r = await rest('DELETE', AUTH_PORT, '/emulator/v1/projects/' + PROJECT + '/accounts');
  if (r.status !== 200) throw new Error('clearAuth failed: ' + r.status);
}

function toFs(v) {
  if (v === null || v === undefined) return { nullValue: null };
  if (typeof v === 'boolean') return { booleanValue: v };
  if (typeof v === 'number') {
    return Number.isSafeInteger(v) && !Object.is(v, -0) ? { integerValue: String(v) } : { doubleValue: v };
  }
  if (typeof v === 'string') return { stringValue: v };
  if (Array.isArray(v)) return { arrayValue: { values: v.map(toFs) } };
  const fields = {};
  Object.keys(v).forEach((k) => { fields[k] = toFs(v[k]); });
  return { mapValue: { fields } };
}
function fromFs(v) {
  if ('nullValue' in v) return null;
  if ('booleanValue' in v) return v.booleanValue;
  if ('integerValue' in v) return Number(v.integerValue);
  if ('doubleValue' in v) return typeof v.doubleValue === 'string' ? Number(v.doubleValue) : v.doubleValue;
  if ('stringValue' in v) return v.stringValue;
  if ('arrayValue' in v) return (v.arrayValue.values || []).map(fromFs);
  if ('mapValue' in v) {
    const o = {};
    Object.keys(v.mapValue.fields || {}).forEach((k) => { o[k] = fromFs(v.mapValue.fields[k]); });
    return o;
  }
  throw new Error('unknown Firestore value ' + JSON.stringify(v));
}
/** Đọc document `ethdca/<name>` thẳng từ emulator (Node, admin) — null nếu chưa tồn tại. */
async function getDoc(name) {
  const r = await rest('GET', FS_PORT, DOCS + '/ethdca/' + name, undefined, ADMIN);
  if (r.status === 404) return null;
  if (r.status !== 200) throw new Error('getDoc ' + name + ': ' + r.status + ' ' + JSON.stringify(r.body));
  return fromFs({ mapValue: { fields: r.body.fields || {} } });
}
/** Ghi document thô (dựng ca corrupt/historical) — ghi đè toàn bộ. */
async function putDoc(name, obj) {
  const r = await rest('PATCH', FS_PORT, DOCS + '/ethdca/' + name, { fields: toFs(obj).mapValue.fields }, ADMIN);
  if (r.status !== 200) throw new Error('putDoc ' + name + ': ' + r.status + ' ' + JSON.stringify(r.body));
}

/* ---------------- so sánh ---------------- */

/** Chuẩn hoá thứ tự khoá (Firestore trả map theo thứ tự riêng) — KHÔNG đổi giá trị. */
function canon(v) {
  if (Array.isArray(v)) return v.map(canon);
  if (v && typeof v === 'object') {
    const o = {};
    Object.keys(v).sort().forEach((k) => { o[k] = canon(v[k]); });
    return o;
  }
  return v;
}
const canonJSON = (v) => JSON.stringify(canon(v));
/** So từng giá trị, bit-exact cho số (===, không dung sai). Trả về danh sách lệch. */
function diff(a, b, pathStr, out) {
  out = out || []; pathStr = pathStr || '$';
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) { out.push(pathStr + ': array mismatch'); return out; }
    a.forEach((x, i) => diff(x, b[i], pathStr + '[' + i + ']', out));
    return out;
  }
  if (a && typeof a === 'object' && b && typeof b === 'object') {
    const keys = new Set(Object.keys(a).concat(Object.keys(b)));
    keys.forEach((k) => {
      if (!(k in a)) out.push(pathStr + '.' + k + ': missing on left');
      else if (!(k in b)) out.push(pathStr + '.' + k + ': missing on right');
      else diff(a[k], b[k], pathStr + '.' + k, out);
    });
    return out;
  }
  if (!Object.is(a, b) && !(a === null && b === null)) out.push(pathStr + ': ' + JSON.stringify(a) + ' !== ' + JSON.stringify(b));
  return out;
}

/* ---------------- HTTP server phục vụ trang (như Firebase Hosting) ---------------- */

let server = null, baseUrl = null;
function startServer() {
  if (baseUrl) return Promise.resolve(baseUrl);
  return new Promise((resolve) => {
    server = http.createServer((req, res) => {
      if (req.url.split('?')[0] === '/' || req.url.startsWith('/index.html')) {
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-cache' });
        res.end(fs.readFileSync(APP_FINAL));
      } else { res.writeHead(404); res.end(); }
    });
    server.unref();   // không giữ tiến trình test sống chỉ vì server còn mở
    server.listen(0, '127.0.0.1', () => {
      baseUrl = 'http://127.0.0.1:' + server.address().port + '/';
      resolve(baseUrl);
    });
  });
}
function stopServer() { if (server) server.close(); server = null; baseUrl = null; }

/* ---------------- browser context ---------------- */

const SDK_FILES = {
  'firebase-app-compat.js': 'firebase-app-compat.js',
  'firebase-auth-compat.js': 'firebase-auth-compat.js',
  'firebase-firestore-compat.js': 'firebase-firestore-compat.js',
};
/** Thẻ <script src="https://www.gstatic.com/firebasejs/<ver>/..."> trong app_shell.html được
 *  trả bằng đúng file cùng version từ node_modules/firebase (mạng agent chặn gstatic). */
async function routeSdk(ctx) {
  // Google Fonts bị proxy của môi trường agent chặn; nếu để trình duyệt tự chờ, mỗi lần nạp
  // trang mất ~12s (stylesheet chặn render). Abort ngay — không liên quan gì tới persistence.
  await ctx.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
  await ctx.route(/^https:\/\/www\.gstatic\.com\/firebasejs\//, (route) => {
    const url = route.request().url();
    const m = url.match(/firebasejs\/([^/]+)\/([^/?]+)/);
    if (!m || m[1] !== SDK_VERSION || !SDK_FILES[m[2]]) return route.abort();
    route.fulfill({
      status: 200, contentType: 'application/javascript',
      body: fs.readFileSync(path.join(DIR, 'node_modules', 'firebase', SDK_FILES[m[2]])),
    });
  });
}
function emulatorConfig(extra) {
  return Object.assign({
    apiKey: 'demo-api-key', authDomain: PROJECT + '.firebaseapp.com', projectId: PROJECT, appId: 'demo-app',
    ackTimeoutMs: ACK_TIMEOUT_MS,
    emulator: { auth: 'http://' + AUTH_HOST + ':' + AUTH_PORT, firestoreHost: FS_HOST, firestorePort: FS_PORT },
  }, extra || {});
}
async function prepareContext(ctx, cfg) {
  await routeSdk(ctx);
  // Đặt TRƯỚC khi firebase_config.js chạy: file đó giữ giá trị đã có (`|| {...}`).
  await ctx.addInitScript('window.ETHDCA_FIREBASE_CONFIG = ' + JSON.stringify(cfg || emulatorConfig()) + ';');
}
function attachErrors(p) {
  const errs = [];
  p.on('dialog', (d) => d.accept());   // beforeunload/confirm: chấp nhận để test không treo
  p.on('pageerror', (e) => errs.push('PAGEERROR: ' + e.message));
  p.on('console', (m) => {
    if (m.type() === 'error' && !/ERR_CONNECTION|font|403|net::/i.test(m.text())) errs.push(m.text());
  });
  return errs;
}

const status = (p) => p.evaluate(() => window.ETHDCA_DEBUG.status());
async function waitPhase(p, phases, timeout) {
  const want = Array.isArray(phases) ? phases : [phases];
  const t0 = Date.now();
  for (;;) {
    const st = await status(p);
    if (want.indexOf(st.phase) !== -1) return st;
    if (Date.now() - t0 > (timeout || 20000)) throw new Error('waitPhase ' + want + ' timeout; now ' + JSON.stringify(st));
    await p.waitForTimeout(100);
  }
}
/** Chờ tới khi máy chủ đã xác nhận bản rev hiện tại (chip "Đã lưu bền"). */
async function waitSaved(p, timeout) {
  const t0 = Date.now();
  for (;;) {
    const st = await status(p);
    if (st.phase === 'ONLINE' && !st.saving && st.durableRev === st.rev && !st.seedPending) return st;
    if (Date.now() - t0 > (timeout || 20000)) throw new Error('waitSaved timeout; now ' + JSON.stringify(st));
    await p.waitForTimeout(80);
  }
}

/** Lần mở đầu tiên với rules còn OWNER_UID_REQUIRED -> app báo KHÔNG NHẬN DIỆN; lấy UID app
 *  hiện, nạp rules với UID đó (bước Owner deploy rules), tải lại -> ONLINE. Đây chính là
 *  chuỗi thiết lập thật của chủ dự án. */
async function bootstrapOwner(p) {
  const st = await waitPhase(p, ['UNRECOGNIZED', 'ONLINE']);
  if (st.phase === 'ONLINE') return st.uid;
  await setRules(st.uid);
  await p.reload();
  await waitPhase(p, 'ONLINE');
  return st.uid;
}

/** Trang mới trên context mới (IndexedDB mới => Anonymous UID mới), emulator được dọn sạch:
 *  đúng kịch bản "Owner mở app lần đầu". opts.seed=false: không nạp seed.
 *  opts.bootstrap=false: dừng ở lần mở đầu (rules placeholder) — để kiểm CHECK-T09B-11. */
async function newPage(b, opts) {
  opts = opts || {};
  if (opts.fresh !== false) {
    await clearFirestore();
    await clearAuth();
    await setRules('OWNER_UID_REQUIRED');
  }
  await startServer();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 1000 } });
  await prepareContext(ctx, opts.config);
  const p = await ctx.newPage();
  const errs = attachErrors(p);
  await p.goto(baseUrl);
  let uid = null;
  if (opts.bootstrap !== false) {
    uid = await bootstrapOwner(p);
    if (opts.seed !== false) {
      await p.setInputFiles('#seedFile', SEED_PATH);
      await waitSaved(p);
    }
  }
  return { ctx, p, errs, uid };
}

/** Context BỀN (user-data-dir trên đĩa): đóng và mở lại giữ nguyên IndexedDB (Anonymous session)
 *  và localStorage — kịch bản CHECK-T09B-04 (same-browser-profile). */
async function newPersistent(chromium, userDataDir, opts) {
  opts = opts || {};
  await startServer();
  const ctx = await chromium.launchPersistentContext(userDataDir, {
    executablePath: CHROMIUM, viewport: { width: 1200, height: 1000 },
    ...(opts.offline ? { offline: true } : {}),
  });
  await prepareContext(ctx, opts.config);
  const p = ctx.pages()[0] || await ctx.newPage();
  const errs = attachErrors(p);
  await p.goto(baseUrl);
  return { ctx, p, errs };
}

/** State đã đi qua Firebase: đọc bản DURABLE từ emulator (Node, độc lập với SDK trong trang)
 *  sau khi máy chủ đã xác nhận, và ĐỐI CHIẾU bit-exact với bản mirror JSON của state trong bộ
 *  nhớ trang. Lệch một giá trị bất kỳ => ném lỗi (DATA_INTEGRITY). Đây là cơ chế biến ba test
 *  kế toán T-09A thành phép kiểm trên state đã round-trip (CHECK-T09B-09). */
async function readState(p) {
  await waitSaved(p);
  const durable = await getDoc('state');
  const mem = await p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));
  if (durable === null && mem === null) return null;
  const d = diff(canon(durable), canon(mem));
  if (d.length) throw new Error('DURABLE != IN-MEMORY state (' + d.length + ' lệch):\n  ' + d.slice(0, 10).join('\n  '));
  return durable;
}

module.exports = {
  APP_FINAL, SEED_PATH, RULES_PATH, CHROMIUM, PROJECT, SDK_VERSION, ACK_TIMEOUT_MS,
  ensureEmulators, setRules, rulesWithUid, clearFirestore, clearAuth, getDoc, putDoc,
  canon, canonJSON, diff, startServer, stopServer, baseUrl: () => baseUrl,
  prepareContext, emulatorConfig, attachErrors, status, waitPhase, waitSaved, bootstrapOwner,
  newPage, newPersistent, readState,
};
