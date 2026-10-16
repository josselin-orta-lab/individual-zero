# A2.30-ZD : attribution des obstacles alimentaires réellement vécus, audit indépendant des archives ZB

**15 octobre 2026.** Préenregistrement **après résultats ZB et avant code d'audit ZD** : `c64a01acb396152534f8592229c880788a05d586`. Exécution indépendante : [CI #38771544556](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38771544556), Python 3.11 + 3.12 **SUCCESS**, 13 tests adversariaux PASS dans chaque environnement, SHA code de réception `d7ce3465110e6426fd7c71d8c0d5f4d5e58c5d37`. Les deux auditeurs lisent les **mêmes données sources**, sans faire exécuter un seul pas à I0.

## Sources originalement figées

- [Run ZB #38767643472](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38767643472), code de naissance `2a19742df22f27752635203304097134a3009c45` : 12 nouvelles vies *autonomes et mortelles*, 32 pas par vie, 384 pas physiques, aucun moteur de commande forcée ni donnée Oracle.
- Deux artefacts **différents** `a230zb-py3.11` et `a230zb-py3.12`, SHA-256 complets des `a230zb-summary.json` : Python 3.11 `ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b`, Python 3.12 `ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362`.
- Pour chacune des 24 exécutions techniques d'une identité de naissance déterministe : vérification **individuelle** des 12 journaux canonisés (hash), WAL M-11 durable (tête / entrées), 384 couples `command_experienced` / `world_transition_experienced`, audit physique P48 du nombre d'ingestions et des gains alimentaires; correspondance aux reçus originaux. Les **deux Pythons représentent les mêmes douze conditions**, pas 24 individus scientifiques indépendants.

## Entonnoir strictement exclusif, 384 pas

| Porte causalement attestée | Pas |
|---|---:|
| `no_planner_proposal` : objectif actif, recherche sans proposition | **174** |
| `no_attested_active_goal` : pas d'objectif actif attesté | **96** |
| `reduced_sleep` : sommeil/capture réduite sans action éveillée | **46** |
| `evaluated_not_crossed` : option liée à l'objectif évaluée, sans franchir seuil | **32** |
| `goal_selected_with_precommit` : objectif sélectionné avec préengagement | **20** |
| `insufficient_same_step_planner_evidence` : premier acte ou contexte sans recherche attribuable au même pas | **12** |
| `crossed_but_not_selected` : option franchissant un seuil mais non sélectionnée | **4** |
| **Total des pas réellement exécutés et vérifiés** | **384** |

Les recherches `SimulatorPlanner` vraiment exécutées parmi les 238 résultats de planification inscrits au journal sont **196** : **174** sans première arête connue (`incomplete_model`), **10** `plan_found`, **12** `partial_progress`; 42 résultats supplémentaires indiquent la réutilisation d'une option `reused_cached` et **ne sont pas 42 recherches nouvelles**. Le cumul des premières arêtes prédictibles est **18**. Les résultats `plan_found` ne sont pas des repas B et les propositions alimentaires ne documentent pas systématiquement l'espèce de baie.

## Éligibilité, perception et sécurité

La reconstitution indépendante du `SimulationState` complet à la naissance, passée **sans entraîner de modèle** dans `SimulatorPlanner.candidate_commands`, donne :
- **4/4 naissances B_LOCAL** : `berry_b` physiquement présente dans la perception locale et `collecter(berry_b)` *candidate*.
- **4/4 naissances B_EAST** : B visible dans le voisin est passable et `se_deplacer(east)` *candidate*. `collecter(B)` n'est pas encore une action admissible à la racine.
- **4/4 naissances B_NONE** : B absente localement et du voisin est; `collecter(B)` absente du jeu initial.
- **12/12 naissances** : `manger(B)` non disponible initialement, inventaire B vide. **0** commande `collecter(B)`, **0** tentative de `manger(B)`, **0** ingestion B. En revanche, **8** ingestions d'autres espèces sont physiquement attestées.
- **0 refus UC** inscrits dans les 384 pas. Les charges UC effectuées ne sont pas des refus et aucune dépense n'est artificiellement attribuée à l'option B absente.

Ceci **réfute une hypothèse simple d'invisibilité initiale** dans les B_LOCAL/EAST et **ne soutient pas** un blocage attribuable à des refus UC dans cette cohorte. Le groupe `no_planner_proposal` est la porte la plus fréquente, mais **ne prouve pas qu'une transition B serait effectivement choisie une fois son modèle disponible**. Sans pas où une proposition spécifiquement B a été attestée puis perdue, on ne peut attribuer la non-consommation de B à une préférence particulière ou à une inhibition de toxicité vécue.

## Vérification numérique entre Python 3.11 et 3.12

Les deux runs produisent **identiquement** les 384 commandes, transitions physiques et captures perceptives, ainsi que les métriques de recherche et de classement. Toutefois, les journaux ne sont pas tous **identiques octet à octet** :
- **6/12** vies `restored` : journaux binaires identiques.
- **6/12** vies `sustained` : première divergence entre les pas **8 et 11**, dans des champs `$f64` de `stage8_option_evaluation`, `competition_cycle` et `td_update_published`, avec écart maximal absolu de **2,220446049250313e−16**.
- Les divergences internes sont de taille ULP et **ne modifient pas les commandes ni les transitions** pour cette cohorte. Puisque le journal est hash-chaîné, une différence de valeur ultérieure change durablement `journal_head` et le SHA-256 du journal. Chaque journal reste **individuellement correctement authentifié** par M11 WAL/P48.

Le contre-auditeur n'a **ni arrondi ni ignoré** la différence de trace; il exige que les divergences soient limitées à des nombres canoniques dans ces trois familles et refuse tout écart de type, primitive, sens physique ou capture. Une reproductibilité binaire universelle **n'est pas établie** : cette dérive numérique mérite une investigation distincte si la spécification exige identité entre interpréteurs. Elle ne démontre aucun biais causal subjectif et ne justifie pas d'altérer la politique de sommeil ou la norme.

## Portée et verdict

**ZD PASS technique comme relecture historique indépendant du runner de naissance**, sous Python 3.11/3.12. Les tests adversariaux détectent : fruits perceptifs inventés, champs cachés injectés, faux récit moteur rompant la chaîne, options choisies sans preuve de compétition, captures hors borne, duplication d'identité, faux refus UC attribuable, glissement numérique non canonique et violations d'intégrité WAL. Les 12 vies du run d'origine sont les seuls individus étudiés.

**A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN.** Le moteur ZD n'améliore pas I0 et ne se branche à aucun module cognitif. Un test discriminant suivant doit isoler **la disponibilité d'une transition B prédictible dans le modèle exact**, tout en restant d'abord **hors I0, en shadow** et sans ingérer une baie potentiellement toxique. Il faut ensuite, sous autorisation distincte, évaluer si cette couverture est suffisante à une proposition utile et si l'action serait jamais choisie; la réussite sur le simulateur n'est pas une vie alimentaire autonome. Aucun changement normatif ni fusion.
