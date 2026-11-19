# i3 Stage8-E2 : falsificateur causal prospectif du bloc d'horizons gamma

**Statut au 19 novembre 2026 : `CAUSAL_DESIGN_ONLY / NO_SOURCE_LOCKED_ALLOCATION / ZERO_NEW_LIVES`.** Hypothèse choisie **après** les associations exploratoires Stage8-E1, mais **avant** toute nouvelle expérience. Ce texte constitue une conception d'étude à rendre exécutable et à source-verrouiller ; il n'est pas encore une autorisation scientifique, un manifeste de préexposition, une cohorte ni une attestation causale.

## 1. Mécanisme candidat et falsificateur

Stage8-C a établi son avantage moyen **+8,676 pas** S−M lorsque la concentration parentale est appariée. Stage8-E1 a identifié `gamma3` parmi les covariations les plus fortes (**r = −0,32361** avec les 32 gains S−M), avec un déplacement G2 moyen **−0,04437** de la plage normalisée, et un même signe dans les deux sous-panneaux (−0,355 / −0,302). **Cela ne prouve aucun gène causal**.

La contrainte native `gamma1 ≤ gamma2 ≤ gamma3` interdit d'échanger arbitrairement `gamma3` seul. Il faut traiter le **triplet `(gamma1,gamma2,gamma3)` comme un bloc indivisible** lors d'une première expérimentation de causalité. Le `stage8e_reciprocal_locus_swap.py::reciprocal_gamma_horizon_block_swap` crée des copies exactes S/M des génomes vivants avant naissance et des frères/soeurs contrefactuels où **seules les trois valeurs gamma sont échangées** entre les deux bras. `genome.validate` prévient tout génome v4 invalide ; les 28 autres gènes restent inchangés. Cette manipulation n'impose **aucune action** au cerveau ou au corps.

**Hypothèse causale prospective candidate :** changer **uniquement le bloc d'horizons** entre deux génomes S/M, à contrôle génétique de fond, World, coûts de cognition et historique de sélection inchangés, modifie le contraste de persistance G2 S−M. Ce test n'isole PAS gamma3 des deux autres horizons.

**Unique estimand primaire proposé, par population `p` :**

```text
T[p] = (mean_G2_steps(S_sham,p) - mean_G2_steps(M_sham,p))
     - (mean_G2_steps(S_gamma_swap,p) - mean_G2_steps(M_gamma_swap,p))

H0: E_population[T] = 0
H1: E_population[T] != 0
```

Une différence significative sous randomisation et traçabilité scellées serait compatible avec une **modulation causale par le bloc gamma** dans les écologies F0, pas une preuve que `gamma3` seul médiatise le gain ancestral. Un effet négatif serait également publié : il suggérerait que la substitution gamma améliore, plutôt que réduit, l'avantage S−M.

## 2. Plan de naissance et puissance à FIGER avant exposition

**Proposition de dimensionnement : n = 64 NOUVELLES populations F0**, à 24 fondateurs chacune, trois familles `stable/depletion/pulse`, deux répétitions World pour chacune et chaque génération. Chaque population est une unité d'inférence, indépendance et approximation de Student à éprouver ; les génomes et vies ne sont pas des unités indépendantes.

- G0 partagé : **64 × 24 × 6 = 9 216 vies**.
- G1 : lignées S (parentalité rangée par persistance corporelle payée) et M (contrôle parent à multiplicité exactement appariée), soit **64 × 24 × 6 × 2 = 18 432 vies**.
- G2 : quatre bras **S_sham / M_sham / S_gamma_swap / M_gamma_swap**, **64 × 24 × 6 × 4 = 36 864 vies**, avec les **384 opportunités World G2 réservées AVANT G0**, appariées entre les quatre bras. 24 génomes × 6 vies = 144 vies par bras et population ; différences calculées sur ces moyennes.
- Total d'une exécution : **64 512 vies**. Deux **répétitions techniques intégrales** Python 3.11 et 3.12 (129 024 vies) puis une **unique allocation scientifique indépendante** après leurs deux validations (64 512 vies), au total **193 536 vies au maximum**, sans remplacement après échec ni résultat négatif. C'est un **budget prévu**, pas une autorisation ou un coût CI déjà encouru.

