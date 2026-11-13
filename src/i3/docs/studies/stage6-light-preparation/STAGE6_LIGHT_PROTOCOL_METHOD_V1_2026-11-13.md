# I3 · Étape 6 légère : protocole méthodologique v1 (13 novembre 2026)

**Statut : `METHOD_FIXED_PREAUTH_NOT_EXECUTABLE`.** Les choix d'analyse et le plan expérimental sont fixés dans ce commit **avant toute nouvelle exposition Stage-6-light**. Ce n'est **ni une autorisation, ni un protocole d'exécution source-scellé, ni une inscription temporelle indépendante**. Aucun nouveau World, indice, individu, rehearsal vivant ou cohorte ne peut être ouvert sur cette base. Les clés de transport, d'allocations et la levée spécifique restent `null` dans le [contrat machine non permissif](STAGE6_LIGHT_PROTOCOL_METHOD_V1.json). **Le [brouillon historique](STAGE6_LIGHT_PROTOCOL_DRAFT_2026-11-13.md) est conservé inchangé**, car sa provenance est épinglée.

**Périmètre.** I3 non enregistré, référence architecturale et scientifique interne P1.3 funded-v2, Stage 2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, I1 runtime actif. ADR-0014 (sélection par persistance), ADR-0017 (scellement et moratoire), ADR-0018 (recommandation non autoritaire), ADR-0020 (préparation documentaire déléguée), ADR-0021 (aucune admission des étapes 3–6). La proposition de feuille de route PR #1359 n'octroie aucun droit. Cette version est une **décision de conception révisable uniquement par une nouvelle version explicite**, sans effet rétroactif sur le préenregistrement historique de P3.

## 1. Hypothèse et estimand unique

**Question :** sur les seules familles écologiques F0 de P2, une sélection intergénérationnelle fondée uniquement sur la persistance individuelle produit-elle, après deux tours, une direction commune de déplacement du poids de curiosité exprimé par rapport à une lignée où les parents sont tirés uniformément ?

Pour chaque population indépendante `p = 0..15`, après G2, définir
`C[p] = mean(beta_u_eff(selected,p,G2)) - mean(beta_u_eff(random_parent,p,G2))` sur les **24 génomes** par bras. `beta_u_eff = beta_u * (1 + 0.5 * temperament.exploration)`. **Unité de réplication et d'inférence : la population entière (n=16)**, jamais le génome, la vie, le World ou un pas. Les mondes, graines de vie et génomes G0 sont appariés **au sein** d'une population ; les flux d'aléa et mondes sont distincts **entre** populations.

- H0 pour la règle de signe : les signes non nuls de `C[p]` sont indépendants et équilibrés entre + et -, sous une absence de déplacement directionnel. Ce postulat est **nécessaire**, non démontré par une simulation.
- H1 : au moins 13 des 16 populations présentent une même direction, positive **ou négative**. La direction n'est pas choisie après lecture.
- `C[p] = 0` compte comme **zéro**, ni positif ni négatif ; zéro n'est pas retiré du dénominateur de 16. Les données manquantes ou illisibles ne sont **jamais** converties en zéro.
- Objectif strictement borné : **déplacement du paramètre héritable**. Même un résultat statistiquement fort n'établit ni survie avantageuse des descendants, ni adaptation généralisée, ni sélection causale d'un gène isolé, ni conscience.

La lecture de P3 (4 populations, signal de signe **négatif** pour `beta_u_eff`) est **descriptive et déjà exposée**. Le [modèle numérique nul](STAGE6_LIGHT_DRIFT_NULL_RESULTS_2026-11-13.md) aide seulement au dimensionnement. Sa grille n'est ni une calibration exhaustive du niveau du test, ni une preuve prospective. La [provenance Git de cette préparation](STAGE6_LIGHT_ORIGINAL_BUNDLE_PROVENANCE_2026-11-13.md) démontre la filiation des objets mais pas l'antériorité indépendante des premières exécutions historiques.

## 2. Bras, mécanismes et liberté de l'individu

