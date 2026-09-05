/* OWNER_LOCAL_ACCEPTANCE: chạy local, chỉ in PASS/FAIL; không đưa dữ liệu Owner vào repo. */
const fs = require('fs'), L = require('./ledger');
const mapping = { ethQty: 'holdings.ETH.qty', avgCostUsdt: 'holdings.ETH.avgCostUsdt', avgCostVnd: 'holdings.ETH.avgCostVnd', investedThisMonthVnd: 'month.investedThisMonthVnd', planInvestedVnd: 'month.planInvestedVnd', remainingPlannedBudgetVnd: 'month.remainingPlannedBudgetVnd', reserveBalanceVnd: 'reserve.balance', nextPlannedDate: 'month.nextPlannedDate', nextPlannedAmountVnd: 'month.nextPlannedAmountVnd' };
try {
  if (!process.argv[2]) throw Error('Cần đường dẫn fixture local');
  const f = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  if (!f.tolerance || ['vnd', 'usdt', 'qty'].some(k => f.tolerance[k] !== 0)) throw Error('Tolerance phải bằng 0');
  if (!f.expected || !('avgCostUsdt' in f.expected || 'avgCostVnd' in f.expected)) throw Error('Cần ít nhất một oracle giá vốn bình quân');
  const d = L.derive(f.openingPosition, f.plan, f.events, f.asOfDate);
  for (const [key, expected] of Object.entries(f.expected)) {
    if (!mapping[key]) throw Error('Trường oracle không hỗ trợ');
    const actual = mapping[key].split('.').reduce((a, k) => a[k], d);
    const matches = actual && typeof actual === 'object' && 'numerator' in actual ? Number.isSafeInteger(expected) && BigInt(actual.numerator) === BigInt(expected) * BigInt(actual.denominator) : actual === (expected === 'UNKNOWN' ? null : expected);
    if (!matches) throw Error('Oracle không khớp');
  }
  console.log('OWNER_LOCAL_ACCEPTANCE: PASS');
} catch (e) { console.error('OWNER_LOCAL_ACCEPTANCE: FAIL'); process.exitCode = 1; }
