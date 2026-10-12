"""Conservative physical step-boundary preflight over a canonical journal.

This checks recorded opening/closing pairs only. It is not the full
independent journal audit and does not verify the physical world.
"""
from __future__ import annotations

import json
from pathlib import Path

from .journal_preflight import check_chain


def check_step_boundaries(path: Path) -> dict:
    chain = check_chain(path)
    result = {"recorded_boundaries_valid": False, "closed_steps": [],
              "terminal_death_recorded": False, "full_causal_audit": False,
              "map_authorized": False, "error": None}
    if not chain["chain_valid"]:
        result["error"] = "invalid_canonical_chain"
        return result
    try:
        with path.open("rb") as stream:
            raw = stream.read(32 * 1024 * 1024 + 1)
        rows = [json.loads(line) for line in raw.split(b"\n")]
        opened = {}
        closed = {}
        terminal = False
        active_step = None
        terminal_step = None
        last_step = 0
        for row in rows:
            event = row["causal_event"]
            kind = event.get("kind")
            if terminal and kind != "step_closed":
                raise ValueError("event_after_death")
            if kind not in {"step_opened", "step_closed", "individual_death_confirmed"}:
                continue
            step = event.get("t_monde")
            attempt = event.get("attempt_ref")
            if type(step) is not int or step < 1 or not isinstance(attempt, str) or not attempt:
                raise ValueError("invalid_step_provenance")
            if kind == "step_opened":
                if active_step is not None or step != last_step + 1 or step in opened:
                    raise ValueError("nonconsecutive_or_duplicate_open")
                opened[step] = attempt
                active_step = step
                last_step = step
            elif kind == "step_closed":
                if active_step != step or opened.get(step) != attempt or step in closed:
                    raise ValueError("unmatched_close")
                if terminal and terminal_step != step:
                    raise ValueError("invalid_terminal_close")
                closed[step] = attempt
                active_step = None
            else:
                if terminal or active_step != step or opened.get(step) != attempt or step in closed:
                    raise ValueError("invalid_terminal_event")
                terminal = True
                terminal_step = step
        if active_step is not None or opened != closed:
            raise ValueError("incomplete_step")
        result["recorded_boundaries_valid"] = True
        result["closed_steps"] = sorted(closed)
        result["terminal_death_recorded"] = terminal
        return result
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        result["error"] = "invalid_or_incomplete_step_boundaries"
        return result
