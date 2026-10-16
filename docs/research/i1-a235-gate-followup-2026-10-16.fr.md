# A2.35, suivi de campagne du 16 octobre 2026

## Travail effectué

- Confirmation de l'état réel de la PR #222, empilée sur #219, sans fusion et avec I0 `main` inchangé.
- Audit de la provenance Stage7 / Stage8 / I1 : un rappel n'est crédité qu'après publication admissible dans `S_t`; les épisodes doivent provenir de la vue autobiographique contrôlée DC-09, et les effets de collecte être positifs, antérieurs et autorisés.
- Nouveau protocole prospective d'arbitrage `docs/research/i1-a235-next-gate-2026-10-16.en.md`, créé au commit `2d268fe5929f1bb7c97ccf83e867f62b0af60caa`, **avant** une éventuelle cohorte de validation à deux options concurrentes. Ce document n'est pas une preuve de validation scientifique.
- Ajout de `tests/test_i1_a235_m11_recall_contract.py` et intégration dans la CI. Le test fait naître de nouveaux I1 avec rappel ON/OFF et coût 1/2 UC, puis compare leurs empreintes contractuelles M11 et les opérations de compute budget. Le code des vieilles vies et le modèle OFF restent isolés.
- [CI A2.35 au SHA exact 4e98958aa0946911406479b93df0fd01ee2d85b0](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38868028896) : **PASS Python 3.11 et 3.12**.

## Verdict nuancé

Les témoins antérieurs ont démontré un effet **sur le score de l'évaluateur** (0,35 → 0,45) après un vrai rappel de collecte. Ils n'ont observé **aucun changement de primitive physique** dans 30 commandes exécutées sur trois vies. Il serait incorrect d'appeler cela une adaptation comportementale démontrée.

Le nouveau test M11 valide **la distinction des empreintes de naissance et du prix UC**, mais ne reconstitue pas un véritable redémarrage à froid après une vie contenant des souvenirs. Le protocole prospective requiert donc explicitement ce contrôle complet, avec comparaison des hash, commandes et résultats après reprise.

Aucun Oracle, danger caché ou étiquette d'échec forcé n'est autorisé à franchir la frontière autobiographique. La mortalité reste irréversible. Les deux modèles gardent leur statut expérimental ; aucune décision de déploiement, amélioration de survie ou fusion I0 ne découle de ces tests.

## Prochaine preuve réellement discriminante

Faire naître un nouveau groupe de paires, en situation de **deux options effectivement admissibles**, garder les deux candidats visibles dans les traces de Competition, puis prouver qu'une preuve vécue antérieure peut changer le choix physique par rapport à un témoin sans mécanisme. Vérifier UC, présence de veto, capture postérieure, preuve de source et coût/survie dans les deux bras. Si aucun environnement naturel ne présente deux candidats admissibles, classer l'essai comme **non informatif**, et ne pas fabriquer une option ou biaiser un oracle pour produire artificiellement un résultat positif.

**PR #222 reste Draft, aucune fusion. I0 sur main intact. Scientific cognitive GO : refusé.**
