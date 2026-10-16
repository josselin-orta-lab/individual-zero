# A2.30-T : plan alimentaire shadow face à l'incertitude de toxicité

**15 octobre 2026.** Préenregistrement avant code T : `1df0a78f96bb53d556f0f939dec8651cf1b3ab8c`. Source modèle antérieur et figé : [A2.30-P #38730415503](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38730415503), corpus `a230p-training-manifest.json` SHA-256 `f706cd25a31b8f716c4bb0a5a7e617bed87c0b8b47577d8b9dd31221cf23839e`. [CI T originale #38741620906](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38741620906) : **SUCCESS Python 3.11 et 3.12**, sortie exactement identique. CI de non-régression après code d'audit U : [#38742839779](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38742839779), **SUCCESS** au SHA `cfdd26ea8cf375806ffd430df8caef377c2c9eb3`.

## Intervention prospectivement fixée

Une lecture *shadow* de la connaissance antérieure P précède **toutes les actions alimentaires** de chaque nouveau monde physique. Le préfixe candidat `collecter berry_a → manger berry_a → attendre` existe uniquement comme **évaluation de prévision** ; les commandes du banc de laboratoire sont préengagées indépendamment de cette prévision et ne sont **pas** envoyées à un I0 vivant. L'accès aux commandes `collecter` avant puis `manger` après collecte est vérifié avec `SimulatorPlanner.candidate_commands`, **sans appel à `search` ni création de plan exécutable**.

**40 mondes physiques détachés, 132 transitions WorldBody.apply**, avec deux bras de 20 mondes appariés : OFF sans attente, ON avec `attendre` avant l'évaluation du modèle et la collecte. Chaque bras croise cinq causes latentes `berry_a` (`benign`, `toxin_7`, `toxin_30` inédit pour P, `toxin_100` terminal, `gain_zero`) × deux niveaux corporels de faim × deux positions. **Huit terminaisons externes** (4 par bras) ; **zéro naissance I0, zéro pas autonome I0, zéro coût UC ou jugement subjectif d'agence mesuré**. Aucune observation terminale n'est comptée comme vécue.

## Comparaison des prédictions et conséquences physiques

| Mesure | Sans attente, 20 mondes | Avec attente, 20 mondes |
|---|---:|---:|
| Branches empiriques P connues pour le préfixe | 4 | 4 |
| Shadow optimiste : au moins une branche vivante gagnant ≥5 de nourriture | **20** | **20** |
| Shadow robuste : **toutes** les branches vues réussissent et survivent | **0** | **0** |
| Shadow interdit la certification de sûreté (branche létale constatée) | **20** | **20** |
| Gain alimentaire physique avec survie après ingestion | **12** | **12** |
| Monde physiquement létal après ingestion | **4** | **4** |
| Monde survivant sans gain alimentaire suffisant | **4** | **4** |
| **Faux succès du critère optimiste externe** | **8** | **8** |
| Actions physiques appliquées | 56 | 76 |

L'indicateur `optimistic_goal_exists` est un **proxy externe**, et non une sortie `plan_found` de Stage6. Le fait qu'une seule issue favorable soit déjà observée n'autorise pas à ignorer les branches toxiques, le fruit sans valeur alimentaire ou les causes cachées jamais encore rencontrées. Les 16 faux succès optimistes correspondent à 8 décès et 8 survivants sans gain suffisant sur la matrice complète ; ce sont des comptages de conditions de laboratoire, **pas** une fréquence naturelle calibrée d'accidents.

Le modèle connaît une branche terminale possible à l'ingestion, conserve `observed_terminal_possible` pour les 40 situations et n'émet **aucun** certificat de sûreté. `toxin_30` est un effet physique absent des branches P entraînées; son contexte accessible demeure identique à celui des fruits bénins, et son identification par l'individu avant ingestion n'est pas démontrée.

## Coût et frontière de l'information

Les **20 appariements** présentent le même statut de risque prévisionnel OFF et ON, la même issue terminale/survie et la même satisfaction du critère alimentaire physique. Les cinq variantes latentes restent indiscernables pour un même profil et une même position au moment de la décision, même après une attente.

L'attente supplémentaire a un coût physique **mesuré par paire** en fin de séquence : **−0,5 énergie, −0,5 nourriture et −0,2 eau**, sans diminution de la mortalité ni amélioration de l'issue alimentaire dans cette fixture. Ces chiffres dépendent explicitement de la physique choisie ; ils ne prouvent pas qu'attendre est toujours inutile. Aucun jugement de valeur d'information subjectif ou coût UC n'est inféré en l'absence de moteur cognitif et de budget exécuté.

## Verdict

**T : PASS technique et scientifique à portée restreinte ; H1 de couverture et limites de représentation restent réelles ; l'optimisme prédictif n'est pas une preuve de résultat alimentaire réalisable en sécurité.** Ce shadow n'est pas un remplacement d'Equipment, ni un Stage6 amélioré en production, ni une méthode suffisante de détection de poison caché. Aucune modification de `Stage6`, `Stage9/DC-05`, `Stage12`, de l'Oracle, du WAL/mortalité ou de `mvp-specification-v1.3.1.md`.

**A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN ; PR #192 DRAFT non fusionnée.** Les scores et les frontières postmortem sont revérifiés séparément en A2.30-U, sans rejouer la physique.
