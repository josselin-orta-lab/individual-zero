# #305 | Observation prospective des vraies lectures Q du classement amont, Oasis B

**Preregistration du 28 octobre 2026**, à partir du `main` vérifié `b0489c40981471c8cea0e0625898f030fdc7b532`, **avant tout nouveau résultat sur les Q des candidats perdants**. Le témoin source est le test M11 de la PR #598 enrichi dans #600 : `tests/i1/test_i1_natural_selective_collect_q_305.py`. Il fait déjà naître deux vies mortelles, appariées, de 18 pas dans `oasis/b`, chacune avec son SQLite M11. Le seul contre-factuel préexistant supprime la preuve du Q(`collecter`) au Stage8 du pas 18; **il ne supprime ni le tri Q amont ni les lectures propriétaire de Planning**.

## Constats à départager

La PR #600 a confirmé **17** propositions `i1_unknown_affordance_proposed` par bras, dont **3** avec `candidate_count=2` au **pas 11, cycles 1/2/3**, candidats `collecter` et `manger`. Le gagnant `manger` était `unlearned` dans les trois cycles ; cela **ne renseigne pas** le Q du candidat `collecter` écarté. Aux pas 12 et 18, `collecter` a un Q appris positif, mais reste candidat unique. La question est : quelles consultations Q effectivement effectuées par Planning correspondent à chaque candidat de ces trois classements ?

Ne pas inférer que le Q perdant est neutre, appris, positif ou négatif sur la seule base du gagnant.

## Instrumentation et provenance autorisées

Ajout **uniquement dans le test opérateur** d'un observateur enveloppant la méthode moteur `ExperimentalI1Stage12Runtime._consider_uncertain_affordance`. Durant son appel **ordinaire**, un wrapper temporaire de `LinearTDValues.learned_value` invoque la méthode d'origine **exactement une fois avec les mêmes arguments**, observe l'objet renvoyé puis le retourne **inchangé**. Il n'appelle jamais de nouveau la fonction après coup. Restreindre le relevé aux lectures de `self.q_active` réellement déclenchées pendant ce classement. Enregistrer signature, statut, valeur, evidence, update_count et ordre des lectures, avec pas/cycle et référence de l'option retenue. Aucun aperçu du monde caché, aucune mémoire injectée, aucun état propriétaire modifié, aucune création de commande, aucune facturation UC supplémentaire, aucune altération TD ou Competition.

Lire les événements M11 **après audit SQLite froid et chaîne du journal**. Pour chaque proposition authentifiée, joindre **une** observation du wrapper au même `(pas, cycle, option_ref)`, exiger que le nombre et l'ordre des primitives Q correspondent exactement à `candidate_count` et `candidate_primitives`, que le gagnant et son Q reproduisent les champs du journal; rejeter lectures orphelines, doublons et écarts. Les consultations perdantes sont une **observation in-process du harnais**, non un reçu propriétaire lui-même inscrit dans M11. Le gagnant, son nombre de candidats et la proposition sont authentifiés dans M11. Ne jamais présenter le relevé externe comme une mémoire vécue supplémentaire.

Préserver les 18 pas historiques, les deux branches, leurs états préaction, leurs UC, leurs commandes appliquées, les identités de naissance, la configuration physique v4, les hashes M11 et le résultat de l'ablation Stage8 au pas 18. Ne pas ajouter de nouvelles vies ni rejouer une source ancienne par rollback. Python 3.11 et 3.12 réexécutent **un même scénario déterministe**, sans constituer deux cohortes indépendantes.

## Verdicts préenregistrés

Pour les fenêtres multi-candidats uniquement :
- `NOT_EXPOSED` si aucune proposition admissible à plusieurs candidats.
- `MULTI_CANDIDATE_BUT_ALL_Q_UNLEARNED` si toutes les lectures de chaque candidat de ces classements sont `unlearned`. Le tri n'est pas fondé sur des valeurs personnelles apprises dans ces contextes; la rotation peut départager les égalités.
- `MULTI_CANDIDATE_WITH_LEARNED_Q` si au moins un candidat, gagnant **ou perdant**, reçoit un Q `learned`. Cela expose une concurrence avec apprentissage, **pas** la nécessité causale de la lecture pour le choix.
- `MISMATCH` ou échec technique si les lectures observées ne se recollent pas aux événements M11, au nombre de candidats ou à la valeur Q du gagnant. Aucune interprétation scientifique admise après un tel échec.

Si `MULTI_CANDIDATE_WITH_LEARNED_Q`, déterminer seulement ensuite si une ablation préenregistrée et **sélective du tri amont** pourrait départager un ordre personnel appris contre la rotation, à monde, coûts, état et action libre comparables. Si `MULTI_CANDIDATE_BUT_ALL_Q_UNLEARNED`, **ne pas** lancer une telle ablation sur ces trois cycles du pas 11; rechercher une exposition post-apprentissage naturelle, sans manipuler action ou seuil. 

Dans tous les cas, effet causal du **tri amont**, crédit différé `collecter→manger`, bénéfice alimentaire après recollecte, robustesse hors-carte, survie et GO adaptatif restent `NOT_ESTABLISHED`. Tout changement de Q propriétaire, de moteur I1/I0, de physiologie, de budget ou de politique est expressément hors portée de cette PR. L'issue #305 reste ouverte jusqu'à une preuve instrumentale supplémentaire.
