# Stage12 issue #110, A2.11b : corpus pré-natal enrichi, résultat physique négatif

**14 octobre 2026. Verdict Stage12 global PARTIAL.** Plan préenregistré **avant le code** au SHA `599d0dbb1b1a83eadcc7ccb34daae54d7763bf3e`. Source effectivement exécutée : `2a9b5826444d79a865876440316a0774d73350fd`. [GitHub Actions #38609675365](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38609675365) **SUCCESS sur Python 3.11 et Python 3.12**, avec exactement les mêmes quatre comparaisons appariées. **8 vies indépendantes et mortelles ×42 pas physiques, 336 transitions distinctes**; les deux versions Python ne sont pas des séries de seeds aléatoires.

## Intervention contrôlée, uniquement prénatale

- **OFF** : Equipment exact-table de référence avec **4 transitions physiquement appliquées** sur WorldBody externe avant naissance : mouvement nord, mouvement est, collecte et ingestion.
- **ON** : conserve intégralement ces quatre exemples et ajoute **deux autres mondes d'entraînement pré-nataux physiquement distincts**. Le premier exécute attendre, nord, est, collecter, manger. Le second exécute nord, une tentative de déplacement est réellement bloquée par une intervention externe sur l'obstacle, puis attendre, déplacement libéré est, collecter, manger. Le corpus élargi possède un SHA/une version Equipment distincts. Les mêmes entrées historiques gardent exactement les mêmes transitions observées.
- **Garde-fou** : `FrozenTableEquipment` est toujours le modèle **strictement exact** : une clé `SimulationState×PrimitiveCommand` absente déclenche `LookupError`. Le test adversarial confirme qu'une commande de fabrication d'outil inconnue reste indisponible. Les événements de corpus proviennent uniquement de `WorldBody.apply` sur des mondes neufs et externes **avant** les vies testées; ni Oracle, ni journal causal de la future vie, ni jugement subjectif ne sert à entraîner un effet.
- Paramètres d'agent conservés : `P15=0.75`, `extrinsic_gain=1.6`, `progressive_subgoals`, revalidation des plans après capture, Competition, UC, Action Control, frontières Stage9/12, v1.3.1 normative inchangés.

## Matrice et observations réellement vécues

Quatre configurations indépendantes, chacune OFF/ON : `restored/sustained` × `sans obstacle/A2 t2 bloqué et t4 libéré`. Les huit vies ont **toutes** appliqué 42 transitions physiques, sans erreur de WAL, journaux, audit Goal Progress, audit GA/attribution, P-48 et causal A2; aucun décès. Les deux Python produisent les mêmes résultats agrégés :

| Profil et environnement | Nombre de recherches `incomplete_model` OFF / ON | Ingestions `effects.ate` OFF / ON | Gains alimentaires corporels attestés OFF / ON | Sites physiques distincts OFF / ON |
| --- | --- | --- | --- | --- |
| restored, libre | 0 / 0 | 1 / 1 | 1 / 1 | 31 / 31 |
| restored, A2 | 8 / 8 | 1 / 1 | 1 / 1 | 30 / 30 |
| sustained, libre | 33 / 33 | 1 / 1 | 1 / 1 | 31 / 31 |
| **sustained, A2** | **36 / 36** | **0 / 0** | **0 / 0** | **32 / 32** |

La présence réelle de nouvelles transitions physiques dans l'Equipment **n'a entraîné aucune diminution des recherches incomplètes, ni aucun changement d'ingestion ou de sites explorés dans cette cohorte**. Le critère prospectif C4 d'au moins un repas supplémentaire en `sustained/A2` est explicitement **FAIL**. L'absence de régression exploratoire reste un fait positif mais n'est pas un gain d'utilité.

## Ce qui est, et n'est pas démontré

**H1 « simple accroissement des exemples observés suffit » : réfutée sur cette matrice.** L'expérience distingue corpus d'entraînement réellement enrichi et couverture des états réellement visités. L'Equipment utilise une empreinte exacte comprenant positions, corps et voisinage. Les nouveaux exemples peuvent donc rester sur des clés trop différentes pour aider à une autre trajectoire vécue. Ce mécanisme est cohérent avec l'effet nul, mais l'expérience n'a **pas calculé les clés exactes de chaque rollout manqué**, donc cette explication détaillée n'est pas encore prouvée clé par clé.

**H_eq « couverture insuffisante de l'Equipment » : renforcée comme limitation générale, sans causalité exclusive établie.** Les 36 `incomplete_model` de `sustained/A2` persistent malgré l'augmentation des exemples. Des recherches incomplètes existent aussi dans `sustained/free`, qui mange pourtant. H_mem (échec de mémoire), H_val (compétition), H_control (veto/UC) ne sont pas séparées par cette expérience. L'audit A2.11 précédent avait trouvé zéro refus explicite de charge UC Planning dans sa cohorte; cela ne démontrait pas une absence universelle de contraintes computationnelles.

**Limites :** modèle d'apprentissage figé, expansion d'un corpus restreint et dérivée du monde d'entraînement, aucun nouvel algorithme de généralisation, pas de tests nocifs ou à effet retardé, aucune variété random indépendante, pas de 600 pas sous cette intervention. On ne peut pas attribuer une responsabilité causale subjective aux augmentations de `food` sur le seul résultat physique.

## Critères et décision

| Critère | Verdict |
|---|---|
| C1 agence subjective | PARTIAL, aucune nouvelle calibration convaincante |
| C2 distinction causale | PARTIAL, A2 externe et effets observés mais intervention sans conséquence comportementale |
| C3 diversité | PASS borné : 100 % de rétention OFF/ON dans cette cohorte |
| C4 alimentation | PARTIAL historique, **FAIL du gain comportemental hypothétique A2.11b** |
| C5 discrimination P-48 | PARTIAL, aucune discrimination nouvelle démontrée |
| C6 stabilité prolongée | INCONCLUSIVE pour le nouveau traitement (42 pas/vie) |
| C7 reproductibilité | PARTIAL : deux Python identiques sur métriques, sans seeds indépendants |
| C8 conformité | PASS borné : corpus prénatal, abstention sur les inconnus, WAL et audits |

**GLOBAL Stage12 PARTIAL. Ne pas clôturer #110 ni déclarer la réception scientifique opérateur.** Ce résultat négatif est conservé.

## Étape suivante avant toute correction générale

Préenregistrer un audit de correspondance **exacte clé par clé** : ne publier les hashes d'états/commandes qu'à l'observateur externe, sans rétroaction vers I0, et identifier quels champs de l'état produisent les refus. Ensuite seulement examiner une représentation de variables pertinentes, **sans supposer** qu'une faim différente implique des effets identiques, ni généraliser la sécurité ou la toxicité à partir d'exemples bénins. Une famille de prédicteurs incertains nécessiterait une justification scientifique explicite, des tests adversariaux et un contrôle du contrat v1.3.1 avant intégration.
