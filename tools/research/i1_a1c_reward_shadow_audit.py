#!/usr/bin/env python3
"""Read-only frozen A1-C reward sensitivity on 48 audited M11 archives.

Never execute the I1 runtime, resume an individual, or overwrite an archive.
Original source SHA and all 48 ZIP SHA-256 values are mandatory. This is a
*static fixed-action-tape Q sensitivity*, NOT a new-life counterfactual.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import sqlite3
import tempfile
import zipfile
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
from statistics import mean

from i1_a1c_reward_shadow import analyze_life, FROZEN_RUN_ID, FROZEN_SOURCE_SHA

# Pinned SHA of the independent manifest, checked BEFORE reading its ZIP list.
ORIGINAL_MANIFEST_SHA256 = '01ac08f8a084dff682256fca721cb6ff0e02b9d085207f088151b76a5e44bfca'


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def _audited_zip(root, name, record):
    """Independently reattest the exact original M11 ZIP and its native chain."""
    path = root / (name + '.zip')
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing or symlinked original A1-C ZIP')
    contents = path.read_bytes()
    if (len(contents) != record['bytes'] or
            sha256(contents).hexdigest() != record['sha256']):
        raise ValueError('mismatched original A1-C ZIP SHA-256')
    with zipfile.ZipFile(path) as archive:
        members = archive.namelist()
        if (not {'life.sqlite', 'report.json'}.issubset(members)
                or len(members) != len(set(members))
                or any('/' in name or '\\' in name or '..' in name
                       for name in members)):
            raise ValueError('unsafe or incomplete original M11 ZIP')
        report = json.loads(archive.read('report.json'))
        life = report['life']
        if (report.get('source_commit') != FROZEN_SOURCE_SHA
                or life.get('source_commit') != FROZEN_SOURCE_SHA
                or life.get('identity') != report.get('identity')
                or report.get('verdict') != 'MEASUREMENT_FRAGMENT_READY'
                or life.get('audited', {}).get('generation') != 48):
            raise ValueError('untrusted source provenance')
        with tempfile.TemporaryDirectory(prefix='i1-a1c-reward-cold-') as tdir:
            work = Path(tdir)
            for filename in ('life.sqlite', 'life.sqlite-wal', 'life.sqlite-shm'):
                if filename in members:
                    (work / filename).write_bytes(archive.read(filename))
            with sqlite3.connect('file:' + str(work/'life.sqlite') + '?mode=ro',
                                 uri=True) as conn:
                conn.execute('PRAGMA query_only=ON')
                conn.execute('BEGIN')
                state = conn.execute('SELECT generation,journal_count,journal_head '
                                     'FROM life_current WHERE slot=1').fetchone()
                rows = conn.execute('SELECT idx,event_id,previous_hash,event_hash,'
                                    'canonical_bytes FROM causal_occurrence '
                                    'ORDER BY idx').fetchall()
    if (state != (48, life['audited']['journal_count'],
                  life['audited']['journal_head'])
            or len(rows) != state[1]):
        raise ValueError('M11 current state/receipt mismatch')
    previous = '00' * 32
    events = []
    for index, eid, parent, digest, raw in rows:
        occurrence = json.loads(raw)
        if (index != len(events) or parent != previous
                or occurrence.get('index') != index
                or occurrence.get('event_id') != eid
                or occurrence.get('previous_hash') != parent
                or occurrence.get('event_hash') != digest
                or _canonical(occurrence) != raw):
            raise ValueError('noncanonical M11 occurrence')
        expected = sha256(bytes.fromhex(previous) + _canonical({
            'event_id': eid, 'causal_event': occurrence['causal_event']
        })).hexdigest()
        if expected != digest:
            raise ValueError('altered M11 hash chain')
        previous = digest
        events.append(occurrence['causal_event'])
    if previous != state[2]:
        raise ValueError('M11 final head mismatch')
    return report, events

ROLES = ('native', 'reversed')
SEEDS = tuple(range(101,113))
MODES = ('canonical','td_read_masked')


def one(item):
    root, name, record, role, seed, mode = item
    report, events = _audited_zip(root, name, record)
    life = report['life']
    if ((report.get('role'),report.get('seed'),report.get('mode')) !=
            (role,seed,mode)
            or (life.get('role'), life.get('seed'), life.get('mode')) !=
            (role,seed,mode)
            or report.get('source_commit') != FROZEN_SOURCE_SHA
            or report.get('verdict') != 'MEASUREMENT_FRAGMENT_READY'):
        raise ValueError('frozen independent birth/source mismatch')
    return analyze_life(events,life)


def summarize(rows):
    if type(rows) is not list or len(rows) != 48:
        raise ValueError('cannot select only successful A1-C lives')
    ids = [(row['role'],row['seed'],row['mode']) for row in rows]
    expected = [(r,s,m) for r in ROLES for s in SEEDS for m in MODES]
    if len(set(ids)) != 48 or set(ids) != set(expected):
        raise ValueError('duplicated or missing A1-C temperament block')
    if (len({x.get('identity') for x in rows}) != 48 or
            len({x.get('m11_final_head') for x in rows}) != 48 or
            any(x.get('scope') != 'POSTHOC_FIXED_ACTION_TAPE_NO_BEHAVIORAL_COUNTERFACTUAL'
                or x.get('a1c_status') != 'NO_GO'
                or x.get('L3') != 'NOT_ESTABLISHED' for x in rows)):
        raise ValueError('invalid distinct source identities or epistemic scope')
    by_action=defaultdict(lambda:Counter())
    by_role={}
    affected=set()
    witnesses=[]
    for row in rows:
        role,seed,mode=row['role'],row['seed'],row['mode']
        for step in row['action_rewards']:
            c=by_action[step['action']]
            c['observations']+=1
            n,s=step['native_reward'],step['shadow_reward']
            c['native_positive']+=int(n>0)
            c['shadow_positive']+=int(s>0)
            c['native_positive_shadow_nonpositive']+=int(n>0 and s<=0)
            c['native_negative_shadow_nonnegative']+=int(n<0 and s>=0)
            c['both_negative']+=int(n<0 and s<0)
            c['native_reward_total']+=n
            c['deficit_only_reward_total']+=s
            c['surplus_reward_total']+=step['surplus_reward']
            for need, value in step['surplus_by_need'].items():
                c['surplus_'+need+'_total']+=value
        if mode=='canonical':
            key=role+'/canonical'
            subset=by_role.setdefault(key,Counter())
            subset['lives']+=1
            subset['wait_q_only_wins']+=len(row['native_q_only_wait_winners'])
            subset['shadow_wait_Q_nonpositive_at_same_original_cycle']+=sum(
                w['shadow_nonpositive'] for w in row['native_q_only_wait_winners'])
            if any(w['shadow_nonpositive'] for w in row['native_q_only_wait_winners']):
                affected.add(seed)
            for w in row['native_q_only_wait_winners']:
                witnesses.append({'role':role,'seed':seed,**w})
    by_seed={str(seed):{
        'native':next(x for x in rows if x['role']=='native' and x['seed']==seed and x['mode']=='canonical')['count_q_only_wait_winners'],
        'reversed':next(x for x in rows if x['role']=='reversed' and x['seed']==seed and x['mode']=='canonical')['count_q_only_wait_winners'],
    } for seed in SEEDS}
    by_seed_shadow = {
        str(seed): {
            role: sum(w['shadow_nonpositive'] for w in witnesses
                      if w['seed'] == seed and w['role'] == role)
            for role in ROLES
        } for seed in SEEDS
    }
    total_updates=sum(x['native_td_updates_verified'] for x in rows)
    total_native_q_checks=sum(x['native_replay_q_checked'] for x in rows)
    return {
        'schema':'individual-zero-i1-a1c-fixed-reward-tape-shadow/1',
        'original_source_sha':FROZEN_SOURCE_SHA,
        'original_run_id':FROZEN_RUN_ID,
        'audited_original_lives':len(rows),
        'paired_worlds':24,
        'independent_birth_temperament_blocks':12,
        'native_td_updates_reverified':total_updates,
        'native_stage8_q_values_reverified':total_native_q_checks,
        'original_wait_q_only_winner_cycles':len(witnesses),
        'shadow_Q_nonpositive_at_same_original_cycle':sum(x['shadow_nonpositive'] for x in witnesses),
        'shadow_Q_positive_at_same_original_cycle':sum(not x['shadow_nonpositive'] for x in witnesses),
        'temperament_blocks_with_shadow_sign_change':sorted(affected),
        'by_action_repeated_steps':{k:dict(v) for k,v in sorted(by_action.items())},
        'by_role_canonical':{k:dict(v) for k,v in by_role.items()},
        'by_seed_canonical_Q_only_original':by_seed,
        'by_seed_shadow_wait_Q_nonpositive':by_seed_shadow,
        'witnesses':witnesses,
        'lives':rows,
        'scope':'POSTHOC_FIXED_ACTION_TAPE_NO_BEHAVIORAL_COUNTERFACTUAL',
        'no_new_births':True,
        'cohort_A1C':'NO_GO',
        'L3':'NOT_ESTABLISHED',
    }


def audit(root, *, workers=1):
    root=Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('missing or symlinked original research root')
    if type(workers) is not int or workers not in (1,2,3,4):
        raise ValueError('worker count out of range')
    manifest_raw = (root/'I1_ECO_A1C_EVIDENCE_MANIFEST.json').read_bytes()
    if sha256(manifest_raw).hexdigest() != ORIGINAL_MANIFEST_SHA256:
        raise ValueError('original A1-C manifest altered')
    manifest=json.loads(manifest_raw)
    if (manifest.get('original_run_id') != FROZEN_RUN_ID
            or manifest.get('original_source_sha') != FROZEN_SOURCE_SHA
            or manifest.get('archived_independent_lives') != 48):
        raise ValueError('non-original run identity')
    expected={f'a1c-{r}-s{s}-{m}':(r,s,m) for r in ROLES for s in SEEDS for m in MODES}
    registered=[r for r in manifest['original_zip_archives']
                if r['name'].endswith('.zip') and r['name'][:-4] in expected]
    originals={r['name'][:-4]:r for r in registered}
    if len(originals)!=48 or len(registered)!=48 or set(originals)!=set(expected):
        raise ValueError('incomplete original A1-C cohort or duplicated ZIP')
    tasks=[(root,name,originals[name],*expected[name]) for name in sorted(expected)]
    if workers==1:
        rows=[one(item) for item in tasks]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows=list(pool.map(one,tasks))
    return summarize(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--workers',type=int,default=1)
    a=p.parse_args()
    result=audit(a.root,workers=a.workers)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('lives','witnesses')},
                     sort_keys=True))


if __name__=='__main__':
    main()
