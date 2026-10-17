"""External A2.12 diagnosis never treats unseen keys as predicted effects."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_a212 import diff_features


class ExactKeyMismatchTests(unittest.TestCase):
    def test_unseen_command_is_not_guessed(self):
        row={"command":{"primitive":"fabriquer_outil","parameters":{}},
             "state":{"x":2}}
        result=diff_features(row,[])
        self.assertEqual(result["category"],"unseen_command")

    def test_mismatched_body_is_not_called_a_supported_key(self):
        class Entry:
            def __init__(self):
                self.command=type("Cmd",(),{"as_dict":lambda _: {"primitive":"attendre","parameters":{}}})()
                self.state=type("State",(),{"as_dict":lambda _: {
                    "x":2,"y":2,"body":{"food":35.0},"inventory":{},
                    "current_water_source":False,"current_resources":[],
                    "adjacent":[],"known_shelter_here":False,"is_night":False}})()
        q={"command":{"primitive":"attendre","parameters":{}},
           "state":{"x":2,"y":2,"body":{"food":34.0},"inventory":{},
                    "current_water_source":False,"current_resources":[],
                    "adjacent":[],"known_shelter_here":False,"is_night":False}}
        d=diff_features(q,[Entry()])
        self.assertEqual(d["category"],"unseen_state_for_known_command")
        self.assertEqual(d["closest_differing_fields"],["body"])

if __name__=="__main__":
    unittest.main()
