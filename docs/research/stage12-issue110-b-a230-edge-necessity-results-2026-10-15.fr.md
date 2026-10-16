# A2.30-E : résultats prospectifs du recensement des arêtes réellement explorées

**15 octobre 2026.** Préenregistrement antérieur à l'instrumentation : `stage12-issue110-b-a230-edge-necessity-prereg-2026-10-15.fr.md` au commit `413b9a15`. Instrumentation laboratoire `7e384ced`, nouvelle cohorte bornée `a230e`, workflow `2be8008d51ad0d8a02d4795739a828acfba72aac`. [GitHub Actions #38715999434](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38715999434), deux interpréteurs Python 3.11/3.12, résultats identiques d'après leurs journaux. Ces exécutions rejouent les **mêmes huit identités** : ne pas doubler le nombre de vies.

## Méthode et limites

Quatre profils alimentaires `restored/sustained/episodic/marginal` × obstacle `free/A2` ; huit nouvelles vies autonomes B, 24 pas chacune, **192 véritables transitions physiques**. Un replay technique non instrumenté de 24 pas est explicitement exclu de cet effectif. Le journal canonique du témoin et de son homologue instrumenté est **identique octet pour octet**. Auditeurs physiques, WAL, first-person, goal progress et dual-scope restent appliqués par le runner hérité. Aucune commande forcée, aucune transmission de vérité cachée au modèle, aucune modification du runtime I0, de son Equipment, de ses règles UC ou de la spécification.

Le témoin externe recense chaque véritable appel de recherche et chaque `Simulator.rollout`, son couple état accessible/commande, sa clé SHA exacte, la disponibilité, le motif réel de refus, la profondeur, ainsi que la présence d'un exemple physique avant naissance. Les compteurs internes `expanded_states`/`unavailable_edges` et les statuts publiés dans le journal sont confrontés aux appels observés.

## Résultats reproduits

| Métrique | Résultat |
|---|---:|
| Vies indépendantes / pas physiques | 8 / 192 |
| Recherches Stage6 réellement observées | 141 |
| Recherches en statut `incomplete_model` | 121 |
| Arêtes effectivement explorées par Stage6 | 926 |
| Entrées exactes Equipment manquantes | 880 |
| Commande jamais enregistrée pour le modèle courant | 670 |
| Commande enregistrée, mais état complet non couvert | 210 |
| Replay technique identique au journal témoin | Oui |

Décomposition des **880 entrées exactes manquantes** par primitive :

| Primitive tentée | Refus |
|---|---:|
| `se_deplacer` | 511 |
| `attendre` | 169 |
| `dormir` | 169 |
| `collecter` | 27 |
| `boire` | 4 |
| **Total** | **880** |

Aucune occurrence `manger` ne figure **parmi les refus** de cette cohorte ; cela ne constitue ni une preuve de présence générale de cette connaissance ni une preuve d'atteignabilité de la nourriture. Certaines commandes candidates ne peuvent apparaître que sous des préconditions accessibles (par exemple possession de baie pour `manger`). Les nombres sont des appels d'arêtes avec répétitions possibles, **pas** des couples indépendants état/commande, et ne représentent pas un taux général de couverture de l'environnement.

## Classification épistémique

- **H1 soutenue, de façon délimitée** : l'Equipment exact en vigueur ne couvre pas 880 appels réellement examinés. On sait précisément si l'entrée est absente pour la commande entière ou pour cet état accessible particulier. **Non démontré** : que ces arêtes manquantes soient indispensables à l'objectif alimentaire dans chacune des 121 recherches incomplètes.
- **H2 non tranchée** : l'horizon fixé à 3 et les préconditions de génération des actions limitent les chemins accessibles. Une arête refusée ne prouve pas l'existence d'un plan plus long ou d'une issue structurellement impossible.
- **H3 non tranchée** : le témoin C1–C5 a passé la CI [#38714785736](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38714785736) en Python 3.11 et 3.12. Il ne prouve pas l'absence de défaut sur toutes les recherches réelles.
- **Attribution Stage12 indépendante** : la réussite physique, le jugement proximal et la responsabilité causale distale restent des prédicats distincts ; GA-06 n'est pas artificiellement complété.

Le déclenchement de `incomplete_model` dans `SimulatorPlanner.search` reste `unavailable_edges > 0` lorsqu'aucun plan / progrès partiel n'est retenu. La nouvelle trace montre les arêtes concrètes qui manquent. Elle ne démontre pas qu'elles soient indispensables et ne valide donc **aucune requalification de statut public**. Il serait trompeur de traduire automatiquement chaque retour par « I0 ignore comment manger ».

## Prochaine hypothèse discriminante

Préenregistrer un essai d'ablation, à modèle exact fixé et état initial accessible égal : comparer, pour les **121 recherches** réelles, les chemins candidats générés, les refus sur des préfixes alimentaires plausibles et un témoin indépendant de graphe borné. Faire ensuite une intervention expérimentale avec corpus alimentaire physique enrichi **uniquement avant naissance**, sur une autre cohorte et un contrôle apparié, sans modifier les politiques et les seuils d'agence. Quantifier séparément la réduction d'entrées inconnues, l'augmentation de plans, les commandes vraiment exécutées et les conséquences alimentaires physiques. Ne pas injecter les clés manquantes issues des vies cibles dans leur propre équipement.

## Décision

**A2.30 PARTIELLE** : diagnostic des entrées inconnues documenté, comportement décisionnel intact, preuves reproductibles ; nécessité causale de ces arêtes et H2/H3 non départagées. **Stage12 PARTIAL, issue #110 OPEN, PR #187 DRAFT.** La clôture et la réception du Stage nécessitent encore un accord opérateur distinct. Aucun amendement normatif MVP v1.3.1 n'est demandé à ce stade.
