/* T-14 bước C — CHECK-T14-04 (`firebase.json` khai `hosting.target`) + CHECK-T14-05 (runbook
 * deploy rules 3 bước) + C-AS-12 (deploy CoinDCA có mục tiêu) + C-AS-13 (giả định cấu hình liên
 * quan Content không đổi).
 * KHÔNG phải production path (PROJECT/PRODUCTION_PATHS.md §2). Không cần emulator/trình duyệt.
 *
 * Cô lập deploy KHÔNG kiểm được bằng cách thật sự deploy (không có Firebase CLI authority trong
 * phiên này, và deploy thật lên project dùng chung là đúng thứ runbook cấm). Cái kiểm được — và
 * là toàn bộ nội dung của hai check này — là: (a) cấu hình repo khai target tường minh; (b) mọi
 * bề mặt cấu hình khác của Hosting/Firestore KHÔNG đổi so với trước T-14, nên không có đường mới
 * nào chạm tới Content; (c) tài liệu vận hành ghi đúng ba bước bắt buộc và lệnh có scope.
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, 'firebase.json'), 'utf8'));
const readme = fs.readFileSync(path.join(__dirname, 'README.md'), 'utf8');

// Cấu hình `firebase.json` TRƯỚC T-14 (origin/main 97434d0), nguyên văn. Bước C được phép thêm
// ĐÚNG một khoá `hosting.target`; mọi khác biệt khác là thay đổi bề mặt deploy => FAIL.
const BEFORE_T14 = {
  hosting: {
    public: 'webapp/public',
    ignore: ['**/.*'],
    headers: [{ source: '**', headers: [{ key: 'Cache-Control', value: 'no-cache' }] }],
  },
  firestore: { rules: 'firestore.rules' },
  emulators: {
    auth: { host: '127.0.0.1', port: 9099 },
    firestore: { host: '127.0.0.1', port: 8080 },
    ui: { enabled: false },
    singleProjectMode: true,
  },
};

let checks = 0, failures = 0;
function assert(cond, label) {
  checks++;
  if (!cond) { failures++; console.log('  ASSERT FAIL:', label); } else console.log('  ok:', label);
}
const has = (re, label) => assert(re.test(readme), label);

console.log('\n=== CHECK-T14-04 — firebase.json khai hosting.target = "coindca" ===');
assert(cfg.hosting && cfg.hosting.target === 'coindca', 'hosting.target === "coindca"');
assert(cfg.hosting.public === 'webapp/public', 'hosting.public không đổi (webapp/public)');
assert(!('site' in cfg.hosting), 'không hard-code `site` vào repo — ánh xạ target->site là thao tác Owner một lần');
has(/firebase target:apply hosting coindca <site-id-coindca>/,
  'tài liệu vận hành ghi lệnh `firebase target:apply hosting coindca <site-id>` Owner chạy một lần');

console.log('\n=== C-AS-13 — bề mặt cấu hình còn lại KHÔNG đổi so với trước T-14 ===');
const after = JSON.parse(JSON.stringify(cfg));
delete after.hosting.target;
assert(JSON.stringify(after) === JSON.stringify(BEFORE_T14),
  'firebase.json khác bản trước T-14 ĐÚNG một khoá hosting.target và không gì khác');
assert(Object.keys(cfg).sort().join(',') === 'emulators,firestore,hosting',
  'không thêm khối cấu hình mới nào (functions/storage/... = không có)');

console.log('\n=== CHECK-T14-05 / C-AS-12 — runbook deploy rules 3 bước + lệnh có scope ===');
has(/##\s*Runbook deploy/, 'README có mục "Runbook deploy"');
has(/không bao giờ chạy `firebase deploy` trần/, 'cấm tường minh `firebase deploy` trần (không scope)');
has(/firebase deploy --only hosting:coindca --project/, 'lệnh deploy Hosting dùng `--only hosting:coindca`');
has(/firebase deploy --only firestore:rules --project/, 'lệnh deploy rules dùng `--only firestore:rules`');
// Ba bước, đúng thứ tự, trong cùng một khối runbook.
const block = readme.slice(readme.indexOf('### Ba bước bắt buộc'));
assert(block.length > 200, 'tìm thấy khối "Ba bước bắt buộc TRƯỚC mọi firebase deploy --only firestore:rules"');
const s1 = block.indexOf('npm --prefix webapp run test:rules-merge');
const s2 = block.indexOf('git diff -- firestore.rules');
const s3 = block.search(/Chỉ deploy sau khi \(1\) và \(2\) đều đạt/);
assert(s1 > 0, 'bước 1 = chạy test safe-merge (`npm --prefix webapp run test:rules-merge`)');
assert(s2 > 0, 'bước 2 = đọc diff `firestore.rules` thủ công');
assert(s3 > 0, 'bước 3 = chỉ deploy sau khi (1) và (2) đều đạt');
assert(s1 < s2 && s2 < s3, 'ba bước xuất hiện ĐÚNG thứ tự test -> diff -> deploy');
has(/ngoài khối `COINDCA`.*(dừng|hỏi)/s, 'bước 2 nêu rõ: thay đổi ngoài khối COINDCA = tín hiệu dừng và hỏi Owner');
has(/FB-3/, 'runbook nhắc FB-3 (placeholder OWNER_UID_REQUIRED có thể tự khoá Owner khi deploy lại)');
// Lệnh trong runbook phải chạy được: script npm được tham chiếu phải tồn tại thật.
const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
assert(typeof pkg.scripts['test:rules-merge'] === 'string',
  'script `test:rules-merge` tồn tại thật trong webapp/package.json (runbook không trỏ vào lệnh ma)');

console.log('\n=== TỔNG KẾT test_t14_deploy_isolation ===');
console.log('assertion đã chạy:', checks, '| FAIL:', failures);
if (failures > 0) { console.log('T-14 DEPLOY ISOLATION: FAIL'); process.exit(1); }
console.log('T-14 DEPLOY ISOLATION: PASS — CHECK-T14-04 + CHECK-T14-05 + C-AS-12/C-AS-13');
