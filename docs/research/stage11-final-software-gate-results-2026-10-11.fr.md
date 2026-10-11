# Stage 11 : bilan de la porte d'acceptation logicielle normative

**11 octobre 2026. Verdict logiciel du périmètre Stage 11 de la spécification EN MVP v1.2.1 : GO (couverture des exigences explicites et contrôles logiciels exécutés).** **Statut définitif du stage dans le MVP révisé : EN ATTENTE DE VALIDATION PAR L'OPÉRATEUR ET DE RÉCONCILIATION DE LA MORT PERMANENTE.**

Ce verdict logiciel **n'est pas** un GO scientifique, un Golden historique indépendant ou une autorisation de fusion. **Stage 9 conserve son NO-GO scientifique.** Le Stage 10 n'est pas déclaré terminé et le Stage 12 n'est pas accepté par transitivité.

## Sources et limites de l'audit

- **Source normative unique du code ici audité :** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, **§14**, **§16.3–16.4**, **§20.3 Stage 11**, **INV-06**, **INV-14** et frontières transversales applicables (§17/§19). Le fichier EN n'a **pas** été modifié.
- [Protocole préalable d'audit logiciel](stage11-software-gate-audit-protocol.en.md), commit **`7ba9276b57ad8e21780d6e0370bd06777d2ed526`**, avant l'extension finale du contrôle des signaux. Sa distinction « acceptance logicielle »/« held-out scientifique » reste normative pour ce bilan.
- Corrections finales antérieures incluent notamment la garde de capacité UC, la propriété des mappings validés, le suivi versionné des occurrences de cycle, le rejeu causal, l'isolation du gain et les tests d'intégrité des véritables signaux.
- Test final `tests/test_stage11_intrinsic_gain_isolation.py` étendu à **toutes** les lignes réelles `stage11_intrinsic_evaluation`, pas seulement aux options géographiques, commit **`3cdc5d4d151b9790901368056732e6e7e3aec519`**. Aucune politique de décision n'a changé lors de cet ajout.
- [Protocole du diagnostic public 600 pas](stage11-600-step-public-software-stability-protocol.en.md) au SHA `81d231adcd4950a55ee63657e80b22486d61294d`; code de sonde au SHA `f930f7673c73fe0e2f5a8083e060f6338544fe88`.
- **SHA testé final pour le présent verdict : `fda5d2444f7cf2038fa0d910af7139b397284ca5`.** Les commits de cette section postérieurs sont documentaires.

## Matrice normative, tests et observation autorisée

| Exigence Stage 11 | Contrôle de régression réellement couvert | Verdict logiciel et limite |
| --- | --- | --- |
| §14 nouveauté calibrée, progrès d'apprentissage, ennui ; intérêt ne découlant pas de propositions répétées | `tests/test_stage11_exploration.py`, y compris `test_noisy_tv_and_snapshot_replay`, `test_repeated_proposals_do_not_create_visits_or_progress`, `test_applied_actions_habituate_without_fabricating_interventions` | **PASS** pour les fixtures publiques. La simple activité ne vaut pas une intervention scientifique et les propositions ne créent pas de visites. |
| §14 cibles d'exploration, motivation `m_a` d'options informationnelles et de tests causaux | `test_stage11_exploration.py`, `test_stage11_geographic_exploration.py`, `test_stage11_intrinsic_gain_isolation.py` | **PASS** : l'intérêt dépend de la provenance causale ; les options invalides ou sans preuve ne reçoivent pas d'intérêt fictif. |
| Stage 11 « B explore north » et couverture physique mesurée | `test_stage11_intrinsic_gain_isolation.py`, tests géographiques, [résultat de 600 pas](stage11-600-step-public-software-stability-results-2026-10-11.fr.md) | **PASS** : dans la comparaison de coefficients +1/−1, la variante positive réalise une capture physique de **(2,1)** ; le test public de 600 pas réalise **600 déplacements et 600 sites physiquement capturés**. Ce sont des observations sur fixtures publiques, pas une généralisation comportementale. |
| V-18, exploration `m_a` variable mais gain `g` de Competition inchangé | `test_stage11_intrinsic_gain_isolation.py` et `test_temperament_affects_intrinsic_only` | **PASS** : `g`, les coûts et les enveloppes UC sont identiques entre les deux variantes contrôlées ; une variation du seul coefficient dérivé n'est pas une réinstanciation complète de deux tempéraments de naissance. |
| §16.4 profils normal, threat, exploration et recovery, conditions, gel intra-cycle, hystérésis et non-oscillation | `test_stage11_modulation.py`, `test_stage11_modulation_public.py`, `test_stage11_modulation_runtime.py` | **PASS** pour l'entrée/sortie dans les fixtures fixées, l'exigence de pas physiques distincts, l'indicateur inconnu et la priorité menace. Le stress de 600 pas n'a observé **aucune transition de profil** ; il n'est pas substitué à ces tests. |
| **INV-06** profil figé durant le cycle | `test_repeat_same_cycle_does_not_change_frozen_profile`, publication `S_t` et réexécution Stage 11 | **PASS** : aucun changement du profil figé lors d'une deuxième phase du même cycle ; transitions seulement aux frontières autorisées. |
| **INV-14** aucun identifiant de signal ne contribue deux fois au même choix, hors effet intentionnel déclaré | `test_stage11_intrinsic_gain_isolation.py` après `3cdc5d4`; `test_stage11_exploration.py` contrôles de références falsifiées ; sondes 600 pas | **PASS** sur les évaluations intrinsèques réellement émises dans les deux variantes de coefficients et sur les 600 évaluations de la sonde longue. Ne prouve pas l'exhaustivité de tous les futurs producteurs. |
| §16.3 / DC-07 budgets UC : plafonds, protection, configurations nulles et repli | `test_compute_budget.py`, `test_stage11_geographic_capacity_guard.py`, `test_stage11_hidden_hazard_budget_snapshots.py`, `test_stage11_multistep_unknown_danger_budget.py` | **PASS** dans les tests nuls/faibles/nominaux et pour la non-facturation de devis infrastructurels. Les impasses de budget demeurent de vrais résultats négatifs ; aucune tâche coûteuse n'est transformée en travail gratuit. |
| Exploration et dangers inconnus : séparation physique/perception/connaissance | `test_stage11_known_danger_transitions.py`, `test_stage11_multistep_unknown_danger_budget.py`, `test_stage11_stale_route_safety.py` et tests d'entrées externes | **PASS** de non-fuite et de provenance dans les scénarios déterministes. La connaissance de la disparition d'un danger, l'apprentissage causal et la récupération autonome ne sont **pas** déclarés démontrés. |
| §17 snapshots propriétaires, journal causal, replay et frontière des tentatives (architecture actuellement codée) | `test_stage11_cycle_occurrence_guard.py`, `test_stage11_guarded_lethal_rollback.py`, `test_stage11_scenario_snapshot_schedule.py`, `test_stage11_external_input_atomicity.py`, `test_causal_journal.py`, `test_journal_views.py` | **PASS** pour le comportement logiciel conforme à la v1.2.1 et pour les captures aux mêmes points. Les checks de rollback ne prouvent **pas** l'architecture de mortalité permanente désormais souhaitée. |
| Stabilité longue de l'implémentation | [CI #38147281654](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38147281654), module `lab.stage11_600_step_software_probe` | **PASS** : deux exécutions indépendantes **600/600 pas**, journaux, états et snapshots identiques ; **42 041 événements** ; 16 artefacts publiés au total par la CI. |

## Validation exacte du logiciel

| Campagne | SHA de code/test | Environnement | Preuve observée |
| --- | --- | --- | --- |
| [CI #38147055433](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38147055433) | `3cdc5d4d151b9790901368056732e6e7e3aec519` | Python 3.12 | suite unitaire **SUCCESS** après extension INV-14 |
| [CI #38147281654](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38147281654) | **`fda5d2444f7cf2038fa0d910af7139b397284ca5`** | Python **3.11.17** | **924/924 tests PASS**, job complet **SUCCESS** |
| [CI #38147281654](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38147281654) | **même SHA** | Python **3.12.15** | **924/924 tests PASS**, job complet **SUCCESS**, diagnostic distinct de **2 × 600 pas PASS** |

Seize artefacts de diagnostic et de référence ont été conservés, dont le rapport 600 pas. Aucun test de CI n'a été contourné ; le job unitaire supplémentaire de la matrice complète est **skipped intentionnellement** et non compté. Les « reference journals » de la CI ne sont **pas automatiquement des Goldens historiques scientifiquement acceptés**.

**Les 600 pas publics** correspondent à un monde de compatibilité avec déclin nourriture/eau et coût énergétique des primitives nuls. Ils soutiennent l'hypothèse de stabilité de cette configuration, **pas** la survie en conditions adverses. L'absence de transition des profils et l'absence d'UC refusées au cours de ces 600 pas ne remplacent pas les fixtures qui en exercent ces mécanismes.

## Décision de clôture et travaux qui restent effectivement distincts

**Verdict du périmètre logiciel tel que v1.2.1 définit Stage 11 : GO.** La couverture explicite de l'objectif, de la construction, des interfaces, de la manifestation physique « B explore north », des critères noisy-TV/couverture/hystérésis/`g` et des gates INV-06/INV-14 est attestée par les suites et fixtures citées. Aucun « GO scientifique » n'est déduit de ce constat.

**Stage 11 n'est PAS officiellement clôturé dans le MVP révisé :**
1. Le nouveau modèle de stage prévoit un **GO explicite de l'opérateur après essai en conditions réelles**, décrit par [la procédure de 600 pas](stage11-validation-operateur-600-pas.fr.md). Aucune signature/validation opérateur n'a été obtenue par cette campagne.
2. La décision récente du projet remplace la mort avec rollback par une **mort définitive** sans effacer les conséquences du monde. La spécification EN v1.2.1 et le runtime de cette branche contiennent encore les processus de rollback : ce changement doit recevoir sa propre modification normative/logicielle et ses tests **avant** acceptation définitive de l'architecture révisée. Les présents tests n'en revendiquent ni la suppression ni la validation.
3. Le Stage 9 conserve un **NO-GO scientifique** indépendant. Les preuves scientifiques finales de chaque module et les campagnes held-out restent une phase ultérieure du projet, ainsi que la complétion réelle des Stages 10 et 12.

**Statuts à utiliser :**
- **Stage 11, implémentation logicielle v1.2.1 : TERMINÉE, GO logiciel sur SHA épinglé.**
- **Stage 11, acceptation opérateur / MVP révisé : EN ATTENTE, non déclaré terminé.**
- **Stage 9 scientifique : NO-GO.**
- **PR #25 : ouverte, Draft, non fusionnée.**
- **`main`, permissions GitHub, protections et spécification EN : inchangés.**

Aucune modification rétroactive des protocoles ou des preuves négatives, ni de suppression de Golden, n'a été effectuée pour ce verdict.
