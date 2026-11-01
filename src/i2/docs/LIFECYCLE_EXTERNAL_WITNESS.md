# I2 : audit externe du journal v5 (proposition G2 uniquement)

**31 octobre 2026. Protocole de temoin v2, lecture seule, aucune naissance, aucune permission motrice et aucune preuve M11.**

Source : `src/i2/modules/lifecycle_external_witness.py`.
Tests : `tests/i2/test_lifecycle_external_witness.py` et `tests/i2/test_lifecycle_external_witness_integration.py`.

## Defaut traite

La PR #679 a ajoute un evenement terminal absorbant dans **un fichier SQLite de test**. Le rejouage et la chaine SHA-256 detectent des incoherences partielles, mais ne detectent pas a eux seuls une **ancienne copie SQLite valide** : une vie apparaitrait non terminale si l'on ne consulte que la copie realisee avant le scellage. Une reecriture integrale avec recalcul des hachages locaux reste egalement possible.

Le nouvel audit compare la sortie deja verifiee de `CognitiveCycleFixture.audit()` a la **derniere tete** revendiquee par un service externe et independant. Les champs compares sont : version du journal, identite de vie et origine declaree, numero d'evenement, dernier pas physique, tete de chaine, reference et pas terminaux. Toutes les comparaisons sont exactes et l'absence de temoin fait **echouer** le controle.

## Contrat avec un futur temoin independant

Le module **ne cree aucun service de garde**. Il exige un port `IndependentWitness` :

1. `read_verified_latest(life_ref, genesis_ref)` doit selectionner **et verifier dans une operation indivisible** la derniere revision monotone pour cette identite, et retourner un `LatestWitness` structurellement valide. Le port est une exigence contractuelle, sans implementation de service independant.
2. Le fournisseur doit verifier la signature, la confiance/revocation du signataire, la fraicheur, l'absence d'equivocation et le lien exact entre preuve et champs **sur la meme revision**. Toute indisponibilite ou erreur est classee `UNKNOWN`, sans recours au hash local. L'ancien couple `read_latest`/`verify_latest` est refuse afin d'eviter une course entre deux operations. Les tests injectent un double in-memory sans valeur de securite.
3. Le controle n'accepte ni un temoin plus recent que le journal local (ancienne copie), ni un journal plus recent que le temoin (publication non encore attestee), ni deux tetes divergentes au meme nombre d'evenements. La fermeture terminale doit coincider exactement.
4. `verify_fixture(fixture, witness)` exige le vrai banc `CognitiveCycleFixture` sur le contrat v5, effectue l'audit local **avant** de consulter le temoin, et produit uniquement une `WitnessAudit` en lecture seule. La comparaison pure `compare_audit(report, witness)` est exposée pour les tests de contrat ; un dictionnaire fourni arbitrairement ne prouve pas son origine.
5. La sortie porte toujours `motor_authority=NONE`, `resumption_authorized=False` et `m11_authenticated=False`, y compris lorsque le temoin concorde sur un etat ouvert. Le statut `MATCHED_OPEN_INSPECTION` **n'autorise aucune reprise**.

## Scenarios adversariaux

- Copie SQLite ouverte avant la cloture terminale, puis controlee contre la tete externe apres cloture : **refus pour copie ancienne**.
- Deux branches SQLite avec meme origine et meme numero d'evenements, mais des evenements terminaux differents : **refus pour bifurcation**.
- Depot local valide avec une extension non encore publiee chez le temoin : **refus**, sans essayer de synchroniser automatiquement ni de refaire une commande.
- Preuve absente, non authentifiee, d'une autre vie, d'un autre genesis, d'un autre schema, de mauvaise chronologie ou incoherente sur le terminal : **refus**.
- Controle d'un ancien journal ou d'un objet arbitraire : **refus avant tout port externe**.
- Correspondance parfaite en mode ouvert ou terminal : **inspection seule**, sans naissance, continuation, action ni debit UC.

## Limites de preuve et prochaines portes

- Le port reste **injecte et simule**. On ne demontre pas qu'une veritable source externe est persistante, independante, signee, recente ou non equivocable. Un faux service qui affirme une vieille tete valide annulerait cette protection.
- Les hachages locaux ne prouvent toujours ni la provenance physique, ni un evenement M11 authentifie. L'origine du banc est declaree par l'appelant et la mortalite est synthetique.
- La lecture externe et l'audit local ne constituent **pas une transaction distribuee**. La lecture seule ne protege aucun `open`, `observe`, `seal_terminal` ou effet sur WorldBody intervenant apres le controle. Un accord de tete ne signifie jamais que le vrai Scheduler/WorldBody peut etre relance.
- Un futur proprietaire M11 devra garantir la preparation privee de la physique, le registre complet des proprietaires (RNG, corps, besoins, Scheduler, memoire, cognition), le COMMIT atomique d'une generation, la cloture de deces, les bornes d'un etat `pending` et la resolution des commits incertains. Voir `docs/operations/m11-sqlite-transactional-custody-v1.3.1.md` pour les distinctions fondamentales.
- Le temoin devrait etre opere separement du fichier a auditer, avec preuve d'identite, anti-rollback monotone, regles de publication et audit externes. Sa creation, sa signature et sa reception independante restent **NOT_IMPLEMENTED**.

