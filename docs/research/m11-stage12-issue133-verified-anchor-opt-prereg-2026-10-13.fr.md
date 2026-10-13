# Issue #133 / M11-OPT1 : audits SQL complets redondants (préenregistrement)

Date : 13 octobre 2026. **Ce document est écrit avant toute modification du mécanisme M11** et avant tout résultat d'optimisation.

## Source, base et mécanisme de coût

Branche `exp/m11-stage12-atomic-paid-index-20261013`, base source `452059a70b1eb3ffff6bc7293eeeee041af81591` (PR #140, empilée sur PR #139). Rapport profil H30 : `docs/research/m11-stage12-issue133-profile30-results-2026-10-13.fr.md` : **120 appels complets `SQLiteLifeLedger.audit` pour 30 pas**, 27-28 secondes cumulatives sur deux Python, vérifications canoniques répétées de 3570 événements H30. H120 a achevé deux vies de 120 pas avec journal identique entre Python et 2 épisodes en attente, mais demeure coûteux (224,60/338,38 secondes).

L'objectif n'est **pas** de diminuer le nombre d'événements à auditer ni la fréquence d'enregistrement SQLite. Un audit complet recalcule encore tous les liens SHA-256, les identités canoniques et le statut terminal des occurrences. Un scan O(1) de l'ancrage de génération **ne constitue jamais** un substitut de vérification après crash.

## Hypothèse et modification autorisée

Les quatre audits SQL complets actuels ont lieu (1) avant l'intention M11, (2) dans `begin_intent`, (3) dans `commit_generation`, et (4) après `COMMIT`. Les audits (2) et (3) peuvent être remplacés **seulement dans le flux qui possède une attestation récente d'audit complet de cette même connexion** par des vérifications sous `BEGIN IMMEDIATE` de l'identité, génération, statut, state_hash, bytes de l'état, journal_count, journal_head, owner roster et présence exacte de l'intention. Les changements intervenus sur les occurrences historiques, même avec ancrages inchangés, doivent rester détectés par un audit complet *après* `COMMIT`, **avant toute publication du candidat privé**. Un crash après commit mais avant ce deuxième audit sera contrôlé par la vérification intégrale obligatoire lors de `cold_recover`.

Le fallback public `begin_intent` et `commit_generation` sans attestation fraîche conserve intégralement les anciennes vérifications. L'attestation est liée à l'objet retourné par `audit()`, à l'unique connexion M11 et à l'intention précise ; l'attestation est consommée une fois, invalidée sur toute exception et jamais sauvegardée dans le journal ni exposée à I0.

## Critères préenregistrés

- Minimum **deux** audits SQL complets par pas M11 réussi (début et fin), contre quatre. Mesurer les appels via cProfile H30 sur Python 3.11 et 3.12, dans le même contexte que le profil de référence; ne pas confondre temps cumulatifs avec portions exclusives.
- Aucun changement des événements, hashes de journal, choix cognitifs et physiques, état des propriétaires, génération, sommeil, `w_C=0`, P-42 100 UC/pas et 600 UC/période, P-43, SQLite `synchronous=FULL`, politique de six passes, taille de lot 6, terminalité ou droit de reprise.
- Vérifier toutes les matrices de crash réel `os._exit` M11/Stage12, h privé puis commit SQL, décès irréversible, parité WAL historique, restauration froide au pas 31, audits read-only et corruption SQL des anciennes occurrences.
- Injecter des altérations SQL sur `state_bytes`, `state_hash`, `journal_head`, `causal_occurrence.canonical_bytes` *entre* les ancrages en utilisant un accès direct adversarial ; refuser l'état final et **ne pas publier** de candidat après détection. Tester le refus d'une ancienne attestation, d'un autre objet, d'une seconde réutilisation d'intention et le fallback complet.
- Exécuter à horizon bref d'abord, puis un comparatif H30 avec profiles bruts retenus; H120 et H600 ne sont pas déclenchés automatiquement. Un gain de temps non démontré est rapporté comme inconclusif et non artificiellement positif.

## Sécurité et critères de décision

Une absence de preuve de détection d'une corruption dans la fenêtre intermédiaire, une modification des journaux ou une reprise d'une vie incertaine => **NO-GO** et retrait de l'optimisation. Une corruption introduite *après* le dernier audit initial peut n'être décelée qu'à l'audit final : c'est acceptable **uniquement si elle empêche la publication du candidat et sa récupération froide**. Aucun relâchement normatif sans validation opérateur. PR #140 demeure en brouillon, PR #139 ouverte, issue #133 ouverte.
