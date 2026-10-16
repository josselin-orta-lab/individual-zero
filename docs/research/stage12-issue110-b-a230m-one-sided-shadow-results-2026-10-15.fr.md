# A2.30-M : apprentissage unilatéral, confiance nominale et conséquence cachée

**15 octobre 2026.** Préenregistrement **avant ajout de la sonde M** au commit `e0c3d6f768390d69d09393363e319874d266707a`. Code et tests au SHA `e29e27d0a459d989a03d9d2302fb8da7d70b11c8`. [GitHub Actions #38723084941](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38723084941) : **SUCCESS Python 3.11 et 3.12**, résultats égaux, y compris les contrôles A2.30-L antérieurs. **M est une expérience logicielle dérivée des contre-exemples physiques déjà enregistrés en L** : six mondes et huit pas de laboratoire réexécutés dans chaque environnement pour les tests ; **aucune nouvelle condition indépendante**, aucune naissance I0 et aucun pas autonome I0 supplémentaire.

## Protocole : l'erreur de confiance d'un échantillon unique

La fonction de laboratoire `_one_sided_shadow()` entraîne une table `FrozenTableEquipment` **avec uniquement l'exemple bénin** de la paire préenregistrée. La conséquence physiquement dangereuse, produite dans un autre monde ayant le *même* couple état accessible/commande, reste **strictement hors entraînement**. La fonction interroge le prédicteur dans cet autre contexte sans effectuer une nouvelle action de monde et compare hors I0 la réponse nominale à la conséquence physique déjà attestée.

| Contrôle apparié | Prédiction E avec une seule observation bénigne | Conséquence réellement enregistrée dans l'autre monde |
|---|---|---|
| `se_deplacer(east)`, danger létal caché | `terminal=False`, `confidence=1.0` | `terminal=True` |
| `manger(berry_a)`, effet nocif caché | `body.integrity=100`, `confidence=1.0` | `body.integrity=93` |

Les entrées de ces contre-exemples ont un `FrozenTableEquipment.input_digest` **strictement identique** aux exemples bénins. Le corps alimentaire atteint **70** dans les deux mondes ingérant `berry_a` ; l'intégrité diffère. Ce sont deux cas discriminants, **pas** un estimateur de fréquence d'erreur ou de risque, ni un test de taux de généralisation.

## Portée

**Résultat démontré :** le champ `confidence=1.0` de `FrozenTableEquipment` atteste dans cette implémentation **la présence exacte d'un couple d'entrée dans la table**, dont la sortie correspond à **l'exemple de formation**. Il ne certifie pas que les conséquences physiquement causées seront les mêmes dans tous les mondes dont les états accessibles sont indiscernables. En présence d'effets cachés, même **sans extrapolation à une clé nouvelle**, un modèle exact à une observation peut prédire un résultat nominalement certain mais faux.

Le refus d'un corpus contenant **deux observations contradictoires** (A2.30-L) n'offre aucune protection lorsque l'observation contradictoire **n'a pas encore été vécue**. Une intervention future ne doit donc **ni** promouvoir `confidence` en preuve physique de sécurité **ni** faire de `plan_found` une attribution causale certaine. Les incertitudes structurelles du monde non observées restent à traiter explicitement, avec abstention et prévention de faux positifs critiques à étudier avant toute politique nouvelle.

Aucun changement du noyau cognitif, de l'Oracle, de Stage9/DC-05, de la norme MVP v1.3.1 ni de la sémantique publique du planificateur. **A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; PR #187 DRAFT**. La sûreté d'un modèle incertain ou probabiliste **n'est pas démontrée** et requiert une évaluation autonome sur des conditions indépendantes et, pour son intégration normative, un arbitrage opérateur.
