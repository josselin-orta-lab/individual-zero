"""I1 experimental proximal recall filter. No physics or external truth."""
from __future__ import annotations
from collections.abc import Mapping, Sequence

POLICY = "i1-lived-proximal-review-v1"


def matched_collection_recall(*, episodes: Sequence[object],
                              autobiography: Sequence[Mapping[str, object]],
                              admitted_recall_refs: Sequence[str],
                              t_monde: int, target: str = "berry_b") -> tuple[str, ...]:
    """Return source IDs for past *positive* collected effects, never a safety claim.

    The autobiography must be the authenticated DC-09 projection supplied by
    JournalViews, not technical journal entries or external lab state.
    """
    if type(t_monde) is not int or t_monde < 1 or target != "berry_b":
        return ()
    source = {item.get("event_id"): item for item in autobiography
              if isinstance(item, Mapping) and type(item.get("event_id")) is str}
    admitted = set(admitted_recall_refs)
    found = []
    for episode in episodes:
        ref = getattr(episode, "id", None)
        if ref not in admitted or getattr(episode, "end_t_monde", t_monde) >= t_monde:
            continue
        refs = getattr(episode, "event_refs", ())
        if not isinstance(refs, (tuple, list)) or not refs:
            continue
        # The episode must actually own the complete lived event pair.
        events = [source.get(r) for r in refs]
        if any(e is None for e in events):
            continue
        for cmd in events:
            if (cmd.get("kind") != "command_experienced"
                    or cmd.get("primitive") != "collecter"
                    or cmd.get("parameters") != {"target": target}):
                continue
            step = cmd.get("t_monde")
            if type(step) is not int or step >= t_monde:
                continue
            for outcome in events:
                if outcome.get("kind") != "world_transition_experienced" or outcome.get("t_monde") != step:
                    continue
                effects = outcome.get("effects")
                collected = effects.get("collected") if isinstance(effects, Mapping) else None
                if (isinstance(collected, Mapping)
                        and collected.get("kind") == target
                        and type(collected.get("quantity")) is int
                        and collected["quantity"] > 0):
                    found.append(cmd["event_id"])
                    found.append(outcome["event_id"])
                    break
    return tuple(dict.fromkeys(found))
