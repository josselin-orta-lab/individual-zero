# Stage12 issue #110 : résultats A2.18, agence subjective séquentielle et non-identifiabilité

**14 octobre 2026.** Préenregistrement A2.18 antérieur au script : commit `a9f804b62df0067c724da9a43413235d6e926086`. Épreuve : script `scripts/run_stage12_issue110_a218.py`, SHA exécuté `a84f623279dce886d02508e676219a6922a641a6`. [GitHub Actions #38636774489](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38636774489) : **SUCCESS sur Python 3.11 et Python 3.12**, deux reproductions de la même cohorte et non 16 seeds indépendantes.

## Vérification

| Critère fixé avant instrumentation | Résultat |
|---|---|
| T1 : 48 mondes physiques séparés et 96 véritables `WorldBody.apply` | **PASS** : 48/48 et 96/96 ; 24 relocalisations extérieures au premier pas, 16 échecs silencieux au second, 16 obstacles extérieurs au second |
| T2 : 24 paires de trois captures successives strictement égales | **PASS** : comparaison de trois `PerceptualCapture` complets et SHA, même séquence de commandes ; cause physique du premier déplacement différente |
| T3 : attributions `self -> self / unknown / world` | **PASS** : 16 `self->self`, 16 `self->unknown`, 16 `self->world` ; chaque séquence compte une histoire normale et une histoire physiquement confondue |
| T4 : pas de faux crédit de révision rétrospective | **PASS pour la frontière méthodologique** : deux `assessment_ref` distincts par monde, aucun remplacement du premier reçu ; **0 révision rétrospective observée** |
| T5 : reproductibilité | **PASS borné** : Python 3.11/3.12 verts et artefacts par monde ; huit seeds spatiales 91–98 seulement |
| T6 : protection des frontières | **PASS au niveau du diff** : uniquement préenregistrement, script externe et workflow ; aucun code de cognition/runtime, physique, norme, UC, Oracle, WAL, Stage9/DC-05 ou seuil 2+2/12 modifié |

## Fait scientifique central

Les **24 premiers jugements `self` issus d'une relocalisation opérateur** sont physiquement faux en tant qu'explication causale de la première commande. Ils sont néanmoins subjectivement cohérents : leur première capture, leur deuxième capture, puis leur troisième capture sont les mêmes que pour une véritable réussite de déplacement, dans chaque paire appariée. Le banc conserve les effets de la commande `scenario_forced_failure` et la relocalisation `set_position` comme preuves physiques ; le service de première personne n'y a pas accès.

Une nouvelle expérience fournit effectivement de nouveaux indices utiles **pour la seconde commande** : succès perceptible (`self`), échec muet (`unknown`), obstacle apparu après préengagement (`world`). Elle ne révèle pas rétroactivement la cause du premier déplacement dans ces mondes appariés. La distinction « juger une nouvelle action » vs « corriger la cause passée » est donc empiriquement nécessaire.

**Interprétation négative et limites :** ce résultat ne montre pas qu'I0 a appris à réviser un jugement ancien, ni qu'une révision est impossible avec *tout* indice ultérieur concevable. Il montre que ces trois familles d'indices, avec l'histoire perceptive disponible, ne distinguent pas les deux causes passées. Aucun modèle de révision n'existe ou n'a été installé par cette PR. Les tests dirigés utilisent bien un même service `GoalAgencyService` sur deux actions, mais **0 vie cognitive autonome**, **0 pas autonome 600**, **0 paire GA-06 issue du banc**. Les nombres reflètent la matrice fixée, pas une estimation de performance dans la population des vies.

## Architecture et décision à l'opérateur

Toute proposition future devrait spécifier sans modifier encore la norme :
1. un jugement sur la **commande/action proximale** distinct de la responsabilité du **résultat de l'objectif distal** (en particulier `inventory` vs `body.food`) ;
2. un reçu de **révision d'un jugement antérieur**, référencé, non destructif, avec indice réellement disponible, coût UC, propriétaire canonique, atomicité WAL, respect du sommeil et de la mort ;
3. un état **indéterminé / abstention** lorsque deux causes demeurent identiques du point de vue de l'individu, plutôt qu'une connaissance cachée de l'événement externe ;
4. une campagne prospective ON/OFF, sécurité et vie autonome multi-seeds, avant toute promotion en politique.

La séparation proximale/distale est **proposée pour arbitrage**, pas adoptée. Aucun seuil `2+2/12` n'est modifié, aucune compétence alimentaire ou attribution distale n'est inférée, aucun PASS de Stage12 revendiqué. **GLOBAL Stage12 PARTIAL. Issue #110 OPEN. Pas de réception opérateur.**

Ce rapport documente la première exécution confirmée par [CI #38636774489](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38636774489). La CI éventuelle du commit documentaire final doit être vérifiée séparément.
