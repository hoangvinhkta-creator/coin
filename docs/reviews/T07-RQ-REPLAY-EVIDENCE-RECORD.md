# T-07 — RQ Replay Evidence Record (Owner-Run, Official Dataset)

**REPLAY EVIDENCE — OWNER-RUN — OFFICIAL T-06 DATASET — NOT A NEW OFFICIAL T-06 RUN.**

Authorized by: `DEC-039`. Script: `docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md` §6 (unmodified,
byte-identical to the smoke-tested version). Purpose of this file: preserve the complete,
verbatim Owner-run stdout as a bounded evidence artifact, separate from interpretation (which
lives in `T07-RQ-EVIDENCE-INVESTIGATION.md`). Modeled on the REPOSITORY-VERIFIED /
OWNER-REPORTED separation of `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §1.

**This file does NOT change, regenerate, or supersede any official T-06 artifact.** It records a
current-HEAD-code + preserved-official-dataset replay, run by the Owner, exactly as
`CHECK-B1-03` Addendum 3 did for `FS-08` post-`F-017`.

## 0. Provenance

| Field | Value |
|---|---|
| Run by | Owner, on the machine holding the preserved official T-06 dataset backup |
| Script source | `docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md` §6, commit `d7746fa` (unmodified) |
| Command | `python rq_evidence_script.py data/raw results/random_control_21b7d88e9691_metrics.json` |
| `SMOKE_MODE` | `false` (confirmed in the `DONE` block below — this is NOT the synthetic smoke path) |
| `STEP_0` | `"PASS — reproduced official baseline bit-for-bit"` |
| Label | **[O] OWNER-REPORTED** for the fact that this exact script ran on the exact preserved official dataset; **REPLAY** for every derived number below |

## 1. Verbatim stdout, as received

```json
{
  "STEP_0": "PASS — reproduced official baseline bit-for-bit"
}
```

```json
{
  "RQ-3_control_by_window": {
    "W1": {
      "v2_eth": 11.798298648485792,
      "control_f_p50": 11.55667403541975,
      "control_f_p95": 11.77132662700702,
      "control_g_p50": 11.521272297265984,
      "control_g_p95": 11.70173731319033,
      "beats_f": true,
      "beats_g": true
    },
    "W2": {
      "v2_eth": 1.1900938694937744,
      "control_f_p50": 1.1792110087444463,
      "control_f_p95": 1.2038805044109546,
      "control_g_p50": 1.1772770824863945,
      "control_g_p95": 1.197055246203998,
      "beats_f": false,
      "beats_g": false
    },
    "W3": {
      "v2_eth": 1.0361407636717388,
      "control_f_p50": 1.0388401320382705,
      "control_f_p95": 1.0501327685560764,
      "control_g_p50": 1.039518678772672,
      "control_g_p95": 1.0494142028285725,
      "beats_f": false,
      "beats_g": false
    },
    "W4": {
      "v2_eth": 8.464296865296985,
      "control_f_p50": 8.273708783259902,
      "control_f_p95": 8.450026625647594,
      "control_g_p50": 8.253047352929041,
      "control_g_p95": 8.392109949335197,
      "beats_f": true,
      "beats_g": true
    },
    "W5": {
      "v2_eth": 1.222811371088066,
      "control_f_p50": 1.2260905417159003,
      "control_f_p95": 1.2482898494246069,
      "control_g_p50": 1.230411887500483,
      "control_g_p95": 1.2499204356956126,
      "beats_f": false,
      "beats_g": false
    },
    "W6": {
      "v2_eth": 5.1466352254888434,
      "control_f_p50": 5.0312254966430245,
      "control_f_p95": 5.167612339560035,
      "control_g_p50": 5.0364726345031965,
      "control_g_p95": 5.146343848233371,
      "beats_f": false,
      "beats_g": true
    },
    "W7": {
      "v2_eth": 1.3690801887377626,
      "control_f_p50": 1.3757095520546216,
      "control_f_p95": 1.3987492303868276,
      "control_g_p50": 1.3807196361479428,
      "control_g_p95": 1.4016883422080118,
      "beats_f": false,
      "beats_g": false
    },
    "W8": {
      "v2_eth": 2.0887465459789536,
      "control_f_p50": 2.1188481678200546,
      "control_f_p95": 2.1643360758597323,
      "control_g_p50": 2.120150956694729,
      "control_g_p95": 2.154213977680725,
      "beats_f": false,
      "beats_g": false
    },
    "W9": {
      "v2_eth": 1.2713425614499638,
      "control_f_p50": 1.2643122718775917,
      "control_f_p95": 1.2819900993454847,
      "control_g_p50": 1.266340951618036,
      "control_g_p95": 1.2811570414832398,
      "beats_f": false,
      "beats_g": false
    },
    "OOS": {
      "v2_eth": 0.7944731110357278,
      "control_f_p50": 0.8044826613916618,
      "control_f_p95": 0.8159396007747329,
      "control_g_p50": 0.8041485135740122,
      "control_g_p95": 0.8141312585070214,
      "beats_f": false,
      "beats_g": false
    }
  }
}
```

```json
{
  "RQ-1_cash_vs_ae": {
    "per_window_cash_ratio_avg": {
      "W1": 0.13171944411340059,
      "W2": 0.14672997263139914,
      "W3": 0.16098072235155264,
      "W4": 0.13748438578618655,
      "W5": 0.16761919470638545,
      "W6": 0.10612811112909964,
      "W7": 0.15003764040778733,
      "W8": 0.12002182961058677,
      "W9": 0.13508558968879478
    },
    "per_window_ae": {
      "W1": 98.24002635320511,
      "W2": 97.8790219413226,
      "W3": 92.966247215573,
      "W4": 99.94327683216174,
      "W5": 100.97378343891359,
      "W6": 92.98840202539066,
      "W7": 101.16470808084873,
      "W8": 85.85999054120464,
      "W9": 94.87591808633995
    },
    "pearson_r": 0.5462761737147702,
    "spearman_r": 0.5,
    "n_windows": 9,
    "CAVEAT": "TUONG QUAN QUAN SAT tren 9 window CHONG LAN, KHONG PHAI bang chung nhan qua. Khong counterfactual run nao duoc thuc hien (cam sua strategy/threshold theo chi thi Owner DEC-039)."
  }
}
```

```json
{
  "RQ-4_eth_by_source": {
    "SMART": {
      "n": 221,
      "nominal": 4417.48915701315,
      "eth": 6.815409576311286,
      "avg_price": 648.1619494105348
    },
    "BASE": {
      "n": 276,
      "nominal": 4600.0,
      "eth": 7.618609285570265,
      "avg_price": 603.784736502035
    },
    "OPPORTUNITY": {
      "n": 20,
      "nominal": 14.537980541701897,
      "eth": 0.04209415628942361,
      "avg_price": 345.36814188041217
    },
    "CRASH": {
      "n": 20,
      "nominal": 128.02610644033717,
      "eth": 0.4346451319689238,
      "avg_price": 294.5531814894243
    }
  },
  "RQ-4_opportunity_cap_hit": {
    "share": 0.967891544773457,
    "n_samples": 2803,
    "n_hit": 2713,
    "reason": null,
    "at_cap_share": 0.967891544773457,
    "mean_idle_ratio": 0.5916959151798376,
    "share_idle_ge_1pct_cap": 1.0,
    "share_idle_ge_10pct_cap": 1.0
  },
  "RQ-4_cash_ratio_full_period": {
    "avg": 0.0368989932610942,
    "max": 1.0
  }
}
```

```json
{
  "DONE": true,
  "SMOKE_MODE": false
}
```

## 2. Internal-consistency verification (performed this session, mechanical, no interpretation)

Every check below is arithmetic re-derivation from the numbers in §1 — nothing here is trusted
narrative, and nothing here re-runs the engine.

| # | Check | Result |
|---|---|---|
| 1 | `SMOKE_MODE` field in the `DONE` block | `false` — confirms this is NOT the synthetic path |
| 2 | `STEP_0` literal string | `"PASS — reproduced official baseline bit-for-bit"` — the exact PASS-branch string the script prints only when all three frozen assertions (`v2_eth`, `control_f_p95`, `control_g_p95` within `1e-6` of the known official replay values) hold |
| 3 | All ten `beats_f`/`beats_g` booleans (`W1`..`W9`, `OOS`) recomputed independently as `v2_eth > control_*_p95` | **10/10 MATCH** — no boolean/numeric contradiction anywhere in `RQ-3_control_by_window` |
| 4 | Sum of `RQ-4_eth_by_source[*].eth` (`SMART+BASE+OPPORTUNITY+CRASH`) | `14.910758150139898` |
| 5 | Cross-check against the known frozen official aggregate `v2_eth = 14.910758150139896` (`CHECK-B1-03` Addendum 3, `WP-B1`) | **matches to `1.78e-15`** (floating-point summation-order artifact only) — strong independent confirmation that this replay's full-period run is the same deterministic computation as the already-canonical `WP-B1` replay |
| 6 | `avg_price` fields (`nominal / eth`) recomputed for all four sources | **4/4 MATCH** exactly |
| 7 | All nine `W1`..`W9` windows plus `OOS` present in `RQ-3_control_by_window` | Confirmed — no window silently dropped or missing |
| 8 | `RQ-4_opportunity_cap_hit.share` vs `.at_cap_share` | **numerically identical** (`0.967891544773457`) — every sampled day where the Opportunity pool was at-cap also happened to be idle in this replay; not a contradiction (`share` is a subset of `at_cap_share` by definition — see `opportunity_cap_hit_share()` in `src/eth_dca_os/metrics.py`), just a notable fact carried into interpretation |

**No contradiction found between any block.** `STEP_0 = PASS` is corroborated independently by
check #5 (the by-source ETH sum reproduces the known frozen aggregate to floating-point
precision), which the script itself does not print explicitly in the PASS branch — this is an
extra, unplanned cross-check that increases confidence in the replay's integrity.

## 3. What this file does NOT do

- Does not alter `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` or any official T-06 artifact.
- Is not a new official T-06 run, not a Gate 1/2/3 re-evaluation, not a verdict recomputation.
- Carries no interpretation beyond the mechanical consistency checks in §2 — interpretation and
  RQ reassessment live in `docs/reviews/T07-RQ-EVIDENCE-INVESTIGATION.md`.
