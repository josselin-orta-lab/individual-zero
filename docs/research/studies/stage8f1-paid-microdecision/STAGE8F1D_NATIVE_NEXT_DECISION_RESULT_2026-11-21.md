# Stage8-F1D · mémoire payée et décision native ultérieure

**Verdict primaire : `NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE` (21 novembre 2026).** C'est un résultat de développement **négatif sur une situation synthétique fixée avant l'expérience**, pas une preuve d'absence générale d'utilité de la mémoire. L'expérience F1C a bien été apprise et payée, mais sa rétention **n'a pas changé la commande motrice suivante dans la condition testée**.

## Sources préexposées et conservation

- [Plan F1D fixé avant la première preuve](STAGE8F1D_NEXT_DECISION_PREEXPOSURE_2026-11-21.md) : critère primaire `(action,param)` différent ; différence de scores ou d'options internes non suffisante. Source projet `6c4d433110f9960bd96b4b5716c214e0465f9214`, [PR #1487](https://github.com/josselin-orta-lab/individual-zero/pull/1487), code examiné `32b4f76cab919b26b4ffd341f710abb6c93769d6`.
- Original F1C [#44837981694](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837981694), artifact #14679910820, fichier `F1C_PAID_NATIVE_ORIGINAL.json` **125 436 octets**, SHA256 `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d`. L'ancien audit F1C `754a4c06eeae546f1fe8900375323752056c1b660e1af89d6b4688419a8e1588` est immuable. Avant tout pas F1D : l'artefact a été téléchargé sous **son nom exact**, haché puis réduit à froid.
- [Workflow F1D corrigé #44889127749](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44889127749) : **2/2 jobs PASS**, 14/14 falsificateurs dédiés ; deux processus Python 3.11 ont reproduit **exactement les mêmes octets**. Auditeur froid Python 3.12, stdlib seule et **sans import de `Mind` ou `World`**, a réétabli la physique native, les deux factures de cognition et les états de frontière à partir du JSON original.
- Artefact #**14700709161** : `F1D_NEXT_DECISION_ORIGINAL.json` et `F1D_NEXT_DECISION_REPRODUCED.json` **70 198 octets chacun**, SHA256 identique `fc2cbdb598be1d5de5491c2615c0d6dafffb7703e0887d672d2891fffb08467e`. Il conserve aussi la copie exacte du JSON F1C.
- Artefact auditeur #**14701610804** : `F1D_INDEPENDENT_COLD_AUDIT.json` **1 204 octets**, SHA256 `0e2f215ce0b8e1ab53de05c9ccedb1a6a133c826c3294f0eb8e64cea9839d5b8`.
- La première CI [#44889036183](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44889036183) reste **FAIL** : le contre-auditeur a cherché le fichier F1C au mauvais niveau du ZIP transféré, après la production réussie des reçus. Seule la référence de chemin a été corrigée ; les résultats moteurs ne sont pas retouchés. Aucun échec n'est effacé ou requalifié en preuve positive.

## Résultat vérifié au pas 2

Les deux bras commencent après la même expérience F1C `dormir`, sur le **même monde natif synthétique** et exactement le **même corps** `[2.9096, 74.63, 59.6, 90.2, 98.776]`. Ils ont prépayé l'apprentissage F1C `CognitiveWork(cycles=2,simulated_steps=32,memory_items=3,replays=1)`, soit **0,1096 énergie + 0,174 vigilance** chacun. Le seul écart d'état mental au début de la décision suivante porte sur les champs `effects`, `values` et `buffer`. RNG, perceptions, cartes, gènes et lois physiques restent appariés.

| Champ mesuré | F1C appris puis **conservé** | F1C appris puis **écarté** |
|---|---|---|
| Nombre d'observations personnelles de `dormir` | 2 | 1 synthétique initiale |
| Prédiction personnelle d'énergie `dormir` | +2,9288 | +3,0000 |
| Option gagnante | `explorer:1,0` | `explorer:1,0` |
| Commande motrice ultérieure | `se_deplacer`, Est | `se_deplacer`, Est |
| Calcul cognitif réel | 4 cycles, 72 pas simulés, 33 items mémoire | 4 cycles, 72 pas simulés, 32 items mémoire |
| Débit décision énergie natif | 0,2306 | 0,2304 |
| Débit décision vigilance natif | 0,344 | 0,344 |
| Énergie après le second `World.step` | 0,6790 | 0,6792 |

Les scores sont effectivement différents, par exemple la première option gagnante `explorer:1,0` reçoit **−0,652133** après conservation, contre **−0,647513** sans conservation. **C'est une différence computationnelle secondaire, pas un changement de décision motrice.** Le travail de décision suivant n'est pas exactement équivalent en coût : la conservation du souvenir ajoute un item, coûtant **0,0002 énergie**. Cette différence est un médiateur potentiel de rétention, et ne doit jamais être masquée ni compensée par une action ou une pensée « gratuite ».

## Portée et suites autorisées

Le préenregistrement concluait à une **preuve d'effet sur l'action** uniquement si `(action,param)` divergeait. Les deux commandes sont identiques : **échec du critère d'influence motrice dans la seule condition testée**. Le test démontre en revanche la propagation des effets observés, valeurs apprises et souvenirs jusqu'à un deuxième `Mind.decide` avec facturation native, à coût variable explicitement mesuré. Aucune supériorité de choix, adaptabilité ou persistance n'en résulte.

Un éventuel essai sur d'autres situations écologiques doit être **nouveau, prospectif, avec ensemble et estimand déclarés avant exposition**, et non un changement posthoc du verdict F1D. Il devra distinguer coût de stockage de la mémoire et contenu informationnel, et vérifier les actions choisies par l'individu sans forcer de `dormir`, de déplacement ou d'inaction.

Zéro `run_life`, aucune naissance, aucune cohorte scientifique, aucun `evidence_head` de vie entière, aucune mémoire historique G2 reconstruite ni équivalence historique. Moteur I1 reste actif, i3 non promu, F1 non admis en vie native. **Stage8-E2 demeure négatif `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`.** L'artefact GitHub Actions expire après **90 jours** ; le [manifeste F1D](STAGE8F1D_NATIVE_NEXT_DECISION_PROVENANCE_MANIFEST_2026-11-21.json) ne remplace pas les octets originaux à conserver durablement.
