# I1 v4 : campagne diagnostique « Apprentissage physiologique et crédit temporel »

**Décision utilisateur** : 29 octobre 2026, consignée dans les issues [#305](https://github.com/josselin-orta-lab/individual-zero/issues/305) et [#304](https://github.com/josselin-orta-lab/individual-zero/issues/304).
**État de preuve conservé** : A1-C [run #40944104333](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40944104333), source `26f7929b6db43f68e78b0cc0d9c67e7444f924c6`, 48 vies M11 originales, 24 paires, 12 blocs, `MEASUREMENT_READY`, **NO-GO L3 ciblé**. Ce document est post hoc et ne modifie aucun critère confirmatoire.

## Livrable 1 : dissocier trois mécanismes falsifiables

- **H-R, récompense vs physiologie** : la récompense TD actuelle est la différence de distances absolues pondérées à des `setpoints`, alors que ECO mesure uniquement les déficits sous ces seuils. Les 195 commandes de collecte natives ont toutes reçu un `return_g` TD strictement positif tout en ne réduisant jamais immédiatement le déficit ECO (181 aggravations, 14 égalités). Récompense moyenne de collecte +1,228718, dont +1,0 énergie, +0,4 eau, −0,171282 nourriture. La répartition des actions et les effets différés empêchent d'affirmer que ce décalage explique seul le NO-GO.
- **H-C, crédit différé** : 195 collectes, 113 ingestions FIFO de la même espèce avant H48, 82 restes non consommés, 61/113 délais ≥5 pas. Après ingestion, 112/112 publications TD testables incluent la signature de collecte dans `updated_signatures` ; cela ne renseigne pas sur son poids, ni la force des conséquences nutritives en Q.
- **H-D, mécanisme de choix** : A1-C a trouvé 24/24 paires avec une lecture TD masquée, une option évaluée avec alternatives en Competition, puis une divergence physique. Le sommeil est très différent entre bras (574/1152 pas canoniques, 876/1152 masqués). Ces faits ne certifient ni un effet d'apprentissage favorable dans les deux rôles, ni un lien causal unique de médiation.

## Livrable 2 : nouvelle reconstruction numérique, en lecture seule

L'algorithme `tools/research/i1_a1c_td_bias.py` retranscrit uniquement la composante de trace pour le **feature constant bias=1** du vrai `LinearTDValues.update_segment` : pour chaque mise à jour M11 authentifiée, `z <- (beta * lambda_e) ** segment_length * z`, puis `z[previous_signature] += 1`, et la contribution au poids constant est `eta * delta * z`. Les paramètres effectifs des 48 naissances sont `beta=0.8`, `lambda_e=0.8`, `eta=0.05`. L'algorithme refuse les signatures publiées incohérentes et les deltas non finis.

Un **auditeur autonome local de la cohorte source**, distinct de l'algorithme pur, a contrôlé SHA-256, événements M11 canoniques et tête SQLite pour 48/48 archives ; sur les 112 mises à jour après ingestion il retrouve :
| Rôle / bras | Ingestions avec TD | Trace-biais moyenne | Contribution `eta*delta*z` moyenne | Contributions positives / négatives |
|---|---:|---:|---:|---:|
| native / canonical | 23 | 0,470062 | +0,008643 | 12 / 11 |
| native / td_read_masked | 28 | 0,184342 | +0,019917 | 22 / 6 |
| reversed / canonical | 35 | 0,615046 | +0,020509 | 18 / 17 |
| reversed / td_read_masked | 26 | 0,177767 | +0,043861 | 12 / 14 |

La **trace n'est ni absente ni nécessairement forte** et son incrément signé après ingestion est aussi négatif dans 48 occurrences (11+6+17+14). **Limite impérative** : la composante bias du poids est seulement l'une des dimensions de Q ; ces nombres ne sont ni la variation totale de Q, ni la preuve d'une attribution nutritive isolée, ni une preuve de bénéfice de survie. Les versions de corps, contexte et concurrents peuvent modifier les autres poids et décisions.

## Contrôles, limites et prochaine porte

- Les contrôles adversariaux purement mathématiques couvrent la récurrence, le crédit négatif malgré une trace positive, le refus de signatures M11 manquantes/étrangères/dupliquées et le rejet de paramètres incohérents. Un audit indépendant des ZIP originaux doit conserver ses propres contrôles cryptographiques.
- **Hypothèses non testées causalement** : changement de la récompense TD, ajustement des traces, modification de Competition, avantage d'une autre politique de sommeil. Elles ne sont pas autorisées sur ce diagnostic.
- Avant toute nouvelle naissance : préenregistrer une intervention **isolée** destinée à départager H-R et H-C avec événements moteur M11 suffisants pour reconstruire la variation complète de Q, puis étudier H-D séparément. Aucune priorité alimentaire imposée ni connaissance cachée des baies.
- **Statuts inchangés** : A1-C `NO_GO`, L3 ciblé et général `NOT_ESTABLISHED`. Ne pas relancer la cohorte, et pas de CI naturelle lourde pour ces seuls outils.

**Reproduction** : les 48 ZIP originaux et le manifeste `I1_ECO_A1C_EVIDENCE_MANIFEST.json` restent les sources ; la reconstruction locale complète est fournie dans le dossier de preuve attaché à la campagne, et la récurrence réutilisable est versionnée ici.