- **Bras :** `selected` et `random_parent`. Les 24 fondateurs G0 sont strictement identiques entre bras pour chaque population ; G0 est vécu **une seule fois**, avec les originaux et identifiants partagés comme source des deux lignée, **sans créer de doubles vies**.
- **Parenté `selected` :** classer les 24 génomes du tour précédent selon le nombre des six vies **censurées à 400 pas**, puis le total des pas effectivement vécus, puis le numéro d'emplacement croissant pour départager les égalités. Tirage d'un parent parmi les 24 classés selon les poids linéaires `24,23,...,1`.
- **Parenté `random_parent` :** tirage uniforme parmi les 24 parents du tour précédent, **sans lecture d'un score pour décider**. Même nombre de descendants, même mutation et même exposition écologique que l'autre bras.
- **Descendance :** 24 descendants par bras après G0 et après G1. Mutation `i3.modules.genome.mutate` à échelle `0.1` dans le contrat génome v4 de la référence ; flux de mutation séparés pour chaque bras, population, génération et emplacement. **Pas de recombinaison, pas de mémoire héritée, pas de fait du monde, pas de score de concepteur additionnel.**
- **Vie :** le Mind et le WorldBody P1.3 funded-v2 décident seuls des actions, de la cognition payée et de la mort. Aucune action imposée, sauvetage, remise en vie, oracle, récompense nouvelle ni changement de budget. On conserve toutes les morts, vies censurées, dépenses de vigilance/énergie, actions, erreurs et effets physiques.

Une sélection laborantine de parents sur la persistance est distincte d'un contrôle des décisions prises par l'individu pendant sa vie. L'existence d'un score de persistance dans le laboratoire ne l'autorise jamais dans le Mind.

## 3. Matrice prospectivement définie (sans graines ouvertes)

| Élément | Valeur fixée |
| --- | --- |
| Populations indépendantes | **16** |
| Génomes fondateurs par population | **24** |
| Générations | **G0, G1, G2** (deux sélections) |
| Familles F0 P2 | **stable, depletion, pulse** |
| Répétitions par famille / génération / population | **2** |
| Monde physique par coordonnée | même WorldSpec et même graine de vie pour tous les génomes, et les deux bras d'une population/génération ; **jamais** réutilisé entre populations |
| Horizon de vie | **400 pas maximum** |
| Graines de mondes nécessaires | **288** identités distinctes (16 × 3 × 3 × 2) |
| Génomes fondateurs | **384** (16 × 24) |
| Vies G0 uniques | **2 304** (16 × 24 × 6) |
| Vies G1 | **4 608** (16 × 2 bras × 24 × 6) |
| Vies G2 | **4 608** |
| Total de vies prévu | **11 520** (pas 13 824 ; G0 n'est pas doublé) |
| Plafond de pas physiques | **4 608 000** |
| Cohortes historiques P2/P3 | **fermées ou réservées, jamais réutilisées** |

Les **288 positions logiques** sont indexées `((p*3+g)*3+f)*2+r`, avec `p=0..15, g=0..2, f=0..2` dans l'ordre `stable,depletion,pulse`, `r=0..1`. **Cet entier est un emplacement de calendrier, pas un indice de World admis ni une graine physique.** Une future allocation prospective distincte doit produire une correspondance totale bijective `coordonnée -> nouvelle graine de monde`, plus les racines de genèse, vie, parents et mutation, chacune dans un domaine distinct, puis sceller son SHA-256 **avant** toute génération. Les deux bras appariés d'une même coordonnée ont le même WorldSpec et la même graine de vie ; toute différence imprévue stoppe le panel.

**Aucune plage numérique n'est réservée par ce texte** ; aucun indice `selection`, `validation`, `reserve`, `engineering`, ni la réserve `1200000..1200199` n'est affecté au futur essai. La future allocation doit prouver disjonction, absence de collisions, indépendance entre populations et source exacte. Les noms de familles F0 ne certifient pas la généralisation hors F0.

## 4. Critère de décision, neutralité et arrêts

Définir `N_plus = count(C[p] > 0)`, `N_minus = count(C[p] < 0)`, `N_zero = 16-N_plus-N_minus` et `T=max(N_plus,N_minus)`. Le signal nominal est `T >= 13`. Sous l'hypothèse **idéalisée** de 16 signes indépendants et équilibrés, `P(T>=13) = 2*sum(comb(16,k),k=13..16)/2^16 = 1394/65536 = 0.021270751953125`. Si des zéros existent, la règle à dénominateur fixe est conservatrice sous cette hypothèse. **Ce nombre n'est pas un niveau réel garanti** si indépendance, symétrie ou stabilité des populations échouent. Publier les 16 contrastes, leurs valeurs, les signes, les zéros et l'incertitude, sans pseudo-réplication.

Les marqueurs `omega`, `temperament.affiliation`, `temperament.reward_sensitivity` sont des **sentinelles**, pas des preuves d'échangeabilité. Un [test d'ingénierie](../../../../../tests/i3/test_reference_neutral_marker_genes.py) sur trois mondes démontre l'invariance pas-à-pas locale aux extrêmes des marqueurs, sans démontrer leur inertie universelle. Il doit repasser **sur le code d'exécution exact** avant toute exposition. Répéter le même `T >= 13` pour chaque sentinelle ; `>=2` sur trois déclenche `STAGE6_LIGHT_INVALID` ; un seul déclenche un avertissement conservé. Ce seuil de sentinelles n'est **pas** un test alpha-calibré de validité.

