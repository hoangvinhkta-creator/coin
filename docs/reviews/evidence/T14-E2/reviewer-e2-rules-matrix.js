/* E2 INDEPENDENT — reviewer-controlled Firestore authorization matrix.
   Uses ONLY low-level emulator primitives (REST + setRules) from the harness.
   Does NOT reuse any implementer assertion, scenario or expectation table. */
const H = require(require('path').join(__dirname, '..', '..', '..', '..', 'webapp', 'test_firebase_harness.js'));
const fs = require('fs');

let pass = 0, fail = 0;
function check(label, got, want) {
  const ok = got === want;
  if (ok) pass++; else fail++;
  console.log((ok ? '  ok  ' : '  FAIL') + ' | ' + label.padEnd(58) + ' got=' + got + ' want=' + want);
}

// Reviewer-chosen identities, deliberately different from the implementer's.
const REV_OWNER_SUB = 'e2-reviewer-owner-9f3a';
const REV_OTHER_SUB = 'e2-reviewer-intruder-71bc';

async function probe(method, path, headers, body) {
  const r = await H.rest(method, H.FS_PORT, '/v1/projects/demo-ethdca/databases/(default)/documents' + path,
    body, headers);
  return r.status === 200 ? 'ALLOW' : (r.status === 403 || r.status === 404 ? (r.status === 403 ? 'DENY' : 'DENY/404') : 'HTTP' + r.status);
}
const FIELDS = { fields: { probe: { stringValue: 'e2' } } };

(async () => {
  await H.ensureEmulators();
  await H.clearFirestore();
  await H.clearAuth();

  const owner = await H.googleAccount(REV_OWNER_SUB, 'e2-owner@example.test');
  const other = await H.googleAccount(REV_OTHER_SUB, 'e2-other@example.test');
  const anon  = await H.anonAccount();

  console.log('reviewer OWNER uid  = ' + owner.uid);
  console.log('reviewer OTHER uid  = ' + other.uid);
  console.log('reviewer ANON  uid  = ' + anon.uid);
  console.log('rules file          = ' + H.RULES_PATH + ' (real repo file, placeholder -> reviewer owner uid)');

  // Deploy the REAL repo ruleset with the reviewer's owner UID substituted.
  await H.setRules(owner.uid);

  // Seed a financial document as admin so READ probes are testing rules, not emptiness.
  await H.putDoc('state', { schema: 'coindca.ledger/2', rev: 7, events: [], secretBalance: 123456789 });

  console.log('\n--- A. CoinDCA financial documents (ethdca/state) ---');
  check('Owner (google.com, matching UID) READ',      await probe('GET',   '/ethdca/state', owner.headers), 'ALLOW');
  check('Owner UPDATE (write)',                        await probe('PATCH', '/ethdca/state', owner.headers, FIELDS), 'ALLOW');
  check('Owner DELETE (must stay denied)',             await probe('DELETE','/ethdca/state', owner.headers), 'DENY');
  check('UNAUTHENTICATED READ',                        await probe('GET',   '/ethdca/state', undefined), 'DENY');
  check('UNAUTHENTICATED WRITE',                       await probe('PATCH', '/ethdca/state', undefined, FIELDS), 'DENY');
  check('ANONYMOUS auth READ',                         await probe('GET',   '/ethdca/state', anon.headers), 'DENY');
  check('ANONYMOUS auth WRITE',                        await probe('PATCH', '/ethdca/state', anon.headers, FIELDS), 'DENY');
  check('OTHER authenticated Google user READ',        await probe('GET',   '/ethdca/state', other.headers), 'DENY');
  check('OTHER authenticated Google user WRITE',       await probe('PATCH', '/ethdca/state', other.headers, FIELDS), 'DENY');

  console.log('\n--- B. ethdca/seed + namespace boundedness ---');
  check('Owner READ ethdca/seed',                      await probe('GET',   '/ethdca/seed', owner.headers), 'DENY/404');
  check('Owner WRITE ethdca/seed',                     await probe('PATCH', '/ethdca/seed', owner.headers, FIELDS), 'ALLOW');
  check('Owner WRITE ethdca/notallowlisted (bounded)', await probe('PATCH', '/ethdca/rogue', owner.headers, FIELDS), 'DENY');
  check('Owner READ ethdca/notallowlisted (bounded)',  await probe('GET',   '/ethdca/rogue', owner.headers), 'DENY');

  console.log('\n--- C. Content namespace: do Content users reach CoinDCA? ---');
  // Build a Content MANAGER profile for the intruder, the strongest Content role short of admin.
  await H.rest('PATCH', H.FS_PORT, '/v1/projects/demo-ethdca/databases/(default)/documents/users/' + other.uid,
    { fields: { role: { stringValue: 'ADMIN' } } }, { Authorization: 'Bearer owner' });
  check('Content ADMIN reads CoinDCA ledger',          await probe('GET',   '/ethdca/state', other.headers), 'DENY');
  check('Content ADMIN writes CoinDCA ledger',         await probe('PATCH', '/ethdca/state', other.headers, FIELDS), 'DENY');

  console.log('\n--- D. Reverse direction: what Content access does the CoinDCA Owner hold? ---');
  check('CoinDCA Owner reads Content /users',          await probe('GET',   '/users/' + other.uid, owner.headers), 'ALLOW');
  check('ANONYMOUS reads Content /users (pre-T14 class)', await probe('GET','/users/' + other.uid, anon.headers), 'ALLOW');
  check('CoinDCA Owner deletes Content user (admin-only)', await probe('DELETE', '/users/' + other.uid, owner.headers), 'DENY');

  console.log('\n--- E. Placeholder ruleset grants nobody ---');
  await H.setRules('OWNER_UID_REQUIRED');
  check('Owner under un-deployed placeholder rules READ', await probe('GET', '/ethdca/state', owner.headers), 'DENY');
  check('Anon under un-deployed placeholder rules READ',  await probe('GET', '/ethdca/state', anon.headers), 'DENY');

  console.log('\n=== E2 INDEPENDENT RULES MATRIX: pass=' + pass + ' fail=' + fail + ' ===');
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('ERROR', e); process.exit(2); });
