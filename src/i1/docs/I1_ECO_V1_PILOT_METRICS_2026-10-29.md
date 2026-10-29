# I1-ECO-v1 — Contrat d'évaluation de l'individu complet (phase A)

État : **protocole pilote non confirmatoire**, 29 octobre 2026. Base de développement : `main e5e8bdb8c4d94dd5e9d3becd2df63585ed000ad5`. Cette branche n'ajoute aucune action ni valeur cognitive. Elle définit des **métriques d'opérateur** indépendantes du moteur. Les PR #605 et #606 continuent leurs vérifications séparément. **Ne pas ouvrir une troisième PR** avant leur résolution.

## Questions
Une naissance mortelle actuelle I1 régule-t-elle mieux ses quatre besoins au fil d'une vie, sans perdre en survie, quand les valeurs personnelles apprises sont disponibles ? L'effet se répète-t-il lorsque les baies bénéfiques et inutiles échangent leurs rôles physiques, sans que le nouveau-né le sache ? Ne pas assimiler l'accumulation locale de Q à un bénéfice global.

## Première livraison logicielle
Le module `tools/i1_eco_metrics.py` accepte des **trajectoires d'opérateur déjà authentifiées**, avec un échantillon corporel final pour chaque pas exécuté, l'état initial, la configuration des consignes et des échelles, un horizon fixé et un statut terminal. Il refuse les états incohérents, les pas manquants, les morts suivies de pas supplémentaires, les NaN et un statut de mort contradictoire. Il calcule :
- `restricted_life_steps` : nombre de pas physiques avant mort ou censure à l'horizon ;
- `mortality` et `censored`, explicitement distincts ;
- `deficit_area_by_need` : aire des déficits normalisés de nourriture, eau, énergie et intégrité sur **tout** l'horizon, avec pénalité **1 par besoin et pas restant après décès**, et aire moyenne par besoin ;
- `deficit_area_total` : somme des quatre aires, aucune pondération cachée et composantes obligatoirement publiées ;
- `actions`, `sleep_fraction`, `productive_actions` (comptes descriptifs seulement), le nombre d'actes disponibles et l'existence d'une fenêtre post-expérience, sans attribuer causalement l'apprentissage.

L'évaluation utilise des **consignes et échelles effectives de naissance** qu'il faudra copier et authentifier dans le rapport, pas des nombres fabriqués par l'évaluateur. Son jugement final est toujours `NOT_ESTABLISHED` tant que des cohortes et interventions confirmatoires indépendantes ne sont pas mises en place.

## Exigences de données et comparaison
Chaque trajectoire expérimentale doit provenir d'un M11/WAL vérifié avec SHA de code, physique, disposition écologique et identifiant unique. La comparaison `canonique/TD-read-masked` exige deux naissances indépendantes appariées dans une **même condition physique** et une intervention dont les lectures réellement touchées sont attestées. Le calculateur **ne valide pas** le masquage à lui seul et refuse d'émettre un verdict de performance intégrée.

Ne pas confondre graines différentes et environnements indépendants : avec une physique déterministe et un même monde, changer l'ID ne crée pas de nouvelle variation. Les enfants Python 3.11/3.12 sont des contrôles techniques, pas des réplicats indépendants.

## Étapes suivantes
Terminer les PR #605 et #606 après 4/4 CI, merge ou fermeture explicite selon les résultats. Raccorder ensuite un lecteur M11 attestant les états corporels, les actes physiques et les identités à ce calculateur. Définir une petite matrice pilote avec variantes physiques contrebalancées, puis une étude confirmatoire distincte, dont l'horizon, les critères et les tailles d'échantillon seront figés avant résultats. **Pas de GO scientifique sur ces seuls tests unitaires.**
