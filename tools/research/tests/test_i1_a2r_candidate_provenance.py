"""Pure provenance classification, no living I1 births."""
import copy
import unittest

from i1_a2r_candidate_provenance import audit_candidate_provenance


def fixture():
    birth = {"scope":"SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE",
             "identity":"life","mode":"CANONICAL_ABS",
             "initial_competition":{"cycle":0,"engaged_option_id":None,"registry":[]},
             "competition_calibration":{"residual":0.5,"base_threshold":1.0}}
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

    def test_uninterrupted_candidate_carry_and_tamper(self):
        b,q,c=fixture()
        events=[
            {"kind":"option_registration","t_monde":1,"cycle":1,
             "data":{"option_ref":"x","registered":True}},
            {"kind":"competition_cycle","t_monde":1,"cycle":1,
             "data":{"traces":[{"option_ref":"x","accumulator_before":0,
                                "accumulator_after":0.25}]}},
            {"kind":"competition_cycle","t_monde":1,"cycle":2,
             "data":{"traces":[{"option_ref":"x","accumulator_before":0.25,
                                "accumulator_after":0.4}]}}
        ]
        report=audit_candidate_provenance(events,birth=b,q_replay=q,control=c)
        self.assertEqual(report["uninterrupted_same_step_candidate_carries_checked"],1)
        bad=copy.deepcopy(events)
        bad[2]["data"]["traces"][0]["accumulator_before"]=0.1
        with self.assertRaisesRegex(ValueError,"carry differs"):
            audit_candidate_provenance(bad,birth=b,q_replay=q,control=c)
        edited=copy.deepcopy(events)
        edited.insert(2,{"kind":"option_registration","t_monde":1,"cycle":2,
                          "data":{"option_ref":"x","registered":True}})
        self.assertEqual(audit_candidate_provenance(edited,birth=b,q_replay=q,
            control=c)["candidate_carries_quarantined"],1)

    def test_nonmonotonic_paid_cycles_rejected(self):
        b,q,c=fixture()
        events=[
            {"kind":"competition_cycle","t_monde":1,"cycle":2,
             "data":{"traces":[]}},
            {"kind":"competition_cycle","t_monde":1,"cycle":1,
             "data":{"traces":[]}},
        ]
        with self.assertRaisesRegex(ValueError,"chronology"):
            audit_candidate_provenance(events,birth=b,q_replay=q,control=c)

    def test_memory_credit_must_precede_and_be_bounded(self):
        b,q,c=fixture()
        reg={"kind":"i1_place_memory_option_registration","t_monde":2,
             "cycle":1,"data":{"option_ref":"memory:x","registered":True}}
        carry={"kind":"i1_place_memory_intention_reconsidered",
               "t_monde":2,"cycle":1,
               "data":{"next_option_ref":"memory:x","carried_evidence":0.3}}
        trace={"kind":"competition_cycle","t_monde":2,"cycle":1,
               "data":{"traces":[{"option_ref":"memory:x",
                                   "accumulator_before":0.2}]}}
        self.assertEqual(audit_candidate_provenance([reg,carry,trace],
            birth=b,q_replay=q,control=c)["source_bounded_memory_credits_checked"],1)
        bad=copy.deepcopy(trace)
        bad["data"]["traces"][0]["accumulator_before"]=0.6
        with self.assertRaisesRegex(ValueError,"upper bound"):
            audit_candidate_provenance([reg,carry,bad],birth=b,q_replay=q,control=c)

    def test_reject_nonempty_or_forged_birth(self):
        b,q,c=fixture()
        b["initial_competition"]["registry"]=[{"fake":"prior"}]
        with self.assertRaises(ValueError):
            audit_candidate_provenance([],birth=b,q_replay=q,control=c)


if __name__=="__main__":
    unittest.main()
