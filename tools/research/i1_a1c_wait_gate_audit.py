#!/usr/bin/env python3
"""Cold, no-newborn A1-C M11 gate, SHA-256 verified original cohort only."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import tempfile
import zipfile

try:
    from i1_a1c_td_full_audit import one as full_m11_attestation
except ImportError:  # historical local exported snapshot
    from i1_a1c_td_full_audit import _audit_one as full_m11_attestation
from i1_a1c_wait_gate import scan_gate, summarize, ROLES, SEEDS, ARMS
from i1_a1c_td_full import FROZEN_SOURCE_SHA, FROZEN_RUN_ID


def audited_one(item):
    base, name, record, role, seed, arm = item
    first = full_m11_attestation(item)
    raw = (base / (name+'.zip')).read_bytes()
    if len(raw)!=record['bytes'] or sha256(raw).hexdigest()!=record['sha256']:
        raise ValueError('original ZIP altered since full M11 attestation')
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        with tempfile.TemporaryDirectory(prefix='i1-a1c-static-wait-') as temp:
            folder=Path(temp)
            for filename in ('life.sqlite','life.sqlite-wal','life.sqlite-shm'):
                if filename in archive.namelist():
                    (folder/filename).write_bytes(archive.read(filename))
            with sqlite3.connect('file:'+str(folder/'life.sqlite')+'?mode=ro',uri=True) as db:
                db.execute('PRAGMA query_only=ON')
                db.execute('BEGIN')
                events=[json.loads(row[0])['causal_event'] for row in db.execute(
                    'SELECT canonical_bytes FROM causal_occurrence ORDER BY idx')]
            report=json.loads(archive.read('report.json'))
    life=report['life']
    if (life['audited']['journal_head']!=first['m11_head']
            or (report['role'],report['seed'],report['mode']) != (role,seed,arm)
            or report['source_commit'] != FROZEN_SOURCE_SHA):
        raise ValueError('native birth provenance differs after attestation')
    snapshot=scan_gate(events,mode=arm,food_setpoint=life['setpoints']['food'])
    return {'name':name,'role':role,'seed':seed,'mode':arm,
            'original_sha256':record['sha256'],'m11_head':first['m11_head'],
            **snapshot}


def audited_cohort(root, *, workers=1):
    if type(workers) is not int or workers not in (1,2,3,4):
        raise ValueError('only 1..4 M11 audit workers supported')
    root=Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError('original evidence root missing or symlinked')
    manifest=json.loads((root/'I1_ECO_A1C_EVIDENCE_MANIFEST.json').read_text())
    if (manifest.get('original_run_id')!=FROZEN_RUN_ID
            or manifest.get('original_source_sha')!=FROZEN_SOURCE_SHA
            or manifest.get('archived_independent_lives')!=48):
        raise ValueError('not the frozen A1-C confirmatory cohort')
    expected={f'a1c-{role}-s{seed}-{arm}':(role,seed,arm)
              for role in ROLES for seed in SEEDS for arm in ARMS}
    records=[r for r in manifest['original_zip_archives'] if r['name'].endswith('.zip')
             and r['name'][:-4] in expected]
    byname={r['name'][:-4]:r for r in records}
    if len(records)!=48 or len(byname)!=48 or set(byname)!=set(expected):
        raise ValueError('incomplete, altered or duplicated original archive list')
    tasks=[(root,name,byname[name],*row) for name,row in sorted(expected.items())]
    if workers==1:
        lives=[audited_one(x) for x in tasks]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            lives=list(pool.map(audited_one,tasks))
    report=summarize(lives)
    report['lives']=lives
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--workers',type=int,choices=(1,2,3,4),default=1)
    args=parser.parse_args()
    result=audited_cohort(args.root,workers=args.workers)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='lives'},sort_keys=True))

if __name__=='__main__':
    main()
