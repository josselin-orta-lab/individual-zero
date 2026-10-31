# I2 : scellage terminal synthétique dans le journal cognitif (G2)

**31 octobre 2026. Proposition expérimentale non exécutable, sans naissance et sans mortalité physiologique réelle.**

Code : `src/i2/modules/cognitive_cycle_fixture.py`, mode opt-in `LIFECYCLE_SCHEMA` (v3). Tests : `tests/i2/test_synthetic_lifecycle.py`. La v3 conserve **un seul compte UC synthétique et un seul journal SQLite** pour intentions, Competition, revue Action Control et déclaration terminale. Elle ne crée aucun service M11, ni second journal, ni nouveau propriétaire WorldBody.

## Contrat de la version v3

1. **Origine synthétique déclarée.** `CognitiveCycleFixture.create(..., genesis_ref=..., terminal_source=...)` n'est disponible qu'avec `current_source` et `safety_source` (mode contrôle v2). `genesis_ref` est une référence de banc déclarée par l'appelant et figée dans une table `lifecycle` du même fichier. Elle est vérifiée lors de `audit()` et `reopen()`. Elle **n'est pas une identité de naissance attestée** : son intégrité ne peut pas être garantie contre la réécriture malveillante complète du fichier.
2. **Événement terminal séparé.** `seal_terminal(physical_step, terminal_ref, evidence_ref)` exige un pas strictement postérieur au dernier événement, une référence du domaine `terminal:` et un résultat **exactement `True`** du port injecté `TerminalSource.verify_terminal`, lié à la vie déclarée, à son origine, au pas et à la tête du journal antérieur. Les tests fournissent un double synthétique. La méthode ne déduit ni la mort, ni sa cause, ni un coût UC depuis la vérité cachée d'un Lab.
3. **Un seul COMMIT local.** L'événement terminal canonique est chaîné par SHA-256, inséré dans `events`, et le marqueur terminal est publié avec l'en-tête `account` par une transaction SQLite `BEGIN IMMEDIATE` / `COMMIT`. Un échec avant COMMIT annule tout ; une confirmation perdue après COMMIT se résout par `terminal_lookup()` sans nouvelle requête au port de décès ni écriture.
4. **Terminal absorbant pour ce fichier.** Une fois le marqueur validé, `open()`, `observe()` et `seal_terminal()` sont refusés, y compris après `reopen()`. Le contrôle intervient **avant tout accès aux ports externes** dans la voie v3. `lookup()` ne transforme jamais un événement terminal en reçu cognitif ; le reçu terminal est exclusivement en lecture seule. Il n'existe pas d'API `revive`, `birth`, `dispatch`, `admit_motor` ou `execute`.
5. **Audit reproductible.** La lecture froide recalcule les transitions cognitives antérieures, l'état intentionnel, le compte UC synthétique, le chaînage et la cohérence événement/marqueur terminal ; elle rejette un événement après le scellage, des en-têtes/étapes incompatibles, des références d'origine divergentes et de nombreuses corruptions partielles. Le champ `committed` compte **tous** les événements, y compris le terminal. Le scellage ne consomme pas d'UC cognitives.
6. **Compatibilité stricte.** Les journaux v1 (cognition seule) et v2 (cognition + revue) restent tels quels. Une ouverture au mauvais schéma est refusée ; il n'existe **aucune migration implicite** v1/v2 → v3, ni restauration d'une identité terminale en une nouvelle vie.

## Frontières qui restent entièrement ouvertes

| Propriété | Validée ici | Non démontrée |
| --- | --- | --- |
| Origine | Comparaison au `genesis_ref` stocké localement | Identité de naissance créée/scellée par M11 ou par un propriétaire indépendant |
| Terminal | Attestation booléenne par un port synthétique obligatoire | Décès physique réel provenant du WorldBody, causalité corporelle et séquence signée |
| Atomicité | Un COMMIT SQLite entre journal, UC locales et marqueur terminal | Transaction complète du vrai Scheduler + M11 + WorldBody |
| Reprise | Inspection froide et refus de nouvelles opérations sur **ce fichier** | Non-résurrection entre fichiers, machines, identités ou restaurations de sauvegardes |
| Intégrité | Rejeu et détection de corruption partielle | Protection contre réécriture intégrale de la base et recalcul de la chaîne sans ancre externe |
| Autorité | `motor_authority=NONE` pour tous les résultats | Toute admission, ordre physique ou contrôle de sécurité temps réel |
| Science | Tests synthétiques de logiciel | Mortalité autonome, apprentissage naturel, robustesse L3, avantage I1/I2 |

L'API v3 **n'est pas** un système de naissance, un orchestrateur de vie ou une interface de mort M11. Il est interdit de l'activer en remplaçant un fournisseur de preuve par un simple `True`, d'affirmer une irréversibilité globale ou de réutiliser les traces I1 comme connaissances initiales.

## Vérification

`python -m unittest discover -s tests/i2 -p 'test_*.py' -q`

Les 31 nouveaux tests isolent l'identité synthétique, la fermeture avant/après cycle, le rejeu post-terminal, la concurrence, la corruption d'événement/marqueur, le rollback et les accusés perdus. Le contrôle final doit être effectué sur le SHA exact en Python 3.11 et 3.12. Une CI I1 lourde n'est pas pertinente pour cette proposition isolée.

**G0 I1 : PARTIAL (archive source Git non protégée) ; G1 : REVIEW_REQUIRED ; G2 : test logiciel v3 ; G3 : M11/Scheduler/WorldBody non établis ; G4-G6 : non commencés. I1 actif, I2 non enregistré et non exécutable ; A1-C NO_GO, L3 NOT_ESTABLISHED, A2-R 0/96.**
