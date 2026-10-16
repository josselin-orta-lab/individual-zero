# A2.30-X : préenregistrement de l'audit indépendant des archives W

**15 octobre 2026, APRÈS connaissance des résultats W, mais AVANT le code X.** Source figée : [GitHub Actions W #38753518412](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38753518412), code original **`aecb8d1172846620c3038a4bc10e7716ec7bde1e`**, archives `a230w-py3.11` et `a230w-py3.12`. W original connu avant X : 92 mondes/240 pas, 16 décès, 16 classes à cinq causes cachées, 160 paires non distinguées, 4 contrôles de ressource et 4 contrôles de passabilité positifs, 65 536 décisions bornées examinées. X est une **relecture a posteriori sans nouveaux mondes ni nouvelles actions**, et ses résultats attendus ne constituent pas une découverte indépendante.

Trois fichiers JSON à télécharger uniquement depuis le run original, comparer **octet à octet** entre les deux Python, vérifier les **SHA-256 entiers** fixés avant code X :
- `a230w-acted-physical-worlds.json` : `999b0ade7734b5591e26eec0c4e2fbfa57a8d6742f5aa229476df9b8caca1889`.
- `a230w-passive-positive-controls.json` : `dcfcacc9f44644a137f6c334dc13fcbac0173d3b07787b6e7ee1b548352fc666`.
- `a230w-summary.json` : `859806366dea71e30c791889e6cef0f4195bd40d78fa9c135b32c894f24a23c9`.

## Recalcul indépendant sans importer le runner W

1. Un script **distinct** doit reconstruire uniquement depuis les données enregistrées tous les `SimulationState` accessibles au moment t, sans importer le runner W, `WorldBody`, `Stage6`, `Oracle`, Bench ni aucun modèle de prédiction.
2. Contrôler chaque identifiant physique, combinaison probe/latent/nourriture/position, les reçus par pas et leurs hashes, le chaînage des états `before/after`, les préfixes prédéclarés, les coûts corporels et les 16 passages en état terminal. **Aucun état postmortem n'est qualifié de vécu**.
3. Construire une nouvelle clé à partir du **contenu de chaque histoire de perceptions avant ingestion**, et non du label latent, du futur physique, de la version du monde ou du code de branche W. Les 16 classes doivent chacune contenir cinq variantes latentes compatibles. Énumérer toutes les paires au sein d'une classe. Recalculer résultats alimentaires, coûts, comptages de 240 applications et les 65 536 choix de commit/abstention. Si la réalité diffère, produire une divergence explicite, sans corriger rétroactivement le protocole.
4. Recalculer les contrôles positifs avec les données **perceptibles uniquement** : `current_resources` et `adjacent.west.passable`. Ne pas en déduire une étiquette de sécurité alimentaire.
5. Contrôles négatifs : (i) un hash d'exemple modifié, (ii) un `SimulationState` post-ingestion déplacé avant la décision, (iii) un label de cause cachée inséré dans une histoire, (iv) un résultat terminal déclaré survécu et vécu, (v) une action ajoutée après mortalité, (vi) un contrôle visible rendu identique, (vii) un identifiant de monde dupliqué, (viii) un résultat synthétique `safe`, (ix) un coût corporel falsifié. **Chaque falsification doit provoquer un échec ciblé**, même si son propre SHA d'exemple a été recalculé lorsque le contrôle le nécessite.

Une archive JSON ne peut **pas prouver indépendamment l'application de `WorldBody.apply`**. X valide les signatures, les champs cognitivement accessibles et la cohérence des résultats dans des traces déjà produites. La future relecture physique Y, si réalisée, sera un contrôle supplémentaire à la physique du moteur et **pas** une nouvelle cohorte indépendante de 80 mondes.

**Statut au préenregistrement : X non exécutée ; W techniquement PASS ; A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; PR #194 DRAFT.** Ne pas modifier `src/i0`, le MVP v1.3.1, Stage9/DC-05, la mortalité WAL ou l'attribution subjective.
