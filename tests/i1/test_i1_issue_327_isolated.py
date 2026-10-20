import unittest
from types import SimpleNamespace
from i1.experimental.local_opportunity_selection import local_interaction_choices,local_q_visibility

class TestLocal(unittest.TestCase):
    def test_no_unearned_command(self):
        commands=tuple(SimpleNamespace(primitive=p) for p in ("boire","attendre","collecter"))
        self.assertEqual([x.primitive for x in local_interaction_choices(commands,enabled=True)],["boire","collecter"])
        self.assertEqual(local_interaction_choices(commands,enabled=False),())
        self.assertEqual(local_q_visibility("neutral"),(False,False))
        self.assertEqual(local_q_visibility("learned"),(True,True))
        with self.assertRaises(ValueError):local_q_visibility("forced")