**G0 I1 PARTIAL ; G1 REVIEW_REQUIRED ; G2 inspecteur logiciel ; G3-Scheduler/M11/WorldBody NOT_ESTABLISHED ; G4-G6 NOT_STARTED.** Aucune connaissance I1 n'est importee, aucune naissance I2 n'a lieu et aucune conclusion L3 ne change.

Reproduction : `python -m unittest discover -s tests/i2 -p 'test_*.py' -v`.

## Diagnostics de refus typés (proposition G2)

`WitnessRefusal` (sous-classe de `ValueError`) distingue désormais `STALE` (copie locale dépassée), `UNANCHORED` (extension locale en avance), `FORK` (divergence à même séquence/terminal) et `UNKNOWN` (preuve absente, provenance invalide, identité étrangère ou schéma externe invalide). Les refus demeurent des exceptions **sans autorité de reprise ni moteur** ; ils ne sélectionnent aucun état gagnant et ne réparent aucune transaction. Les entrées locales incohérentes restent des `ValueError` d'audit. Le port témoin et sa preuve restent simulés, non signés et non indépendants. `MATCHED_*_INSPECTION` ne correspond jamais à une permission de reprendre une vie.

## Limite nouvelle version

Le changement de protocole v1 vers `i2-lifecycle-external-witness-proposal-v2` casse intentionnellement la compatibilite des temoins v1. L'appel atomique reste un **contrat demande au fournisseur**, pas une preuve que le fournisseur existe ou assure des lectures linearizables. Un double de test qui retourne un enregistrement choisi par l'appelant peut toujours produire une inspection `MATCHED` sans origine de confiance. Toute exploitation exige une revue independante et des preuves verifiables du fournisseur. Aucun effet sur Action Control, une vie ou le Scheduler.

## Inspection des COMMIT incertains avec ancrage (G2)

`uncertain_witness_inspection.py` rapproche en **lecture seule** une inspection de tentative SQLite v5 de la dernière tête vérifiée *revendiquée* par le port externe. Les contrôles locaux sont relus avant, pendant et après la consultation distante. `CONFLICT_LOCAL` refuse avant toute sollicitation du témoin ; un journal mouvant ou un port indisponible donne `UNKNOWN` ; une tête externe plus avancée donne `STALE`, une extension locale non ancrée `UNANCHORED`, une bifurcation `FORK`. Une correspondance peut décrire un COMMIT local retrouvé ou une absence seulement locale, jamais une reprise ou un droit de retry. Aucun lock distribué, ancrage réel, signer ou M11 authentifié n'existe. Les doubles de tests ne démontrent ni indépendance ni fraîcheur. L'inspection peut devenir périmée aussitôt retournée.

## Borne monotone externe optionnelle (G2)

`compare_audit` et `verify_fixture` acceptent maintenant `minimum_witness` comme ancien enregistrement **déjà vérifié et conservé hors du domaine de rollback**. Une révision externe inférieure à cette borne échoue `STALE`, une équivocation à séquence identique ou une extension d'un terminal déjà scellé échoue `FORK`. Les comparaisons assurent l'identité et la chronologie déclarées, mais ne prouvent pas l'ascendance cryptographique d'une tête ultérieure. Aucun mécanisme ne crée, ne signe ni ne conserve cette borne ici ; si l'opérateur restaure aussi la borne, la protection disparaît. Tous les diagnostics restent sans autorité motrice, de retry ou de reprise. G3 reste NOT_ESTABLISHED.

## Contrat de réponse signée à défi (G2)

`challenge_witness_contract.py` définit une enveloppe canonique de prétendue attestation avec nonce de 256 bits, identité d'autorité et de clé, durée de validité, enregistrement exact et signature opaque. Une politique de confiance injectée impose clé attendue, fenêtre temporelle et révocation ; un vérificateur de signature externe doit retourner strictement `True`. Les tests injectent seulement un faux vérificateur et ne prouvent pas une signature cryptographique. Le module ne fournit ni générateur de nonce, ni horloge fiable, ni registre de clés révocables, ni service monotone. **Le même défi peut être réutilisé par un appelant défectueux** : les tests démontrent explicitement cette limite, qui nécessite une protection du nonce chez l'autorité réelle. Même une signature cryptographique valide n'établirait pas à elle seule la fraîcheur du dernier état, l'anti-équivocation ou la survie à un rollback global. Ce contrat n'est pas raccordé à `compare_audit` et ne permet ni reprise, ni commande, ni naissance. G3 `NOT_ESTABLISHED`.

## Adaptateur challenge en lecture seule (G2)

