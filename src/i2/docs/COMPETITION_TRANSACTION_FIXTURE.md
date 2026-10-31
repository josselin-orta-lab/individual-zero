# I2 : publication transactionnelle d'un avis Competition (banc de recherche)

**31 octobre 2026. G2 logiciel. Aucun moteur I2, aucune naissance, aucune preuve L3.**

`src/i2/modules/competition_transaction_fixture.py` est un **banc SQLite synthétique** qui réutilise le contrat existant `CompetitionPreview` sans modifier ses critères d'arbitrage ni choisir une politique d'allocation UC. Il ne partage aucun état avec un I1 vivant et ne remplace ni `Scheduler`, ni `M11`, ni `Action Control`.

## Problème borné

Le prototype `CompetitionPreview` protège les captures déjà traitées par des ensembles **en mémoire** et facture via un port de lot externe. Après arrêt du processus, une même capture pourrait être traitée à nouveau, et un débit externe réussi mais non publié reste incertain. Un SHA d'observation ou une validation de type ne résout pas ce problème. Le présent banc vérifie ce qui est possible **lorsque le budget synthétique et l'avis partagent réellement la même base**.

## Contrat réalisé

1. `CompetitionTransactionFixture.create(...)` crée, sans écraser, une base dédiée à une identité **synthétique** et à une capacité UC de test. Son port `frame_source.verify` doit répondre exactement `True` avant d'ouvrir une transaction ; les tests emploient un faux propriétaire non M11.
2. `review(frame)` ouvre `BEGIN IMMEDIATE`, rejoue intégralement le journal, refuse le pas ancien ou la capture déjà consommée, puis réutilise `CompetitionPreview.review` avec un `BatchUCLedger` **local à la même connexion SQLite**. Le débit du lot, l'avis, les évaluations, la nouvelle balance et le hash de journal sont confirmés ensemble par un unique `COMMIT` ; aucun aperçu n'est disponible avant ce commit.
3. Les preuves de valeur proviennent d'un second port `evidence_source.evaluate_batch`, dont la source doit rester first-person et **en lecture seule**. Les valeurs sont liées à chaque reçu UC et candidat ; les tests utilisent des tableaux synthétiques. Il n'existe aucune source de valeur apprise ni d'oracle alimentaire dans ce module.
4. L'avis conserve les statuts `ADVISORY_ONLY`, `UNFUNDED`, `AMBIGUOUS`, `NO_POSITIVE_EVIDENCE`, `NO_CANDIDATES` de `CompetitionPreview` ; une liste incomplète ou falsifiée déclenche un rollback. Une capture `UNFUNDED` est consommée dans le journal avec coût nul et ne peut pas être relancée gratuitement.
5. Une panne injectée après débit, après évaluation ou avant `COMMIT` annule le budget et le journal locaux. En cas de perte de confirmation après `COMMIT`, `lookup(capture_ref)` fournit le reçu déjà publié, sans nouvelle évaluation. `reopen(...).audit()` relit le compte et **recalcule la décision avec le code Competition existant**, les reçus et valeurs archivés. Deux sessions concurrentes sont sérialisées par SQLite et l'unicité des pas/captures.
6. Le résultat `FixtureAdviceReceipt` ne possède ni commande, ni `winner`, ni admission, ni droit moteur ; son `motor_authority` vaut systématiquement `NONE`.

## Limites qui interdisent le branchement direct à I2 vivant

- La dépense n'est PAS celle du vrai Scheduler. La base ne rend atomiques **que ses propres UC synthétiques** ; aucun debit d'un service externe n'est protégé par le commit local.
- Une chaîne SHA-256 sans ancrage externe authentifié détecte des corruptions et falsifications *partielles*. Un attaquant réécrivant toute la base et tous les hashes peut la reconstituer. Ce n'est PAS l'authentification M11.
- `frame_source` et `evidence_source` sont des ports injectés. Un mock `True`, une référence de vie et un digest cohérent ne prouvent ni provenance première personne, ni séparation d'un Lab réel, ni budget payé.
- `reopen` ouvre uniquement un **banc scientifique existant**, jamais une vie interrompue ; aucune sémantique mortelle, sécurité physique, reprise après décès, contrôle moteur ou transition WorldBody n'est offerte.
- L'exigence du lot complet conserve le risque `UNFUNDED` observé dans #673 ; aucune stratégie partielle n'est choisie et aucune valeur/survie d'I1 n'est injectée.

## Reproduction et portes

```bash
python -m unittest discover -s tests/i2 -p 'test_*.py' -v
```

Les 25 tests supplémentaires couvrent en particulier la cohérence ACID, la concurrence, les fautes avant/après commit, le refus de relecture, les données corrompues ou partiellement réhashées, la neutralité de l'intention, les limites d'autorité et les abstentions. Le résultat local Python 3.13.5 comporte **168 tests réussis**. Les CI GitHub Python 3.11/3.12 doivent être **vérifiées sur le SHA exact de la PR** avant fusion ; le contrôle de proposition I2 doit rester `BLOCKED` (Lab/runtime absents).

**G0 partiel, G1 revue nécessaire, G2 banc de recherche, G3 vrai Scheduler/M11/Action Control NON ÉTABLIS, G4–G6 bloquées. I1 actif, I2 non enregistré/non exécutable.**
