# Individual Zero : GA-08 Option A, rapport expérimental et sûreté du 14 octobre 2026

**Statut : validation logicielle ciblée et observation exploratoire positive de `self` spatial ; aucune observation autonome `world`, aucun biais diagnostiqué, aucune réception Stage 12.** Cette étude concerne la PR brouillon #154 construite sur la PR technique #147 et la cible normative v1.3.2 #148 (non fusionnées) ; la spécification historique v1.3.1 reste inchangée. Issue principale #110. Stage 9 scientifique NO-GO maintenu.

## Protocole 1 : présence d'une cible libre / bloquée / absente

Préenregistrement d'origine : `docs/research/stage12-issue110-ga08-spatial-prereg-2026-10-14.fr.md`. Code exact [GitHub Actions #38481590904](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38481590904) : `ad591e5d67190a3a3d51bda67cf1ff75b65d1532`, **SUCCESS Python 3.11 et 3.12**. Six vies nouvelles × 50 pas = **300 vraies transitions** par interpréteur, toutes auditées. **0** sous-critère spatial préenregistré, **0** jugement `self/world` spatial, **0** couple admis/appliqué, **258 diagnostics à `None`** par interpréteur. Aucune action n'est imposée par le laboratoire. Résultat nul conservé. Cette campagne ne teste pas positivement le jugement `world` parce que l'individu ne choisit jamais un déplacement dirigé vers la cible bloquée. Le fait que le noyau fonctionne dans un test WorldBody direct *ne remplace pas* cette absence de décision autonome.

## Protocole 2 : retour autonome à une ressource déjà perçue

Préenregistrement distinct **avant le runner et avant l'expérience** : `docs/research/stage12-issue110-ga08-return-goal-prereg-2026-10-14.fr.md`, commit `6caebd195d5401d4fad1cbed6e26c2dbb1a87763`. Quatre vies neuves, `water/food × GA08 enabled/disabled`, 50 pas physiques chacune. La politique d'entraînement de l'Equipment est une table exacte **physiquement constituée sur un WorldBody de laboratoire différent avant la naissance**, comme les expériences #132/#151/#152. Elle ne démontre aucune acquisition autonome en vie. Aucune sélection d'action, aucun jugement ou résultat n'est injecté dans la cognition après naissance. Même seuil : `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`.

Les premières exécutions conservées ont révélé successivement :
- un faux rejet de l'auditeur qui cherchait un `position_before` **absent** du format canonique WorldBody (GH run #38482063526, 3/4 vies auditées). Correctif : utiliser la capture perceptive *avant* la commande puis vérifier `position_after` et la capture suivante. Aucune preuve favorable n'est créditée à ce run rouge ;
- un défaut du mécanisme de reconnaissance des ressources co-localisées : l'eau écrasait la nourriture même quand le but actif visait `food`. Correctif : sélectionner exclusivement le type de ressource **de l'objectif préexistant**, sans modifier le contexte expérimental, les seuils, l'Equipment, la décision ni les lois WorldBody. Tests de non-régression dédiés ;
- lors de l'ajout des tests M-11, une validation à froid initialement paramétrée pour la politique d'agence historique. Le `GoalAgencyService` de vérification est désormais préactivé à la version GA-08 **uniquement si sa configuration de naissance l'était déjà**, et sans déduire la politique du snapshot non fiable.

### Résultat sur SHA final mesuré et reproductible

