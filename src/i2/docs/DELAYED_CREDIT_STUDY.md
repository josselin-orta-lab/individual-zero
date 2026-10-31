# I2 : crédit différé par éligibilité temporelle, banc H2 G2

**Statut : TESTED_SYNTHETIC uniquement.** Code : `src/i2/modules/delayed_credit_study.py` ; tests : `tests/i2/test_delayed_credit_study.py`.

Le banc reçoit une suite immuable de transitions **déclarées** : même vie, capture, pas physique, action sémantique, référence d'admission, preuve subjective et delta observé. Un port injecté `verify_lived` doit attester chaque transition ; dans les tests, il s'agit d'un double mémoire, non d'une Perception/M11 réelle. Aucun signal caché du Lab ne sert de récompense.

Une action à court terme coûteuse peut recevoir une association positive lorsqu'une conséquence favorable a été **vécue plus tard**, avec poids rationnels `(numerator/denominator)^lag`, horizon borné et remise à zéro au changement de but. Les effets neutres, défavorables, non observés, les rôles inversés et les délais supérieurs à l'horizon servent de contrôles. Des actions incidentes reçoivent également une part du crédit : c'est une limitation falsifiable **de l'association temporelle, pas une attribution causale démontrée**.

Garde : rejets de preuves d'autre vie, captures/actions admises dupliquées, chronologie inversée, valeurs booléennes, delta non observé avec référence de résultat, faux `True` et paramètres non bornés. Aucun calcul caché d'autorité UC ; aucune publication TD/Q, score d'action, candidat, commande, WorldBody, sommeil, naissance ni récupération M11.

Résultat : prototype exact, déterministe et testable. Il **ne démontre ni l'apprentissage naturel, ni la performance autonome, ni la causalité instrumentale, ni un bénéfice de survie**. Les tests locaux de construction ont été exécutés séparément et la CI GitHub Python 3.11/3.12 doit valider le SHA exact. La porte G1 reste en revue, G3 et G4 non établies, I1 actif. Référence : issue #663.

## Comparaison observationnelle appariée (extension G2)

`compare_matched_outcomes` compare **deux épisodes vécus déclarés de la même vie**, disjoints et de longueur identique, avec un contexte subjectif canonique identique, une même action terminale, une seule action préparatoire différente, et des conséquences terminales effectivement déclarées. Les épisodes doivent être contigus, de même but et vérifiés complètement par un port first-person ; les captures, admissions et références d'issues ne peuvent pas être rejouées. Le calcul rend la différence des résultats terminaux et, uniquement si tous les deltas sont observés, le bilan net. Il ne réutilise aucun score temporel comme valeur Q et ne confère aucune admission.

**Limite critique :** l'égalité de contextes *déclarés* ne garantit ni l'absence de variables cachées, ni la même physiologie initiale, ni la comparabilité des effets d'ordre et de fatigue. L'appariement observationnel ne représente pas un contrefactuel exécuté. Un effet différentiel favorable, nul ou adverse demeure `MATCHED_OBSERVATION_NOT_CAUSAL_IDENTIFICATION`. Les tests de permutation des rôles et d'action incidente empêchent d'en faire un raccourci vers un GO scientifique. Ni intervention aléatoire ni expérience avec corps vivant n'ont été réalisées.

## Epreuve prospective hors echantillon (G2)

`project_matched_outcome` lit seulement deux episodes anciens verifies par des ports synthetiques et une opportunite subjective actuelle sans resultats futurs. `ProspectiveCreditForecast` fige l'ecart d'issues observe dans la paire historique avant toute suite temporelle de test. `score_heldout_forecast` compare ensuite deux nouveaux episodes disjoints, de meme contexte declare et chronologiquement posterieurs ; les observations inverses, les anciennes captures, l'absence d'attestation d'emission et les recurrences d'episodes sont refusees. Le score affiche l'erreur absolue et l'accord de signe, jamais une action, une valeur Q ou une autorisation de reprise. **Limitation :** le port d'emission reste un double, le passe peut etre forge et les episodes ne sont pas randomises. Des evenements de vie reellement M11 et un sceau d'emission anterieur au resultat demeurent non etablis. Cette evaluation ne prouve pas la causalite ni une amelioration comportementale.

