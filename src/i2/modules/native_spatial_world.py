"""P1: I2-owned minimal traversable *physical* space, no cognition owner.

Three site names and adjacency only. No site contains a predicted reward.
The current place is replayed exclusively from admitted native motor events
under the existing one-owner SQLite hash chain. No map memory or path planner.
"""
from __future__ import annotations

BORN_SITE = "camp"
GRAPH = {
    "camp": ("passage",),
    "passage": ("camp", "source"),
    "source": ("passage",),
}
MOTIONS = {("se_deplacer_vers_" + dest): dest for dest in GRAPH}


def offered_moves(site):
    if site not in GRAPH:
        raise ValueError("unknown born-world site")
    return tuple("se_deplacer_vers_" + dest for dest in GRAPH[site])


def destination(action):
    if type(action) is not str:
        raise ValueError("movement semantic must be exact string")
    return MOTIONS.get(action)


def site_after(site, action):
    """Return new site only for an actually admitted adjacent move."""
    dest = destination(action)
    if dest is None or dest not in GRAPH.get(site, ()):
        raise ValueError("not an adjacent paid movement")
    return dest


def replay_site(rows, *, enabled):
    """Rows are the single owner's previously committed physical events."""
    if type(enabled) is not bool:
        raise ValueError("born spatial flag must be exact boolean")
    site = BORN_SITE
    for row in rows:
        dest = destination(row[2])
        if dest is not None:
            if not enabled:
                raise ValueError("movement committed in nonspatial birth")
            site = site_after(site, row[2])
    return site


def local_evidence(site):
    """The current site + directly reachable neighbor identities ONLY."""
    return tuple(sorted(
        ("evidence:i2:spatial:current:" + site,) +
        tuple("evidence:i2:spatial:neighbor:" + neighbor
              for neighbor in GRAPH[site])
    ))
