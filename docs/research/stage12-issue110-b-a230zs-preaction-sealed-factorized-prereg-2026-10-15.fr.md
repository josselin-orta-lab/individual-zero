# A2.30-ZS : préenregistrement prospectif de prédictions signées AVANT transitions physiques indépendantes

**Verrou du 15 octobre 2026, avant toute implémentation et avant le moindre monde ZS.** Branche empilée sur [PR #210 ZP](https://github.com/josselin-orta-lab/individual-zero/pull/210), commit parent `1ab0812e7ff09e81a4e5c8cdf32d15504b1e7273`, dépendant de [PR #208 ZO](https://github.com/josselin-orta-lab/individual-zero/pull/208). Toutes les expériences ZO et ZP sont **déjà connues** et ne doivent pas être présentées comme des découvertes ZS. Cette étude est une **nouvelle réplication de mondes physiques**, jamais de nouvelles vies I0.

## Motivation scientifique : réparer un vrai verrou temporel

ZO avait séparé l'entraînement du banc d'évaluation, mais sa fonction `compare_forecast` n'émettait les prédictions pour chaque monde tenu à l'écart **qu'après** l'exécution de toutes les transitions. ZP a audité ce défaut méthodologique et conclu `methodological_strict_prospective_receipt_criterion_met = false`. Une implémentation déterministe peut garder son modèle figé tout en calculant ses sorties a posteriori, ce qui ne prouve pas des prédictions individuelles pré-action scellées.

**Question ZS :** le même prédicteur empirique à six composantes, sans certitude de sûreté, conserve-t-il ses résultats lorsqu'une transaction d'archive immuable des **104** prévisions et entrées perceptives est réalisée dans un **premier job GitHub**, puis que les **104 transitions physiques** ont lieu exclusivement dans un **second job**, redémarré séparément à partir des fichiers scellés, avec preuves SHA inchangées ?

Les prévisions ne valent **que pour** `(x,y,energy,food,water,inventory_berry_b)`. Il est interdit de prédire `integrity`, `terminal`, `next_adjacency`, `safe` ou un état `SimulationState` complet. Une sortie numériquement juste après un danger caché n'est **jamais** une garantie de survie.

## Population et plan d'analyse fixés avant le code

Réutiliser **les recettes** mais **aucune donnée observée** de ZO : `registered_recipes()`, `physical_fixture()`, `fit_partial_empirical()`, `partial_forecast()`, et éventuellement `review_results()` sous le code ZO de base, sans modifier `src/i0`, `Stage9`, `Stage12` ou le MVP normatif.

**120 nouveaux WorldBody détachés (120 actions physiques)**, tous indépendamment construits :
- **16** mondes sources : 2 positions `(5,5),(7,7)` × 2 niveaux food × 2 phases (jour et nuit) × 2 primitives `MOVE_E`/`COLLECT_B`. Exécuter les 16 actions en premier, enregistrer leurs vraies entrées, sorties, `terminal` et SHA, figer la table de référence exacte et le modèle empirique à six deltas. Ne pas utiliser de monde tenu à l'écart à l'entraînement.
- **64** mondes nominaux *heldout* : 4 positions inédites × 2 profils corporels × 2 phases × 2 primitives × 2 effets ingestifs cachés. **Attendus** : 64/64 prédictions partielles à six composantes correctes, 32 paires bénin/létal de perception identique. Cet attendu est issu des résultats ZO déjà connus et n'est pas un nouveau pronostic indépendant.
- **24** mondes adversariaux *heldout*, dont **4 morts motrices** sous `hidden_lethal_east`, **8 dommages à l'intégrité** sous `hidden_danger_here` et **8 erreurs de conséquences numériques** sous `hidden_forced_action_failure`, si ces effets se reproduisent ; aucun paramètre caché n'entre dans le modèle.
- **16** mondes *heldout* en corps aux frontières d'épuisement (énergie 0,5, food 0,25, water 0,1), où les 16 prévisions doivent **s'abstenir** plutôt qu'inventer les effets de clamp. Les mondes physiques appliquent tout de même leur action préenregistrée pour un constat externe.

Les critères ci-dessus sont préenregistrés et **ne peuvent pas être ajustés** aux sorties observées de ZS. Sur un désaccord : `FAIL` documenté, jamais une correction rétrospective des exemples.

## Séparation opérationnelle forte des prédictions

**Job 1 `seal-before-physics` :** exécuter les **16** mondes d'entraînement physiquement ; figer un modèle et sa SHA-256 canonique, puis seulement construire **sans `WorldBody.apply`** les 104 futurs mondes indépendants et leurs captures perceptives initiales. Sur chaque capture, calculer `partial_forecast(frozen_model, firstperson_state, primitive)`. Vérifier que seuls les champs accessibles sont passés à ce modèle; conserver séparément les labels physiques cachés pour le laboratoire, jamais comme entrée du modèle. Écrire un fichier contenant **exactement 104** reçus `{world_id, preaction_firstperson, preaction_sha256, command, prediction, prediction_sha256, model_sha256}`, et un manifeste de preuve `{training_sha256, model_sha256, forecasts_sha256, forecast_count=104, physical_heldout_actions_executed=0, stage=SEALED_BEFORE_HELDOUT}`. Appeler `os.fsync` sur les fichiers, produire le SHA-256 des **octets réels** et sortir du processus et du job. Publier cet artefact sous un nom explicite avec rétention 30 jours. **Aucune création de fichier d'issues réelles dans ce job.** Les labels cachés peuvent figurer dans le recipe-id de traçabilité mais pas dans le contrat de `partial_forecast`.

**Job 2 `realize-after-seal` :** dépend strictement du succès du job 1 et télécharge son artefact scellé; un **nouveau processus** vérifie chaque SHA des trois fichiers sources, le digest du modèle reconstitué et les 104 observations initiales **avant** de lancer une quelconque transition tenue à l'écart. Les mêmes 104 mondes peuvent être construits pour les contrôles perceptifs mais aucune action n'est possible tant qu'ils ne sont pas tous vérifiés. Exécuter ensuite chaque unique commande préenregistrée via `EquipmentCorpusRecorder.record_transition(WorldBody.apply)`, enregistrer l'effet externe y compris décès, conserver la prévision **exactement telle que scellée au job 1**, puis mesurer les erreurs sans rappel à `partial_forecast` après la transition pour une nouvelle émission. Comparer les SHA source pré/post, échouer sur une modification, joindre chaque action à son reçu d'origine par `world_id` et `preaction_sha256`. Écrire un fichier d'effets/scorage externe dont le SHA dépend de l'empreinte scellée.

**Aucun** préfixe B n'est envoyé à I0, aucune ingestion B, aucune reprise après mort, aucun jugement d'agence vécu, aucune facturation UC vécue, aucun canal Oracle→I0.

## Contrôles négatifs prévus

Au minimum : falsification d'un seul octet du manifeste ou d'un reçu pré-action ; substitution du modèle après gel ; score injecté dans le fichier de prédiction ; résultat physique disponible avant publication de l'empreinte ; prévision d'un terminal/safe/integrity ; utilisateur interne d'une étiquette cachée ; prévision sans ressource B visible ; obstacle est visible ignoré ; exemple test placé dans le corpus source ; appariement d'un mauvais monde, état, commande ou phase ; fausse mort ressentie ; reprise postmortem ; UC vécues inventées ; double action sur un monde ; divergence de SHA du commit entre les jobs.

L'audit compare les deux versions Python 3.11/3.12 sans doubler le nombre d'expériences scientifiques. Les fichiers peuvent être identiques ou diverger; le distinguer des résultats numériques. Une discordance de résultats ne doit pas être masquée par un arrondi ou un assouplissement de seuil non préenregistré.

## Verdicts et confidentialité épistémique

- **ZS1 PASS temporel** uniquement si un job/procès de scellement terminé et distinct *précède* toute action heldout et si chaque empreinte de prédiction reste identique dans le second job, avec cas adversariaux SHA bloquants et 104 jointures.
- **ZS2 résultat numérique** : exposer les six erreurs par monde et par composante, les abstentions et les causes externes sans certifier la sûreté. Une concordance n'est pas `safe`.
- **ZS3 contrôle épistémique** : aucun usage des effets `hidden_B`, `lethal_zones` ou `action_failure_schedule` comme entrée du modèle ; les 32 paires nominales doivent produire exactement la même prévision.
- **Si échec** : verdict `FAIL` ou `BLOCKED`, conserver les deux artefacts et ne jamais choisir a posteriori une autre distribution.
- **Aucun** changement à `src/i0`, à la norme v1.3.1, à M11, aux UC, aux garde-fous Stage9/DC-05 et à l'Oracle. Ne pas intégrer le prédicteur partiel dans l'équipement cognitif I0.

**Stage12 scientifiquement PARTIAL, A2.30 PARTIELLE, issue #110 administrativement CLOSED, pas de preuve de compétence alimentaire, pas de fusion automatique.** Le modèle partiel reste un instrument externe de recherche, jamais une proposition sur la responsabilité subjective.