## Mémoire de retour d'expérience, pure et bornée (G2)

`OutcomeFeedbackMemory` maintient au maximum 16 écarts d'issues observées sous un même contexte subjectif déclaré, une même vie et les mêmes rôles d'actions. `read_feedback` projette, **avant** une nouvelle conséquence, une moyenne rationnelle de ces écarts passés, ou à défaut la prédiction historique. `learn_from_feedback` requiert une émission préalable attestée par un port synthétique, un résultat tenu hors de la prédiction et une chronologie strictement croissante. La mémoire antérieure demeure immuable, et les épisodes/captures déjà utilisés sont refusés. La prédiction suivante peut s'inverser après une conséquence adverse, mais peut également échouer sur un épisode nouveau : aucun gain systématique n'est revendiqué.

Il ne s'agit ni d'une mémoire M11, ni de TD/Q, ni d'un propriétaire d'état vivant. Aucun coût UC réel ni effet moteur n'est enregistré. Le port d'émission est un double ; les contextes cachés, la sélection et l'absence d'attestation indépendante demeurent bloquants. G3 et l'apprentissage naturel restent NON ÉTABLIS.

## Pont Competition payé, toujours inerte (G2)

`PaidFeedbackValuationPort` est un adaptateur de `ValuationSource` branché sur le `CognitiveCycleFixture` existant. La fonction `evaluate_batch` est appelée **après** le débit synthétique de tous les candidats. Elle refuse les captures étrangères ou périmées, vérifie le cadre courant, les reçus UC et la présence des deux possibilités, puis lit un retour H2 qui ne contient que des observations antérieures. Les valeurs de base de toutes les options restent évaluées. Un contraste positif renforce la préparation, un contraste négatif renforce son alternative ; c'est une **hypothèse de pondération et non une règle validée**. Les valeurs fractionnaires sont refusées et non arrondies. Tous les contrôles Action Control, veto et coûts du banc v2 restent inchangés. Les échecs provoquent le rollback SQLite local. La présence d'un avis ne confère jamais une commande.

Le port de mémoire n'est pas encore un propriétaire durable, ni un Scheduler réel, et les sources de perception et de valeur restent synthétiques. Le choix d'ajuster les valeurs ne prouve ni un apprentissage naturel, ni une meilleure survie. G3 reste `NOT_ESTABLISHED`.

## Frontière preuve d'effet physique (G2, non authentifiée)

`PhysicalEffectClaim` et `verify_lived_physical_correspondence` imposent une correspondance contrôlée entre vie, génération déclarée, admission, commande, pas physique, référence d'événement committé et capture subjective postérieure. Deux vérifications distinctes sont exigées : effet physique committé et perception subjective après cet effet. Une transition terminale est refusée pour l'apprentissage. Aucune donnée ne provient d'un Oracle, et un avis Competition ne constitue jamais un reçu physique.

**Limites :** les ports de test ne sont pas une attestation M11, la génération n'est pas authentifiée indépendamment, et la vérification ne modifie ni mémoire ni décision motrice. Cette interface ne garantit pas la vérité d'un événement, l'atomicité, le non-rejeu mondial ni la mortalité d'un véritable individu. G3 demeure `NOT_ESTABLISHED`.

Le garde-fou de compatibilité rejette explicitement une étiquette de génération différente de `I2` et toute conséquence non observée. Cette étiquette locale n'est **pas** une attestation cryptographique de génération : l'authentification reste entièrement absente du port simulé.

## Crédit conditionné à une chaîne physique déclarée (G2)

