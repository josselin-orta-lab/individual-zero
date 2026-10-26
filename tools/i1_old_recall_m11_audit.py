"""Operator-only verification of old-episode recall in committed I1 M11 steps.

No Memory reads, runtime mutation, hidden world information, or motor access.
Synthetic event tests establish L1; only authentic M11 journals can establish L2.
"""

def audit_old_recall_step(*, events, world_step, preclosed, newly_closed,
                          previous_commits):
    """Check the chronological Memory -> UC -> observed-source chain."""
    owners = {}
    for episode in preclosed:
        for ref in episode["event_refs"]:
            owners.setdefault(ref, []).append(episode["id"])
    closed = list(preclosed)
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
            if not isinstance(data, dict) or data not in newly_closed:
                raise ValueError("unowned same-step closed episode")
            if any(e["id"] == data["id"] for e in closed):
                raise ValueError("duplicate closed episode")
            closed.append(data)
            for ref in data["event_refs"]:
                owners.setdefault(ref, []).append(data["id"])
        if kind == "memory_recall_proposed":
            if not isinstance(data, dict) or not isinstance(data.get("episode_ref"), str):
                raise ValueError("invalid Memory recall proposal")
            proposals.append((index, event, len(closed)))
        if is_old_charge:
            if (data.get("module") != "planning"
                    or data.get("requested_uc") != 8
                    or type(data.get("accepted")) is not bool):
                raise ValueError("invalid old-memory UC charge")
            paid.append((index, event))
            if data["accepted"]:
                accepted.append((index, event))
        if kind == "i1_old_episode_paid_observation":
            observed.append((index, event))
    if len(accepted) > 1 or len(observed) > 1 or len(paid) > 1:
        raise ValueError("duplicate old-memory charge or observation")
    def valid_old_proposals(before_index, cycle):
        matches = []
        for index, event, count in proposals:
            episode = event["data"]["episode_ref"]
            if (index >= before_index or event.get("cycle") != cycle
                    or not episode.startswith("episode:")
                    or not episode[8:].isascii() or not episode[8:].isdigit()
                    or str(int(episode[8:])) != episode[8:]
                    or int(episode[8:]) >= count - 32):
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
    for obs_index, event in observed:
        data = event.get("data")
        if not isinstance(data, dict):
            raise ValueError("invalid old-memory observation")
        ref = data.get("episode_ref")
        sources = data.get("source_event_refs")
        if (type(ref) is not str or type(sources) is not list
                or not 1 <= len(sources) <= 2
                or len(set(sources)) != len(sources)
                or any(type(x) is not str for x in sources)
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
        matches = [e for e in closed if e["id"] == ref]
        if len(matches) != 1 or set(matches[0]["event_refs"]) != set(sources):
            raise ValueError("closed Memory source set mismatch")
        if any(owners.get(x) != [ref] or previous_commits.get(x, world_step) >= world_step
               for x in sources):
            raise ValueError("source lacks unique old committed custody")
        if (type(data.get("witnesses")) is not list
                or len(data["witnesses"]) > 2):
            raise ValueError("unexpected unbounded lived witnesses")
        success.append(ref)
    return {
        "schema": "i1-old-recall-natural-m11-audit-v1",
        "memory_recall_proposals": len(proposals),
        "old_memory_recall_proposals": sum(
            any(x[0] == index for x in valid_old_proposals(index + 1, event.get("cycle")))
            for index, event, count in proposals
        ),
        "old_read_charges": len(paid),
        "accepted_old_read_charges": len(accepted),
        "authentic_old_consultations": len(success),
        "episode_refs": success,
        "l2_positive": ("OBSERVED" if success else "NOT_OBSERVED"),
        "l3_decision_influence": "NOT_ESTABLISHED",
    }
