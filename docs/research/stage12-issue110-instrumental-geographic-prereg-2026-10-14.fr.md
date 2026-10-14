# Issue #110 : préenregistrement de la motivation instrumentale géographique liée à un but

Date : 2026-10-14. Approbation opérateur : poursuivre le modèle distinguant exploration intrinsèque et exploration instrumentale. Document créé **avant** toute implémentation.

## Hypothèse, mécanisme et frontière

Les études précédentes ont montré : Stage6 `partial_progress` réellement proposé ; Stage8 prévoit un bénéfice du préfixe alimentaire ; une option de progression vers une ressource franchit le seuil de Competition mais arrive derrière une exploration géographique du **même premier déplacement**. Baisser P-15 de 0,75 à 0,35 puis 0 diminue à la fois l'exploration et la poursuite du but, et ne constitue donc pas une solution.

Nous testerons une alternative respectant DC-01, INV-11, INV-14, INV-16 et DC-10 : une **option déjà née chez Planning avec `motive_ref=active_goal` et `goal_ref` actif** peut recevoir, pendant sa valuation ordinaire, un intérêt de découverte indépendant provenant d'Exploration **seulement** lorsque :
1. La planification progressive avec préfixe prospectif a **déjà produit** le plan, grâce à Equipment borné. Le plan est identique à la proposition courante du propriétaire Stage6, avec première commande `se_deplacer`, première destination identique à une frontière effectivement offerte par Exploration depuis la capture courante, et un horizon de prévision strictement supérieur au premier pas.
2. Le premier pas et la frontière sont admissibles selon le contrôle déjà existant. Aucun segment n'acquiert une capacité de contournement du veto.
3. La simulation de Stage8 a le statut **computed** avec une valeur prospective **positive** ; modèle inconnu, simulation incomplète, résultat nul/négatif, incohérence de provenance ou frontière vieillie ne produisent **aucun** intérêt instrumental supplémentaire.
4. Exploration délivre un intérêt fondé sur la visite *nouvelle* et l'état de tempérament courant, avec **le même signal de nouveauté existant** que pour l'option intrinsèque équivalente. L'évaluation vérifie qu'il n'est pas déjà présent dans les signaux extrinsèques (pas de double comptage **dans la même option**). L'option géographique d'origine reste indépendante, toujours concurrente et créditée de son motif `cible_exploration`.
5. Le motif `active_goal` est fixé **avant** décision par Stage6, jamais recréé après déplacement et jamais attribué à la commande intrinsèque retenue. La présence de m_a n'est ni une preuve de satisfaction du but, ni une causalité `self/world`.

**Score expérimental** : composante extrinsèque préexistante `e_ext` calculée par Stage8, puis **exactement DC-01** `clip(e_ext + w_m * m_a)`, pas de bonus spécifique instrumental ni modification de Competition/threshold/noise. `w_m=0.75` comme référence précédente. Option activée via drapeau Stage11 `instrumental_geographic_value=False` par défaut. Les autres mécanismes, corpus Equipment, budget UC, C_max, seuil d'agence et Oracle restent strictement inchangés. La lecture du plan existant par le service Stage11 se produit seulement en phase d'évaluation, sans simulation supplémentaire, et est dépendante du modèle cognitif autorisé, jamais d'une vérité physique cachée.

## Protocole prospectif

Quatre profils physiques déclarés : `restored` (food 35, gain 30, decay 0), `sustained` (food 24, gain 6, decay 0.7), `replenished` (food 35, gain 40, decay 2), `urgent` (food 35, gain 50, decay 4). Deux conditions : `free`, `A2` (obstacle externe après admission au pas 2, retrait avant le pas 4). Deux bras : `control` sans composante instrumentale, et `instrumental` avec. Toutes les vies naissent avec Stage6 `progressive_subgoals=True`, `progressive_evaluation_prefix=True`, profondeur 3, H_eff=3, P-15=0.75. **16 vies uniques, au plus 42 transitions chacune = 672 pas physiques maximum**, réexécutées sous Python 3.11/3.12 pour comparer les deux interpréteurs mais **non** comptées deux fois. Résultat normatif du MVP : 600 pas effectivement appliqués au moins pour qu'une campagne étaye une hypothèse comportementale; déclarer explicitement sous-couverture en cas de décès/arrêt/suspension avant 600.

Rapporter les traces immuables `stage11_intrinsic_evaluation`, `stage8_option_evaluation`, `competition_cycle` et les commandes réellement appliquées, et dans un census externe :
- nouveaux signaux d'intérêt instrumental pré-décision, liens exacts option-but-frontière et rangs de candidats ;
- commandes sélectionnées sous `active_goal` et `cible_exploration`, nouvelles cellules physiquement visitées, gains alimentaires vérifiés, résultats d'objectif ;
- paires Stage12 admises/appliquées/expirées, `self/world/undetermined` à partir de l'expérience, taux d'abstention et fausses attributions extérieures lorsque le dénominateur est légitime ;
- charges UC acceptées/refusées, sommeil, taux de vie/pas, séquences A2, WAL, identité multi-vies, ségrégation Oracle et état mortel ;
- différences d'empreintes Python 3.11/3.12 (défaut numérique TD Stage8 connu, aucune promesse de SHA binaires identiques).

## Tests de falsification

Les options sans but actif, sans ancien plan du propriétaire, ou avec début de plan différent d'une frontière réellement offerte **ne doivent jamais** recevoir l'intérêt instrumental. Un simple but existant sans plan de progression, une simulation absente, un préfixe non positif, une exploration vers l'eau sous un but alimentaire non fondé ou un motif forgé n'autorisent aucun intérêt. Tester la normalisation et l'origine des signaux P-48, la non-duplication, la priorité au plan final dans Stage6, la fermeture après le premier geste (pas d'exécution du reste du préfixe), la protection d'obstacles, la conservation intégrale et l'absence de changement du témoin.

**Décision scientifique :** une option `active_goal` gagnante n'est une preuve de poursuite autonome qu'en présence d'un commandement appliqué et d'un progrès vécu correspondant, pas de la seule evidence `crossed`. Une exploration intrinsèque qui réalise incidemment un progrès ne doit jamais recevoir un motif de but rétrospectif. Si la variante réduit excessivement les nouvelles visites, produit des attributions fausses, crée une sélection inappropriée ou ne franchit pas 600 pas audités, elle n'est pas recommandée.

Aucune fusion/fermeture de PR/issue ni réception Stage12 sans présentation du rapport à l'opérateur. Le document normatif v1.3.1 reste intact pendant l'expérience, sauf nécessité démontrée d'une évolution normative explicitement motivée.
