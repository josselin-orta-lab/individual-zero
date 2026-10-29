"""Frozen A1-C: decision-cycle availability of learned-only wait evidence.

Read-only post-hoc analysis. No synthetic I1 life, no action override, no
counterfactual trajectory, no L3 promotion. Unit of inference is 12 birth
blocks, *not* the number of repeatedly encountered hunger episodes.
"""
from collections import Counter, defaultdict
from math import isfinite

from i1_a1c_td_full import FROZEN_SOURCE_SHA, FROZEN_RUN_ID, numeric

ROLES = ('native', 'reversed')
SEEDS = tuple(range(101, 113))
ARMS = ('canonical', 'td_read_masked')
STEPS = 48


def finite(x):
    value = numeric(x)
    if not isfinite(value):
        raise ValueError('not a finite M11 float')
    return value


def scan_gate(events, *, mode, food_setpoint=60):
    """Audit the final, actually admitted decision cycle at each opportunity.

    Does not recompute neural/TD states: call only AFTER the independent
    full-vector M11 custody and Stage8/Competition audit on the same ZIP.
    """
    if (type(events) is not list or mode not in ARMS
            or type(food_setpoint) not in (int, float)
            or not 0 < food_setpoint <= 100):
        raise ValueError('invalid source-scoped gate input')
    captures, admissions = {}, {}
    evaluations, competitions = defaultdict(dict), {}
    for e in events:
        if type(e) is not dict or type(e.get('t_monde')) is not int:
            raise ValueError('invalid M11 event')
        t, k, c = e['t_monde'], e.get('kind'), e.get('cycle')
        if t not in range(1, STEPS + 1):
            raise ValueError('event outside A1-C horizon')
        if k == 'perceptual_capture':
            if t in captures or type(e.get('data')) is not dict:
                raise ValueError('invalid or repeated body capture')
            captures[t] = e['data']
        elif k == 'command_admitted':
            if t in admissions or type(e.get('data')) is not dict:
                raise ValueError('repeated or invalid native motor admission')
            admissions[t] = e['data']
        elif k in ('stage8_option_evaluation', 'competition_cycle'):
            if type(c) is not int or c <= 0 or type(e.get('data')) is not dict:
                raise ValueError('invalid competition cycle')
            if k == 'stage8_option_evaluation':
                ref = e['data'].get('option_ref')
                if type(ref) is not str or not ref or ref in evaluations[(t,c)]:
                    raise ValueError('forged or duplicate Stage8 option')
                evaluations[(t,c)][ref] = e['data']
            else:
                if (t,c) in competitions or type(e['data'].get('traces')) is not list:
                    raise ValueError('duplicate/invalid Competition')
                competitions[(t,c)] = e['data']['traces']
    if set(admissions) != set(range(1, STEPS + 1)):
        raise ValueError('incomplete physical admissions')
    if (set(evaluations) != set(competitions)
            or {t for (t,c) in competitions} != set(captures)):
        raise ValueError('Stage8/Competition/capture provenance gap')
    for t, capture in captures.items():
        if admissions[t].get('source') != 'decision':
            raise ValueError('non-decision capture')
    counts, witnesses = Counter(), []
    for t in sorted(captures):
        cap = captures[t]
        body, inv = cap.get('dual_scope_visible_body'), cap.get('agency_visible_inventory')
        if (type(body) is not dict or type(inv) is not dict
                or any(type(inv.get(b)) is not int or inv[b] < 0 for b in ('berry_a','berry_b'))):
            raise ValueError('non-native body/inventory capture')
        if not (finite(body['food']) < food_setpoint and
                inv['berry_a'] + inv['berry_b'] > 0):
            continue
        counts['hungry_stock_opportunities'] += 1
        admitted = admissions[t]
        if admitted.get('primitive') != 'attendre':
            continue
        counts['wait_admissions'] += 1
        cycle = max(c for step,c in competitions if step == t)
        stage = evaluations[(t, cycle)]
        traces = competitions[(t, cycle)]
        byref = {v['option_ref']: v for v in traces}
        if (len(traces) != len(byref) or set(byref) != set(stage)):
            raise ValueError('Stage8/Competition option mismatch')
        ref = admitted.get('option_ref')
        if ref not in byref:
            raise ValueError('admitted wait absent from final Competition')
        tr, eval_row = byref[ref], stage[ref]
        if type(tr.get('crossed')) is not bool:
            raise ValueError('nonboolean Competition crossing')
        if tr['crossed'] != (finite(tr['accumulator_after']) >= finite(tr['threshold'])):
            raise ValueError('inconsistent actual threshold')
        if not tr['crossed']:
            if ref != 'permanent:attendre':
                raise ValueError('unregistered noncrossed wait admission')
            counts['wait_fallback_without_crossing'] += 1
            continue
        counts['wait_crossed_winner'] += 1
        others = [v for opt,v in byref.items() if opt != ref and v['crossed']]
        counts['wait_winner_with_competing_crossing'] += int(bool(others))
        if (mode == 'canonical'
                and eval_row.get('learned_value_status') == 'learned'
                and finite(eval_row['learned_value']) > 0
                and eval_row.get('simulated_value_status') == 'unavailable'
                and eval_row.get('simulated_value') is None):
            # This option has no Stage6 sim evidence; Stage8's only present
            # extrinsic input is native learned Q. This is an observed
            # one-cycle dependency, NOT a new unmasked life trajectory.
            counts['observed_positive_Q_without_sim_wait_wins'] += 1
            # Local I1 affordances may also have a non-Q prior evidence input.
            # Only the permanent Stage8 wait with NO simulator has Q as its
            # sole present extrinsic input. Never conflate the two sources.
            permanent_q_only = (ref == 'permanent:attendre'
                                and eval_row.get('learning_signature') == 'primitive:attendre')
            if permanent_q_only:
                counts['permanent_wait_Q_only_wins'] += 1
                counts['permanent_wait_Q_only_sole_crossing'] += int(not others)
                counts['permanent_wait_Q_only_other_crossed'] += int(bool(others))
            else:
                counts['other_wait_Q_with_possible_prior'] += 1
            before = finite(tr['accumulator_before'])
            threshold = finite(tr['threshold'])
            if permanent_q_only and before < threshold:
                counts['permanent_Q_only_new_threshold_crossing'] += 1
            witnesses.append({
                'step': t, 'cycle': cycle,
                'winner': ref, 'learned_q': finite(eval_row['learned_value']),
                'competition_evidence': finite(tr['evidence']),
                'accumulator_before': before,
                'accumulator_after': finite(tr['accumulator_after']),
                'threshold': threshold,
                'other_options_crossed': len(others),
                'Q_only_under_frozen_Stage8': permanent_q_only,
            })
    return {'counts': dict(counts), 'witnesses': witnesses,
            'scope': 'RECORDED_FINAL_CYCLE_ONLY_NOT_CAUSAL_POLICY_REPLAY'}


