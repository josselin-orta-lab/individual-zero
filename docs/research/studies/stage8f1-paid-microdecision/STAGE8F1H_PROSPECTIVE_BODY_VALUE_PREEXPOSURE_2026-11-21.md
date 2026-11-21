# Stage8-F1H · valeur corporelle prospective d'une décision librement influencée par une mémoire acquise

**Plan F1H figé le 21 novembre 2026, AVANT toute exécution F1H.** Base technique Git **`3ad4cb687b403214c9b9f6055b46a489dca44af4`**. Cette étude est indépendante des résultats et critères déjà fermés F1D, F1E, F1F et F1G. Aucune modification de leur code, de leurs logs, de leur rapport, de leurs verdicts ou de leurs préenregistrements n'est autorisée.

## Question expérimentale

La modification motrice causée par le **contenu personnellement appris, conservé et réellement facturé** dans F1F (`full→se_deplacer E` contre `mask_both→se_deplacer N`, écologie `mixed_here_water_east_food`) procure-t-elle un **avantage corporel ultérieur observable** lorsque chaque individu continue à décider, apprendre et payer lui-même son calcul ?

La comparaison est **conditionnelle à la divergence motrice déjà observée dans F1F**. Ce contexte n'est PAS une validation indépendante de la découverte et l'étude ne peut démontrer un effet moteur universel. Les sept autres écologies déclarées avant F1F sont conservées intégralement, sans sélection favorable, comme sondes prospectives de robustesse : `bare`, `water_here`, `water_north`, `water_east`, `water_west`, `food_here`, `food_east`, `mixed_here_water_east_food` dans cet ordre.

**Racines octet-verrouillées** :
- F1C, original de l'expérience réellement payée, run #44837981694, artifact #14679910820, fichier `F1C_PAID_NATIVE_ORIGINAL.json`, SHA256 `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d` ;
- F1F, original des 8 mondes / 24 décisions natives, run #44892635999, artifact #14702338615, fichier `F1F_ECOLOGICAL_ORIGINAL.json`, SHA256 `f620d1b46ddf269dc368dcd90ba6c93f44f0b6442f8d9e6322440de32e3fbab5` ;
- F1F, contre-audit indépendant, même run, artifact #14702267579, fichier `F1F_COLD_ECOLOGY_AUDIT.json`, SHA256 `8013f2add1f3eb0190127bb77eac588c95f153f32ba21113302bafa0292e2ac2`.
- Les verdicts F1G TD/tampon `0/8`, inchangés : run #44893263579, original `a7f0782886b3d2b97cd91ea11803934f31736b91e6d659c700a3d1dd886a8376`, contre-audit `ec3b1c953c69d87dc042ab81da55809984e7b78c175a2697a6b3d0a24fa21310`. Pas de réouverture ou de reclassification.

## Épisode, horizon et interventions fixés

**Horizon final strict : tick `T=12` inclus**, source F1C réelle au tick 1 et décision F1F réexécutée **naturellement** au tick 2, suivie de ticks 3 à 12, soit 11 `World.step` ultérieurs à l'apprentissage initial par bras (sauf mort irréversible). Aucun allongement, déplacement de l'horizon, ajout de monde ou sélection d'actions après exposition aux résultats F1H.

Pour chacune des **huit** écologies déjà figées, construire le `WorldSpec` natif à partir de `stage8f1f_native_ecological_contexts.ECOLOGIES` : mêmes corps, ressources, apparition des stocks au tick 1, même graine de l'individu et mêmes `BodyLaws v2`. Rejouer la **même** première action `dormir` librement décidée par `PaidMicrodecisionMind.decide` et effectivement appliquée par `World.step`; exécuter et **payer** l'apprentissage F1C via `prepare_learning` puis `World.pay_cognition` avant `learn_from_outcome`. Vérifier **bit pour bit** la mémoire F1C originale, ainsi que les 8 reçus au tick 1 déjà fermés.

