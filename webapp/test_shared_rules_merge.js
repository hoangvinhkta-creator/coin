/* T-09B — kiểm chứng merge firestore.rules với rules Content thật (Owner cung cấp 2026-09-02).
 * KHÔNG phải production path (PROJECT/PRODUCTION_PATHS.md §2).
 *
 * `CONTENT_ONLY_RULES` bên dưới là NGUYÊN VĂN rules Content do Owner dán trực tiếp — mốc
 * BEFORE. `firestore.rules` đọc từ đĩa (đã merge khối CoinDCA vào) là mốc AFTER. Test chạy
 * đúng CÙNG một battery probe REST (đọc/ghi thẳng Firestore Rules Emulator từ Node, không
 * qua app, không qua mock) trên CẢ HAI ruleset và so ALLOW/DENY của từng probe Content phải
 * giống hệt nhau — đó là bằng chứng CONTENT_BEHAVIOR_PRESERVED. Sau đó chạy riêng ma trận 12
 * ca của CoinDCA (chỉ có nghĩa trên ruleset đã merge).
 *
 * Không đụng gì của Content ngoài việc ĐỌC nguyên văn rules nó cung cấp; không sửa vulnerability
 * nào lộ ra trong lúc phân tích (báo riêng dưới dạng OBSERVATION, không tự vá).
 */
const http = require('http');
const H = require('./test_firebase_harness.js');

const PROJECT = H.PROJECT;
const AUTH_PORT = 9099, FS_PORT = 8080;
const DOCS = '/v1/projects/' + PROJECT + '/databases/(default)/documents';
const ADMIN = { Authorization: 'Bearer owner' };

let failures = 0, checks = 0;
function assert(cond, label) {
  checks++;
  if (!cond) { failures++; console.log('  ASSERT FAIL:', label); }
  else console.log('  ok:', label);
}

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
function toFs(v) {
  if (v === null || v === undefined) return { nullValue: null };
  if (typeof v === 'boolean') return { booleanValue: v };
  if (typeof v === 'number') return { integerValue: String(v) };
  if (typeof v === 'string') return { stringValue: v };
  const fields = {};
  Object.keys(v).forEach((k) => { fields[k] = toFs(v[k]); });
  return { mapValue: { fields } };
}

/** Ký một anonymous ID token thật qua Auth Emulator — mỗi actor một UID thật, không giả lập. */
async function signUp() {
  const r = await rest('POST', AUTH_PORT,
    '/identitytoolkit.googleapis.com/v1/accounts:signUp?key=fake-api-key',
    { returnSecureToken: true });
  if (r.status !== 200) throw new Error('signUp failed: ' + r.status + ' ' + JSON.stringify(r.body));
  return { uid: r.body.localId, headers: { Authorization: 'Bearer ' + r.body.idToken } };
}
const UNAUTH = {};

let seq = 0;
const fresh = (prefix) => prefix + '_' + (seq++) + '_' + Date.now().toString(36);

async function seedDoc(path, fields) {
  const r = await rest('PATCH', FS_PORT, DOCS + '/' + path, { fields: toFs(fields).mapValue.fields }, ADMIN);
  if (r.status !== 200) throw new Error('seedDoc ' + path + ' failed: ' + r.status + ' ' + JSON.stringify(r.body));
}
async function get(path, actorHeaders) {
  const r = await rest('GET', FS_PORT, DOCS + '/' + path, undefined, actorHeaders);
  return r.status === 200;
}
async function write(path, fields, actorHeaders) {
  const r = await rest('PATCH', FS_PORT, DOCS + '/' + path, { fields: toFs(fields).mapValue.fields }, actorHeaders);
  return r.status === 200;
}
async function del(path, actorHeaders) {
  const r = await rest('DELETE', FS_PORT, DOCS + '/' + path, undefined, actorHeaders);
  return r.status === 200;
}

/* ------------------------------------------------------------------ */
/* Content probe battery — dựng trực tiếp từ ĐÚNG những gì rules Owner cung cấp thể hiện.  */
/* Mỗi case tự chứa: seed (nếu cần) rồi thực hiện đúng MỘT thao tác được rules quyết định.   */
/* ------------------------------------------------------------------ */

