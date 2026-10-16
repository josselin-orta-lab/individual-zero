# A2.30-U : relecture indépendante des archives S et T et contrôles de falsification

**15 octobre 2026.** Préenregistrement U `107c75346e6276c772434cf67f1d09c40010190b` **après les résultats S/T connus, avant code**. Les témoins sources sont les artefacts immuables des runs originaux [S #38740205272](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38740205272) et [T #38741620906](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38741620906), **Python 3.11 et 3.12**, plus le corpus d'entraînement antérieur et figé P du run #38730415503.

## Historique des contrôles et correctifs de l'auditeur

La première [CI U #38742590351](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38742590351) a échoué sur **deux tests adversariaux mal définis**, avant l'exécution finale de l'audit : l'un remplaçait un booléen `False` par `False` et ne falsifiait aucune donnée; l'autre détectait une fausse sûreté via la modification d'une empreinte SHA plutôt que via un motif explicite de certification. Ces tests ont été corrigés **sans modifier les données S/T, le modèle P ou les métriques** aux commits `c54a022eae47377ffe38d5b5e088ab5fc19765ea` et `cfdd26ea8cf375806ffd430df8caef377c2c9eb3`.

La [CI de réception U #38742839615](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38742839615) passe **Python 3.11 et 3.12**, résultats identiques. Les contrôles négatifs altèrent réellement des observations ou critères et vérifient les refus.

## Méthode sans réexécution des mondes

`audit_stage12_issue110_b_a230u_independent.py` ne charge **ni les runners S/T**, ni `LaboratoryJointPrefixModel`, ni `WorldBody`, ni `Stage6Runtime`, ni `Oracle`. Il reconstitue indépendamment les quatre branches alimentaires P à partir des **48 témoins de son corpus historique**, vérifie les empreintes canoniques des reçus S, le chaînage perception-action-conséquence, et recalcule séparément les 36 comparaisons accessibles S et les 40 résultats alimentaires T.

- Les six fichiers JSON d'origine sont **strictement identiques octet par octet entre les artefacts Python 3.11/3.12 de leur cohorte**.
- Source P originale : `a230p-training-manifest.json` SHA-256 `f706cd25a31b8f716c4bb0a5a7e617bed87c0b8b47577d8b9dd31221cf23839e`.
- **S `a230s-worlds.json`** : `8631839f8c9e253601b1b9f203d2fabf55672eefd2b7b17f330b1a5b5f8802bf`.
- **S `a230s-pairs.json`** : `8331090bed8c56d8c3a7e6b85f76bbf99a9c11380a1b882f37dae06c7d95370b`.
- **S `a230s-summary.json`** : `b60935224306279f3b2ac74ddf88407dd95b56aeb1760cdc36c992e488464d57`.
- **T `a230t-worlds.json`** : `c418b9aef5b86d67e599520ea1e1620c2a0970f11d9253b75429b38c91eacada`.
- **T `a230t-paired.json`** : `58c042d323e82e6772f53f58cbc8af5631250f03e155ccdacd94d46fd81b6dde`.
- **T `a230t-summary.json`** : `37885824412243b9186d51a29e2e82799c481e8b20d4eab1b5381a3966534f62`.

## Résultats recalculés

| Cohorte et propriété | Preuve retrouvée par U |
|---|---:|
| S, mondes/observations de transitions d'origine | **36 / 104** |
| S, décès externes et postmortem non vécu | **8 / 0 capture vécue postterminale** |
| S, comparaisons premières personnes | **36**, dont **20 distinguables**, **16 sans distinction commune avant fin mortelle** |
| T, mondes/observations de transitions d'origine | **40 / 132** |
| T, branches physiques P conservées pour la nourriture | **4** |
| T, gains corporels alimentaires physiques avec survie | **24** |
| T, faux succès du proxy optimiste | **16** |
| T, morts externes | **8** |
| T, certifications de sécurité | **0** |
| Nouveaux mondes/nouveaux pas physiques exécutés par U | **0 / 0** |
| Nouvelles vies autonomes d'I0 exécutées par U | **0** |

Les 13 tests de falsification incluent : faux hash physique, capture postmortem ajoutée comme vécue, date de mort fabriquée, prétendue connaissance alimentaire précoce, input du modèle falsifié, certification `safe` inventée, résultat vécu postmortem créé, succès alimentaire fabriqué, branche de progrès réellement positive altérée, duplication de monde et métrique d'agrégat falsifiée. Tous les cas incorrects sont rejetés.

## Limite de validation et décision

Un auditeur de JSON seul **ne peut pas certifier indépendamment que `WorldBody.apply` a produit chaque transition** : U démontre l'intégrité, l'origine et la cohérence interne des reçus archivés, leur reproductibilité d'évaluation, et la séparation perception/savoir externe. Les mondes originaux sont ceux de S et T, déjà exécutés par leurs scripts et CI. L'accord des deux interpréteurs n'est pas une preuve statistique d'un risque physique général.

**U : PASS de validation indépendante des données enregistrées ; A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN.** Aucune modification d'Equipment, du planificateur Stage6, des attributs d'agence subjective ou de la norme MVP n'est permise par ces observations.
