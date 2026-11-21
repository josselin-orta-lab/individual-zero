# Stage8-F1D · effet de la mémoire personnelle payée sur la décision ultérieure

**21 novembre 2026, spécification fixée avant le premier reçu F1D.** Développement logiciel natif synthétique, zéro vie nouvelle. Source i3 `6c4d433110f9960bd96b4b5716c214e0465f9214`. La preuve F1C est terminée mais limitée : [run #44837981694](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837981694), fichier `F1C_PAID_NATIVE_ORIGINAL.json`, SHA256 `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d` et seconde réduction SHA `754a4c06eeae546f1fe8900375323752056c1b660e1af89d6b4688419a8e1588`. Aucune mémoire historique G2 complète n'existe dans ces preuves.

## Question et critère primaire falsifiable

**L'expérience réellement acquise et réellement payée pendant le pas F1C modifie-t-elle une commande motrice de la décision immédiatement suivante, en l'absence de toute intervention sur les choix de l'individu ?**

**Estimand unique de confirmation :** `(action,param)` de `PaidMicrodecisionMind.decide(World.capture(), CognitiveBudget(...))` au tick 1, comparant F1C `retain` à `discard_after_compute`. Les deux branches repartent **du même monde natif au même tick, du même corps post-apprentissage et de la même capture**, avec la même source et les mêmes générateurs aléatoires. **La seule différence admise** de `Mind` à cet instant est `effects`, `values`, `buffer`, obtenue par la conservation ou la non-conservation d'un calcul authentiquement financé.

L'étiquette de résultat est à déterminer **après** lecture des vrais reçus :
- `NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE` si la commande motrice et le paramètre sont identiques, même si les scores, options ou prédictions internes varient ;
- `NEXT_MOTOR_DECISION_EFFECT_OBSERVED_COST_MATCHED` seulement si commande ou paramètre diffèrent **et** `CognitiveWork` des deux décisions est exactement identique et payé sur les deux mêmes réserves par `World.step` ;
- `NEXT_MOTOR_DECISION_DIFFERENCE_WITH_UNEQUAL_COGNITION` si commande ou paramètre diffèrent mais travail ou facture cognitive sont différents : effet de la **rétention globale**, pas identification du contenu mémoriel indépendamment de son coût.

Un refus de cognition, une différence de loi/capture/monde/corps/RNG, un rechargement réécrivant la mémoire, un choix moteur imposé, une transition non financée, une différence au-delà des trois champs autorisés, une source F1C non vérifiée, une divulgation d'information cachée ou un décès censuré vaut `INCONCLUSIVE_INVALID_PAIR`, pas un résultat scientifique positif.

## Plan fixe, sans nouvelle cohorte

1. Télécharger l'artefact original F1C #14679910820 du run #44837981694 sous son **nom exact**, vérifier le SHA du JSON et ses hashes internes. **Ne jamais tirer d'autres racines ou remplacer l'expérience par des observations inventées.**
2. Reconstruction native **déterministe** du seul cas originel F1C `learned_beneficial_sleep` : reproduire la décision F1, le premier `World.step(dormir)`, `prepare_learning`, le vrai débit `pay_cognition`, puis exécuter `learn_from_outcome` pour chaque bras (`retain` / `discard_after_compute`) comme F1C. Exiger, bit à bit, le SHA de la mémoire finale, le `World.capture`, les corps et toutes les factures publiées dans l'archive F1C.
3. Observer ensuite la décision **authentique** du même `Mind`, sans réinitialiser la cognition, sa mémoire, son RNG ni son monde. Aucun `run_life`. Enregistrer les `info`, options, `work`, factures et l'unique nouveau `World.step` par bras. Pas de `learn_from_outcome` supplémentaire ; aucune action forcée ; pas de passe de secours.
4. Démontrer une répétition bit-identique dans deux processus Python séparés, puis audit à froid séparé avec une implémentation arithmétique Python stdlib des lois physiques et des deux monnaies. L'auditeur valide la provenance F1C, les états de frontière, la justesse des factures et la classification **sans se fier au champ de verdict du producteur**.
5. Les calculs secondaires (évolution de la prédiction `dormir`, diagnostic de `info`, `decision_work`, empreinte mentale avant/après) **n'autorisent jamais** à requalifier un résultat moteur nul. Les différences de nombre de souvenirs peuvent changer la facture du cycle suivant et doivent être déclarées. Aucun test de survie, héritabilité, sélection, généralisation ni causalité gamma n'est autorisé.

**Règle d'arrêt :** pas de naissance, pas d'admission F1, pas de nouvelle cohorte ; verdict historique Stage8-E2 `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY` immuable. L'état de preuve final reste `SOFTWARE_ONLY_SYNTHETIC_TWO_TICKS`, jamais l'équivalence G2 vécue ni la capacité de survie démontrée. La conservation durable des JSON originaux et des contre-audits doit être distinguée des 90 jours GitHub Actions.
