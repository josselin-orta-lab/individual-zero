# A2.30-ZD : protocole verrouillé, entonnoir décisionnel B sur archives vécues

**Préenregistrement du 15 octobre 2026, avant implémentation ZD et avant analyse des archives ZB détaillées.** Les agrégats ZB sont déjà publics : 12 naissances, 384 pas, zéro collecte/ingestion B, 196 recherches Stage6, 174 sans première arête prévisible, dix `plan_found`. ZD est une **réanalyse d'archives existantes**, sans nouvelle naissance, intervention physique, apprentissage prénatal, ni coût UC supplémentaire. Aucun échantillon supplémentaire ne doit être compté.

## Question et hypothèses rivales

Pour les 8 vies où B est visible au départ (2 profils ×2 layouts visibles ×2 effets), identifier, au niveau des événements du journal canonique, à quel maillon s'interrompt la chaîne `B perceptible → B éligible → B proposée → B sélectionnée → B autorisée UC → B exécutée → B physiquement confirmée`. Comparer avec les 4 témoins B absente. Ne pas confondre recherche `plan_found` avec commande B, ni commande B éligible avec plan causalement justifié.

Hypothèses concurrentes : H1, aucune option/proposition B dans la politique malgré la perception; H2, B proposée mais écartée par compétition, horizon ou coût; H3, B sélectionnée mais refusée par UC, garde-fou ou monde. **Ces catégories ne sont pas supposées mutuellement exclusives** sur tous les pas. Une absence de preuve de proposition n'est pas une preuve de non-proposition si le journal ne contient pas cet événement.

## Méthode verrouillée

1. Utiliser uniquement les 12 `canonical.jsonl` et `a230zb-life.json` des artefacts CI ZB, et leur WAL durable quand accessible. Vérifier identité, pas, intégrité de la chaîne et rapprochement commandes/transitions avec les audits P48, M11 et dual-scope existants.
2. Construire un inventaire **exhaustif** des types d'événements du journal, de leurs champs disponibles et de leur cardinalité, avant toute inférence d'absence. Ne pas inventer de clés d'arbitrage, ni exploiter les effets cachés de B comme prédicteurs des décisions.
3. Reconstituer par vie et pas les captures B accessibles, diagnostics Stage6 réels, éventuels candidats/intentions/compétitions, refus UC, commandes appliquées et effets physiques. Chaque compteur est relié à un type d'événement et à une clé vérifiable. Marquer `unobservable_in_current_journal` pour toute étape sans preuve.
4. Les diagnostics Stage6 sans recherche effective ne sont pas comptés parmi les 196. Les commandes `berry_a` et `berry_b` ne sont jamais regroupées comme succès de B. Les `plan_found` non exécutés ne sont pas des réussites.
5. Confronter profils et layouts uniquement sur leurs dénominateurs réels, sans causalité forte entre naissances distinctes. Les effets cachés ne peuvent expliquer un comportement pré-exposition lorsque B n'a jamais été ingérée.
6. Contrôles adversariaux de l'analyse : journal falsifié, dénominateur de captures B truqué, commande B fabriquée, événement postmortem inventé, refus UC assimilé à un refus d'action sans jointure, faux `plan_found` assimilé à une ingestion. Toute manipulation détectable doit produire FAIL.

## Critères de conclusion

- **H1 soutenue localement** seulement si le journal rend exhaustivement observable l'ensemble des propositions d'actions pertinentes et ne contient aucune proposition B; sinon H1 indéterminée.
- **H2 soutenue localement** seulement avec proposition B attestée, puis arbitrage/perte attestés par les reçus du même pas.
- **H3 soutenue localement** seulement avec commande B effectivement sélectionnée, puis refus UC/monde attesté et lié au même essai.
- Si aucune de ces jointures n'est possible, verdict `DECISION_FUNNEL_NOT_IDENTIFIABLE_FROM_JOURNAL`; ne pas modifier rétrospectivement le protocole pour obtenir un verdict positif.
- Toute future ablation modifiant un prior alimentaire B exige un protocole séparé, un contrôle d'information Oracle et une décision opérateur. ZD ne déploie rien dans I0.

**Sortie attendue :** script d'audit reproductible, tests adversariaux, résultats CI Python 3.11 et 3.12, bilan avec dénominateurs, chemins des archives et limites épistémiques. **Stage12 PARTIAL, issue #110 OPEN, aucune fusion ni modification normative.**