**Une seule lecture finale, sans exploration des signes après coup.** Priorité des résultats :

1. **`STAGE6_LIGHT_NOT_RUN_NO_AUTHORIZATION`** tant que la levée indexée n'existe pas. C'est le statut de ce document et de son manifeste.
2. **`STAGE6_LIGHT_INVALID`** si une vie manque, un original est modifié, une identité/seed/World/cycle coûteux diffère, l'indépendance d'allocation échoue, un processus ne clôt pas, un contrôle de neutralité d'ingénierie échoue, ou au moins deux sentinelles franchissent 13/16. Les défaillances techniques `ENGINEERING_FAILURE_NOT_A_DEATH` sont publiées séparément comme telles.
3. **`STAGE6_LIGHT_SIGN_CONCORDANCE_PASS`** si `T>=13` et l'intégrité complète est démontrée ; rapporter le signe, l'ampleur et les limites. **Aucun GO scientifique automatique.**
4. **`STAGE6_LIGHT_NO_SIGN_CONCORDANCE`** sinon, à intégrité complète ; les effets petits, mixtes ou opposés restent rapportés, sans verdict « sélection inutile ».

Quantités secondaires uniquement descriptives : `beta_u` non composé, les trois sentinelles, autres gènes et leurs bornes, nombre de fondateurs présents après reproduction, survie/horizon, causes de mort, coûts énergie/vigilance réellement payés, apprentissage et exposition écologique par famille. **Aucune correction, reclassification, modification de seuil ou analyse adaptative** après vue des résultats. Les tests de survie des lignées, avantage causal hors F0, et l'évaluation de génomes G2 sur mondes de validation **sont exclus**.

Le modèle nul propose un **plus petit déplacement détectable d'environ 0,314** pour `beta_u_eff` avec ce plan et **80 % de puissance modélisée** sous un régime `heritable` approximatif. Ce n'est pas une garantie de puissance réelle, ni une marge de non-infériorité, ni une raison de prolonger la lignée après un résultat nul. L'asymétrie signalée pour le produit `beta_u_eff` à génération longue reste un risque de validité ; il faut publier aussi les signes des trois sentinelles et les fondateurs restants.

## 5. Chaîne de scellés nécessaire à une lignée

**Écart méthodologique explicite à l'ADR-0017 :** pour choisir G1, il faut connaître la persistance de G0 ; pour choisir G2, celle de G1. Une phase unique `G` couvrant toutes les générations, sans aucune réduction intermédiaire, est impossible. La **variante par génération ci-dessous ne modifie pas l'ADR-0017** et **doit être acceptée expressément dans l'autorisation spécifique de lignée avant toute ouverture**.

Pour chaque génération (y compris G0), sous la version exacte du transport et du manifeste :

1. **G(g)** : générer toutes les vies prévues de cette génération, dans l'ordre scellé. Archiver chaque original entier et son SHA-256. Pendant G : seulement compte de progression, statut structurel, SHA ; jamais performance, signes, décès, curiosité, score ni résultat de règle.
2. **Sceller G(g)** : ensemble complet des originaux et reçus, source SHA, protocole, arbre de WorldSpec/seed, preuves de coûts payés, manifestes immuables. Toute vie manquante ou coût non vérifié **STOP**, pas une mort.
3. **S(g)**, pour g=0,1 : un réducteur de sélection pré-éprouvé lit uniquement `censored`, `steps_lived`, `slot` et les identités/empreintes strictement indispensables à la chaîne de preuves ; applique la règle de parenté figée et scelle l'identité des parents et mutations de G(g+1). Aucun `C[p]`, signe, agrégat entre bras, table de survie ni classement global n'est affiché à l'opérateur. Le fichier reçu de sélection ne peut autoriser une vie.
4. **Après G2** : `R_final` vérifie les empreintes, reconstruit tous les scores et liens de parenté, teste les invariants sur l'ensemble des populations, puis produit **une seule fois** la statistique principale et les sentinelles ; archiver aussi les nulls, échecs et directions inattendues.

