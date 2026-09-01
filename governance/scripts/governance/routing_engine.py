#!/usr/bin/env python3
import argparse, json
TIERS=['A','B','C','D']; MODELS={'A':'Haiku','B':'Sonnet','C':'Opus','D':'Fable'}
EFF=['low','medium','high','xhigh','max']

# GOVDEF-001: the weighted sums below (weights .25/.20/.15 for model_score,
# .20/.20/.15/.25 for effort_score) are all defined to exactly 2 decimal
# places, multiplied by integer inputs (0-4). The true mathematical value of
# any weighted sum therefore always has at most 2 significant decimal digits
# (e.g. 2.00, 2.60, 1.95) — it can never be irrational or need more precision
# than that. IEEE-754 binary floats cannot represent most such decimals
# exactly, so summing them can leave residual representation noise on the
# order of 1e-15 to 1e-16 (e.g. 1.9999999999999998 instead of the true 2.0).
# That noise is more than 10 orders of magnitude below the 3rd decimal place,
# so rounding to SCORE_DECIMALS=3 discards only the noise and never the true
# value — it is not a tuned epsilon and not specific to any input combination.
# Comparisons against the integer/decimal tier and effort boundaries MUST use
# this same rounded value that is also shown to the reader, so a score that
# displays as exactly 2.0 can never be routed as if it were below 2.0.
SCORE_DECIMALS=3

def clamp(v):
    if not isinstance(v,int) or not 0 <= v <= 4: raise ValueError('all routing scores must be integers 0-4')
    return v

def tier_from_score(s): return 'A' if s < 1 else 'B' if s < 2 else 'C' if s < 3 else 'D'
def effort_from_score(s): return 'low' if s < .8 else 'medium' if s < 1.6 else 'high' if s < 2.4 else 'xhigh' if s < 3.2 else 'max'
def max_tier(a,b): return TIERS[max(TIERS.index(a),TIERS.index(b))]
def max_eff(a,b): return EFF[max(EFF.index(a),EFF.index(b))]

def route(D,R,B,A,X,U,V,H,C,F,categories=(), expected_horizon=None):
    vals=[D,R,B,A,X,U,V,H,C,F]; [clamp(v) for v in vals]
    cats={c.strip().lower() for c in categories if c.strip() and c.strip().lower()!='none'}
    ms=round(.25*D+.25*R+.20*B+.15*A+.15*X, SCORE_DECIMALS)
    base=tier_from_score(ms); tier=base; mf=[]
    if A>=3 and X>=3: tier=max_tier(tier,'C'); mf.append('cognitive:A>=3&X>=3')
    if A==4 and X==4 and (D>=3 or (expected_horizon is not None and expected_horizon>=3)):
        tier=max_tier(tier,'D'); mf.append('cognitive:extreme_ambiguity_cross_system')
    if D>=4 and X>=3: tier=max_tier(tier,'C'); mf.append('cognitive:D>=4&X>=3')
    c_floor={'security','auth','authentication','authorization','destructive_migration','payroll_kpi','payroll','kpi','accounting_financial','accounting','financial'}
    if cats & c_floor: tier=max_tier(tier,'C'); mf.append('safety_business:min_C')
    d_floor={'active_security_incident','long_horizon_orchestration'}
    if cats & d_floor: tier=max_tier(tier,'D'); mf.append('frontier:min_D')
    es=round(.20*U+.20*V+.20*H+.15*C+.25*F, SCORE_DECIMALS)
    effort=effort_from_score(es); ef=[]
    if cats & c_floor: effort=max_eff(effort,'high'); ef.append('safety_business:min_high')
    if cats & {'active_security_incident','irreversible_no_rollback','material_sensitive_data_corruption'}:
        effort=max_eff(effort,'xhigh'); ef.append('critical:min_xhigh')
    warnings=[]
    if tier in {'C','D'} and effort=='low': warnings.append('high_tier_low_effort_recheck')
    if tier=='D' and effort in {'low','medium'}: warnings.append('tier_D_low_effort_requires_evidence')
    return {'routing_status':'ROUTED','model_score':ms,'base_tier':base,'tier':tier,'model':MODELS[tier],
            'effort_score':es,'effort':effort,'model_floors':mf or ['none'],'effort_floors':ef or ['none'],'warnings':warnings or ['none']}

def main():
    p=argparse.ArgumentParser(description='Deterministic Model + Effort router (all scores are integers 0-4).')
    for n in 'DRBAXUVHCF': p.add_argument(f'--{n.lower()}',type=int,required=True)
    p.add_argument('--category',action='append',default=[]); p.add_argument('--expected-horizon',type=int)
    a=p.parse_args(); print(json.dumps(route(a.d,a.r,a.b,a.a,a.x,a.u,a.v,a.h,a.c,a.f,a.category,a.expected_horizon),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
