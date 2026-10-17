# PR #246 — requalification des tests I1 et contrat de validation actuel

Date : 2026-10-17. Base main au démarrage : `bf59eceaf97805f04a18b0b28f1396f2e98bfa89`. Tête PR initiale : `305fe98d2937ec979f9a82b416d7cc1ae5bf9046`.

## Règles de qualification

Les anciennes cohortes, taux de survie et H1/H2 ne sont **jamais** des oracles de I1. Le seul acteur soumis au nouveau testeur est `i1lab.i1_birth.birth_i1` → `i1lab.i1_natural_runtime.I1Runtime`. I0, les contrats de source partagée, le monde physique unique, les événements authentiques, la causalité et la garde M11 restent protégés. La mort est irréversible. Un danger ignoré n'est pas nécessairement un bogue.

Classification des 19 fichiers `tests/test_i1_*.py` présents sur le SHA initial :

| Fichier (préfixe `tests/`) | État | Motif / propriété reportée |
| --- | --- | --- |
| test_i1_a235_lived_recall.py | REPLACE | Provenance de rappels utile ; ancien matcher A2.35 non référentiel |
| test_i1_a235_m11_cold_recall.py | OBSOLETE | Ancien M11 d'acteur expérimental non coordonné |
| test_i1_a235_m11_recall_contract.py | OBSOLETE | Configuration d'activation de rappel expérimentale |
| test_i1_a235_physical_witness.py | OBSOLETE | Témoin expérimental A2.35 on/off |
| test_i1_a235_runtime_birth.py | OBSOLETE | Activation et modèle externe A2.35 |
| test_i1_a236_combined_m11_cold.py | OBSOLETE | Quatre modèles expérimentaux actifs, naissance non canonique |
| test_i1_a236_combined_m11_water.py | OBSOLETE | M11 et D2 historiques, non coordonnés |
| test_i1_a237_d2_no_geography.py | REPLACE | L'ignorance géographique est valide, mais refus D2 historique non obligatoire |
| test_i1_a238_factorial_smoke.py | OBSOLETE | Bras H1/H2 et mortalité expérimentale |
| test_i1_active_birth.py | OBSOLETE | Prior externe / opt-in, pas naissance naturelle |
| test_i1_decision_witness.py | INVESTIGATE | Séquence synthétique demandant une survie malgré une mort physique observée ; conserver audit action/effet et vérifier toxicité |
| test_i1_first_physical_step.py | MOVE | Séparation du fork et pas physique réel ; contrôle technique générique |
| test_i1_generated_isolation.py | KEEP | Génération, déterminisme et isolation de I0 |
| test_i1_issue136_d1_learning.py | REPLACE | Apprentissage vécu pertinent ; ancien contrat de récupération D1 non admissible |
| test_i1_issue136_water_readiness.py | OBSOLETE | Ancien diagnostic d'absence d'apprentissage de l'eau désormais contredit |
| test_i1_m11_cold_recovery.py | KEEP | Protection négative : naissance expérimentale non coordonnée refusée |
| test_i1_model_m11_contract.py | OBSOLETE | Contrat de modèle externe expérimental |
| test_i1_natural_m11_cold_recovery.py | KEEP | Naissance actuelle et reprise M11 authentifiée |
| test_i1_source_snapshot.py | KEEP | I0 inchangé, fork I1 indépendant |

`KEEP` ne signifie pas que l'ancienne campagne est étalon scientifique : seule sa propriété logicielle explicitement identifiée est maintenue. Les `MOVE` et `REPLACE` sont des classements sémantiques, sans renommage physique systématique ; cela évite de casser les usages d'archive.

Les workflows historiques `.github/workflows/i1-*.yml`, hormis le nouveau `i1-current-ci.yml`, sont à invocation **manuelle uniquement** sur cette branche ; les archives restent accessibles pour enquête, mais aucune cohorte invalidée ne doit bloquer la PR. Les autres workflows, particulièrement I0 et les tests transversaux partagés, restent présents. La CI générale `ci.yml` conserve son mode explicite `ci-full` qui contient des tests historiques et ne doit pas être pris comme certification scientifique de I1.

## Contrat de test actuel

Le testeur `scripts/test_i1_ci.py` utilise le moteur généré par `scripts/build_i1_fork.py`, les vrais moteurs d'exécution et WorldBody, de vrais identifiants `i1:` et des WAL séparés.

