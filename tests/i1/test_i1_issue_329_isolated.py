import unittest
from types import SimpleNamespace
from i1.experimental.critical_alert_wake import critical_alert_channels

class Alert(unittest.TestCase):
    def test_read_only_physiological_alert(self):
        pending=SimpleNamespace(woke=True,reason="alert",world_step=3)
        capture=SimpleNamespace(t_monde=3,body=dict(energy=70,food=10,water=8,integrity=95))
        k=dict(pending=pending,sleep_mode="awake",world_step=3,capture=capture,thresholds=dict(energy=10,food=10,water=10,integrity=10))
        self.assertEqual(critical_alert_channels(**k),("water","food"))
        self.assertEqual(critical_alert_channels(**(k|dict(sleep_mode="sleeping"))),())
        with self.assertRaises(RuntimeError):
            critical_alert_channels(**(k|dict(capture=SimpleNamespace(t_monde=3,body={}))))
