# Issue #133 : vérificateur autonome de WAL indexé et matrice os._exit

**Date** : 13 octobre 2026. **Version du test** : `07ad5ab0a78678ab737f15760c95df27006ffed0` sur la PR #139. Le protocole de crash a été préenregistré au commit `b00bb92cd716df9a20e0df395678e8bd1d62cae8`.

## Reproduction et indépendance de la preuve

[Workflow ciblé #38378958987](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38378958987) : **SUCCESS** Python 3.11 et Python 3.12. Artefacts conservés tels quels : `11803065357` (3.11) et `11802217228` (3.12). Vies réelles non reprises, 3 interruptions par interpréteur par `os._exit(76)`, sur le premier lot d'indexation du pas 14, tarif de retrait de 2 UC. La chaîne SHA-256 et la structure canonique sont valides dans les six WAL, et les résultats sont identiques entre interpréteurs.

Nouvel outil : `scripts/audit_stage10_index_wal.py --wal <path>`. Il ne charge ni I0, ni Oracle, ni Bench, ni WorldBody. Il recalcule le hash canonique de toutes les entrées, l'unicité des IDs, l'ordre exact `index_maintenance_charged → version_activated → index_retired`, les lots/UC et les pas physiques inachevés. Codes de sortie : 0 pour WAL complet et apparié (*intégrité seulement*), 2 si corrompu, 3 si intact mais incomplet ou non coordonné. `may_resume_stage12=false` et `recovery_certified=false` sont toujours explicites, même si l'audit passe. Une archive complète saine de 600 pas passe en code 0, sans prétendre autoriser une reprise.

| Point de sortie | WAL SHA-256 intégral | h publié ? | Index retiré ? | Résultat vérificateur | Reprise certifiée ? |
| --- | --- | --- | --- | --- | --- |
| Avant h | VALIDE | Non | Non | Code 3 : triplet incomplet + pas ouvert | NON |
| Après h avant retrait | VALIDE | Oui | Non | Code 3 : triplet incomplet + pas ouvert | NON |
| Après retrait | VALIDE | Oui | Oui | Code 3 : pas physique toujours ouvert | NON |

La matrice a été renforcée pour appeler ce vérificateur après chaque crash (commit `07ad5ab`), et exiger le code 3 plutôt que valider seulement les hachages. Aucun ancien WAL n'est modifié, aucune vie n'est réanimée et aucun `step_closed` n'est ajouté artificiellement.

## Conclusion scientifique et logicielle

- **Débit et facture P-42** : les deux mondes H600 restent techniquement conformes dans les versions du test 600 pas précédemment auditées (index 295/299 et 296/299 contre 242/299 et 238/299 pour scan intégral, 6044/6264 UC contre 10827/9791). Il s'agit d'une hypothèse de stabilité locale soutenue, pas d'une validation de vie longue générale.
- **Auditabilité de la maintenance** : 61 et 58 triples appariés et respectivement 295 et 296 UC de retrait attestés par monde, reproduits octet à octet entre Python 3.11 et 3.12.
- **Crash brutal** : la préservation du WAL est démontrée à trois frontières réelles. Une activation h durable dépourvue du retrait indexé est possible et détectée. C'est une **limitation architecturale encore ouverte** ; il n'existe pas de récupération Stage12 certifiée qui puisse réparer cet état.
- **Action suivante sans changement normatif** : évaluer une enveloppe de commit propriétaire commun ou une stratégie d'arrêt irréversible et de récupération *uniquement avec preuve complète* compatible avec les clauses M11, plutôt qu'une restauration opportuniste depuis un ancien export. Ajouter des tests fail-closed de désynchronisation/corruption de l'index sans augmenter les UC, le sommeil ou `w_C`.

**Décision** : techniquement validé pour débit et audit read-only WAL, **NON VALIDÉ pour une reprise de Stage12 après crash**. Laisser #133 OPEN et PR #139 non fusionnée avant décision opérateur. `w_C=0` inchangé, norme du MVP v1.3.1 inchangée.
