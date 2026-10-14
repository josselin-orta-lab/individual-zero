# Stage12 #110 : A2.13, contre-exemples physiques de généralisation d'états

**14 octobre 2026. Verdict global Stage12 : PARTIAL.** Préenregistrement antérieur au code : `742823084f56c7275939a8c76e498c2863bfe5d4`. Base `main 747cbd44ac89ace066d9bbbc0a527cf5ccb47913`. Cette expérience est **exclusivement une campagne physique dans un laboratoire externe**. Aucune modification du simulateur d'I0, de son Equipment, de ses besoins, du Stage9 ou de la norme v1.3.1.

## Sources et méthodologie

Exécution première : [CI #38619899657](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38619899657), **SUCCESS Python 3.11 et 3.12** ; 6 familles de contre-exemples ×8 seeds (41 à 48) = **48 paires / 96 mondes physiques distincts**. Les expériences ne sont pas 96 vies cognitives, ni 600 pas autonomes. Entrées `SimulationState` construites uniquement depuis `WorldBody.capture_local` et `telemetry` ; conséquences via `WorldBody.apply`, avec états avant/après, commande, inventaire et effets physiques conservés. Le banc externe seul connaît la modification de toxicité et les dangers cachés. Aucun appel Oracle, aucune vérité externe dans l'agent.

**Correction méthodologique après première exécution :** les seize contrastes de cause cachée ont le **même input observable complet**, mais des effets physiques différents. Cette ambiguïté irréductible ne doit **pas** compter comme une contradiction *créée* par une projection supprimant un champ. Le rapporteur et le test distinguent désormais `contradictory_outcome_collision` (input complet initialement différent, projection devenue identique, effet différent) de `irreducible_hidden_ambiguity` (même input complet, effets incompatibles). Cette correction n'a changé aucune physique, aucune entrée, aucune commande et aucun résultat. **Le rejeu corrigé [#38620303210](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38620303210) confirme les mêmes résultats sous Python 3.11 et 3.12.**

## Observations confirmées par la première CI

Dans les 48 paires réelles, les six familles fournissent les différences physiques ciblées :

- **BODY_CAP** : saturation alimentaire, deux corps distincts avec une baie réellement collectée et consommée ; une projection supprimant `body` confond des réponses corporelles incompatibles.
- **INVENTORY** : même cellule finale, mais baie en inventaire ou absente après la vraie tentative de collecte ; supprimer `inventory` confond `effects.ate=berry_a` et `effects.ate=unavailable`.
- **ADJACENT_PASSABILITY** : un mouvement réellement appliqué est libre ou bloqué selon un obstacle voisin perceptible ; supprimer `adjacent` confond des déplacements.
- **NIGHT_CREATURE** : même attente en présence d'une créature voisine, le jour et la nuit ; supprimer `is_night` confond les dommages.
- **HIDDEN_TOXICITY** et **HIDDEN_EXTERNAL_HAZARD** : **16/16 paires d'entrées observables complètes identiques avec conséquences physiques différentes**, reflétant respectivement une toxicité du fruit ou un danger ambiant invisible. Le banc peut les distinguer, I0 ne le peut pas sur ce seul état. Interdiction de transférer les étiquettes du banc dans Equipment/Safety/attribution.

**Les taux ne sont pas des fréquences de danger naturel.** La matrice est volontairement adversariale et appariée. Un échec sous une famille suffit à réfuter une équivalence de représentation dans cette classe de contextes. L'absence d'échec ne suffirait pas à démontrer une sûreté universelle.

## Mesures discriminantes après correction

| Projection supprimée | Contradictions **nouvellement induites** par la projection, sur 48 paires | Verdict |
| --- | ---: | --- |
| `body` | **8** | UNSAFE |
| `inventory` | **8** | UNSAFE |
| `adjacent` | **8** | UNSAFE |
| `is_night` | **8** | UNSAFE |
| `x,y` | **0** | INCONCLUSIVE |

Les **16** paires de toxicité cachée ou de danger ambiant invisible ont été maintenues séparément, sous `irreducible_hidden_ambiguity`. Chaque champ mentionné ci-dessus est comparé à entrée et commande initialement différentes et à effets physiques contradictoires : aucune de ces 16 ambiguïtés cachées n'est comptée dans la colonne « nouvellement induites ». Les seeds 41–48 varient reproductiblement le corps et la localisation des mondes d'essai, mais la projection translationnelle ne dispose pas d'une paire physique déplacée en conservant les mêmes relations spatiales et le même corps : **0 collision n'est pas une preuve de sûreté**.

## Décision scientifique

Ce protocole interdit de supprimer directement `body`, `inventory`, `adjacent` ou `is_night` d'une signature prédictive supposée exacte. La position absolue nécessite un contrôle spécifique d'invariance translationnelle : les paires déjà indistinguables sous la clé complète ne démontrent **pas** que la suppression de `x,y` soit la cause d'une contradiction. Elle reste INCONCLUSIVE en l'absence d'un contraste approprié. Aucune interpolation n'est déployée.

**C1 PARTIAL** (aucune nouvelle attribution subjective), **C2 PARTIAL** (équivalences externes contraires, pas jugement d'I0), **C3/C4/C5/C6 INCONCLUSIVE** pour l'autonomie, la diversité, l'alimentation et la stabilité, **C7 PARTIAL** (réplication technique et 8 seeds physiques), **C8 PASS borné** (laboratoire isolé, aucune modification cognitive). **GLOBAL Stage12 PARTIAL, issue #110 OPEN, aucune réception opérateur.**

## Anomalie transversale préexistante

La suite `focused-stage12` de [CI #38616856989](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38616856989) a échoué sur les deux Python à `tests/test_stage12_a26_long_horizon.py::test_actual_mortal_life_with_small_external_cap` : le test présuppose qu'il existe un `stage10_reduced_capture` après la première paire d'attribution, alors que le reçu est absent dans la vie réellement générée. Cette anomalie est **distincte** de l'audit A2.13, n'est pas masquée par les résultats positifs de la campagne, et mérite une investigation dédiée avant d'annoncer une conformité globale des stages.

**Suite de recherche :** ne développer une représentation translationnelle ou une inférence conditionnelle qu'après une nouvelle expérience contradictoire sur les coordonnées et un protocole explicite d'incertitude. Les effets retardés attribuables à une ingestion n'ont pas été validés par cette expérience. La proposition normative DC-05 v1.3.2 reste non adoptée.
