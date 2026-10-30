"""Synthetic cold geographical counterfeits, no I1 births."""
import unittest
from copy import deepcopy
from i1_a2r_geographic_history_cold import replay_geographic_history
def fixture():
    born={"scope":"SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE",
        "q_at_birth_empty":True,"born_temperament":{"exploration_coefficient":0.},
        "stage11_geographic_max_distinct_sites":3,
        "initial_exploration":{"state_schema":"exploration-activity-v3-geographic",
        "config_version":"e","coefficient":0.,
        "geography":{"schema":"geographic-exploration-v1","version":"g",
                     "visits":[],"last_capture":None}}}
    final={"state_schema":"exploration-activity-v3-geographic",
        "config_version":"e","coefficient":0.,
        "geography":{"schema":"geographic-exploration-v1","version":"g",
                     "visits":[[1,1,1]],"last_capture":[1,1,1]}}
    events=[{"kind":"perceptual_capture","t_monde":1,"data":{
        "capture_t_monde":1,"position":{"x":1,"y":1}}},
        {"kind":"stage11_geographic_visit_observed","t_monde":1,
         "data":{"source":"perception_capture","world_step":1,"position":[1,1],
             "new_distinct_sites":1,"visit_count":1}},
        {"kind":"stage11_geographic_option_proposed","t_monde":1,"cycle":1,
         "data":{"source":"single_perceptual_capture",
             "target_ref":"frontier:2:1:from:1:1",
             "option_ref":"option:geographic:frontier:2:1:from:1:1",
             "destination":[2,1],"direction":"east","goal_ref":None}}]
    return events,final,born
class Tests(unittest.TestCase):
    def call(self,events,final,born):
        return replay_geographic_history(events,final_exploration=final,birth=born,generation=1)
    def test_valid_grounding_still_no_go(self):
        e,f,b=fixture()
        x=self.call(e,f,b)
        self.assertEqual(x["direct_frontier_candidates_checked"],1)
        self.assertEqual(x["direct_frontier_passability_cues_absent"],1)
        self.assertFalse(x["study_admissible"])
    def test_missing_visit_rejected(self):
        e,f,b=fixture()
        with self.assertRaises(ValueError):self.call([e[0],e[2]],f,b)
    def test_visited_frontier_rejected(self):
        e,f,b=fixture()
        e[2]["data"]["destination"]=[1,1]
        with self.assertRaises(ValueError):self.call(e,f,b)
    def test_final_signed_owner_disagreement(self):
        e,f,b=fixture()
        f["geography"]["visits"]=[]
        with self.assertRaises(ValueError):self.call(e,f,b)
    def test_forged_passability_cue_rejected(self):
        e,f,b=fixture()
        e[0]["data"].update(
            agency_capture_schema="stage12-first-person-cue-v1",
            agency_visible_adjacent=[{"direction":"east","x":2,"y":1,"passable":False}])
        with self.assertRaises(ValueError):self.call(e,f,b)
    def test_duplicate_visit_refused(self):
        e,f,b=fixture()
        with self.assertRaises(ValueError):self.call(e[:2]+[deepcopy(e[1]),e[2]],f,b)
if __name__=="__main__":unittest.main()
