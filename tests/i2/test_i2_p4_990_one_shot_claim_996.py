"""No-birth adversarial tests for issue #990 remote single-use claim contract."""
from io import BytesIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.i2_p4_990_one_shot_claim import (
    API_URL, CONSUMED_REF, CONFIRMATION,
    WORKFLOW_REF, REPOSITORY, ClaimRefused, check_preflight, claim_once,
    verify_marker_ruleset,
)

SHA = "a" * 40


def environment(**updates):
    env = {
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_WORKFLOW_REF": WORKFLOW_REF,
        "GITHUB_SHA": SHA,
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_RUN_NUMBER": "1",
        "GITHUB_RUN_ID": "424242",
        "GITHUB_TOKEN": "synthetic-test-only",
        "I2_P4_990_TAG_RULESET_ID": "1234",
    }
    env.update(updates)
    return env


def good_ruleset():
    return {
        "id": 1234, "source": REPOSITORY,
        "target": "tag", "source_type": "Repository",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": [CONSUMED_REF],
                                     "exclude": []}},
        "rules": [{"type": "deletion"}, {"type": "update"}],
        "bypass_actors": [],
    }


class Reply:
    def __init__(self, status, obj):
        self.status = status
        self.data = json.dumps(obj).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.data


class FakeGitHub:
    def __init__(self, *, fail_post=None, move_main=False,
                 ruleset=None, change_ruleset_after_post=False):
        self.refs = {}
        self.ruleset = ruleset
        self.change_ruleset_after_post = change_ruleset_after_post
        self.calls = []
        self.fail_post = fail_post
        self.move_main = move_main

    def __call__(self, request, timeout):
        self.calls.append((request.get_method(), request.full_url))
        if request.get_method() == "GET":
            if request.full_url.endswith("/rulesets/1234"):
                rule = self.ruleset if self.ruleset is not None else good_ruleset()
                if self.change_ruleset_after_post and self.refs:
                    rule = dict(rule, enforcement="disabled")
                return Reply(200, rule)
            self._assert_get(request)
            return Reply(200, {
                "object": {"sha": "b" * 40 if self.move_main else SHA}
            })
        self._assert_post(request)
        if self.fail_post == "timeout":
            raise TimeoutError("synthetic ambiguous response")
        if self.fail_post == "unprocessable":
            raise HTTPError(request.full_url, 422, "already exists", {}, None)
        if self.fail_post == "server":
            raise HTTPError(request.full_url, 503, "temporary", {}, None)
        body = json.loads(request.data)
        if body["ref"] in self.refs:
            raise HTTPError(request.full_url, 422, "duplicate ref", {}, None)
        self.refs[body["ref"]] = body["sha"]
        return Reply(201, {
            "ref": body["ref"], "object": {"sha": body["sha"]}
        })

    @staticmethod
    def _assert_get(request):
        assert request.full_url == (
            API_URL + "/repos/" + REPOSITORY + "/git/ref/heads/main"
        )

    @staticmethod
    def _assert_post(request):
        assert request.full_url == (
            API_URL + "/repos/" + REPOSITORY + "/git/refs"
        )


