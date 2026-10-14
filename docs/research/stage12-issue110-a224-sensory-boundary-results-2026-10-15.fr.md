# A2.24 : résultats de la frontière sensorielle et impossibilité d'attester par auto-cohérence

**15 octobre 2026.** Préenregistrement `34edbee5721a98045148037f42ddfba4758ee7bd` **avant tout code A2.24**. Après deux corrections d'instrumentation (mauvais domaine de seeds dans la fixture importée, puis capture d'une fixture de référence hors du périmètre de l'épisode), l'exécutable final a été vérifié au SHA `e306a29e1a01cd381c57242ffd2e2d1cbe4a1d2a` : [CI #38647774876](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38647774876), **SUCCESS Python 3.11 et 3.12**. Les runs initiaux échoués sont conservés dans GitHub Actions, pas effacés.

## Résultats stricts de la matrice préenregistrée

**20 nouvelles vies Stage12 M11 autonomes et mortelles, chacune bornée à un pas réellement committé** ; quatre variantes spatiales x=8,12,16,20 ; cinq scénarios par variante (`honest_base`, `honest_twin`, `output_spoof`, `input_spoof`, `joint_spoof`). Aucun monde n'est compté deux fois pour les deux versions Python. L'instance est née avec `subjective_goal_agency=True`, son reçu `perceptual_capture` est persistant dans la génération 1 M11, lié au `step_closed` et à l'`attempt_ref`. Aucune seconde WAL ni alimentation de vérité Oracle.

| Condition | Mondes | Projection égale à l'entrée | Entrée égale au témoin déclaré | Capture physiquement correcte |
|---|---:|---:|---:|---:|
| `honest_base` | 4 | 4 | 4 | 4 |
| `honest_twin` | 4 | 4 | 4 | 4 |
| `output_spoof` | 4 | **0** | 4 | 0 |
| `input_spoof` | 4 | 4 | **0** | 0 |
| `joint_spoof` | 4 | **4** | **4** | **0** |
| **Total** | **20** | **16** | **16** | **8** |

**12/12 captures falsifiées sont égales à une capture réelle du monde jumeau translaté**, champ par champ dans les captures de première personne et dans leur projection persistée. L'identité de la vie, les refs du journal et les effets physiques du banc ne sont pas des champs de la perception à comparer. Le capteur compromis ne devient pas physiquement authentique en étant durablement journalisé.

## Interprétation, hypothèses et menace résiduelle

A2.24 sépare expérimentalement trois propriétés qui avaient pu être confondues :
1. fidélité de la **sortie à l'entrée** (altération `output_spoof` détectée),
2. conformité de l'**entrée au témoin déclaré** (altération `input_spoof` détectée),
3. vérité **physique indépendante** (falsification conjointe des deux sources non détectée sans accès à la racine physique).

**Le résultat négatif est explicite : `joint_spoof` passe les deux attestations tout en étant physiquement faux dans 4/4 cas.** Il serait incorrect de proposer un simple hash, une signature contrôlée par le même propriétaire ou une attestation interne comme preuve suffisante contre cette menace. L'auditeur sait ce qui a été fixé à la naissance par le banc ; I0 n'a pas cette information omnisciente.

L'attaque est simulée par un patch de classe dans le même processus de laboratoire, pas par la compromission d'un capteur matériel ou d'une frontière de processus réels. Ces résultats établissent l'indiscernabilité **dans cette matrice déterministe**, pas pour tous les historiques possibles ni sur 600 pas. **0 révision interne de jugement, 0 nouvelle paire GA-06, aucune causalité alimentaire distale** ne peuvent être inférées.

## Verdict

T1–T7 **PASS borné au protocole** sous deux Python ; la falsification conjointe authentifiable est un **résultat négatif** attendu, pas une « protection » démontrée. Les deux premières CI ont rencontré des défauts d'instrumentation et ont été corrigées sans modifier les seuils préenregistrés. **Aucune modification de code de production, UC, WAL, Stage9, Oracle, ni spécification MVP v1.3.1.** Stage12 **PARTIAL** ; issue #110 **OPEN** ; réception opérateur non effectuée. L'arbitrage agence de commande proximale / responsabilité de résultat distal précède toute nouvelle politique cognitive.
