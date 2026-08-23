#!/usr/bin/env python3
import argparse, json
TIERS=['A','B','C','D']; MODELS={'A':'Haiku','B':'Sonnet','C':'Opus','D':'Fable'}
EFF=['low','medium','high','xhigh','max']

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
    ms=.25*D+.25*R+.20*B+.15*A+.15*X
    base=tier_from_score(ms); tier=base; mf=[]
    if A>=3 and X>=3: tier=max_tier(tier,'C'); mf.append('cognitive:A>=3&X>=3')
    if A==4 and X==4 and (D>=3 or (expected_horizon is not None and expected_horizon>=3)):
        tier=max_tier(tier,'D'); mf.append('cognitive:extreme_ambiguity_cross_system')
    if D>=4 and X>=3: tier=max_tier(tier,'C'); mf.append('cognitive:D>=4&X>=3')
    c_floor={'security','auth','authentication','authorization','destructive_migration','payroll_kpi','payroll','kpi','accounting_financial','accounting','financial'}
    if cats & c_floor: tier=max_tier(tier,'C'); mf.append('safety_business:min_C')
    d_floor={'active_security_incident','long_horizon_orchestration'}
    if cats & d_floor: tier=max_tier(tier,'D'); mf.append('frontier:min_D')
    es=.20*U+.20*V+.20*H+.15*C+.25*F
    effort=effort_from_score(es); ef=[]
    if cats & c_floor: effort=max_eff(effort,'high'); ef.append('safety_business:min_high')
    if cats & {'active_security_incident','irreversible_no_rollback','material_sensitive_data_corruption'}:
        effort=max_eff(effort,'xhigh'); ef.append('critical:min_xhigh')
    warnings=[]
    if tier in {'C','D'} and effort=='low': warnings.append('high_tier_low_effort_recheck')
    if tier=='D' and effort in {'low','medium'}: warnings.append('tier_D_low_effort_requires_evidence')
    return {'routing_status':'ROUTED','model_score':round(ms,3),'base_tier':base,'tier':tier,'model':MODELS[tier],
            'effort_score':round(es,3),'effort':effort,'model_floors':mf or ['none'],'effort_floors':ef or ['none'],'warnings':warnings or ['none']}

def main():
    p=argparse.ArgumentParser(description='Deterministic Model + Effort router (all scores are integers 0-4).')
    for n in 'DRBAXUVHCF': p.add_argument(f'--{n.lower()}',type=int,required=True)
    p.add_argument('--category',action='append',default=[]); p.add_argument('--expected-horizon',type=int)
    a=p.parse_args(); print(json.dumps(route(a.d,a.r,a.b,a.a,a.x,a.u,a.v,a.h,a.c,a.f,a.category,a.expected_horizon),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
