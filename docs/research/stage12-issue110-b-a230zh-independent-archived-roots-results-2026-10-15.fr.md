# A2.30-ZH : audit indépendant des archives de vrais I0 et des clés exactes du modèle ZG

**15 octobre 2026.** Protocole ZH déposé **après** connaissance des résultats ZG, mais **avant** l'implémentation de l'auditeur ZH au commit `760742dcb5fb0a668dd003dbc99028b86453b05d`. Code de relecture `audit_stage12_issue110_b_a230zh_sealed_roots.py` (premier commit `828284db27fb21feee9b19f9957d44c2ceefd696`), tests négatifs `test_stage12_a230zh_sealed_roots.py`. [CI GitHub Actions #38778683954](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38778683954) : **17 tests PASS sous Python 3.11 et 3.12**, même rapport. Un contrôle rétrospectif **n'est pas** une nouvelle expérience de physique.

## Deux jeux de données scellés indépendants

**ZG original #38777542232**, `f416424292501671eda7f9ed65accb7a2712f9ef`, 3 fichiers JSON à SHA-256 intégral fixé **avant le code ZH** :

| Fichier | SHA-256 |
|---|---|
| `a230zg-physical-demonstrations.json` | `53f0363f09df2e23984d75bcdddb98550adeb1f35b015810a1b8ad5d37c91625` |
| `a230zg-lived-birth-shadow.json` | `fdfafde49f92f2feb26b41b42e71106766b5f30f3c33fb191ef53866705a9875` |
| `a230zg-summary.json` | `6af19338b42d9d3f17d26e9c3f1fe051e55f47e1fc3e04e7b66ccd5301b78617` |

Les deux artefacts ZG de Python 3.11 et 3.12 sont identiques **octet par octet** pour ces trois fichiers.

**ZB original #38767643472**, `2a19742df22f27752635203304097134a3009c45`, deux archives **non identiques** globalement. SHA du résumé original Python 3.11 : `ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b`; Python 3.12 : `ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362`. Les captures initiales et commandes physiques concordent sur les douze vies; la micro-dérive ULP sur six journaux `sustained` est **connue et n'est pas effacée** par ZH.

## Vérification véritablement indépendante du modèle source

Le code ZH ne charge **ni le runner ZG, ni `WorldBody`, ni `Equipment`, ni `SimulatorPlanner`, ni le runtime I0, ni l'Oracle**. Il réimplémente en lecture seule les caractéristiques admissibles du `SimulationState`, la génération des commandes candidates, les SHA de **chaque** état×commande, les suites physiques et les deux dictionnaires exacts par profil. L'entraînement contient bien les quatre exemples A et les trois exemples B, sans ingestion B, sans collision incompatible.

Pour chacune des 12 racines, ZH compare la version originaire du `SimulationState` dans ZB aux traces ZG, vérifie l'empreinte A historique, l'origine du monde B, le premier effet de `collecter(B)` ou `se_deplacer(east)`, et **recalcule seul** les nombres de `root_candidate_edges`, `root_available_edges`, `root_unavailable_edges`. Il confronte ces recomptages aux diagnostics consignés par **24 véritables recherches Stage6 exécutées dans ZG**, sans refaire de recherche dans ZH.

| Métrique indépendante ZH | Résultat |
|---|---:|
| Naissances historiques ZB dont le root est relié sans ambiguïté | **12** |
| Exemples physiques ZG dont SHA et commande sont recontrôlés | **14** |
| Mondes physiques externes dont le reçu est contrôlé | **6** |
| Roots B visibles avec arête réellement observée puis connaissable | **8/8** |
| Premières sous-étapes B avec sortie Stage6 physiquement justifiée | **8/8** |
| Roots B visibles sans premier pas dans le modèle original | **8/8** |
| Cas B_NONE avec progrès partiel A conservé | **4/4** |
| Recherches originales confrontées à une reconstruction indépendante | **24** |
| Ingestions B connues dans le modèle, faux certificats de sûreté | **0, 0** |
| Nouveaux mondes, actes ou naissances dans ZH | **0, 0, 0** |

**17 contrôles adversariaux PASS** : refus d'un SHA d'artefact altéré, fausse collection sans ressource visible, ingestion B injectée au corpus, root contenant une étiquette cachée, premier pas B fabriqué dans le modèle historique, `plan_found` injustifié, refus UC imaginaires, commande shadow prétendument exécutée, statut `safe` inventé, identité de naissance usurpée, B fantôme en contexte B_NONE, modèle A d'un autre profil et faux changement de sortie causé par la toxicité cachée.

## Frontière de preuve

ZH établit **l'intégrité des preuves enregistrées, la concordance indépendante des entrées perceptives et des clés exactes, et la cohérence des compteurs Stage6**. Les fichiers seuls ne prouvent pas que le moteur physique `WorldBody.apply` a effectivement été exécuté : cette provenance est apportée par le code et la CI du runner original ZG, et non une relecture physique externe ZH. L'identité des sorties 3.11/3.12 dans ZG n'est pas une deuxième cohorte scientifique. Les douze vrais I0 n'ont jamais vécu l'expérience B externe; aucune fusion de mémoire entre individus n'est autorisée.

**ZH : PASS technique, résultat scientifique ZG préexistant corroboré à portée limitée. A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN. Déploiement / garantie de sûreté alimentaire : NO-GO.**
