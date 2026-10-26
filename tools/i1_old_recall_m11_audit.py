"""Operator-only verification of old-episode recall in committed I1 M11 steps.

No Memory reads, runtime mutation, hidden world information, or motor access.
Synthetic event tests establish L1; only authentic M11 journals can establish L2.
"""

def audit_old_recall_step(*, events, world_step, preclosed, newly_closed,
                          previous_commits):
    """Check the chronological Memory -> UC -> observed-source chain."""
    # Do not rebuild the life-long source-owner index on every M11 step.
    # Reconstruct only when an actual old consultation must be attested.
    closed_count = len(preclosed)
    newly_seen = set()
    closed_this_step = []
    proposals, paid, observed = [], [], []
    accepted = []
    for index, event in enumerate(events):
        kind, data = event.get("kind"), event.get("data")
        is_old_charge = (kind == "compute_charge"
                         and isinstance(data, dict)
                         and data.get("operation") == "i1_bounded_old_episode_recall")
        if (kind in {"episode_closed", "memory_recall_proposed",
                     "i1_old_episode_paid_observation"} or is_old_charge):
            if event.get("t_monde") != world_step:
                raise ValueError("cross-step old recall occurrence")
        if kind == "episode_closed":
            if (type(data) is not dict
                    or type(data.get("id")) is not str
                    or type(data.get("event_refs")) is not list
                    or any(type(ref) is not str or not ref
                           for ref in data["event_refs"])
                    or len(closed_this_step) >= len(newly_closed)
                    or data != newly_closed[len(closed_this_step)]):
                raise ValueError("unowned, out-of-order or malformed same-step closure")
            if (data["id"] in newly_seen
                    or any(episode.get("id") == data["id"]
                           for episode in preclosed)):
                raise ValueError("duplicate closed episode")
            newly_seen.add(data["id"])
            closed_this_step.append(data)
            closed_count += 1
        if kind == "memory_recall_proposed":
            if not isinstance(data, dict) or type(data.get("episode_ref")) is not str:
                raise ValueError("invalid Memory recall proposal")
            episode_ref = data["episode_ref"]
            cycle = event.get("cycle")
            if (type(cycle) is not int or cycle < 1
                    or data.get("subject_ref") != f"episode:{episode_ref}"
                    or data.get("contribution_ref") !=
                       f"memory-recall:{episode_ref}:{world_step}:{cycle}"):
                raise ValueError("unauthenticated Memory contribution identity")
            # Preserve the number of closures already witnessed, not merely
            # the final set of owners at the end of the physical step.
            proposals.append((index, event, closed_count,
                              len(closed_this_step)))
        if is_old_charge:
            if (data.get("module") != "planning"
                    or type(data.get("count")) is not int
                    or data["count"] != 1
                    or data.get("requested_uc") != 8
                    or type(data.get("accepted")) is not bool):
                raise ValueError("invalid old-memory UC charge")
            paid.append((index, event))
            if data["accepted"]:
                accepted.append((index, event))
        if kind == "i1_old_episode_paid_observation":
            observed.append((index, event, len(closed_this_step)))
    if len(accepted) > 1 or len(observed) > 1 or len(paid) > 1:
        raise ValueError("duplicate old-memory charge or observation")
    def chronological_old_episode(episode, count, closed_at_proposal):
        # Native episode IDs are labels, not evidence of chronological order.
        # Verify that the actual Memory owner occupying the ordinal slot
        # already existed at the precise moment of the recall proposal.
        if type(episode) is not str or not episode.startswith("episode:"):
            return False
        suffix = episode[8:]
        if (not suffix or len(suffix) > 18 or not suffix.isascii()
                or not suffix.isdigit() or str(int(suffix)) != suffix):
            return False
        ordinal = int(suffix)
        if ordinal >= count - 32:
            return False
        if ordinal < len(preclosed):
            owner = preclosed[ordinal]
        else:
            offset = ordinal - len(preclosed)
            if offset >= closed_at_proposal:
                return False
            owner = closed_this_step[offset]
        return isinstance(owner, dict) and owner.get("id") == episode

    def valid_old_proposals(before_index, cycle):
        matches = []
        for index, event, count, closed_at_proposal in proposals:
            episode = event["data"]["episode_ref"]
            if (index >= before_index or event.get("cycle") != cycle
                    or not chronological_old_episode(
                        episode, count, closed_at_proposal)):
                continue
            matches.append((index, event, count))
        return matches

    # A paid attempt is never a silent anomaly: it must follow an authentic
    # newly emitted, native old Memory proposal in its own cognitive cycle.
    for debit_index, debit in paid:
        if (debit.get("cycle") != 1
                or len(valid_old_proposals(debit_index, debit.get("cycle"))) != 1):
            raise ValueError("old-memory charge without current old recall")

    success = []
    for obs_index, event, closed_before_observation in observed:
        data = event.get("data")
        if not isinstance(data, dict):
            raise ValueError("invalid old-memory observation")
        ref = data.get("episode_ref")
        sources = data.get("source_event_refs")
        if (type(ref) is not str or type(sources) is not list
                or not 1 <= len(sources) <= 2
                or any(type(x) is not str or not x for x in sources)
                or len(set(sources)) != len(sources)
                or data.get("charged_operation") != "i1_bounded_old_episode_recall"
                or data.get("charged_uc") != 8
                or any(data.get(k) is not False for k in (
                    "decision_evidence", "causal_attribution",
                    "q_or_p40_augmented", "motor_permission"))):
            raise ValueError("invalid old-memory receipt")
        if len(accepted) != 1:
            raise ValueError("unpaid old-memory observation")
        debit_index, debit = accepted[0]
        same = [(i, p, n) for i, p, n in
                valid_old_proposals(debit_index, event.get("cycle"))
                if p["data"]["episode_ref"] == ref
                and debit.get("cycle") == event.get("cycle")
                and i < debit_index < obs_index]
        if len(same) != 1:
            raise ValueError("missing same-cycle prior spontaneous recall")
        _, _, count_at_proposal = same[0]
        if not ref.startswith("episode:") or not ref[8:].isascii() or not ref[8:].isdigit():
            raise ValueError("invalid old episode ordinal")
        ordinal = int(ref[8:])
        if ordinal >= count_at_proposal - 32:
            raise ValueError("recalled episode is not older than 32")
        closed = list(preclosed) + closed_this_step[:closed_before_observation]
        matches = [e for e in closed if e["id"] == ref]
        if len(matches) != 1 or set(matches[0]["event_refs"]) != set(sources):
            raise ValueError("closed Memory source set mismatch")
        owners = {source: [] for source in sources}
        for episode in closed:
            for source in episode["event_refs"]:
                if source in owners:
                    owners[source].append(episode["id"])
        if any(owners.get(x) != [ref] or previous_commits.get(x, world_step) >= world_step
               for x in sources):
            raise ValueError("source lacks unique old committed custody")
        if (type(data.get("witnesses")) is not list
                or len(data["witnesses"]) > 2):
            raise ValueError("unexpected unbounded lived witnesses")
        for witness in data["witnesses"]:
            if (type(witness) is not dict
                    or type(witness.get("step")) is not int
                    or not 1 <= witness["step"] < world_step
                    or type(witness.get("source_event_refs")) not in (tuple, list)
                    or len(witness["source_event_refs"]) != 2
                    or any(type(x) is not str or not x
                           for x in witness["source_event_refs"])
                    or set(witness["source_event_refs"]) != set(sources)
                    or type(witness.get("source_episode_refs")) not in (tuple, list)
                    or list(witness["source_episode_refs"]) != [ref]
                    or witness.get("causal_attribution") is not False
                    or witness.get("decision_evidence") is not False):
                raise ValueError("old-memory action witness lacks exact custody")
        success.append(ref)
    return {
        "schema": "i1-old-recall-natural-m11-audit-v1",
        "memory_recall_proposals": len(proposals),
        "old_memory_recall_proposals": sum(
            event.get("cycle") == 1
            and chronological_old_episode(
                event["data"]["episode_ref"], count, closed_at_proposal)
            for index, event, count, closed_at_proposal in proposals
        ),
        "old_read_charges": len(paid),
        "accepted_old_read_charges": len(accepted),
        "authentic_old_consultations": len(success),
        "episode_refs": success,
        "l2_positive": ("OBSERVED" if success else "NOT_OBSERVED"),
        "l3_decision_influence": "NOT_ESTABLISHED",
    }