function contentCases(actors) {
  const { plain, other, manager, admin } = actors;
  return [
    // ---- users/{uid} ----
    { name: 'users.read.unauth', expect: false, run: async () => {
      const id = fresh('u'); await seedDoc('users/' + id, { role: 'USER' });
      return get('users/' + id, UNAUTH);
    } },
    { name: 'users.read.signedIn', expect: true, run: async () => {
      const id = fresh('u'); await seedDoc('users/' + id, { role: 'USER' });
      return get('users/' + id, plain.headers);
    } },
    { name: 'users.create.self', expect: true, run: async () => {
      const a = await signUp();
      return write('users/' + a.uid, { role: 'USER' }, a.headers);
    } },
    { name: 'users.create.wrongUid', expect: false, run: async () => {
      const a = await signUp();
      return write('users/' + fresh('u'), { role: 'USER' }, a.headers);
    } },
    { name: 'users.create.unauth', expect: false, run: async () => {
      return write('users/' + fresh('u'), { role: 'USER' }, UNAUTH);
    } },
    { name: 'users.update.self.sameRole', expect: true, run: async () => {
      const a = await signUp();
      await seedDoc('users/' + a.uid, { role: 'USER' });
      return write('users/' + a.uid, { role: 'USER', note: 'x' }, a.headers);
    } },
    { name: 'users.update.self.escalateRole', expect: false, run: async () => {
      const a = await signUp();
      await seedDoc('users/' + a.uid, { role: 'USER' });
      return write('users/' + a.uid, { role: 'ADMIN' }, a.headers);
    } },
    { name: 'users.update.admin.any', expect: true, run: async () => {
      const id = fresh('u'); await seedDoc('users/' + id, { role: 'USER' });
      return write('users/' + id, { role: 'MANAGER' }, admin.headers);
    } },
    { name: 'users.update.other.nonAdmin', expect: false, run: async () => {
      const id = fresh('u'); await seedDoc('users/' + id, { role: 'USER' });
      return write('users/' + id, { role: 'USER', note: 'y' }, other.headers);
    } },
    { name: 'users.delete.nonAdmin', expect: false, run: async () => {
      const id = fresh('u'); await seedDoc('users/' + id, { role: 'USER' });
      return del('users/' + id, plain.headers);
    } },
    { name: 'users.delete.admin', expect: true, run: async () => {
      const id = fresh('u'); await seedDoc('users/' + id, { role: 'USER' });
      return del('users/' + id, admin.headers);
    } },

    // ---- contents/{id} ----
    { name: 'contents.read.unauth', expect: false, run: async () => {
      const id = fresh('c'); await seedDoc('contents/' + id, { createdBy: 'x' });
      return get('contents/' + id, UNAUTH);
    } },
    { name: 'contents.read.signedIn', expect: true, run: async () => {
      const id = fresh('c'); await seedDoc('contents/' + id, { createdBy: 'x' });
      return get('contents/' + id, plain.headers);
    } },
    { name: 'contents.create.self', expect: true, run: async () => {
      const a = await signUp();
      return write('contents/' + fresh('c'), { createdBy: a.uid }, a.headers);
    } },
    { name: 'contents.create.wrongCreatedBy', expect: false, run: async () => {
      return write('contents/' + fresh('c'), { createdBy: other.uid }, plain.headers);
    } },
    { name: 'contents.create.unauth', expect: false, run: async () => {
      return write('contents/' + fresh('c'), { createdBy: 'x' }, UNAUTH);
    } },
    { name: 'contents.update.owner', expect: true, run: async () => {
      const a = await signUp(); const id = fresh('c');
      await seedDoc('contents/' + id, { createdBy: a.uid, body: 'v1' });
      return write('contents/' + id, { createdBy: a.uid, body: 'v2' }, a.headers);
    } },
    { name: 'contents.update.nonOwnerNonManager', expect: false, run: async () => {
      const a = await signUp(); const id = fresh('c');
      await seedDoc('contents/' + id, { createdBy: a.uid, body: 'v1' });
      return write('contents/' + id, { createdBy: a.uid, body: 'hacked' }, other.headers);
    } },
    { name: 'contents.update.manager', expect: true, run: async () => {
      const a = await signUp(); const id = fresh('c');
      await seedDoc('contents/' + id, { createdBy: a.uid, body: 'v1' });
      return write('contents/' + id, { createdBy: a.uid, body: 'v2-by-manager' }, manager.headers);
    } },
    { name: 'contents.delete.nonAdmin', expect: false, run: async () => {
      const id = fresh('c'); await seedDoc('contents/' + id, { createdBy: 'x' });
      return del('contents/' + id, plain.headers);
    } },
    { name: 'contents.delete.admin', expect: true, run: async () => {
      const id = fresh('c'); await seedDoc('contents/' + id, { createdBy: 'x' });
      return del('contents/' + id, admin.headers);
    } },

    // ---- contents/{id}/versions/{v} ----
    { name: 'contents.versions.read.unauth', expect: false, run: async () => {
      const cid = fresh('c'); const vid = fresh('v');
      await seedDoc('contents/' + cid + '/versions/' + vid, { body: 'v1' });
      return get('contents/' + cid + '/versions/' + vid, UNAUTH);
    } },
    { name: 'contents.versions.read.signedIn', expect: true, run: async () => {
      const cid = fresh('c'); const vid = fresh('v');
      await seedDoc('contents/' + cid + '/versions/' + vid, { body: 'v1' });
      return get('contents/' + cid + '/versions/' + vid, plain.headers);
    } },
    { name: 'contents.versions.create.signedIn', expect: true, run: async () => {
      const cid = fresh('c'); const vid = fresh('v');
      return write('contents/' + cid + '/versions/' + vid, { body: 'v1' }, plain.headers);
    } },
    { name: 'contents.versions.create.unauth', expect: false, run: async () => {
      const cid = fresh('c'); const vid = fresh('v');
      return write('contents/' + cid + '/versions/' + vid, { body: 'v1' }, UNAUTH);
    } },
    { name: 'contents.versions.update.alwaysDeny', expect: false, run: async () => {
      const cid = fresh('c'); const vid = fresh('v');
      await seedDoc('contents/' + cid + '/versions/' + vid, { body: 'v1' });
      return write('contents/' + cid + '/versions/' + vid, { body: 'v2' }, admin.headers);
    } },
    { name: 'contents.versions.delete.alwaysDeny', expect: false, run: async () => {
      const cid = fresh('c'); const vid = fresh('v');
      await seedDoc('contents/' + cid + '/versions/' + vid, { body: 'v1' });
      return del('contents/' + cid + '/versions/' + vid, admin.headers);
    } },

    // ---- schedules/{id} ----
    { name: 'schedules.read.unauth', expect: false, run: async () => {
      const id = fresh('s'); await seedDoc('schedules/' + id, { at: 1 });
      return get('schedules/' + id, UNAUTH);
    } },
    { name: 'schedules.read.signedIn', expect: true, run: async () => {
      const id = fresh('s'); await seedDoc('schedules/' + id, { at: 1 });
      return get('schedules/' + id, plain.headers);
    } },
    { name: 'schedules.create.unauth', expect: false, run: async () => {
      return write('schedules/' + fresh('s'), { at: 1 }, UNAUTH);
    } },
    { name: 'schedules.create.signedIn', expect: true, run: async () => {
      return write('schedules/' + fresh('s'), { at: 1 }, plain.headers);
    } },
    { name: 'schedules.update.anySignedIn', expect: true, run: async () => {
      const id = fresh('s'); await seedDoc('schedules/' + id, { at: 1 });
      return write('schedules/' + id, { at: 2 }, other.headers);
    } },
    { name: 'schedules.delete.nonManager', expect: false, run: async () => {
      const id = fresh('s'); await seedDoc('schedules/' + id, { at: 1 });
      return del('schedules/' + id, plain.headers);
    } },
    { name: 'schedules.delete.manager', expect: true, run: async () => {
      const id = fresh('s'); await seedDoc('schedules/' + id, { at: 1 });
      return del('schedules/' + id, manager.headers);
    } },

    // ---- groups/{id} ----
    { name: 'groups.read.unauth', expect: false, run: async () => {
      const id = fresh('g'); await seedDoc('groups/' + id, { name: 'x' });
      return get('groups/' + id, UNAUTH);
    } },
    { name: 'groups.read.signedIn', expect: true, run: async () => {
      const id = fresh('g'); await seedDoc('groups/' + id, { name: 'x' });
      return get('groups/' + id, plain.headers);
    } },
    { name: 'groups.write.nonManager', expect: false, run: async () => {
      return write('groups/' + fresh('g'), { name: 'x' }, plain.headers);
    } },
    { name: 'groups.write.manager', expect: true, run: async () => {
      return write('groups/' + fresh('g'), { name: 'x' }, manager.headers);
    } },

    // ---- config/{id} (yêu cầu tối thiểu §7) ----
    { name: 'config.read.unauth', expect: false, run: async () => {
      const id = fresh('cfg'); await seedDoc('config/' + id, { k: 'v' });
      return get('config/' + id, UNAUTH);
    } },
    { name: 'config.read.signedIn', expect: true, run: async () => {
      const id = fresh('cfg'); await seedDoc('config/' + id, { k: 'v' });
      return get('config/' + id, plain.headers);
    } },
    { name: 'config.write.nonManager', expect: false, run: async () => {
      return write('config/' + fresh('cfg'), { k: 'v' }, plain.headers);
    } },
    { name: 'config.write.manager', expect: true, run: async () => {
      return write('config/' + fresh('cfg'), { k: 'v' }, manager.headers);
    } },

    // ---- fb_queue/{id} ----
    { name: 'fb_queue.read.unauth', expect: false, run: async () => {
      const id = fresh('q'); await seedDoc('fb_queue/' + id, { job: 'x' });
      return get('fb_queue/' + id, UNAUTH);
    } },
    { name: 'fb_queue.read.signedIn', expect: true, run: async () => {
      const id = fresh('q'); await seedDoc('fb_queue/' + id, { job: 'x' });
      return get('fb_queue/' + id, plain.headers);
    } },
    { name: 'fb_queue.write.unauth', expect: false, run: async () => {
      return write('fb_queue/' + fresh('q'), { job: 'x' }, UNAUTH);
    } },
    { name: 'fb_queue.write.signedIn', expect: true, run: async () => {
      return write('fb_queue/' + fresh('q'), { job: 'x' }, plain.headers);
    } },

    // ---- audit_logs/{id} (yêu cầu tối thiểu §7) ----
    { name: 'audit_logs.read.nonManager', expect: false, run: async () => {
      const id = fresh('a'); await seedDoc('audit_logs/' + id, { userId: 'x' });
      return get('audit_logs/' + id, plain.headers);
    } },
    { name: 'audit_logs.read.manager', expect: true, run: async () => {
      const id = fresh('a'); await seedDoc('audit_logs/' + id, { userId: 'x' });
      return get('audit_logs/' + id, manager.headers);
    } },
    { name: 'audit_logs.create.self', expect: true, run: async () => {
      const a = await signUp();
      return write('audit_logs/' + fresh('a'), { userId: a.uid }, a.headers);
    } },
    { name: 'audit_logs.create.wrongUserId', expect: false, run: async () => {
      return write('audit_logs/' + fresh('a'), { userId: other.uid }, plain.headers);
    } },
    { name: 'audit_logs.create.unauth', expect: false, run: async () => {
      return write('audit_logs/' + fresh('a'), { userId: 'x' }, UNAUTH);
    } },
    { name: 'audit_logs.update.alwaysDeny', expect: false, run: async () => {
      const id = fresh('a'); await seedDoc('audit_logs/' + id, { userId: 'x' });
      return write('audit_logs/' + id, { userId: 'y' }, admin.headers);
    } },
    { name: 'audit_logs.delete.alwaysDeny', expect: false, run: async () => {
      const id = fresh('a'); await seedDoc('audit_logs/' + id, { userId: 'x' });
      return del('audit_logs/' + id, admin.headers);
    } },
  ];
}

