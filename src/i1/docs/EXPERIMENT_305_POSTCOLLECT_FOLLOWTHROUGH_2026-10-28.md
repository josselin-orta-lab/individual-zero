# #305 — Continuation naturelle post-recollecte Oasis B (pas 19–24)

**Préenregistré le 28 octobre 2026, avant génération d'une nouvelle sortie**, branche issue de `main` `4ccc06319031770b52f2647f2b7a84c4ff26c9e0`. Recherche distincte du sondage 18 pas sur quatre identités de la PR #603. Une seule réexécution prospective de la naissance déterministe préexistante `oasis/b`, paramètres M11 v4 et identité `i1:304:heldout:oasis:b`, sans bras d'ablation. Elle n'est **pas** un nouvel individu statistiquement indépendant ; les pas 1–18 servent à restaurer le même parcours naturel, jamais à sélectionner un résultat favorable.

## Motif concret et prédiction contestable

La vie témoin intégrée (#597, #602) a réellement `manger berry_a` au pas 11, puis `dormir` des pas 12 à 17, et `collecter berry_a` au pas 18. Les snapshots M11 témoignent d'un inventaire vide des pas 12–17, puis d'une baie disponible **après** le pas 18. Le TD possède, en fin de vie observée, des signatures mises à jour pour `collecter` et `manger`; cette mise à jour ne garantit **ni** qu'un Q soit positif **ni** que ces deux actions soient physiquement et cognitivement offertes ensemble.

**Question** : pendant les pas 19–24, I1 fait-il naturellement face à `collecter` et `manger` (ou à deux autres options pertinents) alors qu'au moins un des candidats possède un Q `learned` effectivement consulté ? Observe-t-on ensuite une proposition évaluée, une option franchissant Competition, une admission et une commande physique utile ? L'existence d'une baie après le pas 18 ne force ni l'objectif `eat`, ni une offre `manger`, ni une action.

## Protocole

- Réexécuter la **naissance canonique** `oasis/b` dans un **nouveau** SQLite M11, sans importer sa mémoire d'un ancien WAL, avec exactement les paramètres `_birth_parameters(load_preset("oasis"))`, `diagnostic_sample_cost_uc=1`, `module_occupancy_cost_uc=1`, `noise_sigma=0`, physique v4. **24 pas maximum**, arrêt définitif sur décès. Aucun `run_step` supplémentaire après décès; pas de restauration ou rollback.
- Préfixe de provenance : le passé naturel reproduit doit contenir `manger` au pas 11, `dormir` aux pas 12–17, et `collecter berry_a` au pas 18 avec inventaire `berry_a=1` après action. Sinon échec de provenance, **pas** résultat scientifique.
- Pendant les vrais appels de `ExperimentalI1Stage12Runtime._consider_uncertain_affordance`, observer `LinearTDValues.learned_value` **en appelant la méthode d'origine une seule fois** avec les mêmes arguments, sans altérer sa valeur de retour. Ne garder que l'instance propriétaire `owner.q_active`. Cela reste une mesure du harnais, non un événement M11 et non une mémoire d'I1.
- À la fin, auditer à froid SQLite M11 : génération, tête/hash, chaîne d'événements, absence d'intention pendante. Faire correspondre strictement **toutes** les observations in-process aux `i1_unknown_affordance_proposed` authentifiés : pas, cycle, `option_ref`, nombre/ordre/signatures, Q et statut du gagnant. Rejeter orphelins, doublons, valeurs impossibles. Lire directement dans les événements M11 les actions admises/appliquées, les traces Stage8/Competition, Q publié, débits UC, variations du corps et inventaire.
- Fenêtre de l'hypothèse **fixée aux pas 19–24**, sans relance après un négatif. Publier aussi les événements 1–18 pour vérification de préfixe, mais ne pas les réinterpréter comme une nouvelle confirmation indépendante.

## Résultats admissibles, préenregistrés

1. `NO_POSTCOLLECT_UPSTREAM_PROPOSAL` : aucune proposition amont naturelle après le pas 18, même si un aliment est physiquement présent.
2. `ONLY_SINGLE_CANDIDATE` : propositions mais jamais deux admissibles simultanés.
3. `MULTICANDIDATE_ALL_Q_UNLEARNED` : concurrence mais lectures Q `unlearned` pour tous.
4. `MULTICANDIDATE_WITH_LEARNED_Q` : concurrence avec au moins un vrai Q `learned` dans cette fenêtre. **Ceci n'est pas la preuve d'un changement de choix causé par Q**.
5. `DIED_BEFORE_WINDOW_END` est une propriété de statut, **pas** un succès ou un motif pour recommencer. La situation réelle de décès et le nombre de pas restent reportés séparément.

En cas de (4), documenter si le Q gagnant diffère effectivement du Q des perdants et si l'ordre déterministe sans Q aurait pu différer, *sans rejouer d'ablation* dans cette tranche. Une expérience causale avec intervention prénaissance distincte ne serait justifiée qu'après exposition démontrée. **Le crédit instrumental différé `collecter → manger`, l'effet causal du classement, le bénéfice physiologique global, la survie et le GO adaptatif restent `NOT_ESTABLISHED`.**

Garde-fous : aucune action injectée, aucune priorité `manger`, aucun accès au monde caché ou aux effets de `berry_a`, aucune modification de I0/I1/TD/Stage8/Competition/Action Control, aucune UC gratuite, aucun seuil ajusté. Tests exact-head 3.11/3.12 structure/naturel avant fusion; mêmes vies déterministes sous deux Python, pas deux individus.
