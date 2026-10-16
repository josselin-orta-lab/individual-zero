# A2.30-ZS/ZT : décision scientifique et frontière du prédicteur factorisé

**Référence** : [PR #214](https://github.com/josselin-orta-lab/individual-zero/pull/214), protocole ZS AVANT code `8ae4f26650bdb5f47f474051763bd8c91aba7afd`; première CI expérimentale [#38801117723](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38801117723). Contrôle ZT préenregistré rétrospectivement `0aa82ba0d1340ffc7240fd2f45184cf9814eabcb`; audit original [#38802545036](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38802545036). Ce bras **à deux jobs séparés** ne doit pas être confondu avec la réplication homonyme [#213](https://github.com/josselin-orta-lab/individual-zero/pull/213), qui utilise un journal fsync des prédictions et résultats dans un même processus. Les preuves sont complémentaires et aucun mélange d'observations n'est utilisé pour augmenter fictivement N.

## Ce qui est démontré

**Temporalité des prévisions : défendable maintenant, sur ZS uniquement.** Le modèle empirique est figé après 16 véritables transitions sources, les **104 prévisions test** sont enregistrées et scellées **avant** l'ensemble des 104 actes physiques heldout. Le premier job GitHub termine et publie l'artefact avant que le second soit autorisé à appliquer les actions. Chaque prévision est reliée par hash à la première perception accessible et au modèle source. La phase d'évaluation ne choisit pas de nouvelle sortie prédictive après avoir vu le résultat.

**Projection numérique partielle : défendable sur 64/64 cas nominaux de cette grille déterministe.** Les six champs `x,y,energy,food,water,inventory_berry_b` peuvent être estimés au moyen d'un modèle de deltas appris sur seulement 16 exemples, sans nécessiter la même clé exacte que le modèle Stage6 historique. L'absence de modèle exact de premier pas au nouveau contexte ne signifie donc pas qu'aucune statistique stable ne soit apprenable.

**Abstention : effectue 16/16 refus de prédire sur les situations où la dynamique corporelle serait bornée/clampée.** Aucun faux résultat complet n'est produit pour ces cas.

**Limites de danger : contre-exemples maintenus.** Les 24 mondes à interventions cachées comportent 4 morts de déplacement (dont la terminalité reste inconnue du modèle), 8 blessures invisibles non prédites et 8 échecs de commande (les six champs numériques sont faux). Les effets ingestifs bénin/létal de B produisent la même prévision avant consommation. Une « précision 100 % sur 64 » n'est **pas** une mesure de sûreté physique.

## Interdictions et décision

Le nouvel équipement factorisé est une **ablation externe au laboratoire**. I0 n'en a aucune connaissance, il n'a pas proposé ni autorisé ces actions, et n'en a payé ni UC ni vécu la responsabilité. Le modèle **ne représente ni intégrité, ni terminalité, ni sécurité, ni prochain voisinage complet**; il n'implémente pas le contrat de `EquipmentPrediction` et ne peut pas être introduit tel quel dans le Stage6 cognitif. L'observation A2.30-ZQ, selon laquelle un véritable I0 autonome peut mourir en entrant dans une zone motrice cachée, demeure directement applicable à toute politique d'exploration supposée sûre.

La voie scientifique suivante nécessite un **nouveau protocole prospectif d'admissibilité et de responsabilité** : distinguer conséquence observable prévue, risque mortel inconnu, droit de prendre ce risque avec des UC propres, et jugement d'agence sur le résultat réellement vécu. **Aucune modification cognitive ni de spécification sans décision opérateur et preuves de non-régression.**

**Décision** : ZS PASS temporel et numérique borné ; ZT PASS d'authenticité archive et de cohérence indépendante, mais pas de nouvelle physique ; A2.30 PARTIELLE, Stage12 PARTIAL. Issue #110 CLOSED administrativement, **aucun nouveau GO de déploiement**. PR #214 DRAFT, non fusionnée, aucune modification `src/i0` ou MVP v1.3.1.
