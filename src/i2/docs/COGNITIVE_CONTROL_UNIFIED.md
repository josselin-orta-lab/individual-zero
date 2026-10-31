# I2 : contrat unique du banc cognitif (v4)

**Proposition expérimentale inerte. I1 reste l'unique génération active.**

Le banc `CognitiveCycleFixture` impose désormais un **seul schéma SQLite**, `i2-unified-cognitive-lifecycle-fixture-v4`, combinant intention, candidats visibles, débit UC synthétique, Competition, revue Action Control, origine synthétique et terminal absorbant dans un seul journal et une seule transaction locale. Les ports `observation_source`, `valuation_source`, `current_source`, `safety_source`, `genesis_ref` et `terminal_source` sont obligatoires.

Les anciens modes cognition seule v1, contrôle optionnel v2 et cycle de vie v3 ne sont **plus acceptés**. Il n'existe aucun adaptateur, aucune migration implicite et aucune possibilité de relire un ancien fichier sous le nouveau schéma. Les anciens fichiers sont des artefacts historiques hors exécution.

La relecture rejoue intention, coûts, avis, veto, chaînage, origine et terminal. Une faute avant COMMIT annule l'ensemble ; une confirmation perdue se traite par inspection froide sans réexécuter l'action. Tout résultat conserve `motor_authority=NONE`. Ce banc n'est pas un propriétaire WorldBody, une comptabilité UC vivante ni un témoin M11 indépendant. La mémoire H2 n'est pas encore incluse dans le COMMIT : ce verrou G3 reste à traiter.

Les tests I2 constituent une validation logicielle synthétique, pas une preuve d'apprentissage autonome, de naissance ou de mortalité physique.
