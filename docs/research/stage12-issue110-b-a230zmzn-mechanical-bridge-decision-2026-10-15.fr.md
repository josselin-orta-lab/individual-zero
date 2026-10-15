# Décision A2.30-ZK/ZL → ZM/ZN : pourquoi une première expérience ne généralise pas automatiquement

**15 octobre 2026, PR [#207](https://github.com/josselin-orta-lab/individual-zero/pull/207), empilée sur PR #206.**

Les campagnes donnent une décomposition expérimentale de l'obstacle Stage6 :

- **ZG/ZH, PR #200** : sur huit états initiaux réellement vécus par des I0 autonomes, un modèle externe enrichi de transitions B physiquement observées peut former des premières sous-étapes. **Aucune** de ces transitions externes n'est devenue une mémoire propre à I0.
- **ZK/ZL, PR #206** : des sondes B faites *dans le même monde de laboratoire* permettent d'apprendre les anciennes arêtes exactes mais le nouvel état courant a généralement une autre clé; quatre mouvements est avec danger caché sont physiquement terminaux malgré les mêmes perceptions initiales que les témoins sûrs, et parfois malgré les mêmes valeurs visibles de l'état suivant. **Expérience motrice non ingestive ≠ preuve de sûreté.**
- **ZM prospectif, PR #207** : toutes les **64 boucles** retrouvent les coordonnées d'origine après 4 mouvements physiques, mais **4/64** seulement retrouvent le `SimulationState` complet, en l'absence totale de dérive corporelle et de changement jour/nuit. Seules ces quatre racines permettent la réutilisation de `FrozenTableEquipment` et la construction d'un `plan_found` géographique d'un pas. Quatre déplacements suivants sont **réellement appliqués** et correspondent aux conséquences prévues. Tous les **60** autres cas échouent en `incomplete_model` malgré retour au même site. **Ce sont 64 mondes/260 actes +64 recherches Stage6 shadow originaux, 0 vie I0.**
- **ZN rétrospectif, PR #207** : 64 classes, 260 reçus, 64 comptages de clés et les quatre prédictions physiquement confirmées sont recalculés depuis les fichiers immuables d'origine avec **24 tests adversariaux PASS par version Python**. Aucun nouveau monde.

## Ce qui est désormais démontré et ce qui ne l'est pas

La table exacte opère conformément à son contrat : une expérience relative à `(état_ancien, action)` ne permet **pas** de prédire `(état_nouveau, action)` lorsque le nouvel état varie en énergie, faim, eau ou phase nocturne. Cela explique un verrou mécanique **dans la physique du laboratoire et la recherche shadow**, pas une impossibilité de cognition ou une absence générale de mémoire d'I0.

La tentation de supprimer une partie de la clé (`body`, `is_night`) serait **scientifiquement infondée** : les effets corporels absolus dépendent des conditions visibles, et d'autres effets mortels dépendent de causes cachées. Les résultats ZK établissent précisément qu'une prédiction motrice non terminale nominalement reconnue peut manquer une mort physiquement possible. La profondeur du planificateur n'y remédie pas en l'absence d'une première transition prédictible.

## Prochaine décision technique potentielle, non autorisée par cette PR

Avant tout déploiement, étudier sur des mondes **tenus à l'écart** et **sans modifier `src/i0`** un modèle **factorisé et explicitement incertain**, séparant (i) géométrie/visibilité, (ii) deltas corporels observables, (iii) terminalité **inconnue si risque caché non identifié**, et (iv) abstention ou action soumise à un garde-fou. Chaque gain de couverture doit être apparié à un contrôle de fausse sécurité, notamment les zones létales invisibles et les baies toxiques. Il est interdit de remplacer un refus épistémique du Stage9 par une certitude statistique non calibrée. Un résultat shadow positif ne justifie ni arbitrage ou action forcée, ni intégration des expériences d'autres mondes comme mémoire vécue d'I0.

**Statut : A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; PR #207 DRAFT, non fusionnée ; aucun déploiement cognitif ni changement de la spécification MVP v1.3.1.** Les obligations de mortalité M11/WAL, séparation Oracle/Bench, sûreté Stage9/DC-05 et attribution subjective B restent intactes.
