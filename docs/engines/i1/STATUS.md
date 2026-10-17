# I1 development status

**Date:** 2026-10-17. **Generation:** I1 (active).
**Parent reference:** I0 (frozen).
**This is an engineering ledger, not scientific GO.**

## Authority

- Declarative contract: [engine.json](../../../src/i1/engine.json).
- Registry: [engine-registry.json](../../../config/engine-registry.json).
- Architecture map: [ARCHITECTURE.md](ARCHITECTURE.md).
- Validation obligations: [TEST_PLAN.md](TEST_PLAN.md).
- Native migration evidence: [I1_NATIVE_MIGRATION.md](../../engineering/I1_NATIVE_MIGRATION.md).

## Current implementation at creation of this ledger

- I1 birth: `i1lab.i1_birth.birth_i1`, canonical `I1Runtime`.
- Four published cognitive owner families: values/needs, causal model,
  perception, metacognitive health.
- Per-generation Lab: `src/i1/lab/`; native implementations in
  `src/i1/runtime/`. I0 Lab archived at `archive/i0/lab/`.
- M11 authentic SQLite cold recovery and irreversible death exercised by
  current CI. The disposable `i1lab` build remains a **compatibility
  dependency**, not yet a fully direct importable native runtime.
- Structural migration PRs: #251 (archive I0), #252 (generation tooling),
  #253 (I1 native code and versioned Lab). This campaign is stacked after
  #253; verify real GitHub state before merging.
- A CI pass is not proof of emergent intelligence, long-run learning, or
  independently validated active publications.

## Unresolved engineering and scientific gates

- Prove genuine **nonempty Stage10 publication by all relevant owners**
  from experienced events, followed by consistent cold recovery.
- Maintain M11 refusal gates for corrupt state, ambiguous COMMIT and owner
  mismatch; extend fault-injection when transaction boundaries change.
- Replace transitional namespaced build only with proven output and
  persistence compatibility, not by a path rename.
- New preregistered scientific evaluations must use *current* natural I1;
  previous broken experimental cohorts are not acceptance oracles.
- Every future generation needs its own Lab and its own evidence.

## Working agreement

Update this page with factual PR/commit links and new unresolved issues at
the end of each campaign. Do not mark a scientific property achieved on the
strength of software tests alone. No automated rollback of living states.

## Campagne de structuration #254, tranche 2

Les suites logicielles du moteur sont déclarées dans `src/i1/engine.json` et planifiées/exécutées par `tools/run_engine_checks.py` : `structure`, `smoke`, `full`, `m11` et `source`. Le mode par défaut prépare les commandes sans les exécuter ; seul `--execute` exécute les vecteurs Python prédéfinis sans shell. Les générations non actives et non enregistrées sont refusées. L'outil ne délivre aucun GO scientifique.

La CI [#39039120881](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39039120881) valide le commit `9df88896f298cdf45e434d721a67345c3c71b8a7` sur Python 3.11 et 3.12. L'outil de squelette `tools/new_engine.py` reste inerte et non enregistreur : I2 n'a pas été créé ni activé. Les prochaines priorités organisationnelles restent la traçabilité des campagnes, la séparation des tests par génération et la finalisation prudente du générateur transitoire.

## Structuration : isolation des tests actifs, PR #254

Quatre tests actifs ont été transférés sans changer les scénarios de `tests/` vers `tests/i1/` : séparation du build, garde I0/archives, récupération froide M11 et défaillances M11 adversariales. Leurs racines d'import sont adaptées à la nouvelle profondeur; le contrat `engine.json`, le registre et le workflow utilisent leurs nouveaux chemins. Les anciennes campagnes A2 demeurent hors critères d'acceptation du naturel I1.

La CI [#39039607085](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39039607085) a conclu avec succès en Python 3.11 et 3.12 sur le commit `8387ba8ff4f910142d6e8e1ed4cd5bf163d2e122`. La présente documentation est postérieure à ce commit : revérifier le dernier HEAD si une nouvelle validation est demandée.
