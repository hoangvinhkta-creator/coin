const fs = require('fs');
const path = require('path');

// __dirname thay vì cwd: script phải chạy đúng bất kể được gọi từ đâu
// (`node build_app.js` trong webapp/, hay `node webapp/build_app.js` từ gốc repo) — F-027.
const DIR = __dirname;
const shell  = fs.readFileSync(path.join(DIR, 'app_shell.html'), 'utf8');
const engine = fs.readFileSync(path.join(DIR, 'engine.js'), 'utf8');
const logic  = fs.readFileSync(path.join(DIR, 'app_logic.js'), 'utf8');

// BODY chứa 3 placeholder: __STATE__, __SEED__, __TEMPLATE__
const BODY = shell
  + '\n<script id="page-template" type="text/plain">__TEMPLATE__</script>\n'
  + '<script>\n' + engine + '\n</script>\n'
  + '<script>\n' + logic + '\n</script>\n';

// Tài liệu đầy đủ dùng khi trang tự publish
const FULL = '<!doctype html><html lang="vi"><head><meta charset="utf-8">'
  + '<meta name="viewport" content="width=device-width,initial-scale=1">'
  + '</head><body>\n' + BODY + '\n</body></html>';

const b64 = Buffer.from(FULL, 'utf8').toString('base64');

const initialState = JSON.stringify({
  schema: 'ethdca.tracker/1', rev: 0, months: {}, oppFund: {a:0,r:0,d:0},
  treasury: {vnd:0, usdt:0}, eth: 0, costUsdt: 0, costVnd: 0,
  ladders: [], trades: [], p2p: [], ledger: [], extraDays: [],
});

// Trang khởi tạo: body-only (Artifact tool tự bọc doctype/head/body)
const page = BODY
  .replace('__TEMPLATE__', () => b64)
  .replace('__STATE__', () => initialState)
  .replace('__SEED__', () => 'null');

fs.writeFileSync(path.join(DIR, 'app_final.html'), page);
console.log('BODY', BODY.length, 'FULL', FULL.length, 'b64', b64.length, 'page', page.length);

// kiểm tra quine: giải mã b64 -> thay lại -> phải ra tài liệu hợp lệ
const decoded = Buffer.from(b64, 'base64').toString('utf8');
if (decoded !== FULL) throw new Error('base64 round-trip mismatch');
const republished = decoded
  .replace('__TEMPLATE__', () => b64)
  .replace('__STATE__', () => '{"rev":7}')
  .replace('__SEED__', () => 'null');
if (!republished.startsWith('<!doctype html>')) throw new Error('republished missing doctype');
// placeholder trong markup phải biến mất; các literal còn lại nằm trong mã JS
// của pageHTML() — đó là cố ý, lần lưu sau cần chúng.
if (!republished.includes('id="app-state" type="application/json">{"rev":7}')) {
  throw new Error('state not injected into markup');
}
if (!republished.includes('id="app-seed" type="application/json">null')) {
  throw new Error('seed not injected into markup');
}
if (republished.includes('>__TEMPLATE__<')) {
  throw new Error('template placeholder left in markup');
}
// và bản republish vẫn chứa b64 để lần lưu sau còn dùng được
if (!republished.includes(b64)) throw new Error('template lost on republish');
console.log('quine ok; republished', republished.length);
