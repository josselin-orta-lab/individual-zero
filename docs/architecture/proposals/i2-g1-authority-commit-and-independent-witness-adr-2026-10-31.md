# I2 / G1 : autorite de generation, COMMIT et temoin independant (ADR propose)

**Statut : PROPOSED / REVIEW_REQUIRED, non accepte.** Analyse du `main` `edbb242565f5d5e7a553844c3c2da18e0722faa5` du 31 octobre 2026. Issues [#662](https://github.com/josselin-orta-lab/individual-zero/issues/662), [#664](https://github.com/josselin-orta-lab/individual-zero/issues/664) ; G0 [#661](https://github.com/josselin-orta-lab/individual-zero/issues/661). Cette note ne modifie ni la specification MVP v1.3.1 ni la politique des portes. **Aucune naissance, commande, experience ou promotion I2 n'est autorisee.**

## 1. Constat reproductible : carte des autorites reelles

Chemin recherche actuel, **inert** :

```text
Capture subjective revendiquee --[ObservationSource: double]--> IntentionContinuity
      -> reconstruction des options (sans autorite persistante)
      -> CompetitionPreview --[ValuationSource + UC synthetiques]-->
      -> ActionControlBoundary --[Current/Safety: doubles; revue SEULE]-->
      -> [AUCUNE admission motrice]  X  [WorldBody I2 absent]
                            |
                            v
           CognitiveCycleFixture v1/v2/v3 : SQLite de TEST
           (compte UC local, etats/enregistrements synthetiques)
                            |
                            v
             audit() -> lifecycle_external_witness.py
                      --[read_latest + verify_latest : double]-->
             inspection UNIQUEMENT, jamais reprise ni action
```

| Objet et source verifiee | Proprietaire / COMMIT effectif | Statut de preuve | Risque et suite |
| --- | --- | --- | --- |
| Identite/genese, `src/i2/engine.json` | I2 `proposal`, `entrypoints={}`; genese v3 **declaree par l'appelant** dans `lifecycle` | `TESTED_SYNTHETIC`, pas de naissance | Autorite de naissance et identite non duplicable absentes ; definir genesis authentifiee |
| Corps, inventaire, monde, RNG | **Aucun** owner vivant I2 / aucune publication physique | `BLOCKED` | Preparer WorldBody prive, comparer la parite physique, jamais muter avant COMMIT |
| Observation et provenance | `ObservationSource.verify` injecte, capture depuis `ObservationClaim` | `TESTED_SYNTHETIC` | Aucun lien prouve a la perception d'un meme individu vivant |
| Intention / options | `IntentionContinuity` en memoire + snapshot dans `cognitive_cycle_fixture.account`; candidats reconstruits | `TESTED_SYNTHETIC` | L'intention peut survivre, pas ses offres/seuils/admissions |
| Evaluation, Competition et debit | `CompetitionPreview` et `_LocalLedger` du banc SQLite unifie | `TESTED_SYNTHETIC` | Ni vrai Scheduler ni UC effectivement prelevees dans un moteur |
| Revue Action Control | `ActionControlBoundary` ; controle de fraicheur avant et apres la revue dans `CognitiveCycleFixture._process` | `TESTED_SYNTHETIC`; `REVIEWED_NOT_ADMITTED` | Pas de verrou physique entre controles et publication ; **aucun droit moteur** |
| Memoire, TD, sommeil, cognition complete | Uniquement transitions cognitives de banc ; pas de proprietaires I2 reels | `BLOCKED` | Inventaire exhaustif de tous les proprietaires avant integration |
| Journal / terminal | `cognitive_cycle_fixture.py` v3 : un fichier SQLite avec `identity/account/events/lifecycle` et chaine SHA ; `TerminalSource` injecte | `TESTED_SYNTHETIC` | Pas de M11 physique, signature, anti-rollback ni terminal physiologique |
| Tete externe | `lifecycle_external_witness.py` compare un rapport `audit()` a un `IndependentWitness` **simule en memoire** | `TESTED_SYNTHETIC` | Source independante, signature, derniere tete monotone et ancrage atomique absents |
| Stockage reel / instance courante | **Aucune** autorite unique I2 de generation complete | `BLOCKED` | Impossible de revendiquer G3/M11, de reprendre ou de publier un effet |

Inventaire des **quatre bancs SQLite autonomes** (ils ne constituent pas quatre owners autorises d'une vie) :

| Banc de recherche | Transaction locale effective | Politique proposee |
| --- | --- | --- |
| `intention_atomic_fixture.py` | `_process` : capture, cout UC d'intention, `account`, `events`, COMMIT | **Isoler pour reference** et tests de parite ; ne pas composer en runtime |
| `competition_transaction_fixture.py` | `review` : budget UC propre, preuve/avis et `events`, COMMIT | **Isoler pour reference** ; pas de second ledger de Competition |
| `action_control_custody_fixture.py` | `review` : budget UC propre, avis/veto et `events`, COMMIT | **Isoler pour reference** ; pas de ledger moteur independant |
| `cognitive_cycle_fixture.py` v1/v2/v3 | `_process` : intention + Competition + revue (v2/v3), un compte UC et un COMMIT ; `seal_terminal` : terminal + en-tete dans un second COMMIT local v3 | **Conserver uniquement comme banc de parite**, sans le promouvoir en owner vivant |

Les proprietes `sqlite3.connect(...mode=rw)`, `BEGIN IMMEDIATE`, `UPDATE account`, `INSERT INTO events`, `COMMIT` et `lookup` sont verifiables directement dans chaque fichier. Les v1/v2/v3 du dernier banc ne sont **pas** trois transactions d'un meme cycle ; ce sont des variantes de protocole de test. Le `seal_terminal` v3 est un evenement ulterieur, pas une transaction de physique reelle. `ActionControlBoundary` seul utilise des garde-fous ephemeres en memoire et ne doit pas remplacer la garde durable.

**Difference cruciale :** un COMMIT SQLite coherent *dans un banc* ne rend pas atomiques un autre banc, le Scheduler, la physique publique et un ancrage externe. `verify_latest()` pouvant repondre `True` dans un double n'authentifie rien. `MATCHED_OPEN_INSPECTION` reste `motor_authority=NONE`, `resumption_authorized=False`, `m11_authenticated=False`.

## 2. Decision architecturale proposee, **non approuvee**

**D1. Un seul proprietaire de generation courante par vie I2.** Inventaire explicite : identite/genese, etat du WorldBody (corps, ressources, inventaire, danger et cause de mort), RNG et sources de non-determinisme, Scheduler/UC, perception admissible, intentions, options transitoires, Competition, revue de securite, memoire/TD/sommeil, etat cognitif, journal causal, intentions en attente et terminal. Chaque champ mutable a un seul owner, une serialisation canonique et un schema/version. Les projections, caches, audits et temoins ne deviennent pas un deuxieme etat vivant.

**D2. Un seul debit UC normatif.** Un Scheduler possede le solde, facture avant l'operation correspondante dans une preparation transactionnelle et publie le meme resultat que les autres owners. Des devis de test ou les comptes des fixtures ne prouvent pas la depense reelle. En cas de refus/abandon avant effet externe, la politique de frais doit etre explicite, observable et identique apres une lecture froide ; pas de seconde facture sur accuse perdu.

**D3. Intentions et commandes separent les droits.** Une intention conserve sa causalite et une echeance, jamais le candidat, l'accumulateur, l'admission ou la commande. Competition conseille ; Action Control oppose un veto **frais** ; seul un futur owner d'admission independant peut lier une tentative unique a une capture courante, un cout, un etat physique et une generation. `REVIEWED_NOT_ADMITTED` signifie non executable. Aucune admission n'est implementee ici.

**D4. Preparations privees, zero correction arriere.** Une tentative d'action porte un `attempt_id` unique et un `pending_intent` durable **avant tout effet externe possible**. Preparer le nouvel etat physique sur une copie privee, avec lois et RNG identiques ; preparer et valider les owners, l'avis, l'admission fraiche et le terminal ; ne pas appeler une physique mutante publique sous pretexte qu'un `BEGIN IMMEDIATE` serait ouvert. Une transaction locale complete conserve etat/journal/UC/terminal coherents. Aucune copie ancienne ni prefixe non publie ne peut redevenir la vie courante.

**D5. Preuve d'ancrage externe obligatoire, mais ni magique ni motrice.** L'ancrage exige un temoin **reellement independant**, un registre de dernier etat monotone/anti-equivocation, une identite de service et de signataire, et un protocole de publication demontrant comment la generation est liee a l'etat physique unique. La preuve de signature, la fraicheur, l'independance operationnelle et le couplage transactionnel sont **quatre** obligations distinctes. Sans protocole reellement verifie, toute fenetre entre COMMIT local, confirmation externe et publication physique est une **incertitude bloquante**, non un probleme qu'un hash resout.

**D6. Terminal absorbant et recovery fail-closed.** Le terminal physiologique est une consequence appliquee une fois, journalisee integralement et fermee de facon durable. La lecture froide peut inspecter une vie morte, jamais relancer sa cognition. Une vie non terminale ne peut etre envisagee pour reprise que si la generation **complete, courante et unique** est authentifiee, sans pending ambigu, avec preuves externes coherentes et tous les owners verifies. Le resultat du temoin seul ne confere **jamais** cette permission.

## 3. Ordre de publication candidat, avec trous de preuve explicitement ouverts

1. **Capture** : authentifier vie, generation et source perceptive du meme individu. Refuser toute observation d'Oracle/Bench, toute capture stale, terminale ou etrangere.
2. **Reservation durable** : inscrire un identifiant de tentative idempotent, le `pending_intent` et l'etat de precondition, **avant** effet externe. Toute tentative sans reservation ferme l'acces physique.
3. **Preparation privee** : evaluer options et Competition avec UC effectivement allouees ; controler independamment l'admission et le veto sur la generation courante ; calculer la physique, la memoire, le RNG et l'eventuel deces sur copies privees.
4. **COMMIT canonique local** : ecrire d'une seule traite les owners complets, le debit normatif, l'evenement technique integral, le resultat physique et le terminal (ou son attente explicite). Un accuse absent n'autorise pas un second `WorldBody.apply`.
5. **Ancrage monotone externe** : une operation conditionnelle sur la tete/epoch precedente doit garantir unicite et detection de forks. **Une transaction locale et un appel reseau ne sont pas un COMMIT distribue** : crash avant/apres l'un ou l'autre = `technical_halt/UNKNOWN` jusqu'a preuve independante ; aucune reprise automatique ni publication/mutation supplementaire.
6. **Publication visible** : seulement le meme etat canonique dont la garde d'autorite a ete etablie ; l'etape suivante ne peut observer un brouillon. Si l'actuateur physique ne peut ni etre transactionnel avec la publication, ni cloture par fencing/idempotence prouvee, **stopper la conception ici**. Ne jamais inventer un resultat physique a posteriori.

L'ordre precis des etapes 4-5-6 reste **a arbitrer independamment**. Cette sequence est un ensemble d'obligations et de trous a fermer, **pas** un algorithme executable actuellement. Un stockage externe apres le COMMIT local laisse une extension non ancree ; un stockage externe avant le COMMIT local laisse une ancre sans etat local. Ni l'un ni l'autre n'autorise un `GO`.

## 4. Contrat minimal d'une preuve candidate (schema futur, pas implementation)

Pour chaque enregistrement, lier dans des **octets canoniques, versionnes et signes** au minimum : `protocol_version`, `authority_domain`, `engine_generation=I2`, `life_ref`, `genesis_ref`, `journal_schema`, `publication_generation`, `event_seq`, `last_physical_step`, `chain_head`, `state_digest`, `terminal` et `terminal_ref/step`, `previous_anchor`, `writer_epoch`, `lease_or_fencing_token`, `signer_key_id`, `journal_locator`, `proof/signature`. Les encodages, la racine de confiance, le domaine de signature, la rotation/revocation, les preuves de derniere tete et le fournisseur de stockage **restent a choisir apres revue des menaces**. Ne pas substituer un `proof_ref` textuel ou un hash SHA-256 a une signature.

Une seule vue atomique devrait produire **a la fois** l'enregistrement verifie et une preuve de sa derniere tete. L'API actuelle `read_latest` puis `verify_latest` est un **port de tests** ; sans liaison atomique a la meme revision elle est exposee au TOCTOU. Meme une preuve authentiquement signee peut etre perimee. L'invariant anti-equivocation exige un CAS/registre monotone de `(life,genesis,epoch,generation)` et la preuve publiable de tout conflit ; l'expiration d'un bail seule ne remplace pas le fencing d'un ancien auteur.

Interpretation de l'inspection future, **toutes sans autorite motrice ou de reprise** :

| Statut cible | Fait observable | Politique |
| --- | --- | --- |
| `MATCHED` | Toutes les tetes/versions identiques, preuve verifiee **et fraiche** | Inspection uniquement ; gates d'action et de recovery separes |
| `TERMINAL` | Dernier etat atteste mortel, fermeture absorbante | Inspection postmortem ; jamais `observe/act/resume` |
| `STALE` | Copie locale en retard sur la derniere tete attestee | Refus, pas de rollback ni relecture de prefixe comme actif |
| `FORK` | Meme generation/seq, tetes divergentes ou equivocation | Refus, geler auteurs et conserver les deux preuves |
| `UNANCHORED` | Local plus recent que la tete externe certaine | Refus, aucune nouvelle execution/retry |
| `UNKNOWN` | Temoin absent, signature fausse/inconnue, lecture non fraiche, I/O/lease ou couplage incertain | Fail-closed, preservation des preuves et diagnostic operateur |

Le code existant expose des erreurs et deux statuts `MATCHED_*_INSPECTION`; **il n'implemente pas** cette taxonomie future ni une attestation cryptographique.

## 5. Menaces, tests discriminants et preuves attendues (non executes)

| Injection / contre-exemple | Rejet ou observation indispensable | Preuve encore manquante |
| --- | --- | --- |
| Copie SQLite entiere pre-mortem, terminal signe plus recent | `STALE/TERMINAL`, zero action | Derniere tete distante issue d'un service reel |
| Signature valide mais enregistrement ancien, ou reponse cachee | `UNKNOWN/STALE` meme si signature valide | Lecteur monotone et preuve de fraicheur liee a la meme revision |
| Deux auteurs, genesis concurrente, meme seq et tetes differentes | `FORK` et preuve de conflit, aucun gagnant arbitraire | CAS/epoch/fencing independant et scenario multi-processus |
| Copie reecrite avec toute la chaine SHA recalculee | Refus par contradiction avec l'ancre externe | Ancre independante et etat complet de publication |
| Cle inconnue, rotation, revocation, signataire compromis | `UNKNOWN`, aucune cle locale auto-acceptee | Gouvernance des cles et audit externe |
| Crash `os._exit` avant/apres reservation, prepare, debit, insertion d'evenement, COMMIT | Pas de debit/effet fantome ; tentative non rejouee | Proprietaire unique et vraie physique privee |
| Crash apres COMMIT local et avant publication temoin, ou inversement | `UNKNOWN/UNANCHORED`, pas de replay | Protocole de resolution externe auditable |
| Crash apres attestations, avant exposition memoire/WorldBody | Etat courant complet ou technical halt, jamais effet double | Liaison atomique/fencing publication-physique |
| Accuse perdu, timeout, partition ou indisponibilite de temoin | Consultation en lecture seule ; aucune reexecution physique | Recu idempotent et vue actuelle authentifiee |
| WAL tronque/corrompu, disque plein, I/O ou deux processus concurrents | Refus sans restauration d'etat publie | Tests de pannes 3.11/3.12 sur vraie instance |
| Veto, admission stale, UC insuffisantes, ressource disparue | Aucune commande, aucune naissance implicite | Garde motrice independante et Scheduler reel |
| Deces physique puis `observe/act/resume` depuis tout fichier | Refus permanent, conservation du journal complet | Autorite terminale exterieure et tests multi-copies |

Mesurer sur le futur proprietaire unique : **nombre d'owners**, transactions par pas, taille du journal, latence mediane/p95, cout CPU/UC reel, reprises bloquees et classes de pannes ; comparer a la baseline du meme scenario sans masquer les depenses. Executer des tests par **processus/fichiers independants**, pas seulement des doubles en memoire. Les tests actuels de `tests/i2/` valident des invariants **synthetiques**, pas ces scenarios systeme.

## 6. Alternatives et criteres de revue G1

- **Rejet de principe** : assembler les quatre fixtures comme un runtime, conserver quatre journaux UC, transformer une revue en admission, comparer deux hash locaux, utiliser une signature seule, confondre l'archive Git I1 avec l'archive M11, ou creer une cinquieme fixture SQL.
- **A etudier independamment** : (a) une seule autorite de stockage tenant etat physique et journal, avec attestation externe a publication gardee ; (b) protocole transactionnel/fencing avec service de garde distinct et mode de reprise incertaine explicite ; (c) abandon du couplage moteur si l'independance ne peut etre prouvee. Etudier privileges, operations, couts, latence, pannes et tests de falsification **avant** de choisir backend ou cryptographie.
- **Tests de parite avant simplification** : conserver les fixtures historiques comme references, mesurer classes d'invariants couvertes, puis supprimer/archiver seulement les doublons dont l'equivalence est demontree. Aucune deletion dans cet ADR.

**Questions pour revue independante #662/#664 :** Qui atteste la genesis et la mort corporelle ? Qui detient le fencing de l'ecrivain courant ? Quelle operation lie atomiquement tentative physique, debit UC, journal et tete externe ? Comment resoudre une tete externe plus recente qu'un COMMIT local sans ressusciter ? Quel contrat de frais et de conservation M-12 ? Quels tests `os._exit` *refuteraient* l'architecture ? Les droits pour proteger l'archive I1 et assurer la custody M11 restent ouverts en #661.

**Point d'arret :** G1 reste `REVIEW_REQUIRED` tant que ces choix ne sont pas revus par une autorite independante. G0 `PARTIAL` (branche I1 non protegee), G2 `TESTED_SYNTHETIC`, G3 `NOT_ESTABLISHED`, G4-G6 `NOT_STARTED`. Aucune modification de `src/i1/`, `src/i0/`, registre, lois physiques ou preuves A1. A1-C `NO_GO`, L3 `NOT_ESTABLISHED`, A2-R `0/96`.

**References normatives :** [contrat I2 G1](i2-continuity-and-learning-contract-2026-10-31.md), [portes de transition](i2-transition-and-scientific-gates-2026-10-31.md), [M-11/M-12 MVP v1.3.1](../reference/en/mvp-specification-v1.3.1.md), [note M11 SQLite](../../operations/m11-sqlite-transactional-custody-v1.3.1.md), [inspecteur v3](../../../src/i2/docs/LIFECYCLE_EXTERNAL_WITNESS.md).