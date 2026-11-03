# P1 I2 native minimal physical space (research-only)

**Owner-approved [P1 #923](https://github.com/josselin-orta-lab/individual-zero/issues/923) under
[ADR-0011](../../../docs/decisions/ADR-0011-i2-integrated-spatial-life-priorities.md).**
Engineering experiment; **no learning of place value** yet.

## Fixed world and physical meaning

A new birth flag `spatial_world=True` (default False) fixes a 3-site chain:
`camp <-> passage <-> source`, with initial current site `camp`.
Only the **current** site and physically adjacent *neighbor names*
appear in first-person capture evidence. This graph contains no source
quality, nutrition, reward, distance oracle or future world change.

Offered `se_deplacer_vers_<neighbor>` actions are only to adjacent sites.
If and only if the existing paid Competition selects one and fresh
Action Control admits it, the same native SQLite owner commits a standard
`se_deplacer` physical transition (2 body-energy units plus ordinary UC)
and the next capture sees the newly reached site. An edge move is
not available with fewer than 2 physical energy units; native motor
admission and independent cold audit reject unaffordable movement. The position is
**reconstructed from the committed physical action chain** on replay,
not held in a separate mutable map table/owner. Inaccessible or
unborn-spatial moves are rejected on application and independently
cold-audited. Modeled terminal, veto or NO_ACTION never moves the body.

The basic movement priors are **explicit researcher-specified**
(`PRIORS=3` plus a bounded born exploration adjustment), not learned
site value or a claim about hidden world payoffs. An equal paid score
between moves from a branching site can still lead to `AMBIGUOUS`
and NO_ACTION. This negative is preserved rather than inserting a
new exploration/path-selection override. No site is hardcoded as
valuable just because it is named `source`.

The spatial flag is part of **native born schema v11**. Prior v10 local
SQLite experimental lives are not silently migrated or reinterpreted.
The registry remains `NOT_REGISTERED_NOT_EXECUTABLE`, local owner
does not provide independent M11, and the 128-step maximum is
technical only.

## Scientific and technical evaluation boundary

Unit route traces (camp->passage->source->passage->camp) are
**physics-only** adjacency checks, not autonomous motor behavior.
The test additionally starts distinct spatial OFF and ON local
individuals, lets them choose via the unchanged paid Competition,
and records actual movement or abstention, energy/UC, current
subjective site evidence, cold inspection and audit, hidden remote
site exclusion and terminal/censor. No test commands an action.

**Exit threshold:** at least one actual paid/admitted movement in a
single native research life, with later first-person observation,
the absent-neighbor and legacy negatives, and cold replay.
If movement never wins, report a genuine P1 competition blocker;
do not tune a new prior solely to manufacture success.
Remembered place value and voluntary need-driven revisits are
specifically **P2 #924**; renewable resources and multiple needs
are **P3 #925**, longitudinal science **#906**.
