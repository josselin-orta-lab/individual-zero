# A2.29 : arbitrage du planificateur alimentaire en option B, résultats prospectifs

**15 octobre 2026.** Préenregistrement avant code `084827ba`, cohorte empilée PR #186 / A2.28 #185 / B #184. La première [CI #38693092843](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38693092843) était PASS mais réutilisait des identités de naissance `a228`, contrairement au contrat ; ne pas l'accepter comme nouvelle cohorte prospective. Correction **sans modification de politique de production** : `8ab50adc` permet un identifiant de cohorte explicite, défaut historique `a228` inchangé, et `c2e831eb` exige une naissance `i0:stage12:b:a229:`. [CI corrigée #38696158740](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38696158740) **SUCCESS Python 3.11 et 3.12** au SHA `c2e831eb3ebbd958461b2fc6dbfae1ab5253421f`. Reprise des huit vies autonomes mortelles B, quatre profils alimentaires × obstacles OFF/ON, chacune 48 vrais pas : **384 transitions**, **12 jugements B**, aucun échec d'audit, trois contrôles négatifs hors cohorte.

## Entonnoir exhaustif de la cohorte corrigée

| Catégorie descriptive exclusive par pas | Nombre |
| --- | ---: |
| `no_planner_proposal` | **247** |
| `no_attested_active_goal` | **68** |
| `reduced_sleep` | **44** |
| `goal_selected_B` | **12** |
| `evaluated_but_not_crossed` | **7** |
| `crossed_not_selected` | **2** |
| `evidence_insufficient` | **4** |
| **Total** | **384** |

Les deux versions Python rejouent **la même cohorte déterministe**, sans crédit de seize nouvelles vies. Les **247 pas sans option** contiennent des diagnostics `incomplete_model` : le planificateur reçoit un objectif mais ne produit pas de trajectoire admissible. Dans les quatre cas à preuve insuffisante, un objectif est activé pendant le premier pas, après la fixation du contexte de recherche ; la classification ne transforme pas ce délai en dysfonctionnement.

**Compétition réelle plus rare :** deux pas `sustained` au t2 montrent une option alimentaire et une option géographique évaluées pendant **le même cycle 2**, toutes deux au-dessus du seuil 0,5, avec accumulateurs approximatifs **0,804 (alimentaire)** et **0,989 (géographique)**. Le choix final est `se_deplacer`. Ces constats démontrent une compétition simultanée, mais pas l'irrationalité de l'exploration. Les sept options alimentaires évaluées sans franchir le seuil ne sont pas des options perdues au même sens.

## Frontières de preuve

L'outil A2.29 classe à partir de captures, résultats Stage6, `option_registration`, évaluations Stage8, traces de compétition, motif d'action et préengagements B. Il ne fournit aucune vérité physique du banc à I0. Les journaux WAL durables, les jugements de première personne et l'absence de paires GA-06 artificielles passent les auditeurs d'A2.28 dont A2.29 réutilise le moteur, sous réserve de la sémantique *read-only*.

**Résultat principal borné :** dans ce domaine, la pénurie de propositions alimentaires `incomplete_model` explique davantage l'attrition des jugements B que le dépassement par l'option d'exploration. Pour conclure à un défaut de politique, il faut un nouveau protocole contrefactuel prospectif mesurant l'amélioration effective, les conséquences corporelles et les coûts UC, sans imposer les commandes.

Le contrat du jugement B conservateur reste : agence proximale distincte du résultat corporel perçu, responsabilité distale `unknown` en cas de doute. **Aucun `self` distal prouvé, aucun seuil GA-06 abaissé, pas de paires héritées créditées.** Les PR #184/#185/#186 ne doivent pas être fusionnées ensemble au seul motif de la CI scientifique ; il faudra analyser la dépendance de branches, les CI exactes, la migration normative et la réception opérateur. **Stage12 PARTIAL, #110 OPEN, MVP v1.3.1 inchangé.**
