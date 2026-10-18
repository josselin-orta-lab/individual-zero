# I1 development status

**Date:** 2026-10-17. **Generation:** I1 (active).
**Parent reference:** I0 (frozen).
**This is an engineering ledger, not scientific GO.**

## Authority

- Declarative contract: [engine.json](../engine.json).
- Registry: [engine-registry.json](../../../config/engine-registry.json).
- Architecture map: [ARCHITECTURE.md](ARCHITECTURE.md).
- Validation obligations: [TEST_PLAN.md](TEST_PLAN.md).
- Native migration evidence: [I1_NATIVE_MIGRATION.md](../../../docs/engineering/I1_NATIVE_MIGRATION.md).

## Current implementation at creation of this ledger

- I1 birth: `i1lab.i1_birth.birth_i1`, canonical `I1Runtime`.
- Four published cognitive owner families: values/needs, causal model,
  perception, metacognitive health.
- Per-generation Lab: `src/i1/lab/`; native implementations in
  `src/i1/runtime/`. I0 Lab archived at `archive/i0/lab/`.
- M11 authentic SQLite cold recovery and irreversible death exercised by
  current CI. The disposable `i1lab` build remains a **compatibility
  dependency**, not yet a fully direct importable native runtime.
- Structural migration PRs: #251 (archive I0), #252 (generation tooling),
  #253 (I1 native code and versioned Lab). This campaign is stacked after
  #253; verify real GitHub state before merging.
- A CI pass is not proof of emergent intelligence, long-run learning, or
  independently validated active publications.

## Unresolved engineering and scientific gates

- Prove genuine **nonempty Stage10 publication by all relevant owners**
  from experienced events, followed by consistent cold recovery.
- Maintain M11 refusal gates for corrupt state, ambiguous COMMIT and owner
  mismatch; extend fault-injection when transaction boundaries change.
- Replace transitional namespaced build only with proven output and
  persistence compatibility, not by a path rename.
- New preregistered scientific evaluations must use *current* natural I1;
  previous broken experimental cohorts are not acceptance oracles.
- Every future generation needs its own Lab and its own evidence.

## Working agreement

Update this page with factual PR/commit links and new unresolved issues at
the end of each campaign. Do not mark a scientific property achieved on the
strength of software tests alone. No automated rollback of living states.

## Campagne de structuration #254, tranche 2

Les suites logicielles du moteur sont déclarées dans `src/i1/engine.json` et planifiées/exécutées par `tools/run_engine_checks.py` : `structure`, `smoke`, `full`, `m11` et `source`. Le mode par défaut prépare les commandes sans les exécuter ; seul `--execute` exécute les vecteurs Python prédéfinis sans shell. Les générations non actives et non enregistrées sont refusées. L'outil ne délivre aucun GO scientifique.

