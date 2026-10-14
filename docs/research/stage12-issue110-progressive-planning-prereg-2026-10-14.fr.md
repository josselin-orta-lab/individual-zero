# Stage 6 / Stage 12 #110 : préenregistrement de la planification progressive opt-in

Date : 14 octobre 2026. Approbation opérateur : étudier puis implémenter la planification progressive, en adaptant le MVP uniquement si la nécessité normative est démontrée. Document figé **avant code progressif**. Respect strict de `mvp-specification-v1.3.1.md` et des sections héritées de v1.2.1 sur la recherche bornée, l'absence de preuve d'impossibilité hors horizon et le veto Action Control.

## Hypothèse et comparateur

Lorsqu'un objectif `eat` demeure non satisfait après une recherche Stage6 complète à profondeur **3**, une trajectoire simulée par Equipment dans la même recherche peut produire un **progrès corporel observable** (augmentation de nourriture sans atteindre le setpoint) ou une **capacité alimentaire intermédiaire** (nouvelle baie effectivement prédite dans l'inventaire). Un plan progressif ne devient admissible que si au moins l'un de ces indices est prédit, sans état caché ni Oracle. Il est seulement une proposition **à une commande**, au motif du but actif conservé, avec `success_condition=step_completed`, distinct d'un succès final d'objectif. L'Action Control juge toujours l'admissibilité, puis la capture du pas suivant peut faire réviser l'action. Ne jamais qualifier une projection partielle de `plan_found` pour le but absolu.

Activer la variante uniquement par `Stage6PlanningConfig.progressive_subgoals=True` avec une nouvelle version de configuration, sans modification des fixtures Stage6 de référence. Quand le drapeau est faux, **même recherche et même journal** qu'avant. Le nombre maximal d'expansions/simulations ne doit pas augmenter du fait de l'option progressive : exploiter uniquement les noeuds effectivement examinés pendant la recherche exhaustive bornée existante. Ne pas charger de recherche cachée, modifier `H_eff`, l'UC, les seuils de Competition ou le sommeil.

## Expérimentation avant réception

Comparer 4 conditions (restored libre, restored A2, sustained libre, sustained A2) sous la **même profondeur 3**, avec et sans le drapeau progressif, dans des vies indépendantes de 36 pas au maximum. **8 vies uniques, 288 pas maximum**, réplication Python 3.11 / 3.12 pour la reproductibilité des métriques (les journaux SHA binaires peuvent différer en raison des ULP Stage8 déjà connues). La situation A2 reste fixe, obstacle au pas 2 après admission, retrait au pas 4, jamais choisi en lisant les décisions. Aucun action forcing. La règle `window=12`, `bias_min_outcomes_each=2`, `threshold=0.75` reste inchangée.

Mesurer les propositions `stage6_planning_result`, les attestations `active_goal`, engagements Stage12 `self/world/unknown`, les couples admis / appliqués / expirés et la couverture effective 2+2 **dans une même vie**, les coûts UC réellement facturés, durées exogènes et l'existence ou non de `stage6_progress_segment_closed` après un pas. Auditer indépendamment les journaux, WAL, état physique A2, identité, absence de dédoublonnage, absence de fuite des vérités causales. Toute erreur d'audit ou crash produit FAIL et son journal doit rester disponible.

Tests techniques requis : (1) drapeau off équivalence exacte, (2) but atteignable d'abord : priorité au plan complet, (3) but inaccessible à l'horizon mais progrès observé : segment d'une commande vers le but sans en annoncer le succès, (4) aucune amélioration prédite : abstention, (5) modèle incomplet : ne pas inventer des transitions, (6) segment exécuté : invalidation de l'option périmée avant nouvelle recherche, (7) obstacle connu : veto intact, (8) effets après sommeil et reprise M11 selon garanties existantes.

## Contrat cognitif envisagé

Le plan progressif ne satisfait jamais le but par sa simple existence, n'altère ni `GoalManager.active_goal`, ni un résultat de la Metacognition, ni un jugement d'agence, ni l'Oracle. `step_completed` qualifie exclusivement le segment moteur. Son premier geste est une option normale avec `motive_ref.type=active_goal` si et seulement si la recherche a trouvé une trajectoire partielle effectivement utile à la variable du but ; ce motif est fixé **avant** l'admission, jamais requalifié après succès.

Les principes hérités v1.2.1 §8.11 autorisent des plans bornés dirigés vers un but et imposent de ne pas déduire l'impossibilité à partir d'un échec sous horizon. Une **clarification normative additive** (sans modifier rétroactivement v1.3.1) doit seulement être proposée si le nouveau statut de plan partiel réclame un contrat supplémentaire. Toute modification de norme doit être explicite et conserver la possibilité de validation de l'opérateur.

Critère de décision : la comparaison doit montrer si `active_goal` est réellement restauré dans `sustained` sans faux succès, quel coût, quelles fausses attributions et si la calibration du détecteur devient enfin observable. **Si 2+2 reste absent, déclarer calibration NON ÉVALUABLE**, même si le mécanisme progressif fonctionne.
