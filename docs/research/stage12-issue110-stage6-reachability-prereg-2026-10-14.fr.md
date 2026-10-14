# Issue #110 : préenregistrement du contrôle d'atteignabilité Stage6, campagne B (14 octobre 2026)

**Établi avant l'implémentation et l'exécution de cette variante, après avoir consulté les résultats négatifs antérieurs.** Ce travail est une exploration corrective, **pas** une confirmation hors échantillon.

## Cause à éprouver

Le planificateur Stage6 calcule une trajectoire de satisfaction d'un objectif **absolu** (`food >= setpoint`) avec `max_depth=3`. L'étude multi-engagement précédente remplaçait le gain de `berry_a` par 3, 6 ou 12 alors que le déficit alimentaire initial pouvait atteindre 27–38 unités. Même un trajet de trois actions parfaites ne pouvait pas combler ce déficit avec une seule ingestion ; zéro `active_goal` a été sélectionné malgré un objectif `eat` actif et un grand nombre de déplacements d'exploration. La présente étude doit vérifier la production réelle de `stage6_planning_result` et pas seulement la présence des buts.

## Variantes physiques fixées avant naissance

Conserver **tous** les paramètres cognitifs, compute budget, équipement appris pré-naissance et garanties de garde : seuils du détecteur intacts `window=12`, `bias_min_outcomes_each=2`, `threshold=0.75`; Stage6 `max_depth=3`. Le corps commence dans la même cellule et la nourriture sur la cellule (3,1). Chaque condition possède une contrepartie A2 `set_obstacle` à t2 `after_admission` puis retrait à t4 `before_step`, temps et coordonnées fixés avant naissance, jamais conditionnés à la commande.

| Profil | Nourriture initiale | Gain par ingestion `berry_a` | Décroissance alimentaire/pas | Baies |
| --- | ---: | ---: | ---: | ---: |
| restored | 35 | 30 | 0 | 12 |
| replenished | 35 | 40 | 2 | 12 |
| urgent | 35 | 50 | 4 | 12 |

**Six vies indépendantes × au plus 36 transitions physiques = 216 pas.** Le premier profil sert de témoin de compatibilité du scénario positif déjà observé, sans artificiellement déclarer une vie riche en objectifs. Les variantes avec décroissance cherchent si un nouveau besoin peut revenir après satisfaction sans qu'une intervention cognitive l'impose.

## Mesures et protections

Conserver les journaux immuables JSONL, WAL et SHA, plus un recensement read-only par pas des buts, des reçus `stage6_planning_result` (`proposal_ref` vrai/faux), des propositions exploration, des inscriptions, des options évaluées, des motifs de commande attestés, des suivis cognitifs, des paires et des étiquettes diagnostiques si les critères sont atteints. Les auditeurs indépendants des objectifs, agence, paires, interventions A2 et WAL doivent accepter intégralement chaque vie. Comparer les deux versions de Python sans supposer une identité binaire du journal, car la divergence des valeurs TD Stage8 est déjà documentée.

Un `world` n'est évaluable que s'il est émis par Action Control à partir d'une capture vécue pertinente ; aucun résultat Oracle ne peut lui être injecté. Les `unknown` restent des abstentions. Comparer explicitement le nombre de propositions Stage6 non nulles aux options exploration sélectionnées. S'il n'existe toujours pas de trajectoire autonome 2 succès + 2 échecs dans une fenêtre de 12, conclure `NON ÉVALUABLE`; ne pas modifier arbitrairement les seuils et ne pas agréger des vies au sein d'I0.

Pas de modification du document normatif v1.3.1, pas de fusion ni clôture de l'issue #110 sans réception opérateur.