**Panne :** une erreur de World/moteur au cours de G ou une erreur de S(g) ferme l'essai en `ENGINEERING_FAILURE_NOT_A_DEATH`, sans rejouer ni compléter un panel ni redistribuer ses graines. Une erreur de lecture **strictement finale** (aucune nouvelle vie possible) peut suivre la réparation aveugle de réduction prévue à l'ADR-0017 : source de réparation distincte, originaux inchangés, deux cycles maximum, sans lecture des résultats. En cas de dépassement, statut invalide. L'exposition future doit tester ces chemins en synthétique avant un éventuel rehearsal scellé.

## 6. Conditions de délivrance, séparées et actuellement toutes absentes

Le présent fichier **fixe la méthode**, pas les conditions administratives ou techniques d'exécution. Le [manifeste](STAGE6_LIGHT_PROTOCOL_METHOD_V1.json) est `FAIL_CLOSED` : `worlds_allowed=false`, `cohorts_allowed=false`, `engineering_rehearsal_allowed=false` et toutes les preuves de levée à `null`. Une application qui lit ce document/JSON comme une permission est fautive. **Aucun nouveau runner scientifique n'est créé dans cette PR.**

Avant **même une répétition vivante de cohorte d'ingénierie**, exiger une autorisation spécifique de cette répétition, la traçabilité de l'identité d'exécution et une protection des sorties (résultats de survie occultés). Les tests purement statiques et synthétiques **sans World/vie** sont permis dès maintenant. L'ingénierie ne devient jamais preuve.

Avant toute **cohorte scientifique**, il faut, dans cet ordre, une décision portée par le propriétaire sur la variante G/S/R de l'ADR-0017, un transport I3 indépendant et testé, une allocation prospective fraîche et indépendante des 288 graines de mondes + 384 fondateurs et autres flux aléatoires, le plan d'estimand et de puissance conservé, l'examen d'intégrité/couts, une répétition scellée **complète à la même échelle** en Python 3.11 et 3.12 sur source exacte, puis **une levée explicite indexée par le propriétaire** (source/transport SHA, protocole/manifest SHA, graines, indices, scope, non-réessai et limites), enregistrée dans les autorités du dépôt. Si l'une manque, résultat `NOT_RUN_NO_AUTHORIZATION`, aucune entrée World.

Après émission de l'autorisation : une seule cohorte scientifique prospective, aucun arrêt favorable, aucune relance, aucune récupération postmortem. Un changement de source, de modèle, de coefficient, de coût, de plan, de graine ou de règle après rehearsal invalide le prêt-à-exécuter et impose **un nouveau cycle d'autorisation**. Le statut scientifique Stage 2 reste distinct ; un résultat Stage 6 ne le promeut pas.

## 7. Préengagement, traçabilité et rapport final prévu

Cette version est **fixée avant de nouvelles cohortes Stage-6-light** mais résulte de la lecture antérieure de P3 et du modèle nul. Elle n'est ni un préengagement ex nihilo, ni un scellement indépendant du temps. Conserver le SHA de ce commit et le SHA de ce document/JSON en tant que **référence de conception**. L'acte scientifique prospectif futur devra faire l'objet d'un **nouveau manifeste d'exécution immuable**, approuvé et scellé avant la première vie, portant la chaîne exacte des permis et de la répétition.

Le rapport final publiera, même défavorable : identité du protocole et du transport ; origines et empreintes de chaque World et vie ; 16 contrastes `C[p]` ; signes positifs/négatifs/nuls ; sentinelles ; fondateurs ; morts/censures ; coûts ; tous les écarts de protocole ; liens vers les scellés ; conclusion limitée aux familles F0 et à la référence figée. Aucune inférence si la provenance ou l'indépendance n'est pas vérifiable.

## 8. Résumé de décision technique et limites

- **Méthode arrêtée ici :** 16 × 24 × G0/G1/G2, 3 familles × 2 répétitions, G0 unique, 11 520 vies **éventuelles**, seuil bilatéral 13/16, contrôles neutres et arrêts explicites.
- **Manque de preuve non dissimulé :** l'échangeabilité des signes, l'indépendance physique des futures graines et la puissance réelle devront être défendues à partir du transport et de l'allocation préexposés. L'ancien bundle n'a pas de preuve temporelle indépendante du premier calcul.
- **Aucune permission nouvelle :** pas de cohorte, pas de World, pas de vie, pas de nouveau moteur, pas d'indice, pas de verdict, pas de reprise de P3. `I1` reste actif et `I3` la référence non enregistrée.

**Prochaine étape sans World :** tester le contrat de méthode et le futur réducteur sur **données synthétiques uniquement**, puis préparer la demande de levée scientifique distincte. **Aucune campagne vivante n'est lancée par ce protocole.**