/** Chạy toàn bộ battery, trả về map name -> allowed thật đo được (KHÔNG so với expect ở đây —
 *  so hai lượt BEFORE/AFTER với nhau là phép kiểm chính; so với expect chỉ để chắc test tự nó
 *  không vô nghĩa). */
async function runBattery(actors) {
  const cases = contentCases(actors);
  const out = {};
  for (const c of cases) {
    out[c.name] = { allowed: await c.run(), expect: c.expect };
  }
  return out;
}

/* ------------------------------------------------------------------ */
/* Ma trận CoinDCA (§8, 12 ca) — chỉ chạy trên ruleset đã merge.        */
/* ------------------------------------------------------------------ */
async function coinDcaMatrix(owner, plain) {
  await seedDoc('ethdca/state', { schema: 'ethdca.tracker/1', rev: 1 });
  await seedDoc('ethdca/seed', { schema: 'ethdca.seed/1' });

  assert((await get('ethdca/state', UNAUTH)) === false, '1. no auth -> ethdca/state read -> DENY');
  assert((await get('ethdca/seed', UNAUTH)) === false, '2. no auth -> ethdca/seed read -> DENY');
  assert((await get('ethdca/state', plain.headers)) === false, '3. wrong anon uid -> state read -> DENY');
  assert((await get('ethdca/seed', plain.headers)) === false, '4. wrong anon uid -> seed read -> DENY');
  assert((await get('ethdca/state', owner)) === true, '5. owner uid -> read state -> ALLOW');
  assert((await write('ethdca/state', { schema: 'ethdca.tracker/1', rev: 2 }, owner)) === true,
    '6. owner uid -> write state -> ALLOW');
  assert((await get('ethdca/seed', owner)) === true, '7. owner uid -> read seed -> ALLOW');
  assert((await write('ethdca/seed', { schema: 'ethdca.seed/1', v: 2 }, owner)) === true,
    '8. owner uid -> write seed -> ALLOW');
  assert((await write('ethdca/other', { x: 1 }, owner)) === false,
    '9. unsupported ethdca document (owner uid) -> DENY');
  assert((await del('ethdca/state', owner)) === false, '10. delete state (owner uid) -> DENY (T-09B: no delete)');
  assert((await del('ethdca/seed', owner)) === false, '11. delete seed (owner uid) -> DENY (T-09B: no delete)');

  // 12. CoinDCA owner UID không được vô tình có thêm quyền Content do rule merge: hành vi của
  // owner trên các path Content phải KHỚP ĐÚNG hành vi "signedIn thường" mà chính rules Content
  // đã định nghĩa cho MỌI actor đã xác thực — không hơn, không kém.
  const cfgId = fresh('cfg'); await seedDoc('config/' + cfgId, { k: 'v' });
  const cfgReadAsOwner = await get('config/' + cfgId, owner);
  const cfgReadAsPlain = await get('config/' + cfgId, plain.headers);
  assert(cfgReadAsOwner === true && cfgReadAsOwner === cfgReadAsPlain,
    '12a. owner uid đọc config/* == hành vi signedIn thường của Content (đều ALLOW, chỉ vì signedIn(), không phải quyền mới)');
  const logId = fresh('a'); await seedDoc('audit_logs/' + logId, { userId: 'x' });
  const auditReadAsOwner = await get('audit_logs/' + logId, owner);
  const auditReadAsPlain = await get('audit_logs/' + logId, plain.headers);
  assert(auditReadAsOwner === false && auditReadAsOwner === auditReadAsPlain,
    '12b. owner uid đọc audit_logs/* == hành vi signedIn thường của Content (đều DENY, không có quyền manager)');
  const usrId = fresh('u'); await seedDoc('users/' + usrId, { role: 'USER' });
  const usersReadAsOwner = await get('users/' + usrId, owner);
  const usersReadAsPlain = await get('users/' + usrId, plain.headers);
  assert(usersReadAsOwner === true && usersReadAsOwner === usersReadAsPlain,
    '12c. owner uid đọc users/* == hành vi signedIn thường của Content (đều ALLOW, chỉ vì signedIn())');
}

