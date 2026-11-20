"""Cold read-only Stage8-E3A motor/cost/physiology decomposition.

No native runner, no World and no genome mutation imports. Accepts ONLY the
closed Stage8-E2 single science root, independently completed original audits,
and each of the 36,864 ORIGINAL G2 gzip bytes. Every identity and both gzip
hashes must match archived MANIFEST.json before descriptive aggregation.

This is exploratory POSTHOC diagnosis; it never issues a confirmatory test,
scientific promotion or an individual-level p-value.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import gzip
from hashlib import sha256
import io
import json
import math
from pathlib import Path
import re
import tarfile

SCHEMA = 'i3-stage8e3a-original-g2-motor-cost-readonly/v0'
RUN_ID = 44637950471
ENGINE_HEAD = '03faff4b9c194a5288b92e394f6a75cbe62cd095'
ENGINE_SHA = 'e816ff5f5ee679253fc57f6e9ee79d21dff73dd72d6adf3c7f55ba7aa0f3e7f6'
SCIENCE_HEAD = '404bdf6c844c048985659d6c4d03827ffb19d878'
SCIENCE_RESULT_SHA = '18ad42a1e68a0a7c1c2390bd397ee90e7872bdf398f0f5bac37d06bbfff8af45'
G2_MANIFEST_SHA = '61eb74a1f429c2f9189ee13da5c52593776d2b6f9d2b2d8ac41bfdea31a6ba00'
G2_SHA = 'stage8e2-science-G2-original-gzip-44637950471'
PROTOCOL = 'i3-stage8e2-gamma-factorial-P1.3-funded-v2-technical/v0'
COLD_PASS = 'ALL_64512_NATIVE_ORIGINAL_GZIP_REAUDITED_NO_SCIENCE'
ORIGINALS = 36864
ARM_LIVES = 144
ARMS = ('S_sham', 'M_sham', 'S_swap', 'M_swap')
FAMILIES = ('stable', 'depletion', 'pulse')
ACTIONS = ('se_deplacer', 'collecter', 'manger', 'boire', 'dormir', 'attendre', 'physical_inactivity')
CHANNELS = ('energy', 'food', 'water', 'integrity', 'vigilance')
WORK = ('cycles', 'simulated_steps', 'memory_items', 'replays')
CURRENCIES = ('energy', 'vigilance')
BILLS = ('requested', 'paid', 'unpaid')
CORE = ('t', 'action', 'param', 'option', 'body', 'pos', 'dead')
EXTRA = ('cognitive_work', 'cognitive_accounting', 'funding_phases', 'info')
NAME = re.compile(r'life-[0-9]{3,5}\.json\.gz\Z')
HEX = re.compile(r'[0-9a-f]{64}\Z')
MAX_PACKED = 2_000_000
MAX_DECODED = 2_000_000
TOL = 1e-7


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf8')


def digest(obj):
    return sha256(canonical(obj)).hexdigest()


def positive_int(x, *, allow_zero=False):
    return type(x) is int and x >= (0 if allow_zero else 1)


def num(x):
    return type(x) in (int, float) and math.isfinite(x)


def close(a, b):
    return num(a) and num(b) and math.isclose(a, b, abs_tol=TOL, rel_tol=1e-9)


def unpack_gzip(packed):
    if len(packed) > MAX_PACKED:
        raise ValueError('oversized compressed original')
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as gz:
        raw = gz.read(MAX_DECODED+1)
        if len(raw) > MAX_DECODED or gz.read(1):
            raise ValueError('oversized decompressed original')
    return raw


def native_trace_chains(life):
    """Independent source-exact trace/evidence verification, no physical replay."""
    trace = life['trace']
    if type(trace) is not list or len(trace) != life['steps_lived']:
        raise ValueError('missing first-person steps')
    head = sha256(json.dumps([life['genome'], life['world'], life['life_seed'],
                              life['horizon']], separators=(',', ':')).encode()).hexdigest()
    ev = life['manifest_id']
    for i, step in enumerate(trace):
        if type(step) is not dict or set(step) != set(CORE+EXTRA):
            raise ValueError('wrong original trace record schema')
        if step['t'] != i+1:
            raise ValueError('broken native World tick sequence')
        core = {key: step[key] for key in CORE}
        head = sha256((head + json.dumps(core, sort_keys=True,
                            separators=(',', ':'))).encode()).hexdigest()
        ev = digest({'previous':ev, 'record':core,
                     'work':step['cognitive_work'],
                     'accounting':step['cognitive_accounting'],
                     'funding_phases':step['funding_phases']})
    ev = digest({'previous':ev, 'terminal':life['terminal'],
                 'accounting':life['cognitive_accounting']})
    if head != life['trace_head'] or ev != life['evidence_head']:
        raise ValueError('original bodily/paid cognitive evidence chain mismatch')


def read_manifest(metadata_tar):
    root = Path(metadata_tar)
    if root.is_symlink() or not root.is_file():
        raise PermissionError('missing pristine original metadata TAR')
    filenames = {
        'native-originals/PHYSICAL_G2/G2/MANIFEST.json': None,
        'native-originals/PHYSICAL_G2/G2/MANIFEST.sha256': None,
    }
    with tarfile.open(root, 'r|') as tar:
        for item in tar:
            name = item.name.lstrip('./')
            if name in filenames:
                if filenames[name] is not None or not item.isfile() or item.size > 64_000_000:
                    raise ValueError('duplicated or malformed G2 manifest')
                filenames[name] = tar.extractfile(item).read()
    if any(v is None for v in filenames.values()):
        raise ValueError('original G2 manifest missing from science metadata')
    body = filenames['native-originals/PHYSICAL_G2/G2/MANIFEST.json']
    seal = filenames['native-originals/PHYSICAL_G2/G2/MANIFEST.sha256']
    if sha256(body).hexdigest() != G2_MANIFEST_SHA or seal.strip().decode() != G2_MANIFEST_SHA:
        raise ValueError('G2 published original manifest hash drifted')
    manifest = json.loads(body)
    if (type(manifest) is not dict or manifest.get('schema') != 'i3-two-phase-panel/v1'
            or manifest.get('status') != 'GENERATED' or manifest.get('failure') is not None
            or manifest.get('planned') != ORIGINALS or manifest.get('generated') != ORIGINALS
            or type(manifest.get('files')) is not list or len(manifest['files']) != ORIGINALS):
        raise ValueError('not all original G2 lives published')
    unique_keys = set()
    seen_seeds = set()
    worlds = {}
    indexed = {}
    for i, row in enumerate(manifest['files']):
        name = f'life-{i:03d}.json.gz'
        if type(row) is not dict or set(row) != {'file', 'identity', 'sha256', 'uncompressed_sha256'}:
            raise ValueError('foreign original manifest row')
        if row['file'] != name or not NAME.fullmatch(name) or any(
            type(row[k]) is not str or not HEX.fullmatch(row[k])
            for k in ('sha256', 'uncompressed_sha256')
        ):
            raise ValueError('bad original file naming/hash')
        idn = row['identity']
        key = tuple(idn.get(k) for k in ('population','generation','arm','slot','family','repeat'))
        if (type(idn) is not dict or set(idn) != {
                'population','generation','arm','slot','family','repeat',
                'world_seed','world_sha256','life_seed','genome_sha256','source_sha256'
            } or type(idn['population']) is not int or not 0 <= idn['population'] < 64
            or idn['generation'] != 2 or idn['arm'] not in ARMS
            or type(idn['slot']) is not int or not 0 <= idn['slot'] < 24
            or idn['family'] not in FAMILIES or type(idn['repeat']) is not int
            or idn['repeat'] not in (0,1) or idn['source_sha256'] != ENGINE_SHA
            or key in unique_keys or type(idn['life_seed']) is not int
            or idn['life_seed'] in seen_seeds
            or not HEX.fullmatch(idn['genome_sha256'])
            or not HEX.fullmatch(idn['world_sha256'])):
            raise ValueError('missing, duplicate or foreign G2 native identity')
        unique_keys.add(key)
        seen_seeds.add(idn['life_seed'])
        wk = (idn['population'],idn['family'],idn['repeat'])
        w = (idn['world_seed'], idn['world_sha256'])
        if wk in worlds and worlds[wk] != w:
            raise ValueError('G2 worlds no longer arm-matched')
        worlds[wk] = w
        indexed[name] = row
    if (len(unique_keys) != ORIGINALS or len(seen_seeds) != ORIGINALS
        or len(worlds) != 384 or len(set(worlds.values())) != 384):
        raise ValueError('original G2 factorial schedule is incomplete')
    return indexed


def verify_prior_science(science_final, cold_audit, independent):
    paths = [Path(x) for x in (science_final, cold_audit, independent)]
    if any(x.is_symlink() or not x.is_file() for x in paths):
        raise PermissionError('three original historical science receipts required')
    raw = paths[0].read_bytes()
    if sha256(raw).hexdigest() != SCIENCE_RESULT_SHA:
        raise PermissionError('not the published CLOSED Stage8-E2 SCIENCE_FINAL')
    science, cold, second = (json.loads(f.read_bytes()) for f in paths)
    if (science.get('source_engine_head') != ENGINE_HEAD
        or science.get('source_protocol_head') != SCIENCE_HEAD
        or science.get('status') != 'STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0'
        or science.get('G2_original_lives_scored') != ORIGINALS
        or science.get('original_native_lives_rehashed') != 64512
        or science.get('no_retry') is not True
        or science.get('cold_audit') != cold
        or digest(cold) != science.get('cold_originals_sha256')
        or cold.get('status') != COLD_PASS
        or cold.get('g0_g1_g2_manifest_sha256', [None]*3)[2] != G2_MANIFEST_SHA
        or cold.get('original_lives_rehashed') != 64512
        or cold.get('source_git_head') != ENGINE_HEAD
        or cold.get('source_files_sha256') != ENGINE_SHA
        or second.get('science_result_file_sha256') != SCIENCE_RESULT_SHA
        or second.get('scientific_status') != science['status']
        or second.get('status') != 'SCIENTIFIC_64_POPULATION_PRIMARY_INDEPENDENTLY_REPRODUCED'):
        raise PermissionError('historical frozen null result or independent original audit invalid')
    if type(science.get('original_population_means')) is not list or len(science['original_population_means']) != 64:
        raise PermissionError('64 original population reference results absent')
    return science


def _accumulator():
    return {'lives':0, 'steps':0, 'dead':0, 'censored':0,
            'deaths':Counter(), 'actions':Counter(), 'early20_actions':Counter(),
            'early20_steps':0, 'paid':Counter(), 'decision_paid':Counter(),
            'learning_paid':Counter(), 'unpaid':Counter(), 'work':Counter(),
            'learning_updates':0, 'replays_executed':0,'shortfall_steps':0,
            'final_body':Counter(), 'body_low10':Counter(), 'body_step_sum':Counter(),
            'drinks':0, 'meals':0}


def _require_cost(item, name):
    if type(item) is not dict or set(item) != set(CURRENCIES):
        raise ValueError(name + ': incomplete paid cost channels')
    for c in CURRENCIES:
        if type(item[c]) is not dict or set(item[c]) != set(BILLS) or not all(
                num(item[c][k]) and item[c][k] >= 0 for k in BILLS):
            raise ValueError(name + ': nonphysical currency accounting')
        if not close(item[c]['requested'], item[c]['paid'] + item[c]['unpaid']):
            raise ValueError(name + ': funding discrepancy')


def _require_work(item):
    if type(item) is not dict or set(item) != set(WORK) or any(
        not positive_int(item[k], allow_zero=True) for k in WORK
    ):
        raise ValueError('invalid cognitive work record')


def _require_body(item):
    if type(item) is not list or len(item) != 5 or any(
        not num(x) or not 0 <= x <= 100 for x in item
    ):
        raise ValueError('incomplete or nonphysical first-person body')


def summarize_one(identity, life):
    """Return only inspected motor/cost/physical counts, not a success verdict."""
    if type(identity) is not dict or type(life) is not dict:
        raise ValueError('original package wrong type')
    manifest = life.get('manifest')
    steps = life.get('steps_lived')
    if (type(manifest) is not dict or manifest.get('protocol') != PROTOCOL
        or manifest.get('source',{}).get('git_head') != ENGINE_HEAD
        or manifest.get('source',{}).get('sha256') != ENGINE_SHA
        or manifest.get('world_sha256') != identity['world_sha256']
        or manifest.get('life_seed') != identity['life_seed']
        or manifest.get('horizon') != 400
        or life.get('life_seed') != identity['life_seed']
        or life.get('genome') != identity['genome_sha256']
        or life.get('world') != manifest.get('world',{}).get('name')
        or life.get('horizon') != 400
        or life.get('manifest_id') != digest(manifest)
        or type(steps) is not int or not 1 <= steps <= 400):
        raise ValueError('original source/World/genome/horizon or manifest mismatch')
    native_trace_chains(life)
    trace = life['trace']
    if not trace or type(life.get('actions')) is not dict:
        raise ValueError('missing native action exposure')
    final = life.get('final_body')
    _require_body(final)
    for c, x in enumerate(trace[-1]['body']):
        if not close(final[c], round(x,6)):
            raise ValueError('final body inconsistent with trace')
    if (life.get('terminal') not in ('censored','dead')
        or type(life.get('death_causes')) is not list
        or life['death_causes'] != trace[-1]['dead']
        or (life['terminal'] == 'dead') != bool(life['death_causes'])
        or (life['terminal'] == 'censored' and steps != 400)
        or not positive_int(life.get('drinks'), allow_zero=True)
        or not positive_int(life.get('meals'), allow_zero=True)):
        raise ValueError('impossible native terminal or count')
    audit = life.get('cognitive_accounting')
    if (type(audit) is not dict or audit.get('schema') != 'i3-cognitive-funding/v2'
        or audit.get('status') != 'SETTLED_FOR_DECLARED_WORK'
        or audit.get('pending_energy') != 0 or audit.get('pending_vigilance') != 0
        or audit.get('pending_replays') != 0):
        raise ValueError('unsettled cognitive work on original life')
    _require_cost(audit['totals'], 'final total')
    stats = _accumulator()
    stats['lives'] = 1
    stats['steps'] = steps
    stats['dead'] = int(life['terminal'] == 'dead')
    stats['censored'] = int(life['terminal'] == 'censored')
    stats['deaths'].update(life['death_causes'])
    counter = Counter()
    for i, step in enumerate(trace):
        action = step['action'] if step['action'] is not None else 'physical_inactivity'
        if action not in ACTIONS:
            raise ValueError('unknown native motor choice')
        counter[action] += 1
        if i < 20:
            stats['early20_actions'][action] += 1
            stats['early20_steps'] += 1
        _require_body(step['body'])
        for j,c in enumerate(CHANNELS):
            stats['body_step_sum'][c] += step['body'][j]
            stats['body_low10'][c] += step['body'][j] < 10
        if i < steps - 1 and step['dead']:
            raise ValueError('action after native death')
        _require_cost(step['cognitive_accounting'],'per-step')
        _require_work(step['cognitive_work'])
        phases = step['funding_phases']
        if type(phases) is not dict or set(phases) != {'decision','learning'}:
            raise ValueError('unfunded or missing paid cognitive phase')
        for phase in ('decision','learning'):
            item = phases[phase]
            if type(item) is not dict or set(item) != {'work','accounting','body_before','body_after_debit'}:
                raise ValueError('invalid phase payment record')
            _require_work(item['work'])
            _require_cost(item['accounting'],phase)
            _require_body(item['body_before'])
            _require_body(item['body_after_debit'])
        if not all(close(phases['learning']['body_after_debit'][i],step['body'][i]) for i in range(5)):
            raise ValueError('unaccounted end-step body state')
        for k in WORK:
            if step['cognitive_work'][k] != (phases['decision']['work'][k] +
                                             phases['learning']['work'][k]):
                raise ValueError('work field differs from paid decision and learning')
            stats['work'][k] += step['cognitive_work'][k]
        for c in CURRENCIES:
            for k in BILLS:
                if not close(step['cognitive_accounting'][c][k],
                             phases['decision']['accounting'][c][k] +
                             phases['learning']['accounting'][c][k]):
                    raise ValueError('step total disagrees with paid phases')
            stats['paid'][c] += step['cognitive_accounting'][c]['paid']
            stats['unpaid'][c] += step['cognitive_accounting'][c]['unpaid']
            stats['decision_paid'][c] += phases['decision']['accounting'][c]['paid']
            stats['learning_paid'][c] += phases['learning']['accounting'][c]['paid']
    if dict(counter) != life['actions'] or sum(counter.values()) != steps:
        raise ValueError('action counter not derived from original actions')
    if (life['drinks'] != counter['boire'] or life['meals'] != counter['manger']
        or audit['inactive_steps'] != counter['physical_inactivity']):
        raise ValueError('native motor, drink, meal or inactivity totals drifted')
    for c in CURRENCIES:
        if not close(stats['paid'][c],audit['totals'][c]['paid']) or not close(
               stats['unpaid'][c],audit['totals'][c]['unpaid']):
            raise ValueError('per-life cognitive funding total differs from original steps')
    for k in ('learning_updates','replays_executed','shortfall_steps'):
        value = audit.get(k)
        if not positive_int(value, allow_zero=True) or value > (400 if k != 'replays_executed' else 1_000_000):
            raise ValueError('impossible native cognition count')
        stats[k] = value
    stats['actions'] = counter
    stats['drinks'] = life['drinks']
    stats['meals'] = life['meals']
    stats['final_body'].update(dict(zip(CHANNELS, final)))
    return stats


def _merge(out, one):
    for key in ('lives','steps','dead','censored','early20_steps','learning_updates',
                'replays_executed','shortfall_steps','drinks','meals'):
        out[key] += one[key]
    for key in ('deaths','actions','early20_actions','paid','decision_paid',
                'learning_paid','unpaid','work','final_body','body_low10','body_step_sum'):
        out[key].update(one[key])


def aggregate_group(x):
    if x['lives'] != ARM_LIVES or x['steps'] <= 0 or x['early20_steps'] <= 0:
        raise ValueError('incomplete G2 population arm or no native exposure')
    l,s,first = x['lives'],x['steps'],x['early20_steps']
    out = {
        'lives': l, 'lived_steps': s,
        'mean_steps': s/l,
        'dead_fraction': x['dead']/l,
        'censored_fraction':x['censored']/l,
        'cognition_energy_paid_per_step':x['paid']['energy']/s,
        'cognition_vigilance_paid_per_step':x['paid']['vigilance']/s,
        'decision_energy_paid_per_step':x['decision_paid']['energy']/s,
        'learning_energy_paid_per_step':x['learning_paid']['energy']/s,
        'decision_vigilance_paid_per_step':x['decision_paid']['vigilance']/s,
        'learning_vigilance_paid_per_step':x['learning_paid']['vigilance']/s,
        'work_cycles_per_step':x['work']['cycles']/s,
        'work_simulated_steps_per_step':x['work']['simulated_steps']/s,
        'work_memory_items_per_step':x['work']['memory_items']/s,
        'work_replays_per_step':x['work']['replays']/s,
        'learning_updates_per_step':x['learning_updates']/s,
        'replays_executed_per_step':x['replays_executed']/s,
        'shortfall_steps_fraction':x['shortfall_steps']/s,
        'energy_cognition_unpaid_per_step':x['unpaid']['energy']/s,
        'vigilance_cognition_unpaid_per_step':x['unpaid']['vigilance']/s,
    }
    for action in ACTIONS:
        out['action_'+action+'_per_step'] = x['actions'][action]/s
        out['early20_action_'+action+'_per_step'] = x['early20_actions'][action]/first
    for channel in CHANNELS:
        out['body_'+channel+'_below10_per_step'] = x['body_low10'][channel]/s
        out['body_'+channel+'_mean_end_step'] = x['body_step_sum'][channel]/s
        out['body_'+channel+'_mean_final'] = x['final_body'][channel]/l
    for reason in ('zero_food','zero_water','zero_integrity'):
        out['death_'+reason+'_per_life'] = x['deaths'][reason]/l
    return out


def analyse_manifest_and_tar(metadata, g2, final, cold, independent):
    cases = read_manifest(metadata)
    science = verify_prior_science(final, cold, independent)
    groups = {(p,a):_accumulator() for p in range(64) for a in ARMS}
    observed = set()
    packed_bytes = 0
    decoded_bytes = 0
    tarfile_path = Path(g2)
    if tarfile_path.is_symlink() or not tarfile_path.is_file():
        raise PermissionError('G2 original TAR missing or symlinked')
    # Streaming preserves original bytes. Never modify/unpack life files to disk.
    with tarfile.open(tarfile_path, 'r|') as tar:
        for item in tar:
            name = item.name.lstrip('./')
            if name.startswith('PHYSICAL_G2/G2/life-'):
                rel = name.removeprefix('PHYSICAL_G2/G2/')
                if rel not in cases or rel in observed or not item.isfile() or item.size>MAX_PACKED:
                    raise ValueError('unexpected, duplicate or oversize original in G2 TAR')
                packed=tar.extractfile(item).read()
                if len(packed) != item.size or sha256(packed).hexdigest() != cases[rel]['sha256']:
                    raise ValueError('original compressed bytes not authenticated')
                raw=unpack_gzip(packed)
                if sha256(raw).hexdigest() != cases[rel]['uncompressed_sha256']:
                    raise ValueError('original raw bytes not authenticated')
                blob=json.loads(raw)
                if type(blob) is not dict or set(blob) != {'identity','life'}:
                    raise ValueError('foreign native gzip payload')
                if blob['identity'] != cases[rel]['identity']:
                    raise ValueError('wrong original identity in gzip')
                idn=blob['identity']
                one=summarize_one(idn,blob['life'])
                _merge(groups[idn['population'],idn['arm']],one)
                observed.add(rel)
                packed_bytes += len(packed)
                decoded_bytes += len(raw)
    if observed != set(cases):
        raise ValueError(f'missing G2 native originals: {len(cases)-len(observed)}')
    p_rows=[]
    metrics=None
    for p in range(64):
        arms={a:aggregate_group(groups[p,a]) for a in ARMS}
        if metrics is None:
            metrics=tuple(k for k in arms['S_sham'] if k not in ('lives','lived_steps'))
        row=science['original_population_means'][p]
        if row['population'] != p:
            raise ValueError('foreign original science population order')
        for a in ARMS:
            if not close(arms[a]['mean_steps'], row['mean_G2_steps'][a]) or row['original_lives_by_arm'][a] != ARM_LIVES:
                raise ValueError('original G2 raw survival differs from frozen science primary')
        p_rows.append({'population':p,'by_arm':arms})
    derived=[]
    for metric in metrics:
        arr=[]
        for row in p_rows:
            arms=row['by_arm']
            vals={a:arms[a][metric] for a in ARMS}
            t=(vals['S_sham']-vals['M_sham'])-(vals['S_swap']-vals['M_swap'])
            arr.append({'population':row['population'], 'did':t,
                        'S_swap_minus_S_sham':vals['S_swap']-vals['S_sham'],
                        'M_swap_minus_M_sham':vals['M_swap']-vals['M_sham']})
        averages={a:math.fsum(row['by_arm'][a][metric] for row in p_rows)/64 for a in ARMS}
        derived.append({
            'metric':metric,'population_unit':64,
            'arm_means_equal_population_weight':averages,
            'mean_exploratory_DID':math.fsum(x['did'] for x in arr)/64,
            'mean_S_swap_minus_sham':math.fsum(x['S_swap_minus_S_sham'] for x in arr)/64,
            'mean_M_swap_minus_sham':math.fsum(x['M_swap_minus_M_sham'] for x in arr)/64,
            'positive_negative_zero_DID_population_count':[
                sum(x['did']>0 for x in arr),sum(x['did']<0 for x in arr),sum(x['did']==0 for x in arr)],
            'all_64_population_descriptive_DID':[x['did'] for x in arr],
        })
    main=next(x for x in derived if x['metric']=='mean_steps')
    if not close(main['mean_exploratory_DID'],science['primary']['primary_gamma_block_did_mean_steps']):
        raise ValueError('exploratory score reinterprets frozen negative primary')
    return {
        'schema':SCHEMA,'status':'READONLY_36864_ORIGINAL_G2_MOTOR_COST_AUDIT_COMPLETE_POSTHOC',
        'source_engine_head':ENGINE_HEAD,'source_engine_sha256':ENGINE_SHA,
        'source_science_protocol_head':SCIENCE_HEAD,'source_science_run_id':RUN_ID,
        'published_science_final_sha256':SCIENCE_RESULT_SHA,
        'published_g2_manifest_sha256':G2_MANIFEST_SHA,
        'original_g2_gzip_full_compressed_and_raw_sha256_rechecked':len(observed),
        'packed_original_bytes_rehashed':packed_bytes,'decoded_original_bytes_rehashed':decoded_bytes,
        'original_step_traces_and_paid_evidence_chains_recomputed':len(observed),
        'populations':64,'arms':list(ARMS),'lives_per_population_arm':ARM_LIVES,
        'native_lives_generated':0,'scientific_new_cohort':False,
        'original_frozen_primary':'STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0',
        'original_frozen_primary_mean_steps':science['primary']['primary_gamma_block_did_mean_steps'],
        'exploratory_only_no_new_p_values_or_effect_proof':True,
        'population_rows':p_rows,'exploratory_metric_descriptions':derived,
        'limitations':[
            'POSTHOC_MULTIPLE_METRICS_NO_INFERENTIAL_SIGNIFICANCE',
            'NO_MEDIATOR_RANDOMIZATION_AND_NO_CAUSAL_MEDIATION_IDENTIFIED',
            'STEP_NORMALIZATION_DOES_NOT_REMOVE_SURVIVOR_SELECTION',
            'EARLY20_ACTION_DENOMINATORS_ARE_OBSERVED_STEPS_NOT_LIFE_UNIFORM',
            'PRIMARY_STAGE8E2_NEGATIVE_VERDICT_IMMUTABLE',
            'F0_ONLY_NO_EXTERNAL_ATTESTATION',
        ]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata-tar',required=True)
    parser.add_argument('--g2-tar',required=True)
    parser.add_argument('--science-final',required=True)
    parser.add_argument('--cold-audit',required=True)
    parser.add_argument('--independent-statistics',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    result=analyse_manifest_and_tar(args.metadata_tar,args.g2_tar,args.science_final,
                                   args.cold_audit,args.independent_statistics)
    data=canonical(result)
    path=Path(args.output)
    with path.open('xb') as f:
        f.write(data)
    print(json.dumps({'status':result['status'],'originals':result['original_g2_gzip_full_compressed_and_raw_sha256_rechecked'],
                      'populations':result['populations'],'science_primary_unchanged':result['original_frozen_primary'],
                      'output_sha256':sha256(data).hexdigest()},sort_keys=True))


if __name__=='__main__':
    main()
