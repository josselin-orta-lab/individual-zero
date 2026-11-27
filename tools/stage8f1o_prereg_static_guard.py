"""F1O static preregistration + engine-free arithmetic reference, ZERO births.

Nothing here authorizes native work or reads a scientific result. Reference
calculations are tested on synthetic numbers only until a separate audited
producer and independent cold reader exist. All native funding is future work.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / 'docs/research/studies/stage8f1-paid-microdecision'
GRID = STUDY / 'STAGE8F1O_PERSONAL_ERROR_FORECAST_PREEXPOSURE_GRID_2026-11-27.json'
PROTOCOL = STUDY / 'STAGE8F1O_PERSONAL_ERROR_FORECAST_PREEXPOSURE_2026-11-27.md'
GRID_BLOB = '5f9781517cca9c72187073c0db58672772f744dd'
PROTOCOL_BLOB = 'a59207d71c7bc7f9b95ff887104e40541124c68a'
BASE = '2980e435896bd9bd3946dd42cf838a6aec028fc7'
ROOT_IDS = tuple(f'O{i:02d}' for i in range(1, 49))
SEEDS = tuple(range(202611279901, 202611279949))
ACQUIRE = tuple(range(1, 9))
VALIDATE = tuple(range(9, 25))
EPS = 1e-10
GAIN = 0.5
POSITIVE = 'LOCAL_T24_ONE_STEP_PERSONAL_ERROR_FORECAST_ACCURACY_GAIN'
NEGATIVE = 'NO_REPRODUCIBLE_LOCAL_T24_ONE_STEP_PERSONAL_ERROR_FORECAST_ACCURACY_GAIN'
INCONCLUSIVE = 'INCONCLUSIVE_F1O_PROVENANCE_FUNDING_OR_COMPLETENESS'


def demand(condition, message):
    if not condition:
        raise ValueError('F1O PREEXPOSURE: ' + message)


def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def exact(path, expected):
    demand(path.is_file() and blob(path.read_bytes()) == expected,
           'Git blob changed: '+str(path.relative_to(ROOT)))


def prior_seeds(value):
    if isinstance(value, dict):
        for k, v in value.items():
            if 'seed' in k and type(v) is int:
                yield v
            yield from prior_seeds(v)
    elif isinstance(value, list):
        for v in value:
            yield from prior_seeds(v)


def verify_grid(g):
    """A structural check supplements, never replaces, exact byte pins."""
    demand(g['baseline_main'] == BASE and g['schema'] ==
           'i3-stage8f1o-prospective-personal-error-point-forecast-T24/v0',
           'source or schema altered')
    demand(g['phase'] == 'PREEXPOSURE_ONLY_NO_F1O_WORLD_STEP' and
           g['exposure'] == {'scientific_births':0, 'scientific_world_steps':0,
              'scientific_dispatch_authorized':False,
              'native_producer_implemented':False,'results_available':False},
           'exposure gate altered')
    demand(tuple(g['acquisition_ticks']) == ACQUIRE and
           tuple(g['validation_ticks']) == VALIDATE and g['horizon'] == 24,
           'acquisition or validation horizon altered')
    origins = g['origins']
    demand(tuple(r['id'] for r in origins) == ROOT_IDS and
           tuple(r['seed'] for r in origins) == SEEDS, 'root allocation altered')
    ecologies = g['ecologies']
    ids = [e['id'] for e in ecologies]
    combos = {(e['factors']['water_access'], e['factors']['water_gain'],
               e['factors']['food_effect']) for e in ecologies}
    demand(len(ids)==len(set(ids))==8 and combos=={
        (a,w,f) for a in ('adjacent','diagonal') for w in ('low','high')
        for f in ('safe','bitter')}, 'ecology factorial allocation changed')
    demand(all(r['ecology']==ids[i//6] and r['body']==g['body_templates'][i%6]
               for i,r in enumerate(origins)), 'six origins per ecology changed')
    a,b = g['dev_allocations']['A'],g['dev_allocations']['B']
    dev=a+b
    demand(len(a)==len(b)==8 and len({x['id'] for x in dev})==16 and
           len({x['seed'] for x in dev})==16 and
           not ({x['seed'] for x in dev}&set(SEEDS)) and
           all(x['id'].startswith('DEV_O') for x in dev), 'DEV identities overlap')
    mem, p, s = g['memory'],g['primary'],g['scope']
    demand(mem['capacity_records']==8 and mem['correction_gain']==GAIN and
           mem['freeze_after_tick']==8 and p['epsilon']==EPS and
           p['min_global_gain']==.10 and p['min_positive_roots']==32 and
           p['min_positive_ecologies']==6 and p['positive']==POSITIVE and
           p['negative']==NEGATIVE and p['inconclusive']==INCONCLUSIVE,
           'correction or prospective decision threshold altered')
    demand(g['forecast_pair']['same_admitted_action_and_native_target'] is True
           and g['forecast_pair']['no_output_to_policy'] is True
           and g['forecast_pair']['native_learning_continues'] is True
           and g['forecast_pair']['prepay_each_before_capture']=={
               'cycles':1,'simulated_steps':1,'memory_items':'3+n','replays':0}
           and s['calibration_only'] is True and
           s['motor_or_adaptation_claim_allowed'] is False and
           s['all_48_complete_funded_pairs_and_shams_required'] is True and
           s['expected_original_gzip_count']==96 and
           s['explicit_new_owner_exposure_authorization_required'] is True,
           'paid projection or scope altered')
    demand(len(g['pins'])==11 and len(g['prior_grids'])==6,
           'historical pin set incomplete')


def check_files():
    exact(GRID,GRID_BLOB)
    exact(PROTOCOL,PROTOCOL_BLOB)
    g=json.loads(GRID.read_bytes())
    verify_grid(g)
    occupied=set()
    for p,h in {**g['pins'],**g['prior_grids']}.items():
        exact(ROOT/p,h)
        if p in g['prior_grids']:
            occupied.update(prior_seeds(json.loads((ROOT/p).read_bytes())))
    fresh=set(SEEDS)|{r['seed'] for a in g['dev_allocations'].values() for r in a}
    demand(not (fresh&occupied),'known historical seed collision')
    # Search all tracked text in the actual baseline Git tree, not the current
    # files that contain our new reservation. Full historical dynamic allocation
    # audit is a separate explicit prerequisite of the future scientific shot.
    scan=subprocess.run(['git','grep','-I','-l','-F','202611279',BASE,'--','.'],
                        cwd=ROOT,capture_output=True,text=True,check=False)
    demand(scan.returncode==1 and not scan.stdout.strip(),
           'reserved namespace present in baseline or Git baseline unavailable: '
           +scan.stdout[:400]+scan.stderr[:400])
    return g,len(occupied)


def vector(v, lo, hi):
    demand(type(v) in (list,tuple) and len(v)==5 and all(
        type(x) in (float,int) and math.isfinite(x) and lo<=x<=hi for x in v),
        'invalid five-channel vector')
    return tuple(float(x) for x in v)


def forecast_work(n):
    """Registered logical blocks, NOT payment authority."""
    demand(type(n) is int and 0<=n<=8,'memory outside eight records')
    return {'cycles':1,'simulated_steps':1,'memory_items':3+n,'replays':0}


def native_mean_reference(stats, key):
    """Read all three native candidates and select normal EffectsModel fallback."""
    demand(type(key) is tuple and len(key) in (1,2),'invalid action key')
    candidates=[stats.get(k) for k in (key,(key[0],None),('*',))]
    for x in candidates:
        if x is not None and x[0]>0:
            return vector(x[1],-100,100)
    return (0.,)*5


def choose_record(records, key, body, t):
    """Pure reference for an already paid read; no policy state or future data."""
    body=vector(body,0,100)
    demand(type(t) is int and 1<=t<=24 and len(records)==min(t-1,8),
           'wrong prior source count')
    best=None
    best_rank=None
    for idx,r in enumerate(records,1):
        demand(set(r)=={'t','key','body','error'} and r['t']==idx and idx<t,
               'future, duplicate or missing acquisition trace')
        b=vector(r['body'],0,100)
        err=vector(r['error'],-100,100)
        if tuple(r['key'])==tuple(key):
            rank=(math.fsum(abs(x-y) for x,y in zip(body,b)),-idx)
            if best_rank is None or rank<best_rank:
                best_rank=rank
                best=(idx,err)
    return best if best is not None else (None,(0.,)*5)


def point_forecast(body,mean,error,mode):
    b=vector(body,0,100); m=vector(mean,-100,100); e=vector(error,-100,100)
    demand(mode in ('corrected','masked'),'unregistered readout')
    applied=e if mode=='corrected' else (0.,)*5
    return tuple(min(100.,max(0.,x+y+GAIN*z)) for x,y,z in zip(b,m,applied))


def mae(prediction,target):
    p=vector(prediction,0,100); y=vector(target,0,100)
    return math.fsum(abs(a-b) for a,b in zip(p,y))/5.


def reference_verdict(grid, rows):
    """Arithmetic only. Caller must independently prove every native quality gate.

    Unit tests provide explicitly synthetic arrays. This function never certifies
    source quality, authors an actual outcome, or launches a cohort.
    """
    try:
        demand(type(rows) is list and len(rows)==48,'incomplete root count')
        root_gains=[]
        by_ecology={e['id']:[] for e in grid['ecologies']}
        for r,o in zip(rows,grid['origins']):
            demand(r['id']==o['id'] and r['ecology']==o['ecology'] and
                   r['independent_quality_verified'] is True and
                   tuple(x['t'] for x in r['pairs'])==VALIDATE,
                   'incomplete, reordered or invalid audited source')
            gain=math.fsum(mae(x['masked'],x['target'])-
                           mae(x['corrected'],x['target']) for x in r['pairs'])/16
            root_gains.append(gain)
            by_ecology[o['ecology']].append(gain)
        means={k:math.fsum(v)/6 for k,v in by_ecology.items()}
        overall=math.fsum(root_gains)/48
        positive=sum(x>EPS for x in root_gains)
        positive_ecologies=sum(x>EPS for x in means.values())
        ok=overall>=.10 and positive>=32 and positive_ecologies>=6
        return {'verdict':POSITIVE if ok else NEGATIVE,
                'global_gain':overall,'positive_roots':positive,
                'negative_roots':sum(x < -EPS for x in root_gains),
                'equal_roots':sum(abs(x)<=EPS for x in root_gains),
                'positive_ecologies':positive_ecologies,
                'root_gains':root_gains,'ecology_gains':means,
                'motor_or_adaptation_claim_allowed':False}
    except (ValueError,TypeError,KeyError,AttributeError,IndexError,OverflowError):
        return {'verdict':INCONCLUSIVE,'motor_or_adaptation_claim_allowed':False}


def main():
    g,n=check_files()
    print(json.dumps({'status':'F1O_PREREG_STATIC_ONLY_NO_EXPOSURE',
       'protocol_blob':PROTOCOL_BLOB,'grid_blob':GRID_BLOB,
       'prior_literal_seeds_checked':n,'scientific_roots':len(g['origins']),
       'future_validation_pairs':48*16,'future_original_gzips':96,
       'native_world_steps':0,'scientific_dispatch_authorized':False,
       'scientific_result_available':False},sort_keys=True))


if __name__=='__main__':
    main()
