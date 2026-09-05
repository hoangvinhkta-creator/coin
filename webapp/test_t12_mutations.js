/* Mutate actual production source in a temporary module; each invariant must kill its mutant. */
const fs = require('fs'), os = require('os'), path = require('path'), { spawnSync } = require('child_process');
const assert = require('assert/strict');
const original = fs.readFileSync(path.join(__dirname, 'ledger.js'), 'utf8');
const mutations = [
  ['INV-1', 'return s;\n  }\n  function derive', 'return Object.assign(s, { costVnd: 42 });\n  }\n  function derive'],
  ['INV-3', 'return exact(sign * ((2n * n + d) / (2n * d)));', 'return exact(sign * (n / d));'],
  ['INV-4', "if (out > usdt.qty) inconsistent(e);", '/* mutant: lose deficit flag */'],
  ['INV-9', "if (e.source === 'PLAN') planSpent[m]", "if (e.source !== 'PRICE') planSpent[m]"],
  ['INV-11', 'return cost === null || total <= 0 || qty > total ? null', 'return cost === null || total <= 0 || qty > total ? 0'],
  ['INV-12', 'if (!result.ok) return result;', 'if (!result.ok) { await hooks.commit(current); return result; }'],
  ['INV-14', 'await hooks.snapshot(clone(current));', '/* mutant: no snapshot */']
];
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 't12-mutation-')), results = [];
try {
  for (const [id, from, to] of mutations) {
    assert.equal(original.split(from).length, 2, id + ' mutation must match exactly once');
    const target = path.join(dir, id + '.js'); fs.writeFileSync(target, original.replace(from, to));
    const r = spawnSync(process.execPath, ['--test', '--test-name-pattern=^' + id + ' ', path.join(__dirname, 'test_t12_ledger.js')], { env: { ...process.env, T12_LEDGER_MODULE: target }, encoding: 'utf8' });
    assert.equal(r.status, 1, id + ' survived!\n' + r.stdout + r.stderr);
    assert.match(r.stdout + r.stderr, /AssertionError|ERR_ASSERTION/, 'must fail an assertion, not syntax or environment');
    results.push({ id, from, to, exitCode: r.status, result: 'KILLED', evidence: (r.stdout + r.stderr).split('\n').filter(x => /✖|not ok|AssertionError|Expected|actual:|expected:/.test(x)) });
  }
  console.log(JSON.stringify({ baseline: 'c610a29', total: results.length, killed: results.length, survivors: 0, results }, null, 2));
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
