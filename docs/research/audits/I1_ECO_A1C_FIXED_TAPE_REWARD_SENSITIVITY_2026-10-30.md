# I1 / A1-C : sensibilité de la récompense TD sur les mêmes trajectoires M11

**Audit post hoc du 30 octobre 2026.** Source de vérité : expérience confirmatoire unique [GitHub Actions #40944104333](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40944104333), commit générateur `26f7929b6db43f68e78b0cc0d9c67e7444f924c6`, 48 vies mortelles M11, 24 paires et **12 blocs de tempérament**. Aucun nouvel individu, aucune nouvelle action ni politique de récompense dans le moteur. Le verdict A1-C historique **NO-GO** et le niveau L3 **NOT_ESTABLISHED** sont conservés.

## Question et hypothèse

L'audit #623 a établi que, parmi 391 décisions canoniques avec faim et nourriture en inventaire, 154 admissions de `permanent:attendre` avaient une valeur Q apprise comme seule preuve extrinsèque disponible dans le cycle final ; 107 ne présentaient aucun autre franchissement de seuil. Ces épisodes sont issus de **3 tempéraments**, pas 154 réplicats.

**H-R (analyse exploratoire à trajectoire figée)** : la récompense fondée sur la distance *absolue* aux consignes corporelles valorise parfois la perte de réserves initialement au-dessus de leur consigne. Une récompense fondée uniquement sur la diminution des déficits réduirait-elle la Q apprise d'`attendre` pour les **mêmes états, options sélectionnées et transitions physiques réellement enregistrés** ? Cette hypothèse est distincte d'un bénéfice d'apprentissage vérifié.

## Deux récompenses, même expérience vécue

Pour les quatre besoins `energy`, `food`, `water`, `integrity`, avec consigne innée `s_i`, poids de naissance `w_i`, état corporel avant `b_i` et après `a_i` :

- Récompense native historique : `R_abs = sum_i w_i * (abs(b_i-s_i) - abs(a_i-s_i))`.
- Récompense candidate **seulement hors ligne** : `R_def = sum_i w_i * (max(s_i-b_i,0) - max(s_i-a_i,0))`.
- Identité exacte : `R_abs = R_def + R_surplus`, où `R_surplus = sum_i w_i * (max(b_i-s_i,0) - max(a_i-s_i,0))`.

**Attention** : `R_def` conserve les poids corporels effectifs. Ce n'est **pas** le score ECO normalisé et écrêté, et son remplacement éventuel n'est ni décidé ni validé. La conservation de réserves au-dessus de la consigne peut avoir une valeur future : neutraliser leur récompense immédiate n'est pas automatiquement optimal.

Le lecteur `tools/research/i1_a1c_reward_shadow_audit.py` atteste d'abord les **48 ZIP d'origine** par SHA-256 (manifeste `I1_ECO_A1C_EVIDENCE_MANIFEST.json`, SHA-256 `01ac08f8a084dff682256fca721cb6ff0e02b9d085207f088151b76a5e44bfca`), chaque chaîne M11 et les reçus de génération. Le modèle natif TD à **12 caractéristiques** est reconstruit et vérifié contre `1 067` publications TD et `5 261` valeurs Q natives Stage8. En parallèle, un second système de poids TD reçoit uniquement `R_def`, mais sur **les mêmes commandes et les mêmes états enregistrés** : `beta=0,8`, `lambda_e=0,8`, `eta=0,05`, mêmes caractéristiques, mêmes signatures et segments. Aucune simulation physique, admission motrice, consommation, réorganisation UC ou mort alternative n'est créée.

Le calcul avec quatre ouvriers et le calcul séquentiel produisent **un fichier de résultat strictement identique** (SHA-256 de l'audit complet : `7217281b17e39f0d042f93f9ab9c9e70d31dac019390e4b9ae7a9eebcf336931`).

## Résultats observés, sans interprétation de causalité comportementale

Les **2 304** actions physiques des 48 vies sont regroupées ci-dessous (ce sont des pas répétés, pas des sujets indépendants) :

| Action | Pas enregistrés | `R_abs > 0` | `R_def > 0` | Moyenne de `R_abs` | Moyenne de `R_def` |
|---|---:|---:|---:|---:|---:|
| `collecter` | 195 | 195 | 0 | +1,228718 | −0,185641 |
| `attendre` | 442 | 442 | 270 | +0,820511 | +0,034674 |
| `dormir` | 1 450 | 765 | 565 | −0,862214 | −0,043799 |
| `boire` | 104 | 48 | 48 | −7,138462 | +11,338462 |
| `manger` | 113 | 63 | 64 | +2,725839 | +3,463317 |

Pour la collecte, le terme de surplus positif représente en moyenne **+1,414359**. Sa décomposition totale (195 pas) : énergie **+195,0**, eau **+78,0**, nourriture **+2,8**, intégrité **0,0**. Le gain de récompense natif moyen dépasse donc la perte alimentaire, sans bénéfice alimentaire immédiat.

Exemple authentifié sur la vie `native / tempérament 101 / canonical` : lors du premier boire, eau `35 → 74,6`, `R_abs=+10,7` et `R_def=+24,8`. Au second boire, eau `74,6 → 100`, `R_abs=−25,1` et `R_def=−0,2`. Le dernier déficit restant vient des autres réserves corporelles, et non d'une récompense pour la surhydratation.

### Valeurs Q d'attente dans le même cycle M11

Sur **154** cycles où la Q apprise était la seule preuve extrinsèque native de `permanent:attendre` et où `attendre` avait *effectivement* été admis :

- **102/154** valeurs Q recalculées sous `R_def` deviennent **nulles ou négatives** ; les **52 restantes** demeurent positives.
- Les 154 cycles proviennent de trois tempéraments : `101` (52 cycles), `102` (50), `111` (52), chaque graine apparaissant dans les deux mondes nutritionnels.
- **102/154** inversions de signe sont concentrées dans **deux blocs indépendants** : graine `102` (50) et graine `111` (52). Le bloc `101` conserve une Q positive (52/52).
- La Q native des 154 épisodes est systématiquement positive. Le rejeu n'invente aucune nouvelle option ni nouvelle admission ; il calcule seulement une Q de sensibilité à l'instant archivistique correspondant.

**Conclusion locale :** le signe d'une part du signal Q d'attente est sensible au traitement des réserves au-dessus de leurs consignes. Cela ne permet pas de dire « 102 attentes évitées », ni « 102 ingestions supplémentaires » ; les trajectoires sans cette récompense sont inconnues. L'inférence scientifique porte sur **12 blocs**, avec un effet non uniforme, pas sur les 154 épisodes.

## Contre-épreuves, provenance et décision

L'auditeur refuse un original ZIP absent/altéré, un manifeste incohérent, une chaîne M11 falsifiée, une naissance hors protocole, des poids physiologiques anormaux, des segments TD incohérents, des `return_g/q_previous/q_next/delta` frauduleux, des signatures TD non conformes et une Q apprise Stage8 contradictoire. Les tests adversariaux purs contrôlent l'identité de décomposition, l'exemple hydrique, les cas de collecte, les deltas signés, les paramètres et l'interdiction d'une sélection de vies.

**Verdict contractuel :** `POSTHOC_FIXED_ACTION_TAPE`, aucune naissance, `A1-C=NO_GO`, `L3=NOT_ESTABLISHED`. Les variations de Q ne sont **pas** un essai causal sur la politique ou sur la survie.

## Prochaine porte avant d'envisager une nouvelle naissance

Formuler une expérience **prospective distincte** de récompense, dont la variante est fondée uniquement sur la physiologie perçue et **ne privilégie aucun nom d'action ni de baie**. Préenregistrer les sources de tempérament, les deux rôles nutritifs inversés, l'horizon, les unités statistiques indépendantes, l'exposition effective à une décision Q/Competition, le score principal pénalisant les morts et les règles de GO/NO-GO avant toute vie. La version canonique de `main` doit rester une condition témoin. Le coût d'opportunité du sommeil et l'importance des besoins devront être mesurés sans imposer de priorité à `manger`. Si les outils ne prouvent pas la séparation des deux traitements, **ne pas lancer**.

### Reproduction

Depuis une copie contenant les 48 ZIP originaux et le manifeste :

```bash
python tools/research/i1_a1c_reward_shadow_audit.py \
  --root /chemin/archives-a1c-originales \
  --out /chemin/audit-recompenses.json --workers 4
python -m unittest discover -s tools/research/tests \
  -p test_i1_a1c_reward_shadow.py -v
```

Les résultats sont un diagnostic instrumenté à partir de la **même** cohorte expérimentale historique. Aucun GO L3 ne peut découler de cet audit post hoc.
