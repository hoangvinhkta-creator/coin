/* T-14 bước C — CHECK-T14-02 (rules giữ nguyên shape) + CHECK-T14-03 (ma trận danh tính 5 kịch
 * bản) + C-AS-01…C-AS-04, C-AS-13.
 * KHÔNG phải production path (PROJECT/PRODUCTION_PATHS.md §2). Dữ liệu tổng hợp.
 *
 * Hai tầng bằng chứng, không tầng nào thay được tầng kia:
 *   A. TĨNH — diff `firestore.rules` chỉ chạm khối COINDCA: phần header và TOÀN BỘ khối Content
 *      phải trùng ĐÚNG TỪNG BYTE với bản trước T-14 (khoá bằng SHA-256 ghi ngay trong file này);
 *      các dòng THI HÀNH của khối COINDCA phải trùng đúng danh sách dưới đây (chỉ comment được
 *      phép đổi); không có `delete` ở bất kỳ đâu trong khối COINDCA.
 *   B. ĐỘNG — Firestore Rules Emulator chạy ĐÚNG `firestore.rules` của repo, với danh tính THẬT
 *      do Auth Emulator ký (federated google.com cho Owner và cho một tài khoản Google khác,
 *      anonymous cho ca ẩn danh). Không mock rules, không mock token.
 * Regression hành vi Content (C-AS-04) = chạy lại nguyên văn `test_shared_rules_merge.js`
 * (baseline DEC-023) như một tiến trình con và đòi exit 0.
 */
const { spawn } = require('child_process');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const H = require('./test_firebase_harness.js');

const RULES = fs.readFileSync(H.RULES_PATH, 'utf8');
const CONTENT_MARK = '    // ==================== CONTENT';
const COINDCA_MARK = '    // ==================== COINDCA';
// Băm của bản TRƯỚC T-14 (origin/main 97434d0). Đổi một byte nào ngoài khối COINDCA => FAIL.
const HEADER_SHA = '3e93d6a1e4a00c879cba1004434e90f099b9038d5dd607505f52ead13c3d2f2a';
const CONTENT_SHA = 'ea0489ca598c5fb4733eec91c9ec452347a1d15aeb39b732b921869f665a4ffb';
const COINDCA_EXEC = [
  '    function isCoinDcaOwner() {',
  '      return request.auth != null && request.auth.uid == "OWNER_UID_REQUIRED";',
  '    }',
  '    match /ethdca/state {',
  '      allow read, create, update: if isCoinDcaOwner();',
  '    }',
  '    match /ethdca/seed {',
  '      allow read, create, update: if isCoinDcaOwner();',
  '    }',
  '  }',
  '}',
];

let checks = 0, failures = 0;
function assert(cond, label) {
  checks++;
  if (!cond) { failures++; console.log('  ASSERT FAIL:', label); } else console.log('  ok:', label);
}
const sha = (s) => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
const exec = (s) => s.split('\n').map((l) => l.replace(/\s+$/, '')).filter((l) => l.trim() && !l.trim().startsWith('//'));

