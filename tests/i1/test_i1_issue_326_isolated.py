import unittest
from i1.experimental.intention_continuity import IntentEvidence, bounded_continuation

class TestContinuity(unittest.TestCase):
    def test_transfer_requires_observed_applied_hop(self):
        prior=IntentEvidence("same-site", 10, (1, 0), 0.8)
        kw=dict(intended_ref="same-site",now_step=11,observed_origin=(1,0),ceiling=0.5,residual=0.5,applied=True)
        self.assertEqual(bounded_continuation(prior,**kw),0.25)
        for delta in (dict(applied=False),dict(now_step=12),dict(observed_origin=(2,0)),dict(intended_ref="different")):
            self.assertIsNone(bounded_continuation(prior,**(kw|delta)))
    def test_invalid_values_fail_closed(self):
        with self.assertRaises(ValueError):
            bounded_continuation(IntentEvidence("a",10,(1,0),0.5),intended_ref="a",now_step=11,observed_origin=(1,0),ceiling=0.5,residual=True,applied=True)
