# I2 : revue G1 proposee des frontieres de publication

**Statut : proposition a examiner, aucune autorisation G1/G3.** I1 reste actif et I2 non enregistre. Ce texte distingue des exigences futures des proprietes deja prouvees dans les tests G2.

## Proprietaires et ordre requis

1. **WorldBody prive (non implemente)** : preparer une consequence une seule fois sur un candidat detache. N'afficher aucune mutation physique publique avant la publication canonique. La preparation inclut besoins, RNG, Scheduler UC, memoire, cognition et statut terminal.
2. **Coordonnateur M11 unique (non implemente)** : verifier l'identite, le schema, le roster complet des proprietaires et une revision attendue ; enregistrer une intention durable avant tout effet non transactionnel. La validation doit lier et publier une seule generation, avec evenement causal et terminal si applicable, dans une transaction durable. Incertitude du COMMIT : lecture froide, jamais nouvelle execution de la commande.
3. **Ancrage externe independant (non implemente)** : CAS monotone sur une tete scellee et identite/genese, signature verifiable, revocation, anti-equivocation et anti-rollback externe. L'absence de preuve ou une tete locale avancee impose une suspension, pas une reexecution ni une restauration d'ancien etat.
4. **Projection publique (non implemente)** : publier uniquement le candidat exactement commite, sous protocole de fencing interdisant deux ecrivains, sans appliquer une seconde fois l'action. Apres crash entre COMMIT et publication, une resolution doit prouver la publication ou refuser la reprise ; un simple controle de hashes ne suffit pas.
5. **Mort (non implemente)** : terminal absorbe toute commande, naissance, restauration et continuation sur cette identite, y compris apres rollback de copies locales.

## Risques et controles adversariaux obligatoires

| Fenetre | Exigence | Preuve existante |
| --- | --- | --- |
| Avant COMMIT local | Aucune mutation publique, rollback des proprietaires prives | SQLite G2 synthétique seulement |
| COMMIT incertain | Audit froid et blocage de toute repetition | Test G2, pas de physique |
| COMMIT avant ancrage | Journal plus recent : UNANCHORED, jamais reprise | Comparaison G2 |
| Ancrage plus recent que copie locale | STALE, aucune copie ancienne selectionnee | Test G2 avec fournisseur injecte |
| Divergence a sequence egale | FORK, aucun gagnant arbitraire | Comparaison G2 |
| Changement local pendant lecture du temoin | UNKNOWN apres seconde lecture locale | Test G2 de la presente tranche |
| Ancrage coherent avant nouveau COMMIT | Aucune fenetre de publication garantie apres lecture | Non resolu |
| COMMIT avant effet public, crash ou double ecrivain | Fencing + acte exactement une fois ou arret technique | Non implemente |
| Terminal et rollback complet du temoin | Mort jamais annulable, ancrage hors domaine | Non implemente |

## Decision G1 demandee

Faire revoir independamment l'inventaire des proprietaires, l'ordre du protocole, les fenetres de crash et les impossibilites de transactions reparties. Ne pas promouvoir un simple double audit en verrou linearisable. L'inspection actuelle n'emporte jamais `motor_authority`, `resumption_authorized` ni `m11_authenticated`. Aucune naissance I2 avant revue G1, preuves G3 et approbation distincte. Ne pas importer le runtime I1 ni une identite historique.
