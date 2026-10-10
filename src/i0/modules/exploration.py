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
        """Read published, independently matched physical proofs only."""
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
        for v in state.get("causal_interventions", ()):
            if (v.get("action_applied") is True and v.get("source") == "monde"
                and not v.get("oracle_derived") and not v.get("counterfactual")
                and not v.get("rollback_cancelled")):
                observed.setdefault(v["contingency_ref"], set()).add(v["identifier"])
        for row in state.get("published", ()):
            ref, status = row["ref"], row["causal_status"]
            if status not in self._rank or row["safety_status"] != "aucun":
                self._questions.pop(ref, None)
                continue
            earlier = self._questions.get(ref)
            previous_ids = set() if earlier is None else set(earlier["ids"])
            ids = previous_ids | observed.get(ref, set())
            visits = len(ids - previous_ids)
            advanced = earlier is not None and self._rank[status] > self._rank[earlier["status"]]
            self._questions[ref] = {
                "version": row["version"], "status": status,
                "proof": proofs.get(ref), "ids": tuple(sorted(ids)),
                "visits": (0 if earlier is None else earlier["visits"]) + visits,
                "stagnant": (0 if advanced else (0 if earlier is None else earlier["stagnant"]) + visits),
                "progress": 1.0 if advanced else (0.0 if visits else (0.0 if earlier is None else earlier["progress"])),
            }

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

    def export_causal_state(self):
        return {"config_version": self.config.version, "coefficient": self.coefficient,
                "questions": [[key, dict(value)] for key,value in sorted(self._questions.items())]}

    def restore_causal_state(self, state):
        if state["config_version"] != self.config.version or state["coefficient"] != self.coefficient:
            raise ValueError("exploration snapshot mismatch")
        restored = {}
        for ref, q in state["questions"]:
            if ref in restored or q["status"] not in self._rank or q["visits"] < 0 or q["stagnant"] < 0:
                raise ValueError("invalid exploration snapshot")
            restored[ref] = {**q, "ids": tuple(q["ids"])}
        self._questions = restored
