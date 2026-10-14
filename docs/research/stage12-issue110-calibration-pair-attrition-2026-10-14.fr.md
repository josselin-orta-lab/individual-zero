# Issue #110 : audit de perte des couples vécus et décision de calibration (14 octobre 2026)

## Provenance

Campagne instrumentée, source `4d35dca45e4b0af76e09368fe1bbd82bcb5c6565`, [GitHub Actions #38532582877](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38532582877) : **PASS Python 3.11 et Python 3.12**. Aucun changement de la dynamique physique, du planificateur, des jugements subjectifs ou des seuils. Traces événementielles `CALIBRATION_STEP` directement produites à partir de journaux canoniques et conservées dans les logs, archives JSONL et WAL.

## Décomposition des 4 vies × 16 pas

| Condition | Sous-critères préenregistrés | Jugements self/world/unknown | Paires admises | Consommées | Expirées sur sommeil | En attente à horizon |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Sans obstacle | 3 | 2 / 0 / 1 | 2 | 1 | 1 (diagnostic dû à t6, réveil t7) | 0 |
| Obstacle fixe | 1 | 0 / 1 / 0 | 1 | 1 | 0 | 0 |
| Retrait à t3 | 4 | 2 / 0 / 2 | 2 | 1 | 1 (dû à t7, réveil t8) | 0 |
| Retrait à t4 | 3 | 1 / 1 / 1 | 2 | 1 | 0 | 1 (admise t16, due t17) |
| **Total externe descriptif** | **11** | **5 / 2 / 4** | **7** | **4** | **2** | **1** |

Les deux occurrences `sleep_expired` sont explicites, validées par les reçus `stage12_attribution_sample_unavailable` et ne sont pas des doublons ou des paires silencieusement supprimées. L'occurrence `pending` est un *censurage de fin d'observation*, et non une perte. Dans les contrôles « libre » et « retrait t3 », `collecter` est suivi du jugement `unknown` (pas d'indice d'agence suffisant) ; sa mesure `failure` ne peut pas donner lieu à une paire valide. Le fait que le détecteur reste `None` est donc justifié par le journal.

## Cause comportementale du manque de couverture

Les actions effectivement libres après le réveil se composent principalement de `se_deplacer`, sans nouvelles préinscriptions d'objectif admissibles correspondant à un but actif et à une cible immédiatement pertinente. Modifier le seuil, conserver un couple pendant le sommeil ou créer un engagement a posteriori serait un changement épistémique/architectural qui ne découle pas de ces observations et qui n'est **pas autorisé** dans ce correctif.

Une extension d'horizon de quelques pas permettrait de consommer le couple `t16` du cas retrait t4, mais **ne comblerait pas** deux succès et deux échecs dans une seule vie. Allonger arbitrairement à 600 pas sans mécanisme d'engagement soutenu n'est pas rationnel.

## Garde-fous

Le relevé de couverture `coverage_census` dans `scripts/run_stage12_issue110_calibration_feasibility.py` classe les paires selon trois résultats vérifiables : consommé dans la fenêtre, suppression explicite pour sommeil/refus UC, ou candidat encore en attente au dernier pas. Les tests refusent une comptabilité impossible. Le recensement ne réinjecte rien dans I0 et n'ajoute aucun propriétaire d'état.

**Statut de cette investigation :** la perte apparente de preuves est expliquée par les contrats existants et le comportement observé ; aucune restauration, duplication ou promotion de `unknown` ne doit être codée. La calibration du détecteur exige des vies offrant une pluralité réellement autonome de buts et de conséquences contrastées avant de devenir évaluable. Issue #110 ouverte, Stage12 non reçu, PR #155 brouillon, Stage9 NO-GO.
