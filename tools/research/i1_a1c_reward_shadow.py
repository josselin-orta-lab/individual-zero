"""Frozen A1-C 48-life reward sensitivity on the SAME immutable action tape.

No new birth, no world simulation, no action choice, no reinforcement-policy
intervention. This is a post-hoc static reward and Q calculation, NOT an
independently identified causal effect on behavior or L3.

Requires native M11 chain and original SHA-256 ZIP custody verification by
``i1_a1c_td_full_audit._audited_zip`` BEFORE invoking ``analyze_life``.
"""
from __future__ import annotations

from collections import defaultdict
from math import isfinite

from i1_a1c_td_full import (
    FROZEN_SOURCE_SHA, FROZEN_RUN_ID, FROZEN_TD_VERSION,
    dot, numeric, p32_features, replay_life,
)
from i1_a1c_wait_gate import scan_gate

NEEDS = ('energy', 'food', 'water', 'integrity')
REWARD_MODES = ('absolute_setpoint', 'deficit_only')


def _record_body(raw):
    if type(raw) is not dict or set(raw) != set(NEEDS):
        raise ValueError('incomplete signed M11 body')
    vals = {k: numeric(raw[k]) for k in NEEDS}
    if any(not 0 <= v <= 100 for v in vals.values()):
        raise ValueError('M11 body outside physical bounds')
    return vals


def config_from_birth(life):
    if type(life) is not dict or life.get('source_commit') != FROZEN_SOURCE_SHA:
        raise ValueError('not the frozen A1-C source')
    born = life.get('born_temperament', {})
    setpoints = life.get('setpoints')
    weights = born.get('body_weights')
    if (type(weights) is not dict or type(setpoints) is not dict
            or set(weights) != set(NEEDS) or set(setpoints) != set(NEEDS)):
        raise ValueError('missing born physiological reward weights')
    setpoints = {k: numeric(setpoints[k]) for k in NEEDS}
    weights = {k: numeric(weights[k]) for k in NEEDS}
    if (any(not 0 <= n <= 100 for n in setpoints.values())
            or any(not 0 < n <= 10 for n in weights.values())):
        raise ValueError('invalid physical reward configuration')
    td = life.get('born_td')
    if (type(td) is not dict or td.get('version') != FROZEN_TD_VERSION
            or (numeric(td['beta']), numeric(td['lambda_e']), numeric(td['eta']))
            != (.8, .8, .05)):
        raise ValueError('source TD birth differs from A1-C')
    return setpoints, weights


def reward_components(before, after, *, setpoints, weights):
    """Identity: native absolute-distance reward = shortfall + surplus drift.

    Positive shortfall reward means a deficit actually decreased. A positive
    surplus-drift term means the body moved toward its target from *above*.
    This is the precise source of the sign disagreement, not a behavioral
    prediction or a change to I1's own reward.
    """
    b = _record_body(before)
    a = _record_body(after)
    if type(setpoints) is not dict or type(weights) is not dict:
        raise ValueError('missing born homeostatic reward config')
    if set(setpoints) != set(NEEDS) or set(weights) != set(NEEDS):
        raise ValueError('invalid born reward signature')
    s = {k: numeric(setpoints[k]) for k in NEEDS}
    w = {k: numeric(weights[k]) for k in NEEDS}
    if (any(not 0 <= s[k] <= 100 for k in NEEDS)
            or any(not 0 < w[k] <= 10 for k in NEEDS)):
        raise ValueError('invalid born reward bounds')
    shortfall = {k: w[k] * (max(0., s[k] - b[k])
                            - max(0., s[k] - a[k])) for k in NEEDS}
    surplus = {k: w[k] * (max(0., b[k] - s[k])
                          - max(0., a[k] - s[k])) for k in NEEDS}
    return {
        'deficit_by_need': shortfall,
        'surplus_by_need': surplus,
        'deficit_total': sum(shortfall.values()),
        'surplus_total': sum(surplus.values()),
        'native_total': sum(shortfall.values()) + sum(surplus.values()),
    }


def reward_between(before, after, *, setpoints, weights, mode):
    """Exact native reward or general deficit-only candidate, in native units.

    Candidate is weighted positive shortfalls, NOT ECO's clipped/normalized
    outcome. It encodes no action, berry, sleep or physical oracle.
    """
    if mode not in REWARD_MODES:
        raise ValueError('unregistered read-only reward candidate')
    parts = reward_components(before, after, setpoints=setpoints,
                              weights=weights)
    return (parts['native_total'] if mode == 'absolute_setpoint'
            else parts['deficit_total'])


def discounted(rewards, beta):
    if not rewards or type(rewards) not in (list, tuple):
        raise ValueError('TD segment must contain original physical rewards')
    return sum(beta ** i * float(r) for i, r in enumerate(rewards))