/* ------------------------------------------------------------------ */

const CONTENT_ONLY_RULES = `rules_version = '2';

// Quy tắc bảo mật cho công cụ Content Zalo Group — Tín Phát
// Nạp bằng: firebase deploy --only firestore:rules
// hoặc dán trực tiếp vào Firebase Console → Firestore → Rules

service cloud.firestore {
  match /databases/{database}/documents {

    function signedIn()  { return request.auth != null; }
    function profile()   { return get(/databases/$(database)/documents/users/$(request.auth.uid)).data; }
    function hasProfile(){ return exists(/databases/$(database)/documents/users/$(request.auth.uid)); }
    function role()      { return hasProfile() ? profile().role : 'USER'; }
    function isManager() { return signedIn() && role() in ['MANAGER', 'ADMIN']; }
    function isAdmin()   { return signedIn() && role() == 'ADMIN'; }
    function isOwner(f)  { return signedIn() && resource.data[f] == request.auth.uid; }

    // Hồ sơ người dùng — ai cũng đọc được để hiển thị tên người phụ trách
    match /users/{uid} {
      allow read:   if signedIn();
      allow create: if signedIn() && request.auth.uid == uid;
      allow update: if isAdmin()
                    || (request.auth.uid == uid && request.resource.data.role == resource.data.role);
      allow delete: if isAdmin();
    }

    // Content — nhân viên sửa bài của mình, quản lý sửa tất cả, không hard-delete
    match /contents/{id} {
      allow read:   if signedIn();
      allow create: if signedIn() && request.resource.data.createdBy == request.auth.uid;
      allow update: if isOwner('createdBy') || isManager();
      allow delete: if isAdmin();

      match /versions/{v} {
        allow read:   if signedIn();
        allow create: if signedIn();
        allow update, delete: if false;   // lịch sử version là bất biến
      }
    }

    // Lịch đăng — nhân viên được đánh dấu đã đăng, chỉ quản lý mới huỷ
    match /schedules/{id} {
      allow read:   if signedIn();
      allow create: if signedIn();
      allow update: if signedIn();
      allow delete: if isManager();
    }

    match /groups/{id} {
      allow read:  if signedIn();
      allow write: if isManager();
    }

    match /config/{id} {
      allow read:  if signedIn();
      allow write: if isManager();
    }

    // Hàng đợi Facebook (tính năng dự phòng)
    match /fb_queue/{id} {
      allow read:  if signedIn();
      allow write: if signedIn();
    }

    // Nhật ký thao tác — ghi được, không sửa được
    match /audit_logs/{id} {
      allow read:   if isManager();
      allow create: if signedIn() && request.resource.data.userId == request.auth.uid;
      allow update, delete: if false;
    }
  }
}
`;