class SingleUseClaimContract(unittest.TestCase):
    def test_first_claim_then_second_dispatch_refused_without_birth(self):
        fake = FakeGitHub()
        receipt = claim_once(SHA, CONFIRMATION, environ=environment(),
                             opener=fake)
        self.assertEqual(receipt["claim"], "GITHUB_CREATE_REF_201")
        self.assertEqual(fake.refs, {CONSUMED_REF: SHA})
        with self.assertRaisesRegex(ClaimRefused, "verification refused"):
            claim_once(SHA, CONFIRMATION, environ=environment(), opener=fake)
        self.assertEqual(sum(method == "POST" for method, _ in fake.calls), 2)

    def test_second_run_number_and_rerun_attempt_fail_before_network(self):
        for modified in ({"GITHUB_RUN_NUMBER": "2"},
                         {"GITHUB_RUN_ATTEMPT": "2"}):
            fake = FakeGitHub()
            with self.subTest(modified=modified):
                with self.assertRaisesRegex(ClaimRefused, "dispatch context"):
                    claim_once(SHA, CONFIRMATION,
                               environ=environment(**modified), opener=fake)
                self.assertEqual(fake.calls, [])

    def test_wrong_context_or_confirmation_fail_before_network(self):
        changes = [
            {"GITHUB_REF": "refs/heads/feature"},
            {"GITHUB_EVENT_NAME": "pull_request"},
            {"GITHUB_WORKFLOW_REF": "wrong"},
            {"GITHUB_REPOSITORY": "another/repo"},
            {"GITHUB_SHA": "b" * 40},
            {"GITHUB_RUN_ID": "1;unsafe"},
        ]
        for changed in changes:
            fake = FakeGitHub()
            with self.subTest(changed=changed):
                with self.assertRaises(ClaimRefused):
                    claim_once(SHA, CONFIRMATION,
                               environ=environment(**changed), opener=fake)
                self.assertEqual(fake.calls, [])
        with self.assertRaises(ClaimRefused):
            check_preflight(SHA, "NOT-CONFIRMED", environment())
        with self.assertRaises(ClaimRefused):
            check_preflight("bad", CONFIRMATION, environment())

    def test_missing_token_fails_before_network(self):
        fake = FakeGitHub()
        with self.assertRaisesRegex(ClaimRefused, "token required"):
            claim_once(SHA, CONFIRMATION,
                       environ=environment(GITHUB_TOKEN=""), opener=fake)
        self.assertEqual(fake.calls, [])

    def test_main_moved_refused_without_create(self):
        fake = FakeGitHub(move_main=True)
        with self.assertRaisesRegex(ClaimRefused, "main moved"):
            claim_once(SHA, CONFIRMATION, environ=environment(), opener=fake)
        self.assertEqual([m for m, _ in fake.calls], ["GET", "GET"])

    def test_ambiguous_post_never_retried(self):
        for failure in ("timeout", "unprocessable", "server"):
            with self.subTest(failure=failure):
                fake = FakeGitHub(fail_post=failure)
                with self.assertRaisesRegex(ClaimRefused,
                                            "verification refused"):
                    claim_once(SHA, CONFIRMATION, environ=environment(),
                               opener=fake)
                self.assertEqual([m for m, _ in fake.calls], ["GET", "GET", "POST"])

    def test_ruleset_missing_is_refused_before_network(self):
        fake = FakeGitHub()
        with self.assertRaisesRegex(ClaimRefused, "ruleset id required"):
            claim_once(SHA, CONFIRMATION,
                       environ=environment(I2_P4_990_TAG_RULESET_ID=""),
                       opener=fake)
        self.assertEqual(fake.calls, [])

    def test_wrong_or_bypassable_ruleset_refused_before_tag_creation(self):
        invalid = [
            dict(good_ruleset(), id=4321),
            dict(good_ruleset(), source="different/repository"),
            dict(good_ruleset(), target="branch"),
            dict(good_ruleset(), enforcement="evaluate"),
            dict(good_ruleset(), rules=[{"type": "deletion"}]),
            dict(good_ruleset(), bypass_actors=[{
                "actor_id": 5, "actor_type": "RepositoryRole",
                "bypass_mode": "always"}]),
            dict(good_ruleset(), conditions={"ref_name": {
                "include": ["refs/tags/*"], "exclude": []}}),
            dict(good_ruleset(), conditions={"ref_name": {
                "include": [CONSUMED_REF], "exclude": ["refs/tags/*"]}}),
        ]
        for rule in invalid:
            with self.subTest(rule=rule):
                fake = FakeGitHub(ruleset=rule)
                with self.assertRaisesRegex(ClaimRefused, "not protected"):
                    claim_once(SHA, CONFIRMATION,
                               environ=environment(), opener=fake)
                self.assertEqual([m for m, _ in fake.calls], ["GET"])
                self.assertFalse(fake.refs)

    def test_ruleset_disabled_after_marker_creation_refuses_birth(self):
        fake = FakeGitHub(change_ruleset_after_post=True)
        with self.assertRaisesRegex(ClaimRefused, "not protected"):
            claim_once(SHA, CONFIRMATION, environ=environment(), opener=fake)
        self.assertEqual(fake.refs, {CONSUMED_REF: SHA})
        self.assertEqual([m for m, _ in fake.calls],
                         ["GET", "GET", "POST", "GET"])

    def test_idempotent_no_birth_no_chosen_actions_no_secrets_in_receipt(self):
        fake = FakeGitHub()
        receipt = claim_once(SHA, CONFIRMATION, environ=environment(),
                             opener=fake)
        self.assertEqual(receipt["scientific_result"],
                         "NOT_EXECUTED_BY_THIS_GUARD")
        self.assertFalse(receipt["m11_authenticated"])
        self.assertNotIn("synthetic-test-only", json.dumps(receipt))
        self.assertEqual(receipt["consumed_ref"], CONSUMED_REF)


if __name__ == "__main__":
    unittest.main()
