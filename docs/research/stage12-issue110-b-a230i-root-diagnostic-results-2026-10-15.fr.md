# A2.30-I : diagnostic de premier pas dans Stage6, validation logicielle et parité

**15 octobre 2026.** Modification enregistrée **après** le préenregistrement \`98fa01b697f569bcdd2d57108cef4aa9df2c8f37\`. Commit source \`d99f1a4ccf20c6350a71863f71d837fe10ea5dfb\`, tests unitaires \`7c8dc11733f97c13cf415635a447f4c84fe75908\`, exécution finale contrôlée \`3d35d885b19ffc687b4929aecbec662b461b099f\`.

## Changement strictement limité à l'observabilité

\`src/i0/modules/stage6_planning.py\` conserve les statuts historiques \`plan_found\`, \`partial_progress\`, \`incomplete_model\`, \`not_found_within_horizon\`, les commandes et tous les appels \`Simulator.rollout\`. Les nouvelles propriétés du \`PlanningSearchResult\` comptent, durant **la même recherche** :

- \`root_candidate_edges\` : commandes réellement proposées à la racine avant lancement des prédictions ;
- \`root_available_edges\` : celles qui ont retourné exactement une transition prédite complète ;
- \`root_unavailable_edges\` : celles qui n'ont pas pu être prédites par le simulateur.

Dans le diagnostic existant (opt-in \`progressive_subgoals\`), \`root_model_diagnostic = no_predictable_first_step\` **uniquement** si une recherche terminée en \`incomplete_model\` a tenté toutes ses candidates initiales et que chacune est indisponible. Le motif \`at_least_one_predictable_first_step\` exige au moins une prédiction initiale vraie ; \`not_classified\` reste réservé aux cas sans preuve adéquate. Les résultats de succès anticipé ne sont jamais considérés comme des recherches entièrement explorées.

**Ne pas convertir cette métadonnée en label de cause alimentaire ni en preuve d'impossibilité physique.** Aucune transition conjecturale n'est ajoutée ; aucune connaissance du laboratoire n'est transmise à I0.

## Tests et compatibilité

- [CI Stage6 A2.30-I #38718639833](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38718639833) : **PASS 3.11 et 3.12**. Tests propres de racine inconnue, racine partiellement prédictible, succès anticipé, objectif initial déjà atteint, progrès partiel et mode historique sans \`progressive_subgoals\` ; régressions Stage6 Planning/Equipment/runtime et Stage12 Goal Agency/revalidation.
- [CI de parité physique et subjective #38718640403](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38718640403) : **PASS 3.11 et 3.12**, 8 relectures techniques de 24 pas physiquement exécutés chacune, comparées aux huit archives canoniques d'origine A2.30-E / run #38715999434.
- Parité de **192 commandes primitives** et de leurs pas, captures corporelles et spatiales, présence d'options Stage6, anciens statuts/compteurs de recherche, préjugements proximaux et jugements distaux. Les audits indépendants des nouvelles vies restent exécutés dans le runner B ; zéro échec remonté.
- Ces **192 pas de relecture technique** sont de vraies actions appliquées dans des mondes de test neufs, mais portent les **mêmes configurations et identités de cohorte** pour le contrôle de parité : **zéro naissance scientifique indépendante supplémentaire**. Les exécutions Python 3.11/3.12 sont deux relectures techniques, pas deux cohortes.
- Les empreintes SHA-256 du journal avant/après **ne sont pas supposées égales** : les données diagnostiques publiées sont nouvelles et modifient légitimement les bytes canoniques. La preuve compare les comportements, pas l'identité de tous les octets.

## Résultat logiciel et scientifique

Le code fournit une classification descriptive beaucoup plus précise des échecs : l'opérateur peut maintenant distinguer \`incomplete_model\` **sans première transition prédictible** de \`incomplete_model\` **après une ou plusieurs transitions connues**, lorsque l'option progressive est activée. Il ne crée pas de seconde politique de planification, d'accès à l'Oracle, ni de charge UC supplémentaire.

Les 121 recherches anciennes A2.30-E ont déjà été vérifiées indépendamment en A2.30-G/H : 121/121 sans première arête connaissable dans le modèle, 620 refus initiaux (468 commandes exactes jamais entraînées et 152 états complets inédits pour commande pourtant entraînée), **113/121 sans commande alimentaire directement candidate à la racine**. Ces observations antérieures **ne sont pas des résultats de la nouvelle version logicielle**. Le contrôle de parité supporte l'absence de changement de décision pour les huit conditions rejouées ; il ne prouve aucune généralisation à tous les mondes.

## Suites et réception

La frontière du modèle exact demeure. Faire disparaître \`incomplete_model\` via une interpolation naïve pourrait inventer des effets de fruits dangereux et violer la frontière DC-05. Toute nouvelle représentation ou généralisation d'Equipment doit être préenregistrée avec témoins adversariaux, effets retardés, coûts UC, éventuelle mortalité et preuve qu'aucune vérité physique cachée n'est injectée.

**A2.30 PARTIELLE** : diagnostic de cause immédiate et correction d'observabilité **PASS technique**, mais amélioration alimentaire encore non démontrée, H3 projection/objectif non exclue, validation opérateur absente. **Stage12 PARTIAL ; issue #110 OPEN ; PR #187 DRAFT, empilée sur #186/#185/#184.** Aucune fusion ni modification normative MVP v1.3.1.
