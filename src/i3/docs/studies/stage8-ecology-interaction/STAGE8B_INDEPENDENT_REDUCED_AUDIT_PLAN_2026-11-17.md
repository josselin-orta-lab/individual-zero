# Stage8-B : contre-calcul indépendant des statistiques écologiques (lecture seule)

**Date de création : 17 novembre 2026, avant le verdict Stage8-B.** Ce module est un contrôle secondaire développé sur une branche distincte, **pas** un amendement du protocole exposé au commit `9f94d1c2c4170fd923ea0de68761bed2ac3d8377` et **pas** une nouvelle étude. La campagne originale est [Actions #44060101150](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44060101150), issue [#1433](https://github.com/josselin-orta-lab/individual-zero/issues/1433). Au moment de l'écriture, les répétitions techniques Python 3.11 et 3.12 étaient en cours, la cohorte scientifique **non née**.

## But et entrées

Recalculer séparément, sans importer le réducteur Stage8-B ni le moteur i3, le **test omnibus Hotelling T²/F(2,30)** à partir des 32 observations G2 × trois familles écologiques publiées dans les résultats scellés. Confronter chaque statistique et le verdict aux champs de sortie, sans supprimer les populations négatives.

Après la conclusion de la campagne, fournir trois entrées **extraites sans altération** des artéfacts de la **même et unique** exécution :
- `SCIENCE_PLAN.json` : le plan scientifique publié avant naissance, SHA d'allocation, 192 identités de mondes G2 réservées et méthode p<0,025.
- Racine de l'archive scientifique extraite, incluant `CLAIM.json` et `SCIENCE_FINAL.json`.
- `SCIENCE_RESULT.json` : les 32 `all_population_statistics` et le `primary` publié.

```bash
PYTHONPATH=src python -m i3.lab.stage8b_independent_reduced_audit \
  /read-only/plan/SCIENCE_PLAN.json \
  /read-only/originals \
  /read-only/result/SCIENCE_RESULT.json
```

Le contrôle valide la source Git originale, l'empreinte canonique d'allocation, la réservation des **192** coordonnées `(population,family,repeat)`, l'identité du `CLAIM`, les SHA-256 du résultat final et la cohérence des **32×3 différences écologiques avec les 32 différences G2**. Il recalcule en Python standard la covariance des deux vecteurs de contrastes, le T², F, sa probabilité bilatérale, les moyennes et signes par famille, puis vérifie qu'aucun nombre ne diffère du résultat exposé. L'expérience peut être favorable **ou défavorable** : une baisse ou un effet nul n'est jamais supprimé.

**Limite importante, à ne pas masquer : ce script ne relit pas les 23 040 gzip natifs et n'atteste PAS leur contenu individuellement.** Son champ `original_lives_rehashed` vaut toujours **0**, même lorsqu'il conclut `READ_ONLY_REDUCED_ROWS_REPRODUCED`. Une telle réussite vérifie **les sorties réduites et leur liaison SHA au plan**, et non une seconde réduction complète depuis les vies. Cette vérification doit être suivie d'un audit original-level distinct si l'on veut une seconde attestation des 23 040 vies. Ses tests synthétiques sont **sans World, sans vie nouvelle et sans moteur** ; réussite CI ≠ résultat scientifique.

En cas de discordance : `AUDIT_MISMATCH/NO_NEW_VERDICT`, conserver intégralement le résultat original, ses métadonnées et tous les cas négatifs ; n'autoriser aucun nouveau tirage de graines, replay ou déplacement du critère principal. Le statut scientifique d'origine Stage8-B dépend exclusivement de son **protocole prospectif**, même si un audit échoue. Stage8-A positif moyen et Stage7 négatif directionnel restent `CLOSED_NO_RETRY`. I1 actif, i3 référence non promue, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`. La preuve interne GitHub n'est pas une attestation indépendante externe.
