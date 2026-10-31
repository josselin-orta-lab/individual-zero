# I2 : crédit différé par éligibilité temporelle, banc H2 G2

**Statut : TESTED_SYNTHETIC uniquement.** Code : `src/i2/modules/delayed_credit_study.py` ; tests : `tests/i2/test_delayed_credit_study.py`.

Le banc reçoit une suite immuable de transitions **déclarées** : même vie, capture, pas physique, action sémantique, référence d'admission, preuve subjective et delta observé. Un port injecté `verify_lived` doit attester chaque transition ; dans les tests, il s'agit d'un double mémoire, non d'une Perception/M11 réelle. Aucun signal caché du Lab ne sert de récompense.

Une action à court terme coûteuse peut recevoir une association positive lorsqu'une conséquence favorable a été **vécue plus tard**, avec poids rationnels `(numerator/denominator)^lag`, horizon borné et remise à zéro au changement de but. Les effets neutres, défavorables, non observés, les rôles inversés et les délais supérieurs à l'horizon servent de contrôles. Des actions incidentes reçoivent également une part du crédit : c'est une limitation falsifiable **de l'association temporelle, pas une attribution causale démontrée**.

Garde : rejets de preuves d'autre vie, captures/actions admises dupliquées, chronologie inversée, valeurs booléennes, delta non observé avec référence de résultat, faux `True` et paramètres non bornés. Aucun calcul caché d'autorité UC ; aucune publication TD/Q, score d'action, candidat, commande, WorldBody, sommeil, naissance ni récupération M11.

Résultat : prototype exact, déterministe et testable. Il **ne démontre ni l'apprentissage naturel, ni la performance autonome, ni la causalité instrumentale, ni un bénéfice de survie**. Les tests locaux de construction ont été exécutés séparément et la CI GitHub Python 3.11/3.12 doit valider le SHA exact. La porte G1 reste en revue, G3 et G4 non établies, I1 actif. Référence : issue #663.
