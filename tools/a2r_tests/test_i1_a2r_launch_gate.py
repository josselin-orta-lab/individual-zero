"""Pure A2-R context admission tests. No GitHub run, I1 birth, or cohort."""
import unittest

from i1_a2r_archive_guard import canonical_bytes, origin_lock
from i1_eco_a2r_launch_gate import (
    REPOSITORY, WORKFLOW_REF, PROTOCOL, validate_launch_context,
)
from hashlib import sha256


def fixture():
    source = "a" * 40
    tree = "b" * 40
    preset = "c" * 64
    lock = canonical_bytes(origin_lock(
        source_commit=source, source_tree=tree,
        preset_sha256=preset, run_id=12345))
    digest = sha256(lock).hexdigest()
    github = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_WORKFLOW_REF": WORKFLOW_REF,
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_RUN_ID": "12345",
        "GITHUB_SHA": source,
    }
    approval = {
        "A2R_REVIEWED_PROTOCOL": PROTOCOL,
        "A2R_REVIEWED_SOURCE_SHA": source,
        "A2R_REVIEWED_LOCK_SHA256": digest,
        "A2R_REVIEWED_RUN_ID": "12345",
    }
    return dict(role="native", seed=2001, mode="CANONICAL_ABS",
                raw_lock=lock, externally_pinned_sha256=digest,
                github=github, approval=approval)


class GateTests(unittest.TestCase):
    def test_exact_claims_are_only_preflight_not_authorization(self):
        result = validate_launch_context(**fixture())
        self.assertEqual(result["seed"], 2001)
        self.assertEqual(result["github_run_id"], 12345)
        self.assertFalse(result["cohort_launch_authorized_by_this_module"])
        self.assertFalse(result["external_run_event_independently_verified"])
        self.assertFalse(result["protected_environment_review_independently_verified"])

    def test_bad_origin_and_outside_matrix(self):
        for mutation in ("role", "seed", "mode", "digest", "lock"):
            args = fixture()
            if mutation == "role": args["role"] = "other"
            if mutation == "seed": args["seed"] = 2025
            if mutation == "mode": args["mode"] = "masked"
            if mutation == "digest": args["externally_pinned_sha256"] = "d" * 64
            if mutation == "lock": args["raw_lock"] += b" "
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_launch_context(**args)

    def test_no_retry_dispatch_or_pr_source(self):
        for key, value in (
            ("GITHUB_RUN_ATTEMPT", "2"),
            ("GITHUB_EVENT_NAME", "pull_request"),
            ("GITHUB_REF", "refs/heads/research"),
            ("GITHUB_REPOSITORY", "other/repo"),
            ("GITHUB_WORKFLOW_REF", "unregistered"),
            ("GITHUB_SHA", "d" * 40),
            ("GITHUB_RUN_ID", "12346"),
            ("GITHUB_RUN_ID", "0"),
        ):
            args=fixture()
            args["github"][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):
                validate_launch_context(**args)

    def test_unreviewed_run_and_source_rejected(self):
        for key, value in (
            ("A2R_REVIEWED_RUN_ID", "12346"),
            ("A2R_REVIEWED_SOURCE_SHA", "d"*40),
            ("A2R_REVIEWED_LOCK_SHA256", "e"*64),
            ("A2R_REVIEWED_PROTOCOL", "other"),
        ):
            args=fixture()
            args["approval"][key]=value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_launch_context(**args)

    def test_duplicate_json_key_rejected(self):
        args=fixture()
        args["raw_lock"]=args["raw_lock"].replace(
            b'"authorization":', b'"authorization":"injected","authorization":')
        args["externally_pinned_sha256"]=sha256(args["raw_lock"]).hexdigest()
        args["approval"]["A2R_REVIEWED_LOCK_SHA256"]=args["externally_pinned_sha256"]
        with self.assertRaises(ValueError):
            validate_launch_context(**args)


if __name__ == "__main__":
    unittest.main()
