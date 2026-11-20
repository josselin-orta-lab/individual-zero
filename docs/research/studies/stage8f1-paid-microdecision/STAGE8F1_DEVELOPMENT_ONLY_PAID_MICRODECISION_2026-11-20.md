# Stage8-F1 · contrat d'un choix allégé, payé et volontaire

**20 novembre 2026. Développement logiciel uniquement : `NOT_ADMITTED_FOR_NATIVE_LIVES`.** Aucun nouveau World, individu, descendant, test prospectif ou changement de l'engin historique. Le verdict causal Stage8-E2 demeure **`STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`**.

## Ce que les originaux ont montré

L'[audit E3C](../stage8e3c-first-energy-gate/STAGE8E3C_ORIGINAL_TEMPORAL_RESULT_2026-11-20.md), avec ses 36 864 gzip G2, a constaté que **17 560 individus** perdent la possibilité de financer leur première décision et que **0** ne retrouvent une commande motrice ensuite. Le [bilan E3D](../stage8e3d-energy-ledger/STAGE8E3D_NATIVE_ENERGY_BALANCE_RESULT_2026-11-20.md) montre un coût initial moyen de déplacement/autres actions de ~1,54 énergie/pas, ~0,39 en cognition et seulement ~0,26–0,28 récupéré via sommeil/pas. Ce n'est ni une preuve de médiation génétique ni une validation du bloc gamma.

## Contrat du moteur

La référence `Mind.decide` exige avant toute opération un forfait `CognitiveWork(cycles=3,memory_items=slots)`. La loi v2 facture au moins **0,06 énergie + 0,0002×slots**, et 0,15 vigilance. Au premier refus, `Mind` retourne `None` ; `World.step(None)` ne produit ni sommeil ni recharge d'énergie. Le seuil énergétique observé à la panne est ~0,052, avec vigilance ~94. Les lois et le moteur historiques restent figés.

La discordance [#1478](https://github.com/josselin-orta-lab/individual-zero/issues/1478) reste explicitement traçable : `ACTION_COSTS["dormir"]` affiche 0,25 énergie, mais la branche historique `transition("dormir")` ne débite **aucun coût moteur sommeil** ; elle peut restaurer de l'énergie *après* facturation cognitive. Aucune correction rétroactive ou réduction fictive des coûts n'est autorisée.

## Prototype non raccordé au générateur de vies

Le module [`PaidMicrodecisionMind`](https://github.com/josselin-orta-lab/individual-zero/blob/main/src/i3/modules/stage8f1_paid_microdecision_mind.py) est un **prototype non admis dans `run_life`**, et n'est pas un nouveau `decision_policy`. Il préserve `Mind.decide` tant que son financement initial réussit ; uniquement si le refus historique ne dépense rien, il peut essayer un forfait réduit **préalablement payé** : `CognitiveWork(cycles=1,memory_items=64)`, soit **0,0328 énergie et 0,05 vigilance** sous les lois v2.

La borne 64 paie un bloc local déterministe, des paramètres corporels et génétiques, et au plus **sept lectures d'effets personnels appris**. Ce coût est un modèle de travail cognitif déclaratif, **pas une mesure de CPU** ni une équivalence avec la cognition complète. Le candidat ne prélève jamais un futur regain de sommeil pour financer sa décision.

Il évalue **après paiement** les actions physiquement possibles à partir de sa seule capture première personne : `dormir`, `attendre` si le corps peut le payer, `boire` si une eau accessible est vue et finançable, et au plus quatre pas adjacents finançables. Les effets proposés viennent de **son propre modèle d'apprentissage**, et les enjeux de **ses propres paramètres génétiques `theta/p/w`**, sans source cachée ni bonus de sommeil. L'abstention, **elle aussi payée**, reste admissible et gagne lorsque le modèle ne prédit pas d'amélioration de sa détresse. Le prototype ne force **jamais** une restauration, un repos ni une commande de survie.

Portée délibérément réduite : pas de planification spatiale, de collecte ou de repas, de recherche, de mémoire supplémentaire ou de simulation d'avenir. Les sorties `F1_PAID_SELF_SELECTED_ACTION` / `F1_PAID_VOLUNTARY_ABSTENTION` sont **de nouveaux statuts logiciels expérimentaux, non compatibles avec les traces historiques**. Elles ne sont pas raccordées au runtime ; une admission future nécessiterait une version explicite du manifeste, des contrôles d'intégrité, un audit du financement décision/apprentissage et une preuve d'autorité motrice.

## Contrôle de même dépense cognitive, résultat volontairement écarté

Le même module fournit aussi la sous-classe de laboratoire `PaidMicrodecisionEqualPaidDiscardMind` : elle **lit les mêmes effets appris, évalue les mêmes options et paie exactement `MICRO_WORK` dans les deux monnaies**, puis écarte **après calcul** le résultat moteur de la branche micro et produit `None`. Elle restaure l'intention précédente et n'ouvre jamais de moteur gratuit. Elle ne touche jamais les décisions P1.3 financées normalement. Les tests vérifient l'égalité stricte des corps disponibles après cognition et des preuves de travail, avant la différence d'effet moteur (sommeil réel contre absence d'action).

**Limite cruciale :** il s'agit de parité de **calcul décisionnel**, pas de parité des coûts corporels après action. Le résultat écarté n'est pas l'acte autonome de l'individu ; c'est un contrôle expérimental d'information. Aucune vie n'est exécutée par ce contrôle aujourd'hui, et son admission dans des preuves natives exigerait une version nouvelle, un appariement prospectif de coûts et des audits de traces.

## Critères de falsification sans nouvelle naissance

Les tests synthétiques doivent vérifier : refus inchangé de la référence à énergie ~0,052 ; action de sommeil décidée seulement si **une prédiction personnellement favorable** la justifie ; abstention payée si les prédictions sont nulles ou défavorables ; impossibilité d'emprunter une fraction d'énergie future quand le forfait de 0,0328 est inabordable ; refus après décès vital ou sans budget moteur ; coût cognitif effectivement débité même lorsqu'il choisit `None` ; écart physique sommeil **nominal 0,25 / exécuté 0**.

## Règle d'arrêt et suite

Aucun succès scientifique F1 ne peut être annoncé sur ces tests synthétiques. Avant une vie expérimentale : (i) confirmer les deux suites Python et les invariants natifs, (ii) valider la parité du **contrôle logiciel à calcul égal mais résultat écarté** sur états et mémoires réellement appariés, sans créer d'action gratuite, (iii) définir les nouveaux types de preuves/censeurs et l'audit indépendant, (iv) fixer prospective WorldSpecs, critères de succès et racines séparées, puis seulement deux répétitions techniques et une racine scientifique distincte si la méthode est suffisamment solide. **Ne jamais réutiliser Stage8-E2** pour sauver son résultat causal négatif.

**Statuts :** aucun individu F1 créé, candidat logiciel en développement, i3 non promu, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, Stage8-E2 `CLOSED_NO_RETRY`.
