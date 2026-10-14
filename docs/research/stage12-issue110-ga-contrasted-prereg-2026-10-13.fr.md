# Individual Zero Stage 12, issue #110: campagne exploratoire contrastée préenregistrée

**Préenregistrement daté du 13 octobre 2026, avant toute exécution de ce nouveau protocole.**

Code-source de départ figé : PR #147, commit `a2252620db065bacd8a4072e5bfa86fdb54a0dc9`. La campagne scientifique suit la spécification candidate PR #148 (GA-01..GA-07), sans prétendre qu'elle est déjà intégrée dans `main` ; la norme publiée v1.3.1 et le Stage 9 scientifique NO-GO restent intacts.

## Questions de recherche

- **H1, acquisition vécue** : les transitions physiques autonomes créent de véritables critères de progression préenregistrés puis vérifiés avec `success/failure/unknown`. Zéro réussite ou zéro échec est un résultat valable, pas une classe à fabriquer.
- **H2, appréciation à la première personne** : Action Control peut produire `self` à partir d'une ingestion volontaire préengagée et d'une diminution *perçue* de l'inventaire, indépendamment de la hausse corporelle de nourriture. `unknown` est attendu lorsque les indices ne permettent pas de conclure. Le producteur actuel ne justifie pas `world` pour les critères corporels, et doit rester conservateur.
- **H3, jointure** : les seuls couples admissibles ont une intention réelle, une commande/transition vécue, un résultat vérifié, un jugement original indépendant, des références uniques et les débits UC acceptés. Un couple ne représente pas une causalité physique prouvée.
- **H4, diagnostic** : les sorties `self_serving_pattern`, `self_blame_pattern`, `no_detected_pattern` et `None` suivent uniquement les échantillons admissibles et seuils figés : `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`. L'absence de `world` ou d'échecs admissibles peut rendre le diagnostic indisponible.
- **H5, exactitude technique** : WAL et export complet concordent ; audits indépendants et débits UC cohérents, pas de cognition après mort, aucune autorité Oracle/Bench dans I0.
- **H6, contrôle de contexte** : observer sans imposer les actions si les contextes de ressources et de sommeil modulent naturellement les fréquences de préengagement, jugement et jointure.

## Plan fixé avant exécution

Factoriel **3 × 2 × 2 = 12 vies nouvellement instanciées** par interpréteur, sans réemploi des états :
- monde `reference`, `water_available` (source et 2 baies au départ, contexte perceptible), `path_obstructed` (obstacle aux coordonnées de référence (3,2)) ;
- eau initiale `20.0` ou `35.0` ;
- `sleep_reference` ou `awake_ablation` (fatigue_gain/night_weight/consolidation_weight mis à zéro, comme le protocole Stage12 de développement antérieur).

Exécuter jusqu'à **50 transitions physiques réellement appliquées par vie**, donc 600 transitions demandées par campagne d'un interpréteur, mais **ne compter que les transitions réalisées**. Une mort, un `safety_block`, un `technical_halt` ou un échec de propriété provoque l'arrêt sans reprise de cette identité. Ne pas poursuivre une vie pour rattraper le quota. Même plan Python 3.11 et 3.12 : **contrôle de déterminisme inter-version, pas 24 réplications statistiques indépendantes**.

Les environnements sont fournis à la naissance et les actions demeurent librement sélectionnées par I0. Ne pas imposer `manger` ou `boire`, injecter un diagnostic, ajuster les seuils, changer le coût UC ou alimenter I0 avec le journal technique ou des vérités cachées. Les règles physiques de WorldBody ne changent pas. Une classe d'action n'a aucune garantie d'apparition.

Configurations GA activées à la naissance : `subjective_goal_agency=True`, `goal_agency_cost_uc=1`, `attribution_join=True`, `attribution_join_cost_uc=1`, `diagnostic_sample_cost_uc=1`, `module_occupancy_cost_uc=1`. Détecteurs : `window=12`, `stagnation_steps=4`, `stagnation_tolerance=0.05`, `loop_repetitions=3`, `loop_max_period=2`, `entropy_min_samples=4`, `entropy_warning_fraction=0.25`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`. Politique figée : `stage12-issue110-ga-contrasted-v1`. Les seuils ne peuvent être modifiés après observation.

## Mesures et vérification indépendantes

Pour chaque vie, conserver en fichiers séparés le WAL, l'export causal canonical JSONL, l'empreinte SHA-256 du fichier, le `head_hash` de la chaîne et le nombre d'occurrences, SHA source et configuration, action primitives, statut terminal, transitions réellement appliquées, rapports d'erreur intégraux et résultats négatifs.

Auditer en lecture seule `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_first_person_agency`, `audit_stage12_attribution_pairs` et `audit_stage12_diagnostics`. Contrôler exactes mêmes ancres pour tous les auditeurs.

Publier les critères préenregistrés, vérifiés en succès/échec/inconnus, jugement `self/world/unknown/unavailable`, couples enregistrés/appliqués/manqués, coûts UC acceptés/refusés, diagnostics positifs/négatifs/`None`, nombre de pas effectifs, morts/arrêts, et vies rejetées par un audit. Un nombre observé nul doit rester explicite.

Des contrôles adversariaux sur journaux rechaînés et tests de prédiction P-47 différente avec conséquence inchangée sont exécutés comme **tests logiciels distincts**, jamais crédités comme comportements scientifiques autonomes.

## Verdicts préfixés

- **PASS logiciel exploratoire ciblé** uniquement si le test exact-source, WAL et audits indépendants concordent ; aucun résultat favorable de biais n'est requis.
- **HYPOTHÈSE EXPLORATOIRE PARTIELLEMENT SOUTENUE** si des résultats et jugements authentiques, avec au moins un couple réel admissible, sont mesurés. Une validation du *détecteur de biais* demande au contraire ses deux classes de résultats et les seuils prédéfinis réellement atteints.
- **INCONCLUSIF** si la vie est correctement auditée mais l'une des classes ou la provenance manque ; 600 pas seuls ne satisfont pas l'hypothèse du biais.
- **NO-GO logiciel** si journaux actifs falsifiés/contradictoires ou fausse attribution positive sont acceptés, ou si UC/atomicité/mortalité ne respectent pas les règles ; conserver les artefacts.
- **PAS DE VALIDATION SCIENTIFIQUE FINALE**, pas de réception opérateur, pas de changement du NO-GO Stage 9 sur ce seul protocole.

**Limites décidées d'avance :** mêmes règles déterministes et modèles sur les vies d'un interpréteur ; contexte expérimental programmé ne garantit pas des situations générales ; deux signaux de même capture ne prouvent pas deux vérités physiques indépendantes ; aucun `world` prouvé par l'actuelle politique ; configuration `awake_ablation` ne couvre pas le sommeil ; pas de M-11 `os._exit` de cette campagne. Le dossier complet de Stage12 et les essais M-11 demeurent distincts.
