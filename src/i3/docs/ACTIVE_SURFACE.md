# I3 active surface

## Stage8-E3D · conservation du budget énergétique G2 réellement exécuté (20 novembre 2026)

[Audit léger E3D #44775193275](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44775193275) **3/3 PASS, 1re tentative**, source E3C SHA-vérifiée, **1 024 bilans population×bras×fenêtre** et 28 descriptions recalculées indépendamment. **Pas de nouveaux gzip réhachés ici** (les 36 864 originaux ont été réaudités en E3C), zéro nouvelle vie. Dans les vingt premiers pas, 36 864 vies observées : coût moteur **~1,54 énergie/pas**, cognition **~0,393**, restauration par sommeil **~0,26–0,28**, Δ énergie **~−1,65 à −1,69**. Les coûts moteurs initiaux dominent la facture corporelle, mais **aucune médiation causale gamma→survie n'est démontrée**. Note de contrat : `ACTION_COSTS["dormir"]=0.25` figure dans la table native, pourtant le débit moteur **effectivement exécuté** de `dormir` est **0**. [Rapport E3D et empreintes](../../../docs/research/studies/stage8e3d-energy-ledger/STAGE8E3D_NATIVE_ENERGY_BALANCE_RESULT_2026-11-20.md). Stage8-E2 reste négatif / CLOSED_NO_RETRY, Stage2 non promu.

## Stage8-E3C · le premier échec énergétique ne récupère pas dans les vies G2 (20 novembre 2026)

[Workflow à froid E3C #44737606261](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44737606261) **PASS 3/3, attempt=1** : **36 864 gzip G2 originaux** réhachés, chaînes corporelles et cognitives réauditées, **64 populations** vérifiées par second calcul indépendant ; zéro vie nouvelle. **17 560/36 864 vies (47,63 %) ont au moins un premier `NO_PROCESSING_BUDGET` ; 0/17 560 ont retrouvé une action financée avant décès/censure**, 15 321 sont mortes et 2 239 furent censurées après le premier refus. **Aucun premier refus dans les pas 1–20** ; échecs aux pas 21–100 : 10 098, 101–200 : 3 555, 201–400 : 3 907. Dans les dix pas précédents, ~55 % de déplacements, ~25 % de sommeil, ~0,54 énergie cognitive payée par pas ; énergie du premier refus ~0,052, vigilance ~94. Contraste descriptif d'incidence sur 64 populations : **−3,472 points**, 23 positives/37 négatives/4 nulles. [Rapport E3C + limites](../../../docs/research/studies/stage8e3c-first-energy-gate/STAGE8E3C_ORIGINAL_TEMPORAL_RESULT_2026-11-20.md). **Impasse motrice historique observée, pas causalité gamma→énergie→survie**. Stage8-E2 causal reste négatif et CLOSED_NO_RETRY, Stage2.1 non promu.

## Stage8-E3B · inactivité G2 due au financement énergétique du traitement (20 novembre 2026)

[Audit à froid E3B #44715847132](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44715847132) **3/3 jobs PASS**, **36 864 gzip G2 originaux**, 64 populations, zéro vie nouvelle. **99,884 % des pas `None`** relèvent de `NO_PROCESSING_BUDGET`, contre environ 0,116 % dus aux deux autres portes. Toutes ces défaillances de traitement surviennent avec **énergie de prédécision <10** mais **vigilance ≥10** ; le paiement initial de cognition exige 0,06 énergie + mémoire et seulement 0,15 vigilance : **goulet d'étranglement énergétique logique**, non défaut de vigilance. Cette porte explique **99,980 % du contraste descriptif E3A de −2,915 points d'inactivité**. Les 20 premiers pas observés sont tous `FUNDED`. [Rapport E3B, audit indépendant, bornes et erratum gamma3 seul](../../../docs/research/studies/stage8e3b-funding-gates/STAGE8E3B_ORIGINAL_G2_FUNDING_GATE_RESULT_2026-11-20.md), [gamma3 et portée anticipée, associations post hoc](../../../docs/research/studies/stage8e3b-funding-gates/STAGE8E3B_POSTHOC_GAMMA3_ANTICIPATORY_REACH_2026-11-20.md). Ces lectures **ne démontrent pas** la médiation gamma→énergie→survie ; Stage8-E2 causal reste négatif, sans retry. I1 actif, I3 non promu, Stage2 général `NOT_ISSUED`.

## Stage8-E2 clos · effet causal du bloc gamma123 NON démontré (20 novembre 2026)

La [campagne technique source-figée #44536464441](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44536464441) a terminé **2 répétitions indépendantes Python 3.11/3.12**, 64 512 vies chacune, **129 024 originaux gzip conservés et réaudités**. Une [troisième cohorte scientifique distincte #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471), 64 populations F0 × 24 fondateurs, G0/G1/G2, 64 512 vies originales et 384 WorldSpecs G2 préengagés, a été préexposée AVANT G0 puis intégralement auditée à froid. **Résultat primaire bilatéral gamma123** : `T=(S_sham-M_sham)-(S_swap-M_swap)`, moyenne **−0,090712 pas**, t63 **−0,046302** contre seuil `|t|>2,2962`, IC 97,5 % **[−4,589 ; +4,408]**, **31 populations positives / 33 négatives**. `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`. Ce résultat **n'est pas une preuve d'équivalence ou d'effet nul**, n'isole pas `gamma3`, et ne contredit pas le résultat Stage8-C sur son estimand distinct. [Rapport scientifique complet, empreintes, attestations internes et limites de conservation des gzip](../../../docs/research/studies/stage8e2-gamma-block/STAGE8E2_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-20.md). **193 536 vies originales au total, pas de nouvelle naissance autorisée pour réessayer Stage8-E2.** Archives originales GitHub Actions à rétention 90 jours seulement ; export durable toujours nécessaire. I1 actif, i3 non promu, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`.

## Stage8-E1 terminé · 31 gènes analysés, mécanisme causal non identifié (19 novembre 2026)

[Audit source-figé #44505924594](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44505924594) **PASS** sur **32 256 vies gzip et 4 608 filiations**, zéro vie nouvelle, analyse des 31 gènes v4 par **32 populations**, sans pseudoréplication. Associations descriptives les plus fortes avec G2 S−M : `temperament.exploration` r=−0,32479, `gamma3` r=−0,32361, `theta.vigilance` r=+0,31616 et `theta.energy` r=−0,30853 ; **aucun gène causal démontré**, aucune p-value confirmatoire après classement post hoc. La totalité des gènes et les dix populations défavorables sont dans l'[artifact #14518619277](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44505924594) et le [rapport de provenance](studies/stage8-parent-concentration/STAGE8E1_POSTHOC_GENE_ASSOCIATIONS_RESULT_2026-11-19.md). [Conception historique Stage8-E2 préalable à naissance](studies/stage8-parent-concentration/STAGE8E2_GAMMA_BLOCK_PROSPECTIVE_CAUSAL_DESIGN_2026-11-19.md) : cette cohorte a **depuis été exécutée et close négative** selon son critère, voir la clôture Stage8-E2 ci-dessus. Les historiques Stage7 négatif, Stage8-A moyen positif, Stage8-B interaction négative, Stage8-C S−M positif et Stage8-D diversité faible restent inchangés. I1 actif ; i3 non promu ; Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`.

## Stage8-C terminé · bénéfice moyen S−M vérifié sur les originaux (18 novembre 2026)

La [campagne prospective unique #44320492293](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44320492293) a réussi ses deux répétitions techniques 3.11/3.12 et un job scientifique distinct **32 populations / 32 256 vies G0/G1/G2**, S parents pondérés par persistance vécue, M contrôle de **multiplicités de reproduction exactement appariées mais d'identité parentale brouillée**, U témoin uniforme. Préengagement des 192 World G2 et méthode Student unilatérale `alpha=0,025` avant naissance. Critère primaire G2 S−M **+8,675998 pas**, borne inférieure unilatérale 97,5 % **+1,468357 >0**, **22 populations gagnantes / 10 perdantes**, verdict `STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0 / CLOSED_NO_RETRY`. Le [second audit brut indépendant #44406977082](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44406977082) a **réussi** (32 256 gzip rehashés, 4 608 ascendances mutées reconstituées, aucune vie nouvelle), auditeur source épinglée avant résultat `23d0e3ea`. [Rapport scientifique, archives et limites](studies/stage8-parent-concentration/STAGE8C_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-19.md). Les contrastes S−U et M−U sont descriptifs. Le gain observé reste inférieur aux 10 pas pris comme effet intéressant pour le dimensionnement : **aucune affirmation de supériorité pratique universelle, de gène causal ou hors F0**. Les protocoles et registres Stage8-C datés d'avant naissance restent conservés comme tels. Stage8-A positif moyen, Stage8-B négatif interaction et Stage7 négatif signe demeurent inchangés. Stage2.1 reste `NOT_ISSUED/HOLD_NO_VERDICT`, I1 actif, I3 non promu.

## Stage8-B terminé · interaction écologique NON démontrée (17 novembre 2026)

La [campagne prospective source-figée #44060101150](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44060101150) a terminé deux répétitions techniques puis une cohorte scientifique indépendante de **23 040 vies natives** (32 populations, 192 mondes G2 réservés avant naissance). L'omnibus Hotelling pour l'interaction sélection×écologie F0 est **`p=0,6577705128`** contre **`p<0,025`** : **`STAGE8B_NO_INTERACTION_DEMONSTRATED_F0 / CLOSED_NO_RETRY`**. Moyennes G2 descriptives selected−uniform `stable` +16,096, `depletion` +14,374, `pulse` +18,074 pas ; ni interaction démontrée, ni équivalence prouvée. L'[audit brut indépendant #44126032148](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44126032148) a **réussi** : 23 040 gzip natifs SHA-vérifiés, 9 216 vies G2 relues par famille, 32 profils et zéro vie nouvelle. [Résultat scientifique et limites](studies/stage8-ecology-interaction/STAGE8B_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-17.md). Stage8-A positif pour son critère moyen et Stage7 négatif pour son critère directionnel demeurent inchangés. Le [contrôle Stage8-C](studies/stage8-parent-concentration/STAGE8C_CONTROL_DESIGN_2026-11-17.md) était un **précurseur logiciel daté**, et sa [cohorte scientifique distincte](studies/stage8-parent-concentration/STAGE8C_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-19.md) a depuis été menée et auditée.

## Stage8-A completed · positive preregistered MEAN-persistence result (17 November 2026)

[One-shot GitHub Actions #43950098410](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43950098410) on source `ac353a9c4206ee3ecfd90bb101e26d092103958b` completed **two sealed native engineering rehearsals** and then a distinct **32-population** G0/G1/G2 scientific run, each 23 040 lives. The frozen PRIMARY **mean** G2 selected-minus-uniform-parent step difference was **+14.487413194444445**, with **Student one-sided 97.5% lower confidence bound +7.993312233799369 >0**. **23 positive / 9 negative populations**. Verdict `STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0`, **`CLOSED_NO_RETRY`**. This is a **separate new experiment** from Stage7, not a post hoc reversal of its negative 13/16 sign criterion. Study [prospective protocol](studies/stage8-mean-persistence/STAGE8A_MEAN_PERSISTENCE_PROTOCOL_2026-11-16.md) and [final custody & limitations](studies/stage8-mean-persistence/STAGE8A_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-17.md). [Independent re-reduction PASS](studies/stage8-mean-persistence/STAGE8A_INDEPENDENT_READONLY_AUDIT_RESULT_2026-11-17.md) verifies 23,040 originals and reproduces the mean, lower bound and 23+/9− without new lives.

**Exploratory read-only decomposition**: [ecology and parental diversity post hoc](studies/stage8-mean-persistence/STAGE8A_POSTHOC_ECOLOGY_PARENT_DIVERSITY_2026-11-17.md) reports family-level G2 gains +12.86/+14.55/+16.05 steps (stable/depletion/pulse) and 14.00 vs 15.25 distinct parents per 24 G2 offspring in selected vs control. Only 2 of 9 adverse populations lost across all three families; no causal ecological interaction or genetic bottleneck demonstrated. **Hard limits:** F0 only, no independent external witnesses, independent read-only original-level rehash completed (not an external witness), insufficient evidence for causal mechanism or general benefit across every ecology and lineage; 9 disadvantaged populations must remain visible. The general Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, I1 active runtime and I3 unregistered reference are unchanged. No more Stage8-A births or reruns. Stage8-B (ecology) and Stage8-C (genetic/diversity mechanism) require separate new questions.

## Stage7 completed · negative prespecified persistence result (16 November 2026)

The [single source-locked Stage7 inherited-persistence run](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125) (exact source `06cfcf9cc9414e0f139b39a42d05177ddb813782`) **completed** its separate Python 3.11/3.12 sealed engineering rehearsals and prospective 16-population scientific execution. The frozen primary was **not met**: 12/16 positive G2 population persistence contrasts, requiring at least 13/16, reported as `PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0`. Sealed original receipts and the [frozen protocol](studies/stage7-persistence/STAGE7_PERSISTENCE_PROTOCOL_2026-11-16.md) are the authorities, not a technical workflow PASS. This one-shot is **CLOSED_NO_RETRY**. The separate Stage6-light `beta_u_eff` primary also closed negative at 9/16; neither result proves all learning or inheritance impossible. [Current concise science status and receipts](STATUS.md) supersede dated prospective-launch wording.

The sections below describe the **Stage2 software/engineering architecture** and older (dated) gate decisions; they do not supersede the subsequent owner [ADR-0022 research permission](../../../docs/decisions/ADR-0022-i3-owner-authorizes-prospective-experiments-internal-evidence.md) or authorize reuse of any old Stage6/Stage7 allocation. I1 remains active, I3 the unregistered owner-selected research reference; Stage2 general science remains `NOT_ISSUED/HOLD_NO_VERDICT`.

This is the short operational map for developers and agents. It does not replace
scientific evidence or ADRs. See the
[code/dependency audit](I3_DEPENDENCY_AUDIT_2026-11-09.md) for archival
rationale, checked references and deliberate compatibility boundaries. The machine-readable authority is
[`../ACTIVE_SURFACE.json`](../ACTIVE_SURFACE.json).

## Current research decision (13 November 2026)

[ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) and the [internal C01/RP-A1 disposition](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md) record `HOLD_NO_VERDICT` for the general Stage-2 question **without a mandatory external reviewer**. This is not a scientific Stage-2 negative/positive closure: `NOT_ISSUED` remains canonical; E1/E3 are negative only on frozen candidates. Keep all scientific World admissions closed, P1.3 funded-v2 unchanged, I3 unregistered and I1 active. Parallel R1/R2 M11 engineering remains permitted under ADR-0020, but not engine release.

## Current state

- **Reference:** P1.3 on funded v2.
- **Stage 1:** closed negative under ADR-0018.
- **Current stage:** Stage 2.1, replay gate.
- **Canonical Stage-2.1 status:** `REPLAY_GATE_CAPACITY_SHOWN`.
- **ADR-0017:** **owner-lifted on 9 November 2026** for fingerprint `dcada9e2…f1` and the frozen DEVELOPMENT 80/81 pilot only.
- **I3:** proposal only, unregistered.

**Current research handoff (11 November 2026, after E3):** The [Stage-2 stop and closure-readiness assessment](studies/stage2-replay-gate-selected-design/STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md) is the **current operational decision**, not the older cost-only #1302 handoff. The precommitted [E3 native VISIBLE-versus-paid-discard result](studies/stage2-replay-gate-selected-design/E3_NATIVE_PAID_BRANCH_DELIVERY_RESULTS_2026-11-11.md) had **equal modeled optional computation in both arms**, one intermediate native score difference among two informed *synthetic/unpaid* histories, but **zero** legal native motor changes; the separate empty-history control was null. [Exact-source CI #43065730480](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43065730480) passed **1,148/1,148 I3 software tests each** on Python 3.11 and 3.12. **This precise E3 candidate is CLOSED NEGATIVE** without post-exposure retuning. It is not a general cognition/survival failure; Stage-2 scientific verdict remains **NOT_ISSUED**. The old [cost-identifiability result](studies/stage2-replay-gate-selected-design/COMPUTATION_VALUE_IDENTIFIABILITY_RESULTS_2026-11-11.md) remains intact as historical E0 data, not the current launch instruction.

**Immediate gate:** do not create another replay head, new synthetic fixture/seed search or Stage-2.2/2.3 controller just to obtain an action. Future research requires a **genuinely distinct** first-person paid information mechanism that passes a separately frozen **no-World native-action** falsifier. The older external C01 review requirement has been replaced **for the documentary HOLD only** by the internal source-traceable disposition; it does not establish broad scientific closure. Only then consider independent ecological sampling/NI power, true physical two-currency/learning cost, exact G/R custody and a **new, separately scoped owner-index authorization**. Current `next_scientific_action` encodes this hold, **not** permission to create a World; no new World opening is authorized. Keep `fresh_lived_worlds_allowed=false`, consumed studies closed, P1.3 unchanged and I3 unregistered.

The corrected R0-R4 software falsifier executed exactly once and passed.
The hardened transport passed 36/36 G/R rehearsals on Python 3.11 and 3.12
with the **same exact content fingerprint** `dcada9e2…f1`, verified after
merging PR #1220. The owner lift is recorded in [STATUS.md](STATUS.md).
The **single prospective DEVELOPMENT 80/81 pilot has now completed**:
36/36 original lives generated, 36/36 reduced, zero structural failures;
[descriptive findings](studies/stage2-replay-gate-development-80-81/RESULTS.md).
It reduced replay and pooled paid cognition, but did **not** establish survival
non-inferiority. The owner-lifted scope is **consumed** and 80/81 is closed
without retry. All additional Worlds, validation, selection, reserve and
confirmatory gates remain closed until newly frozen authorization. The current
legacy `stage2_panel.execute()` and `stage2_admission.admit()` are now hard-closed
for all scientific cohorts, even when the historical owner-lift entry exists.
The new random-control policy is an engineering-only opt-in, not a new lift.

## Active scientific surface

Only these files define the current scientific intervention:

- `modules/p13_replay_gate_mind.py`
- `modules/stage2_random_equal_mean.py` (RANDOM-EQUAL-MEAN control)
- `lab/stage2_replay_gate_falsifier.py` (historical one-shot, do not rerun)
- `docs/STAGE2_LAUNCH.md`
- `docs/STAGE2_REPLAY_GATE.md`
- `docs/studies/stage2-replay-gate-software/RESULTS.md`

Stage 2 must not import Stage-1 laboratory helpers. If it needs one, first ask
whether the concept is genuinely current or whether historical machinery is
leaking back into the design.

## Active engineering surface

These files support ADR-0017 execution custody and are not themselves evidence:

- `lab/engineering_cohort.py`
- `lab/two_phase_panel.py`
- `tests/i3/test_stage2_execution_pipeline.py`
- `runtime/admission.py` (World-bound admission tickets)
- `lab/stage2_admission.py` (engineering tickets only, old science hard-closed)
- `lab/stage2_panel.py` (engineering rehearsal only; old pilot `execute` disabled)
- `lab/stage2_random_equal_mean.py`, `lab/stage2_gate_design.py` (software-only design)
- `tests/i3/test_stage2_random_equal_mean.py`, `tests/i3/test_stage2_gate_design.py`
- `tests/i3/test_stage2_exact_transport.py`
- `docs/studies/stage2-replay-gate-development-80-81/` (frozen plan,
  sealed rehearsal, completed immutable scientific originals and descriptive result)

The supplied 68/69 pilot runner is **archived**, not an active transport:
`archive/stage2/development_68_69.py`. Its historical observations cannot
be reused as prospective evidence. The historical transport was owner-lifted only for the frozen DEVELOPMENT
80/81 pilot; its authority is consumed. This does not retroactively legitimize the supplied 68/69 run.

## Compatibility-only Stage 1

Stage-1 candidate code is archived under `src/i3/archive/stage1/`
for retained compatibility tests and regression tooling.
They are listed in `ACTIVE_SURFACE.json`.

Their presence does **not** mean Stage 1 is open. Do not extend them into a new
candidate or use them as the current scientific handoff.

The [Stage-1 historical document catalogue](../archive/stage1/DOCUMENTS.md)
links to the frozen protocols and results at their unchanged evidence paths.
Older Stage-1 scientific runners and retired tests already moved to
`archive/i3/stage1-2026-11-09/`. Evidence under `docs/studies/` stays at its
stable paths for citation and custody.

## Read order

For current development, read only:

1. `docs/STATUS.md`
2. this file / `ACTIVE_SURFACE.json`
3. `docs/studies/stage2-replay-gate-selected-design/STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md`
4. the specific **frozen** source, protocol and tests you are auditing; read `docs/STAGE2_REPLAY_GATE.md` for the historical gate, not as an instruction to relaunch it

Read `DEVELOPMENT_PLAN.md` when changing stage boundaries or ordering. Read
older Stage-1 documents only for a named historical question.

## Drift alarms

Stop and re-evaluate if a change does any of the following:

- reopens the now-closed DEVELOPMENT 80/81 panel or any other World without
  a separately frozen protocol and fresh owner authorization;
- dispatches replay-gate cognition without a matching canonical owner lift,
  exact transport fingerprint and full-WorldSpec-bound ticket;
- changes the frozen replay-gate formula or R0-R4 rules after the canonical
  software verdict;
- treats the formally passing but flat S1 R3 fixture as proof of graded cost
  sensitivity;
- imports Stage-1 lab helpers into active Stage-2 science;
- creates another Stage-1 candidate;
- reuses supplied 68/69 as prospective evidence;
- launches Stage 2.2 or 2.3 while the scientific Stage-2.1 verdict is `NOT_ISSUED`;
- retunes the frozen E3 synthetic states after the **0/2** native action result or relabels a score-only difference as a living motor and body improvement.

The purpose of this map is not to erase history. It is to stop history from
pretending to be the present.