(async () => {
  const stop = await H.ensureEmulators();
  try {
    await H.clearFirestore();
    await H.clearAuth();

    console.log('\n=== Dựng actor thật qua Auth Emulator ===');
    const actors = {
      plain: await signUp(),
      other: await signUp(),
      manager: await signUp(),
      admin: await signUp(),
    };
    await seedDoc('users/' + actors.manager.uid, { role: 'MANAGER' });
    await seedDoc('users/' + actors.admin.uid, { role: 'ADMIN' });
    console.log('  plain=' + actors.plain.uid + ' other=' + actors.other.uid +
      ' manager=' + actors.manager.uid + ' admin=' + actors.admin.uid);

    console.log('\n=== BEFORE — rules Content nguyên văn (Owner cung cấp) ===');
    await H.setRules(null, CONTENT_ONLY_RULES);
    const before = await runBattery(actors);

    console.log('\n=== AFTER — firestore.rules đã merge (Content + CoinDCA) ===');
    // UID owner CoinDCA cho test: một actor thật vừa được Auth Emulator ký, KHÔNG phải chuỗi
    // đoán — thay vào placeholder OWNER_UID_REQUIRED giống hệt bước Owner sẽ làm thật
    // (`bootstrapOwner` trong test_firebase_harness.js dùng đúng cơ chế này).
    const coinDcaOwner = await signUp();
    const mergedForTest = require('fs').readFileSync(H.RULES_PATH, 'utf8')
      .replace(/OWNER_UID_REQUIRED/g, coinDcaOwner.uid);
    await H.setRules(null, mergedForTest);
    const after = await runBattery(actors);

    console.log('\n=== So khớp CONTENT_BEHAVIOR_BEFORE == CONTENT_BEHAVIOR_AFTER ===');
    const names = Object.keys(before);
    let mismatch = 0;
    for (const n of names) {
      const b = before[n], a = after[n];
      const same = b.allowed === a.allowed;
      if (!same) mismatch++;
      assert(same, n + ': BEFORE=' + b.allowed + ' AFTER=' + a.allowed +
        (same ? '' : '  <== ĐỔI HÀNH VI CONTENT, KHÔNG CHẤP NHẬN ĐƯỢC'));
      // đối chiếu luôn với kỳ vọng đọc thẳng từ rules text, để test tự nó không vô nghĩa
      assert(b.allowed === b.expect, n + ' (BEFORE khớp phân tích rules): expect=' + b.expect + ' got=' + b.allowed);
    }
    console.log('  tổng probe Content: ' + names.length + ' | lệch BEFORE/AFTER: ' + mismatch);

    console.log('\n=== Ma trận CoinDCA (12 ca, §8) trên ruleset đã merge ===');
    await coinDcaMatrix(coinDcaOwner.headers, actors.plain);
  } finally {
    await stop();
  }
  console.log('\n=== TỔNG KẾT test_shared_rules_merge ===');
  console.log('assertion đã chạy:', checks, '| FAIL:', failures);
  if (failures > 0) { console.log('SHARED RULES MERGE: FAIL'); process.exit(1); }
  console.log('SHARED RULES MERGE: PASS — CONTENT_BEHAVIOR_PRESERVED = YES, CoinDCA matrix 12/12');
})().catch((e) => { console.error(e); process.exit(1); });
