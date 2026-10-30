"""A2-R research birth scope: one prebirth reward-owner substitution only.

No canonical I1 source is modified. Both independently born arms retain the
normal Q/TD, Stage8, Competition, Action Control, WorldBody, UC, and M11.
The selector is temporarily installed only while the fresh owner is created;
it is *never* patched during a physical step or a cold-running lifetime.

Research mode is pinned twice: in the immutable born ValueNeedsConfig.version
(which enters the M11 constructor contract) and in Value/Needs's published
causal owner state (which is validated on M11 cold recovery).
"""
from contextlib import contextmanager, nullcontext
from dataclasses import replace
from hashlib import sha256
from unittest.mock import patch

from i1lab.i1_active_value_needs import I1ActiveValueNeeds

CANONICAL_ABS = "CANONICAL_ABS"
RESEARCH_DEFICIT = "RESEARCH_DEFICIT"
MODES = (CANONICAL_ABS, RESEARCH_DEFICIT)
ROLES = ("native", "reversed")
SEEDS = tuple(range(2001, 2025))
MATRIX = tuple((role, seed, mode) for role in ROLES
               for seed in SEEDS for mode in MODES)
ID_PREFIX = "i1:eco:a2r:reward:"
REWARD_VERSION_SUFFIX = "+i1-a2r-deficit-reward-v1"
REWARD_STATE_KEY = "i1_a2r_reward_policy"
REWARD_STATE_SCHEMA = "i1-a2r-reward-deficit-owner-v1"
IDENTITIES = {
    row: ID_PREFIX + sha256(
        ("i1-a2r-reward-identity-v1|%s|%s|%s" % row).encode("ascii")
    ).hexdigest()[:24] for row in MATRIX
}
ORDER = tuple(sorted(MATRIX, key=lambda row: sha256(
    ("i1-a2r-reward-order-v1|%s|%s|%s" % row).encode("ascii")
).hexdigest()))


class A2RDeficitValueNeeds(I1ActiveValueNeeds):
    """Research-only, one and only Value/Needs owner; no separate Q state."""

    def __init__(self, config):
        if (type(config.version) is not str
                or not config.version.endswith(REWARD_VERSION_SUFFIX)):
            raise ValueError("A2-R deficit owner needs its prebirth version")
        super().__init__(config)

    def reward_between(self, before, after):
        """Only TD's experienced physical-return policy changes.

        This is NOT ECO's normalized/clipped deficit-area score. It preserves
        innate body weights, setpoints and all existing downstream learners.
        All call sites, including sleep/wake, dispatch this same owner method.
        """
        c = self.config
        return sum(
            c.weights[name] * (
                max(c.setpoints[name] - float(before[name]), 0.0)
                - max(c.setpoints[name] - float(after[name]), 0.0)
            )
            for name in ("energy", "food", "water", "integrity")
        )

    def export_causal_state(self):
        state = super().export_causal_state()
        state[REWARD_STATE_KEY] = REWARD_STATE_SCHEMA
        return state

    def restore_causal_state(self, state):
        if (type(state) is not dict
                or state.get(REWARD_STATE_KEY) != REWARD_STATE_SCHEMA
                or state.get("config_version") != self.config.version):
            raise ValueError("A2-R reward owner state/mode mismatch")
        bare = dict(state)
        del bare[REWARD_STATE_KEY]
        super().restore_causal_state(bare)


def _version_deficit(config):
    """Pin the mode in the nested, birth-frozen M11 constructor contract."""
    s9 = config.stage9
    s8 = s9.stage8
    s7 = s8.stage7
    s6 = s7.stage6
    s4 = s6.stage4
    if REWARD_VERSION_SUFFIX in s4.value_needs.version:
        raise ValueError("reward mode already registered in birth config")
    changed = replace(s4.value_needs,
                      version=s4.value_needs.version + REWARD_VERSION_SUFFIX)
    changed_config = replace(config, stage9=replace(
        s9, stage8=replace(s8, stage7=replace(
            s7, stage6=replace(s6, stage4=replace(s4, value_needs=changed))
        ))
    ))
    changed_config.validate()
    return changed_config


def verify_born_reward_owner(owner, *, mode):
    """Check actual birth, without using a scientist-selected label as proof."""
    if mode == CANONICAL_ABS:
        if (type(owner) is not I1ActiveValueNeeds
                or REWARD_VERSION_SUFFIX in owner.config.version
                or REWARD_STATE_KEY in owner.export_causal_state()):
            raise ValueError("canonical A2-R birth is not canonical")
    elif mode == RESEARCH_DEFICIT:
        state = owner.export_causal_state()
        if (type(owner) is not A2RDeficitValueNeeds
                or not owner.config.version.endswith(REWARD_VERSION_SUFFIX)
                or state.get(REWARD_STATE_KEY) != REWARD_STATE_SCHEMA):
            raise ValueError("A2-R birth mode not attested by the causal owner")
    else:
        raise ValueError("unregistered A2-R reward mode")
    return True


@contextmanager
def a2r_matched_reward_birth(*, life_id, role, seed, mode):
    """Temporarily install a *birth-only* selector for one fresh I1Runtime.

    For M11 cold recovery apply this same scope while constructing the fresh
    runtime_factory. Never patch a live owner, its bound reward method or TD.
    A separate run/audit contract must verify the immutable source SHA.
    """
    if (type(role) is not str or role not in ROLES
            or type(seed) is not int or seed not in SEEDS
            or type(mode) is not str or mode not in MODES
            or life_id != IDENTITIES.get((role, seed, mode))):
        raise ValueError("A2-R identity, seed, role or reward mode not preregistered")

    from i1lab import i1_natural_runtime, i1_active_value_needs
    from i1lab.matched_temperament_research import matched_temperament_configuration

    original_temperament = i1_natural_runtime.configure_birth_temperament
    original_owner = i1_active_value_needs.I1ActiveValueNeeds
    if original_owner is not I1ActiveValueNeeds:
        raise RuntimeError("A2-R owner construction was already overridden")
    calls = []

    def configure(stage11_config, *, life_id):
        if life_id != expected:
            raise ValueError("A2-R scope intercepted an unrelated individual")
        if calls:
            raise RuntimeError("A2-R attempted a second temperament projection")
        configured = matched_temperament_configuration(
            stage11_config, life_id=life_id,
            world="eco-a2r-reward", seed=seed,
        )
        calls.append(life_id)
        return (_version_deficit(configured)
                if mode == RESEARCH_DEFICIT else configured)

    expected = life_id
    owner_scope = (patch.object(i1_active_value_needs, "I1ActiveValueNeeds",
                                A2RDeficitValueNeeds)
                   if mode == RESEARCH_DEFICIT else nullcontext())
    with patch.object(i1_natural_runtime, "configure_birth_temperament", configure):
        with owner_scope:
            yield
    if calls != [expected]:
        raise RuntimeError("A2-R did not construct exactly one new temperament")
    if (i1_natural_runtime.configure_birth_temperament is not original_temperament
            or i1_active_value_needs.I1ActiveValueNeeds is not original_owner):
        raise RuntimeError("A2-R birth-only selector was not restored")
