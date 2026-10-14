# A2.18 : épreuve séquentielle de la révision d'une attribution d'agence subjectivement plausible

**Préenregistrement daté du 14 octobre 2026, avant toute instrumentation A2.18.** Base vérifiée : `main 5174c161df76838d49a786de599b441e8da12fe2`. Référence : issue #110, A2.17b (PR #172 et #173 fusionnées). Spécification normative v1.3.1 inchangée. Stage12 PARTIAL, aucune réception opérateur.

## Question scientifique et frontière de connaissance

A2.17b a établi deux faits complémentaires : (1) un déplacement externe, après l'échec physique d'une commande, peut produire exactement les mêmes captures de première personne et le même jugement `self` qu'un mouvement réellement exécuté ; (2) une augmentation d'inventaire est au mieux un indice **proximal** de collecte et non la responsabilité du résultat alimentaire **distal**.

A2.18 ne présuppose pas que de nouvelles expériences rendent la cause passée identifiable. Elle teste si des indices *ultérieurs* (`self`, `unknown` ou `world` pour une nouvelle action) modifient le jugement initial, et vérifie si l'historique perceptif entier suffit à distinguer une première commande réussie d'une première relocalisation externe. Il est interdit de livrer au juge les `WorldBody.apply.effects`, `set_position`, les schedules d'échec, une vérité Oracle/Bench ou une étiquette physique.

## Hypothèses préalables

- **H1, non-identifiabilité longitudinale :** si deux mondes ont des captures accessibles identiques à chaque pas et des intentions/commandes identiques, le service subjectif actuel donne les mêmes jugements, même quand la cause physique du premier déplacement diffère. Les effets externes permettent seulement au banc de connaître cette différence.
- **H2, indice nouveau spécifique :** une seconde commande réussie et constatée est jugée `self`, un échec silencieux et non déplacé `unknown`, un obstacle apparu visiblement *après* son préengagement `world`. Ces indices concernent **la seconde commande**. Ils ne constituent pas à eux seuls une preuve rétrospective de la cause de la première.
- **H3, absence de rétro-révision automatique dans le service actuel :** le premier jugement `self` persiste dans le reçu d'expérience initial ; le second est une *nouvelle* attribution, non une rectification de la première. C'est une évaluation du service `GoalAgencyService`, pas la preuve que l'ensemble du système cognitif ne peut jamais apprendre.
- **H4, frontière alimentaire :** aucune sortie A2.18 ne transforme un indice de mouvement ou d'inventaire en preuve d'agence sur la variation de `body.food`; aucune paire GA-06 n'est inférée de ce banc.

## Plan expérimental fixé avant code

**8 seeds spatiales 91 à 98 ; six conditions appariées par seed, soit 48 mondes `WorldBody` indépendants et 96 véritables transitions physiques `WorldBody.apply` (2 commandes par monde).** Toutes les conditions partent de la même cellule par seed, avec deux ressources hydriques adjacentes successives à l'est, perçues strictement localement. Le même objet `GoalAgencyService` est utilisé *dans chaque monde* pour les deux préengagements successifs : pas 1 -> jugement au pas 2, puis préengagement au pas 2 -> jugement au pas 3. Il n'y a ni remise à zéro de l'owner entre ces jugements, ni pas physique fictif.

Trois familles de seconde expérience, chacune avec deux origines physiques de premier déplacement :

| Histoire de premier déplacement | Seconde commande | Conditions |
| --- | --- | --- |
| Réussite volontaire réelle / échec physique suivi de `set_position` extérieur invisible vers la même cible | Réussite volontaire réelle | `normal_then_success`, `confounded_then_success` |
| Même paire d'origines | Échec imposé invisible, sans déplacement ni nouveau blocage observable | `normal_then_silent_failure`, `confounded_then_silent_failure` |
| Même paire d'origines | Obstacle extérieur créé **après** le second préengagement et avant l'application physique | `normal_then_new_obstacle`, `confounded_then_new_obstacle` |

Décompte préenregistré : **24 relocalisations extérieures** au premier pas ; **16 échecs silencieux** au second ; **16 nouveaux obstacles physiques** au second. Les codes physiques et les reçus d'événements restent exclusivement dans les artefacts du banc. Pour chaque essai, enregistrer captures et empreintes de perception t1, t2, t3 ; préengagements, jugements, refs, commande et SHA de transition ; événements extérieurs, effets réels, états avant intervention et après transition.

## Critères fixés avant résultats

- **T1 (intégrité physique) :** exactement 48 mondes, 96 appels effectifs `WorldBody.apply`, 24 relocalisations, 16 échecs silencieux au second pas, 16 nouveaux obstacles. Au premier pas des 24 histoires confondues, la commande est physiquement empêchée *avant* la relocalisation. Les mouvements normaux aboutissent par la commande.
- **T2 (indiscernabilité longitudinale) :** pour chaque seed et chaque famille de seconde expérience, les **trois captures `PerceptualCapture` complètes** sont égales entre l'histoire normale et confondue. Les commandes et engagements de même signification le sont aussi (références de vie exclues). Si cela échoue, H1 est INCONCLUSIVE.
- **T3 (jugements actuels) :** pour chacune des 8 seeds, `self -> self` (famille réussite), `self -> unknown` (échec silencieux), `self -> world` (nouvel obstacle), **sans divergence de jugement entre causes physiques appariées**. Le premier `self` est physiquement erroné dans 24 histoires confondues sans être subjectivement incohérent.
- **T4 (révision) :** ne pas comptabiliser le second jugement comme une révision du premier. Vérifier qu'il s'agit d'un autre `assessment_ref` et que la preuve antérieure est conservée par l'observateur ; si aucune correction de la première attribution n'existe, publier honnêtement **0 révision observée**, sans qualifier cela d'échec de la bonne calibration d'un mécanisme de révision qui n'existe pas.
- **T5 (reproductibilité et indépendance) :** matrice GitHub Actions Python 3.11/3.12, SHA du code et résultats par monde ; deux versions Python reproduisent les *mêmes* 8 seeds et ne sont pas 16 répétitions indépendantes. Aucune vie cognitive autonome ni stabilité 600 pas prouvée par ce banc.
- **T6 (garde-fous) :** ne pas changer la spécification v1.3.1, le contrat de `GoalAgencyService`, les propriétaires/UC, Action Control, WorldBody, WAL, mortalité, Equipment, Oracle, Stage9/DC-05 ou les seuils `2+2/12`. Aucun jugement synthétique admis au détecteur ; no-go pour toute promotion en politique.

## Décision conditionnelle

Si H1/H2/H3 sont confirmées, conclure seulement à la **limite d'identifiabilité des expériences successives** et à l'absence de révision explicite dans le service testé. Une vraie stratégie de révision exige un contrat distinct sur la mémoire des jugements, la provenance des nouveaux indices, l'incertitude, les UC et l'atomicité, puis un ON/OFF sur vies autonomes. La séparation **agence proximale de l'action / responsabilité distale de l'objectif** demeure une **décision normative opérateur non prise**, préalable à toute modification cognitive. Maintenir Stage12 PARTIAL et issue #110 OPEN même si T1–T6 sont satisfaits.
