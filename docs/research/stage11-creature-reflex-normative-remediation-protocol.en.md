# Separate normative safety repair: reflex must move away from adjacent creatures

**Prospective remediation protocol, 11 October 2026; do not merge into the earlier changed-route experiment.** This is a targeted software defect investigation, not a held-out result. Normative source: `docs/architecture/reference/en/mvp-specification-v1.2.1.md` §9.2: “MVP reflex: move away from an adjacent creature”; §9.1 and INV-52 preserve canonical admission/veto for all sent commands. A failed run and actual physical trace have been frozen separately: [initial changed-route safety report](stage11-stale-route-safety-first-results-2026-10-11.fr.md), CI #38120585742 at commit `3f71b8aa`.

## Problem observed before this protocol

In the publicly fixed 10-step junction, an external journaled creature appears at (3,2) just as the individual is at (4,2). The only locally passable exit is the very creature-occupied neighbor to the west. The current Stage-3 reflex picks the 'farthest' *among available moves*, including a move that **decreases** the minimum creature distance to zero when no genuinely farther exit exists. The individual enters the occupied tile through `source="reflex"`; the Stage-11 geographic route correctly withheld its own direct blocked transit. No nighttime creature injury occurs on this specific daytime fixture. Calling this an ordinary successful route would be incorrect.

## Proposed minimal, general, version-relevant correction

In the existing, shared, canonical `ActionControl.reflex` routine, maintain the existing sorted candidate order and choose only **physically passable moves that strictly increase the minimum squared Euclidean distance to every adjacent creature** compared with the current captured position. When none exists, do **not** send a false 'avoidance' reflex; leave the normal, vetoed deliberation path eligible in that same world step. This is generic, stimulus-derived behavior, never a special-case route, coordinate or test escape script. It must not skip `CONTRÔLE.admettre`, suppress canonical veto, create an option, or use world truth. Document any changed Stage-3 behavior in I0-vNext; historical Stage9 frozen commits remain untouched, and scientific NO-GO remains intact.

## Prespecified checks

1. Unit controls: creature at sole passable neighbor means no reflex; with a genuinely farther passable alternative, the same single direct reflex chooses the farther move deterministically; ties retain existing direction precedence; multiple adjacent creatures require increasing the **nearest-creature** distance; no creatures means no reflex.
2. Integration: rerun exact externally journaled `creature_blocks_return` and `creature_removed` worlds from the *unchanged* initial WorldBody and Stage11 configuration. The new physically observed t3 command must **not** be an admitted 'move away' reflex into (3,2). The optional Stage11 route also cannot enter a currently creature-occupied neighbor. Preserve all real t3–t10 positions and any nonreturn/failure; do not force a successful return after the creature leaves.
3. Test a separate invisible nonlethal danger (not a creature) to confirm it does not cause a false creature reflex or leak into Action Control before physical perception.
4. Preserve exact journal/owner-state replay per condition and existing Stage-3–11 unit coverage. A test success is local software compliance, not a demonstration of general safe navigation. Python3.11 full and Goldens remain separate.

**No modifications to normative specification, known safety policy, branch protections, visibility, held-out evidence or Stage9 scientific verdict.** If the shared Stage3 repair causes unintended broader regressions, retain FAIL evidence and report the conflict instead of weakening normative constraints.
