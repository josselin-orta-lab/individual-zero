# Stage8-F1E | effet isolé du CONTENU de mémoire à coût cognitif strictement identique

**2026-11-21 · préenregistrement, avant premier reçu F1E.** Code de référence Git `3dd12c94843ca2cadf1af5c885b9eb215db31553`. L'original F1C (deux bras, apprentissage postaction réellement financé) reste fichier `F1C_PAID_NATIVE_ORIGINAL.json`, SHA256 `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d`, artifact #14679910820, [Actions #44837981694](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837981694). Le verdict Stage8-F1D `NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE` reste **négatif, fermé** pour cette comparaison. Stage8-E2 gamma123 reste `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`.

## Hypothèse principale falsifiable

Dans le même F1C à mémoire **entièrement apprise, réellement payée et conservée**, le **contenu numérique des effets vécus** (et non l'existence ou le nombre de souvenirs) influence-t-il l'action motrice de `PaidMicrodecisionMind.decide` immédiatement suivante ? Le même corps, la même capture, les mêmes paramètres génétiques, RNG, carte, `values`, `buffer`, stats (clés, nombres `n_eff` / `count`) et tous les coûts cognitifs doivent être identiques au début des deux décisions. L'individu sélectionne librement son action, y compris l'abstention ; aucune règle n'impose sommeil, déplacement, réussite ou secours.

**Intervention F1E strictement limitée au readout** : sur une **copie détachée** de l'EffectsModel du Mind F1C `retain`, durant le calcul de la décision seulement, masquer les **cinq moyennes** des clés `("dormir",)` et `("*",)` en les replaçant par les moyennes correspondantes de l'instant original F1C `private_before_postaction_learning`, **elles-mêmes déjà apprises synthétiquement avant le tick 1**. Les vraies stats acquises `n_eff`, `count`, et tous leurs nombres d'entrées restent **strictement inchangés**, y compris l'incertitude. Les `buffer` et `values` post-learning restent conservés dans les deux bras, de même que la mémoire réelle sous-jacente : la substitution est **temporaire pendant la lecture**, puis annulée, sans écraser l'état appris original. Ce n'est **pas** une politique i3, pas une invention de connaissance, ni une reconstitution d'un G2 vécu.

## Conditions fixées (une écologie synthétique déjà utilisée, pas une exploration posthoc)

Toutes les conditions repartent de la **même** reconstruction exacte de `F1C.retain`, source SHA-vérifiée, après le `World.step(dormir)` choisi par l'individu et la `World.pay_cognition` de l'apprentissage, au tick **1**, corps `[2.9096, 74.63, 59.6, 90.2, 98.776]`, puis exécutent **une seule** décision et **un seul** `World.step` supplémentaire (tick 2).

| Condition | Intervention temporelle sur les moyennes numériques de lecture |
|---|---|
| `full` | aucune, lecture authentique F1C et apprentissage conservé |
| `sham` | assigner temporairement la **même** moyenne après apprentissage, puis restaurer (contrôle intervention-neutre) |
| `mask_both` | contrôle primaire, moyennes `dormir` et globale `*` remplacées par les moyennes personnelles d'avant l'expérience, compteurs inchangés |
| `mask_sleep_only` | analyse secondaire : seule moyenne d'action `dormir` masquée |
| `mask_global_only` | analyse secondaire : seule moyenne globale `*` masquée |

**Interdiction** d'ajouter, supprimer ou sélectionner des contextes, actions ou niveaux de mémoire en observant la sortie. Les cinq variantes ont le **même** `Mind` privé avant l'application des masques. Les cinq décisions ont des `CognitiveWork` et des débits `World.step` énergie/vigilance **identiques** ; à défaut, **`INVALID_EQUAL_COST_GATE`**. Un masque qui change `n_eff`, `count`, les tailles du buffer, les RNG ou les génomes invalide également le résultat. Un `sham` qui diffère de `full` dans sa décision ou ses factures est également **`INVALID_SHAM_NEUTRALITY`**. La restauration immédiate de l'EffectsModel authentique doit être vérifiée après chaque calcul et après la physique.

## Critère primaire et falsificateurs

Comparer `(action,param)` de `full` à `mask_both`. Un **effet comportemental isolé du contenu des moyennes** n'est démontré, *dans cette seule écologie synthétique*, que si la commande native diffère **et** si chaque facture `CognitiveWork`, les deux débits, les conditions corporelles, la capture, les stats de structure et le contrôle sham sont strictement appariés. Si commandes égales, **`NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE`**, même si les scores, plans, prévisions ou états d'apprentissage sont différents. En cas d'intervention non neutre, de facture divergente, d'incertitude modifiée, de téléchargement F1C incorrect ou de physique native non reproductible, le verdict est **`INVALID_OR_INCONCLUSIVE`**. Toute conclusion non préenregistrée est une observation exploratoire et ne peut « sauver » le test.

Les lectures ne peuvent ni consulter le monde caché ni modifier les lois physiques, les positions, les ressources ou les données premières de F1C. Conserver instantanés mentaux typés complets avant, pendant et après le masque, les corps, entrées `World.capture`, tâches `CognitiveBudget` exactes et reçus `World.step` exacts avec SHA256. Ne pas réexécuter une cohorte, une vie ou le Stage8-E2 clos.

## Vérification indépendante et règle d'arrêt

Deux processus producteur Python 3.11 doivent restituer des fichiers **octet-identiques**. Un second job Python 3.12 **sans importer World, Mind ni le générateur** doit lire l'archive via GitHub Actions, réauditer froidement le JSON F1C exact, valider l'unique changement numérique autorisé, les incertitudes/compteurs identiques, les transactions physiques (5 reçus natifs au deuxième pas, et F1C original vérifié), les factures égales et le critère moteur. Tests malveillants avec rescellement des reçus pour rejeter factures contrefaites, contexte changé, contenu modifié hors masque, sham incorrect et verdict positif requalifié.

Portée maximale, même en cas de divergence : **`SOFTWARE_ONLY_SYNTHETIC_EXACT_COST_EFFECT_CONTENT_CAUSAL_INTERVENTION`**. Aucun gain de survie, d'héritabilité ou de généralisation, aucune équivalence aux souvenirs historiques G2, aucun `run_life`, aucune nouvelle vie/cohorte, aucun Stage8-E2 réouvert. Les preuves brutes doivent survivre au-delà des **90 jours** de rétention GitHub Actions via une conservation indépendante distincte.
