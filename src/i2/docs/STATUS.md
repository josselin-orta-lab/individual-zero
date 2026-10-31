# I2 : etat de developpement, 31 octobre 2026

**PROPOSAL ONLY / NOT REGISTERED / NOT EXECUTABLE / SCIENTIFIC GO NOT ESTABLISHED.**

- **G0 I1 PARTIAL** : reference source au SHA `1e19f02db14b64a35f8bb014d69cc061f311002c` ; branche d'archive non protegee et archives M11 historiques non auditees publiquement par un tiers.
- **G1 REVIEW_REQUIRED** : revue architecturale/scientifique et contrats de coordination des proprietaires d'etat toujours ouverts (#662).
- **G2 prototypes isoles** : continuite des intentions, provenance/UC via ports synthetiques, reconstruction des candidats, Competition, revue Action Control, banc SQLite cognitif unifie v1/v2 et origine/terminal synthetiques v3. Nouvelle `lifecycle_external_witness.py` : audit en lecture seule confrontant une tete locale v3 au **dernier** etat revendique par un port independant. Detecte les anciennes copies et bifurcations seulement si la fraicheur et l'authenticite du port sont garanties. Voir [LIFECYCLE_EXTERNAL_WITNESS.md](LIFECYCLE_EXTERNAL_WITNESS.md).
- **G3 NOT_ESTABLISHED** : pas de vraie source M11 signee, autorite de naissance/mort physiologique, Scheduler UC ou WorldBody raccorde. Le temoin de tests est en memoire, **non independant et non signe** ; aucune preuve de non-resurrection globale ni de COMMIT distribue. Aucun controle moteur vivant.
- **G4-G6 NOT_STARTED** : aucun protocole I2 confirmatoire final, vie, cohorte, promotion ou preuve de gain adaptatif.

I1 reste seul actif dans `config/engine-registry.json`, I2 n'a aucun point d'entree. Aucune politique alimentaire, Q, memoire ou donnee historique I1 ne devient la naissance d'I2. **Toute `WitnessAudit` conserve `resumption_authorized=False` et `motor_authority=NONE`, meme si les preuves concordent.**

- **G2 laboratoire fichier (31/10)** : `operator_file_witness.py` propose une projection append-only cote operateur, `flock`, HMAC-SHA256, CAS sur tete et relecture froide interprocessus (voir [OPERATOR_FILE_WITNESS.md](OPERATOR_FILE_WITNESS.md)). Le test negatif montre que le rollback complet du fichier reste possible et indetectable sans ancrage independant. Ce composant n'est pas un service M11, ne signe pas avec une cle de confiance externe et ne donne jamais de droit moteur/reprise. CI a verifier sur SHA de PR ; G3 reste `NOT_ESTABLISHED`.
