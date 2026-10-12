# Stage 12 / issue #133 : résultats de calibration P-40, 2026-10-12

**Statut** : étude exploratoire rétrospectivement dépouillée, essais techniques **PASS**, hypothèse de calibration **partiellement soutenue**. Aucun changement du MVP normatif, aucune adoption d'un poids autre que le **w_C=0 provisoire** approuvé, aucune réception opérateur de Stage 12, aucune validation scientifique confirmatoire.

## Antériorité, source et audit

- [Préenregistrement avant la première exécution](stage12-issue133-calibration-prereg-2026-10-12.fr.md), commit `6e20623787b2b792981853d1628670182a548d79`.
- Code **effectivement exécuté et figé** : `e6bee4480af356429cb81fdc42a272f62a30a61d` ; dépôt [PR #137](https://github.com/josselin-orta-lab/individual-zero/pull/137).
- [Actions #38312011974](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38312011974) : 16 jobs Stage 12 SUCCESS, dont les deux campagnes à 12 vies, les tests six passes, les tests d'eau et les deux essais distincts de 600 pas. [CI rapide #38312011838](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38312011838) : SUCCESS.
- [Archive Python 3.11](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38312011974/artifacts/11774882982) ; SHA-256 de l'archive ZIP téléchargée : `2135697eedc2d0533f844579e6111971dfd6911b8a5ccd336fc111817a42fc40`.
- [Archive Python 3.12](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38312011974/artifacts/11775092385) ; SHA-256 de l'archive ZIP téléchargée : `a824f7d67f7557150c56a64998d7b8b4d18ce8cced1bd0f26cf37c728247c897`.
- Audit indépendant **après** l'exécution et distinct des unités d'analyse : lecture stdlib des deux ZIP, vérification des **24** empreintes SHA-256 des exports, WAL == export + séparateur, **chaîne causale entièrement recalculée**, unicité/ordre des événements et 80 clôtures/actions appliquées par vie ; chaque publication h est reliée à **six checkpoints validés, tarifés et ordonnés** du même identifiant ; correspondance des références d'épisodes publiés et de `consolidated_episode_refs` finaux ; gains hydriques liés à `stage12_goal_progress_followup`. Résultats et hashes des 12 configurations **identiques entre Python 3.11 et 3.12**.
- La procédure d'audit hors vie a été écrite *après* les observations : elle confirme les invariants techniques mais **ne transforme pas cette campagne exploratoire en étude confirmatoire préenregistrée**.

Les 12 configurations d'une version réalisent 12 naissances mortelles autonomes et 960 **vrais pas physiques** (maximum fixé à 80/vie), soit 24 vies et 1920 pas physiques sur deux versions Python. 0 erreur d'audit, 0 vie remplacée, 0 décès, 24 arrêts opérateur. **L'unité expérimentale reste la vie**, avec deux mondes déterministes et aucune graine tenue à l'écart ; reproduire le même traitement sous 3.12 est une reproduction technique et ne double pas le nombre de traitements indépendants.

## Résultats mesurés par vie, identiques sous Python 3.11 et 3.12

Les valeurs de sommeil sont le **nombre de commandes `dormir` parmi 80 actions** ; les autres actions sont `se_deplacer` et, dans le contrôle positif, une commande `boire`. Toutes les conditions emploient une vraie politique de consolidation six passes et les coûts UC P-42.

| w_C | `dormir` / 80, équipement de référence | `dormir` / 80, eau entraînée | Checkpoints h, référence / eau | Publications h, référence / eau | Épisodes non consolidés finaux, référence / eau | Eau bue (contrôle positif) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **0,00** | 22 | 20 | 11 / 10 | 1 / 1 | 38 / 39 | 1 |
| **0,05** | 31 | 26 | 15 / 13 | 2 / 2 | 37 / 38 | 1 |
| **0,10** | 39 | 39 | 19 / 19 | 3 / 3 | 36 / 37 | 1 |
| 0,20 | 76 | 76 | 26 / 26 | 4 / 4 | 35 / 35 | 1 |
| 0,35 | 77 | 77 | 26 / 26 | 4 / 4 | 35 / 35 | 1 |
| 0,50 | 77 | 77 | 26 / 26 | 4 / 4 | 35 / 35 | 1 |

Détails :
- Dans le monde d'eau contrôlé, **une seule commande `boire` est effectivement admise et appliquée au pas 3 pour chaque poids**. L'audit de progression préenregistrée vérifie au pas 4 un gain corporel réel de **20 à 60**. Cela démontre un contrôle logiciel positif avec modèle d'équipement *entraîné hors de la vie*, **pas** l'apprentissage autonome dans un monde nouveau.
- Le monde à équipement de référence n'exécute aucune commande `boire` et ne reçoit aucune preuve de progression du besoin d'eau. Son modèle de transition est connu comme incomplet (issue distincte [#136](https://github.com/josselin-orta-lab/individual-zero/issues/136)).
- **Aucun événement `stage10_consolidation_work_deferred`** dans les 12 journaux par version. Chaque checkpoint h montre un débit P-42 strictement positif ; chaque publication est précédée des six passes exigées, dans le bon ordre.
- Le compteur `episodes_in_memory_end` inclut les épisodes déjà consolidés ; **seules les références effectivement publiées** comptent comme consolidées. Le stock non consolidé demeure très élevé (35 à 39 épisodes par vie). Quatre publications h ne démontrent pas la qualité de mémoire ni la durabilité de son utilité.
- Les publications h sont parfois plus nombreuses avec poids 0,20 ou 0,50 **parce que l'individu dort presque toute sa vie**. Une hausse de h ne suffit donc pas à proclamer un meilleur comportement ou un meilleur compromis.

## Verdicts explicites selon préenregistrement

**H133-B1 : SUPPORTED dans ce banc déterministe.** Le poids de consolidation est un levier important du sommeil : 0,05 et 0,10 produisent des proportions intermédiaires, tandis que 0,20 et plus aboutissent à 95 % de pas dormis ou davantage. Aucune relation monotone universelle n'est inférée au-delà de ce banc.

**H133-B2 : PASS des invariants techniques, utilité INCONCLUSIVE.** Les six checkpoints tarifés et les publications h sont réellement présents ; il ne s'agit pas d'un simple comptage de commandes dormir. Mais le stock non consolidé reste important, et aucune amélioration comportementale attribuable à la qualité d'un souvenir consolidé n'est établie.

**H133-B3 : SUPPORTED pour la capacité à répondre à l'eau dans le contrôle positif ; généralisation INCONCLUSIVE.** Boire et gain d'eau sont conservés avec chacun des six poids testés dans le seul monde entraîné. Le monde témoin ne boit pas, ce qui reflète aussi l'équipement incomplet. Ce contrôle ne mesure pas le transfert à un monde inconnu.

**H133-B4 : PASS ciblé des budgets/journaux/arrêts observés.** 24/24 vies terminent 80 pas en respectant WAL et chaîne d'événements ; les publications sont techniquement cohérentes et aucun report de passe P-42 n'a été enregistré. L'atomicité en cas de crash réel **M-11/Stage12** reste hors de cette campagne.

### Application mécanique de la règle prospective de décision

Deux et seulement deux **poids strictement positifs** remplissent les critères de *candidat de développement* fixés avant les données :

- `w_C=0,05` : 31/80 et 26/80 pas dormis ; 2 publications h et 1 boisson exécutée avec gain d'eau.
- `w_C=0,10` : 39/80 dans les deux mondes ; 3 publications h et 1 boisson exécutée avec gain d'eau.

Les poids `w_C≥0,20` **échouent** au seuil maximal préenregistré de 50 % de sommeil. Ils ne constituent pas des candidats sur ces critères, même avec quatre publications h.

**Le profil de développement reste `w_C=0,00` par décision opérateur.** Ne pas sélectionner après coup 0,05 ou 0,10 en production, même si un meilleur compromis potentiel apparaît. Le 0,05 maximise la fraction éveillée parmi les poids positifs testés, tandis que 0,10 consolide davantage : il manque des critères d'utilité sémantique et de capacité à couvrir une demande cognitive, pas uniquement un comptage de h.

## Travaux encore nécessaires et décision sur issue #133

Conserver **issue #133 OPEN** tant qu'une décision opérateur de poids et une couverture durable des mécanismes ne sont pas justifiées. Avant de déplacer la configuration de développement au-delà de w_C=0 :

1. Comparer `0,00`, `0,05`, `0,10` sur des **vies plus longues**, mondes et graines réellement différents, en préenregistrant l'utilité de mémoire et les conséquences d'un stock croissant d'épisodes non consolidés.
2. Mesurer l'effet des versions h sur un comportement *après* leur publication, et non seulement leur nombre. Contrôler la gestion des urgences, les dommages, le manque de sommeil et les budgets UC plus contraints.
3. Préserver les contrôles négatifs de l'équipement, le lien besoin → plan admissible → boisson et le journal indépendant. Ne jamais donner à I0 une vérité d'Oracle ou une récompense inventée.
4. Garder distinctes l'issue #110 (attribution subjective réellement vécue), l'issue #136 (équipement acquis durant la vie) et la persistance atomique Stage12/M-11, qui ne sont **pas** résolues par cette campagne.

**Décision finale de cette EXP : techniquement achevée et reproductible ; deux candidats à approfondir ; aucun GO scientifique global ni réception opérateur du Stage 12.** Le MVP normatif v1.3.1 et les résultats négatifs antérieurs restent intacts.
