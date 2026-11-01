# I2 / G1 : delta de revue des proprietaires et de la publication (1 novembre 2026)

**Statut : DOSSIER DE REVUE / REVIEW_REQUIRED, non approuve.** Snapshot inspecte : `main` `d426248be734d5250012a1e1688c4d79c80feaa2` (1 novembre 2026). Ce texte prepare une revue **architecturale ET scientifique independante** des issues [#662](https://github.com/josselin-orta-lab/individual-zero/issues/662) et [#664](https://github.com/josselin-orta-lab/individual-zero/issues/664). Il ne change ni l'ADR-0001 acceptee ni le contrat de transition approuve ; il ne constitue pas une approbation G1, un programme executable ou une preuve G3. Le registre declare **I1 actif**, et `src/i2/engine.json` declare I2 `proposal`, `entrypoints={}`, `NOT_REGISTERED_NOT_EXECUTABLE`.

## 1. Pourquoi ce delta est necessaire

La note [G1/ADR historique du 31 octobre](i2-g1-authority-commit-and-independent-witness-adr-2026-10-31.md) etait exacte pour son snapshot `edbb242...` mais decrit **quatre bancs SQLite**, les variantes `v1/v2/v3` et une API externe `read_latest` + `verify_latest`. Ces representations **ne sont plus celles du code a ce snapshot**. Garder le document historique sans delta risque de faire examiner une architecture deja retiree, ou de confondre succes locaux et autorite M11.

| Objet examine | Etat du code au SHA de reference | Ce qui demeure NON etabli |
| --- | --- | --- |
| Proprietaire de cognition | `src/i2/modules/cognitive_cycle_fixture.py` : **un seul banc SQLite v5**, compte UC synthetique, intentions, avis Competition, revue Action Control, H2 et terminal synthetique ; anciens proprietaires transactionnels retires | Aucun proprietaire unique d'une generation **physique** complete, ni Scheduler vivant |
| Tentative COMMIT incertaine | `inspect_uncertain_cognition` lie capture **et requete exacte** (`open/observe`, reference semantique, preuve, TTL) ; releve historique local seulement | Aucun droit de reessayer une action ou de reprendre une vie ; effets WorldBody non verifies |
| Temoin et comparaison | `lifecycle_external_witness.py` : `read_verified_latest` **atomique demande** par contrat v2, controles locaux et prefixe ; tous les ports de confiance sont injectes | Pas de service independant, de preuve de derniere tete linearizable ni de signature authentifiee |
| Nonce et garde operateur | `challenge_witness_*`, `durable_challenge_source.py`, `operator_file_witness.py` : controles locaux / faux verifier, HMAC et garde fichier du meme operateur | Rollback de domaine complet, lecteur non cooperatif, signataire et anti-equivocation independants |
| Frontiere moteur | `src/i2/engine.json` n'a ni naissance ni runtime ; aucune commande motrice, `motor_authority=NONE` | WorldBody I2, admission et consequence physiques, mort physiologique irreversibles non implementes |

Ces observations portent sur les **sources** ; les suites CI G2 passees sur leurs SHA sont des validations logicielles synthetiques, pas une experience I2 et pas une decision scientifique. La relecture du document historique ne doit ni ressusciter les bancs retires ni faire creer un nouveau proprietaire concurrent.

## 2. Frontieres et invariant de securite a faire accepter

Distinguer **trois domaines**, aujourd'hui non relies par une garantie de publication :

- **Domaine individuel futur** : une identite/genese, un proprietaire de generation courante et son inventaire exhaustif : corps/ressources/inventaire, RNG, pas physique, Scheduler et solde UC, capture subjective, intentions, Competition, revue/veto, memoire/H2, journal causal, intention en attente et terminal. La *preparation privee* d'un candidat n'est **pas** sa publication. **Ce domaine vivant n'existe pas dans I2.**
- **Domaine ancre externe futur** : dernier enregistrement monotone de chaque vie, auteur/fencing, revision precedente, signatures avec politique de revocation et preuve de fraicheur, provenance materielle du service. La garde operateur HMAC et les faux temoins G2 ne remplissent pas ce role.
- **Domaine effet public futur** : le WorldBody effectivement observe par le prochain pas, avec compteur de generation et un effet physique au plus par tentative. Si ce domaine est separe de la transaction, la concordance d'un hash ou un double audit avant/apres ne prouvent pas un effet exactement une fois.

Les invariants de revue sont : **S1** une seule generation canonique et un seul proprietaire UC ; **S2** zero effet public avant reservation durable et autorisation motrice fraiche ; **S3** zero double effet et zero nouvelle UC pour une tentative incertaine ; **S4** aucune intention ne conserve gagnant, commande, veto favorable ou admission d'un pas precedent ; **S5** terminal absorbant, sans nouveau pas ni reprise apres mort ; **S6** aucun ancien prefixe ni etat I1 ne peut redevenir la generation active ; **S7** source first-person, aucune information cachee Oracle/Bench dans le choix ; **S8** apres une incoherence d'ancre/projection, blocage plutot que resolution imaginaire.

**Important :** S1 a S8 sont des obligations **proposees**, pas des proprietes verifiees sur une vie I2. G1 doit preciser le point de linearisation, le proprietaire de chaque champ et qui constate leur violation.

## 3. Fenetres de panne a falsifier (pas des tests vivants executes)

| Trace | Rupture imposee / contre-exemple | Observation acceptable pour G1, a imposer en G3 | Statut actuel |
| --- | --- | --- | --- |
| C0 | Naissance et ancien identifiant I1 reutilise, ou deux genesis identiques | Refus d'identite ; aucun etat ne nait avec memoire importee | Pas de naissance I2 |
| C1 | Capture non first-person, perimee, ou changement de but/sommeil | Intention expiree/suspendue ; candidats reconstruits ; pas de commande heritee | G2 tests locaux seulement |
| C2 | UC indisponibles ou veto/safety change entre evaluation et publication | Aucune commande, charge normative coherente selon politique explicite ; nouvel arbitre au pas suivant | Revue/veto et UC synthetiques seulement |
| C3 | Crash avant reservation durable, puis lors de preparation privee | Aucun effet public et aucun debit fantome ; inspection locale sans retenter l'acte | Pas de reservation physique |
| C4 | Crash ou perte d'accuse avant/apres COMMIT **local** | Inspecter la tentative et tous les owners ; aucune reexecution physique ; `UNKNOWN` si incertitude | Relecture v5 G2 seulement |
| C5 | COMMIT local durable, ancre externe encore ancienne | `UNANCHORED`/suspension ; aucun nouvel effet ou resume par confiance dans SQLite seul | Compareur avec temoin injecte |
| C6 | Ancre externe avancee, copie locale ancienne ou bifurquee | `STALE/FORK`, geler les auteurs ; jamais recuperer une copie pre-mortem | Minimum et ascendance locale testees G2 |
| C7 | Ancre concordante, crash avant exposition WorldBody | Prouver par **recu d'effet** et fencing que l'etat exact est publie au plus une fois, sinon `technical_halt` | **Aucune preuve** |
| C8 | Effet public applique, accuse d'application perdu puis redemarrage | Ne jamais rappeler `WorldBody.apply` sans preuve durable d'idempotence ; sinon arret technique non reversible | **Aucune preuve** |
| C9 | Deux ecrivains et CAS concurrents, lease ancien encore actif | Un auteur fence ; ancien auteur incapable de publier malgre son lease ; conserver trace du conflit | Aucun fencing vivant |
| C10 | Mort terminale, restauration de SQLite et du temoin local avant la mort | Lecture postmortem ou arret ; impossible de rendre l'identite vivante via rollback | Anti-rollback independant absent |
| C11 | Disque plein, WAL incoherent, rollback de tout le dossier, signature revoquee | `UNKNOWN/technical_halt`, pas de correction automatique ni recuperation de prefixe | G2 teste des cas locaux, pas la custody distante |

**Critere de refutation commun :** s'il existe une seule execution ou la meme tentative applique deux consequences physiques, ou dans laquelle une ancienne vie/ancienne generation recouvre l'autorite apres terminal/rollback, la proposition ne satisfait pas G1/G3. Aucune simple sortie `MATCHED_*_INSPECTION` ne remplace une preuve de causalite physique.

## 4. Arbitrages que la revue independante doit trancher AVANT G3

| Decision | Question testable, actuellement ouverte | Artefact demande au relecteur |
| --- | --- | --- |
| R1 : publication | WorldBody fait-il partie **du meme owner durable** avec projection pure/idempotente, ou existe-t-il une transaction/fence prouvee avec un effet externe ? Qui est l'unique point de linearisation ? | Sequence de publication revue, trace de C7/C8 et rejet explicite de toute hypothese d'atomicite fictive |
| R2 : attente | Comment un `pending_intent` est-il reserve puis resolu a froid lorsque l'accuse d'une etape manque ? Qui possede `technical_halt` et son impossibilite de reprise ? | Invariants d'etat, classes d'`UNKNOWN`, preuve de non-retry par crash-injection |
| R3 : UC / acteurs | Quels champs mutables et debit UC normatif appartiennent a **une meme generation** ? Qu'advient-il des frais d'un cycle refuse ou interrompu ? | Registre complet des owners, contrat de debit et preuve d'absence de second compte |
| R4 : ancre | Qui opere le temoin **hors domaine**, detient la derniere tete, CAS/epoch/fencing, les cles et la revocation, et prouve les lectures fraiches ? | Modele de confiance, preuve de non-equivocation et test contre rollback coherent |
| R5 : H1 | Quel evenement first-person renouvelle/expire une intention ? Le sommeil, la disparition d'une ressource et le changement de but annulent-ils une capacite motrice cachee ? | Contrat de transition d'intention + tests negatifs de veto, TTL, reconstruction et UC |
| R6 : H2/H3 | Quelle preuve personnelle relie action admise, consequence et feedback *sans future leak* ? Comment compter non-offre, budget, abstention, veto, action admise et resultat physique ? | Contrat de provenance causale, controle negatif/inverse et observables non confondus |
| R7 : mortalite | Quelle preuve relie le terminal physiologique et le sceau M11, et rend l'ancien vivant irrecuperable meme sous substitution de disque ? | Revue d'echec C10, garde independante de naissance et mort |
| R8 : science | Quels preregistrements et controles independants sont indispensables avant tout essai vivant ? | Avis science distinct sur H1-H3, biais, comparateurs et mesures ; G4 ne demarre pas ici |

**Issues de decision autorisees :** `ACCEPT_G1_ARCHITECTURE` uniquement **par revue independante documentee**, `REVISE_G1`, ou `REJECT_G1`. **Ce dossier porte `REVIEW_REQUIRED` et ne peut pas enregistrer un `ACCEPT` par son seul merge.** Aucun outil, test unitaire ou nombre de PR ne vote a la place du relecteur.

## 5. Dossier minimal a exiger pour toute decision

- Identification des relecteurs **architecture et science**, de leur independance vis-a-vis de l'auteur, des versions et SHA precis examines ; decision et objections signees ou verifiables, pas seulement un check GitHub.
- Choix R1-R8 et raisons du refus/acceptation des alternatives ; toute garantie manquante classee `UNPROVEN`.
- Pour chaque C0-C11, lien vers un futur test, un observateur independant et la condition de falsification. Tant que les artefacts G3 n'existent pas, noter `NOT_EXECUTED`.
- G0 #661 reste `PARTIAL` : code archive != custody originale M11 ni analyse confirmatoire independante. A1-C = `NO_GO` cible ; A2-R = `NOT_EXECUTED 0/96` ; L3 I1 `NOT_ESTABLISHED`. Ces resultats ne certifient pas I2.
- Conditions de sortie : **pas de constructeur vivant, de nouvelle identite, de motor admission, de promotion ou d'activation** sur la base de cette seule proposition.

## 6. Handoff et fichiers de reference

**Point de depart code :** `src/i2/modules/cognitive_cycle_fixture.py`, `uncertain_witness_inspection.py`, `lifecycle_external_witness.py`, `challenge_witness_contract.py`, `operator_file_witness.py`, `src/i2/engine.json`. Tests G2 pertinents : `tests/i2/test_single_transaction_owner.py`, `test_uncertain_commit_inspection.py`, `test_uncertain_witness_inspection.py`, `test_pinned_witness_minimum.py`, `test_operator_file_witness.py`. Les tests G2 **ne sont pas des preuves** des C7-C11 physiques.

**Sources de politique (ne pas modifier retrospectivement) :** [ADR-0001](../../decisions/ADR-0001-strict-generation-autonomy.md), [contrat H1-H3](i2-continuity-and-learning-contract-2026-10-31.md), [frontieres de publication](i2-publication-boundaries-g1-review-2026-10-31.md), [transition I1-I2](i2-transition-and-scientific-gates-2026-10-31.md), [M11/M12 reference](../reference/en/mvp-specification-v1.3.1.md).

**Suite admissible :** soumettre ce delta et les contre-exemples a une **vraie** revue G1 independante (#662), avec menace de custody #664 et archive G0 #661 en parallele. En cas de revue positive seulement, proposer un G3 minimal **separe**, un seul owner de generation I2, en commençant par les preuves de publication physique/terminal et les tests adversariaux. Ne pas reintroduire les fixtures historiques, importer `i1lab`, demarrer de cohortes ou confondre la simulation avec une vie.
