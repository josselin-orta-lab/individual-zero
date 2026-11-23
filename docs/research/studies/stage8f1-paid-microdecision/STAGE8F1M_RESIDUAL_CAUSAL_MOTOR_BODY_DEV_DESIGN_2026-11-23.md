# Stage8-F1M · Effet des accumulateurs persistants : commande réelle et valeur corporelle

**Statut : DEV_ONLY_DESIGN_NOT_SCIENTIFIC_PREREGISTRATION, 23 novembre 2026.** Ce document décrit le développement. Il ne préenregistre pas de cohorte F1M scientifique, ne réserve aucune graine et n'autorise aucun World.step des futures racines scientifiques. Les vies L01..L32 sont définitivement consommées et ne peuvent jamais être rejouées. Les résultats F1L et historiques restent intacts.

## Trois questions qui ne doivent pas être confondues

1. **Influence algorithmique** : conserver les accumulateurs hérités de T5, plutôt que neutraliser exclusivement leurs valeurs avant T6, change-t-il l'option gagnante de la compétition, à preuve et seuils identiques ?
2. **Effet causal sur la commande réellement exécutée** : un changement d'option engendre-t-il une commande autonome (action, paramètre) différente et admise par le contrôle moteur, réellement suivie d'un World.step ? Un changement d'option sans commande motrice différente ne compte pas.
3. **Conséquence corporelle et valeur adaptative** : le moteur a-t-il réellement débité les coûts et modifié les cinq réserves (énergie, nourriture, eau, intégrité, vigilance), stocks et trajectoires T6..T60 ? Les différences de réserves ne prouvent pas une amélioration de persistance. Les différences de survie sont mesurées séparément, sans score composite.

Les estimands sont hiérarchisés, sans tri a posteriori sur les seuls individus dont la commande change. Une compilation réussie, une décision différente, une récompense interne ou une réserve améliorée ne suffisent pas à proclamer une capacité adaptative.

## Pilote DEV_M sur des expériences natives originales

Grille DEV-only exacte : DEV_M01..08, graines 202611239601..608, 2 mondes (eau au sud-ouest ou au sud-est, nourriture dans un autre coin), WorldSpecs et graines distincts des sources scientifiques F1L et DEV_L. Politique opt-in F1JFixedRoundMind inchangée, corps et RNG individuels.

- T1..T4 : mémoire personnelle de départ vide, TD nul, tampon vide, apprentissage réellement payé après chaque action choisie librement, et ancre des statistiques possédées au T1.
- T5 : deux états de lecture, statistiques personnelles récentes ou moyennes anciennes de ce même T1, seulement sur les clés déjà acquises. Les quatre composantes de CognitiveWork et les factures énergie/vigilance doivent être strictement identiques et effectivement payées. Le modèle choisit librement et paie son action puis l'apprentissage. Une copie full_sham indépendante doit rester neutre.
- Entre T5 et T6 : pour chacun des deux contenus, clone de l'état réellement produit après apprentissage. Un bras conserve les valeurs des accumulateurs et le second met uniquement leurs valeurs à zéro en préservant les clés, l'intention, l'état TD, le buffer, le RNG, le corps, le monde, le cache, la mémoire et les capacités. Ce reset est une intervention de laboratoire sur l'état et non une action prescrite.
- T6..T60 : quatre bras (recent/carry, recent/zero, stale/carry, stale/zero) poursuivent des décisions et apprentissages réellement exécutés et financés. Chaque bras possède une duplication native sham, avec reçus conservés, audités indépendamment. Aucun rééquilibrage fictif des coûts T7+, des corps ou des stocks après une divergence.

## Gates et observables

Ordre fail-closed : (1) source réellement financée, vivante et quatre ticks T1..T4 complets ; (2) neutralité full_sham à T5 et des quatre sham du fork R ; (3) factures identiques de décision T5 entre contenus, puis T6 pour chacun des deux couples carry/zero, portant sur cycles, étapes simulées, memory_items, replays, énergie et vigilance réellement payés ; (4) seulement alors mesure des options et commandes.

Les statuts techniques sont DEV_INCONCLUSIVE_UNFUNDED_OR_INCOMPLETE_SOURCE, DEV_INVALID_NONNEUTRAL_SHAM, DEV_INCONCLUSIVE_REAL_DECISION_COST_GATE, puis DEV_ONLY_MOTOR_EFFECT_OBSERVED_NOT_SCIENCE ou DEV_ONLY_NO_MOTOR_EFFECT_NOT_SCIENCE. Aucune branche manquante n'est remplacée et aucun coût fictif n'est ajouté.

Les diagnostics obligatoires couvrent le gagnant avant Action Control, la commande avec paramètre après admissibilité, l'aléa et l'intention, les accumulateurs avant/après et tous les tours effectivement payés, les deux factures natives, le delta corporel après moteur T6 et après apprentissage T6, puis les cinq réserves, stocks, repas, boissons, coûts cumulés et ticks vécus jusqu'à T60.

La comparaison des cinq réserves terminales via Pareto est définie uniquement lorsque les deux bras survivent au même horizon. Sinon, on publie les nombres de ticks séparément et on ne traite pas un corps précoce comme comparable à un corps T60. Les 2 × N comparaisons DEV ne sont pas N × 2 individus indépendants : les deux contenus partagent leur origine.

## Audit indépendant et limites

L'auditeur DEV Python 3.12 ne doit importer ni i3.modules, ni le Mind moteur, ni le World natif, ni le producteur F1M. Il reconstruit toutes les étapes depuis les originaux, y compris la lecture T5 temporaire, les états de fork T6 identiques hormis les accumulateurs, le contrôle moteur, les coûts en deux monnaies, l'apprentissage post-action et les conséquences corporelles, sans aucun World.step nouveau. Les shams originaux complets sont conservés pour une comparaison indépendante des octets sémantiques.

Les pilotes DEV_M peuvent établir la faisabilité et falsifier les contrôles. Ils ne sont pas la campagne F1M scientifique ; un effet moteur ou corporel DEV_M ne représente pas un gain adaptatif reproductible ni une promotion de Stage2.

## Condition de prochaine exposition scientifique distincte

Le chantier F1M #1516 propose une nouvelle cohorte potentielle de 32 origines, 8 écologies, 4 continuations par origine, avec leurs contrôles. Toute grille scientifique, graine et seuil doit être publié sur main et figé par blob Git avant toute exposition ou accès à ses résultats. L'estimand moteur ITT peut exiger, à titre de proposition non encore figée, 6 paires motrices modifiées sur 64, réparties sur 3 écologies. La valeur corporelle doit posséder un **critère indépendant**, fixé avant naissance, qui distingue persistance et simple Pareto.

Un futur tir exige ensuite le transport source-verrouillé, la protection create-only d'une référence de consommation sans contournement, Releases immuables, deux répétitions techniques disjointes, audit froid indépendant, une seule tentative et conservation d'originaux/partiels même si l'exécution échoue. **Autorisation scientifique F1M spécifique encore absente.** L'autorisation du tir F1L ne s'étend pas à F1M.

Références : issue https://github.com/josselin-orta-lab/individual-zero/issues/1516 ; F1L original https://github.com/josselin-orta-lab/individual-zero/actions/runs/45162724456 ; F1L posthoc archivistique https://github.com/josselin-orta-lab/individual-zero/actions/runs/45179149574 .