def _close(observed, predicted, label):
    if abs(numeric(observed) - predicted) > 2e-9 * max(1., abs(predicted)):
        raise ValueError('signed M11 %s does not match frozen tape' % label)


class DualFrozenTD:
    """Native Q replay and a SHADOW reward-only Q replay on identical phi/actions."""
    def __init__(self, beta=.8, lam=.8, eta=.05):
        if (beta, lam, eta) != (.8, .8, .05):
            raise ValueError('not the source-specific born coefficients')
        self.beta = beta
        self.lam = lam
        self.eta = eta
        self.weights_native = {}
        self.weights_shadow = {}
        self.traces = {}
        self.counts = {}
        self.updates = 0

    def q(self, sig, phi, *, mode):
        if len(phi) != 12 or mode not in ('native', 'shadow'):
            raise ValueError('not a frozen twelve-feature Q read')
        bank = self.weights_native if mode == 'native' else self.weights_shadow
        return dot(bank.get(sig, (0.,) * 12), phi)

    def update(self, *, previous_sig, previous_phi, next_sig, next_phi,
               native_segment, shadow_segment, row):
        n = row['segment_length']
        if (type(n) is not int or n < 1 or len(native_segment) != n
                or len(shadow_segment) != n
                or row['previous_signature'] != previous_sig
                or row['next_signature'] != next_sig
                or row['td_version'] != FROZEN_TD_VERSION):
            raise ValueError('TD segment deviates from original selected actions')
        ret_native = discounted(native_segment, self.beta)
        ret_shadow = discounted(shadow_segment, self.beta)
        _close(row['return_g'], ret_native, 'return_g')
        qprev = self.q(previous_sig, previous_phi, mode='native')
        qnext = self.q(next_sig, next_phi, mode='native')
        delta_native = ret_native + self.beta ** n * qnext - qprev
        _close(row['q_previous'], qprev, 'q_previous')
        _close(row['q_next'], qnext, 'q_next')
        _close(row['delta'], delta_native, 'TD delta')
        shadow_prev = self.q(previous_sig, previous_phi, mode='shadow')
        shadow_next = self.q(next_sig, next_phi, mode='shadow')
        delta_shadow = ret_shadow + self.beta ** n * shadow_next - shadow_prev
        factor = (self.beta * self.lam) ** n
        for sig in self.traces:
            self.traces[sig] = [v * factor for v in self.traces[sig]]
        trace = self.traces.setdefault(previous_sig, [0.] * 12)
        self.traces[previous_sig] = [x + y for x, y in zip(trace, previous_phi)]
        active = sorted(sig for sig, z in self.traces.items() if any(z))
        published = row.get('updated_signatures')
        if (type(published) is not list or len(published) != len(set(published))
                or set(published) != set(active)):
            raise ValueError('TD eligibility signatures disagree with M11')
        for sig in active:
            z = self.traces[sig]
            for bank, delta in ((self.weights_native, delta_native),
                                (self.weights_shadow, delta_shadow)):
                prev = bank.get(sig, [0.] * 12)
                bank[sig] = [x + self.eta * delta * y for x, y in zip(prev, z)]
            self.counts[sig] = self.counts.get(sig, 0) + 1
        self.updates += 1
        return {'native_return':ret_native, 'shadow_return':ret_shadow,
                'native_delta':delta_native, 'shadow_delta':delta_shadow,
                'segment_length':n}


