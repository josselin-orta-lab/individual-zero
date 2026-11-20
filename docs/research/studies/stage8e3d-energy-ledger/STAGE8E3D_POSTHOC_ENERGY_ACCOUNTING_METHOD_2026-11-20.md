# Stage8-E3D · bilan énergétique effectif sur les mêmes vies G2, sans re-téléchargement des originaux

**Méthode descriptive post hoc, 20 novembre 2026.** Les directions et amplitudes préliminaires des bilans ont été inspectées avant rédaction : ce document **n'est pas un préenregistrement confirmatoire**. Le protocole historique Stage8-E2 reste **négatif et clos** ; aucune nouvelle naissance, intervention génétique, allocation de World ou simulation. Le bilan E3D est une **réduction secondaire des tableaux E3C déjà réaudités depuis les originaux**, et NON un nouveau travail de rehash gzip.

## Sources exactes

- [Workflow E3C #44737606261](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44737606261), première exécution, **3 jobs PASS** : **36 864 gzip G2 originaux** inspectés et leurs traces du paiement réellement exécuté auditées. Le [rapport complet](../stage8e3c-first-energy-gate/STAGE8E3C_ORIGINAL_TEMPORAL_RESULT_2026-11-20.md) établit **17 560 premiers refus de financement** et **0 reprise d'action après le premier refus**. Il reste une observation, non une preuve de médiation gamma.
- E3C source JSON : artifact **14629459511**, fichier `STAGE8E3C_FULL.json`, SHA-256 **`c99011ff4dc2bc7d57eb4edea5e68fa3a273777d984ddae8073777c38e5e4e23`**.
- E3C réduction indépendante : artifact **14629908704**, fichier `STAGE8E3C_SECOND.json`, SHA-256 **`b3ed0a35f4b51d9b77e8d34edb7f48b7d5858de05036018868da237ecffd2fd0`**.
- Moteur originel figé SHA Git `03faff4b9c194a5288b92e394f6a75cbe62cd095` ; [`body.py`](https://github.com/josselin-orta-lab/individual-zero/blob/03faff4b9c194a5288b92e394f6a75cbe62cd095/src/i3/modules/body.py), [`world.py`](https://github.com/josselin-orta-lab/individual-zero/blob/03faff4b9c194a5288b92e394f6a75cbe62cd095/src/i3/modules/world.py) et [`life.py`](https://github.com/josselin-orta-lab/individual-zero/blob/03faff4b9c194a5288b92e394f6a75cbe62cd095/src/i3/runtime/life.py). Physique *exécutée* de la cohorte 2026, pas physique projetée ou corrigée.

## Identité de conservation reconstituée depuis les sommes déjà archivées

Dans chaque cellule `population × bras × fenêtre`, les originaux E3C incluent les totaux d'énergie de **prédécision**, les états énergétiques **après l'action et l'apprentissage réellement payé**, le travail cognitif de décision/apprentissage en monnaie énergie et les six choix moteurs appliqués ou `None`.

Définir :

- `ΔE = ΣE_fin_pas − ΣE_début_prédécision` ;
- `C = Σénergie_cognition_payée_décision + Σénergie_cognition_payée_apprentissage` ;
- `M = 2×n(se_deplacer) + 1×n(collecter) + 0,5×[n(manger)+n(boire)] + 0,35×n(attendre)` ;
- `R_sommeil_observé = ΔE + C + M`.

La seule source de récupération d'énergie moteur dans ce contrat natif est `dormir`, gain **entre 0 et 3** par action en fonction des réserves et de l'hydratation ; **le moteur historique n'applique pas** à l'action `dormir` la valeur *nominale* `ACTION_COSTS["dormir"]=0.25` inscrite dans la table. La branche `if action=="dormir"` dans `transition` traite le gain directement et évite le débit d'action normalement porté par `elif action is not None`. Il s'agit d'une **discordance de contrat logiciel constatée** : ne ni modifier les octets historiques, ni prétendre que la table nominale est la dépense réellement exécutée.

**Falsificateur exact :** chaque cellule doit satisfaire `0 ≤ R_sommeil_observé ≤ 3×n(dormir)` (tolérance flottante 1e-4) ; si aucun sommeil n'a été observé, le gain calculé doit être nul à précision près. Un résultat qui devrait bénéficier d'une dépense sommeil fictive de 0.25 échoue au contrôle dès qu'il dépasse la récupération physique maximum.

## Évaluation fixée au niveau de la population

Les quatre fenêtres **déjà fixées par E3C** : `t001_020`, `t021_100`, `t101_200`, `t201_400`, l'ensemble **256 cellules × 4 fenêtres = 1 024 bilans**. Chaque cellule contient 144 vies originales, et le contraste quatre bras est calculé **par population, n=64**, jamais sur les 9 211 248 pas comme s'ils étaient indépendants.

Descripteurs annoncés : dépense motrice par pas observé, énergie cognitive réellement payée par pas, regain réel dû au sommeil par pas et par sommeil, variation corporelle nette d'énergie par pas, fraction de déplacements et fraction de sommeil. Toutes les 64 valeurs de chaque contraste post hoc sont conservées, positives, négatives et nulles ; **aucune p-value**. Les pas t1–20 correspondent aux **36 864 vies présentes**, sans sélection par survie dans cette fenêtre ; les taux des fenêtres tardives sont explicitement affectés par la survie et les premières impasses.

**Double contrôle** : un premier calculateur reconstitue le bilan depuis le JSON original E3C SHA-figé ; un second, sans import du premier, recalcule les numérateurs physiques, les 1 024 cellules et les 28 rapports populationnels. Tests synthétiques visant source détachée, ajout arbitraire du coût sommeil nominal, gain sans sommeil, facturation imaginaire, populations manquantes et verdict Stage8-E2 réécrit.

**Arrêt** : toute divergence de source, identité physique, conservation ou statistique descriptive ⇒ **pas de nouveau résultat**, non une « répétition » de G2. La véritable conservation des neuf archives gzip originales hors rétention 90 jours continue d'être suivie en [#1463](https://github.com/josselin-orta-lab/individual-zero/issues/1463). **Le résultat causal Stage8-E2 demeure négatif, CLOSED_NO_RETRY.**
