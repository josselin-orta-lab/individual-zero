# A2.30-X : recalcul indépendant des histoires perceptives W et des risques cachés

**15 octobre 2026.** L'audit X a été préenregistré **après les résultats W, avant son code**, au commit `49972042b3fb92fff25a81f061b408733ad94b83`. [GitHub Actions #38754552318](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38754552318) : **PASS Python 3.11 et 3.12**, mêmes fichiers de sortie, code `87d50e193a5571a0201c9f543e0cd2480feac682`.

L'auditeur `audit_stage12_issue110_b_a230x_sealed_probes.py` ne charge **ni le runner W, ni WorldBody, ni Stage6, ni Oracle, ni Bench**. Il télécharge les **deux archives de la CI physique d'origine W #38753518412** et vérifie leur égalité octet par octet et leurs SHA-256 complets :

- `a230w-acted-physical-worlds.json`: `999b0ade7734b5591e26eec0c4e2fbfa57a8d6742f5aa229476df9b8caca1889`;
- `a230w-passive-positive-controls.json`: `dcfcacc9f44644a137f6c334dc13fcbac0173d3b07787b6e7ee1b548352fc666`;
- `a230w-summary.json`: `859806366dea71e30c791889e6cef0f4195bd40d78fa9c135b32c894f24a23c9`.

À partir de ces **traces déjà connues**, il reconstitue avec un code différent les chaînes de `SimulationState`, les commandes et leurs SHA canoniques, leurs moments d'accessibilité, les coûts des sondes, les étiquettes externes de mortalité, le gel de l'histoire avant ingestion, les classes d'histoires perceptives complètes et les huit changements réellement visibles des témoins positifs. Les **13 tests adversariaux**, incluant les altérations avec SHA d'exemple recalculé, rejettent les contradictions corporelles, les captures postmortem, l'ajout de connaissance latente, les duplications, les fausses certifications, les modifications de contrôles positifs et les faux agrégats.

| Compteur recalculé par X | Résultat |
|---|---:|
| Mondes agis originaux | **80** |
| Témoins passifs originaux | **12** |
| Reçus `WorldBody.apply` originaux analysés | **240** |
| Décès externes vérifiés dans les reçus | **16** |
| Classes d'observations pré-exposition | **16** |
| Paires de conséquences cachées à histoires identiques | **160** |
| Paires distinguées avant ingestion | **0** |
| Contrôles positifs d'espèce/obstacle | **4 + 4** |
| Politiques aliment / abstention bornées | **65 536** |
| Politiques sans décès et avec au moins un repas dans ces cellules | **0** |
| Nouveaux mondes ou pas exécutés par X | **0** |

**Limite essentielle :** X valide la cohérence causale, temporelle et documentaire des **octets originaux** ainsi que la frontière perceptive, mais **n'établit pas indépendamment que le moteur de physique a bien appliqué les commandes**. Sa réussite n'est pas une nouvelle répétition statistique du monde. Une reprise distincte du runner original W avec `WorldBody.apply`, prévue par Y, est le contrôle technique suivant.

**Décision X PASS de relecture des archives ; W techniquement PASS ; A2.30 PARTIELLE, Stage12 PARTIAL, #110 OPEN, #194 DRAFT.** Les risques cachés restent indécidables d'après les seules observations pré-exposition des sondes W ; aucune nouvelle capacité cognitive ni politique de sûreté n'est déduite.
