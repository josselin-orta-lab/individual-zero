# I2 : audit externe du journal v3 (proposition G2 uniquement)

**31 octobre 2026. Lecture seule, aucune naissance, aucune permission motrice et aucune preuve M11.**

Source : `src/i2/modules/lifecycle_external_witness.py`.
Tests : `tests/i2/test_lifecycle_external_witness.py` et `tests/i2/test_lifecycle_external_witness_integration.py`.

## Defaut traite

La PR #679 a ajoute un evenement terminal absorbant dans **un fichier SQLite de test**. Le rejouage et la chaine SHA-256 detectent des incoherences partielles, mais ne detectent pas a eux seuls une **ancienne copie SQLite valide** : une vie apparaitrait non terminale si l'on ne consulte que la copie realisee avant le scellage. Une reecriture integrale avec recalcul des hachages locaux reste egalement possible.

Le nouvel audit compare la sortie deja verifiee de `CognitiveCycleFixture.audit()` a la **derniere tete** revendiquee par un service externe et independant. Les champs compares sont : version du journal, identite de vie et origine declaree, numero d'evenement, dernier pas physique, tete de chaine, reference et pas terminaux. Toutes les comparaisons sont exactes et l'absence de temoin fait **echouer** le controle.

## Contrat avec un futur temoin independant

Le module **ne cree aucun service de garde**. Il exige un port `IndependentWitness` :

1. `read_latest(life_ref, genesis_ref)` retourne **un seul** `LatestWitness` structurellement valide pour la derniere version attestee de cette identite ; la lecture doit etre monotone, coherente, atomique et protegee contre les anciennes preuves.
2. `verify_latest(record)` retourne litteralement `True` seulement si la signature, le proprietaire, la fraicheur de la lecture, l'absence d'equivocation et le lien exact entre preuve et champs sont controles par une autorite **distincte du fichier local**. Aucune implementation cryptographique de ce port n'existe dans I2. Les tests injectent un double in-memory sans valeur de securite.
3. Le controle n'accepte ni un temoin plus recent que le journal local (ancienne copie), ni un journal plus recent que le temoin (publication non encore attestee), ni deux tetes divergentes au meme nombre d'evenements. La fermeture terminale doit coincider exactement.
4. `verify_fixture(fixture, witness)` exige le vrai banc `CognitiveCycleFixture` en mode v3, effectue l'audit local **avant** de consulter le temoin, et produit uniquement une `WitnessAudit` en lecture seule. La comparaison pure `compare_audit(report, witness)` est exposée pour les tests de contrat ; un dictionnaire fourni arbitrairement ne prouve pas son origine.
5. La sortie porte toujours `motor_authority=NONE`, `resumption_authorized=False` et `m11_authenticated=False`, y compris lorsque le temoin concorde sur un etat ouvert. Le statut `MATCHED_OPEN_INSPECTION` **n'autorise aucune reprise**.

## Scenarios adversariaux

- Copie SQLite ouverte avant la cloture terminale, puis controlee contre la tete externe apres cloture : **refus pour copie ancienne**.
- Deux branches SQLite avec meme origine et meme numero d'evenements, mais des evenements terminaux differents : **refus pour bifurcation**.
- Depot local valide avec une extension non encore publiee chez le temoin : **refus**, sans essayer de synchroniser automatiquement ni de refaire une commande.
- Preuve absente, non authentifiee, d'une autre vie, d'un autre genesis, d'un autre schema, de mauvaise chronologie ou incoherente sur le terminal : **refus**.
- Controle d'un journal v1/v2 ou d'un objet arbitraire : **refus avant tout port externe**.
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
