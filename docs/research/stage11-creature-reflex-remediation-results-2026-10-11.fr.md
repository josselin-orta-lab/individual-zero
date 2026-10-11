# Stage 11 : réparation du réflexe d'évitement, résultat de développement

**Date :** 11 octobre 2026. **Classification :** logiciel public, non scientifique, non held-out et non Golden. Référence normative inchangée : `docs/architecture/reference/en/mvp-specification-v1.2.1.md` §9.2. **Stage 9 reste NO-GO scientifique.**

## Antériorité et séparation des deux expériences

La première campagne physique du trajet modifié était enregistrée [avant expérience](stage11-stale-frontier-route-safety-protocol.en.md) et son contre-exemple [est préservé ici](stage11-stale-route-safety-first-results-2026-10-11.fr.md) ; aucune conclusion négative n'a été effacée. Son correctif **de mesure uniquement** a été validé au commit `68921e5b`, [CI #38120720084](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38120720084), **818/818 Python 3.12 PASS** et smoke PASS. À cette étape, le réflexe vers la case occupée était toujours présent.

La réparation normative indépendante a été [préalablement déclarée](stage11-creature-reflex-normative-remediation-protocol.en.md), commit `04612911`. L'implémentation commune `ActionControl.reflex` n'admet désormais un mouvement direct que s'il **augmente strictement la distance au danger adjacent le plus proche**. Si aucun voisin réellement observé n'éloigne l'individu, aucun faux réflexe d'évitement n'est envoyé ; la délibération ordinaire prend le relais, sous veto canonique habituel.

**Code vérifié :** `8210af6960ccc52b01ea8dee1564a2a2bfabd179`. [CI #38120897916](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38120897916) : **826 tests Python 3.12 PASS**, bootstrap smoke PASS, Python 3.11 complet et Goldens **NON EXÉCUTÉS**.

## Comparaison physique sur dix pas

| Variante | Avant correction de réflexe | Après correction de réflexe | Retour au carrefour après correction | Dommages de zone |
| --- | --- | --- | --- | ---: |
| Sans créature | retour routé via (3,2), puis (2,2) et branche sud | même chemin | Oui | 0 |
| Créature persistante en (3,2) dès le pas 3 | réflexe direct vers la case occupée, puis branche sud | deux déplacements vers l'est puis **huit pas attendre** sur (4,2) | **Non** | 0 |
| Créature supprimée au pas 5 | réflexe direct au pas 3 et branche sud | même immobilité sur (4,2), y compris après suppression | **Non** | 0 |
| Danger caché en (3,2) dès le pas 3 | même trajet routé que témoin, dommage réel | même trajet routé que témoin, dommage réel | Oui | **10** |

Le routage d'Exploration n'a jamais émis d'option appliquée directement sur la case occupée ; **le comportement fautif venait du réflexe**, auquel l'ancien classement des mouvements `passable` autorisait de se rapprocher de la créature faute de meilleure option. Sa réparation générale ne retouche aucun seuil de sécurité, ne consulte aucun état privé du monde et ne crée aucune capacité cognitive particulière au scénario. Les tests nouveaux couvrent l'impasse, les alternatives éloignantes, les égalités et plusieurs créatures.

En parallèle, la version corrective met en évidence un **manque distinct** : lorsqu'une créature disparaît au pas 5, une observation géographique enregistrée pendant son occupation peut rester obsolète. L'individu ne reprend pas le chemin malgré la réouverture physique. Ne pas présenter cela comme une incapacité générale à apprendre ; c'est une limite locale d'actualisation du graphe observé.

## Empreintes des journaux après correction

| Variante | SHA-256 du journal |
| --- | --- |
| Témoin | `9ebcd79f0bfd90bf70de75a97ef7a323eb79d7e322a1e1b3db3fcaf514cdc5df` |
| Créature persistante | `d1456f1aee545941041af7b86200186de14c26aa84c002005878d92626379092` |
| Créature retirée | `6372e6a7ac5d2430d16ff62e29a313f4ef8a1ad00d3c38d187ae8cc7272901c2` |
| Danger caché | `e65e11899990bd59ef24ed4f7332c26f4f77117a9b540a7c0e4889de5121bfc6` |

## Reproduction

```sh
python -m pip install -e .
python -m unittest tests.test_stage11_creature_reflex_remediation tests.test_stage11_stale_route_safety -v
python -m lab.stage11_stale_route_safety_probe
```

**Prudence :** le correctif modifie un composant **commun aux stages antérieurs** sur la branche vNext, non un module exclusif Stage 11. Les comparaisons historiques restent rattachées à leurs commits antérieurs ; la validation de compatibilité exhaustive sous Python 3.11, les Goldens et l'évaluation scientifique doivent encore être effectués séparément. PR #25 brouillon, dépôt privé, Stage 11 **EN COURS**, Stage 9 **NO-GO**.