`study_physically_linked_credit` vérifie, avant tout calcul de crédit, une correspondance 1:1 entre chaque transition subjective et chaque effet physique déclaré, une chaîne continue d'états avant/après et de pas, l'absence de références de COMMIT et d'admission rejouées et l'absence d'effet terminal. Un refus annule tout résultat, sans crédit partiel. Les attestations demeurent des doubles de test sans ancre WorldBody/M11 : la cohérence d'une chaîne déclarée n'établit ni réalité physique ni causalité. Aucun droit moteur, aucun propriétaire supplémentaire.

Une action réellement appliquée peut laisser l'état inchangé ou ramener le corps à un état précédemment vu. Le contrôle G2 ne confond donc plus égalité de digest avant/après ou retour d'état avec un rejeu. Les refus restent fondés sur les identifiants de COMMIT/admission, la séquence de pas et la continuité entre effets. Ceci ne constitue toujours pas une preuve de publication M11 indépendante.

L'adaptateur Competition exige désormais aussi `verify_feedback_issue(readout)` avant que la calibration H2 soit prise en compte. Un pronostic historique attesté ne suffit pas à autoriser un retour de calibration recalculé : si l'émission de ce retour n'est pas attestée, le banc SQLite annule le débit synthétique et l'avis. Cette vérification passe encore par un double de test, pas par M11.

Le reçu `FeedbackReadout` lie maintenant son émission à l'empreinte canonique du **contenu complet** de `OutcomeFeedbackMemory`, y compris les références d'émission et d'épisodes. Deux historiques de même longueur et même moyenne ne sont plus interchangeables lors d'une mise à jour, et l'évidence synthétique de Competition lie également cette empreinte. SHA-256 local ne prouve ni authenticité des observations ni garde M11 externe.

La mémoire H2 conserve une **fenêtre glissante de 16 observations**, un compteur cumulatif et une tête de chaînage locale des retours. Elle ne devient donc pas inutilisable après la 16e expérience. Les anciens éléments sortis de la fenêtre ne sont plus inspectables individuellement par cet état; le chaînage n'est pas une preuve M11 et ne suffit pas à empêcher un rollback d'une copie entière. La limite totale de démonstration est d'un million de retours synthétiques.

## Contrat de transition H2 vers un COMMIT unique (G2)

`feedback_transition_contract.py` valide purement une transition de memoire depuis le digest exact de l'etat precedent : identite et but inchanges, progression de version d'une unite, avancee du pas physique, journal chaîné et references des nouveaux resultats. Refus du rejeu, de l'ancien digest, du score altere et d'un droit moteur. Il s'agit **uniquement d'un validateur**, sans colonne, table, commit, reprise ni source M11 : l'owner transactionnel unique n'est PAS encore branche a ce contrat. Une mise a jour de memoire par un port synthetique ne demontre pas son origine physique.

## Intégrité hors échantillon au COMMIT v5

Avant d'accepter un score H2 dans le journal cognitif, le validateur recalcule la prédiction uniquement à partir des différences **antérieures** conservées dans la fenêtre de mémoire, ou de la prévision de base si la fenêtre est vide. Il refuse la substitution d'une prédiction choisie après observation de la conséquence, même si l'erreur rapportée est cohérente avec cette substitution. Il refuse également tout recouvrement entre épisodes d'entraînement et épisodes déclarés hors échantillon. Cela renforce la cohérence du banc G2, sans authentifier les sources ou établir un gain comportemental réel.

## Comparaison auditée du journal H2 (G2)

`CognitiveCycleFixture.feedback_scorecard()` relit le journal v5 après vérification intégrale, et calcule les erreurs absolues moyennes exactes du retour H2, de la prévision historique figée et du dernier résultat observé (référence persistance, avec repli initial vers la prévision historique). Les trois prédictions sont établies uniquement depuis les états antérieurs ou reçus committés, sans utiliser l'issue courante avant son score. La méthode ne crée aucun stockage ni aucune autorité motrice, et expose aussi les résultats défavorables. Les scénarios restent choisis pour la validation logicielle ; ni échantillonnage indépendant ni protocole confirmatoire préenregistré ne sont établis.

