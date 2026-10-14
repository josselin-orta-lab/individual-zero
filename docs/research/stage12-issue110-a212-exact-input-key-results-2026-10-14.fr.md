# Individual Zero #110 : A2.12, correspondance exacte des états et commandes du simulateur

**14 octobre 2026, verdict GLOBAL Stage12 PARTIAL.** Préenregistrement réalisé avant instrument : `e98c6327012ce2772c6bc2278caae297f4043a88`. Code exécuté : `107500dd60e18307324f0247c69407f1201508f7`. La source `main` de départ est `461bc552fa20f95bcc59b6319e3e9050d9ea1036`, spécification v1.3.1 inchangée.

## Méthode reproductible et contrôle d'innocuité

[CI A2.12 #38616392756](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38616392756), **SUCCESS sous Python 3.11 et Python 3.12**. Huit vies mortelles neuves ×42 pas = **336 transitions physiques uniques** par cohorte de conditions (les deux interpréteurs répètent la même matrice, ce ne sont pas seize seeds indépendantes). Les validations physiques existantes de A2.11b, journaux canoniques/WAL/GA/P-48/A2 et la nouvelle sonde prédisent les mêmes agrégats, zéro erreur technique.

La sonde est **externe**, branchée autour de l'appel exact `FrozenTableEquipment.predict` sans modifier la réponse ni le `LookupError`; elle reçoit les états/commandes réellement demandés par le simulateur, et les confronte exclusivement aux entrées `EquipmentCorpusRecorder.record_transition` réellement générées avant naissance. Elle ne modifie ni la décision, ni les UC, ni le contenu de l'Equipment ni la physique. Les fichiers `exact-key-audit.json` par vie dans l'artefact GitHub contiennent pour chaque entrée refusée un SHA-256, la commande, le nombre d'appels, une classification `unseen_command` versus `unseen_state_for_known_command`, et, lorsqu'il existe un exemple de la même commande, la liste des champs qui diffèrent du **plus proche exemple de ce corpus**. Un « champ du plus proche exemple » n'est **pas** une preuve que ce champ est la cause nécessaire du refus, car toutes les différences contribuent au SHA exact.

## Observations primaires

| Profil / monde | Clés distinctes inconnues OFF | Clés distinctes inconnues ON | Diminution ON |
| --- | ---: | ---: | ---: |
| restored / libre | 101 | 99 | 2 |
| restored / obstacle A2 | 117 | 115 | 2 |
| sustained / libre | 183 | 182 | 1 |
| sustained / obstacle A2 | 191 | 190 | 1 |
| **Total** | **592** | **586** | **6** |

Sur les huit vies : **1 178 clés d'entrée distinctes refusées**, dont **610 clés de commandes sans exemple correspondant** dans leur Equipment prénatal. Le reste, **568 clés**, correspond à des commandes au moins une fois entraînées mais demandées depuis un état complet jamais observé. Il s'agit de clés uniques **par vie**, pas d'unions inter-vies, ni du nombre de requêtes répétées. Les différences par champ sont enregistrées dans les artefacts individuels ; aucune statistique de dominance de champs n'est revendiquée ici sans extraction agrégée vérifiée.

**Contrôle comportemental :** les mêmes quatre paires A2.11b conservaient exactement le même nombre d'ingestions OFF/ON (restored libre 1/1, restored A2 1/1, sustained libre 1/1, sustained A2 **0/0**) et de recherches `incomplete_model` (0/0, 8/8, 33/33, 36/36). La réduction de **six clés inconnues** entre les huit conditions n'améliore aucun repas physiquement vécu; elle n'est pas un PASS C4. L'apparente contradiction avec des comptes `incomplete_model` identiques est attendue : une recherche peut rencontrer beaucoup de clés inconnues, et réduire leur nombre sans devenir complète.

## Ce que l'expérience démontre, et ses limites

**H_exact : fortement étayée et maintenant mesurée clé par clé.** Le modèle prénatal est strict exact : `input_digest` contient état corporel, inventaire, localité, ressources voisines, jour/nuit et commande. Les couples connus donnent une vraie prédiction issue du corpus; les couples inconnus restent indisponibles. La nouvelle observation identifie séparément **610 clés sans aucune preuve de commande entraînée**, et **568 refus sur commande déjà connue mais état différent**. Cela ne signifie pas que les 568 états pourraient être généralisés sans danger. La classification est relative à chaque corpus et à chaque vie.

**H_coverage : effet technique faible**, réduction totale de 592 à 586 clés refusées en huit vies; hypothèse de rétablissement alimentaire **FAIL**, même après ajout de transitions physiques authentiques. Aucune preuve que la mémoire est intrinsèquement défaillante ni que le veto de sécurité est la cause principale. Le contrôle explicite des UC Planning du sous-lot A2.11 indiquait zéro refus, mais il n'évaluait pas toute l'ordonnancement computationnel.

**Risques :** il serait scientifiquement non défendable de normaliser arbitrairement la variable food, de neutraliser le voisinage ou d'imputer une sécurité commune à tous les fruits pour transformer artificiellement les 568 clés en prédictions. Les tests de conséquences toxiques et retardées, les contre-exemples de causalité et la calibration subjective à 2 succès+2 échecs/window12 ne sont toujours pas démontrés.

## Décision et critères

| Critère | Verdict |
| --- | --- |
| C1 attribution subjective | PARTIAL, pas de calibration nouvelle |
| C2 distinction causale | PARTIAL, aucun accès oracle ajouté |
| C3 diversité | PASS borné, résultats physiques A2.11b OFF/ON conservés |
| C4 alimentation | FAIL pour le gain hypothétique A2.11b ; Stage12 encore PARTIAL |
| C5 discrimination P-48 | PARTIAL |
| C6 stabilité prolongée | INCONCLUSIVE, horizon 42 pas |
| C7 reproductibilité | PARTIAL, agrégats identiques entre deux Python, aucune seed indépendante |
| C8 conformité | PASS borné, sonde externe, clés inconnues inchangées, audits physiques |

**Verdict global Stage12 PARTIAL, issue #110 OUVERTE, aucun acte de réception opérateur.**

**Suite justifiée** : préenregistrer séparément une matrice de classification par famille de commande et champs divergents (sans modifier le noyau). Avant de tester une représentation d'état compressée, produire des exemples adversariaux où deux états aux mêmes variables supposées pertinentes donnent des effets corporels ou de danger différents. Une généralisation probabiliste devra conserver `unavailable` tant qu'un effet ne peut pas être estimé de façon crédible.
