# Issue #110 : réanalyse indépendante des 12 journaux de vies contrastées

**Date : 13 octobre 2026.** Données sources : GitHub Actions [run 38470291508](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38470291508), archives `issue110-contrasted-science-py3.11` et `issue110-contrasted-science-py3.12` avec WAL, JSONL et manifests. Code réellement exécuté : `c701fa40feb8cef415b0e9af86d0e079a4c9a763` (source mentionnée par les deux résumés). Statut GitHub SUCCESS sous les deux interpréteurs.

Ce rapport réanalyse les JSONL originaux *après l'expérience*, indépendamment des tableaux calculés par le runner. Il n'alimente jamais la cognition d'I0. Aucune modification de source expérimentale, de scénario ou de seuil n'est effectuée à partir de ces résultats.

## 1. Données physiques observées et non inférées

| Mesure | Python 3.11 | Python 3.12 |
| --- | ---: | ---: |
| Vies réellement exécutées et techniquement auditées | 12 | 12 |
| Pas physiques effectivement appliqués | 600 | 600 |
| Actions `se_deplacer` | 318 | 318 |
| Actions `dormir` | 282 | 282 |
| Publications de diagnostics `stage12_lived_diagnostics_published` | 504 | 504 |
| Activations/changements d'objectif `active_goal_changed` | 12 | 12 |
| Résultats de planning `stage6_planning_result` | 492 | 492 |
| Résultats avec `proposal_ref` non nul | 0 | 0 |
| Commandes précédées d'un motif `cible_exploration` attesté | 318 | 318 |
| Commandes précédées d'un motif `sleep_pressure` attesté | 186 | 186 |
| Commandes avec motif `active_goal` attesté | 0 | 0 |
| Préenregistrements d'objectif | 0 | 0 |
| Préenregistrements de jugement d'agence | 0 | 0 |
| Couples attribution/résultat admis | 0 | 0 |

Les 96 actions de sommeil sans motif `stage12_action_motive_attested` correspondant aux 504 publications ne sont **pas** interprétées comme 96 actions sans moteur cognitif : elles peuvent relever de la continuation de sommeil. Les 504 attestations de motif couvrent 318 explorations + 186 options `sleep_pressure`, et **aucune** n'atteste de commande dirigée vers le but actif.

Les 12 noms de configuration, 12 volumes de journaux et leurs SHA-256 respectifs ont été comparés octet par octet entre les deux archives : **12/12 journaux canoniques binaires-identiques**. Les sources Python 3.11 et 3.12 sont des reproductibilités d'un même protocole déterministe, **pas** 24 réplicats statistiques.

## 2. Ce qui est démontré et ce qui ne l'est pas

1. **Démontré sur cette campagne :** le système ne publie aucun engagement GA parce que chaque commande attestée est exploratoire ou liée au sommeil, pas à `active_goal`. La jointure et le détecteur ne peuvent pas recevoir de couple admissible. Ne pas abaisser leur seuil pour compenser.
2. **Démontré dans les traces du planificateur Stage 6 :** aucune des 492 tentatives publiées n'a produit d'option utilisable. Les variables de contexte ont bien été modifiées avant la naissance ; ce résultat n'est donc pas exclusivement dû à une seule carte ou une seule pression d'eau.
3. **Hypothèse causale à tester :** le modèle d'équipement `E-v1-stage6-reference` est une table déterministe exacte où une transition non vue renvoie `LookupError`, et son corpus ne comporte que quatre transitions de référence, dont une ingestion d'eau. Le changement de position, d'eau initiale ou d'état interne peut empêcher la recherche planificatrice. Les traces ne démontrent pas encore quelle clé exacte manque à chacun des 492 appels.
4. **Autre hypothèse à tester :** un objectif activé durant le premier pas et les options intrinsèques exploratoires concurrentes empêchent la mise en compétition d'options de but, même en présence d'une source d'eau au point de départ. Le Stage 6 doit être évalué indépendamment du biais d'attribution pour départager concurrence et capacité prédictive.
5. **Limite fondamentale :** une absence de commande motivée par un objectif n'est ni une attribution subjective `world`, ni une déficience universelle d'I0, ni une preuve physique d'inexécution des buts dans tous les mondes.

## 3. Suite préenregistrée

L'étude prospective `stage12-issue110-goal-access-ablation-prereg-2026-10-13.fr.md` compare sans forcer les commandes quatre vies à facteurs `enable_geography=true/false` et eau initiale `20/35`, dans le contexte `water_available`. Elle réutilise les seuils de diagnostic et les audits. Si aucune proposition Stage 6 ne se matérialise dans l'ablation, l'exploration géographique n'explique pas à elle seule le manque de preuves ; la couverture exacte du modèle doit être diagnostiquée séparément.

## 4. Décision

**Résultat exploratoire : INCONCLUSIF pour l'attribution d'agence, PASS technique limité pour la provenance des données.** Le Stage 12 et l'issue #110 restent ouverts ; la cible normative v1.3.2 n'est pas équivalente à un code intégré. La validation opérateur et la validation scientifique globale restent explicitement indisponibles.