## Batterie de régimes fixés avant leur exécution (G2, non confirmatoire)

`tests/i2/test_h2_frozen_regime_battery.py` définit **avant le calcul des scores** cinq suites indépendantes de 24 observations : défavorable stable (-8), conforme à la prévision historique (+7), inversion après 12 observations (-8 puis +7), alternance (-8/+7) et dérive entière de -8 à +15. La métrique primaire est la moyenne des erreurs absolues (MAE) sur les 24 prévisions ; les références sont la prévision historique de +7 et la persistance du dernier résultat. Aucun paramètre ni scénario n'est sélectionné après consultation des résultats. Chaque suite recommence sur une base SQLite v5 neuve ; les 24 événements sont committés, le propriétaire est rouvert à froid à chaque cycle, le scorecard lit et audite le journal, et les refus de contexte étranger et les interruptions avant/après COMMIT sont vérifiés. Les cinq résultats, y compris les contre-performances H2, sont publiés dans les logs de tests. Ce protocole est fixé **dans le même développement que les tests** et ne constitue donc pas un préenregistrement indépendant ni une preuve de généralisation, d'action motrice ou de causalité physique.

## Comparateur fantôme à horizon court (G2)

`test_h2_shadow_horizon_heldout.py` compare, sans changer H2 ni le journal v5, quatre prédicteurs en fractions exactes : moyenne H2 sur 16, moyenne fantôme sur 4, historique +7, dernier résultat. Deux séquences de conception et quatre séquences de vérification distinctes sont fixées dans le test. Tous les résultats, favorables ou non à la fenêtre courte, sont rapportés ; un contrôle de préfixe vérifie l'absence de fuite depuis des observations futures. Cette comparaison est calculée en mémoire et non depuis un journal v5 committé. Elle n'est ni un préenregistrement externe ni une preuve de gain généralisable, causal ou naturel. Aucune politique d'I2 n'est modifiée.

## Sélecteur fantôme d'horizon issu du journal (G2)

`feedback_horizon_shadow_report()` applique une règle fixe en lecture seule aux événements H2 du journal v5 intégralement audité : choisir une moyenne sur quatre observations seulement lorsque ses erreurs absolues sur les huit observations **précédentes** sont strictement inférieures à celles de la moyenne sur seize ; autrement retenir seize. Le premier choix et les égalités restent sur seize. Les cinq régimes de la batterie #710 sont rejoués pour contrôler la cohérence du choix et les résultats défavorables sont conservés. Ce n'est pas une politique motrice ni une preuve hors échantillon indépendante : la règle a été développée après observation de batteries précédentes. Aucun paramètre du moteur H2, aucun schéma SQLite et aucune naissance I2 ne changent.

## Vérification distincte du sélecteur 4/16 (G2)

`test_h2_fresh_committed_selector.py` fixe quatre régimes supplémentaires de 24 issues, différents des batteries #710 et #711. Le sélecteur #712 est inchangé. Chaque scénario utilise 24 COMMITs dans son propre journal v5, une relecture froide et un rapport de MAE exact pour sélection 4/16, horizons fixes, historique et persistance, y compris résultats défavorables. Un scénario injecte une erreur avant COMMIT et la perte de son accusé après COMMIT. Résultats imprimés sans filtrage. Les scénarios sont conçus dans cette PR : ce n'est pas une préinscription indépendante ni une validation de politique motrice.

## Comparateur fantôme à trois prédicteurs (G2)

`feedback_three_way_shadow_report()` compare H2-16, H2-4 et persistance depuis les scores du seul journal v5 audité. La règle fixe utilise les erreurs des huit épisodes strictement antérieurs, avec départage déterministe 16, puis 4, puis persistance. Trois nouveaux régimes sont testés sur des COMMITs synthétiques, sans changement de l'apprentissage, du stockage ni de l'autorité motrice. Les tests ne fournissent pas une préinscription indépendante ou une preuve de généralisation ; les performances défavorables doivent être conservées.
