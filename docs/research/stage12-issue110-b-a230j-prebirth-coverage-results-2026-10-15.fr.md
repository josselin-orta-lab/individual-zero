# A2.30-J : augmentation de couverture prénatale physique, résultats appariés

**15 octobre 2026.** Préenregistrement enregistré avant code au commit `2670af2d66bae3a5b46107d0cd3cd7c85f5184fc`. Code de l'expérience `e08dc08e79b9c1a465dee9a4f9fd86ce7e94af99`. La première [CI #38720683267](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38720683267) échoue **uniquement** sur le nombre déclaré dans les tests d'intégrité (43 attendu contre **46 réellement enregistré**), avant tout lancement des vies A2.30-J. Le contrôle est corrigé dans `73d04843735bdfd60ddbf40ae064057847b614fb`, sans changer les recettes, les seuils, l'horizon, le monde ni le plan expérimental. La [CI définitive #38720764403](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38720764403) est **SUCCESS sous Python 3.11 et 3.12**, avec comptes identiques et audits par vie effectués.

## Intervention prospective et provenance

**16 nouvelles naissances autonomes**, quatre profils de faim × obstacle libre/A2 × deux modèles figés avant naissance, 32 transitions par vie = **512 vrais pas physiques**. Le traitement conserve les quatre observations historiques `north/east/collecter berry_a/manger berry_a` et ajoute **46 transitions effectivement appliquées** dans **14 mondes d'entraînement pré-nataux indépendants**, selon les recettes prédéclarées. Le contrôle conserve l'Equipment historique. Les deux modèles gardent la table exacte et refusent toujours `manger berry_b` et toute entrée corporelle non entraînée. Aucune commande n'est forcée durant les vies; le code I0 et les règles normatives ne changent pas. Les deux versions Python reproduisent la **même** matrice : ne pas les compter comme 32 vies ni 1 024 pas scientifiques indépendants.

## Résultat vérifié

| Profil / monde | Recherches Stage6 OFF/ON | Recherches sans premier pas connu OFF/ON | Première arête prédictible OFF/ON | Repas physiques OFF/ON |
|---|---:|---:|---:|---:|
| restored, libre | 2 / 2 | 0 / 0 | 1 / 1 | 1 / 1 |
| restored, obstacle A2 | 11 / 11 | **8 / 5** | **2 / 5** | 1 / 1 |
| sustained, libre | 27 / 27 | 24 / 24 | 3 / 3 | 1 / 1 |
| sustained, obstacle A2 | 28 / 28 | 27 / 27 | 1 / 1 | 0 / 0 |
| episodic, libre | 29 / 29 | 25 / 25 | 4 / 4 | 1 / 1 |
| episodic, obstacle A2 | 29 / 29 | 27 / 27 | 2 / 2 | 0 / 0 |
| marginal, libre | 29 / 29 | 26 / 26 | 3 / 3 | 0 / 0 |
| marginal, obstacle A2 | 30 / 30 | 28 / 28 | 2 / 2 | 0 / 0 |
| **Total** | **185 / 185** | **165 / 162** | **18 / 21** | **4 / 4** |

**8 ingestions attestées au total**, avec **4 par bras**, et **4 étapes de gain alimentaire dans chaque bras**. Les **12 jugements B par bras** ne changent pas. Les 16 vies sont terminées par l'opérateur expérimental (`experiment_stopped`), **pas par une mort**. Aucune réussite alimentaire n'est inventée pour un profil sans ingestion.

Les effectifs `first_step_available_searches` décomptent les recherches ayant **au moins une première arête prédite** : la recherche `restored/free` a aussi un autre statut distinct et ne constitue pas une partition exhaustive de toutes les recherches par ces deux seuls compteurs. Les comptes d'arêtes portent sur des tentatives susceptibles de se répéter, pas sur des informations indépendantes.

## Conclusions discriminantes et limites

- **J1, effet logiciel de couverture : soutenu localement.** Trois recherches `restored/A2` cessent d'être bloquées dès leur racine dans le modèle élargi, avec un nombre de recherches identique. Sur les sept autres paires, le compte des racines bloquées est stable. Le gain total reste **3 sur 185 recherches** par bras, et ne démontre aucun comportement alimentaire nouveau.
- **J2, transfert alimentaire : non soutenu.** Aucune ingestion supplémentaire, aucun gain alimentaire supplémentaire, aucun jugement B additionnel. Le protocole ne permet pas d'affirmer une amélioration de l'agence causale subjective.
- **J3, lacunes de représentation : soutenu descriptivement.** Malgré les 46 nouvelles transitions par configuration, la majorité des états de départ interrogés restent non couverts par la table exacte, notamment dans les situations de faim soutenue, épisodique ou marginale.
- **J4, sûreté :** les journaux WAL, la vérification indépendante, la frontière des entrées non entraînées et les contrôles B n'ont signalé aucun défaut dans cette matrice. Les comptes agrégés ne suffisent **pas** à affirmer que toutes les trajectoires exploratoires ou tous les coûts UC sont identiques ; le préenregistrement de l'audit offline A2.30-K vise cette question.
- **Causalité :** les identités de naissance sont distinctes entre les deux bras, et la matrice est déterministe : elle établit un contraste expérimental apparié de configuration, **pas** un effet causal général ni une estimation statistique sur des graines indépendantes.

**Verdict : A2.30 PARTIELLE / Stage12 PARTIAL / issue #110 OPEN.** La correction Stage6 A2.30-I reste exclusivement diagnostique. Ni extrapolation dangereuse du modèle ni élévation artificielle du taux de succès ne sont justifiées. La PR #187 reste en brouillon, sans fusion ni réception opérateur.