La CI [#39039120881](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39039120881) valide le commit `9df88896f298cdf45e434d721a67345c3c71b8a7` sur Python 3.11 et 3.12. L'outil de squelette `tools/new_engine.py` reste inerte et non enregistreur : I2 n'a pas été créé ni activé. Les prochaines priorités organisationnelles restent la traçabilité des campagnes, la séparation des tests par génération et la finalisation prudente du générateur transitoire.

## Structuration : isolation des tests actifs, PR #254

Quatre tests actifs ont été transférés sans changer les scénarios de `tests/` vers `tests/i1/` : séparation du build, garde I0/archives, récupération froide M11 et défaillances M11 adversariales. Leurs racines d'import sont adaptées à la nouvelle profondeur; le contrat `engine.json`, le registre et le workflow utilisent leurs nouveaux chemins. Les anciennes campagnes A2 demeurent hors critères d'acceptation du naturel I1.

La CI [#39039607085](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39039607085) a conclu avec succès en Python 3.11 et 3.12 sur le commit `8387ba8ff4f910142d6e8e1ed4cd5bf163d2e122`. La présente documentation est postérieure à ce commit : revérifier le dernier HEAD si une nouvelle validation est demandée.

## Campagne de structuration : rapport de provenance

`tools/campaign_report.py` lit le vrai `git HEAD` de l'environnement, le SHA-256 du contrat I1 et les résultats des suites enregistrées / JUnit, puis produit `reports/i1-campaign-3.11.json`, `reports/i1-campaign-3.11.md` (et leurs variantes 3.12). Il distingue `PASS`, `FAIL`, `NOT_OBSERVED` et `INVALID`, sans attribuer un statut de merge ou un GO scientifique. Le rapport n'interroge pas GitHub et n'affirme pas que tous les contrôles du workflow ont réussi : le statut final du workflow reste à contrôler séparément.

La CI [#39040216449](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39040216449) a validé les deux jobs Python 3.11 et 3.12 pour le commit `1d2bfe3fff1f6ffc341015c4ca1fcdd3cc763d01`. Les anciennes campagnes scientifiques non vérifiées ne sont pas reprises comme référentiel.

## Structuration : examen des propositions non activables

`tools/assess_engine_proposal.py` évalue en lecture seule les propositions I2+ (structure, Lab propre, contrats, tests, dépendances parentales), mais ne les enregistre et ne les active jamais. Des tests négatifs couvrent le squelette incomplet, un import direct du runtime parent et une fausse activation. Voir `docs/engineering/ENGINE_PROMOTION.md`. Cette campagne ne crée aucune génération I2.

## Monde prédéfinis pour le Lab I1 (2026-10-17)

Six mondes ont été ajoutés dans `src/i1/lab/world_presets/` : oasis, foraging, dry-valley, empty-land, hazard-edge, blocked-route. Le lanceur `tools/run_i1_world_preset.py` utilise la naissance naturelle d'I1, avec WAL ou M11, sans injecter d'oracle ni choisir les actions. Le workflow manuel `.github/workflows/i1-preset-worlds.yml` est préparé pour GitHub Actions, avec rapports JSON et données de custody ; sa disponibilité dans le menu Actions dépendra de son intégration à la branche par défaut. Les contrôles automatiques exécutent deux naissances réelles courtes, oasis/WAL et empty-land/M11, mais ces essais techniques ne constituent pas une preuve scientifique de survie ou d'émergence. Les cartes sont fixes par nom, la graine contrôle l'identité individuelle. Documentation : `src/i1/docs/WORLD_PRESETS.md`.

## PR #254: follow-up implementation handbook (2026-10-17)

At the initial verified PR HEAD `84d7e0ef47ade9be804a680b96eb5fe1ad396db8`, the current workflow run [#39052167410](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39052167410) was reported as successful. That result does **not** validate later documentation commits.

This iteration added [UC_AND_SCHEDULING.md](UC_AND_SCHEDULING.md) covering the two separately metered P-43/P-42 UC budgets and connected it from the handbook, expanded the executable failure-diagnosis index, and recorded an **OPEN source-level Stage10 defect**: `_publish_live_consolidation` references the local `canonical` before assigning it. No living publication execution or scientific validation was run for this observation. Targeted code correction and a regression test remain needed before nonempty publication claims.

The GitHub workflow for documentation HEAD `dbbf1d732d8a9c1b52e4986dd44af1e529b49d41` was **pending at the time checked**; subsequent commits require checking their own exact SHA. Local suites were **NOT_RUN** because no repository checkout / GitHub clone was available in the execution container. Structural and scientific state must not be inferred from an earlier green SHA.

## PR #254: documentation integrity checks, tranche suivante

An additional static guard `scripts/check_i1_handbook.py --json` checks the actual `src/i1/docs/` Markdown inventory, local links, quoted explicit source paths and agreement between `engine.json`, the evidence index and active generation registry. The checker does not execute referenced commands or infer scientific results. Negative regressions live in `tests/i1/test_i1_handbook_integrity.py`; `.github/workflows/engine-structural.yml` executes the guard on Python 3.11 and 3.12.

**OPEN #255:** [Stage10 canonical initialization before owner mapping](https://github.com/josselin-orta-lab/individual-zero/issues/255). This runtime repair is isolated from the documentation PR: current CI retains byte-exact I1 generated-output parity against a frozen pre-migration commit. No parity gate was relaxed, and no cognitive runtime source was modified in this tranche.

The previous documentation HEAD `f861ac4afb95bfe3d9641af351a4f8b4950bc869` completed [CI #39052847125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39052847125) successfully. The new validator and workflow commits require separate SHA-specific acceptance; **not yet certified** by this historical result.

## Stage10 issue #255 targeted repair

The source-level `UnboundLocalError` in `Stage10Runtime._publish_live_consolidation` is addressed by moving the `canonical` assignment ahead of coordinator construction, without changing the selected owner mapping, cognitive choices, M11, physical dynamics or frozen I0. Dedicated test: `tests/i1/test_i1_stage10_canonical_publication.py` (natural and generic owner dispatch and invalid-form deferral). The migration parity gate `scripts/test_i1_artifact_parity.py` retains byte equality for all artifacts except the exact, independently checked movement of this one Stage10 assignment. The CI script inventory was also updated to include `scripts/check_i1_handbook.py`, resolving the known inventory mismatch from workflow #39053148874.

**Verification status:** pending on the exact final patch SHA at the time of this report. A green earlier commit is not sufficient. This change does not establish the scientific usefulness of four-owner consolidation; real nonempty form deltas, attribution, P-42 UC and M11 cold state evidence remain OPEN / NOT_OBSERVED.

## Stage architecture and agent navigation, PR #254

Added [STAGES_AND_INTERFACES.md](STAGES_AND_INTERFACES.md) by inspecting current source: the natural `I1Runtime` resolves a cooperative multiple-inheritance chain through I1-specific water/uncertainty and Stage12, `Stage11SleepRuntime(Stage11Runtime, Stage10Runtime)`, Stage9 to Stage4 and the Stage3/2 physical substrate. Stage1 and Stage5 are not on that active inheritance chain. The guide maps concrete phase entrypoints, cross-module data, provenance restrictions, UC, M11 custody and current test anchors, without promoting old cohorts or software tests to scientific proof. The handbook index and required-document tests now include this guide.

Previous head `ca716fe501622e1c90dff8cb746b376d8a2c05bd` passed GitHub Actions #39053624321 on its exact SHA. The current documentation edits require their own workflow validation; no new scientific GO is asserted. Remaining gaps include an executable per-mechanism evidence map with direct tests and prospective four-owner publication traces.

## Documentation, state custody and runnable suite contracts (2026-10-17)

The prior source-backed guide commit `af03d5c79bdde097eddceb181cdda772c31efc00` passed [GitHub CI #39053993737](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39053993737). This success applies **only** to that SHA.

This iteration added [DATA_CONTRACTS_AND_CUSTODY.md](DATA_CONTRACTS_AND_CUSTODY.md), covering `Contribution`, `STVersion`, the technical/autobiographical boundary, Stage10 publication keys versus canonical owner IDs, owned cold-state envelopes and M11 failure fencing. [LIVED_EVIDENCE_WALKTHROUGH.md](LIVED_EVIDENCE_WALKTHROUGH.md) gives the existing, operator-only `report.json` walkthrough with the explicit `NOT_OBSERVED` cognitive fields. Existing Memory, M11, development and README guides now cross-reference them. Documentation presence checks cover both new guides.

A separate **source-inspected executable-contract error** was found: `scripts/test_i1_ci.py` requires `--junit`, but the declared `engine.json` smoke/full suite argument lists omitted it. Both registered test vectors and example commands now include their own report targets, with a focused `tests/i1/test_engine_suites.py` assertion. This changes test dispatch only, not I1 cognition, Stage10, physics, owner state or I0.

**Acceptance at this iteration's newest commit is pending** the exact CI workflow result. Neither a green previous SHA nor current documentation constitutes proof of natural learning or multi-owner publication. Those remain OPEN / NOT_OBSERVED.

## PR #254: charged-work and Stage10 publication diagnostics (2026-10-17)

Confirmed successful workflow [#39054465750](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39054465750) for the **prior** SHA `f895ad3bc62a3096de071284ce85294b35275fc3`. This is not certification of the current changes.

The present documentation iteration expands [UC_AND_SCHEDULING.md](UC_AND_SCHEDULING.md) with exact P-43/P-42 requested/accepted charge semantics, configuration-level protected modules versus runtime protected-hook refusal, and no-cost quotes; expands [CONSOLIDATION_AND_PUBLICATION.md](CONSOLIDATION_AND_PUBLICATION.md) into executable sleep/cut/pass/rebase/commit/M11 decision gates; expands [OBSERVABILITY.md](OBSERVABILITY.md) with measured versus absent fields for WAL/M11 and permitted passive observation. **None** of these commits changes I1's cognitive runtime, the six world presets, I0 or mortal recovery.

`scripts/check_i1_handbook.py` now attempts static AST validation of explicitly annotated Python functions and class methods, without importing a living runtime. `tests/i1/test_i1_handbook_integrity.py` includes a missing method reference negative case. Exact-SHA CI must confirm the validator does not overclaim coverage: bare unannotated symbols and scientific claims remain outside its scope. No novel nonempty four-owner publication was measured; OPEN / NOT_OBSERVED still applies.

## PR #259 : intégrité des références physiques (revue du 2026-10-18)

La revue de l'index transitoire de publication causale a identifié une limite
du premier diff : le remplacement d'un identifiant de rapport pouvait
conserver indûment une ancienne référence physique dans le set temporaire.
La correction fait expirer cette référence uniquement si aucun autre
identifiant publié ne la détient encore. Les essais différentiels comparent
l'ancien bloc avec l'implémentation réelle, y compris collisions d'identifiants,
références dupliquées et séquences courtes exhaustives. Le chemin commun
sans remplacement reste un contrôle O(1) par observation après construction
initiale. La validation des deux versions Python sur le SHA corrigé et la
fusion restent à constater ; aucun GO scientifique n'en découle.

## PR #260 : index transitoire des témoins numériques

La publication des témoins physiques numériques utilisait une recherche
linéaire dans toutes les références déjà publiées pour chaque nouveau témoin.
Le candidat ajoute un ensemble transitoire des `transition_event_ref` existants,
mis à jour seulement après admission. Contrairement aux rapports AgencyEvidence,
les témoins numériques interdisent déjà le remplacement d'identifiant; aucun
cas d'éviction n'est autorisé. L'ordre, la validation, l'atomicité, la provenance
et la persistance sont inchangés. Les tests différentiels couvrent les collisions
dans l'historique et le lot, et des comparaisons exhaustives de petits lots.
Le GO scientifique et les performances réelles restent non établis; la fusion
attend les contrôles CI exacts Python 3.11 et 3.12.

## PR #261 : sélection unique de provenance par témoin (2026-10-18)

Dans `established_prediction_corrections`, le minimum lexical des
identifiants d'interventions actives était recalculé pour chaque rapport
P-47 compatible d'un même témoin numérique. La valeur est indépendante
des rapports : la calculer une fois après la garde `n2` garde le même
identifiant de provenance pour tous les résultats. Une vérification
différentielle exhaustive de petites combinaisons et la parité exacte de
deux blocs limitent le changement. Aucun fait cognitif, test forcé ou
jugement causal supplémentaire. Validation CI du nouveau SHA exigée
avant fusion; pas de GO scientifique.

## PR #262 : tri unique des contrôles alimentaires (2026-10-18)

La revue d'hypothèse alimentaire retraiait `sorted(controls)` dans la
boucle de chaque exposition, alors que les contrôles sont inchangés pour
toute la requête. Un tri transitoire unique avant la boucle réduit ces
triages sans modifier l'ordre lexical, la sélection du premier couple
observé ou la preuve physique. La parité exacte est prolongée à partir
des transformations approuvées #258–#261. L'essai exhaustif de petites
séquences compare les mêmes résultats des deux algorithmes. La CI du
commit précis reste nécessaire avant fusion ; aucun GO scientifique.

## PR #263 : recherche des contrôles d'hydratation (2026-10-18)

Le parcours de tous les contrôles déjà triés pour chaque exposition
hydrique est remplacé par un index temporaire par contexte observé et
variables de contrôle. L'index préserve strictement l'ordre d'insertion
des témoins triés et ne filtre que les comparaisons qui auraient déjà été
éliminées. Le premier couple admissible, les références physiques et les
gardes de causalité restent inchangés. Les tests différentiels couvrent
de petites séquences exhaustives; contrôle exact du code généré, CI 3.11/3.12,
M11 et I0 restent nécessaires avant fusion. Pas de GO scientifique.

### PR #263 : garde des observations non canoniques

Revue complémentaire avant fusion : les contrats existants acceptent des
variables de contrôle sous forme de tuples **ou de listes**. L'index
transitoire ne s'active donc que pour les tuples de tuples, et le parcours
ordonné original reste utilisé pour les entrées comparables mais non
indexables. Aucun contrôle ne reçoit une interprétation nouvelle. Les tests
différentiels incluent maintenant les représentations mixtes ainsi que les
séquences canoniques. La validation du commit corrigé reste nécessaire.

## PR #264 : cache transitoire des interventions admissibles

Les témoins numériques d'une même contingence publiée recalculaient à
chaque requête la même fenêtre de révision, le nombre de contextes
physiques indépendants et la première provenance. La PR propose une
mémorisation strictement locale à l'appel, sans nouveau propriétaire,
évidence, persistance, ou changement des frontières DC-09. Les tests
différentiels couvrent plusieurs témoins, contextes et bornes de
réfutation. Validation Python 3.11/3.12 requise avant fusion;
aucun GO scientifique n'en découle.

## PR #265 : index transitoire des sources physiques causales (2026-10-18)

Après #264, le traitement des observations `publish_causal_inference`
balayait `observations.values()` pour chaque nouvel alias physique.
La tranche #265 construit un index de première occurrence uniquement
pour les lots de trois observations ou plus. Il est mis à jour après
admission et reste privé à cette publication. Une collision d'identifiant
désactive immédiatement le chemin indexé pour tout le reste du lot,
préservant les remplacements du dictionnaire historique et les contrôles
de contradiction. Les petits lots et lots vides conservent le scan.
Le test exécute directement l'ancien et le nouveau bloc de publication
sur des combinaisons exhaustives, incluant alias, conflits, collisions et
crédits orphelins; benchmark CPU synthétique facultatif. Les garanties
I0, M11 et causalité vécue restent intactes. La CI exacte est nécessaire
avant fusion. Aucun GO scientifique n'est affirmé.

## PR #266 : réutilisation du comptage P-35 des observations positives

Après #265, la publication d'une corrélation calculait les identifiants
positifs distincts dans `confirmed`, puis reparcourait les mêmes
observations `e.values()` pour les recompter dans la comparaison de taux
de base. L'expression utilise maintenant `len(confirmed)` déjà validé
contre le seuil n1. Cette égalité repose sur la construction de `e`
comme dictionnaire à identifiant unique. Les gardes des témoins,
l'indépendance des sources, les seuils et le statut restent identiques.
Une suite différentielle et la parité source exacte sont fournies.
Les performances réelles et toute validation scientifique restent
non établies avant les contrôles CI du SHA courant.

## PR #267 : dispatch par prédicat des revues vécues (2026-10-18)

Chaque contingence précédemment corrélée invoquait les revues alimentaires
et hydriques, bien que leurs gardes de prédicat soient mutuellement
exclusives (`toxic_item` et `hydration_effect`). Une seule revue est
maintenant appelée, avec le même résultat ou `None`. Aucun fait n'est
produit sans preuve physique, et le statut causal reste soumis aux
contrats en vigueur. À la demande de l'utilisateur, aucun test nouveau
ni campagne manuelle supplémentaire n'a été ajouté ou exécuté.
Revue de code et contrôle de parité exact sont fournis; la PR reste
non fusionnée tant que les contrôles existants ne sont pas satisfaits.

## PR #268 : projection directe des paires de contrôle non canoniques

Le chemin P-35 acceptant des contrôles sous forme de listes matérialisait
d'abord toutes les paires compatibles, puis effectuait deux parcours pour
les réduire en dictionnaires d'identifiants. Cette optimisation construit
directement les deux dictionnaires pendant le parcours exposé/contrôle.
Les tests, contrats, ordre d'insertion et résultats cognitifs restent
conceptuellement inchangés. Aucun nouveau test n'est ajouté à la demande
de l'utilisateur. Un contrôle de parité source contraint le seul bloc
modifié. Aucun GO scientifique ou gain CPU mesuré n'est revendiqué.

## PR #269 : réutilisation révisable des contextes d'intervention (2026-10-18)

La publication de plusieurs interventions positives reconstruisait, pour
chaque admission, l'ensemble des contextes indépendants de tous les
témoins positifs d'une même contingence. La tranche #269 conserve le
parcours original pour les petits lots (moins de trois interventions en
attente) ; pour les autres, elle conserve uniquement pendant l'appel
un ensemble par référence de contingence et borne de réfutation.
Seuls les témoins physiques admis, positifs et `self_compatible`
enrichissent cet ensemble, lorsque leur pas observé est postérieur à
la borne. Une réfutation qui avance la borne invalide immédiatement
l'ensemble. L'historique admis reste l'unique source de vérité ;
la promotion finale différée conserve son calcul historique.
Le contrôle de parité du code généré autorise exactement quatre blocs.
Aucun nouveau test n'est ajouté ni lancé manuellement, conformément
à la consigne. Aucune validation scientifique ni accélération mesurée
n'est revendiquée avant les contrôles habituels du dépôt.

## PR #270 : parcours direct des index de provenance physique (2026-10-18)

Le contrôle des interventions précédemment admises construisait un tuple
contenant la concaténation de quatre index déjà en mémoire, y compris les
répétitions possibles d'un même témoin. Cette optimisation conserve les
quatre listes par référence et les parcourt dans l'ordre identique pour
toute vérification de conflit. La simple présence d'une référence dans
l'un de ces index continue à bloquer tout nouveau crédit, y compris pour
les descriptions d'autres contingences. Le contrôle de conflit s'exécute
toujours avant celui de crédit. Aucun autre statut causal ou preuve
vécue n'est modifié. Aucun nouveau test ni campagne manuelle n'est
ajouté, conformément à la consigne. Le changement de code généré est
contraint par trois blocs exacts et attend la CI existante; aucun gain
mesuré ou GO scientifique n'est revendiqué.

## PR #271 : comptage et sélection P-47 en un parcours

La promotion différée au statut établi conserve désormais seulement les
signatures de contextes et le témoin maximal pendant un unique parcours
des interventions déjà admises au-delà de la borne de réfutation. Elle
n'alloue plus la liste temporaire des témoins positifs. Le seuil n2 et
la règle de sélection du maximum (pas du monde, identifiant) restent
identiques ; les interventions invalidées sont ignorées. Aucun test
supplémentaire ni campagne manuelle selon la consigne. Validation CI
habituelle requise avant fusion, sans GO scientifique revendiqué.

## PR #272 : classification unique des observations hydriques

La revue hydrique ne matérialise plus une liste de toutes les observations
candidates avant de la filtrer deux fois. L'unique parcours sépare
directement les interventions positives et les contrôles négatifs ;
les deux groupes sont ensuite triés lexicalement comme auparavant.
Les observations de modalités mixtes restent exclues de chaque groupe.
La provenance vécue, l'ordre d'admission et les conditions physiques
ne sont pas modifiés. Aucun test ajouté ni lancement manuel selon la
consigne. Source générée limitée à un bloc exact, CI habituelle avant
fusion. Aucun GO scientifique.

## PR #273 : éviter les tris sans paire hydrique disponible

Une revue hydrique nécessite une exposition et un contrôle physique.
Lorsqu'un des deux groupes est vide après classification, retourner
immédiatement `None` évite deux tris et la construction d'un index.
Le résultat de recherche était déjà `None` dans ce cas. Le parcours
vécu, les seuils, les témoins admis et la provenance sont inchangés.
Aucun test nouveau et aucune campagne manuelle. Le diff source est
strictement contrôlé; fusion après CI existante seulement.

## PR #274 : retour anticipé sans paire alimentaire observée

Après avoir filtré les preuves vécues, la revue alimentaire ne peut
produire de comparaison sans exposition positive ni contrôle observé.
Un retour anticipé `None` évite alors les tris lexicographiques et
leurs allocations. Les gardes de provenance, P-35 et les situations où
les deux bras existent restent inchangées. Aucun test ajouté ou lancé
manuellement conformément à la consigne. Parité source strictement
limitée au bloc révisé ; fusion soumise à la CI existante.

## PR #275 : contrôle en un parcours des alias DC-09 fermés

L'ingestion des comparaisons Agency issues d'un épisode autobiographique
fermé matérialisait une liste de références puis un second ensemble pour
détecter les doublons. Le même contrôle d'unicité s'effectue maintenant
au fil des références fermées, sans liste intermédiaire. La sélection
`agency_source_refs` et l'ordre de la vérification préalable à tout
décodage et admission restent inchangés. Aucun nouveau test ni campagne
manuelle selon la consigne; parité source exacte avant fusion.

## PR #276 : parcours direct des témoins numériques physiques

Le précontrôle de l'épisode autobiographique recréait un tuple concaténé
de l'historique des témoins numériques et de la liste en attente pour chaque
nouveau témoin. Cette tranche parcourt ces deux collections directement
et dans le même ordre, en conservant la règle de rejet du premier doublon.
Pas de nouvelle mémoire cognitive ni de modification de I0/M11, mortalité
ou admission physique. Aucun test ajouté ou exécuté manuellement; la CI
habituelle doit valider le SHA exact avant toute fusion.
