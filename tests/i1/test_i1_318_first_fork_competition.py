"""#318 local first-fork attribution is a conservative read-only classifier."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location(
    "auditq318", ROOT/"tools/audit_i1_318_local_q_ablation_cohort.py")
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

def row(sig, status, registered=True):
    return {"learning_signature":sig,"q_status_at_proposal":status,
            "registered":registered,"evaluated":True,
            "competition_evaluated":True}

class FirstFork(unittest.TestCase):
    def test_local_ranking_difference(self):
        self.assertEqual(a.classify_first_fork_pathway(
            {"local_candidates":[row("boire","unlearned")]},
            {"local_candidates":[row("collecter","learned")]}),
            "local_candidate_rank_changed")

    def test_same_signature_with_prior_Q(self):
        self.assertEqual(a.classify_first_fork_pathway(
            {"local_candidates":[row("boire","unlearned")]},
            {"local_candidates":[row("boire","learned")]}),
            "same_local_signature_different_Q_evidence")

    def test_absent_registration_never_proves_Q_effect(self):
        self.assertEqual(a.classify_first_fork_pathway(
            {"local_candidates":[row("boire","unlearned",False)]},
            {"local_candidates":[row("boire","learned")]}),
            "insufficient_local_Competition_evidence")

    def test_empty_option_no_causal_claim(self):
        self.assertEqual(a.classify_first_fork_pathway(
            {"local_candidates":[]},{"local_candidates":[]}),
            "insufficient_local_Competition_evidence")

if __name__=="__main__":
    unittest.main()
