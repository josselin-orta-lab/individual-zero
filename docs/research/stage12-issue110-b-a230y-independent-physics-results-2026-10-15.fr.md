# A2.30-Y : relecture physique indépendante des quatre sondes alimentaires W

**15 octobre 2026.** Préenregistrement Y **après connaissance des résultats W et X mais avant le code Y**, au commit `8eaccf644021918730bf840ff362c9fc3c7883d0`. Source physique W originale immuable : [CI #38753518412](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38753518412), code `aecb8d1172846620c3038a4bc10e7716ec7bde1e`. La relecture Y : [CI #38755394234](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38755394234), **PASS Python 3.11 et 3.12**, résultats identiques au commit `a4737e8d11c471266dc49f2cb698b9abae9c2909`, 11 tests adversariaux par interpréteur.

## Contrôle physique indépendant du runner scientifique W

Le code `replay_stage12_issue110_b_a230y_physical_probes.py` **n'importe ni le runner W, ni `EquipmentCorpusRecorder`, ni le planificateur ni l'Oracle**. Il reconstruit la physique via `independently_configure` du banc A2.30-R (constructeur indépendant du P-builder réutilisé dans W), et vérifie les hashes de `WorldPhysicsConfig` et de `WorldLayout` **avant tout acte**. La source W est extraite de l'artefact original GitHub Actions, dont les trois SHA-256 documentés dans les rapports W/X sont entièrement contrôlés.

Le relecteur instancie un nouveau `WorldBody` pour chacune des **80** cellules de sondes (cinq latents × quatre préfixes × deux nourritures × deux positions). Il exécute les **240 actions de replay physique** avec `WorldBody.apply` puis recapture les données réellement disponibles pour l'individu via `SymbolicPerception.capture` et `state_from_capture`. Il reconstitue séparément les **12 témoins positifs de visibilité**, sans acte.

Toutes les configurations physiques, captures avant/après, commandes préengagées, terminalités, consommations, reçus canoniques SHA-256 et champs de prévision perceptive correspondent **exactement** au corpus original : **0 divergence physique**, **0 reprise après décès** et **16 terminaisons reconfirmées**. Les contrôles négatifs rejettent une configuration ou un layout altéré, une conséquence corporelle falsifiée même avec hash recalculé, une fausse terminalité, une commande modifiée, une observation perceptive future inventée, un postmortem présenté comme vécu, une action supplémentaire après décès et un contrôle visible falsifié.

| Groupe de replay | Instances techniques | Actions physiques techniques |
|---|---:|---:|
| Sondes et ingestions W | **80** | **240** |
| Témoins perceptifs | **12** | **0** |
| **Total** | **92** | **240** |

**Comptabilité scientifique stricte :** Y a effectivement réalisé 240 nouvelles applications `WorldBody.apply` dans 92 nouvelles instances techniques, mais elles rejouent les **mêmes 92 conditions déterministes déjà étudiées en W**. Ce ne sont donc **pas** 92 nouvelles conditions scientifiques, ni une population I0 indépendante. Ne pas additionner W 240 et Y 240 pour prétendre à 480 pas scientifiques indépendants, ni doubler les mondes du fait des deux Pythons.

## Portée et décision

Y démontre que l'absence de discrimination pré-exposition, les coûts de sondes, les huit changements visuellement détectables et les 16 morts après ingestion dans W sont conformes à la **physique effectivement implémentée** et ne résultent pas simplement d'archives incohérentes ou d'un runner de collecte original défaillant. Y ne démontre pas la vérité d'une physique naturelle, une loi universelle d'identifiabilité, la sûreté de toutes les ressources, un choix autonome d'I0, ou la cognition d'agence subjective.

**Y : PASS technique, A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, PR #194 DRAFT, intégration cognitive NO-GO.** Aucun changement de la spécification v1.3.1, Stage6, Stage9/DC-05, Stage12, mortalité WAL ou UC.
