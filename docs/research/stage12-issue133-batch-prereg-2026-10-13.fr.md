# Stage 12 / #133 : préenregistrement du changement de débit (13 octobre 2026)

**Avant toute nouvelle vie.** Baseline main `7a7376852d47f95212a087ecf0dd343adc18eecb`, suite au rapport exploratoire PR #137. Aucune modification des résultats antérieurs ni du MVP normatif.

Hypothèse technique principale : la limite de lot `maximum_episodes=1` et les six étapes séquentielles expliquent l'arriéré de consolidation ; augmenter à **3 épisodes par transaction** tout en conservant un seul cycle six-passes validé pour l'ensemble du lot peut augmenter le débit sans modifier les coûts par événement réellement traité. Un gain mesuré n'est pas garanti : l'algorithme sémantique et les contrôles d'intégrité peuvent limiter les lots. Une publication doit porter la preuve des six checkpoints et de *tous* les IDs sélectionnés ; aucune publication partielle.

**Plan initial :** deux vies mortelles de 80 pas sur un monde de référence, six passes réellement actives, `w_C=0` (décision opérateur), `maximum_episodes=1` contre `3`, budget P-42 initial inchangé (`step_slot_uc=100`, `period_capacity_uc=600`). Toute différence d'événements de consolidation, de nombre de références consolidées, de temps de sommeil, de résultats refusés, de vérifications ou de mortalité sera conservée.

**Contre-hypothèse UC à investiguer :** à long terme le coût `episode_scan = 1` est payé sur l'intégralité de `Memory.episodes`, même ceux déjà consolidés ; un lot de 3 ne résout pas l'arrivée au plafond. On exige un test supplémentaire d'exactitude pour toute implémentation de scan UC incrémental : paiement **avant** accès à chaque tranche, résultat de sélection identique au scan complet, un cut figé, consommation persistante malgré réveil et interdiction de publier des lots incomplets. Si cette preuve manque, la fonction restera expérimentale sans activation dans le runtime d'I0.

Les vies Python 3.11/3.12 sont des répétitions techniques, pas des graines indépendantes. Les résultats sont exploratoires ; `w_C=0` reste le profil de développement. M11 Stage12, validité scientifique globale, Stage9 et l'indépendance Oracle ne changent pas.
