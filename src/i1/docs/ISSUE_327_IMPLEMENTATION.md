# Issue #327: isolated continuation work

Origin: experimental PR #318. Base main: `756aebe79db3f468a33919afe5f1a42b6e91f00f`.

Extracts only opt-in availability and Q-exposure helpers from PR #318, without attaching any second producer, modifying birth, or promoting NO-GO behavior.

The actual implementation in this PR is `src/i1/experimental/local_opportunity_selection.py`, with an independent technical unit test in `tests/i1/test_i1_issue_327_isolated.py`.

**No canonical activation**, no motor authority, no change to I0, M11, birth, Competition thresholds, TD, sleep or irreversible death. This is an isolated work package, **not scientific GO**. Review and separate PR required before any promotion. No new behavioral or population campaigns are requested.
