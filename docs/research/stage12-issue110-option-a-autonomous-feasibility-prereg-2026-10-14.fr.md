# Option A #110 — préenregistrement de faisabilité autonome des indices extérieurs spatiaux

**2026-10-14, enregistré AVANT le runner et toute exécution**. Branche Option A #155. Cette étude de faisabilité n'est pas une validation du détecteur : le producteur intégré et le registre de sous-objectif spatial restent en développement. Les jugements calculés hors runtime ne sont **jamais admis** comme croyances I0.

## Hypothèse et facteurs

Sur quatre nouvelles vies physiques indépendantes, observer si les actions autonomes `se_deplacer` sont orientées vers des ressources *déjà perçues* et si des destinations bloquées sont effectivement **admises et exécutées** par Action Control. Un indice perceptif extérieur seul n'est pas un jugement subjectif. Si les commandes sont absentes, en concurrence avec exploration/sommeil, ou interdites par la sécurité, le résultat est **inconclusif sur la production de world** ; il ne faut jamais forcer une action.

**Conditions** (toutes avant naissance), au départ (2,2), eau 70, nourriture 35, Equipment alimentaire hors-vie issu du corpus physique figé de #152, h_eff=3, 50 pas physiques max par vie :
- `near_food_free` : deux baies sur (3,2), cellule Est passable ; aucune baie initiale sur le départ
- `near_food_blocked` : deux baies sur (3,2), obstacle sur (3,2), Est imperméable mais baie adjacente perceptible
- `near_water_free` : source d'eau sur (3,2), Est passable ; nourriture de référence sur (2,2)
- `near_water_blocked` : source d'eau sur (3,2), obstacle sur (3,2), Est non passable ; nourriture de référence sur (2,2)

Le chevauchement d'un obstacle et d'une ressource ou source n'est recevable que si `WorldLayout.validate` du moteur physique l'autorise réellement, **sans supprimer les invariants WorldBody**. Ne pas changer la sécurité, la physique, les seuils UC, les poids de sommeil ou les choix d'action. La variable `world` reste indisponible jusqu'à admission réelle par le producteur cognitif futur.

## Mesures pré-déclarées

Depuis chaque journal canonique et WAL validés indépendamment, compter : pas réellement appliqués, commandes `se_deplacer` par direction, essais vers la cellule Est, commandes vers Est dont une perception antérieure témoigne de `passable=False`, commande orientée vers la cible adjacente propre à la vie, motivation `active_goal`, résultats de planification, préengagements GA existants, jugements `self/world/unknown`, couples admis/appliqués, UC, sommeil, décès et erreurs. Les références doivent être auditables et les mesures post-hoc hors I0 ne fournissent aucun jugement au runtime.

Conserver pour chaque vie WAL, JSONL, SHA256/head/count, paquet d'audits indépendant, dénominateur des résultats nuls, et statut de mort. Python 3.11 et 3.12 reproduisent exactement les mêmes conditions ; ne pas compter les deux environnements comme huit individus statistiques.

## Critères de décision

- Des commandes vraiment autonomes dirigées vers une cible perçue et bloquée ouvrent la voie à l'intégration de l'attribution spatiale, mais **ne suffisent pas** à démontrer `world`.
- Aucun mouvement admissible vers une cellule bloquée => voie actuellement non observée, conserver `world` inconnu et investiguer la compétition/planificateur plutôt que modifier les critères ou forcer les décisions.
- Une incohérence sémantique ou WAL => **échec logiciel** et arrêt, pas publication de résultat favorable.
- Aucune validation Stage 12, aucun GO scientifique, aucune fusion de PR et aucune clôture de #110 avant suite de la chaîne GA, crash/cold recovery M11 et réception opérateur.
