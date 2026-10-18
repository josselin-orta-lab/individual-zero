# S1 pilot initial execution: technical blocker (2026-10-18)

- Subject and world preset source: frozen SHA `f87cbc15a34f9b0f2a43749bb2b3377a45401b84`, natural `I1Runtime`.
- Pre-registered pilot: six fixed preset worlds, seed 246, three independent mortal WAL births each, maximum 60 steps per life. No cognitive or world modifications made.
- Executed via [workflow run #39089750371](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39089750371), which checked out the immutable frozen SHA separately from the science observer.
- Result: **TECHNICAL_FAILURE at first `oasis` scenario**. The `Run preregistered independent mortal pilot` step failed with `KeyError: 'consolidated_episode_refs'` while Stage10 attempted publication.
- Source-level cause: `Stage10PublicationCoordinator.publish` constructs `SlowHistory(birth_version=prepared.source_version, birth_state={})`, but `SlowHistory.__init__` requires `birth_state["consolidated_episode_refs"]`. Trace reaches actual `_sleep_step`, `_run_live_consolidation` and `_publish_live_consolidation`.
- Independent correction tracking: [issue #283](https://github.com/josselin-orta-lab/individual-zero/issues/283).
- Workflow archived the run's partial output. It has **not** produced six valid complete scenarios or 18 completed life datasets. The external analyzer did not run; no action means, category percentages, cognitive deltas or learning curves are supported.
- This is not death or non-learning; do not classify technical errors as biological mortality. No retries of the same identity, no rollback, no stage10 bypass and no silent patching of experimental subject.
- Scientific disposition: `BLOCKED_TECHNICAL_FAILURE`. Resume prospective experiments only after a **separate** corrected and validated I1 SHA is formally frozen. Previous failed cohort is retained only as source-specific defect evidence. Do not merge cohorts across versions.