**Test proposé à figer : Student bilatéral n=64, df63, alpha=0,025, `|t|>2,2962367715148795` et variance populationnelle strictement positive.** Un intervalle bilatéral de 97,5 % excluant zéro constituerait un signal d'effet du **bloc** sous les hypothèses de l'étude. Si variance nulle, test invalide ou provenance rompue : **pas de succès automatique**. Le traitement synthétique `stage8e_causal_gamma_population_test.py` impose 64 observations, les quatre bras, 144 vies attendues, des valeurs finies dans [0,400] et un critère simple. Il marque **toujours `scientific_claim_authorized=false`** tant que les archives natives ne sont pas indépendamment revalidées.

**Hypothèse de puissance purement de dimensionnement :** avec effet causal de 10 pas et écart-type hypothétique de T de 25 pas, une approximation normale bilatérale alpha .025 donne environ 83 % de puissance pour n=64. **Aucune variance réelle de T n'a été mesurée** : cela ne garantit pas la puissance d'une étude future. Une variance supérieure, des dépendances entre populations ou l'épistasie peuvent réduire fortement la puissance. Aucun dimensionnement ne doit être retouché d'après un aperçu d'une cohorte confirmatoire.

## 3. Identifiabilité et contrôles non négociables

- Construire les G1/G2 descendants en respectant une sélection S basée **uniquement sur les six vies parentales effectivement observées**, et M sur les mêmes multiplicités parentales sans consulter ses propres scores ; aucune vie G2 ne doit être visible avant l'allocation.
- Répliquer chaque génome G2 en un sham **identique** et une version gamma-swap, sans reconstruire, réutiliser ou transmettre une mémoire, un état cognitif ou un vécu de l'ancêtre. G2 est **une naissance distincte et mortelle**, avec politique motrice autonome P1.3 funded-v2, facturation énergie/vigilance identique et aucune action forcée.
- Préallouer, publier et sceller **tous** les index World, graines de vies, graines de mutation et clés de permutation pour les familles/bras, avec domaines disjoints des études Stage6/7/8-A/B/C ; apparier les spécifications physiques G2 mais distinguer les identités et flux RNG individuels.
- Garantir par tests purs que les shams gardent leurs SHA de génome exacts, que les quatre descendants ont les mêmes 28 gènes hors bloc au sein de chaque paire, que le triplet gamma reste ordonné, que le parentage S/M, l'horizon 400, les morts à 400 vs censures, les budgets corporels et toutes les populations défavorables restent observables.
- Avant toute science : deux répétitions complètes du **même nouveau source HEAD** en Python 3.11/3.12, archives et reçus gzip complets, contrôle strict de la méthode figée et de deux allocations disjointes. Ensuite seulement **troisième racine** d'entropie nouvelle, manifeste scientifique publié avant naissance, exécution unique **sans retry**, audit indépendant original gzip et publication des valeurs même nulles/négatives.
- Séparer le contrôle scientifique du contrôle mécanique : un résultat statistique `T≠0` ne démontre pas la sélection naturelle du bloc gamma, la causalité propre à `gamma3`, un mécanisme d'apprentissage cognitif, une équivalence entre écologies, ni la généralisation hors F0.

## 4. Portée exacte du développement présent

Un opérateur **logiciel pur** de permutation gamma et son falsificateur **sur entrées synthétiques**, avec tests, sont proposés dans la PR de conception. **Le nouveau générateur de cohorte, la matrice réelle d'allocation, les worldspecs, les identités de naissance, les empreintes source, les deux répétitions techniques et le protocole de registre des résultats ne sont PAS encore construits ou exécutés.** Leur travail reste requis avant d'appeler cette étude une expérience prospective préenregistrée.

L'autorisation générale ADR-0022 permet la **recherche laboratoire prospective** selon un protocole nouveau effectivement figé, mais n'autorise ni relance de Stage8-C ni promotion d'i3. I1 actif ; i3 référence de développement non enregistrée ; Stage2.1 scientifique `NOT_ISSUED/HOLD_NO_VERDICT`. Les conclusions précédentes restent intactes.
