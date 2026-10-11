# Stage 11 : atomicité des reçus du journal technique et des snapshots

**Date :** 11 octobre 2026. **Qualification :** régression logicielle publique de développement, et non protocole expérimental held-out ou acceptation scientifique. **Source normative exclusive :** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, sections 4.6, 17.4, 17.6–17.8, DC-08, INV-33/44/49. **Stage 11 : EN COURS ; Stage 9 : NO-GO scientifique.** PR #25 maintenue en Draft, non fusionnée.

## Ordre chronologique des preuves

| Étape | SHA ou exécution | Nature et statut |
| --- | --- | --- |
| Point de départ intégré | `8d7806ed5f98a7b467d48fe0fddfda7f2ed25bfe` | [CI #38131536457](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38131536457), 883/883 Python 3.11 et 883/883 Python 3.12 PASS ; état antérieur aux deux corrections |
| Protocole reçu externe | `bdf61f2ca8533da24ff9bc1cea6b8dc0f0a3e335` | `stage11-external-journal-atomicity-protocol.en.md`, déposé **avant code et test** |
| Correction des entrées externes | `147ca1a1bd4d4ebb9b08b7d26bdf7ad91c6a9515` | `src/lab/injected_scenario.py` |
| Deux tests d'entrées externes | `8e955f1157589c06ceb4224c723fdea7c7c0a3b8` | `tests/test_stage11_external_input_atomicity.py` ; [CI #38132874940](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38132874940), **885/885** Python **3.12.15** PASS en **107,581 s**, bootstrap PASS |
| Protocole reçu snapshot | `a34951e4ad75ecc2c01086a4b48eb4e24b736658` | `stage11-snapshot-journal-receipt-atomicity-protocol.en.md`, déposé **avant code et test** |
| Correction snapshots | `5330b7afc3b732b709588c86246310b7caebbe91` | `src/lab/snapshots.py` |
| Deux tests snapshots | **`338f88ce1990fcbad1f750ed8a6ff8c7788ecfd9`** | `tests/test_snapshots.py` ; [CI complète #38133087743](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38133087743), **887/887** Python **3.11.17** PASS en **82,255 s**, **887/887** Python **3.12.15** PASS en **114,334 s** ; **2/2 jobs complets** PASS ; **15 artefacts** de diagnostics/référence, aucun échec de job |

Les nombres de tests proviennent des lignes `Ran ... tests` et `OK` des journaux GitHub Actions réels. Les deux campagnes ont reçu un runner, installé le projet et exécuté leurs étapes. La suite Python 3.12 à 885 tests et la campagne complète à 887 tests portent sur **deux SHA différents** ; aucune réussite n'est extrapolée à un autre code. Le rapport présent est une addition documentaire postérieure au SHA source/test complet.

## Contrat corrigé : événement physique / reçu technique

Avant correction, `InjectedScenario.apply_for_step` récupérait WorldBody en cas d'échec dans `apply_scenario_event` mais pas après un échec d'ajout de `external_input_received` ou de `external_input_applied`. Une perte du reçu `applied` après mutation pouvait laisser le monde changé et le scénario non arrêté. Une perte du reçu `received` pour le deuxième input pouvait laisser la première opération physique du lot en place.

Les trois opérations sont désormais incluses dans **un seul bloc de compensation** : réception journalisée, application physique, confirmation journalisée. En cas de défaut technique de reçu, le gestionnaire restaure l'état WorldBody capturé avant le lot, remet le curseur au premier input du pas, gèle la branche via son marqueur de rejet, journalise `external_input_rejected` et, si nécessaire, `external_input_batch_rolled_back`. La raison `technical_journal_failure` ne s'applique qu'aux échecs d'écriture ; les motifs antérieurs d'erreur physique sont conservés. `ScriptedStage2Runtime` clôt ce pas par `external_stop` avec zéro commande et zéro avancement du monde. **Le journal technique n'est jamais restauré ou tronqué.**

Les deux tests nouveaux injectent **délibérément un échec synthétique local** de `journal.append` au second input après une première opération acceptée, l'un sur `external_input_received`, l'autre sur `external_input_applied`. Ils exigent l'égalité stricte de WorldBody avant/après, la séparation des événements réellement reçus/appliqués/refusés, l'absence de capture ou commande post-échec, `journal.verify()`, le fail-stop, et, pour le reçu `applied`, le rejeu indépendant byte-identique sous le même calendrier de faute. Ces injections sont des **tests logiciels**, non des événements physiques vécus par l'individu.

## Contrat corrigé : reçu de snapshot

Avant correction, `SnapshotManager.take` insérait le snapshot dans `_snapshots` **avant** de journaliser `snapshot_taken` ; un échec du reçu laissait un checkpoint accessible mais techniquement non enregistré. Dans `restore`, l'événement `snapshot_restored` était écrit après la zone `try/except` qui savait compenser les propriétaires, donc un reçu refusé pouvait laisser des propriétaires causaux restaurés sans événement technique correspondant. Enfin, `_journal_sequence` avançait avant l'acceptation effective de l'ajout.

Le snapshot est maintenant construit et détenu localement, son événement `snapshot_taken` est accepté **avant** publication dans `_snapshots`. `snapshot_restored` appartient au même `try` que la restauration des propriétaires ; une écriture refusée déclenche leur compensation complète depuis les états précédant la tentative. La séquence technique n'avance **qu'après** une écriture acceptée. Les chemins ordinaires gardent leurs identifiants, leur payload causal et leurs hashes. Le journal append-only reste hors de la restauration.

Deux nouveaux tests **entièrement synthétiques** bloquent successivement `snapshot_taken` puis `snapshot_restored` : pas de snapshot orphelin ; état antérieur des deux propriétaires conservé après rejet de restauration ; pas de trou d'identifiant technique ; et nouvelle tentative valide strictement égale en octets et en hash à l'exécution indépendante sans faute. Les anciennes vérifications d'incompatibilité d'owner et de snapshots/hazards continuent d'être couvertes par les 887 tests.

## Périmètre et limites de preuve

- **Démontré dans les tests logiciels :** compensation des frontières identifiées en présence d'une défaillance injectée et bornée de l'ajout au journal, rejets explicites, unicité préservée, cohérence des propriétaires et des événements, suites intégrées PASS sous Python 3.11 et 3.12.
- **Non démontré :** confinement contre Python hostile avec accès aux attributs privés ; récupération générale si le journal demeure indisponible pour écrire *aussi* le marqueur de refus, ou si la récupération du monde/propriétaire échoue elle-même ; validation d'un comportement d'exploration général, sécurité universelle contre dangers cachés ou capacité à apprendre une menace à partir d'une oracle.
- **Goldens historiques :** le workflow complet génère plusieurs journaux de référence et un **diagnostic** Stage 9 de rejeu étendu ; ce fait ne vaut pas campagne de comparaison scientifique Golden indépendante ou held-out.
- **Stage 9 :** **NO-GO scientifique conservé**, indépendamment de ces 887 tests.
- **Stage 11 :** **EN COURS**. Les impasses géographiques à horizon plus long, les dangers inconnus et la saturation sous budgets UC dégradés ne deviennent pas validés par ces régressions transactionnelles.
- Aucun changement de la spécification normative, de `main`, des permissions de dépôt ou du statut Draft de la PR. Pas de fusion.

## Reproduction

Depuis un clone du SHA **`338f88ce1990fcbad1f750ed8a6ff8c7788ecfd9`**, avec Python 3.11 ou 3.12 et installation `python -m pip install -e .` :

```sh
python -m unittest discover -s tests -p 'test_stage11_external_input_atomicity.py' -v
python -m unittest discover -s tests -p 'test_snapshots.py' -v
python -m unittest discover -s tests -q
```

Pour les diagnostics étendus réellement exécutés, consulter les logs et les 15 artefacts de [CI #38133087743](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38133087743) liés à ce SHA. Ne pas présenter les artefacts de diagnostic comme une attestation scientifique.

**Prochaine priorité indépendante :** analyser les rejets de restauration d'un état WorldBody malformed/incompatible au niveau du propriétaire (en particulier prévalidation des versions/valeurs avant mutation), puis reproduire les horizons multi-pas et budgets UC encore négatifs, sans modifier les protocoles historiques.