À partir de ce point, **trois copies profondes de chaque monde et de la même mémoire F1C acquise**. Au tick 2 seulement :
- `full` : le cerveau lit ses moyennes authentiquement apprises ;
- `sham` : exactement les mêmes moyennes, mais passage par la copie d'intervention de laboratoire (neutralité obligatoire) ;
- `mask_both` : uniquement les moyennes `("dormir",)` et `("*",)` sont présentées à la lecture avec leurs **vraies valeurs F1C d'avant apprentissage**, sans changer les stats `n_eff/count`, buffer, TD, RNG, mémoire occupée ni perception ; toutes les mémoires vraies sont restaurées **avant** la physique.

Les trois **choix tick 2**, leurs `CognitiveWork`, leurs débits natifs et les témoins mentaux avant/après doivent **correspondre exactement à l'original F1F** (JSON source SHA-verrouillé), sinon `INVALID_F1F_TICK2_ANCHOR`. Le `sham` doit rester strictement identique à `full`.

## Continuation libre et financement réel (aucune action imposée)

À la suite du vrai `World.step` au tick 2, et à chaque tick **jusqu'au tick 12**, exécuter l'enchaînement natif :

1. `Mind.observe_outcome` si `last` existe, sans avantage gratuit (déplacement et perception corporelle) ;
2. `Mind.prepare_learning` avec un **nouveau** `CognitiveBudget` correspondant au corps réel après motricité ; ne rien apprendre si mort, `last is None` ou base de travail non finançable ;
3. si un travail d'apprentissage positif est autorisé, le débiter **immédiatement** avec `World.pay_cognition` des **deux monnaies** avant toute écriture de mémoire, actualiser le résultat avec le vrai corps après paiement comme dans le runtime i3, puis `Mind.learn_from_outcome` avec **exactement** le nombre de replays préfinancés ;
4. pour les ticks suivants, `World.capture` puis `PaidMicrodecisionMind.decide(capture,CognitiveBudget(...))`, et `World.step(action,param,work)` natif, sans autre intervention mémoire ou exogène.

Aucune politique prescrite, aucun choix/rejet imposé, aucun secours médical/énergétique, aucune suppression d'une mort ni fermeture artificielle de boucle. Une absence de financement doit laisser le moteur retourner son abstention native. Aucun `World.step` après mort. Le même `WorldSpec` reste en vigueur, **y compris le token alimentaire F1F `f1f-neutral-food` sans `token_effects`** : ne pas inventer d'effets nutritifs favorables ou défavorables. Si ce manque rend une action `manger` inexécutable, consigner une **défaillance d'ingénierie explicite**, ne pas réécrire les lois ou retirer le monde.

Pour chaque pas, sceller : horodatage tick, capture première personne, copie mentale complète avant et après décision, action choisie et paramètre, `CognitiveWork`, facture native `World.step` énergie/vigilance et `remaining`, corps et position, inventaire/ressources/lois, puis préparation/apprentissage/debit postaction, `Mind` après apprentissage et états mentaux d'origine F1C. Les factures de cognition des trajectoires peuvent **légitimement différer après le tick 2**, car les décisions et états corporels divergent ; **il est interdit de les égaliser artificiellement**. Les coûts doivent être identiques à l'instant du contraste tick 2; après ce tick, ils font **partie des conséquences** à mesurer, pas un biais à corriger a posteriori.

## Critères et classification préexposés

**Population d'analyse descriptive : 8 écologies déterministes, 3 bras chacun ; comparaison principale conditionnelle au contexte mixte préalablement connu comme différent.** Les 7 autres contrastes sont rapportés intégralement, y compris les éventuelles divergences apparues aux ticks suivants.

