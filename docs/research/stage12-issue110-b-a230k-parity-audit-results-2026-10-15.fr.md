# A2.30-K : audit externe des conséquences de l'enrichissement prénatal

**15 octobre 2026.** Préenregistrement : `e73279efaac51ca72f88b94b88fad418e6585e52`, antérieur au code `518d18cb181c166506f7a809187b8009cd85233f`. **[CI A2.30-K #38721458209](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38721458209) SUCCESS Python 3.11 et Python 3.12**, avec des agrégats identiques. Source vérifiée et non modifiée : les 16 vies A2.30-J ([CI #38720764403](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38720764403)), SHA `73d04843735bdfd60ddbf40ae064057847b614fb`, 512 transitions physiques. **A2.30-K n'a exécuté aucune nouvelle vie ni aucun nouveau pas.**

## Garanties de provenance

L'auditeur indépendant lit le ZIP GitHub Actions `a230j-py3.11` et vérifie les 16 identités de naissance prévues, les 16 ancrages de journal canonique, les 16 empreintes SHA-256, les WAL durables, les pas physiques, les compteurs d'action, les prédicats P-48, les reçus Stage6, les évaluations Stage12, les refus UC et les preuves d'entraînement prénatal. **0 divergence / 16 vies**. Les deux interpréteurs exécutent la même analyse sur le même artefact : pas de double décompte.

Le traitement avait bien **46 transitions physiques supplémentaires** dans 14 mondes prénataux indépendants, en plus des quatre originales, sans extrapolation des entrées inconnues. Après dédoublonnage des clés exactes, chaque condition `restored` ajoute **9 nouvelles clés**, tandis que `sustained`, `episodic` et `marginal` en ajoutent **31** par condition. Ces totaux reflètent l'état des corpus contrôlés, pas le nombre de transitions effectivement utiles aux vies cibles.

## Contraste après une même fenêtre de 32 pas

| Propriété mesurée entre OFF et ON (8 paires) | Paires présentant une différence |
|---|---:|
| Diagnostic de recherche Stage6 | **5 / 8** |
| Commandes primitives effectivement émises | **0 / 8** |
| Traces physiques de positions et sites explorés | **0 / 8** |
| Captures de corps/nourriture et inventaire perçu | **0 / 8** |
| Refus de budget UC | **0 / 8** |
| Jugements distaux Stage12 B | **0 / 8** |
| Nombre d'ingestions physiques | **0 / 8** |

Les huit trajectoires physiques OFF/ON restent appariées à résultat et comportement identiques. Chacune comporte 32 pas ; **aucun décès** dans les 16 vies, toutes terminées par l'opérateur comme `experiment_stopped`. Chaque bras totalise **185 recherches Stage6**, **4 ingestions indépendamment attestées**, **4 étapes de gain alimentaire**, et **12 jugements B**. Les recherches privées de premier pas prédictible passent de **165/185 à 162/185**, uniquement sur `restored/A2`.

### Différences de prédiction, sans comportement différent

Le détail des journaux canoniques compare les diagnostics `status`, `root_available_edges`, `root_unavailable_edges` et le compteur des arêtes explorées, en conservant les statuts publics :

- **`restored/A2`, pas 9–11 :** le modèle historique indique `incomplete_model` avec zéro première arête connue, 6 indisponibles. Le modèle enrichi connaît **une** première arête (5 indisponibles) mais conserve **`incomplete_model`** car les préfixes plus profonds restent incomplets. Il ne crée aucune option alimentaire supplémentaire ni changement moteur.
- **`episodic/free`, `episodic/A2`, `marginal/free`, `marginal/A2`, pas 1 :** `partial_progress` dans les deux bras. Le modèle connaît **1 première arête sur 7** en OFF puis **7 sur 7** en ON, mais aucune commande effectivement exécutée ni conséquence physique ne change.
- **`restored/free` et les deux variantes `sustained` :** les diagnostics de recherche et les comportements appariés ne diffèrent pas dans cette matrice.

**Important :** le changement d'Equipment ne suffit pas à établir qu'une trajectoire utile est désormais entièrement prédictible, admissible, évaluée, choisie et physiquement réalisée. Une première arête connue reste seulement une capacité de prévision partielle. Aucun `self` distal ni preuve d'agence fiable n'est fabriqué.

## Jugement scientifique et limites

**H1 (lacune exacte d'Equipment) : confirmée au niveau racine pour la cohorte A2.30-E et persistante dans J.** L'apport de 46 observations prénatales crée de nouvelles connaissances exactes, améliore parfois la couverture des racines, mais aucune compétence alimentaire nouvelle. **H2 (horizon seulement) : exclue pour les recherches sans aucune première arête**, jamais pour les autres situations. **H3 (omission BFS) : aucun témoin n'a montré un défaut de parcours**, mais la projection, le choix des caractéristiques, les critères d'objectif et la représentation du monde méritent encore des tests.

Cette comparaison est déterministe et ne comporte pas de graines aléatoires indépendantes. Les deux bras ont des identités de naissance distinctes, ce qui doit limiter toute généralisation causale à d'autres environnements. Une parité observée de 32 pas ne démontre pas une sûreté ou une neutralité comportementale universelle.

**A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, PR #187 DRAFT.** Correction Stage6 A2.30-I validée sur le diagnostic, mais aucune correction de la compétence alimentaire n'est démontrée. Aucune fusion, révision normative ou acceptation opérateur ne découle de ces seules CI.

### Priorité scientifique après K

Avant de toucher à la représentation des prédictions, étudier **des transitions physiques appariées à états accessibles contrastés**, comprenant un contre-exemple de sûreté (aliment nocif/délai, contexte spatial dangereux) afin de déterminer quelles caractéristiques d'une règle de transition sont réellement indispensables. Un prédicteur généralisable ne pourra jamais inférer automatiquement que deux ressources ou deux positions partagent la même toxicité, ni s'attribuer les résultats omniscients de l'Oracle. Une décision normative explicite sera nécessaire si le contrat `FrozenTableEquipment` ou son statut dans le MVP doit changer.
