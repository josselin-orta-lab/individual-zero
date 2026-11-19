# Stage8-E2 · Clôture technique source exacte et protocole prospectif causal

**État constaté au 20 novembre 2026 :** deux répétitions techniques complètes et audit indépendant à froid réussis, sur les originaux. **Aucune troisième cohorte scientifique n'a encore été générée** à la rédaction de ce document.

## 1. Vérification technique fermée, aucune inférence causale

- GitHub Actions one-shot : [#44536464441](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44536464441), `completed/success`, tentative 1, six jobs réussis. HEAD scientifique moteur P1.3 figé `03faff4b9c194a5288b92e394f6a75cbe62cd095`. Source `source_snapshot().sha256=e816ff5f5ee679253fc57f6e9ee79d21dff73dd72d6adf3c7f55ba7aa0f3e7f6`.
- Python 3.11 : **64 512 gzip originaux contrôlés** par job indépendant, allocation `ed37fdb55a355a49ebaa71bf19c1dabdb634a09b85dec642a543d96b283bc741`. Manifestes G0 `572034b5c685f84d4f1772f63562afb69514546adc9dd9acff4f233116f3d062`, G1 `507b68ea30acee4a6394a0327f2550fcad4fb70c1c6177ce1d10e691101fa1b7`, G2 `c2803dbef371ad6aa9f931005d2f30454e78ce95f104a56428a3d46a825a9ed3`. Chaîne neuf phases `1cd354277fb58f53aac6b3a381cf0a24e98f4f6bc27aedfac0bb8afb094fd67b`.
- Python 3.12 : **64 512 gzip originaux contrôlés** par un autre job indépendant, allocation `b8c6a9895ed1ae7ef9a61fac8ffafc1cb772b1ea01f8f4a23f3031c8839858e2`. Manifestes G0 `25e6cc2eab589c6dcecbba7a523997ec7a088f1cd6aa29fcbf0cbe0ae5a7122e`, G1 `0385714dbb28b97c276b0c4f9eeeb5ba99e52a3dae2d2dbe50a9cb2ed357e044`, G2 `2ea44ff819cf746f4f3d18f6bef8f67c36d86bee0aa47bcbb4c9e9e55a312c43`. Chaîne `ccccb27fecdccf679b5e792bca08896aaaed33df0fd1524fb0e751ace05b6c92`.
- 6 archives originales G0, G1, G2 conservées comme artifacts GitHub, total de **129 024** vies; facturation, corps, origine, mutations et traces recalculés sous `stage8e2_cold_original_archive_audit`. Reçu final `TWO_TECHNICAL_RECEIPTS_STRUCTURALLY_ACCEPTED_NO_SCIENCE`, `total_mutations_claimed=12288`. Le contrôle final ne décompresse pas lui-même les fichiers, mais les deux jobs cold audit l'ont fait.
- Dates et fichiers originaux : [artefacts du run](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44536464441) ; [issue méthodologique #1459](https://github.com/josselin-orta-lab/individual-zero/issues/1459). **Ne réutiliser ou réexécuter aucune des deux racines.** Les artifacts GitHub ont une rétention finie et doivent être exportés pour conservation longue durée.

Aucun résultat de persistance issu des répétitions techniques ne doit être consulté pour redéfinir l'hypothèse confirmatoire.

## 2. Préenregistrement prospectif de la troisième cohorte, indépendant des répétitions

Une unique **troisième racine OS aléatoire nouvelle**, une seule campagne scientifique F0, 64 populations indépendantes, 24 fondateurs par population, trois générations, familles World `stable`, `depletion`, `pulse` × deux répétitions par génome, horizon 400, politique native P1.3 référence et coûts cognitifs corporels réglés. Allocation neuve : **9 216 G0 + 18 432 G1 + 36 864 G2 = 64 512 vies originales**. Aucune naissance avant publication GitHub distincte des fichiers `SCIENCE_PLAN.json`, `NATIVE_PLAN.json`, de leur SHA-256 et des deux audits techniques épinglés.

G1 et G2 : sélection S par rang de persistance des six vies parentales authentifiées, contrôle M de multiplicités parentales appariées avec identité permutée et scores M cachés à la sélection ; mutations v4 graines séparées. Avant G2, chaque paire S/M produit quatre génotypes de naissance : `S_sham`, `M_sham`, `S_swap`, `M_swap`, échange réciproque exclusif du bloc `gamma1/gamma2/gamma3`, préservation vérifiée des 28 autres gènes. Les quatre bras partagent des WorldSpecs physiques G2 appariés, mais ont des identités de vie et RNG distinctes. Les individus demeurent autonomes et mortels, jamais de commande forcée.

**Estimand primaire unique à l'échelle des 64 populations :**

```
T[p] = (mean_G2_steps(S_sham,p) - mean_G2_steps(M_sham,p))
     - (mean_G2_steps(S_swap,p) - mean_G2_steps(M_swap,p))
```

Chaque moyenne utilise **144 vies G2 originales** (24 génomes × 6 mondes), sans pseudoréplication. Comparaison de la moyenne des **64** valeurs T[p] contre zéro par test **Student bilatéral** avec df=63, alpha 0,025 et `|t| > 2.2962367715148795`. Calculer également l'intervalle de confiance bilatéral 97,5 %. La variance doit être strictement positive et tous les 64 T disponibles ; sinon `NO_VERDICT`. Si l'intervalle exclut strictement 0 et variance>0, `STAGE8E2_CAUSAL_GAMMA_BLOCK_MODULATION_F0`. Sinon, sous audit valide, `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0`. Un signe négatif est publié tel quel ; aucune étude ni sous-groupe n'est relancé pour changer le verdict.

**Portée et interprétation :** au mieux, une modulation causale du **bloc gamma complet** de la persistance G2 dans F0 sous ce mécanisme de substitution, non une causalité unique de `gamma3`, une sélection naturelle de cet allèle, ni une généralisation hors F0. L'unité de causalité expérimentale est l'intervention de copie du bloc. Aucun effet comportemental particulier n'est imposé.

## 3. Frontières de source, de provenance et de conclusion

Le code scientifique de réduction et d'admission est un **orchestrateur extérieur au moteur** (`tools/` et workflow GitHub), dans un nouveau commit méthodologique prépublié. Les naissances sont exécutées uniquement depuis le moteur exact des deux répétitions, au HEAD `03faff...` et source `e816ff...`. Le workflow scientifique vérifie que **zéro fichier `src/i3` n'a changé** entre ce HEAD et le commit qui contient la préinscription. Le moteur de génération technique demeure un **générateur natif à verdict technique nul**, pas une preuve scientifique ; seul l'enveloppe externe prospectivement préinscrite, avant G0, pourra déclarer une hypothèse confirmatoire après l'audit indépendant des gzip. L'enveloppe est également scellée par son propre SHA et son commit.

Des validations distinctes doivent s'enchaîner, avec arrêt définitif de la racine sur tout échec : (1) admission à partir des deux archives techniques et leurs audits à froid ; (2) préexposition d'une troisième racine avant G0 ; (3) transport G0/G1/G2 unique, sans retries ni réutilisation de populations ; (4) conservation des 64 512 gzip G0/G1/G2 ; (5) **relecture complète des originaux** et vérification indépendante des ascendances avant calcul du test ; (6) reproduction des 64 contrastes et du verdict à partir de la source originale.

Ne jamais utiliser les agrégats techniques comme observations scientifiques ni les 24 génomes/144 vies comme 1 536 ou 9 216 observations indépendantes. Stage7, Stage8-A/B/C/D et Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT` demeurent inchangés.
