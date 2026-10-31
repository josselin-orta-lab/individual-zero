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
