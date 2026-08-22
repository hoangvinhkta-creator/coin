/* ETH DCA OS V2.1.5 — score & capital engine, bản JS cho app theo dõi.
 *
 * Đây là bản cài đặt THỨ HAI của cùng một đặc tả (bản gốc là Python trong repo).
 * Impl Plan §1 muốn live và backtest dùng chung một core function; một trang tĩnh
 * không chạy được Python nên không thể dùng chung thật. Bù lại, mọi seed đều mang
 * theo OSCORE do Python tính và app đối chiếu liên tục — xem checkParity().
 *
 * Tham chiếu điều khoản: Strategy §1 (score), §3 (degradation), §4 (unlock),
 * §11 (spacing), §12–13 (ladder), §18.2 (invalidation).
 */

const ENGINE = (() => {
  "use strict";

  const clamp = (x, lo = 0, hi = 1) =>
    Number.isFinite(x) ? Math.min(Math.max(x, lo), hi) : NaN;

  /* ---------- rolling helpers (khớp semantics của pandas trong indicators.py) ---------- */

  // rolling(window, min_periods=window).max()
  function rollMax(a, w) {
    const out = new Array(a.length).fill(NaN);
    for (let i = w - 1; i < a.length; i++) {
      let m = -Infinity, ok = true;
      for (let j = i - w + 1; j <= i; j++) {
        if (!Number.isFinite(a[j])) { ok = false; break; }
        if (a[j] > m) m = a[j];
      }
      if (ok) out[i] = m;
    }
    return out;
  }

  function rollMean(a, w) {
    const out = new Array(a.length).fill(NaN);
    for (let i = w - 1; i < a.length; i++) {
      let s = 0, ok = true;
      for (let j = i - w + 1; j <= i; j++) {
        if (!Number.isFinite(a[j])) { ok = false; break; }
        s += a[j];
      }
      if (ok) out[i] = s / w;
    }
    return out;
  }

  // _rolling_percentile_of_last: tỷ lệ giá trị trong cửa sổ NHỎ HƠN giá trị hiện tại
  function rollPercentileOfLast(a, w) {
    const out = new Array(a.length).fill(NaN);
    for (let i = w - 1; i < a.length; i++) {
      let c = 0, ok = true;
      for (let j = i - w + 1; j <= i; j++) {
        if (!Number.isFinite(a[j])) { ok = false; break; }
        if (a[j] < a[i]) c++;
      }
      if (ok) out[i] = c / w;
    }
    return out;
  }

  // RSI Wilder chuẩn — khớp indicators.wilder_rsi
  function wilderRSI(close, period = 14) {
    const n = close.length;
    const out = new Array(n).fill(NaN);
    if (n <= period) return out;
    const delta = new Array(n);
    delta[0] = 0;
    for (let i = 1; i < n; i++) delta[i] = close[i] - close[i - 1];
    const gain = delta.map((d) => (d > 0 ? d : 0));
    const loss = delta.map((d) => (d < 0 ? -d : 0));

    let ag = 0, al = 0;
    for (let i = 1; i <= period; i++) { ag += gain[i]; al += loss[i]; }
    ag /= period; al /= period;
    const avgGain = new Array(n).fill(NaN), avgLoss = new Array(n).fill(NaN);
    avgGain[period] = ag; avgLoss[period] = al;
    for (let i = period + 1; i < n; i++) {
      avgGain[i] = (avgGain[i - 1] * (period - 1) + gain[i]) / period;
      avgLoss[i] = (avgLoss[i - 1] * (period - 1) + loss[i]) / period;
    }
    for (let i = period; i < n; i++) {
      if (!Number.isFinite(avgGain[i])) continue;
      if (avgLoss[i] === 0) { out[i] = 100; continue; }
      const rs = avgGain[i] / avgLoss[i];
      out[i] = 100 - 100 / (1 + rs);
    }
    return out;
  }

  /* ---------- indicators ---------- */

  /** history: [{d, e, b, v}] đã sắp theo ngày tăng dần. Trả về mảng cùng độ dài. */
  function computeIndicators(history) {
    const close = history.map((r) => r.e);
    const btc = history.map((r) => r.b);
    const vol = history.map((r) => r.v);
    const n = history.length;

    const high365 = rollMax(close, 365);
    const ma200 = rollMean(close, 200);
    const pct365 = rollPercentileOfLast(close, 365);
    const rsi14 = wilderRSI(close, 14);
    const vol7 = rollMean(vol, 7);
    const vol90 = rollMean(vol, 90);

    const ethbtc = close.map((c, i) =>
      Number.isFinite(c) && Number.isFinite(btc[i]) && btc[i] !== 0 ? c / btc[i] : NaN);
    const ebPct180 = rollPercentileOfLast(ethbtc, 180);

    const dailyRet = new Array(n).fill(NaN);
    for (let i = 1; i < n; i++) dailyRet[i] = close[i] / close[i - 1] - 1;
    const adr30 = rollMean(dailyRet.map((x) => (Number.isFinite(x) ? Math.abs(x) : NaN)), 30);

    const out = [];
    for (let i = 0; i < n; i++) {
      const ret7 = i >= 7 ? close[i] / close[i - 7] - 1 : NaN;
      const eb30 = i >= 30 ? ethbtc[i] / ethbtc[i - 30] - 1 : NaN;
      out.push({
        d: history[i].d,
        close: close[i],
        btc_close: btc[i],
        volume: vol[i],
        high365: high365[i],
        dd365: Number.isFinite(high365[i]) ? close[i] / high365[i] - 1 : NaN,
        ma200: ma200[i],
        ma_ratio: Number.isFinite(ma200[i]) ? close[i] / ma200[i] : NaN,
        percentile365: pct365[i],
        rsi14: rsi14[i],
        return7: ret7,
        volume_ratio: Number.isFinite(vol7[i]) && Number.isFinite(vol90[i]) && vol90[i] !== 0
          ? vol7[i] / vol90[i] : NaN,
        adr30: adr30[i],
        ethbtc: ethbtc[i],
        ethbtc_return30: eb30,
        ethbtc_percentile180: ebPct180[i],
      });
    }
    return out;
  }

  /* ---------- score (Strategy §1, §3) ---------- */

  function subFactors(ind) {
    const V0 = clamp((ind.volume_ratio - 1) / 1.5);
    let V;
    if (!Number.isFinite(ind.return7) || !Number.isFinite(ind.volume_ratio)) V = NaN;
    else V = ind.return7 >= 0 ? 0 : V0;
    return {
      D: clamp((-ind.dd365 - 0.05) / 0.55),
      M: clamp((1.05 - ind.ma_ratio) / 0.40),
      P: clamp((0.90 - ind.percentile365) / 0.80),
      R: clamp((55 - ind.rsi14) / 30),
      S7: clamp((-ind.return7 - 0.02) / 0.18),
      V: V,
      W: clamp((-ind.ethbtc_return30 - 0.02) / 0.18),
      RP: clamp((0.70 - ind.ethbtc_percentile180) / 0.60),
    };
  }

  const FACTOR_DEF = {
    PRICE_LOCATION: [["D", 0.50], ["M", 0.30], ["P", 0.20]],
    MARKET_STRESS: [["R", 0.50], ["S7", 0.30], ["V", 0.20]],
    RELATIVE_VALUE: [["W", 0.60], ["RP", 0.40]],
  };
  const SUB_NAMES = ["D", "M", "P", "R", "S7", "V", "W", "RP"];

  /** DEGRADED: sub-factor thiếu đóng góp 0, KHÔNG rescale phần còn lại (Strategy §3). */
  function factorScores(sf, weights = [50, 30, 20]) {
    const top = {
      PRICE_LOCATION: weights[0], MARKET_STRESS: weights[1], RELATIVE_VALUE: weights[2],
    };
    const res = {};
    let allNaN = true;
    for (const [factor, pairs] of Object.entries(FACTOR_DEF)) {
      let acc = 0, everyNaN = true;
      for (const [name, w] of pairs) {
        const v = sf[name];
        if (Number.isFinite(v)) { acc += v * w; everyNaN = false; }
      }
      res[factor] = top[factor] * acc;
      if (!everyNaN) allNaN = false;
    }
    const missing = SUB_NAMES.filter((k) => !Number.isFinite(sf[k])).length;
    return {
      price_location_score: res.PRICE_LOCATION,
      market_stress_score: res.MARKET_STRESS,
      relative_value_score: res.RELATIVE_VALUE,
      oscore: allNaN ? NaN
        : res.PRICE_LOCATION + res.MARKET_STRESS + res.RELATIVE_VALUE,
      data_quality: missing === 0 ? "GOOD" : (missing < SUB_NAMES.length ? "DEGRADED" : "INVALID"),
      missing_count: missing,
    };
  }

  function scoreForDay(ind, weights) {
    const sf = subFactors(ind);
    return Object.assign({ sub: sf }, factorScores(sf, weights));
  }

  /* ---------- unlock & spacing (Strategy §4, §11) ---------- */

  const smartUnlock = (oscore) => clamp((oscore - 35) / 35);
  const opportunityUnlock = (oscore) => 0.60 * clamp((oscore - 65) / 30);

  const MULT_X = [40, 60, 70, 80, 90];
  const MULT_Y = [0.80, 0.90, 1.00, 1.15, 1.30];
  function scoreMultiplier(oscore) {
    if (!Number.isFinite(oscore)) return NaN;
    if (oscore <= MULT_X[0]) return MULT_Y[0];
    if (oscore >= MULT_X[MULT_X.length - 1]) return MULT_Y[MULT_Y.length - 1];
    for (let i = 1; i < MULT_X.length; i++) {
      if (oscore <= MULT_X[i]) {
        const t = (oscore - MULT_X[i - 1]) / (MULT_X[i] - MULT_X[i - 1]);
        return MULT_Y[i - 1] + t * (MULT_Y[i] - MULT_Y[i - 1]);
      }
    }
    return MULT_Y[MULT_Y.length - 1];
  }

  function smartSpacing(adr30, oscore, cfg) {
    const raw = adr30 * cfg.smart_spacing_factor * scoreMultiplier(oscore);
    return Math.min(Math.max(raw, cfg.smart_spacing_min), cfg.smart_spacing_max);
  }
  const opportunitySpacing = (smartSp, cfg) =>
    Math.min(Math.max(smartSp * cfg.opportunity_spacing_multiplier, 0.06), 0.15);
  const crashSpacing = (oppSp) => Math.max(oppSp, 0.07);

  /* ---------- ladders (Strategy §12–14, §18.2) ---------- */

  const SMART_ALLOC = [0.33, 0.33, 0.34];
  const CRASH_ALLOC = [0.20, 0.25, 0.25, 0.30];

  function opportunityWeights(oscore) {
    const t = clamp((oscore - 70) / 10);
    return [0.10 * t, 0.15, 0.20, 0.25, 0.40 - 0.10 * t];
  }

  function invalidationPrice(anchor, spacing) {
    return anchor * (1 + Math.max(0.12, 2 * spacing));
  }

  function buildLadder(type, anchor, spacing, eligibleVnd, oscore) {
    let allocs;
    if (type === "SMART") allocs = SMART_ALLOC;
    else if (type === "OPPORTUNITY") allocs = opportunityWeights(oscore);
    else allocs = CRASH_ALLOC;
    const zones = allocs.map((a, i) => ({
      index: i,
      target_price: anchor * (1 - i * spacing),
      allocation_pct: a,
      target_vnd: eligibleVnd * a,
      status: "ACTIVE",
      filled_vnd: 0,
    }));
    return {
      type, anchor_price: anchor, spacing_pct: spacing,
      score_at_creation: oscore, eligible_capital_vnd: eligibleVnd,
      invalidation_price: invalidationPrice(anchor, spacing),
      status: "ACTIVE", zones,
      consecutive_invalidation_closes: 0,
    };
  }

  /* ---------- parity check vs Python ---------- */

  /** So OSCORE tính bằng JS với OSCORE do Python xuất trong seed. */
  function checkParity(seed, tol = 1e-6) {
    const ind = computeIndicators(seed.history);
    const byDay = new Map(ind.map((r) => [r.d, r]));
    const weights = (seed.config && seed.config.score_weights) || [50, 30, 20];
    let checked = 0, worst = 0, worstDay = null;
    const mismatches = [];
    for (const p of seed.parity || []) {
      const row = byDay.get(p.d);
      if (!row) continue;
      const s = scoreForDay(row, weights);
      const a = s.oscore, b = p.oscore;
      if (!Number.isFinite(a) && !Number.isFinite(b)) { checked++; continue; }
      if (!Number.isFinite(a) || !Number.isFinite(b)) {
        mismatches.push({ d: p.d, js: a, py: b, diff: NaN });
        continue;
      }
      const diff = Math.abs(a - b);
      checked++;
      if (diff > worst) { worst = diff; worstDay = p.d; }
      if (diff > tol) mismatches.push({ d: p.d, js: a, py: b, diff });
    }
    return { checked, worst, worstDay, mismatches, ok: mismatches.length === 0 };
  }

  return {
    clamp, rollMax, rollMean, rollPercentileOfLast, wilderRSI,
    computeIndicators, subFactors, factorScores, scoreForDay,
    smartUnlock, opportunityUnlock, scoreMultiplier,
    smartSpacing, opportunitySpacing, crashSpacing,
    opportunityWeights, invalidationPrice, buildLadder,
    checkParity, SUB_NAMES,
  };
})();

if (typeof module !== "undefined" && module.exports) module.exports = ENGINE;
