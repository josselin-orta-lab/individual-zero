# Issue #110 / Stage 6 : préenregistrement du contraste de profondeur 3, 4, 5, 6

Date : 2026-10-14. Validation opérateur : comparaison de profondeurs 3/4/5/6 et étude d'une planification progressive. Ce texte est committé **avant** toute variante de profondeur et tout nouveau run. Campagne exploratoire et non réception du Stage12.

## Source normative et frontière

`docs/architecture/reference/en/mvp-specification-v1.3.1.md` (conserve 1.2.1 §§8.11 et 12.4). L'horizon Stage6 de **3** était défini par `scripts/run_stage12_issue110_first_planning_state.py` ; la fixture Stage6 de `main` est à **2**. L'architecture exige recherche bornée, `planning.max_depth <= simulator.h_max`, charges UC, horizon `H_eff` égal entre candidats, jamais une valeur normative universelle 3. Le changement expérimental ne touche ni Stage6Planner, ni la politique de compétition ni le journal causal.

## Contrastes figés

Facteur profondeur `planning.max_depth` = **3, 4, 5, 6**. `simulator.h_max` est relevé seulement pour rendre cette profondeur admissible. **Le budget d'évaluation d'option `H_eff=3` et `R_eff`, les coûts UC, le seuil Stage12, l'Equipment pré-naissance, le monde, les actions et la sécurité restent identiques à profondeur différente.** Versionner les configurations si valeur différente de trois.

Facteurs monde :
- `restored` : corps nourriture 35, gain par baie 30, décroissance 0, baies 12, nourriture (3,1), plan initial atteignable dans l'horizon après découverte.
- `sustained` : corps nourriture 24, gain par baie 6, décroissance 0.7, baies 12, même emplacement. Contrôle « faible effet alimentaire » où atteindre directement le setpoint pourrait rester introuvable même à profondeur 6.
- Chaque monde a **libre** et **A2** (obstacle externe fixé à t2 `after_admission`, retrait t4 `before_step`, sans adaptation aux décisions).

**16 vies autonomes indépendantes** (= 4 profondeurs × 2 mondes × 2 contraintes), jusqu'à **12 transitions physiques** par vie, soit au plus **192 transitions uniques**. Répéter sous Python 3.11 et 3.12 sur les **mêmes identités de naissance** pour contrôle de versions ; ces répétitions ne sont pas 32 vies. Les cas incomplets, décédés, hors budget ou en erreur sont retenus comme négatifs/censurés et publiés. Un job CI par `(python, profondeur)`, 4 vies par job, délai de 15 min, aucun pilotage des commandes d'I0.

## Mesures

- Journal JSONL canonique, WAL, empreintes et audit durabilité pour chaque vie ; même journal interne I0, aucune injection de vérité Oracle.
- Reçus par pas `stage6_planning_result` (proposition non nulle / absente), enregistrement d'option, action sélectionnée réellement `active_goal`, premières actions liées au but, engagements Stage12, résultats `self/world/unknown`, paires admises/appliquées, échéances de sommeil, diagnostics `attribution_bias`.
- Coût d'exécution mesuré **de l'extérieur** par `time.perf_counter()`, sans lecture par I0, par vie et par pas ; charge UC réelle des reçus `compute_charge` (approuvée/refusée). Le nombre de noeuds explorés est indisponible dans le reçu public du Stage6 ; **ne pas l'inventer**.
- Audits indépendant `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_first_person_agency`, `audit_stage12_attribution_pairs`, et audit A2 des interventions effectivement inscrites, avec erreur fail-closed.
- Comparer couverture et coût avec même profil et même condition A2 ; **aucune agrégation de paires entre vies dans le détecteur**. Reproductibilité binaire inter-Python non présumée : la divergence en ULP de Stage8 précédemment prouvée reste un contrôle indépendant.

## Falsification et décision

Une profondeur plus longue n'est pas un succès si elle produit moins de but réellement poursuivi, augmente fortement le coût ou compromet UC, mortalité, veto ou audit. Le calcul du biais reste indisponible sans deux `success` et deux `failure` vérifiés dans une même fenêtre de 12 diagnostics. Une absence de plan sous horizon fini **n'est jamais** une preuve d'impossibilité physique.

La planification progressive à horizon borné est un **candidat architectural à étudier après les résultats** : maintien du but, première commande orientée vers un sous-objectif perceptible, réévaluation payée sans prédire la causalité cachée. Ne pas ajouter immédiatement de priorité fictive, heuristique Oracle, exploration contournant Stage6 ou nouvel owner. Si le contrat normatif implique une évolution, demander l'arbitrage de l'opérateur avant de modifier la spécification.

**Critère de clôture de cette campagne :** 16 rapports de vie (ou rapport de fail explicite), comparaison honnête des 4 profondeurs et recommandation technique, pas réception automatique de Stage12 ni clôture #110.
