# Stage8-F1B · parité des factures natives F1 versus témoin à calcul égal

**21 novembre 2026 : résultat de laboratoire informatique, sur huit états synthétiques appariés.** Source des 24 vrais appels à `World.step` : [workflow #44834616307](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44834616307), job `matched_real_world_step_receipts` **PASS**. Aucune vie native n'a été créée, aucun `run_life`, aucun apprentissage après action. Il ne s'agit **pas** d'un nouveau résultat scientifique sur les cohortes historiques.

## Résultats strictement établis

- Les **huit paires** F1 actif / F1 calcul payé puis écarté partent de la **même empreinte de `Mind` personnel, de la même `World.capture()` et du même corps**, avec RNG et mémoire clonés.
- Les **24 reçus physiques** issus du code natif sont présents dans l'artefact #**14677558926**, `STAGE8F1B_MATCHED_NATIVE_FULL.json`, SHA256 **`9e645b8aed70c5cf68047c2cd25ddd50d4d9a5441a147d9c6a11531aec91c65a`** (31 957 octets JSON). Le fichier `STAGE8F1B_NATIVE_RECEIPT.json` est inclus. Les signatures SHA du reçu de chaque pas et la chaîne des 24 reçus se vérifient.
- Un **contrôle arithmétique indépendant hors CI**, réalisé depuis **ces octets téléchargés** sans importer `Mind`, `World` ni les scripts du dépôt, reconstitue **24/24** dépenses natives et transitions énergétiques, toutes les morts, les positions et **8/8** paires de cognition énergie/vigilance identique. Rapport SHA256 **`4d1d7fe7cca67f1bd7e3eadefc98d13b6e5cbbf99170a0f08cf0c294cfdf9bbc`**.
- Cinq paires déclenchent la microdécision, facturée **0,0328 unité d'énergie et 0,05 vigilance dans chaque bras** ; parmi elles **une décision autonome de sommeil et quatre abstentions payées**. Deux paires n'ont pas les fonds (tous calculs et actions refusés sans crédit). Dans la huitième, P1.3 normalement financé produit **le même déplacement et la même facture** dans les trois bras : **0,2504 énergie et 0,394 vigilance** de cognition native, plus le coût moteur réellement appliqué.
- Dans les trois bras de l'état `terminal_food_not_rescued`, **zéro nourriture physique après un pas** provoque trois décès vitaux natifs, même avec microdécision disponible. Le système n'injecte aucun secours et le témoin ne produit aucune action gratuite.

## Incidents d'exécution, non cachés

1. Première source first-only [#44833916451](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44833916451) : **échec au préflight** faute de `PYTHONPATH=src:.`, aucune preuve native produite. Source première conservée non relancée. Voir [rapport incident](STAGE8F1B_FIRST_ONLY_PACKAGING_FAILURE_2026-11-21.md).
2. Deuxième source first-only [#44834616307](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44834616307) : **préflight PASS, 24 reçus natifs produits PASS** ; job CI de réduction indépendante **FAIL sur la recherche d'un ancien nom d'artefact**. Les reçus sont préservés sous leur vrai nom `i3-stage8f1b-corrected-matched-native-24-step-receipts-44834616307`. L'audit arithmétique extérieur, non GitHub Actions, a réussi sur ces octets exacts.
3. Le troisième workflow est **uniquement un lecteur indépendant à froid** du fichier déjà publié. Il doit identifier l'artefact par son nom exact, sa racine d'origine et son SHA256 ; il **ne doit jamais relancer `World.step`**. Un éventuel PASS sera ajouté avec l'ID du nouveau run et le hash du second reçu.

## Portée exacte du verdict

**Parité du calcul réellement payé : OUI, sur états synthétiques parfaitement appariés, pour F1 et son contrôle à lecture écartée.** Il ne faut pas comparer le financement F1 à P1.3 comme si leur travail était égal. Le sommeil et l'absence d'action **produisent des conséquences corporelles différentes après la décision** : c'est justement ce que l'on veut pouvoir identifier, et ce n'est pas une violation de la parité cognitive.

Ce test ne démontre **ni survie améliorée, ni causalité génétique, ni apprentissage réel G2, ni conservation des chaînes `run_life` historiques**. Les originaux E3C/E3D ne contiennent pas le `Mind` complet au premier échec ; impossible d'en obtenir un contrefactuel à mémoire exactement identique. La vérification est un **gate logiciel de facturation**, pas une autorisation de nouvelle cohorte.

**Statuts inchangés :** Stage8-E2 `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`, Stage2.1 `NOT_ISSUED`, moteur I1 actif, i3 non promu ; zéro naissance F1B.