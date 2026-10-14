# Individual Zero #110 : A2.9, résultats de réouverture d'obstacle et récupération alimentaire

**Date : 14 octobre 2026. Verdict scientifique : PARTIAL.** Le protocole prospectif `docs/research/stage12-issue110-a29-perturbation-recovery-prereg-2026-10-14.fr.md` a été committé au SHA `47c13342a394f61778da59d6306f2af8d04ad0af` avant le runner, les CI et les résultats. Code audité `00d9e1df9432af4be2a2fc37c83056f36b48b7aa`. [CI #38599941769](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38599941769) **SUCCESS sous Python 3.11 ET 3.12**, résultats appariés identiques : 16 vies autonomes, 42 pas physiques clos chacune, 672 transitions physiques indépendantes (et non 1344), 0 erreur d'audit/WAL/runtime, 0 vie calibrable pour `attribution_bias`. Aucune action forcée, aucun changement cognitif.

## Hypothèses et variables contrôlées

2 profils corporels `restored/sustained` × 2 gains extrinsèques pré-nataux `1.0/1.6` × 4 programmes externes `none/early(original obstacle retiré avant t3)/original(retiré avant t4)/persistent(retiré avant t20)`. Le nom `persistent` désigne une levée tardive, pas un obstacle permanent. I0 effectue le même cycle cognitif habituel (Stage6 `progressive_subgoals`, Stage8, Stage9, P-48 instrumental OFF, Stage12 GA); toutes les vérités d'intervention proviennent du monde externe et sont seulement auditées a posteriori.

| Profil | Calendrier de l'obstacle | Gain 1.0 : `collecter`, `ate`, food final, sites | Gain 1.6 : mêmes métriques |
| --- | --- | --- | --- |
| restored | aucun | 1, 1, 65, 31 | 1, 1, 65, 31 |
| restored | retrait t3 | 1, 1, 65, 30 | 1, 1, 65, 30 |
| restored | retrait t4 | 1, 1, 65, 28 | 1, 1, 65, 29 |
| restored | retrait t20 | **0, 0, 35, 30** | **0, 0, 35, 30** |
| sustained | aucun | 0, 0, 0, 33 | **1, 1, 0.6, 31** |
| sustained | retrait t3 | **0, 0, 0, 32** | **0, 0, 0, 32** |
| sustained | retrait t4 | **0, 0, 0, 32** | **0, 0, 0, 32** |
| sustained | retrait t20 | **0, 0, 0, 32** | **0, 0, 0, 32** |

Tous les calendriers d'obstacle produisent **1 reçu de mouvement bloqué** par vie. `none` en produit 0. Le cas `sustained/free/gain1.6` avait déjà été confirmé dans A2.8 : ingestion et hausse corporelle réelle mais niveau final 0.6 après 42 pas, pas une alimentation durable.

## Tests prospectifs et mécanismes

- **H0 « retirer tôt suffit » : FAIL dans sustained.** Retrait t3 n'a permis **aucune** ingestion dans `sustained/gain1.6`, tout comme t4 et t20, tandis que le témoin sans obstacle a ingéré une baie. Le blocage vécu à t2 peut donc avoir des conséquences comportementales après disparition physique de l'obstacle. Il reste possible que la différence dépende du seul trajet engagé sans mémoire persistante : aucune attribution mécanistique forte ne suit de ce contraste.
- **Sensibilité de l'état corporel** : `restored` réussit après une levée t3 ou t4, mais pas t20. L'effet n'est donc pas une impossibilité uniforme du déplacement/retour physique.
- **Indisponibilité du modèle** : le nombre de `stage6_planning_result.progressive_search_diagnostic.status=incomplete_model` sous `restored` est 0/0 (sans obstacle), 0/0 (t3), 8/8 (t4), **34/34** (t20) pour gains 1.0/1.6. Sous `sustained` : 34/33 (sans obstacle), 35/35 (t3), 36/36 (t4), 35/35 (t20). Dans `sustained`, il ne suffit donc pas de supprimer une indisponibilité au mauvais pas : déjà sans obstacle, de nombreuses recherches restent incomplètes, même lorsqu'une ingestion locale devient possible en gain 1.6. Cette indisponibilité est un facteur du contexte et non une explication causale unique établie.
- **Diversité physique** : dans `sustained`, les scénarios avec obstacle conservent 32/31=103 % des sites du témoin sans obstacle à gain 1.6, mais ne mangent pas. L'exploration est persistante mais inutilisable pour l'objectif alimentaire. En `restored`, t20 atteint 30 lieux et aucune ingestion. La disparition d'un repas ne se traduit pas par une disparition des déplacements.
- **Agence** : **0/16 vies calibrables** pour le détecteur au seuil inchangé 2 succès+2 échecs consommés dans 12 observations d'une seule vie. L'alignement temporel obstacle/action/résultat dans le journal externe n'est pas une nouvelle preuve subjective de causalité attribuable à I0. Les reçus `world` causaux n'ont pas été injectés à l'agent.
- **Réplicabilité** : Python 3.11 et 3.12 présentent **exactement les mêmes métriques appariées**. Ce sont des répétitions du même programme déterministe, non des seeds statistiquement indépendants. L'égalité bit-à-bit des archives n'a pas été démontrée.

## Contre-exemples et limites

Le critère H0 avait été fixé *avant* la cohorte : `sustained/early/gain1.6` devait ingérer lorsque `sustained/original/gain1.6` n'ingère pas. Le critère est **réfuté**, non redéfini. Une réouverture précoce ne suffit pas, mais cette conclusion locale ne signifie pas que toute mémoire de ressource ou toute replanification future échouerait. Les chiffres `incomplete_model` sont des **étiquettes de recherches interrompues par l'Equipment**, non des décisions de sécurité ni des impossibilités du monde. Rien ne prouve encore la bonne réponse subjective à des conséquences alimentaires nocives/retardées, un retour vers une ressource mémorisée, ou une calibration du détecteur.

**Contrôle T1 technique** : 16 vies ×42 pas et 0 erreur ont été vérifiées sur les deux Python. **T2 temporalité des injections** : les journaux conservent les opérations causales externes, et l'auditeur A2 d'origine valide l'intervention t2 et l'effet réel bloqué. La phase de levée t3/t4/t20 est conservée dans l'entrée scénario ; l'audit temporel prospectif spécifique de la levée reste un contrôle à expliciter si le protocole est étendu. Ne pas faire passer une seule tête de hash valide pour une preuve de toutes les sémantiques d'intervention.

## Verdicts bornés C1 à C8

| Critère | Verdict | Fondement |
| --- | --- | --- |
| C1 agence subjective | PARTIAL | Aucun nouveau seuil individuel de calibration atteint |
| C2 distinction causale | PARTIAL | Intervention exogène et effet bloqué vérifiés; aucune contre-intervention subjective riche |
| C3 diversité | PASS borné | Sites ≥80 % des témoins sans obstacle; exploration utile insuffisante |
| C4 alimentation | PARTIAL avec H0 FAIL | Repas restored après t3/t4 mais 0 ingestion sustained perturbé, y compris t3 |
| C5 P-48 | PARTIAL | P-48 inchangé; source d'intérêt ne valide pas la responsabilité |
| C6 long horizon | INCONCLUSIVE | 42 pas par vie; pas de stabilité démontrée A2.9 |
| C7 reproductibilité | PARTIAL | Deux Python concordent; pas de multi-seeds indépendants |
| C8 conformité technique | PASS borné | Aucun code cognitif ni contrat normatif modifié; WAL et auditeurs validés |

**GLOBAL PARTIAL.** Conserver Stage12 #110 OPEN et sans réception opérateur.

## Décision après l'expérience

**Ne pas introduire une règle de « revenir vers la baie » codée en dur** et ne pas augmenter indéfiniment la valeur extrinsèque. Le prochain protocole A2.10 doit tester une **mémoire d'opportunités perceptibles ou un routage vers une ressource vécue**, de façon strictement générale et sous coûts UC, avec ablation OFF/ON, absence d'Oracle, risque inconnu distinct de sécurité démontrée, contrôle nocif/différé et comparaison de ressources alternatives. Avant toute modification du modèle, démontrer que les observations nécessaires existent côté I0 et que le calcul relève d'un module propriétaire légitime. Un changement du contrat scientifique/architecture v1.3.1 nécessiterait une décision normative explicite distincte.