def analyze_life(events, life):
    """Validate native TD first, then run deficit-only reward on frozen tape."""
    if type(events) is not list or type(life) is not dict:
        raise ValueError('invalid source-controlled M11 inputs')
    mode = life.get('mode')
    if mode not in ('canonical','td_read_masked'):
        raise ValueError('invalid registered A1-C arm')
    setpoints, weights = config_from_birth(life)
    native_attestation = replay_life(events, born_td=life['born_td'], mode=mode)
    gate = scan_gate(events, mode=mode, food_setpoint=setpoints['food'])
    transitions = {}
    actions = {}
    physical = []
    for e in events:
        if e['kind'] == 'world_transition_experienced':
            t = e['t_monde']
            if t in transitions:
                raise ValueError('duplicate physical world step')
            transitions[t] = e
        elif e['kind'] == 'command_experienced':
            if e['t_monde'] in actions:
                raise ValueError('duplicate executed action')
            actions[e['t_monde']] = e['primitive']
    if set(transitions) != set(range(1,49)) or set(actions) != set(transitions):
        raise ValueError('incomplete original physical trajectory')
    for t in range(1,49):
        e = transitions[t]
        b = _record_body(e['body_before'])
        a = _record_body(e['body_after'])
        if t > 1:
            previous_after = _record_body(transitions[t - 1]['body_after'])
            for key in NEEDS:
                _close(b[key], previous_after[key], 'physical body continuity')
        parts = reward_components(b, a, setpoints=setpoints, weights=weights)
        rn, rs = parts['native_total'], parts['deficit_total']
        _close(rn, rs + parts['surplus_total'], 'reward decomposition identity')
        physical.append({'step':t, 'action':actions[t], 'native_reward':rn,
                         'shadow_reward':rs, 'reward_difference':rs-rn,
                         'surplus_reward':parts['surplus_total'],
                         'surplus_by_need':parts['surplus_by_need']})
    rewards_native = {x['step']:x['native_reward'] for x in physical}
    rewards_shadow = {x['step']:x['shadow_reward'] for x in physical}
    learner = DualFrozenTD()
    last_capture = None
    current_goal = None
    stage_by_step = defaultdict(dict)
    last_state = None
    last_signature = None
    last_t = None
    pending = None
    wait_q = []
    updates = []
    for e in events:
        kind, t, cycle = e.get('kind'), e.get('t_monde'), e.get('cycle')
        d = e.get('data')
        if kind == 'perceptual_capture':
            last_capture = e
        elif kind == 'active_goal_changed':
            after = d['after']
            current_goal = None if after is None else after['goal_type']
        elif kind == 'stage8_option_evaluation':
            if last_capture is None or last_capture['t_monde'] != t:
                raise ValueError('Stage8 state lacks same-step capture')
            opt, sig = d['option_ref'], d['learning_signature']
            stage_by_step[t][opt] = sig
            if opt == 'permanent:attendre' and sig == 'primitive:attendre':
                if mode == 'canonical' and d['learned_value_status'] == 'learned':
                    phi = p32_features(last_capture,current_goal)
                    qnative = learner.q(sig,phi,mode='native')
                    qshadow = learner.q(sig,phi,mode='shadow')
                    _close(d['learned_value'],qnative,'native Stage8 wait Q')
                    wait_q.append({'step':t, 'cycle':cycle,
                                   'native_q':qnative,'shadow_q':qshadow,
                                   'simulated_status':d['simulated_value_status'],
                                   'native_evidence':d['evidence']})
        elif kind == 'command_admitted' and d['source'] == 'decision':
            sig = stage_by_step[t].get(d['option_ref'])
            if not sig or last_capture is None or last_capture['t_monde'] != t:
                raise ValueError('actual decision lacks Stage8 and P32')
            pending=(t,sig,p32_features(last_capture,current_goal))
            if last_state is None:
                last_t,last_signature,last_state=pending
        elif kind == 'td_update_published':
            if pending is None or last_state is None:
                raise ValueError('TD has no actual selected decisions')
            next_t,next_sig,next_phi=pending
            if t != next_t or next_t - last_t != d['segment_length']:
                raise ValueError('TD segment does not match real action gap')
            # Rewards for *actual* experienced steps from previous decision
            # through the step immediately preceding the next decision.
            actual_steps=range(last_t,next_t)
            upd=learner.update(
                previous_sig=last_signature,previous_phi=last_state,
                next_sig=next_sig,next_phi=next_phi,
                native_segment=[rewards_native[x] for x in actual_steps],
                shadow_segment=[rewards_shadow[x] for x in actual_steps],row=d)
            updates.append({'step':t, **upd})
            last_t,last_signature,last_state=pending
    if learner.updates != native_attestation['td_updates'] or len(updates) != native_attestation['td_updates']:
        raise ValueError('shadow TD did not follow every signed original update')
    # Link to exact previously audited, Q-dependent, *actually winning*
    # permanent wait decision cycle. Not a causal alternative trajectory.
    bystep={(row['step'],row['cycle']):row for row in wait_q}
    witness=[]
    for x in gate['witnesses']:
        if not x['Q_only_under_frozen_Stage8']:
            continue
        row=bystep.get((x['step'],x['cycle']))
        if row is None:
            raise ValueError('M11 wait winner missing native Q source')
        _close(row['native_q'], x['learned_q'], 'wait winner Q')
        witness.append({'step':x['step'],'cycle':x['cycle'],
                        'native_q':row['native_q'],'shadow_q':row['shadow_q'],
                        'shadow_nonpositive':row['shadow_q'] <= 0.,
                        'sole_crossing_native':x['other_options_crossed']==0})
    return {
        'role':life['role'],'seed':life['seed'],'mode':mode,
        'identity':life['identity'],
        'm11_final_head':life['audited']['journal_head'],
        'native_td_updates_verified':learner.updates,
        'native_replay_q_checked':native_attestation['native_m11_q_checks'],
        'physical_steps':len(physical),
        'action_rewards':physical,'td_update_comparisons':updates,
        'native_q_only_wait_winners':witness,
        'count_q_only_wait_winners':len(witness),
        'scope':'POSTHOC_FIXED_ACTION_TAPE_NO_BEHAVIORAL_COUNTERFACTUAL',
        'a1c_status':'NO_GO','L3':'NOT_ESTABLISHED',
    }
