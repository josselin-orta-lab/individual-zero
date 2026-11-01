# I2: current proposal status

**Snapshot:** 31 October 2026. **PROPOSAL_ONLY / NOT_REGISTERED / NOT_EXECUTABLE / NOT_BORN.** Confirm live source and checks at the exact SHA. The [full development ledger](STATUS_HISTORY.md) is historical and contains superseded v4 descriptions.

## Scientific and engineering gates

| Gate | Current interpretation |
| --- | --- |
| G0 / I1 baseline | I1 source was pinned for comparison; independent archive/M11 provenance audit and branch protection remain open, see [transition report](../../../docs/architecture/proposals/i2-transition-and-scientific-gates-2026-10-31.md) |
| G1 | Architectural and scientific review still required |
| G2 | Independent **synthetic** research fixtures and a local SQLite cognitive/H2 v5 cycle have been implemented and targeted software checks documented |
| G3 | **NOT_ESTABLISHED**: no independently authenticated living M11, UC Scheduler, physical WorldBody, birth or mortality authority |
| G4–G6 | **NOT_STARTED**: no I2 confirmatory study, living cohort or promotion |

## Current technical scope

- [Unified synthetic v5 cycle](COGNITIVE_CONTROL_UNIFIED.md): one local SQLite journal/transaction owner for intent, test UC, Competition/Action Control opinions, terminal seal and H2 feedback.
- [Delayed credit](DELAYED_CREDIT_STUDY.md) and [test plan](TEST_PLAN.md): artificial input ports and negative controls, **not** established live learning or causal attribution.
- [External witness](LIFECYCLE_EXTERNAL_WITNESS.md) and [file witness](OPERATOR_FILE_WITNESS.md): synthetic verification now rejects non-canonical JSONL and a locally moving SQLite head during inspection, but **cannot** prove independent authenticity, global anti-rollback or authorization to resume a life.
- [I2 contract](../engine.json) has **no entrypoints** and I2 remains absent from the active registry. No test fixture gains motor, physiological, recovery or scientific authority.

Latest G1-only proposal: [publication, anchoring and crash-boundary review](../../../docs/architecture/proposals/i2-publication-boundaries-g1-review-2026-10-31.md). This is a requested independent review, not a runtime implementation or promotion.

### Nouvelle vérification synthétique G2

Les fonctions `inspect_uncertain_cognition` et `inspect_uncertain_terminal` classent uniquement la présence locale d'un COMMIT SQLite v5 en lecture seule (`RECORDED_LOCAL_ONLY`, `ABSENT_LOCAL_ONLY`, `CONFLICT_LOCAL`). Elles ne donnent **aucun droit de rejeu, reprise ou action**, et n'attestent aucun effet physique, M11 ou ancrage externe. Voir [contrat de cycle](COGNITIVE_CONTROL_UNIFIED.md).

### Confrontation d'un COMMIT incertain à une tête externe (G2 uniquement)

L'adaptateur `uncertain_witness_inspection.py` confronte un diagnostic local à un port de témoin externe **injecté** ; les classifications `UNKNOWN`, `STALE`, `UNANCHORED` et `FORK` restent non autorisantes. Les témoins tests n'établissent ni M11 indépendant, ni effet WorldBody, ni droit de reprise ou de retry. Voir [audit externe](LIFECYCLE_EXTERNAL_WITNESS.md).

### G2 : borne externe déclarée pour le témoin

Le test `minimum_witness` refuse un témoin externe régressif (`STALE`), équivoque ou étendant un état terminal (`FORK`), **seulement si** une borne antérieure déjà vérifiée a été gardée indépendamment du rollback. Le projet ne fournit ni stockage indépendant, ni signature, ni preuve M11, ni droit d'action ou de reprise. Voir [audit du témoin](LIFECYCLE_EXTERNAL_WITNESS.md).

### G2 : réponse signée à défi et témoin synthétique

Les contrats `challenge_witness_contract.py` et `challenge_witness_adapter.py` spécifient et testent des enveloppes de témoin avec nonce, identité, fenêtre de validité et vérifications **injectées**. La borne `minimum_witness` est également transmise par l'inspection terminale. Il n'existe pas de fournisseur externe authentifié, ni de gestion persistante de nonce, ni de service de signature/de temps fiable ; les tests montrent un risque de rejeu avec nonce réutilisé. Ces diagnostics G2 n'autorisent **aucune naissance, action, reprise, ni promotion G3**. Voir [l'audit externe](LIFECYCLE_EXTERNAL_WITNESS.md) et le [registre historique](STATUS_HISTORY.md).

### G2 : non-réutilisation des défis dans une instance

L'adaptateur de témoin réserve et valide maintenant le nonce avant tout appel au transport, sous verrou interthreads. Une répétition ou un nonce malformé est refusé, et un échec réseau ne libère pas le nonce. Il s'agit d'un garde **volatile** uniquement : aucune garantie d'unicité après redémarrage ou entre processus, aucune source cryptographique indépendante ni M11 vivant. Les tests sont synthétiques et ne donnent aucune autorité motrice ni de reprise.


### G2 : registre de defis local durable (proposition)

Le composant `durable_challenge_source.py` reserve des defis avant transport dans un journal append-only distinct du SQLite cognitif v5. Tests de redemarrage, concurrence cooperative, corruption et permissions. Cette persistance est **locale et restaurable**, sans anti-rollback global ni preuve d'independance M11. I1 actif ; I2 sans naissance, moteur ou autorite de reprise.


### G2 : refus de perte partielle du registre de défis

L'initialisation de `durable_challenge_source.py` refuse les états partiellement absents ou vidés au redémarrage. La suppression simultanée du verrou et du journal reste un contre-exemple documenté ; elle ne peut être détectée sans autre domaine de confiance. Aucun droit moteur ou naissance I2.


### G2 : identité des fichiers du registre

Le laboratoire vérifie les inodes de ses fichiers de garde sous verrou et avant sortie, avec tests de substitution du verrou et du répertoire. Reste vulnérable aux remplacements cohérents avant la lecture et au rollback global. I2 reste inerte, G3 non établi.

### G2 : relecture locale après refus du témoin

`verify_fixture` réaudite désormais le journal local même si le fournisseur externe lève une erreur ou signale `STALE`, `FORK` ou `UNANCHORED`. Une modification concurrente ou un échec du second audit est classé `UNKNOWN`, sans reprise ni rejeu. L'inspection des COMMIT incertains refuse également les erreurs du second audit. Protection locale contre une course détectée, non linéarisable, aucune authentification M11 ni effet physique.


### G2 : controle du prefixe historique local

L'audit froid peut verifier une tete historique SQLite v5. `verify_fixture` compare ce prefixe a une borne precedemment verifiee declaree, refusant une divergence `FORK` meme quand la tete actuelle correspond au fournisseur. Aucun serveur independant ni preuve M11 n'est ajoute, aucune activation I2.

## Next authorized work

Review [architecture](ARCHITECTURE.md), [research hypothesis](../../../docs/architecture/proposals/i2-continuity-and-learning-contract-2026-10-31.md) and [promotion procedure](../../../docs/engineering/ENGINE_PROMOTION.md); close separately the genuine-world, independent custody and preregistered science gates. Do not instantiate an I2 individual.

All earlier G2 iterations and their provenance are retained **verbatim** in [STATUS_HISTORY.md](STATUS_HISTORY.md). Their older schemas or planned tasks are not current contracts.
