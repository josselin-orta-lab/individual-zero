# A2.23b : reçu subjectif né activé, conservation M-11 et frontière de confiance du capteur

**Préenregistrement le 15 octobre 2026, avant instrumentation A2.23b.** Branche de la [PR #179](https://github.com/josselin-orta-lab/individual-zero/pull/179). L'épreuve A2.23a précédente a validé seulement la conservation M-11 des reçus hérités de Stage3 avec `subjective_goal_agency=False`. Le critère normatif de provenance de l'agence subjective était donc **INCONCLUSIVE** : aucune amélioration rétroactive des critères A2.23a n'est autorisée.

## Objet et hypothèse vérifiable

A2.23b crée de **nouvelles vies Stage12 réellement autonomes et mortelles** dont la naissance fixe `subjective_goal_agency=True`, `m11_sqlite_custody=True`, `wal_path=None`, une identité de vie unique et la configuration UC du service d'agence. Elle ne modifie ni Stage12Runtime, ni Stage3, ni M11. Les reçus `perceptual_capture` enrichis (`stage12-first-person-cue-v1`) doivent provenir du chemin existant `Stage3Runtime._perceptual_capture_receipt` et devenir durables dans **le journal et l'état M-11 d'une seule génération**. Aucune truth Oracle, aucune intervention du banc et aucun nouveau WAL ne doit être livré à l'individu.

## Cohorte technique fixée avant code

Quatre configurations spatiales réellement distinctes `141 → (8,8)`, `142 → (12,8)`, `143 → (16,8)`, `144 → (20,8)`, chacune avec une source d'eau locale deux cellules à l'est (les autres paramètres physiques/vécus sont ceux de la fixture de Stage12). Chaque cellule est strictement intérieure à la grille 32×32. Ce sont 4 configurations spatiales déterministes, **pas 4 seeds aléatoires indépendantes de comportement**. Pour chacune, injecter `os._exit(76)` à six frontières natives M11 (`after_intent`, `before_private_execution`, `after_private_execution`, `before_sql_commit`, `after_sql_commit`, `after_publication`). **24 naissances autonomes mortelles et 24 processus tués**, sans jouer deux fois une commande lors de la reprise.

Attendus : **16 intentions pendantes** (génération 0, capture non committée, `cold_recover` interdit) et **8 générations valides** (génération 1, exactement un reçu enrichi du pas 1, lié au même `attempt_ref` que la clôture, avant `step_closed`, et empreinte/count conformes à M11). Le témoin de position reflète exactement la configuration spatiale de naissance. Le service d'agence est activé *à la construction* et son contrat UC appartient à la configuration canonique ; ne pas simuler un jugement `self` à la main. Sur les 8 vies valides, relancer `cold_recover` avec la **même** factory née activée, puis exécuter un nouveau pas vivant et vérifier le reçu enrichi au pas 2 sans retour au mode historique. La reprise ne rejoue jamais une commande précédente. La matrice principale contient donc **24 exécutions physiques privées attendues** : 8 dans des candidats interrompus avant COMMIT, 8 effectivement committées avant crash, 8 continuations post-crash. Les 8 autres processus tombent avant l'exécution privée.

## Attaques et contrôles négatifs

- **Post-journal, 32 essais :** pour chaque archive validée avant reprise, proposer quatre dossiers externes falsifiés (coordonnée, `attempt_ref`, `capture_t_monde`, voisinage de la capture). L'auditeur compare des bytes canoniques `perceptual_capture` à ceux d'une archive M11 ouverte et auditée ; toutes les substitutions doivent être refusées. Ne pas considérer une simple comparaison d'objets Python comme une preuve cryptographique.
- **Mauvaise identité de naissance, 8 essais :** une factory Stage12 de vie ou de position différente doit être refusée par M11 au cold recovery.
- **Compromission pré-journal, 4 vies distinctes supplémentaires :** dans un **processus de test uniquement**, substituer une sortie de `SymbolicPerception.capture` avant émission de `perceptual_capture` (coordonnée faussée, sans modifier `WorldBody.position`), puis laisser M11 committer. Résultat négatif prospectif : M11 peut enregistrer un reçu cohérent, mais sa position est fausse par rapport à la cause physique réelle tenue par l'évaluateur. **4/4 devraient illustrer que M11 n'authentifie pas un capteur compromis avant enregistrement**. Tout échec d'exécution doit être publié comme échec ou INCONCLUSIVE, jamais corrigé par des seuils a posteriori.

## Verdicts

T1 : 24/24 crashs M11 réels, répartition 16/8, pas d'accès à une ancienne vie lorsque pending ; un seul émetteur et propriétaire.
T2 : 8/8 reçus enrichis physiques distincts au premier pas, avec bon `t_monde`, identité, commande/closure et projection de 4 voisins ; aucun champ Oracle.
T3 : 8/8 reprises froides avec la même identité/contrat de naissance, progression à une **nouvelle** génération 2 et second reçu enrichi. Pas de réécriture de la première occurrence.
T4 : 32/32 post-journal falsifications et 8/8 erreurs d'identité rejetées, mécanisme de preuve délimité.
T5 : quatre contrôles négatifs pré-journal acceptés ou limitation rapportée honnêtement ; ne jamais interpréter le reçu comme preuve de vérité physique ni de cause.
T6 : Python 3.11 et 3.12 répètent les mêmes cas. Pas de verdict de conformité sur 600 pas.
T7 : seules la documentation, les scripts de recherche et les workflows peuvent changer. Zéro nouveau WAL ou UC, aucun changement d'Action Control, mortalité, Oracle, Stage9/DC-05, détecteur 2+2/12, ni MVP v1.3.1. **Aucune paire GA-06** imputable à ce banc.

**Conclusion conditionnelle :** un PASS établit seulement la conservation *d'un reçu subjectif émis par une instance Stage12 authentiquement configurée au départ* dans la transaction M11 et sa continuité après une reprise autorisée. Ni la véracité perceptive contre un capteur compromis, ni l'agence causale passée, ni la responsabilité alimentaire distale, ni la révision subjective ne deviennent prouvées. Stage12 reste **PARTIAL** ; issue #110 **OPEN** ; réception opérateur absente. La décision normative sur l'agence proximale/distale doit précéder toute extension du jugement subjectif.