Commandes depuis la racine après `python -m pip install -e .` :

```bash
python scripts/test_i1_ci.py --mode smoke --seed 246 --junit reports/i1-smoke.xml
python scripts/test_i1_ci.py --mode full --seed 246 --junit reports/i1-full.xml
```

Le code retour zéro signifie que les assertions exécutées ont réussi. Le JUnit contient le scénario, la classe, l'erreur et la graine en attribut de suite ; la reproduction nécessite la même révision, la même graine et le même mode. Une nouvelle méthode `test_...` se place dans `CurrentI1` si rapide, ou `FullI1` si approfondie. Chaque naissance possède un répertoire d'exécution propre. Pour tester la sensibilité du testeur, `--self-test` déclenche intentionnellement une assertion invalide et une exception : le code retour doit être non nul (ne jamais intégrer comme succès).

Les validations actuellement codées couvrent la naissance naturelle, l'unicité des propriétaires, la perception locale sans oracle, les pas réels, la chaîne WAL, la physiologie / collection / ingestion / boisson **comme contrôles du moteur physique et non décisions imposées à l'individu**, la privation, la mort sans résurrection, la projection de tempérament et les formes publiées vides strictement consultatives. La stabilité sur plusieurs vies est abordée dans FULL. Les protections techniques I0 / fork sont dans le workflow dédié.

## Lacunes à ne pas camoufler

- L'autonomie réelle à consommer et à boire sous des besoins variés, et la remontée des effets physiques vers l'apprentissage, nécessitent des scénarios supplémentaires sur la vie canonique.
- La publication active **non vide** après six passages facturés et la synchronisation de chacun des quatre propriétaires sont insuffisamment couvertes par le nouveau SMOKE.
- La reprise M11 actuelle et ses corruptions adversariales doivent être exercées en CI actuelle via le test maintenu ou un remplacement autonome.
- Les garanties de déterminisme s'appliquent uniquement aux paramètres effectivement figés ; un taux de survie passé ne valide rien.
- Les `tests/test_stage*.py` mélangent des propriétés I0 / partagées ; leur classification exhaustive reste distincte des 19 fichiers préfixés I1.
- La réussite de workflows scientifiques historiques, ou une CI générale sautée en PR brouillon, ne valent pas validation de la nouvelle suite.

## Diagnostic des CI précédentes

Au SHA initial, les workflows A2.36, A2.37, A2.37-R1 et D1 échouaient sur `RecoveryBlocked: unsupported runtime: additional mutable/WAL owners not coordinated` lors de naissances M11 expérimentales. Le test de décision synthétique de l'ancien workflow d'isolement attendait de pouvoir poursuivre alors que la trace de l'ingestion aboutissait à `dead`. Ce n'est pas un motif pour restaurer un individu mort. Le nouveau testeur a initialement détecté une erreur de test (accès au champ inexistant `ParametresTemperament.temperament`) ; l'assertion a été corrigée pour vérifier les paramètres projetés réellement exposés. Tous les autres tests SMOKE avaient réussi dans ce premier run.

Les liens de CI doivent toujours être lus sur le **dernier SHA** de la PR ; aucun résultat historique ne confirme une exécution ultérieure. Le dépôt I0 et `src/lab` n'ont pas été modifiés dans cette campagne.

## Exécution constatée de la nouvelle CI (2026-10-17)

Sur le commit `2ece981fc4160e4d1c3a4bd0610be184afd844c2`, le run [#39029365995](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39029365995) est **success** sur Python 3.11 et 3.12, en 11 secondes environ par job. À chaque version : 10 tests SMOKE actuels réussis, auto-test contrôlé confirmant 1 assertion invalide et 1 exception détectées, 1 test de reprise M11 canonique réussi, 4 tests d'isolement du fork et le contrôle Stage6 I0 réussis. Rapports JUnit déposés comme artifacts. Le workflow général `CI` reste **skipped** en PR brouillon : son absence d'exécution n'est pas un succès.

La campagne ne revendique pas de validation scientifique complète ni de couverture de tous les comportements émergents. Le test FULL n'a pas encore été exécuté sur ce commit. Les contrats de publication active non vide / continuité de tous propriétaires et l'autonomie de l'ingestion restent des travaux ouverts.

Aucun fichier `src/i0/**` ni `src/lab/**` n'a été modifié. PR #246 encore brouillon, non fusionnée.
