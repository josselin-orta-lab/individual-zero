# Stage 11 / Stage 12 issue #110 : préenregistrement de l'arbitrage intrinsèque/extrinsèque

Date : 14 octobre 2026. Version prospective avant toute modification du banc d'expérience. Décision validée par l'opérateur : poursuivre l'investigation des objectifs progressifs sans priorité artificielle. Norme : MVP v1.3.1, héritage v1.2.1 §8.5 et registre P-15 (poids intrinsèque w_m >= 0).

## Raison scientifique

Dans la campagne préfixe prospectif [#38558243904](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38558243904), au pas 2/cycle 2, l'option géographique a une marge normalisée de +1,1786033 et l'option de progression alimentaire de +0,0053882. L'exploration exploite un signal intrinsèque indépendant et un poids P-15 fixé à 0,75 par le profil de développement. Cette dissymétrie peut expliquer l'absence de commande `active_goal`. La présente expérience **ne conclut pas** qu'un changement de coefficient est bon : elle mesure la sensibilité et le coût comportemental opposé.

## Comparaison, fixée avant résultats

- Facteur P-15 pré-naissance : `w_m` = **0.75 (contrôle de référence), 0.35, 0.0 (ablation)**. Ni adaptation réactive à la réussite d'une action ni arbitrage par l'évaluateur, et surtout **aucune modification du code de Competition**.
- Monde : `restored` et `sustained` du pilote précédent, avec variante `free` et intervention indépendante A2 (obstacle à t2 après admission, retrait à t4).
- Pour toutes les vies : Stage6 `progressive_subgoals=True` et `progressive_evaluation_prefix=True`, profondeur 3, budget Stage8 `H_eff=3`, corpus physique strictement pré-naissance identique et indépendant ; expérience de 36 pas physiques maximum.
- **12 vies uniques × 36 pas = 432 pas maximum**, sous Python 3.11 et Python 3.12 comme répétition technique des *mêmes* conditions et non 24 sujets.
- Les vies dont l'exploration échoue par absence d'evidence (`w_m=0`) sont enregistrées explicitement, pas dissimulées comme succès d'agence. Le fait qu'un objectif arrive au seuil ou qu'une action soit exploratoire n'est pas une preuve de responsabilité causale.

## Mesures et hypothèses falsifiables

1. Sélection autonome d'une option `active_goal` et exécution effective de sa première commande (séparée des candidatures à seuil franchi).
2. Progrès alimentaire vécu et critères de but, jugements `self/world/unknown`, paires Stage12 réellement consommées, fenêtres 2 success / 2 failure. Comparer tous les résultats à la politique naïve réussite->self/échec->world **seulement si assez de résultats**.
3. Conservation de l'exploration intrinsèque légitime : commandes `cible_exploration`, nombre de nouveaux sites physiques distincts, diversité des actions et trajets. **Réduction de la curiosité à zéro est une ablation, jamais une recommandation automatique.**
4. Valeur ex ante de l'option géographique et du but, score, classement, admissions et veto par cycle. Les labels d'agence et leur provenance ne doivent dépendre que des captures d'I0.
5. Charges UC, entrées de sommeil, transitions réellement closes, WAL et audit de conservation de journal, intégrité M11, absence de régression de mortalité.

Les métriques doivent être calculées indépendamment à partir des journaux JSONL, et chaque vie possède sa propre identité. Les différences binaires inter-Python de valeurs flottantes Stage8 restent signalées.

## Règles de décision

- Si diminuer P-15 rétablit la poursuite des buts **sans effondrement de l'exploration légitime** : décrire la plage prometteuse, mais toute recommandation de P-15 demande une campagne indépendante, incluant des situations où l'exploration est utile au maintien de la vie. Ne pas sélectionner un P-15 a posteriori pour rendre le biais détectable.
- Si seule l'ablation w_m=0 fonctionne : **échec de l'équilibre**, non solution. Étudier un arbitrage intrinsèque/extrinsèque fondé sur données légitimes et cohérent avec les invariants INV-11, INV-14 et P-15 ; proposer une adaptation normative seulement après analyse.
- Si tous les profils restent non pertinents : localiser le blocage en aval (réception et admission), ne pas multiplier les expériences.
- Ne pas modifier les seuils `attribution_bias`, forcer des commandes ni ajouter des labels Oracle.

Stage12 non reçu, issue #110 ouverte et PR #155 en brouillon jusqu'à réception opérateur explicite.
