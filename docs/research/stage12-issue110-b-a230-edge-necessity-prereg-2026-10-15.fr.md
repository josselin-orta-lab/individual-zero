# A2.30-E : audit prospectif des transitions exactes et témoins discriminants

**Préenregistrement du 15 octobre 2026, antérieur aux nouveaux instruments.** Suite de la PR #187 sur la branche `science/stage12-b-a230-model-completeness-20261015`, non fusionnée. La première cohorte A2.30 (SHA `5942cfe3f3d033017d89c61a98d43613f6588a9c`, CI #38697941748) a exécuté huit vies, 384 pas physiques et 250 diagnostics `incomplete_model`, mais n'a pas établi de cause par arête. Les résultats existants ne sont **pas** des données prospectives de ce nouvel audit.

## Hypothèses et prédictions

- **H1 : couverture exacte insuffisante.** Le couple `SimulationState × PrimitiveCommand` tenté est absent du corpus physique accessible au modèle ; absence ne signifie pas que l'arête serait nécessaire au but. Séparer `unseen_command` et `unseen_state_for_known_command`, ainsi que les champs d'état qui diffèrent du corpus.
- **H2 : trajectoire inadmissible.** Un témoin extérieur démontre soit une trajectoire de longueur minimale strictement supérieure à `max_depth`, soit l'absence de chemin dans un graphe fermé fini de transitions connues. Une recherche bornée seule ne prouve pas l'impossibilité.
- **H3 : défaut de recherche.** Un témoin indépendant trouve, sur le *même modèle accessible* et dans le *même horizon*, une trajectoire que Stage6 omet ; rechercher les cas de projection, pruning, ordre et propagation.
- **Indéterminé :** une ou plusieurs arêtes indisponibles qui ne sont pas démontrées indispensables ; un budget/une capture non observés ne doivent pas recevoir une étiquette causale.
- **Arbitrage extérieur :** propositions effectivement produites mais non choisies, distinctes de l'absence de plan.

## Témoins algorithmiques C1–C5

Construire de petits graphes alimentaires figés en fixtures **de laboratoire**, sans les présenter comme des expériences physiques vécues. C1 : `manger` connu et directement satisfaisant ; arêtes périphériques inconnues mais résultat trouvé. C2 : `manger` manquant dans la table, puis ajouté uniquement au modèle expérimental ; changement contrôlé. C3 : `collecter` puis `manger` connus, profondeur 1 contre 2, aucun refus de modèle. C4 : état alimentaire sans ressource dans un graphe fini complet de `dormir`/`attendre`, absence de chemin démontrée uniquement dans ce graphe. C5 : comparer Stage6 à un témoin BFS écrit indépendamment sur des arêtes exactes connues ; un désaccord indiquerait H3. Aucun changement de norme ou de politique.

## Expérience vécue A2.30-E : appel réel au simulateur, sans intervention

Créer huit **nouvelles** identités de naissance préenregistrées `i0:stage12:b:a230e:<profil>:<A2|free>`, quatre profils `restored/sustained/episodic/marginal` × obstacle OFF/ON, 24 étapes physiques au plus par vie (192 pas nominaux), graines et politiques inchangées par rapport à A2.30. **Aucune action forcée, injection de vérité, `set_body`, ressource ajoutée, modification d'UC ou de motivation.** Mesurer à l'extérieur, sans modifier la valeur de retour :

1. chaque `SimulatorPlanner.search` réellement appelé, son état initial accessible, son objectif-mesure, son horizon, son statut et ses compteurs ;
2. chaque `Simulator.rollout` réellement appelé pendant cette recherche, son couple état/commande, clé exacte, statut, motif d'indisponibilité, et comparaison **externe** au corpus physique pré-natal ;
3. les préconditions déjà encodées dans `candidate_commands` (ressource locale, inventaire, voisin franchissable), sans fabriquer d'arêtes ;
4. rapprocher les recherches des reçus canoniques `stage6_planning_result`, des charges UC, des propositions et des jugements B ;
5. préserver les audits WAL, journal, perception, progrès et attribution B. La trace de laboratoire ne doit jamais être transmise à I0.

Le contrôle non-instrumenté comparera sur une vie indépendante à graine et naissance équivalentes les octets canoniques avant/après instrumentation et les résultats physiques. Les répétitions Python 3.11/3.12 ne doublent pas l'échantillon scientifique.

## Critères d'acceptation et bornes

- Tout accès à la table d'entraînement et tout calcul de différence de champs restent **après l'appel** et exclusivement dans l'observateur externe.
- Cohérence arêtes disponibles/indisponibles et compteurs exacts des recherches vérifiée. Pas de certification d'une « connaissance indispensable » depuis un simple `LookupError`.
- C1–C5 passés, ou défaut H3 documenté, tests de non-régression en cas de changement logiciel.
- Compter les pas réels et les identités, ne pas promettre 192 pas si décès/arrêt ; garder séparées les 384 étapes antérieures.
- Aucun changement de Stage9/DC-05, séparation Oracle/I0, GA-06, UC, journal M11, seuil subjectif, ni `mvp-specification-v1.3.1.md`.
- **Statut conservateur : A2.30 PARTIELLE** tant que le niveau d'explication et la reproductibilité ne justifient pas une recommandation à l'opérateur. Issue #110 ouverte et Stage12 non terminé.
