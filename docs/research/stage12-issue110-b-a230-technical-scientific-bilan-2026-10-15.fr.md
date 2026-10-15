# Individual Zero : bilan de la campagne A2.30, du diagnostic à la sûreté du modèle

**15 octobre 2026.** Source normative `docs/architecture/reference/en/mvp-specification-v1.3.1.md` inchangée. Référence dépôt `main` : `cb630f6edffab1aecb4630e2b7da2369bb593118` au début de ce bilan. Travaux en brouillon sur la PR [#187](https://github.com/josselin-orta-lab/individual-zero/pull/187), empilée sur #186 → #185 → #184 ; ces PR ne sont **pas fusionnées**. L'issue [#110](https://github.com/josselin-orta-lab/individual-zero/issues/110) reste ouverte.

## Réponse à la question de départ

La cause **immédiate** des retours `incomplete_model` étudiés est **la couverture insuffisante des entrées exactes au départ** : dans A2.30-E, **121 recherches sur 121** n'ont **aucune première transition prédictible**. On ne peut construire aucune trajectoire non vide dans le modèle courant sans une première transition connue. C'est une démonstration de lacune collective de l'Equipment, **pas** la preuve que la commande `manger` manque en général ni qu'une trajectoire réelle est impossible.

## Chaîne de preuves reproductibles

| Expérience | Données réellement vérifiées | Résultat principal |
|---|---|---|
| A2.30, audit initial | 8 vies × 48 = 384 pas | 250 diagnostics `incomplete_model`; pas de cause par arête |
| A2.30-E | 8 nouvelles vies × 24 = 192 pas | 141 recherches, dont 121 incomplètes; 880 appels d'arêtes indisponibles sur 926 |
| A2.30-G, relecture indépendante | **0 nouvelle vie**, 192 pas historiques relus | 121/121 recherches incomplètes sans première arête connue, 0 divergence BFS |
| A2.30-H, classification des clés | **0 nouvelle vie** | 620 refus initiaux : 468 commandes exactes absentes, 152 états inédits pour commande connue; 113/121 recherches sans `collecter`/`manger` candidat |
| A2.30-I, correction d'observabilité | **0 nouvelle naissance scientifique**, relectures techniques 192 pas | Statut historique préservé, compteurs de racine `no_predictable_first_step`, commandes/captures/jugements inchangés |
| A2.30-J, corpus prénatal élargi | 16 nouvelles vies × 32 = 512 pas | 46 exemples physiques supplémentaires par traitement, 165→162 racines bloquées, **4→4 ingestions** |
| A2.30-K, relecture des résultats J | **0 nouvelle vie**, 512 pas historiques relus | 0 différence de commandes, physique, nourriture perçue, UC et B dans 8 paires; 5 paires diffèrent diagnostiquement |
| A2.30-L, tests adversariaux | **0 nouvelle vie I0**, 6 mondes et 8 pas physiques de laboratoire | Même observation+commande, sorties divergentes pour létalité cachée et toxicité, trainer exact rejette les contradictions |

Les **384 + 192 + 512 = 1 088 vrais pas d'I0** appartiennent à **trois cohortes scientifiques distinctes**, chacune bornée en dessous de 600 pas; ce total ne représente **pas** une unique trajectoire. Les CI Python 3.11 et 3.12 et les relectures des mêmes identités **ne sont jamais recomptées comme des naissances indépendantes**. Les huit transitions physiques de L appartiennent exclusivement à des mondes d'entraînement détachés, pas aux pas autonomes d'I0.

## Classification scientifique H1 / H2 / H3

**H1 : CONFIRMÉE à portée limitée.** Les arêtes prédictibles font réellement défaut pour toute première commande dans les 121 recherches initiales étudiées. L'augmentation de corpus en J apporte 9 à 31 clés uniques exactes supplémentaires selon le profil, mais n'améliore les racines bloquées que dans 1/8 paire et les repas dans 0/8. Il n'est pas prouvé quelle commande alimentaire *particulière* doit être apprise pour obtenir un plan utile.

**H2 : l'horizon seul est exclu comme remède pour ces 121 états initiaux.** Plus de profondeur ne peut rendre prédictible une arête initiale absente. Cette conclusion ne porte pas sur les recherches disposant d'un préfixe connu ni sur une impossibilité structurelle hors modèle. Aucun graphe physique fermé ne prouve l'impossibilité alimentaire générale.

**H3 : aucune omission BFS démontrée, mais limites de représentation subsistantes.** Le témoin indépendant G n'a trouvé aucun pruning non justifié dans les recherches épuisées du modèle connu. Il n'exclut pas des défauts de projection, de préconditions, de buts ou des informations cachées. L démontre qu'une même représentation accessible peut produire des conséquences physiques différentes : aucune généralisation déterministe sûre n'est possible sans incertitude ou variables pertinentes supplémentaires.

## Résultat logiciel et frontière Stage12

La **seule modification cognitive de production** est diagnostique : Stage6 conserve les statuts, commandes, simulateur, budgets et comportement, et ajoute aux recherches opt-in `root_candidate_edges`, `root_available_edges`, `root_unavailable_edges` et `root_model_diagnostic`. Une première arête indéterminable est désormais décrite correctement, sans qualifier abusivement la nourriture ou une impossibilité physique. Les tests unitaires ciblés et la régression physique Stage12 ont confirmé la parité décisionnelle (192 pas techniques reconstitués). Le journal technique change de hash uniquement en raison des champs diagnostiques ajoutés; aucune mémoire subjective omnisciente n'est créée.

Stage12 conserve la distinction entre plan, décision, action, résultat vécu, attribution subjective et vérité externe. La cohorte J produit **12 jugements B par bras** sans prétendre augmenter l'attribution distale `self` ni recalibrer GA-06. Les garanties de mortalité, M-11/WAL, Oracle et Stage9/DC-05 restent intactes dans les tests exécutés.

## Validation et décision

Sources CI de référence :
- [A2.30-E #38715999434](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38715999434);
- [A2.30-G #38717100599](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38717100599);
- [A2.30-H #38717728847](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38717728847);
- [A2.30-I #38718639833](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38718639833) et [parité #38718640403](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38718640403);
- [A2.30-J #38720764403](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38720764403);
- [A2.30-K #38721458209](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38721458209);
- [A2.30-L #38722518797](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38722518797).

**A2.30 PARTIELLE** : la **cause épistémique des recherches sans premier pas est démontrée**, les statuts deviennent explicables et les correctifs d'observabilité passent leur contrôle. L'**autonomie alimentaire fonctionnelle** n'est pas améliorée dans les contrastes expérimentés. Présenter A2.30 comme une validation complète de Stage6 serait injustifié ; de même, un gain de couverture n'est pas une preuve de responsabilité causale vécue.

**Prochaine expérience prioritaire :** étudier hors du runtime I0 et sur données tenues à l'écart des entraînements une représentation incertaine/factorisée des transitions conditionnelles, avec contre-exemples `berry_a`/toxicité, mouvement létal invisible et variabilité corporelle. Ne jamais effacer l'incertitude pour produire un plan. Si l'opérateur souhaite transformer cette recherche en comportement cognitif, **demander sa validation normative et architecturale avant le déploiement ou la modification du MVP**. La fermeture #110 et Stage12 restent soumises au processus opérateur.
