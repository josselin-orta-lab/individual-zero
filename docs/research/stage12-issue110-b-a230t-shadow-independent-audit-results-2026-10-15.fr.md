# A2.30-T-archive : contrôle indépendant de la science S-shadow sur sources gelées

**15 octobre 2026.** Préenregistrement T-archive **après résultat S-shadow mais avant code** au commit `c8bb93736b14adfc008a7bc6f86f654862b1e404`. Les mêmes entrées et les résultats étaient connus ; **aucune nouvelle vie, monde ni action physique n'a été créée** par T. [CI #38741660739](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38741660739) : SUCCESS Python 3.11/3.12 ; résultat recalculé identique. Code auditeur autonome `scripts/audit_stage12_issue110_b_a230t_shadow_archives.py`, qui n'importe **ni S-runner, ni Stage6/Simulator/FrozenTableEquipment, ni WorldBody, ni Oracle**.

Le témoin télécharge les deux archives scientifiques **immuables du run S #38740664255**, recontrôle les 3 SHA-256 originaux et leur égalité octet à octet. Il reconstitue pour les 64 mondes actifs tous les hashes des exemples, les chaînes d'observation, les commandes effectivement enregistrées, les 24 terminaisons et l'absence d'action postmortem ; pour les 8 mondes passifs il recalcule les indices de ressource/obstacle.

Pour chacune des **56** recherches Shadow Stage6, un **algorithme indépendant** reconstruit la table des seuls exemples antérieurs du même monde, vérifie le SHA du corpus temporel, énumère les commandes **uniquement disponibles dans l'état observable à l'instant t**, calcule les hashes exacts des `state × command` et constate **zéro première arête prédictible pour 56/56**. Le planificateur réel S était appelé avec horizon3 et but 65 ; le témoin archive démontre que `incomplete_model` est cohérent au niveau racine **sans simuler l'ensemble des plans**, précisément parce que toutes les racines examinées sont indisponibles.

**Résultats identiquement recalculés :** 72 mondes, 196 pas, 44 ingestions, 24 terminalités, 8 paires ingestion aux perceptions strictement équivalentes, 4 attentes différenciantes avec coût physique, 4 secondes ingestions encore indiscernables, 8 contrastes de retrait physique préengagé et 56 recherches aux racines inconnues.

Tests adversariaux PASS : refus d'une observation SHA altérée, d'un événement du futur injecté dans l'historique, d'une première arête connue falsifiée, d'une intervention environnementale masquée, d'une conséquence corporelle falsifiée, d'une action postmortem et d'identifiants dupliqués. Ce contrôle établit la **cohérence interne des octets archivés**, **pas** l'application indépendante de la physique ; cette dernière est testée dans U.

Les résultats sont originaux à S, **pas des données scientifiques supplémentaires T**. Les travaux parallèles de la [PR #190](https://github.com/josselin-orta-lab/individual-zero/pull/190) et de la [PR #192](https://github.com/josselin-orta-lab/individual-zero/pull/192) restent des protocoles distincts ; ne pas requalifier cet audit en étude T-food de #192.

**T-archive PASS technique ; Stage12 PARTIAL ; issue #110 OPEN ; A2.30 PARTIELLE, PR #191 DRAFT.**
