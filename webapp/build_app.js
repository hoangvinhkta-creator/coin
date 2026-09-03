const fs = require('fs');
const path = require('path');

// __dirname thay vì cwd: script phải chạy đúng bất kể được gọi từ đâu
// (`node build_app.js` trong webapp/, hay `node webapp/build_app.js` từ gốc repo) — F-027.
const DIR = __dirname;
const shell  = fs.readFileSync(path.join(DIR, 'app_shell.html'), 'utf8');
const fbcfg  = fs.readFileSync(path.join(DIR, 'firebase_config.js'), 'utf8');
const engine = fs.readFileSync(path.join(DIR, 'engine.js'), 'utf8');
const logic  = fs.readFileSync(path.join(DIR, 'app_logic.js'), 'utf8');

// T-09B (DEC-020 OD-A): app chạy trên Firebase Hosting, nguồn bền là Cloud Firestore.
// Trang KHÔNG còn nhúng state/seed (`app-state`/`app-seed`) và KHÔNG còn nhúng base64 của
// chính nó để tự publish — cả hai là cơ chế của host artifact cũ; nhúng state vào trang sẽ
// tạo một "nguồn sự thật" thứ ba cạnh Firestore, trái CHECK-T09B-16.
const BODY = shell
  + '\n<script>\n' + fbcfg + '\n</script>\n'
  + '<script>\n' + engine + '\n</script>\n'
  + '<script>\n' + logic + '\n</script>\n';

const FULL = '<!doctype html><html lang="vi"><head><meta charset="utf-8">'
  + '<meta name="viewport" content="width=device-width,initial-scale=1">'
  + '</head><body>\n' + BODY + '\n</body></html>';

// Kiểm tra: không placeholder nào còn sót, và ba mảnh bắt buộc đều có mặt.
['__STATE__', '__SEED__', '__TEMPLATE__', 'id="app-state"', 'id="app-seed"'].forEach((t) => {
  if (FULL.includes(t)) throw new Error('legacy placeholder left in page: ' + t);
});
['window.ETHDCA_FIREBASE_CONFIG', 'firebase-app-compat.js', 'firebase-auth-compat.js',
 'firebase-firestore-compat.js', 'const ENGINE', 'ethdca/state'].forEach((t) => {
  if (!FULL.includes(t)) throw new Error('required fragment missing from page: ' + t);
});

// 1. webapp/app_final.html — bản dùng cho bộ test (mở qua HTTP server của harness).
fs.writeFileSync(path.join(DIR, 'app_final.html'), FULL);
// 2. webapp/public/index.html — thư mục `hosting.public` trong firebase.json (firebase deploy).
const PUB = path.join(DIR, 'public');
fs.mkdirSync(PUB, { recursive: true });
fs.writeFileSync(path.join(PUB, 'index.html'), FULL);

console.log('BODY', BODY.length, 'FULL', FULL.length,
  '->', path.relative(process.cwd(), path.join(DIR, 'app_final.html')),
  '+', path.relative(process.cwd(), path.join(PUB, 'index.html')));