[Actions #38482809874](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38482809874), **SUCCESS CPython 3.11 et 3.12**, source exacte `3824f993f32773cc19730a69b1bde3c9bad4cce3`. Les synthèses et les SHA-256 des **quatre journaux canoniques** coïncident exactement entre interpréteurs.

| Par interpréteur | Résultat |
| --- | ---: |
| Vies physiquement exécutées et intégralement auditées | 4/4 |
| Pas physiques effectivement appliqués | 200 |
| Sous-critères spatiaux préenregistrés avant transition | 2 |
| `spatial_progress_v1` succès vécus et audités | 2 |
| `spatial_progress_v1` échecs vécus | 0 |
| Jugements subjectifs spatiaux `self` | 2 |
| Jugements subjectifs spatiaux `world` | **0** |
| UC Action Control pour jugement spatial | 2 |
| Couples `(success,self)` spatiaux réellement appliqués au détecteur | **2** |
| Diagnostics de biais `None` publiés | 174 |
| Diagnostics de biais positifs ou négatifs disponibles | **0** |
| Vies non auditées ou arrêtées | 0 |

| Monde/contrôle | Plans Stage6 | Sous-critères spatiaux | Jugements `self` spatiaux | Couples diagnostiques spatiaux appliqués |
| --- | ---: | ---: | ---: | ---: |
| Eau, GA-08 activée | 2 | 1 | 1 | 1 |
| Eau, critère corporel GA-08 désactivée | 2 | 0 | 0 | 0 |
| Nourriture, GA-08 activée | 3 | 1 | 1 | 1 |
| Nourriture, critère corporel GA-08 désactivée | 3 | 0 | 0 | 0 |

SHA-256 des JSONL canoniques, chacun vérifié identique sous 3.11/3.12 :
- `water_spatial` : `c9a7267a4cfdeeff89194a3c94f29579ebd686a60bcdc9a2a9a73a1dfd2e495a`
- `water_body` : `43ff5c694a58cebf1b8200806d943884c64951979d09c43f3dce39e7691425a1`
- `food_spatial` : `6402fdf0b8471f5796658da7082dc7829f1d39041dc41d14e110eddee84507e1`
- `food_body` : `d2f4a19fcd8d35d9d70f92e1f0f541a1a497b0906a4590dad8f538f4c0b4332e`

Chaque succès spatial signifie **seulement** diminution de la distance Manhattan vers une cible effectivement perçue. L'atteinte de cette cellule ne démontre ni réalisation totale du besoin ni causalité physique personnelle indépendante.

## Architecture, audit et réserves scientifiques

- **Metacognition** possède toujours le registre canonique unique `Stage12GoalProgressLedger`, étendu de façon versionnée avec `SpatialGoalPrecommit`; **Action Control** possède seul `GoalAgencyService`. `self/world/unknown/unavailable` est évalué dans Action Control sans lire le résultat du critère, les étiquettes du comparateur P-47, l'Oracle ni les causes invisibles. Le résultat spatial est calculé séparément, toujours sur la capture autorisée et préenregistrée.
- L'UC supplémentaire GA-08 est **pré-natale, positive, déterministe et intégrée au prélèvement `stage12_diagnostic_sample` versionné** ; le jugement et la jointure conservent leurs opérations payées séparément. Aucun calcul n'est injecté gratuitement dans un audit, aucun changement de six phases ou d'unicité des échantillons.
- L'auditeur `audit_stage12_spatial_provenance` vérifie les captures initiales et suivantes, passabilité précise et cible pertinente, décision admise/réellement transmise, transition WorldBody, provenance, fenêtres, coûts et jugements. Des tests reconstruisent volontairement **une chaîne de hash cryptographiquement cohérente** après falsification de cible, direction, obstacle, identité, commande ou résultat : la vérification sémantique doit les refuser, parfois encore plus tôt via l'audit autobiographique. Cela ne prouve pas la vérité physique externe à partir d'un journal.
- **Limite de dépendance des signaux** : pour une cible directement adjacente, la réussite de réduction de distance et l'indice personnel de déplacement partagent une mesure perceptive de position. Ils sont calculés et préenregistrés par des propriétaires distincts, mais leur forte dépendance interdit de considérer `(success,self)` comme une preuve d'un biais autocentré. Les expériences ne sont **pas une calibration positive/négative du détecteur**.
- `world` ne peut être produit que si un obstacle spécifique de destination était perceptible, la commande liée au but a été réellement exécutée, et le déplacement n'a pas eu lieu ; **une prédiction non conforme, un non-gain et une position inchangée seuls ne suffisent jamais**. Aucune vie autonome actuelle ne satisfait ces conditions. Ne pas forcer de mouvement bloqué.
- Les nouvelles images M-11 sont validées sur les propriétaires existants, sans import historique. Tests : génération SQLite à froid, intention spatiale en attente puis clôturée, `os._exit` avant et après commit. Les exécutions scientifiques citées utilisent un WAL durable, distinct des tests SQLite exclusifs. Pas de restauration de vie morte et pas de preuve postmortem.
- Les deux versions Python sont des tests de reproductibilité technique de **quatre configurations**, pas huit vies indépendantes.

## Reproduction opérateur sans lecture manuelle de milliers d'événements

Depuis la branche de travail PR #154, SHA fixé avant toute reproduction :

```bash
python -m pip install -e .
python -m unittest discover -s tests -p 'test_stage12_ga08_spatial_evidence.py' -v
python -m unittest discover -s tests -p 'test_stage12_ga08_owner_runtime.py' -v
python -m unittest discover -s tests -p 'test_stage12_ga08_rehashed_semantic_audit.py' -v
python -m unittest discover -s tests -p 'test_stage12_ga08_m11_recovery.py' -v
python scripts/run_stage12_issue110_ga08_return_goal_science.py --output-dir /tmp/i0-ga08-return-operator
cat /tmp/i0-ga08-return-operator/summary.json
```

Chaque vie dispose de `canonical.jsonl`, `life.wal`, `life-result.json`. Le runner refuse un défaut d'audit indépendant et conserve les résultats nuls/techniques dans `index.json`. Les archives exactes sont disponibles sous les jobs 3.11/3.12 du run GH #38482809874. La procédure est **exploratoire**, pas une campagne de science finale du MVP.

**Verdict : GA-08 produit déjà des jugements `self` spatiaux authentiques et les transmet à temps au détecteur sur deux vies ; aucune attribution autonome `world`, aucun biais positif/négatif, aucune clôture de l'issue #110, aucune réception Stage 12, aucune fusion.** Stage 9 conserve son NO-GO.
