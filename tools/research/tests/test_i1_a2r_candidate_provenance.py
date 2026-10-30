"""Pure provenance classification, no living I1 births."""
import copy
import unittest

from i1_a2r_candidate_provenance import audit_candidate_provenance


def fixture():
    birth = {"scope":"SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE",
             "identity":"life","mode":"CANONICAL_ABS",
             "initial_competition":{"cycle":0,"engaged_option_id":None,"registry":[]}}
    replay = {"scope":"A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3",
              "full_q_replay_verified":True,"m11_identity":"life","mode":"CANONICAL_ABS"}
    control = {"all_motor_receipts_matched":True}
    return birth,replay,control


class CandidateProvenanceTests(unittest.TestCase):
    def test_first_observation_is_only_consistent_not_independent_owner_proof(self):
        b,q,c=fixture()
        events=[
            {"kind":"option_registration","t_monde":1,"cycle":1,
             "data":{"option_ref":"candidate:x","registered":True}},
            {"kind":"competition_cycle","t_monde":1,"cycle":1,
             "data":{"traces":[{"option_ref":"candidate:x","accumulator_before":0}]}},
            {"kind":"competition_cycle","t_monde":1,"cycle":2,
             "data":{"traces":[{"option_ref":"candidate:x","accumulator_before":1}]}},
        ]
        report=audit_candidate_provenance(events,birth=b,q_replay=q,control=c)
        self.assertEqual(report["first_seen_zero_consistent"],1)
        self.assertEqual(report["prior_state_or_refresh_quarantined"],1)
        self.assertFalse(report["study_admissible"])

    def test_memory_carry_is_never_zero_birth(self):
        b,q,c=fixture()
        events=[
            {"kind":"i1_place_memory_option_registration","t_monde":2,"cycle":1,
             "data":{"option_ref":"memory:x","registered":True}},
            {"kind":"i1_place_memory_intention_reconsidered","t_monde":2,"cycle":1,
             "data":{"next_option_ref":"memory:x"}},
            {"kind":"competition_cycle","t_monde":2,"cycle":1,
             "data":{"traces":[{"option_ref":"memory:x","accumulator_before":0.3}]}},
        ]
        report=audit_candidate_provenance(events,birth=b,q_replay=q,control=c)
        self.assertEqual(report["memory_carry_quarantined"],1)

    def test_missing_registration_quarantined_and_late_registration_rejected(self):
        b,q,c=fixture()
        trace={"kind":"competition_cycle","t_monde":1,"cycle":1,
               "data":{"traces":[{"option_ref":"candidate:x","accumulator_before":0}]}}
        report=audit_candidate_provenance([trace],birth=b,q_replay=q,control=c)
        self.assertEqual(report["missing_registration_quarantined"],1)
        late={"kind":"option_registration","t_monde":1,"cycle":1,
              "data":{"option_ref":"candidate:x","registered":True}}
        with self.assertRaises(ValueError):
            audit_candidate_provenance([trace,late],birth=b,q_replay=q,control=c)

    def test_reject_nonempty_or_forged_birth(self):
        b,q,c=fixture()
        b["initial_competition"]["registry"]=[{"fake":"prior"}]
        with self.assertRaises(ValueError):
            audit_candidate_provenance([],birth=b,q_replay=q,control=c)


if __name__=="__main__":
    unittest.main()
