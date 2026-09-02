/* WP-C1 — smoke test đường sản phẩm: seed -> vốn -> P2P -> ladder -> mua -> dashboard ->
 * lịch sử -> reload.
 *
 * BẢO TRÌ T-09A (2026-09-02): thêm MỘT bước tiền đề — nhập chuỗi ngày giảm giá qua đúng UI
 * "Nhập số liệu" để mở Smart unlock. Trước T-09A, bước 4 reserve 100% Smart available khi
 * Smart unlock = 0%, tức đúng hành vi mà V-02 tố cáo là SAI (Strategy §12). Sau bản vá,
 * thao tác đó bị TỪ CHỐI, nên tiền đề là bắt buộc để bước 4 còn tạo được ladder. Các bước
 * và phép kiểm phía sau GIỮ NGUYÊN.
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const H = require('./test_helpers.js');

// __dirname thay vì cwd: test phải chạy đúng bất kể được gọi từ đâu — F-027.
const DIR = __dirname;
const APP_FINAL = path.join(DIR, 'app_final.html');
const SEED_PATH = path.join(DIR, '..', 'demo', 'results3', 'live_seed.json');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 1200, height: 1000 } });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  p.on('console', m => { if (m.type() === 'error' && !/ERR_CONNECTION|font/i.test(m.text())) errs.push('console: ' + m.text()); });

  await p.goto('file://' + APP_FINAL);
  await p.waitForTimeout(400);

  console.log('-- initial banners:', (await p.textContent('#banners')).replace(/\s+/g,' ').slice(0,120));

  // 1. nạp seed
  await p.setInputFiles('#seedFile', SEED_PATH);
  await p.waitForTimeout(900);
  console.log('-- seed msg:', (await p.textContent('#seedMsg')).trim());
  console.log('-- OSCORE:', (await p.textContent('#osVal')).trim());
  console.log('-- chips:', (await p.textContent('#stateChips')).replace(/\s+/g,' ').trim());
  console.log('-- parity:', (await p.textContent('#parityBox')).replace(/\s+/g,' ').slice(0,160));

  // 1b. tiền đề T-09A: mở Smart unlock qua đường nhập giá thật
  const unlock0 = await H.pushDeclineDays(p, 12);
  console.log('-- Smart unlock sau tiền đề T-09A:', (unlock0.smartUnlock * 100).toFixed(2) + '%');

  // 2. nạp vốn tháng
  await p.click('[data-tab="entry"]');
  await p.fill('#cbMonth', '2026-06');
  await p.fill('#cbAmt', '10000000');
  await p.click('#cbAdd');
  await p.waitForTimeout(250);
  console.log('-- contribution:', (await p.textContent('#cbMsg')).trim());

  // 3. P2P mua USDT
  await p.fill('#p2pVnd', '5000000');
  await p.fill('#p2pUsdt', '196.5');
  await p.fill('#p2pFee', '0');
  await p.click('#p2pAdd');
  await p.waitForTimeout(250);
  console.log('-- p2p:', (await p.textContent('#p2pMsg')).trim());

  // 4. tạo ladder Smart
  await p.click('[data-tab="ladder"]');
  await p.waitForTimeout(150);
  console.log('-- cap hint:', (await p.textContent('#ldCapHint')).trim());
  await p.fill('#ldCap', '3000000');
  await p.click('#ldAdd');
  await p.waitForTimeout(300);
  console.log('-- ladder:', (await p.textContent('#ldMsg')).trim());
  const zoneRows = await p.$$eval('#ladderList tbody tr', r => r.length);
  console.log('-- zone rows:', zoneRows);

  // 5. mua ETH
  await p.click('[data-tab="entry"]');
  await p.fill('#buyUsdt', '150');
  await p.fill('#buyPrice', '205.5');
  await p.fill('#buyRec', '204.0');
  await p.fill('#buyVndRate', '25400');
  await p.click('#buyAdd');
  await p.waitForTimeout(250);
  console.log('-- buy:', (await p.textContent('#buyMsg')).trim());

  // 6. kiểm dashboard
  await p.click('[data-tab="dash"]');
  await p.waitForTimeout(250);
  const port = await p.textContent('#portfolioStats');
  console.log('-- portfolio:', port.replace(/\s+/g,' ').slice(0, 220));
  const trez = await p.textContent('#treasuryStats');
  console.log('-- treasury:', trez.replace(/\s+/g,' ').slice(0, 200));
  console.log('-- action:', (await p.textContent('#actionBox')).replace(/\s+/g,' ').slice(0,150));

  // 7. invariant check qua state trong localStorage
  const st = await p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));
  const m = st.months['2026-06'];
  const tot = x => x.a + x.r + x.d;
  console.log('-- base pool total:', tot(m.base), '(expect 5,000,000)');
  console.log('-- smart pool a/r/d:', m.smart.a, m.smart.r, m.smart.d, 'total', tot(m.smart));
  console.log('-- oppFund total:', tot(st.oppFund));
  console.log('-- treasury vnd/usdt:', Math.round(st.treasury.vnd), st.treasury.usdt.toFixed(2));
  console.log('-- eth:', st.eth, 'trades:', st.trades.length, 'ledger:', st.ledger.length);
  const neg = [m.base, m.smart, st.oppFund].some(x => x.a < -1e-6 || x.r < -1e-6 || x.d < -1e-6);
  console.log('-- any negative pool:', neg);

  // 8. lịch sử
  await p.click('[data-tab="history"]');
  await p.waitForTimeout(200);
  console.log('-- trade rows:', await p.$$eval('#tradeTable tbody tr', r => r.length));
  console.log('-- ledger rows:', await p.$$eval('#ledgerTable tbody tr', r => r.length));

  // 9. persistence: reload -> state phải còn
  await p.reload();
  await p.waitForTimeout(700);
  console.log('-- after reload OSCORE:', (await p.textContent('#osVal')).trim());
  const st2 = await p.evaluate(() => JSON.parse(localStorage.getItem('ethdca-tracker-state-v1')));
  console.log('-- after reload eth:', st2.eth, 'trades:', st2.trades.length);

  // 10. pageHTML() dựng được tài liệu hợp lệ
  const okHtml = await p.evaluate(() => {
    const el = document.getElementById('page-template');
    if (!el) return 'no template el';
    const b64 = el.textContent.trim();
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
    const tpl = new TextDecoder('utf-8').decode(bytes);
    return tpl.startsWith('<!doctype html>') && tpl.includes('__STATE__') ? 'ok' : 'bad';
  });
  console.log('-- template decodable:', okHtml);

  await p.screenshot({ path: path.join(DIR, 'app-dash.png'), fullPage: true });
  await ctx.close(); await b.close();
  console.log(errs.length ? '\nERRORS:\n' + errs.join('\n') : '\nno page errors');
})();
