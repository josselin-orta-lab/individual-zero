# I2 : etat de developpement, 31 octobre 2026

**PROPOSAL ONLY / NOT REGISTERED / NOT EXECUTABLE / SCIENTIFIC GO NOT ESTABLISHED.**

- **G0 I1 PARTIAL** : reference source au SHA `1e19f02db14b64a35f8bb014d69cc061f311002c` ; branche d'archive non protegee et archives M11 historiques non auditees publiquement par un tiers.
- **G1 REVIEW_REQUIRED** : revue architecturale/scientifique et contrats de coordination des proprietaires d'etat toujours ouverts (#662).
- **G2 prototypes isoles** : continuite des intentions, provenance/UC via ports synthetiques, reconstruction des candidats, Competition, revue Action Control, banc SQLite cognitif unifie v4 uniquement (modes v1/v2/v3 supprimes). Nouvelle `lifecycle_external_witness.py` : audit en lecture seule confrontant une tete locale v4 au **dernier** etat revendique par un port independant. Detecte les anciennes copies et bifurcations seulement si la fraicheur et l'authenticite du port sont garanties. Voir [LIFECYCLE_EXTERNAL_WITNESS.md](LIFECYCLE_EXTERNAL_WITNESS.md).
- **G3 NOT_ESTABLISHED** : pas de vraie source M11 signee, autorite de naissance/mort physiologique, Scheduler UC ou WorldBody raccorde. Le temoin de tests est en memoire, **non independant et non signe** ; aucune preuve de non-resurrection globale ni de COMMIT distribue. Aucun controle moteur vivant.
- **G4-G6 NOT_STARTED** : aucun protocole I2 confirmatoire final, vie, cohorte, promotion ou preuve de gain adaptatif.

I1 reste seul actif dans `config/engine-registry.json`, I2 n'a aucun point d'entree. Aucune politique alimentaire, Q, memoire ou donnee historique I1 ne devient la naissance d'I2. **Toute `WitnessAudit` conserve `resumption_authorized=False` et `motor_authority=NONE`, meme si les preuves concordent.**

- **G2 laboratoire fichier (31/10)** : `operator_file_witness.py` propose une projection append-only cote operateur, `flock`, HMAC-SHA256, CAS sur tete et relecture froide interprocessus (voir [OPERATOR_FILE_WITNESS.md](OPERATOR_FILE_WITNESS.md)). Le test negatif montre que le rollback complet du fichier reste possible et indetectable sans ancrage independant. Ce composant n'est pas un service M11, ne signe pas avec une cle de confiance externe et ne donne jamais de droit moteur/reprise. CI a verifier sur SHA de PR ; G3 reste `NOT_ESTABLISHED`.

- **G2 integration crash boundaries (31/10)** : tests `tests/i2/test_operator_file_witness_lifecycle.py` interconnectent seulement la base `CognitiveCycleFixture` v4 et la garde operateur fichier ; processus Python distincts et sorties `os._exit` apres COMMIT terminal ou ancre. Refus attendu `UNANCHORED` si SQLite terminal est en avance, `STALE` sur vieille copie et inspection sans droit de reprise quand les tetes concordent. Ce n'est PAS une transaction distribuee : proprietaires de physique/Scheduler/M11 absents, HMAC fichier modifiable et aucune autorite de naissance. CI ciblee doit passer sur SHA exact ; G3 `NOT_ESTABLISHED`.

- **H2 éligibilité temporelle G2 (31/10)** : `delayed_credit_study.py` teste, sans moteur, l'association entre préparation coûteuse et résultat vécu ultérieur, y compris contrôles neutres, inversés et adverses. Le scénario d'action incidente recevant du crédit démontre une limite causale explicite. Voir [DELAYED_CREDIT_STUDY.md](DELAYED_CREDIT_STUDY.md). Ni TD/Q, ni Scheduler, ni preuve de causalité, ni naissance ou promotion ; G3 `NOT_ESTABLISHED`.

- **H2 episodes apparies G2 (31/10)** : `compare_matched_outcomes` et les tests `test_matched_outcomes.py` contrastent deux observations de meme vie et meme contexte subjectif declare, avec une unique preparation differente, sans Oracle, Q, UC reelles ni droit moteur. Les confusions par contextes caches, ordre des episodes et auto-selection restent ouvertes. Attribution causale `NOT_ESTABLISHED`, G3 `NOT_ESTABLISHED` ; cf. `DELAYED_CREDIT_STUDY.md`.

- **H2 prospective hors echantillon G2** : le module `delayed_credit_study.py` fige une hypothese issue d'episodes historiques avant d'inspecter des consequences posterieures distinctes ; `test_prospective_heldout.py` inclut des resultats adverses, essais anciens, falsification et preuves d'emission non verifiees. Port d'emission synthetique : aucune autorite M11, aucun vrai changement de decision ni gain scientifique. G3 `NOT_ESTABLISHED`.

