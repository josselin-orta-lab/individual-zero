# A2.30-ZT : contre-audit indépendant des sept archives originales de ZS

**15 octobre 2026.** Protocole ZT verrouillé **après connaissance des résultats ZS** mais **avant le code ZT** : commit `0aa82ba0d1340ffc7240fd2f45184cf9814eabcb`. ZT est **rétrospectif**, n'émet aucune prédiction nouvelle auprès du monde et ne crée aucun monde, aucune action physique ni vie I0. Son exécution d'origine sur les archives scellées est [GitHub Actions #38802545036](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38802545036), **22 tests adversariaux PASS** dans chacun de Python 3.11 et 3.12. L'auditeur est écrit en **bibliothèque standard Python seulement** et n'importe ni le runner ZS/ZO, ni `WorldBody`, ni `lab.determinism`, ni Stage6, ni Stage12Runtime ni Oracle.

## Sources contrôlées

**Run primaire ZS [#38801117723](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38801117723)**, SHA de code `804e2ebb653278f18bd85aa364015acffd3bdb0e`. L'auditeur ZT télécharge directement **quatre artefacts originaux** de ce run, deux archives de prévision et deux archives de résultats physiques. Les trois fichiers de source et le manifeste plus les trois fichiers de résultats ont les sept SHA originaux fixés dans le préenregistrement ZT. Ces **sept paires Python sont identiques octet pour octet** ; leurs octets ont été vérifiés séparément avant toute interprétation.

Après vérification de la SHA des fichiers, ZT implémente seul la représentation canonique causale SHA-256 (NFC et floats hex), réextrait les deltas des **16 exemples physiques réels de laboratoire consignés**, vérifie le modèle `d837d17d285c20ac53a55f3f78818d4f2abfa7cd387b6232e3c105bd9ac25171`, puis **recalcule chacune des 104 prévisions signées** à partir du modèle et des seules captures `preaction_first_person`.

Il joint ensuite toutes les 104 prévisions aux 104 autres reçus physiques, recompte **les 104 clés exactes inédites**, les six erreurs par champ, les décès/blessures/échecs, les 16 abstentions, les 32 paires nominales de toxicité cachée et les 24 contrôles des interventions invisibles.

| Recalcul indépendant ZT | Constats |
|---|---:|
| Exemples de formation physiquement attestés par reçus et SHA | **16** |
| Prévisions sur perceptions accessibles recalculées | **104** |
| Exemples tenus à l'écart physiquement attestés et rejoints aux prévisions | **104** |
| Clés d'état exact déjà présentes parmi les 16 entraînements | **0** |
| Prévisions numériques nominales à six champs correctes | **64/64** |
| Abstentions physiques limites | **16/16** |
| Décès, blessures, échecs de commandes cachés | **4 / 8 / 8** |
| Paires de toxicité B masquées et concordantes | **32** |
| Nouveaux mondes, nouvelles actions ou nouveaux individus par ZT | **0 / 0 / 0** |

**22 tests adversariaux PASS** de l'auditeur : refus de hash de fichier altéré, source manquante/doublée, modification re-hashée d'une prévision, certificat `safe` injecté, variable cachée dans l'entrée, exemple d'entraînement contaminé par un monde de test, faux `terminal`, faux score de succès, fausse charge UC, assimilation d'un acte de laboratoire à une naissance I0, champ futur dans le manifeste et acceptation d'une fausse chronologie. La première CI ZT était rouge **uniquement** parce qu'une assertion de négatif exigeait le mauvais texte d'erreur : la protection SHA refusait déjà la falsification; seule l'expression attendue du test a été rectifiée, sans retoucher les sept originaux, leur SHA, l'expérience ZS ou les seuils de l'audit.

## Frontière de preuve

ZT démontre indépendamment **l'intégrité des archives, les recomptages et les restrictions de la prévision**. **Il ne rejoue pas `WorldBody.apply`**, il n'évalue pas le modèle dans une nouvelle distribution physique, et **les fichiers JSON ne peuvent pas attester à eux seuls l'ordre historique des jobs**. La preuve temporelle repose sur le workflow original `needs: [seal-before-physics]`, les journaux de [#38801117723](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38801117723) et les fichiers scellés avant la première transition heldout, chacun conservé séparément. Il s'agit d'une preuve d'intégrité **plus** une preuve de procédure CI, non d'une mesure indépendante de mécanisme de causalité physique cachée.

Le contraste ZS/ZT est **techniquement PASS, scientifiquement borné** : les mouvements invisiblement mortels ne sont pas sûrs, et le prédicteur ne saurait être utilisé pour délivrer une commande autonome sans contrat supplémentaire sur risque et responsabilité. **Stage12 PARTIAL, A2.30 PARTIELLE, issue #110 administrativement CLOSED, aucun déploiement I0.**
