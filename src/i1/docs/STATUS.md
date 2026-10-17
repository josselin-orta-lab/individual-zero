# I1 development status

**Date:** 2026-10-17. **Generation:** I1 (active).
**Parent reference:** I0 (frozen).
**This is an engineering ledger, not scientific GO.**

## Authority

- Declarative contract: [engine.json](../engine.json).
- Registry: [engine-registry.json](../../../config/engine-registry.json).
- Architecture map: [ARCHITECTURE.md](ARCHITECTURE.md).
- Validation obligations: [TEST_PLAN.md](TEST_PLAN.md).
- Native migration evidence: [I1_NATIVE_MIGRATION.md](../../../docs/engineering/I1_NATIVE_MIGRATION.md).

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

## Campagne de structuration : rapport de provenance

`tools/campaign_report.py` lit le vrai `git HEAD` de l'environnement, le SHA-256 du contrat I1 et les résultats des suites enregistrées / JUnit, puis produit `reports/i1-campaign-3.11.json`, `reports/i1-campaign-3.11.md` (et leurs variantes 3.12). Il distingue `PASS`, `FAIL`, `NOT_OBSERVED` et `INVALID`, sans attribuer un statut de merge ou un GO scientifique. Le rapport n'interroge pas GitHub et n'affirme pas que tous les contrôles du workflow ont réussi : le statut final du workflow reste à contrôler séparément.

La CI [#39040216449](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39040216449) a validé les deux jobs Python 3.11 et 3.12 pour le commit `1d2bfe3fff1f6ffc341015c4ca1fcdd3cc763d01`. Les anciennes campagnes scientifiques non vérifiées ne sont pas reprises comme référentiel.

## Structuration : examen des propositions non activables

`tools/assess_engine_proposal.py` évalue en lecture seule les propositions I2+ (structure, Lab propre, contrats, tests, dépendances parentales), mais ne les enregistre et ne les active jamais. Des tests négatifs couvrent le squelette incomplet, un import direct du runtime parent et une fausse activation. Voir `docs/engineering/ENGINE_PROMOTION.md`. Cette campagne ne crée aucune génération I2.

## Monde prédéfinis pour le Lab I1 (2026-10-17)

Six mondes ont été ajoutés dans `src/i1/lab/world_presets/` : oasis, foraging, dry-valley, empty-land, hazard-edge, blocked-route. Le lanceur `tools/run_i1_world_preset.py` utilise la naissance naturelle d'I1, avec WAL ou M11, sans injecter d'oracle ni choisir les actions. Le workflow manuel `.github/workflows/i1-preset-worlds.yml` est préparé pour GitHub Actions, avec rapports JSON et données de custody ; sa disponibilité dans le menu Actions dépendra de son intégration à la branche par défaut. Les contrôles automatiques exécutent deux naissances réelles courtes, oasis/WAL et empty-land/M11, mais ces essais techniques ne constituent pas une preuve scientifique de survie ou d'émergence. Les cartes sont fixes par nom, la graine contrôle l'identité individuelle. Documentation : `src/i1/docs/WORLD_PRESETS.md`.

## PR #254: follow-up implementation handbook (2026-10-17)

At the initial verified PR HEAD `84d7e0ef47ade9be804a680b96eb5fe1ad396db8`, the current workflow run [#39052167410](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39052167410) was reported as successful. That result does **not** validate later documentation commits.

This iteration added [UC_AND_SCHEDULING.md](UC_AND_SCHEDULING.md) covering the two separately metered P-43/P-42 UC budgets and connected it from the handbook, expanded the executable failure-diagnosis index, and recorded an **OPEN source-level Stage10 defect**: `_publish_live_consolidation` references the local `canonical` before assigning it. No living publication execution or scientific validation was run for this observation. Targeted code correction and a regression test remain needed before nonempty publication claims.

The GitHub workflow for documentation HEAD `dbbf1d732d8a9c1b52e4986dd44af1e529b49d41` was **pending at the time checked**; subsequent commits require checking their own exact SHA. Local suites were **NOT_RUN** because no repository checkout / GitHub clone was available in the execution container. Structural and scientific state must not be inferred from an earlier green SHA.

## PR #254: documentation integrity checks, tranche suivante

An additional static guard `scripts/check_i1_handbook.py --json` checks the actual `src/i1/docs/` Markdown inventory, local links, quoted explicit source paths and agreement between `engine.json`, the evidence index and active generation registry. The checker does not execute referenced commands or infer scientific results. Negative regressions live in `tests/i1/test_i1_handbook_integrity.py`; `.github/workflows/engine-structural.yml` executes the guard on Python 3.11 and 3.12.

**OPEN #255:** [Stage10 canonical initialization before owner mapping](https://github.com/josselin-orta-lab/individual-zero/issues/255). This runtime repair is isolated from the documentation PR: current CI retains byte-exact I1 generated-output parity against a frozen pre-migration commit. No parity gate was relaxed, and no cognitive runtime source was modified in this tranche.

The previous documentation HEAD `f861ac4afb95bfe3d9641af351a4f8b4950bc869` completed [CI #39052847125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39052847125) successfully. The new validator and workflow commits require separate SHA-specific acceptance; **not yet certified** by this historical result.

## Stage10 issue #255 targeted repair

The source-level `UnboundLocalError` in `Stage10Runtime._publish_live_consolidation` is addressed by moving the `canonical` assignment ahead of coordinator construction, without changing the selected owner mapping, cognitive choices, M11, physical dynamics or frozen I0. Dedicated test: `tests/i1/test_i1_stage10_canonical_publication.py` (natural and generic owner dispatch and invalid-form deferral). The migration parity gate `scripts/test_i1_artifact_parity.py` retains byte equality for all artifacts except the exact, independently checked movement of this one Stage10 assignment. The CI script inventory was also updated to include `scripts/check_i1_handbook.py`, resolving the known inventory mismatch from workflow #39053148874.

**Verification status:** pending on the exact final patch SHA at the time of this report. A green earlier commit is not sufficient. This change does not establish the scientific usefulness of four-owner consolidation; real nonempty form deltas, attribution, P-42 UC and M11 cold state evidence remain OPEN / NOT_OBSERVED.

## Stage architecture and agent navigation, PR #254

Added [STAGES_AND_INTERFACES.md](STAGES_AND_INTERFACES.md) by inspecting current source: the natural `I1Runtime` resolves a cooperative multiple-inheritance chain through I1-specific water/uncertainty and Stage12, `Stage11SleepRuntime(Stage11Runtime, Stage10Runtime)`, Stage9 to Stage4 and the Stage3/2 physical substrate. Stage1 and Stage5 are not on that active inheritance chain. The guide maps concrete phase entrypoints, cross-module data, provenance restrictions, UC, M11 custody and current test anchors, without promoting old cohorts or software tests to scientific proof. The handbook index and required-document tests now include this guide.

Previous head `ca716fe501622e1c90dff8cb746b376d8a2c05bd` passed GitHub Actions #39053624321 on its exact SHA. The current documentation edits require their own workflow validation; no new scientific GO is asserted. Remaining gaps include an executable per-mechanism evidence map with direct tests and prospective four-owner publication traces.
