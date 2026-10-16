# Audit chronologique A2.30-P/Q/R : restauration des contrôles historiques Stage 4/5

**Date : 15 octobre 2026.** La PR #189, plus ancienne PR ouverte, ne doit pas être fusionnée sur la seule foi des contrôles scientifiques A2.30-P/Q/R. Le run général [#38806465721](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38806465721), deuxième tentative sur `c0e41be2279c8c4b8a574df32cfe5a11f99fe5af`, a terminé avec 8 échecs sur 1 644 tests. Les fichiers incriminés étaient **byte-identiques à `main`**, et les échecs étaient les anciens scénarios Stage 4 (sept cas) et la batterie de persévérance Stage 5 (un cas). Aucun échec n'est imputé par simple corrélation au modèle de laboratoire P.

## Correction atomiquement rattachée à la plus ancienne PR

Afin de ne pas fusionner la PR #205 avant la PR #189, cette réparation de *gate* reprend **exactement**, sans adaptation, les trois blobs source/test déjà testés dans l'intégration cumulative isolée `c5e6b91e9e1efa9ad19f0c88f37265a6fa380820` (run [#38806391990](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38806391990), Python 3.11 et 3.12, 1 621 tests par version réussis) :

- `tests/test_stage4_runtime.py`, blob `93a14e99a91bd7d61b8019693185064506e75dc7`, repris de la PR #205 : eau visible à une case, témoin négatif à deux cases, commandes et transitions physiquement attestées, pas de second comparateur inventé.
- `src/lab/stage5_reference_fixture.py`, blob `724a2ae18b003dbcfe94fe2caf08215ed8d7f3b2`, repris de la PR #216 : paramètre de disposition du monde **avant la naissance**, limité à la portée perceptive réelle, sans modification du défaut historique.
- `tests/test_stage5_trait_battery.py`, blob `de6dad9b478964b252cce16a5a2ba3b492aad488`, repris de la PR #216 : persévérance uniquement sur action réellement choisie puis empêchée physiquement, contrôle négatif d'absence d'action.

Ces changements sont strictement des réparations de témoins et de fixtures du laboratoire. Aucun `src/i0`, `EquipmentModel`, choix Stage6, diagnostic Stage9, autorité Oracle ou juge Stage12 n'est modifié. Les anciens tests de rollback Stage4 sont des témoins de **compatibilité historique non mortelle**, et ne restaurent pas les vies du runtime mortel MVP v1.3.1. Aucun résultat de batterie ne se transforme en preuve générale de sécurité alimentaire, d'agence subjective ou d'efficacité des UC.

## Gates à respecter sur cette tête exacte

Les 1 621 tests réussis sur la branche cumulative antérieure **ne valident pas rétroactivement la nouvelle tête de #189**. Exiger CI complète (ou équivalent obligatoire), Stage12 focalisé et intégré, P/Q/R archives et physique, vérification de la branche `main` et tests post-fusion. Ne pas fusionner si une validation obligatoire échoue. Après intégration, auditer les PR #205 et #216 à leur tour chronologique pour déterminer ce qui reste (workflows et rapports), et éviter les doubles correctifs.

**Science conservée :** A2.30 partielle, Stage12 PARTIAL, modèle P/Q/R externe **NO-GO** pour toute utilisation comme planificateur cognitif ou certificat de sûreté, issue #110 administrativement close mais non validée scientifiquement. Aucune modification silencieuse de la norme MVP v1.3.1.