- **Critère primaire d'adaptation, `restricted_survival`** : à tick 12, comparer les **ticks physiques vécus après le fork** des bras `full` et `mask_both` : 11 si survie jusqu'au tick 12, sinon nombre de transitions exécutées jusqu'à et incluant le tick de mort. Un bénéfice de survie de la décision influencée par la mémoire n'est déclaré **que** si, **dans le contexte mixte**, `full` a plus de ticks vécus que `mask_both` sans mort cachée. Si égalité, `NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12`. Si inférieur, `SURVIVAL_DISADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12`. Cette classification est conditionnelle et locale. Un décès au tick 12 compte comme décès, mais peut donner le même nombre de ticks : consigner aussi `alive_at_T12`, et en cas d'égalité de compte mais différence de survie, classer **en faveur du survivant à T12**.
- **Critère secondaire corporel**, si les deux bras survivent jusqu'au même tick : comparer sans pondération arbitraire les **cinq réserves corporelles** `[énergie,nourriture,eau,intégrité,vigilance]` après chaque facture et apprentissage. **Dominance corporelle stricte au terminal** uniquement si chacune des 5 réserves du bras `full` est au moins celle du contrôle et au moins une strictement supérieure, à tolérance absolue `1e-9`. Une domination inverse est défavorable ; toute compensation entre réserves est `MIXED_BODILY_TRADEOFF`, pas un « gain adaptatif ».
- **Critères secondaires non promotionnels** : intégrales brutes des 5 réserves sur les ticks ayant un état réellement observé, minimum des 3 réserves vitales `food/water/integrity`, compteur d'accès à l'eau, aliment ramassé/consommé, positions, survie au terminal, dépenses cumulées `CognitiveWork` décision/apprentissage et **coûts énergie/vigilance** ; aucune comparaison d'intégrales entre suivis de longueurs différentes sans préciser le nombre de ticks. Aucun indice composite ad hoc.
- **Sham obligatoire** : `full` et `sham` produisent la **même chaîne d'actions, de corps, d'apprentissages et de hashes** aux 8 contextes. Si `sham` diverge à un seul tick, `INVALID_SHAM`.
- **Portes d'audit** : original F1C byte-exact, original F1F et audit froid byte-exact, copie exacte des 24 reçus du tick 2, financement `World.step` et `World.pay_cognition` de toutes les monnaies, pas d'apprentissage sans prépaiement, source et changements écologiques intacts, pas d'actions après mort. Si une porte échoue : **`INVALID_PROSPECTIVE_ADAPTIVE_VALUE`**, aucun succès de survie ni de dominance ne peut être déclaré.
- **Résultat indéterminé** si incapacité à exécuter un tick natif ou fin anticipée pour une raison non vitale : **`INCONCLUSIVE_NATIVE_CONTINUATION`**, publier l'erreur, le dernier tick original et les reçus conservés sans adapter le protocole.
- **Interprétation causale** : un effet corporel éventuel est celui de **l'intervention limitée de lecture au tick 2 avec tous ses médiateurs naturels** (commande, position, état compétitif, apprentissage futur). **Ce n'est pas une estimation isolée de « Est contre Nord »** à état interne identique, car imposer le moteur pour l'isoler violerait l'autonomie. Une différence de position seule ou un écart de score ne constitue pas un bénéfice adaptatif.

## Reproductibilité et statut

Deux processus Python 3.11 indépendants rendent un JSON **octet-identique**, avec source/provenance et preuves originales conservées. Un second job Python 3.12 **stdlib-only, n'importe ni `Mind`, `World`, `BodyLaws` ni le producteur**, refait toutes les factures, la physiologie native des cinq réserves et le classement selon les critères fixés; manipulations malveillantes rescellées, fausses ressources, résurrections et résultats positifs falsifiés doivent être rejetés. Archiver les originaux et le contre-audit hors de la limite des 90 jours des GitHub Actions.

**Portée maximale** : causalité corporelle de **trajectoires synthétiques conditionnelles** au fork F1F, pas de preuve d'utilité adaptative générale, ni de succès d'apprentissage hérité, ni de mémoires G2 historiques. Aucun `run_life`, naissance, nouvelle cohorte ou promotion du moteur i3. F1D/F1E restent négatifs, F1F reste **1/8 effet de commande**, F1G **0/8 TD + 0/8 tampon**. Stage8-E2 gamma reste irrévocablement `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`.