`challenge_witness_adapter.py` relie l'enveloppe de la PR #724 au contrat `read_verified_latest`. Ses quatre sources sont injectees : generation du defi, horloge de confiance, transport et verification cryptographique. Il exige la meme identite vie/genese apres verification et transmet toute erreur afin que l'audit la classe `UNKNOWN`. Aucune cle, implementation cryptographique, fournisseur independant, protection persistante contre les nonces reutilises ni monotonie du service n'existent dans l'adaptateur. Les tests de replay de nonce sont intentionnellement negatifs. La borne `minimum_witness` est aussi desormais transmise par le chemin terminal de l'inspection des COMMIT incertains, qui refusait autrement de l'appliquer. Le code ne produit aucune autorite de reprise, de commande ou de naissance. G3 non etabli.

## Garde de non-rejeu des défis dans une instance (G2)

L'adaptateur réserve désormais chaque nonce hexadécimal de 256 bits dans un registre en mémoire protégé par un verrou **avant** tout appel au transport. Une répétition, une valeur malformée ou une réponse perdue ne déclenchent pas un second appel externe avec le même défi dans cette instance. Après échec du transport, le nonce reste consommé volontairement. Des tests couvrent valeur invalide, timeout et requêtes concurrentes. Ce garde ne prouve ni entropie, ni unicité entre processus/redémarrages, ni fraîcheur du dernier état, ni signature indépendante ou M11 réel. Un nonce réutilisé après un redémarrage reste une limite ouverte. Aucun droit moteur ou de reprise.

## Source de défis persistante, laboratoire G2

`durable_challenge_source.py` reserve un nonce avant la requete externe dans un journal append-only local distinct du proprietaire cognitif v5. Verrou OS cooperatif, controle de permissions, refus de fichiers lies, validation stricte des octets, `fsync` du journal et du repertoire permettent des tests de non-rejeu entre instances utilisant le meme repertoire non restaure. Le registre limite volontairement la capacite a 4096 reservations puis echoue ferme. Le fournisseur par defaut utilise `secrets.token_hex(32)` ; un fournisseur injecte est exclusivement un outil de test. Une copie ou restauration de l'ensemble du repertoire, un disque trompeur, un adversaire de meme UID, un systeme de fichiers non durable ou une corruption physique peuvent annuler ces garanties. Aucun ancrage externe, signataire independant, Scheduler, preuve M11 ou autorite de reprise.

## G2 : refus de réinitialisation partielle du registre

Un journal absent associé à un verrou existant, ou l'inverse, échoue désormais en lecture. Une fois initialisé, un journal vide est également refusé. Seul un répertoire vierge sans aucun des deux fichiers est initialisable. Les tests démontrent toutefois qu'une restauration ou suppression **simultanée** des deux fichiers permet de réutiliser un nonce ; il faut une borne externe réellement indépendante pour détecter ce scénario. Protection limitée aux processus coopératifs d'un même répertoire, aucun M11 ni droit de reprise.

## G2 : contrôle d'identité des fichiers de garde

Le registre local vérifie l'identité (device/inode) du répertoire, du verrou après acquisition et du journal pendant la réservation. Il refuse une substitution détectée au lieu de valider un verrou détaché. Cela ne protège pas contre les remplacements antérieurs à l'ouverture, les attaquants capables de manipuler les fichiers avec le même UID, le rollback intégral ou un faux stockage durable. Aucun changement d'autorité M11 ni de reprise.

## G2 : ascendance locale verifiee a froid

`verify_fixture` exige maintenant, lorsqu'une borne `minimum_witness` est fournie, que le hash et le pas du maillon historique exact soient retrouves dans le journal SQLite v5 apres rejeu complet. Une extension locale dont la tete recente concorde avec le fournisseur mais dont le prefixe diverge est refusee `FORK`. Un fichier local trop court est `STALE`. Cette preuve porte seulement sur le journal local fourni et sur la borne **declaree** : elle ne demontre pas que la borne a ete authentifiee, que le fournisseur est independant, ni que l'effet physique a eu lieu. Les inspections restent sans reprise ou pouvoir moteur.

## Inspection incertaine avec ascendance dans un seul snapshot (G2)

Le diagnostic d'un COMMIT incertain et le maillon historique demandé par `minimum_witness` proviennent désormais du même snapshot SQLite audité. L'inspection refuse `FORK` avant de contacter le témoin lorsque l'ascendance locale diverge, `STALE` si le préfixe manque, et `UNKNOWN` lorsqu'une modification concurrente est détectée au réaudit. Cette cohérence est locale et temporaire, non linéarisable avec le fournisseur externe, sans permission de rejeu, d'action ou de reprise et sans attestation M11 réelle.

## G2 : incident de lecture du probe COMMIT incertain

Une exception de lecture locale durant le second probe est classee `UNKNOWN` avant tout acces au temoin, tandis qu'une erreur d'arguments reste un `ValueError`. Aucune permission de retry, reprise ou action et aucune nouvelle couche SQLite.
