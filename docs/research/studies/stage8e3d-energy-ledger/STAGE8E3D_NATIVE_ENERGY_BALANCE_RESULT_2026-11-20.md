# Stage8-E3D · dépense motrice, cognition payée et récupération réelle d'énergie

**Clôture descriptive post hoc du 20 novembre 2026.** Le bilan énergétique réellement exécuté dans les vies G2 historiques a été reconstruit **sans simuler ni reconstituer aucune vie** et **sans télécharger de nouveau gzip**. **1 024 bilans population×bras×fenêtre**, **28 descripteurs comparés par 64 populations**, validations logicielles et physique indépendante réussies. L'étude reste **exploratoire, non confirmatoire, et n'identifie aucune médiation génétique**. Le test causal prospectif Stage8-E2 garde son verdict **`STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`**.

## Sources et chaîne de contrôle

- [Run historique Stage8-E2 science #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471), moteur original `03faff4b9c194a5288b92e394f6a75cbe62cd095`. Chaque vie G2 possède un gzip et une chaîne corporelle/cognition payée.
- [Stage8-E3C #44737606261](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44737606261), préflight + relecture **des 36 864 gzip G2 originaux**, des deux SHA-256 par original et des chaînes de vie, puis vérification indépendante sur 64 populations ; **3/3 PASS, tentative=1**. Source E3C `STAGE8E3C_FULL.json` SHA256 **`c99011ff4dc2bc7d57eb4edea5e68fa3a273777d984ddae8073777c38e5e4e23`**, réduction E3C `STAGE8E3C_SECOND.json` SHA256 **`b3ed0a35f4b51d9b77e8d34edb7f48b7d5858de05036018868da237ecffd2fd0`**. **C'est E3C, pas E3D, qui a effectivement réhaché les 1,49 Go de gzip historiques.**
- [Run E3D source-verrouillé #44775193275](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44775193275), source audit `33e5e7971aa24b5c84b8b7155b7865c1b11cd2c7`, **3/3 jobs PASS, tentative=1** : tests synthétiques, calcul original-dérivé et vérificateur indépendant Python 3.12. **Zéro nouvelle vie, zéro nouvelle simulation et zéro gzip original re-téléchargé**.
- Artifact E3D principal **14649591313**, `STAGE8E3D_FULL.json` SHA256 **`3a427bdd6965f76166e1ff01f27a5c70c35a007b0b0c16b9e3fed69fc21458c3`** ; artifact de recalcul indépendant **14648827332**, `STAGE8E3D_SECOND.json` SHA256 **`c9152ef7bd006e16e09c0d04883482630ca49185fe0888e437d5c3103da1bbfd`**. Les **1 024** cellules ont été validées et les **28** contrastes descriptifs réobtenus sans importer le premier calculateur.
- **Troisième vérification hors CI**, à partir des quatre JSON E3C/E3D téléchargés et de leurs SHA exacts : **1 024/1 024 bilans recomputés**, **28/28 descriptions et signes des 64 contrastes** concordants. C'est un contrôle arithmétique des **rapports originaux-dérivés**, pas un nouvel audit des octets gzip.

Le [protocole E3D](STAGE8E3D_POSTHOC_ENERGY_ACCOUNTING_METHOD_2026-11-20.md) déclare explicitement que l'examen est **post hoc** : les premières amplitudes avaient été regardées avant le document de méthode. Ne jamais transformer ce résultat en test de causalité préenregistré.

## 1. Une identité de conservation physique, sans comportement inventé

Pour les sommes de chaque cellule et fenêtre, l'énergie de corps **avant** décision et **après** exécution/apprentissage est réellement enregistrée. La facturation énergétique cognitive (décision, puis apprentissage), les actions motrices exécutées et le sommeil sont également présents. On définit :

`ΔE = E_fin_pas − E_début_prédécision = −C_décision − C_apprentissage − M_moteur + R_sommeil`.

L'énergie motrice **réellement débitée par le moteur 2026** est `M_moteur = 2×se_deplacer + 1×collecter + 0,5×(manger+boire) + 0,35×attendre`. L'action `None` ne produit ni sommeil ni récupération. Le gain réel `R_sommeil` est retrouvé par différence et doit respecter `0 ≤ R_sommeil ≤ 3 × n(dormir)`. **Toutes les 1 024 fenêtres passent cette contrainte physique**, sans déficit ou récupération impossible.

**Discordance logiciel/contrat à documenter séparément :** la constante `ACTION_COSTS["dormir"]` du moteur initial affiche **0,25 énergie**, mais la branche `if action=="dormir"` de `transition` contourne le `elif action is not None` qui applique les autres coûts. La dépense motrice d'énergie **effectivement exécutée** par un sommeil est donc **0**, avec un regain physique au plus égal à 3, et des coûts **cognitifs payés** séparément. Réinjecter fictivement 0,25 pour « corriger » le bilan historique fausserait le résultat ; **aucun patch des lois, du moteur ni des vies originales n'a été effectué**.

## 2. Les vingt premiers pas : même exposition pour toutes les vies

Tous les **36 864 individus** ont vécu les **20 premiers pas**, avec décision financée et sans première panne énergétique. **184 320 pas par bras**, **64 populations indépendantes** pour les contrastes. Chaque valeur ci-dessous est une moyenne des **64 comptes population×bras à poids égaux** :

| Énergie par pas exécuté, t = 1–20 | S_sham | S_swap | M_sham | M_swap |
|---|---:|---:|---:|---:|
| **Coût des actions motrices** | 1,540803 | **1,558213** | 1,545390 | 1,534002 |
| **Coût de cognition réellement payée** | 0,393456 | 0,391536 | 0,393160 | 0,394787 |
| **Énergie effectivement récupérée par sommeil** | +0,276009 | +0,257520 | +0,270654 | +0,281364 |
| **Variation nette d'énergie** | **−1,658250** | **−1,692229** | **−1,667896** | **−1,647425** |

Dans toutes les lignées, la dépense motrice des premiers pas est environ **quatre fois** la facture cognitive ; le sommeil actif est alors rare (~8,6–9,4 % des pas), avec un gain d'environ **3 unités par sommeil**. Le bilan énergétique moyen reste fortement négatif, **−1,65 à −1,69 unité par pas**. Le bras S_swap présente une perte moyenne plus forte que S_sham ; M_swap présente au contraire une perte initiale moyenne moins forte que M_sham.

Contraste descriptif à **n=64 populations** pour la *variation nette* : `[(S_sham−M_sham)−(S_swap−M_swap)] = +0,05445 unité/pas`, **34 populations positives et 30 négatives**, sans p-value ou test confirmatoire. Les trois composantes physiques individuelles et leurs 64 contrastes sont dans l'artefact source. Le signe de ce constat énergétique **n'autorise aucun renversement du test de persistance Stage8-E2**.

## 3. Fenêtres ultérieures : énergie, repos et sélection par survie

Énergie **nette par pas observé**, moyenne à poids égal des populations dans chaque bras :

| Fenêtre native | S_sham | S_swap | M_sham | M_swap |
|---|---:|---:|---:|---:|
| t=1–20 | −1,658 | −1,692 | −1,668 | −1,647 |
| t=21–100 | −0,190 | −0,194 | −0,216 | −0,218 |
| t=101–200 | −0,061 | −0,062 | −0,064 | −0,062 |
| t=201–400 | −0,066 | −0,064 | −0,061 | −0,064 |

À partir de t=21, la fraction de sommeil augmente (~30–35 % des pas, selon fenêtre et bras), la dépense motrice par pas baisse et les plus faibles réserves aboutissent à une **impossibilité de financer la décision** : les pas `None` continuent à exister tant que le corps est vivant, sans coût cognitif ou moteur ni regain du sommeil. Le **petit coût net observé** dans les fenêtres tardives ne traduit pas automatiquement une meilleure efficacité ou adaptation : les individus déjà défaillants contribuent des pas presque sans activité et l'exposition des survivants est sélective.

Il serait trompeur de déduire ici une causalité « un sommeil supplémentaire sauve la vie », une médiation du bloc gamma par les dépenses motrices, ou une stratégie optimale ; les données décrivent des **flux déjà réalisés**.

## 4. Ce que l'expérience enseigne et ce qu'elle ne démontre pas

**Mécanisme observable confirmé :** avant que le budget cognitif ne devienne inaccessible, le moteur engage une dépense énergétique **dominée initialement par les déplacements**, ajoutée aux coûts cognitifs, et les sommeils observés compensent seulement une partie de ces pertes. E3C avait montré que **17 560 vies** atteignent une porte `NO_PROCESSING_BUDGET` et que **0** ne retrouvent ensuite une action motrice financée ; E3D explique par la comptabilité physique **comment l'énergie a diminué**, sans inférer le comportement d'individus qu'on aurait « sauvés ».

**Non démontré :** un effet causal gamma1, gamma2 ou gamma3 sur les dépenses, une médiation héréditaire de la survie, une supériorité évolutionnaire, une généralisation hors F0, ou l'efficacité d'un correctif. Les 28 descriptions par quatre fenêtres et leurs signes sont **post hoc, multiples, non confirmatoires**. Les fenêtres tardives sont sélectionnées par survie et par le blocage lui-même. Toute nouvelle modification de l'architecture nécessiterait un protocole distinct ; ne pas altérer les originaux source-figés.

**Suites possibles sans requalifier l'échec Stage8-E2 :** ouvrir un contrôle logiciel strict sur la divergence entre coût nominal et coût physique réellement payé du sommeil ; puis, dans une étude future **prospective distincte**, mesurer si la représentation des dépenses ou le financement de la décision favorise une récupération choisie par l'individu, sans déclenchement moteur imposé. Les données E3D ne sont **pas** l'autorisation ou le résultat d'une telle expérience.

**Statuts inchangés :** Stage8-E2 `CLOSED_NO_RETRY / causal non démontré` ; Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT` ; I1 moteur actif, i3 non promu. La conservation durable des archives historiques gzip au-delà de la rétention GitHub Actions de 90 jours reste [#1463](https://github.com/josselin-orta-lab/individual-zero/issues/1463).
