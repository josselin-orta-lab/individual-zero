"""Observer-only incremental first-seen provenance for committed M11 Memory.

The current full owner-exported seen-ref set is still reconstructed each step:
this is required by the existing per-step custody checks. Only the redundant
Python-level walk of all previous refs for first-ingestion timestamps is
replaced with a difference in C and an update of genuinely new refs.

This helper cannot read, write, or become an owner of I1's Memory state.
"""


def update_first_memory_ingestion(first_ingestion, current_seen, *, world_step):
    """Record only newly witnessed Memory sources after an M11 COMMIT.

    The caller has already reconstructed current_seen from the authenticated
    post-step owner export and must continue using that complete set for all
    same-step provenance audits. A disappearing previously seen source fails
    closed instead of silently retaining its stale first-ingestion witness.
    """
    if (type(first_ingestion) is not dict
            or type(current_seen) is not set
            or type(world_step) is not int or world_step < 1):
        raise RuntimeError("invalid M11 first-ingestion index input")
    if not first_ingestion.keys() <= current_seen:
        raise RuntimeError("M11 Memory seen sources regressed")
    newly_ingested = current_seen.difference(first_ingestion)
    if any(type(ref) is not str or not ref for ref in newly_ingested):
        raise RuntimeError("invalid newly ingested Memory source reference")
    # Do not rewrite first dates for old refs. All validation precedes update.
    first_ingestion.update(dict.fromkeys(newly_ingested, world_step))
    return len(newly_ingested)