/* ---------------- A. Tĩnh ---------------- */
function staticChecks() {
  console.log('\n=== CHECK-T14-02 — firestore.rules: chỉ khối COINDCA bị chạm, shape không đổi ===');
  const i = RULES.indexOf(CONTENT_MARK), j = RULES.indexOf(COINDCA_MARK);
  assert(i > 0 && j > i, 'tìm thấy cả hai mốc khối CONTENT và COINDCA');
  assert(sha(RULES.slice(0, i)) === HEADER_SHA, 'header trước khối Content trùng từng byte với bản trước T-14');
  assert(sha(RULES.slice(i, j)) === CONTENT_SHA, 'TOÀN BỘ khối Content trùng từng byte với bản trước T-14 (không đổi một ký tự)');
  const coin = RULES.slice(j);
  // Mọi khẳng định về HÀNH VI chỉ đo trên dòng thi hành — comment tài liệu không được tính.
  const coinExec = exec(coin).join('\n');
  assert(JSON.stringify(exec(coin)) === JSON.stringify(COINDCA_EXEC), 'dòng THI HÀNH của khối COINDCA không đổi (chỉ comment đổi)');
  assert(!/allow[^\n]*\bdelete\b/.test(coinExec), 'khối COINDCA không có rule `delete` nào');
  assert((coinExec.match(/request\.auth\.uid\s*==/g) || []).length === 1, 'đúng MỘT biểu thức so sánh UID duy nhất (không role, không bảng hồ sơ)');
  assert(!/\bget\(|\bexists\(/.test(coinExec), 'khối COINDCA không đọc document nào khác để quyết định quyền');
  assert(!/signedIn\(\)/.test(coinExec), '"đã đăng nhập" KHÔNG được dùng làm điều kiện của CoinDCA (Step-C spec §6)');
}

/* ---------------- B. Động ---------------- */
const rest = H.rest;
function toFs(v) {
  if (v === null || v === undefined) return { nullValue: null };
  if (typeof v === 'boolean') return { booleanValue: v };
  if (typeof v === 'number') return { integerValue: String(v) };
  if (typeof v === 'string') return { stringValue: v };
  const fields = {};
  Object.keys(v).forEach((k) => { fields[k] = toFs(v[k]); });
  return { mapValue: { fields } };
}
const get = async (p, h) => (await rest('GET', H.FS_PORT, H.DOCS + '/' + p, undefined, h)).status === 200;
const write = async (p, f, h) => (await rest('PATCH', H.FS_PORT, H.DOCS + '/' + p, { fields: toFs(f).mapValue.fields }, h)).status === 200;
const del = async (p, h) => (await rest('DELETE', H.FS_PORT, H.DOCS + '/' + p, undefined, h)).status === 200;
const seed = async (p, f) => { await rest('PATCH', H.FS_PORT, H.DOCS + '/' + p, { fields: toFs(f).mapValue.fields }, H.ADMIN); };

const CONTENT_PROBES = [
  ['users/{x}', 'read'], ['contents/{x}', 'read'], ['schedules/{x}', 'read'],
  ['groups/{x}', 'read'], ['config/{x}', 'read'], ['fb_queue/{x}', 'read'], ['audit_logs/{x}', 'read'],
  ['users/{x}', 'write'], ['contents/{x}', 'write'], ['schedules/{x}', 'write'],
  ['groups/{x}', 'write'], ['config/{x}', 'write'], ['fb_queue/{x}', 'write'], ['audit_logs/{x}', 'write'],
];
let n = 0;
async function contentProfile(actor) {
  const out = {};
  for (const [tpl, op] of CONTENT_PROBES) {
    const id = 'p' + (n++) + Date.now().toString(36);
    const docPath = tpl.replace('{x}', id);
    await seed(docPath, { createdBy: 'someone-else', userId: 'someone-else', role: 'USER' });
    out[tpl + ':' + op] = op === 'read' ? await get(docPath, actor.headers) : await write(docPath, { note: 'probe' }, actor.headers);
  }
  return out;
}

async function dynamicChecks() {
  console.log('\n=== CHECK-T14-03 — ma trận danh tính 5 kịch bản trên rules THẬT của repo ===');
  await H.clearFirestore();
  await H.clearAuth();

  const owner = await H.googleAccount(H.OWNER_SUB, H.OWNER_EMAIL);
  const other = await H.googleAccount(H.OTHER_SUB, H.OTHER_EMAIL);
  const anon = await H.anonAccount();
  console.log('  owner(google)=' + owner.uid + '  other(google)=' + other.uid + '  anon=' + anon.uid);
  await H.setRules(owner.uid);              // đúng thao tác Owner làm khi deploy rules thật
  await seed('ethdca/state', { schema: 'coindca.ledger/2', rev: 1 });
  await seed('ethdca/seed', { schema: 'ethdca.seed/1' });

  // Dòng 1 — Owner (UID Google đúng): ALLOW  (C-AS-01)
  assert(await get('ethdca/state', owner.headers), '1. Owner Google UID -> read ethdca/state -> ALLOW');
  assert(await get('ethdca/seed', owner.headers), '1. Owner Google UID -> read ethdca/seed -> ALLOW');
  assert(await write('ethdca/state', { schema: 'coindca.ledger/2', rev: 2 }, owner.headers), '1. Owner -> update ethdca/state -> ALLOW');
  assert(await write('ethdca/seed', { schema: 'ethdca.seed/1', v: 2 }, owner.headers), '1. Owner -> update ethdca/seed -> ALLOW');

  // Dòng 2 — không đăng nhập: DENY  (C-AS-02)
  assert((await get('ethdca/state', {})) === false, '2. Không đăng nhập -> read ethdca/state -> DENY');
  assert((await write('ethdca/state', { rev: 99 }, {})) === false, '2. Không đăng nhập -> write ethdca/state -> DENY');
  assert((await get('ethdca/seed', {})) === false, '2. Không đăng nhập -> read ethdca/seed -> DENY');

  // Dòng 2b — ẩn danh (đã xác thực nhưng Anonymous): DENY — "đã đăng nhập" KHÔNG phải Owner
  assert((await get('ethdca/state', anon.headers)) === false, '2b. Ẩn danh (đã xác thực) -> read ethdca/state -> DENY');
  assert((await write('ethdca/state', { rev: 99 }, anon.headers)) === false, '2b. Ẩn danh -> write ethdca/state -> DENY');

  // Dòng 3 — tài khoản Google KHÁC đã đăng nhập: DENY  (C-AS-03)
  assert((await get('ethdca/state', other.headers)) === false, '3. Tài khoản Google khác -> read ethdca/state -> DENY');
  assert((await write('ethdca/state', { rev: 99 }, other.headers)) === false, '3. Tài khoản Google khác -> write ethdca/state -> DENY');
  assert((await get('ethdca/seed', other.headers)) === false, '3. Tài khoản Google khác -> read ethdca/seed -> DENY');

  // Dòng 4 — delete: DENY cho mọi actor (mặc định deny, không có rule delete)
  for (const [name, a] of [['Owner', owner.headers], ['Google khác', other.headers], ['ẩn danh', anon.headers], ['không đăng nhập', {}]]) {
    assert((await del('ethdca/state', a)) === false, '4. delete ethdca/state bởi ' + name + ' -> DENY');
    assert((await del('ethdca/seed', a)) === false, '4. delete ethdca/seed bởi ' + name + ' -> DENY');
  }
  // Không document ethdca/* nào khác được mở
  assert((await write('ethdca/other', { x: 1 }, owner.headers)) === false, '4b. document ethdca/* ngoài allow-list (kể cả Owner) -> DENY');

  // Dòng 5 — Owner CoinDCA KHÔNG có quyền Content đặc biệt nào (C-AS-04 phần "không leak ngược")
  const ownerProfile = await contentProfile(owner);
  const otherProfile = await contentProfile(other);
  const deviations = Object.keys(ownerProfile).filter((k) => ownerProfile[k] !== otherProfile[k]);
  assert(deviations.length === 0,
    '5. Owner CoinDCA có ĐÚNG quyền Content của một người dùng đã đăng nhập bình thường (lệch: ' + JSON.stringify(deviations) + ')');
  console.log('    (14 probe Content × 2 actor; hồ sơ quyền: ' + JSON.stringify(ownerProfile) + ')');
}

/* ---------------- C-AS-04 — regression baseline DEC-023, nguyên văn ---------------- */
function runSharedRulesMerge() {
  return new Promise((resolve) => {
    console.log('\n=== C-AS-04 — chạy lại nguyên văn test_shared_rules_merge.js (baseline DEC-023) ===');
    const child = spawn(process.execPath, [path.join(__dirname, 'test_shared_rules_merge.js')],
      { cwd: __dirname, stdio: ['ignore', 'pipe', 'pipe'] });
    let tail = '';
    const keep = (c) => { tail = (tail + c).slice(-2000); };
    child.stdout.on('data', keep); child.stderr.on('data', keep);
    child.on('close', (code) => {
      assert(code === 0, 'test_shared_rules_merge.js exit 0 — CONTENT_BEHAVIOR_PRESERVED, 0 deviation');
      if (code !== 0) console.log(tail);
      else console.log('  ' + tail.trim().split('\n').slice(-2).join('\n  '));
      resolve();
    });
  });
}

(async () => {
  staticChecks();
  const stop = await H.ensureEmulators();
  try {
    await dynamicChecks();
    await runSharedRulesMerge();
  } finally { await stop(); }
  console.log('\n=== TỔNG KẾT test_t14_rules ===');
  console.log('assertion đã chạy:', checks, '| FAIL:', failures);
  if (failures > 0) { console.log('T-14 RULES: FAIL'); process.exit(1); }
  console.log('T-14 RULES: PASS — CHECK-T14-02 + CHECK-T14-03 + C-AS-01..04/C-AS-13');
})().catch((e) => { console.error(e); process.exit(1); });
