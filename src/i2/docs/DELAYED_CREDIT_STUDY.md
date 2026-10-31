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
