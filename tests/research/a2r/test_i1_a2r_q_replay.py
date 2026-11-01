"""Synthetic, no-birth tests for A2-R independent twelve-feature TD replay."""
import copy
import unittest
from i1_a2r_q_replay import replay_q, features, FEATURES

TD = {"version": "p31-stage8-reference-v1",
      "feature_version": "p32-reference-v1",
      "feature_names": FEATURES, "beta": .8, "eta": .05,
      "lambda_e": .8, "position_scale_x": 31., "position_scale_y": 31.}
WORLD = {"day_steps": 300, "night_steps": 100, "night_start_step": 200}
S = {k: 60. for k in ("energy","food","water","integrity")}
W = {k: 1. for k in S}


def cohort_events(*, n=3, dead=False, tamper=False):
    events = []
    previous = {"energy": 90., "food": 60., "water": 55., "integrity": 100.}
    for t in range(1, n + 1):
        before = dict(previous)
        after = dict(before)
        after["energy"] -= .5
        after["water"] -= .4
        from i1_a2r_m11_cold import reward
        val = reward(before, after, setpoints=S, weights=W,
                     mode="RESEARCH_DEFICIT")
        events.extend([
            {"kind":"perceptual_capture","t_monde":t,
             "data":{"capture_t_monde":t,"dual_scope_visible_body":before,
                     "position":{"x":8,"y":8}}},
            {"kind":"stage8_option_evaluation","t_monde":t,"cycle":1,
             "data":{"option_ref":"permanent:attendre",
                     "learning_signature":"primitive:attendre",
                     "learned_value_status":"unlearned" if t <= 2 else "learned",
                     "learned_value":None, "evidence":0.2}},
            {"kind":"competition_cycle","t_monde":t,"cycle":1,
             "data":{"traces":[{"option_ref":"permanent:attendre",
                                  "evidence":0.2,"crossed":True}]}},
            {"kind":"command_admitted","t_monde":t,"cycle":1,
             "data":{"source":"decision","option_ref":"permanent:attendre",
                     "primitive":"attendre"}},
            {"kind":"command_experienced","t_monde":t,"attempt_ref":str(t),
             "primitive":"attendre","parameters":{}},
            {"kind":"world_transition_experienced","t_monde":t,"attempt_ref":str(t),
             "body_before":before,"body_after":after},
            {"kind":"step_closed","t_monde":t,"attempt_ref":str(t),
             "data":{"outcome":"dead" if dead and t == n else "normal",
                     "applied_command_count":1,"world_advance_count":1}},
        ])
        if t > 1 and not (dead and t == n):
            # The engine's first two real decisions are unlearned. The update
            # published by the second decision gives Q to the third one.
            phi = (1., before["energy"]/100., before["food"]/100.,
                   before["water"]/100., before["integrity"]/100.,
                   8/31., 8/31., 0., 0., 0., 0., 0.)
            prev_phi = (1., (before["energy"]+.5)/100., 60./100.,
                        (before["water"]+.4)/100., 1., 8/31., 8/31.,
                        0., 0., 0., 0., 0.)
            ret = reward({"energy": before["energy"]+.5,"food":60.,
                          "water":before["water"]+.4,"integrity":100.},
                         before,setpoints=S,weights=W,mode="RESEARCH_DEFICIT")
            if t == 2:
                qp = qn = 0.
            else:
                qp = qn = 0.
            # Synthetic 3rd step is covered by an independent state fixture below.
            if t == 2:
                events.append({"kind":"td_update_published","t_monde":t,
                    "cycle":1,"data":{"previous_signature":"primitive:attendre",
                    "next_signature":"primitive:attendre","segment_length":1,
                    "return_g": ret + (1 if tamper else 0),
                    "q_previous":qp,"q_next":qn,"delta":ret,
                    "updated_signatures":["primitive:attendre"],
                    "td_version":TD["version"]}})
        previous = after
    return events


class FullQReplayContracts(unittest.TestCase):
    def test_two_decisions_and_twelve_dimensions(self):
        ev=cohort_events(n=2)
        x=replay_q(ev,generation=2,status="active",
                   mode="RESEARCH_DEFICIT",setpoints=S,weights=W,
                   born_td=TD,world_clock=WORLD)
        self.assertEqual(x["td_updates"],1)
        self.assertEqual(len(x["q_weights"]["primitive:attendre"]),12)
        self.assertEqual(x["native_q_checks"],0)
        self.assertFalse(x["full_q_replay_verified"])
        self.assertEqual(x["adaptive_learning_go"],"NOT_ESTABLISHED")

    def test_tampered_td_return_refused(self):
        with self.assertRaisesRegex(ValueError,"return_g"):
            replay_q(cohort_events(n=2,tamper=True),generation=2,
                status="active",mode="RESEARCH_DEFICIT",
                setpoints=S,weights=W,born_td=TD,world_clock=WORLD)

    def test_changed_frozen_feature_order_refused(self):
        bad=dict(TD,feature_names=tuple(reversed(FEATURES)))
        with self.assertRaises(ValueError):
            replay_q(cohort_events(n=2),generation=2,status="active",
                     mode="RESEARCH_DEFICIT",setpoints=S,weights=W,
                     born_td=bad,world_clock=WORLD)

    def test_missing_td_update_not_silently_accepted(self):
        ev=[e for e in cohort_events(n=2) if e["kind"]!="td_update_published"]
        with self.assertRaisesRegex(ValueError,"missing or spurious"):
            replay_q(ev,generation=2,status="active",
                     mode="RESEARCH_DEFICIT",setpoints=S,weights=W,
                     born_td=TD,world_clock=WORLD)

    def test_lethal_transition_without_synthetic_terminal_credit(self):
        ev=cohort_events(n=2,dead=True)
        x=replay_q(ev,generation=2,status="dead",
                   mode="RESEARCH_DEFICIT",setpoints=S,weights=W,
                   born_td=TD,world_clock=WORLD)
        self.assertEqual(x["td_updates"],0)
        self.assertTrue(x["uncredited_lethal_step"])

    def test_forged_final_q_image_refused(self):
        ev=cohort_events(n=2)
        bad={"config_version": TD["version"],
             "feature_version":TD["feature_version"],
             "weights":{},"traces":{},"update_counts":{},"pending":None}
        with self.assertRaisesRegex(ValueError,"final weights"):
            replay_q(ev,generation=2,status="active",
                     mode="RESEARCH_DEFICIT",setpoints=S,weights=W,
                     born_td=TD,world_clock=WORLD,final_td_state=bad)

    def test_horizon_192_no_h48_assumption(self):
        capture={"kind":"perceptual_capture","t_monde":192,
                 "data":{"capture_t_monde":192,"position":{"x":8,"y":8},
                         "dual_scope_visible_body":dict(S)}}
        v=features(capture,None,world_clock=WORLD,born_td=TD)
        self.assertEqual(len(v),12)
        self.assertEqual(v[7],0.)

    def test_duplicate_competition_refused(self):
        ev=cohort_events(n=2)
        ev.insert(3,copy.deepcopy(ev[2]))
        with self.assertRaises(ValueError):
            replay_q(ev,generation=2,status="active",
                     mode="RESEARCH_DEFICIT",setpoints=S,weights=W,
                     born_td=TD,world_clock=WORLD)

if __name__=="__main__":
    unittest.main()
