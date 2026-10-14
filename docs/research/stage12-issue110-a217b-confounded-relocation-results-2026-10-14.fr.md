# Stage12 issue #110 : A2.17b, erreur d'agence subjective cohérente avec une expérience perceptivement confondue

**14 octobre 2026. Verdict Stage12 global PARTIAL.** Protocole préenregistré **avant code** au commit `fa52ad4c9107208aa42319fa45f6c329f35bb699`. Base `main ecfbf96b90aa2195dec4806815f2f1cc24d28143`. Expérimentation externe sans modification de l'algorithme, du runtime I0 ni de la norme v1.3.1.

## Protocole et sources

[GitHub Actions #38633398169](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38633398169) : **SUCCESS Python 3.11 et 3.12** avec résultats identiques, 8 seeds physiques `81..88`, **24 mondes WorldBody distincts**, **24 commandes physiques volontaires**, et **8 interventions externes de relocalisation**. Chaque essai crée un `WorldBody` nouveau avec une ressource hydrique visible au voisin est. Le véritable `GoalAgencyService` se préengage sur le déplacement est vers l'eau, puis juge à t2 depuis la perception locale et la copie de sa propre commande. `effects.movement`, `scenario_forced_failure` et `set_position` restent hors de la cognition : **le banc les conserve uniquement pour identifier la cause physique**.

Trois mondes appariés pour chaque seed :
1. **Déplacement normal** : la commande `se_deplacer east` déplace réellement le corps.
2. **Échec forcé sans relocalisation** : la commande est inhibée par un événement physique externe invisible ; le corps ne bouge pas.
3. **Échec forcé suivi d'une relocalisation** : la même commande est physiquement inhibée, puis un événement externe `set_position` installe le corps à la destination prévue, avant la capture perceptive du cycle t2.

La comparaison des deux captures intégrales autorisées `PerceptualCapture`, après sérialisation déterministe, est **strictement égale 8/8** entre les conditions 1 et 3, pour la même seed, aussi bien avant l'action qu'après l'action. Les journaux individuels de laboratoire conservent la perception et ses SHA, la transition appliquée et son SHA, les effets de l'action, l'éventuelle intervention opérateur, l'engagement subjectif et le jugement.

## Résultats factuels

| Condition | Résultat physique de la commande | Intervention extérieure après la commande | Jugement `self` | `world` | `unknown` |
| --- | --- | --- | ---: | ---: | ---: |
| Déplacement normal | `movement=moved` | Aucune | **8** | 0 | 0 |
| Commande physiquement inhibée | `scenario_forced_failure=se_deplacer` ; corps immobile | Aucune | 0 | 0 | **8** |
| Commande inhibée + relocalisation opérateur | **Mouvement volontaire non effectué** | `set_position` vers la cible | **8** | 0 | 0 |

**8/8 attributions subjectives `self` de la condition confondue sont physiquement incorrectes** si l'on demande si le déplacement a été causé par l'action volontaire : le déplacement provient ici de `set_position`. Elles sont néanmoins **épistémiquement compatibles** avec une preuve interne identique à celle d'une action accomplie. L'erreur n'est visible que grâce au reçu causal externe de l'opérateur. Les huit autres `self` (déplacement normal) sont cohérents avec l'action réellement appliquée, et les huit `unknown` avec une absence d'indice perceptif distinctif.

Le premier CI [#38633308064](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38633308064) a échoué à cause d'une méthode de sérialisation `PerceptualCapture.as_dict` inexistante ; la correction `dataclasses.asdict` a uniquement affecté **l'instrumentation de comparaison**, sans modifier l'expérience physique ni les seuils. Les erreurs restent visibles et les suites Python 3.11/3.12 ont validé la correction.

## Portée scientifique

- **H1/H2/H3 : PASS dans la matrice physique preregistrée.** La comparaison prouve qu'il existe une ambiguïté entre causalité physique et attribution subjective lorsque l'état perceptible et l'intention sont identiques.
- **C1 : PARTIAL**, car une capacité d'erreur subjective vérifiable existe et le système n'est pas mécaniquement omniscient ; la révision de cette erreur à travers l'apprentissage n'a pas été démontrée.
- **C2 : PASS borné sur l'indiscernabilité**, pas sur une causalité subjective véritable. Le banc sait distinguer l'intervention externe, I0 non.
- **C3/C4/C5/C6 : INCONCLUSIVE** pour diversité, alimentation autonome, P-48 et stabilité : ce sont **24 essais physiques externes**, pas 24 vies autonomes, et aucune fenêtre 2+2/12 n'est alimentée par eux.
- **C7 : PASS borné**, mêmes résultats sur deux Python, 8 seeds spatiales déclarées ; deux Python ne sont pas 16 seeds scientifiques.
- **C8 : PASS borné**, aucune donnée Oracle/Bench ou vérité du scénario externe n'entre dans le juge d'I0 ; aucune modification de l'Equipment, UC, mémoire, Action Control, Safety, WAL, mortalité ou norme v1.3.1.

**VERDICT GLOBAL Stage12 : PARTIAL. Issue #110 OPEN. Aucune réception opérateur.**

## Décision

Ne pas ajouter un détecteur ad hoc de `set_position` ou de `scenario_forced_failure` à I0 : cela violerait la frontière épistémique et rendrait l'attribution artificiellement omnisciente. Ne pas reclassifier chaque déplacement conforme en `unknown` à partir de l'existence d'un cas confondu ; il faut mesurer le coût de la prudence et les indices réellement disponibles. L'objectif de la phase cognitive ultérieure A2.18 est de tester **la révision d'une attribution initialement plausible mais fausse** à partir d'expériences successives, et de maintenir la différenciation alimentaire et la sécurité sans injecter la cause véritable du banc. Une campagne longue sur vies autonomes, plusieurs seeds, nourriture nocive/retardée, diversité exploratoire et calibrabilité reste nécessaire avant tout PASS global.