def summarize(lives):
    """Summarize 48 previously attested, disjoint original M11 lives."""
    if type(lives) is not list or len(lives) != 48:
        raise ValueError('expected exact A1-C original 48-life cohort')
    expected = {(r,s,a) for r in ROLES for s in SEEDS for a in ARMS}
    indexes = set()
    for l in lives:
        k = (l.get('role'), l.get('seed'), l.get('mode'))
        if k not in expected or k in indexes or l.get('scope') != 'RECORDED_FINAL_CYCLE_ONLY_NOT_CAUSAL_POLICY_REPLAY':
            raise ValueError('duplicate or nonoriginal provenance')
        indexes.add(k)
    if indexes != expected:
        raise ValueError('missing cohort member')
    categories = {}
    for role in ROLES:
        for arm in ARMS:
            selection = [l for l in lives if l['role']==role and l['mode']==arm]
            total=Counter()
            for l in selection:
                total.update(l['counts'])
            categories[role+'/'+arm]={
                'counted_lives': len(selection),
                'repeated_decision_counts': dict(total),
                'lives_with_learned_wait_winner': sum(
                    l['counts'].get('observed_positive_Q_without_sim_wait_wins',0)>0
                    for l in selection),
                'lives_with_learned_only_sole_crossing': sum(
                    l['counts'].get('permanent_wait_Q_only_sole_crossing',0)>0
                    for l in selection),
            }
    affected = [seed for seed in SEEDS if any(
        l['seed']==seed and l['mode']=='canonical'
        and l['counts'].get('permanent_wait_Q_only_sole_crossing',0)>0
        for l in lives)]
    return {
        'schema':'individual-zero-i1-a1c-posthoc-static-decision-gate/1',
        'original_run_id':FROZEN_RUN_ID,
        'original_source_sha':FROZEN_SOURCE_SHA,
        'audited_lives':len(lives),
        'independent_temperament_blocks':len(SEEDS),
        'role_mode_categories':categories,
        'affected_independent_temperament_seeds':affected,
        'number_affected_independent_temperament_blocks':len(affected),
        'unit':'DECISION_EPISODES_NESTED_IN_12_TEMPERAMENT_BLOCKS',
        'epistemic_scope':'ONE_RECORDED_CYCLE_NOT_NO_Q_COUNTERFACTUAL_TRAJECTORY',
        'a1c_confirmatory_status':'NO_GO',
        'general_L3':'NOT_ESTABLISHED',
    }
