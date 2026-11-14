# I3 · Stage-6-light : préflight source-exact du checkout, sans World (14 novembre 2026)

**Statut : `CHECKOUT_BYTES_MATCH_EXTERNAL_PINS_PREAUTH_ONLY` uniquement en cas de succès du vérificateur.** Cette étape est un contrôle informatique *hors ligne*, pas un préenregistrement temporel, pas une levée de l’ADR-0017, pas un transport vivant, pas une répétition d’ingénierie et pas une autorisation scientifique. Le protocole Stage-6-light reste `METHOD_FIXED_PREAUTH_NOT_EXECUTABLE`, Stage 2.1 reste `NOT_ISSUED/HOLD_NO_VERDICT`, I1 actif et I3 référence non enregistrée.

## Pourquoi ce contrôle est nécessaire

Le [préflight précédent](STAGE6_LIGHT_NATIVE_ORIGINAL_PREFLIGHT_2026-11-14.md) prouve que des archives au **format** de `two_phase_panel` peuvent être lues et contrôlées, mais les sources de leurs manifestes étaient des **déclarations autocohérentes**, qui pouvaient être entièrement fabriquées. Cette nouvelle vérification relie le bloc `manifest.source` à **l'ensemble précis des octets `.py` du checkout** et aux blobs du commit Git déclaré. Elle exige **trois empreintes fournies séparément du dossier examiné** : SHA-1 du commit, SHA-256 canonique de la carte des sources et SHA-256 des octets du protocole de méthode. On ne peut pas calculer les trois pins depuis les pièces à vérifier puis prétendre qu'ils sont indépendants.

Le module autonome [`stage6_light_checkout_source_preflight.py`](../../../lab/stage6_light_checkout_source_preflight.py) n'importe aucun module I3, ne crée ni génome ni World et n'invoque pas de moteur de vie. Il ne possède pas de CLI d'exécution et tous ses appels `open_world`, `run_life`, `authorize_science` refusent l'opération.

## Contrat vérifié, sans naissance

1. **Avant le checkout**, vérifier le SHA-256 externe du document JSON de méthode, son schéma v1, l'ensemble exact des permissions à `false`, des champs de levée/indices à `null`, et la nécessité d'une décision distincte sur la sélection intergénérationnelle G/S/R.
2. Exiger un `source_record` avec **exactement** les quatre champs `files`, `sha256`, `git_head`, `working_tree_dirty`. Son `git_head` doit correspondre au SHA-1 externe et `sha256` au SHA-256 externe. Les fichiers doivent former une carte non vide de chemins Python relatifs sûrs et de SHA-256 valides. La canonicalisation du SHA de carte suit celle de `i3.runtime.provenance.digest`, sans importer ce runtime.
3. Exiger que `checkout_root` soit la racine du dépôt Git, que `git rev-parse HEAD` soit exactement le commit externe, et que `git status --porcelain --untracked-files=all` ne rapporte **aucune modification ni aucun fichier non suivi**. Un dépôt sale arrête la vérification.
4. Énumérer l'intégralité des `*.py` sous `src/i3` (pas seulement ceux annoncés), refuser les chemins dangereux ou liens symboliques, lire les **octets réels**, puis exiger leur concordance avec chaque SHA du manifeste, la carte complète et le SHA externe. Pour chaque fichier, comparer aussi les octets à ceux de `git show HEAD:src/i3/<chemin>`, afin de détecter notamment des modifications cachées par `assume-unchanged`.
5. Retourner uniquement la portée `CHECKOUT_BYTES_MATCH_EXTERNAL_PINS_PREAUTH_ONLY`, l'identité des pins et les compteurs structurels. Déclarer explicitement `owner_authorization=false`, `worlds_opened=0`, `lives_executed=0`, `scientific_verdict=NOT_ISSUED`, `external_pre_execution_timestamp_attested=false` et `source_or_method_independently_authenticated=false`.

Ce contrôle est *purement en lecture*. Il ne génère, n'assigne ni ne réutilise aucune graine prospective. Aucun reçu de fitness, score, mortalité, signe de contraste ou classification favorable n'est lu ou publié.

## Falsificateurs testés

[`test_stage6_light_checkout_source_preflight.py`](../../../../../tests/i3/test_stage6_light_checkout_source_preflight.py) met en place de petits **dépôts Git temporaires contenant deux modules purement fictifs**, sans importer `World`, `Mind`, `run_life`, ni les algorithmes du génome. Les 12 tests couvrent la concordance des empreintes externes, les limites explicites du rapport, la suppression/forgérie des pins, les mutations du protocole et des permissions, les fichiers modifiés/ajoutés/non suivis, les modifications marquées `assume-unchanged`, les changements de HEAD, les manifestes incomplets, les clés de chemin dangereuses, les liens symboliques et le refus systématique des points d'entrée vivants.

Commande de test logiciel uniquement :

```bash
PYTHONPATH=src python -m unittest discover -s tests/i3 -p 'test_stage6_light_checkout_source_preflight.py' -v
```

## Limites et travaux encore requis

- Cette vérification établit **une égalité d'octets relativement à des pins fournis**, pas leur source d'autorité. Les pins doivent être publiés dans un futur manifeste d'exécution extérieur au jeu de résultats, approuvé avant la première vie. Une signature ou ancre de temps indépendante reste une décision de gouvernance distincte.
- Le commit Git local, les fichiers et les empreintes sont vérifiés à l'instant de l'audit ; cela n'empêche pas les changements de processus, la modification en mémoire entre contrôle et usage, ni une substitution de l'interpréteur/du binaire Git. Ce n'est pas un environnement d'exécution attesté, une enclave ou une protection contre un opérateur hostile.
- **Ne peut pas attester rétroactivement** la première exécution des préenregistrements P3 historiques conservés dans le bundle. Leur statut `INDEPENDENT_PRE_EXECUTION_TIME_NOT_ATTESTED` demeure.
- La filiation parentale et l'égalité réelle de `mutate(parent,seed,scale=0.1)` ne sont **pas encore prouvées** ; les chaînages de pas corporels et dépenses cognitives originaux ne sont pas rejoués ; l'indépendance écologique des 16 populations et la disjonction exhaustive des futurs indices restent **non vérifiées**.
- Un résultat positif n'est **pas** une autorisation de naissance. Aucun transport vivant, répétition de cohorte d'ingénierie ou run scientifique ne peut être ouvert sans décision méthodologique spécifique ADR-0017, allocation prospective, source et manifeste scellés, répétition validée et levée propriétaire indexée. Voir [issue #1395](https://github.com/josselin-orta-lab/individual-zero/issues/1395).

**Bilan :** contrôle de correspondance de sources reproductible sur de petites données Git synthétiques, **zéro World, zéro vie, zéro nouvelle cohorte et zéro nouvelle permission**. Pas de changement à `ACTIVE_SURFACE.json`, au registre moteur, aux ADR, aux études historiques ou aux modules vivants I3.
