"""Stage-10 autonomous real WorldBody life through full atomic h publication.

No fixture manufactures a Memory episode, a plan success, an online update,
or an independent scientific result. The sleep option is actually selected,
applied, and one life is advanced until its own verified autobiographical
episodes trigger a private consolidation, then a coordinated publication.
"""
import unittest

from lab.stage10_reference_fixture import build_stage10_reference_runtime


class Stage10RealConsolidationLifeTests(unittest.TestCase):
    def test_lived_episode_consolidates_and_commits_all_active_owner_forms(self):
        r=build_stage10_reference_runtime(consolidation_life=True)
        old=r.slow_history.current_version
        modes=[]
        for _ in range(45):
            step=r.run_step()
            self.assertEqual(step.execution_status,"applied")
            self.assertEqual(r.scheduler.active_attempt,None)
            self.assertEqual(r.world.position, r.world.position)
            modes.append(step.source)
            if r.slow_history.current_version!=old:
                break
        self.assertIn("decision",modes)
        self.assertIn("sleep",modes)
        self.assertNotEqual(r.slow_history.current_version,old)
        self.assertTrue(r.journal.verify())
        self.assertIsNone(r.consolidation.current)
        versions=[row for row in r.journal.entries
                  if row.causal_event["kind"]=="stage10_consolidation_version_activated"]
        self.assertEqual(len(versions),1)
        technical=versions[0].causal_event["data"]
        self.assertEqual(technical["source_history_version"],old)
        self.assertEqual(technical["new_history_version"],r.slow_history.current_version)
        history=r.slow_history.read_committed()
        self.assertTrue(history["consolidated_episode_refs"])
        self.assertEqual(set(history["forms"]),
                         set(r.publication.owners))
        for name,owner in r.publication.owners.items():
            # Causal snapshots can contain tuples, while the slow-history
            # portable h_new uses canonical JSON; compare canonical bytes.
            from lab.determinism import canonical_causal_bytes
            self.assertEqual(
                canonical_causal_bytes(history["forms"][name]),
                canonical_causal_bytes(owner.export_causal_state()),
            )
        self.assertEqual(
            [item["status"] for item in history["hypotheses"]],
            ["hypothese_causale"]*len(history["hypotheses"]),
        )
        self.assertEqual(
            r.causal_model.export_causal_state()["consolidated_hypotheses"],
            history["hypotheses"],
        )

    def test_exact_reexecution_is_deterministic_even_with_private_work(self):
        a=build_stage10_reference_runtime(consolidation_life=True)
        b=build_stage10_reference_runtime(consolidation_life=True)
        for _ in range(12):
            x=a.run_step()
            y=b.run_step()
            self.assertEqual(x.source,y.source)
            self.assertEqual(a.scheduler.t_monde,b.scheduler.t_monde)
            self.assertEqual(a.journal.canonical_bytes(),b.journal.canonical_bytes())
        self.assertEqual(a.slow_history.export_causal_state(),
                         b.slow_history.export_causal_state())

if __name__=="__main__":
    unittest.main()
