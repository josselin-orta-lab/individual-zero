# Stage8-B : audit indépendant COMPLET des 23 040 vies natives G0/G1/G2

**Statut à la rédaction du 17 novembre 2026 : CODE ET TESTS SYNTHÉTIQUES SEULEMENT, AUCUN AUDIT BRUT EXÉCUTÉ.** L’expérience prospective reste celle du run [#44060101150](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44060101150), source gelée `9f94d1c2c4170fd923ea0de68761bed2ac3d8377`. Cette vérification post hoc reste entièrement séparée et **ne modifie ni ses vies ni son protocole**.

## Niveaux de preuve

La [PR #1435](https://github.com/josselin-orta-lab/individual-zero/pull/1435) vérifie indépendamment la statistique T² de Hotelling sur les tableaux **déjà réduits**, mais annonce honnêtement `original_lives_rehashed=0`.

Le nouvel outil `stage8b_independent_original_audit.py` ajoute un niveau distinct : **relecture de tous les 23 040 gzip originaux**, sans appel au générateur Stage8-A/Stage8-B, ni au moteur World, ni au mutateur génétique. Il réutilise le vérificateur de **structure et SHA des enregistrements** du précédent Stage7, puis refait les sommes écologiques et le test statistique indépendamment du réducteur expérimental.

Pour chaque panneau de 16 populations, l’audit valide :
- l'empreinte SHA256 des plans scientifiques et techniques, la source Git native d’origine, les 288 allocations World, 384 fondateurs et 1 536 tirages/mutations planifiés, et l’absence de collision des graines ;
- **9 phases scellées par panneau**, G0/G1/G2, trois manifestes et les reçus techniques G/S/R ; donc **18 phases** dans l'expérience ;
- les 11 520 gzip par panneau, leurs empreintes comprimées/décomprimées, les identités individuelles, génomes, graines, World, traces de longueur effectivement vécue, morts et censures à horizon 400, et la dette cognitive énergie/vigilance ;
- la liaison des **192 réservations G2** au plan exact des mondes G2 réellement utilisés, avec populations/familles/répétitions appariées ;
- les **9 216 originaux G2 relus une seconde fois pour réagréger indépendamment** 32×3 contrastes d’écologie (48 vies G2 par bras et famille), pour vérifier durées et fractions censurées publiées ;
- les 32 lignes complètes G0/G1/G2 et les 32 vecteurs (depletion−stable, pulse−stable) recalculés, avant de reproduire séparément l’unique test omnibus préenregistré `p<0,025`, la covariance 2×2, T², F(2,30), les 3 moyennes F0 et les comptes de populations favorables.

**Sortie de succès attendue si les données concordent** : `READ_ONLY_ORIGINALS_REPRODUCED`, `native_original_lives_rehashed=23040`, `new_lives=0` et le verdict biologique original **sans le modifier**. Tout écart technique : sortie non nulle, enquête transparente, pas de nouveau verdict biologique ni de relance. L’audit doit réussir avec un statut biologique positif **ou négatif**, mais jamais masquer les négatifs.

## Usage (après publication définitive de TOUTES les archives scientifiques)

Télécharger/extraitre, **sans modifier les ZIP** et depuis la même tentative unique :
1. `stage8b-science-preexposure-44060101150` avec `SCIENCE_PLAN.json`.
2. `stage8b-science-originals-44060101150` contenant `CLAIM.json`, `SCIENCE_FINAL.json`, `INNER_PLAN.json`, `INNER_CORE.json`, `NATIVE_ORIGINALS/PANEL_0, PANEL_1`, etc.
3. `stage8b-science-result-44060101150` contenant `SCIENCE_RESULT.json`.

```bash
PYTHONPATH=src python -m i3.lab.stage8b_independent_original_audit \
  /read-only/preexposure/SCIENCE_PLAN.json \
  /read-only/originals \
  /read-only/result/SCIENCE_RESULT.json
```

Le workflow `i3-stage8b-readonly-original-audit-20261117.yml` présent dans la PR **ne doit être fusionné qu’APRÈS la publication réussie des trois artefacts ci-dessus**. Son déclenchement initial sur `main` n'ouvre **aucun** World et relit seulement la source historique complète. Ne pas fusionner s’il manque un reçu, une archive, une empreinte ou une cohorte, et ne jamais déclencher une expérience de remplacement pour obtenir un audit favorable.

## Limites interprétatives

Le contrôle revalide les **enregistrements scellés**, pas la fidélité des actions motrices via un replay du monde, ni l’authenticité off-host des graines, ni l'indépendance statistique ou la normalité multivariée. Le pont de vérification originale du Stage7 contrôle l’ABI et les corps, mais cet audit n’est pas une revalidation indépendante du **choix parental ou des mutations** au niveau de leur mécanisme : ces derniers ont été contrôlés dans le scellé de l’expérience, pas recomputés par ce module. L’interaction demeure limitée aux **trois familles F0** ; un non-rejet de H0 ne démontre pas l’égalité ou l’équivalence.

`INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED`. Stage8-A reste positif pour le gain moyen selon sa règle ; Stage7 reste négatif selon la sienne. I1 est actif, i3 n'est pas promu, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`. Les résultats défavorables restent conservés dans leurs originaux.
