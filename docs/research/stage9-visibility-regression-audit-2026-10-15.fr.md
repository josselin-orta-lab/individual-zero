# Stage 9 : régression du témoin de cause lointaine, visibilité subjective préservée

**15 octobre 2026.** Spécification normative : `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, frontière DC-05. Le présent correctif porte seulement sur les **attentes du test**, sans aucun changement à `WorldBody`, Perception, CausalModel, Stage6, l'Oracle ou l'évaluateur.

## Reproduction avant changement

- Contrôle `main cb630f6edffab1aecb4630e2b7da2369bb593118`, branche `audit/ci-main-baseline-20261015`, workflow `a230-main-legacy-regression-control.yml`, Python 3.11/3.12 : **un échec Stage9 sur huit**, identique à la suite complète de la PR #201.
- L'ancien témoin `toxic_berry_far_creature` place physiquement une créature à **distance Manhattan 5** après une attente, puis exécute réellement `manger(berry_a)` empoisonné. L'assertion fautive cherchait cette créature dans `PerceptualCapture.visible_entities`.
- `WorldBody.capture_local()` autorise seulement les entités à **distance Manhattan au plus 1**. La créature distante reste donc absente des sensations autorisées. Exiger qu'elle soit visible revient à exiger une fuite d'information interdite.
- Diagnostic sur le monde réellement exécuté : capture sans créature distante, intégrité corporelle **100 → 90**, nourriture **60 → 70**, et **une** association alimentaire `ambiguous_food_association` effectivement admise; aucun crédit de sûreté `toxic:berry_a` publié.

## Correction attendue et contrôle

Le **même** monde, la **même** créature et la **même** ingestion sont conservés. Le test vérifie désormais que la créature lointaine **n'est pas perçue**, puis maintient les assertions préexistantes : un témoin alimentaire vécu est admis, le dommage est observé, la provenance `toxic:berry_a` est conservée, le statut est ambigu, aucune règle toxique déterministe n'est publiée.

Les témoins voisins restent inchangés : une créature effectivement proche et visible interdit toute conclusion alimentaire non justifiée; une créature sur la propre case est visible; un danger caché et une baie toxique peuvent être sensoriellement indiscernables.

**Portée :** réparation d'une fixture épistémiquement obsolète, pas calibration ou validation scientifique du Stage9. Les sept échecs Stage4 et l'échec Stage5 observés sur le même `main` sont des dossiers distincts ([issue #203](https://github.com/josselin-orta-lab/individual-zero/issues/203)). La PR #199 est hors périmètre et doit rester intacte.

## Critère avant intégration

Vérifier sur le SHA final les tests `test_stage9_concurrent_cause_audit.py` sous Python 3.11 et 3.12, les contrôles indépendants existants DC-05, puis confirmer sur `main` que la chaîne de journal et les composants cognitifs sont restés inchangés.
