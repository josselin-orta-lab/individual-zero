# I2 : architecture candidate autonome

**Statut actuel : G2 `TESTED_SYNTHETIC`, I2 `PROPOSAL_ONLY`, non enregistrée et non exécutable.** Il existe des composants cognitifs et un cycle SQLite **de test** ; il n'existe ni Lab/WorldBody vivant, ni runtime I2, ni identité née.

Chaque génération possède ses propres modules, runtime, Lab, UC, mémoire, contrôles et contrats. Aucun import de `i1lab` comme moteur I2. Le champ `parent: I1` indique une filiation scientifique, jamais une dépendance d'exécution. Norme obligatoire : [ADR-0001](../../../docs/decisions/ADR-0001-strict-generation-autonomy.md).

## Sources normatives et état courant

- [Contrat de recherche I2](../../../docs/architecture/proposals/i2-continuity-and-learning-contract-2026-10-31.md) : proposition G1, non revue indépendamment.
- [Cycle cognitif v4](COGNITIVE_CONTROL_UNIFIED.md) : unique propriétaire SQLite synthétique du débit UC, de l'intention, Competition, Action Control et du terminal.
- [Étude H2](DELAYED_CREDIT_STUDY.md) : apprentissage et crédit différé **expérimentaux**, pas de politique motrice prouvée.
- [État actuel](STATUS.md) : portes G0 à G6, blocages, inventaire et liens vers les expériences.

Les anciens modes et les propriétaires transactionnels séparés ne sont plus supportés. Aucun héritage de données de vie, migration silencieuse, naissance ou activation I2 n'est autorisé.
