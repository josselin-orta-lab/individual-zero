"""Stage 11 P-48: deterministic, development-only intrinsic causal curiosity.

Consumes only read-only canonical Causal Model exports, never Lab or oracle.
A proposed option is not evidence of progress. Normative MVP sections 8.5/14.
"""
from dataclasses import dataclass, asdict
from math import isfinite

@dataclass(frozen=True)
class ExplorationConfig:
    version: str
    novelty_weight: float
    progress_weight: float
    habituation_visits: int
    stagnant_visit_limit: int

    def validate(self):
        if not self.version or self.habituation_visits < 1 or self.stagnant_visit_limit < 1:
            raise ValueError("invalid version or visit limits")
        if any(not isfinite(v) or v < 0 for v in (self.novelty_weight, self.progress_weight)):
            raise ValueError("invalid weights")
        if self.novelty_weight + self.progress_weight > 1:
            raise ValueError("intrinsic weights exceed 1")

@dataclass(frozen=True)
class IntrinsicAssessment:
    status: str
    value: float | None
    reason: str
    signal_ids: tuple[str, ...] = ()

class Exploration:
    owner_id = "exploration"
    _rank = {"aucun": 0, "correlation_observee": 1,
             "hypothese_causale": 2, "testee_par_intervention": 3, "etablie": 4}

    def __init__(self, config: ExplorationConfig, *, coefficient: float):
        config.validate()
        if not isfinite(coefficient) or not -1 <= coefficient <= 1:
            raise ValueError("invalid derived exploration coefficient")
        self.config = config
        self.coefficient = float(coefficient)
        self._questions = {}

    def observe_causal_state(self, state):
        """Only confirmed causal publications can create learning progress.

        A previously *executed* information-seeking action is an activity
        visit, regardless of whether its physical result later passes P-47.
        A subsequent canonical intervention for the SAME command/step must
        not increment that visit a second time (INV-14).
        """
        if not isinstance(state, dict):
            raise ValueError("canonical causal state must be a mapping")
        observations = {
            v["identifier"]: v for v in state.get("causal_observations", ())
            if v.get("source") == "monde" and v.get("independent_episode") is True
            and not v.get("oracle_derived") and not v.get("counterfactual")
            and not v.get("rollback_cancelled")
        }
        proofs = {}
        for review in state.get("causal_review_proofs", ()):
            ref = review["contingency_ref"]
            for first, second in review.get("contrasting_pairs", ()):
                a, b = observations.get(first), observations.get(second)
                if (a and b and a["contingency_ref"] == ref
                    and b["contingency_ref"] == ref
                    and a["observation_ref"] != b["observation_ref"]
                    and a["cause_present"] is True and b["cause_present"] is False):
                    proofs.setdefault(ref, review["identifier"])
        observed = {}
        for row in state.get("causal_interventions", ()):
            if (row.get("action_applied") is True and row.get("source") == "monde"
                and not row.get("oracle_derived") and not row.get("counterfactual")
                and not row.get("rollback_cancelled")):
                observed.setdefault(row["contingency_ref"], {})[row["identifier"]] = row
        updates = {}
        for row in state.get("published", ()):
            ref, status = row["ref"], row["causal_status"]
            if status not in self._rank or row["safety_status"] != "aucun":
                continue
            old = self._questions.get(ref)
            prior_ids = set() if old is None else set(old["ids"])
            accepted = observed.get(ref, {})
            now_ids = prior_ids | set(accepted)
            new_ids = set(accepted) - prior_ids
            attempts = () if old is None else old["executed_keys"]
            # A physically applied and recorded test was counted when the
            # command was executed. Its later independently verified
            # intervention must not create a fictitious extra exploration.
            not_yet_counted = sum(
                f"{accepted[ident].get('command_ref')}@"
                f"{accepted[ident].get('emitted_step')}" not in attempts
                for ident in new_ids
            )
            progress = (
                old is not None
                and self._rank[status] > self._rank[old["status"]]
            )
            updates[ref] = {
                "version": row["version"], "status": status,
                "proof": proofs.get(ref),
                "ids": tuple(sorted(now_ids)),
                "executed_keys": attempts,
                "visits": (0 if old is None else old["visits"]) + not_yet_counted,
                "stagnant": 0 if progress else (
                    (0 if old is None else old["stagnant"]) + not_yet_counted
                ),
                "progress": (
                    1.0 if progress else
                    0.0 if not_yet_counted else
                    (0.0 if old is None else old["progress"])
                ),
            }
        # A removed/invalidated canonical question cannot survive in local
        # curiosity counters and keep motivating a stale test.
        self._questions = updates

    def record_applied_causal_test(self, *, option, sent_step: int) -> bool:
        """Record an ACTUALLY applied command received from Action Control.

        This is an activity/habituation counter, NEVER causal confirmation.
        An ordinary proposal, planned command, or rolled-back action must
        not call this method. The vNext runtime owns that dispatch boundary.
        """
        if type(sent_step) is not int or sent_step < 1:
            raise ValueError("applied exploratory command needs world time")
        if self.motivation(option).status != "available":
            return False
        ref = option.motive_ref.id[len("test_causal:"):]
        q = self._questions[ref]
        key = f"{option.id}@{sent_step}"
        previous = set(q["executed_keys"])
        if key in previous:
            return False
        previous.add(key)
        self._questions[ref] = {
            **q,
            "executed_keys": tuple(sorted(previous)),
            "visits": q["visits"] + 1,
            "stagnant": q["stagnant"] + 1,
            "progress": 0.0,
        }
        return True

    def motivation(self, option):
        motive = option.motive_ref
        if motive.type != "test_causal":
            return IntrinsicAssessment("not_applicable", None, "other_option")
        if not motive.id.startswith("test_causal:"):
            return IntrinsicAssessment("unavailable", None, "bad_motive")
        ref = motive.id[len("test_causal:"):]
        q = self._questions.get(ref)
        if not q or not q["proof"] or q["status"] not in ("hypothese_causale", "testee_par_intervention"):
            return IntrinsicAssessment("unavailable", None, "unverified_question")
        if option.provenance != "test_causal" or option.id != f"option:causal-test:{ref}:v{q['version']}":
            return IntrinsicAssessment("unavailable", None, "stale_option")
        raw = (self.config.novelty_weight / (1 + q["visits"] / self.config.habituation_visits)
               + self.config.progress_weight * q["progress"])
        if q["stagnant"] >= self.config.stagnant_visit_limit:
            raw = 0.0
        value = min(1.0, max(0.0, (1 + self.coefficient) * raw))
        return IntrinsicAssessment("available", value, "physically_grounded_interest",
                                   (f"exploration:question:{ref}:proof:{q['proof']}",))

    def cibles(self, *, degraded=False):
        if degraded:
            return ()
        return tuple(sorted(ref for ref,q in self._questions.items()
                            if q["proof"] and q["status"] in ("hypothese_causale", "testee_par_intervention")
                            and q["stagnant"] < self.config.stagnant_visit_limit))

    def boredom_detected(self) -> bool:
        """Development-only evidence of stagnation, not a synthetic reward.

        A genuinely unanswered but *unexplored* question is not boredom.
        Repeated proposals do not increment visits and cannot create it.
        """
        unresolved = [
            q for q in self._questions.values()
            if q["proof"] and q["status"] in (
                "hypothese_causale", "testee_par_intervention"
            )
        ]
        return bool(unresolved) and all(
            q["stagnant"] >= self.config.stagnant_visit_limit
            for q in unresolved
        )

    def export_causal_state(self):
        return {
            "state_schema": "exploration-activity-v2",
            "config_version": self.config.version,
            "coefficient": self.coefficient,
            "questions": [
                [ref, dict(q)] for ref, q in sorted(self._questions.items())
            ],
        }

    def restore_causal_state(self, state):
        """Reject a corrupted snapshot before mutating owner state."""
        if (
            not isinstance(state, dict)
            or state.get("state_schema") != "exploration-activity-v2"
            or state.get("config_version") != self.config.version
            or state.get("coefficient") != self.coefficient
            or not isinstance(state.get("questions"), list)
        ):
            raise ValueError("incompatible exploration snapshot")
        expected = {
            "version", "status", "proof", "ids", "executed_keys",
            "visits", "stagnant", "progress",
        }
        restored = {}
        for raw in state["questions"]:
            if (
                not isinstance(raw, (list, tuple)) or len(raw) != 2
                or not isinstance(raw[0], str) or not raw[0]
                or raw[0] in restored or not isinstance(raw[1], dict)
                or set(raw[1]) != expected
            ):
                raise ValueError("invalid exploration snapshot entry")
            ref, q = raw
            ids, applied = q["ids"], q["executed_keys"]
            if (
                type(q["version"]) is not int or q["version"] < 1
                or q["status"] not in self._rank
                or q["proof"] is not None
                and (not isinstance(q["proof"], str) or not q["proof"])
                or any(
                    not isinstance(values, (list, tuple))
                    or any(not isinstance(x, str) or not x for x in values)
                    or tuple(values) != tuple(sorted(set(values)))
                    for values in (ids, applied)
                )
                or type(q["visits"]) is not int or q["visits"] < 0
                or type(q["stagnant"]) is not int
                or not 0 <= q["stagnant"] <= q["visits"]
                or type(q["progress"]) not in (int, float)
                or q["progress"] not in (0.0, 1.0)
            ):
                raise ValueError("corrupt exploration learning counters")
            restored[ref] = {
                **q, "ids": tuple(ids), "executed_keys": tuple(applied),
            }
        self._questions = restored

