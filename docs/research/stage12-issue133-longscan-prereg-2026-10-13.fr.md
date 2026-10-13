# Stage12 #133 : protocole de résistance P-42 sur 240 pas (13 octobre 2026)

**Préenregistré avant les essais longs.** Les premiers tests de lots 1/3 ont été définis dans `stage12-issue133-batch-prereg-2026-10-13.fr.md`. Cette nouvelle expérience s'intéresse à la traversée du plafond de balayage par pas dans une longue vie.

Plan : deux vies distinctes de **240 pas physiques maximum**, dans le monde de référence, `w_C=0` conformément à la décision opérateur, six passes et `maximum_episodes=3`. Le contrôle conserve le balayage historique monolithique, la variante active le propriétaire de parcours incrémental sauvegardé entre sessions. Même source et budgets : `step_slot_uc=100`, `period_capacity_uc=600`, tarif `episode_scan=1` et un seul traitement P-42 par véritable pas dormant.

**Attentes :** les deux chemins produisent exactement les mêmes lots classés lorsqu'un scan complet tient dans l'enveloppe ; passé le seuil, l'ancien chemin peut refuser le balayage entier tandis que le nouveau poursuit uniquement après débits et checkpoints réels, sans lire de nouvelles observations au-delà du cut initial. Vérifier au moins un cas avec `scan_total>100` et `charged_records<scan_total` si l'exécution l'atteint. Toute absence de franchissement est `INCONCLUSIVE`, jamais PASS fictif. Aucun commit h sans six checkpoints validés. Enregistrer compteurs de scan, refus, épisodes non consolidés, UC, décès, h et WAL complets.

Un échec ou un arrêt prématuré ne doit pas être compensé par de nouvelles naissances. Les versions Python 3.11 et 3.12 ne sont que des répétitions techniques. Les études restent exploratoires, et l'option incrémentale est opt-in tant que ce test et les adversariaux de reprise n'ont pas passé.
