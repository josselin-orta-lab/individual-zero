# A2.30-S : expériences appariées d'acquisition d'informations observables

**15 octobre 2026.** Préenregistrement `906a74eb617168939275c4b95dec1768783d2e27` avant le code et les résultats. [CI GitHub Actions #38740205272](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38740205272) : **SUCCESS** Python 3.11 et 3.12, résultats identiques au SHA `66772ec2281acfbfb6c4c49858c60837feb6b5da`. Les doubles exécutions Python portent sur les **mêmes conditions déterministes**, non des graines indépendantes.

## Séparation rigoureuse cognition / banc

36 mondes `WorldBody` **détachés**, 104 transitions physiques réellement appliquées, 8 morts terminales vérifiées extérieurement; **aucune vie I0**. Les captures de perception potentielles sont limitées à `SymbolicPerception`, à la télémétrie corporelle autorisée et au `SimulationState` reconstruit. Une capture technique effectuée après la transition terminale figure **seulement** dans le reçu physique externe et n'est **jamais** comptée parmi les observations vécues. Ces actions préengagées par le banc ne sont pas des choix de l'individu, et **aucune UC n'a été mesurée**.

Trois familles × trois causes latentes × nourriture initiale {35,45} × positions {(5,5),(7,7)} :

| Intervention de laboratoire | Mondes | Pas appliqués | Décès externes | Première divergence accessible aux deux survivants |
|---|---:|---:|---:|---|
| `attendre → collecter berry_a → manger berry_a` | 12 | 36 | 4 à t3 | t3, uniquement bénin vs toxicité −7 |
| `attendre → se_deplacer(east) → attendre` | 12 | 32 | 4 à t2 | t2, uniquement sans danger vs dégâts 40 |
| `attendre ×3` avec décroissance corporelle modifiée | 12 | 36 | 0 | t1, nourriture/eau déjà accessibles |
| **Total** | **36** | **104** | **8** | |

**36 comparaisons appariées** de deux mondes avec état initial accessible strictement égal. **20** paires présentent une différence accessible pendant qu'elles sont toutes deux encore vivantes, **16** n'ont aucune différence mutuellement vécue avant la fin terminale de l'une d'elles. S1 : aucune connaissance de toxicité obtenue avant `manger`; S2 : aucune connaissance du danger caché obtenue avant `se_deplacer(east)`; S3 : une attente révèle au pas t1 la dérive corporelle, mais **pas la sécurité d'une baie ou d'une position**.

## Interprétation épistémique

Ces résultats ne démontrent **pas** que l'I0 réel souhaite ou sait exécuter ces sondes. Ils mesurent ce qui serait *accessible si* les commandes préengagées étaient réellement exécutées. Un résultat terminal n'a pas de sensation rétrospective vécue : le banc sait que l'issue est létale, mais l'individu ne peut pas accumuler après sa mort une nouvelle connaissance subjective pour la décision suivante. Une altération de l'intégrité chez les survivants peut être observable, mais **seulement après l'exposition**, pas avant la prise de risque.

L'attente reste une action physique avec consommation d'énergie/eau/nourriture dans la fixture : la présence de nouvelle information sur une dérive n'en fait pas une stratégie économiquement ou physiquement optimale. Les coûts UC de délibération et la valeur subjective de l'information ne sont pas mesurés dans ce protocole sans instance d'I0.

**S : PASS technique dans son domaine préenregistré. A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN, PR #190 DRAFT.** Une extension en shadow mode doit garder la même discipline, ne pas promettre qu'une prédiction « reconnue » garantit une ingestion sûre, et ne modifier aucun runtime ni norme MVP.
