# Stage 11 : restauration atomique des snapshots physiques WorldBody

**Date :** 11 octobre 2026. **Qualification :** tests logiciels publics de développement. Aucune expérience scientifique held-out, acceptation de Golden historique ou inférence de sécurité universelle. **Spécification normative inchangée :** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, §§17.2–17.6, DC-08 et INV-33/44. **Stage 11 : EN COURS. Stage 9 : NO-GO scientifique.**

## État préalable et protocole

La dernière campagne complète avant cet incrément, [CI #38133087743](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38133087743), a validé **887/887 tests** sous Python 3.11 et sous Python 3.12 sur le SHA `338f88ce1990fcbad1f750ed8a6ff8c7788ecfd9`, antérieur à cette correction WorldBody. Aucun résultat n'est réattribué au nouveau code.

Le protocole [stage11-worldbody-snapshot-atomic-restore-protocol.en.md](stage11-worldbody-snapshot-atomic-restore-protocol.en.md) a été commité **avant** modification du code et des tests : `e4e6e65de137cb2f9b574319712b8902966a09a3`.

## Défaut exact

Dans `WorldBody.restore_causal_state`, les affectations `_position`, `_body`, `_inventory`, `_resources`, zones du monde, pierres et programmes externes intervenaient **au fil du décodage**. Un champ invalide découvert tardivement pouvait donc provoquer une exception après modification de la vérité physique. La vérification de `physics_version` était réalisée en dernier. Les conversions `int(...)` acceptaient notamment valeurs fractionnaires, booléens ou chaînes pour des quantités/positions et des entrées dupliquées pouvaient être silencieusement fusionnées. Ces erreurs se situent à la frontière du propriétaire WorldBody ; une compensation orchestrée par SnapshotManager ne remplace pas l'atomicité du propriétaire.

## Correction et tests

**Code :** `96ca50fe8b8c9bbc48dcfdbfed8908aec62f9129`, `src/lab/world.py`. La lecture de l'état vérifie d'abord la version physique puis prépare en mémoire locale tous les propriétaires de données WorldBody : position, BodyState, inventaire, ressources, obstacles, sources, créatures, zones dangereuses/létales, abris, pierres et compteurs de scénarios. Le décodage exige des coordonnées **exactement entières** dans l'intérieur normatif, des valeurs de corps numériques bornées, des quantités entières non négatives et des identités uniques, ainsi que des programmes d'échec et curseurs cohérents. Toutes les affectations du monde ne surviennent **qu'après** validation complète. Les snapshots ordinaires, l'ordre des listes exportées et les octets canoniques de leurs états valides sont conservés. Aucune physique, action, oracle, donnée cognitive, protocole normatif ou journal n'a été modifié par ce correctif.

**Tests :** `dba0184350674bec262ce6bd7e2fddb9040a9605`, `tests/test_world_physics.py`, deux nouveaux tests :
- restauration d'un état propriétaire rempli (ressources, pierre posée, zone dangereuse, créature, position externe et programme d'échec partiellement consommé), comparée à la restauration dans un WorldBody **indépendant**, avec égalité de `canonical_causal_bytes` et absence de références partagées ;
- **21 sous-cas** de rejets atomiques : version tardivement incompatible, coordonnées fractionnaires/booléennes/textuelles/hors grille/obstruées, NaN et booléen de corps, quantités invalides, duplications de ressources/positions/pierres/programmes, indices d'échec invalides. Chaque échec laisse `export_causal_state()` et ses octets canoniques égaux à l'état pré-opération, puis une restauration authentique reste possible.

Ces fixtures sont des **états logiciels synthétiques**, non des perceptions réelles ou des dangers appris par l'individu.

## Exécution GitHub Actions sur les SHA exacts

| Campagne | Code/test SHA | Python | Tests | Bootstrap / diagnostics | Verdict |
| --- | --- | --- | --- | --- | --- |
| [CI #38133892145](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38133892145) | `dba0184350674bec262ce6bd7e2fddb9040a9605` | **3.12.15** | **889/889** PASS, **88,626 s** | Bootstrap smoke PASS | **SUCCESS** |
| [CI complète #38134027826](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38134027826) | `dba0184350674bec262ce6bd7e2fddb9040a9605` | **3.11.17** | **889/889** PASS, **114,440 s** | Job complet et références PASS | **SUCCESS** |
| [CI complète #38134027826](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38134027826) | `dba0184350674bec262ce6bd7e2fddb9040a9605` | **3.12.15** | **889/889** PASS, **75,043 s** | Job complet et références PASS | **SUCCESS** |

Le workflow complet s'est achevé avec deux jobs réussis et **15 artefacts** de diagnostic/référence, sans étape en échec. Le job supplémentaire `quick-unit-tests` de cette campagne a été délibérément ignoré par le contrôle de coût du workflow ; il n'est pas compté comme un test supplémentaire. Une exécution précédente `#38133884333` a aussi été **skipped** ; seul `#38133892145` a réellement exécuté la suite courte de ce SHA.

Le diagnostic Stage 9 de référence et les journaux historiques générés dans `ci-full` sont des contrôles de logiciel, **pas** une campagne scientifique Golden indépendante, ni une validation prospective sur seeds cachées. Le NO-GO scientifique du Stage 9 n'est pas levé.

## Couverture, limites et suite

Ce correctif ferme la classe de mutations partielles de `WorldBody.restore_causal_state` due à une entrée malformée ou à une incompatibilité tardive **dans les tests existants et nouveaux**. Il ne prouve pas une résilience universelle à un code Python hostile, à des défaillances persistantes du journal, à des corruptions disque après publication, ni à toutes les continuations depuis des snapshots arbitraires. `WorldBody.apply_scenario_event`, l'interface d'entrées externes, les mécanismes d'Exploration, Planning, Gatekeeper et leurs budgets UC n'ont pas été modifiés.

**Prochaine priorité :** continuer les scénarios géographiques multi-pas et les dangers cachés dans les enveloppes UC strictes, avec transitions physiques contrôlées, versions gelées et tests de replay. Les cas d'entrée externe contenant des champs non reconnus peuvent aussi être audités séparément, sans requalifier une réception comme un fait appris.

Reproduction logicielle depuis le **SHA exact de code/tests** :

```sh
git checkout dba0184350674bec262ce6bd7e2fddb9040a9605
python -m pip install -e .
python -m unittest discover -s tests -p 'test_world_physics.py' -v
python -m unittest discover -s tests -q
```

**PR #25 : ouverte, Draft, non fusionnée. `main` et la spécification anglaise v1.2.1 inchangées.**