- **H2 calibration prospective G2 (31/10)** : `OutcomeFeedbackMemory` est un état de recherche pur, immuable, borné à 16 observations, mis à jour seulement après score hors échantillon et attestation d'émission synthétique. Une conséquence adverse peut inverser la prochaine prévision, mais un contrôle prouve que cette adaptation peut aussi se tromper. Aucun propriétaire M11/UC/TD/Q ni droit moteur, G3 `NOT_ESTABLISHED`.

- **H2 Competition payé G2 (31/10)** : un adaptateur `PaidFeedbackValuationPort` lit les erreurs de prédiction passées seulement après la facturation intégrale synthétique des candidats dans la transaction SQLite existante, sans créer de nouvelle base. Tests pour l'avis, le veto, la sous-dotation et le rollback des unités fractionnaires. Aucune mémoire M11 réelle, aucun débit Scheduler vivant ni publication physique ; G3 `NOT_ESTABLISHED`.

- **G2 frontière preuve physique (31/10)** : `verify_lived_physical_correspondence` impose une concordance explicite et deux ports de preuve déclarée (effet committé et observation personnelle après effet). Toute transition terminale, avis seul ou décalage identitaire/chronologique est refusé. Les doubles ne prouvent pas M11/WorldBody ; aucun acte moteur ni apprentissage vivant, G3 `NOT_ESTABLISHED`.

- **H2 chaîne physique G2 (31/10)** : le calcul de crédit peut désormais être conditionné à une suite ininterrompue d'effets physiques déclarés et d'observations subjectives, avec refus des doublons, ruptures, terminaux et conséquences inconnues. Tests purement synthétiques ; aucune attestation WorldBody/M11, aucun droit moteur, G3 `NOT_ESTABLISHED`.

- **Correction G2 physique (31/10)** : le garde de crédit H2 permet les actions sans changement physique et les retours à un état antérieur ; ces phénomènes ne sont pas des restaurations de vie en eux-mêmes. Le rejeu d'un commit/admission et une rupture chronologique restent interdits. Preuves de test seulement, G3 `NOT_ESTABLISHED`.

- **G2 garde émission H2 (31/10)** : l'adaptateur Competition réclame l'attestation synthétique du retour de calibration lui-même, et non seulement celle de la prévision historique. Échec : rollback local intégral UC/événement, aucun avis moteur. G3 reste `NOT_ESTABLISHED`.

- **G2 intégrité mémoire H2 (31/10)** : émission et évidence Competition sont liées à l'empreinte canonique de la mémoire complète et non à sa seule moyenne/version. Tests de substitution d'historiques équivalents numériquement. Empreinte locale non signée, G3 `NOT_ESTABLISHED`.

- **G2 fenêtre H2 longue durée (31/10)** : après seize retours, fenêtre glissante de 16, compteur cumulatif et tête de chaînage locale; la prédiction reste accessible. Tests au-delà du plafond et garde anti-rejeu dans la fenêtre. Pas de stockage authentifié M11, ni preuve globale anti-rollback. G3 `NOT_ESTABLISHED`.

- **G2 contrat de transition H2 (31/10)** : `feedback_transition_contract.py` valide le couple ancien/nouveau snapshot H2 et sa chaine avant un futur COMMIT unique. Les tests ciblent CAS perime, rejeu, changement d'identite et tetes falsifiees. Aucun branchement SQLite de cette memoire n'est encore realise : G3 `NOT_ESTABLISHED`.

- **G2 garde de score H2 (31/10)** : le contrat de transition rejette maintenant les scores hors échantillon contrefaits, incohérents, dupliqués ou déclarant des privilèges M11/moteur. Cette PR ne modifie pas le schéma SQLite : l'insertion atomique de H2 avec les UC et les événements reste non établie, et exige une évolution de schéma/rejeu étudiée séparément.

- **Refonte sans modes anciens (31/10)** : un seul contrat cognitif/contrôle/terminal synthétique v4, origine et ports obligatoires. Relecture des bases v1/v2/v3 interdite, pas de migration. La mémoire H2 n'est pas encore dans ce COMMIT ; G3 `NOT_ESTABLISHED`.

- **Nettoyage du noyau I2 (31/10)** : les trois transactions SQLite autonomes historiques (intention, Competition et garde Action Control) et leurs suites dédiées ont été supprimées. Le cycle v4 contient désormais lui-même les fonctions de sérialisation et de rejeu requises ; plus aucun import d'un ancien banc transactionnel. Les mécanismes purs, H2 et les témoins expérimentaux restent disponibles. G3 toujours `NOT_ESTABLISHED`.

- **Consolidation documentaire G2 (31/10)** : documents du mode cognitif v1 et modèle CI inerte retirés ; contrat v4 et plan de tests alignés sur la CI existante. Nouveau test structurel interdisant un second import SQLite dans les modules I2. Les travaux H2 et témoins sont conservés ; G3 reste `NOT_ESTABLISHED`.
