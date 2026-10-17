from __future__ import annotations

import unittest

from i0.requests import Request, Response
from lab.request_registry import RequestRegistry, RequestRegistryConfig
from lab.stage7_reference_fixture import build_stage7_reference_runtime


def root_request(
    *,
    ident: str = "req:root",
    emitter: str = "planning",
    recipient: str = "memory",
    question: str = "recall_recent",
    deadline: int = 10,
) -> Request:
    return Request(
        id=ident,
        individual_id="i0",
        emitter=emitter,
        recipient=recipient,
        question=question,
        context_refs=("S_t:1",),
        budget_uc=10,
        budget_cycles=2,
        deadline_value=deadline,
        deadline_unit="pas",
        expected_format="episodes",
        depth=0,
        root_ref=ident,
    )


class RequestRegistryTests(unittest.TestCase):
    def registry(self) -> RequestRegistry:
        return RequestRegistry(
            RequestRegistryConfig(
                version="stage7-request-test-v1",
                recency_window_steps=3,
            )
        )

    def test_depth_greater_than_one_is_rejected_by_contract(self) -> None:
        request = Request(
            id="req:bad-depth",
            individual_id="i0",
            emitter="planning",
            recipient="memory",
            question="recall_recent",
            context_refs=(),
            budget_uc=1,
            budget_cycles=1,
            deadline_value=2,
            deadline_unit="pas",
            expected_format="episodes",
            depth=2,
            root_ref="req:bad-depth",
        )
        with self.assertRaises(ValueError):
            self.registry().register(request, t_monde=1)

    def test_subrequest_cannot_exceed_parent_budget_or_deadline(self) -> None:
        registry = self.registry()
        parent = root_request()
        registry.register(parent, t_monde=1)
        sub = Request(
            id="req:sub",
            individual_id="i0",
            emitter="memory",
            recipient="perception",
            question="context",
            context_refs=(),
            budget_uc=11,
            budget_cycles=2,
            deadline_value=10,
            deadline_unit="pas",
            expected_format="context",
            depth=1,
            root_ref=parent.id,
            parent_ref=parent.id,
        )
        with self.assertRaisesRegex(ValueError, "UC budget"):
            registry.register(sub, t_monde=1)

    def test_two_node_request_cycle_is_rejected(self) -> None:
        registry = self.registry()
        parent = root_request(emitter="planning", recipient="memory")
        registry.register(parent, t_monde=1)
        sub = Request(
            id="req:cycle",
            individual_id="i0",
            emitter="memory",
            recipient="planning",
            question="need-more",
            context_refs=(),
            budget_uc=5,
            budget_cycles=1,
            deadline_value=9,
            deadline_unit="pas",
            expected_format="value",
            depth=1,
            root_ref=parent.id,
            parent_ref=parent.id,
        )
        with self.assertRaisesRegex(ValueError, "cyclic"):
            registry.register(sub, t_monde=1)

    def test_same_question_same_recipient_is_refused_within_W(self) -> None:
        registry = self.registry()
        registry.register(root_request(ident="r1"), t_monde=2)
        with self.assertRaisesRegex(ValueError, "duplicate_recent_question"):
            registry.register(root_request(ident="r2"), t_monde=3)

        registry.register(root_request(ident="r3"), t_monde=5)
        self.assertIn("r3", registry.statuses)

    def test_response_after_step_deadline_becomes_late(self) -> None:
        registry = self.registry()
        request = root_request(deadline=3)
        registry.register(request, t_monde=1)
        delivered = registry.deliver(
            Response(
                request_ref=request.id,
                status="delivered",
                shareable=True,
                produced_t_monde=4,
                content={"episode_ref": "episode:0"},
            ),
            t_monde=4,
        )

        self.assertIsNotNone(delivered)
        self.assertEqual(delivered.status, "late")
        self.assertEqual(
            registry.statuses[request.id].response_status,
            "late",
        )

    def test_cancelled_request_drops_later_response(self) -> None:
        registry = self.registry()
        request = root_request()
        registry.register(request, t_monde=1)
        registry.cancel(request.id, t_monde=2)

        delivered = registry.deliver(
            Response(
                request_ref=request.id,
                status="delivered",
                shareable=True,
                produced_t_monde=2,
                content=[],
            ),
            t_monde=2,
        )
        self.assertIsNone(delivered)


class MemoryRequestIntegrationTests(unittest.TestCase):
    def test_memory_answers_valid_request_without_technical_journal_access(self) -> None:
        runtime = build_stage7_reference_runtime()
        for _ in range(3):
            runtime.run_step()
        self.assertGreater(len(runtime.memory.episodes), 0)

        runtime.stage3.open_step()
        request = root_request(
            ident="req:runtime",
            deadline=runtime.scheduler.t_monde + 2,
        )
        response = runtime.request_memory(request, cycle=0)

        self.assertIsNotNone(response)
        self.assertIn(response.status, {"delivered", "empty"})
        self.assertEqual(
            runtime.request_registry.statuses[request.id].state,
            "closed",
        )

    def test_past_dependent_episode_query_improves_after_experience(self) -> None:
        before = build_stage7_reference_runtime()
        empty_request = root_request(
            ident="req:before-history",
            question="episode:episode:0",
            deadline=10,
        )
        empty_response = before.memory.respond(
            empty_request,
            st=before.s_t.current,
            t_monde=0,
        )
        self.assertEqual(empty_response.status, "empty")

        after = build_stage7_reference_runtime()
        for _ in range(3):
            after.run_step()
        self.assertGreater(len(after.memory.episodes), 0)

        learned_request = root_request(
            ident="req:after-history",
            question="episode:episode:0",
            deadline=10,
        )
        learned_response = after.memory.respond(
            learned_request,
            st=after.s_t.current,
            t_monde=after.scheduler.t_monde,
        )
        self.assertEqual(learned_response.status, "delivered")
        self.assertEqual(
            learned_response.content["id"],
            "episode:0",
        )

    def test_pending_request_status_is_published_in_S_t(self) -> None:
        runtime = build_stage7_reference_runtime()
        request = root_request(
            ident="req:pending",
            deadline=20,
        )
        runtime.request_registry.register(request, t_monde=0)

        runtime.run_step()

        self.assertIsNotNone(runtime.s_t.current)
        self.assertEqual(
            runtime.s_t.current.requests["req:pending"],
            "pending",
        )


if __name__ == "__main__":
    unittest.main()
