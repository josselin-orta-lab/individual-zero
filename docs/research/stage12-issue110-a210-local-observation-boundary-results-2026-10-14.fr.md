# Individual Zero #110 : A2.10a, correction épistémique des entités non locales

**14 octobre 2026. Verdict scientifique global Stage12 PARTIAL.** Préenregistrement `ee04443a0761b9f4ab731b07c9dfb12e5484ad46` avant code. Source d'exécution `6fe5307442ad5a4a6d1c959c96c5b6a8983cda09`. [GitHub Actions #38602506664](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38602506664) **SUCCESS** sous Python 3.11 et Python 3.12. Chacun exécute les **mêmes** 16 vies ×42 pas (672 transitions physiques uniques, non 1 344), zéro échec d'audit/WAL/GA/A2, plus tests de perception/physique. Deux interpréteurs ne constituent pas deux séries de seeds aléatoires indépendantes.

## Défaut reproduit avant correction

Dans les archives originelles A2.9 `sustained_early_gain1p6`, à t1 l'individu est physiquement à **(2,2)** et ne voit que sa case courante et les quatre voisines dans la capture locale. Pourtant son `S_t` au cycle 1 contient `observation:berry_a:3:1:1:1` ; la baie (3,1) est distante de Manhattan 2. `WorldBody.capture_local` recensait sans restriction `visible_entities` pour **toutes** les ressources, sources d'eau, créatures et abris du monde. `SymbolicPerception` transmettait ces entités sous apparence d'observations déjà vécues.

Ceci n'était **pas** un accès direct à l'Oracle ou au journal externe, mais violait la frontière épistémique revendiquée de perception locale. L'audit technique des frontières de perception est distinct de l'audit de chaîne causale, qui peut être cryptographiquement valide même lorsqu'un contenu n'aurait pas dû être visible.

## Correction minimale réalisée

Dans `src/lab/world.py` seulement, le flux `LocalWorldState.visible_entities` est désormais limité à `|x_entité - x_i0| + |y_entité - y_i0| <= 1` au moment de la capture. Tous les types (baie, eau, créature, abri) sont couverts ; `current_resources`, `adjacent`, commandes, effets physiques, `WorldBody.ground_truth`, journal, WAL, accès Oracle séparé et spécification normative v1.3.1 ne sont **pas** modifiés. Les nouveaux tests vérifient la disparition d'une baie hors du rayon local puis son apparition après un **déplacement réellement exécuté**. Aucun nouveau mécanisme de mémoire ni aucune information future n'est introduit.

## Rejeu A2.9 borné et contrasté

La cohorte est identique au plan A2.9 (profils `restored/sustained`, gain pré-natal `1.0/1.6`, quatre programmes externes `none/early(t3)/original(t4)/persistent(t20)`). Chaque condition est une **nouvelle naissance**. Les deux Python rapportent exactement les mêmes agrégats physiques :

| Profil | Obstacle | Ingestions avant à gain 1.0/1.6 | Ingestions après à gain 1.0/1.6 | Sites distincts après à gain 1.0/1.6 |
| --- | --- | --- | --- | --- |
| restored | none | 1/1 | 1/1 | 31/31 |
| restored | early | 1/1 | 1/1 | 30/30 |
| restored | original | **1/1** | **0/1** | 30/30 |
| restored | persistent | 0/0 | 0/0 | 30/30 |
| sustained | none | 0/1 | 0/1 | 33/31 |
| sustained | early | 0/0 | 0/0 | 32/32 |
| sustained | original | 0/0 | 0/0 | 32/32 |
| sustained | persistent | 0/0 | 0/0 | 32/32 |

Tous les mondes avec obstacle ont un mouvement physique bloqué authentique. **Divergence observable** : en `restored/original/gain1.0`, l'ingestion historique disparaît après correction locale. Les recherches `incomplete_model` y montent de 8 à 17 (aux comptes des diagnostics, non à des échecs physiques inventés). `restored/original/gain1.6` continue une ingestion vécue, `incomplete_model=8`, 30 sites visités. `sustained` échoue toujours après obstacle, même levé à t3 ; `sustained/none/gain1.6` continue d'ingérer une baie avec bénéfice corporel modeste.

## Interprétation limitée

Le système antérieur disposait d'une entrée de ressource non locale, susceptible d'influencer l'état cognitif et la décision. La correction prouve qu'au moins une trajectoire était sensible à cette information indue. Elle ne démontre pas qu'un manque de mémoire est la **cause unique** de l'échec alimentaire; les limites de couverture Equipment sont également observées. Les campagnes antérieures (A2.5–A2.9) demeurent historiquement reproductibles dans leur ancien code, mais **ne doivent plus servir à valider la perception localement bornée**. Les chiffres avant/après ne sont pas un test d'ablation de mémoire. Le résultat négatif `restored/original/gain1.0` reste conservé; ne pas restaurer les ingestions en réexposant des ressources distantes.

**C1 PARTIAL, C2 PARTIAL, C3 PASS borné à 42 pas, C4 PARTIAL avec échec sustained, C5 PARTIAL, C6 INCONCLUSIVE sur cette nouvelle frontière, C7 PARTIAL (cross-Python PASS mais seeds indépendants non validés), C8 PASS borné au filtrage des entités locales. GLOBAL Stage12 PARTIAL.**

## Décision de suite

Ne pas clore l'issue #110 ni recevoir Stage12. Le prochain travail A2.10b, à préenregistrer séparément, devra examiner la mémoire d'opportunités **réellement** observées aux captures successives, leur obsolescence physique, la planification routée **sous UC et veto sécurité**, les alternatives et la différence avec le modèle Equipment incomplet. Aucun `collecter` ni `manger` imposé, aucune certitude d'innocuité d'une baie non expérimentée et aucun signal Oracle accessible à I0. Toute modification de contrat normatif v1.3.1 est à soumettre à décision explicite.
