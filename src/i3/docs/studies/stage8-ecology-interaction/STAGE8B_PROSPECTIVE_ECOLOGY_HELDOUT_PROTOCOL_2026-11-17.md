# i3 Stage8-B · Interaction prospective sélection parentale × écologie (17 novembre 2026)

**Statut initial : `PROSPECTIVE_PROTOCOL_PRE_EXPOSURE_NO_STAGE8B_LIVES`.** Le présent protocole est une NOUVELLE étude source-verrouillée. Les mondes, lignées et graines des campagnes Stage6, Stage7 et Stage8-A sont fermés sans relance et ne sont PAS des observations Stage8-B. Aucune donnée de Stage8-B n'est autorisée à modifier ce protocole, l'effectif ou le seuil après la première naissance.

## Hypothèse et falsificateur

Stage8-A a satisfait son critère distinct de **gain moyen** G2 : +14,4874 pas (borne Student unilatérale 97,5 % +7,9933 ; 23+/9−) sur 32 populations, [source scellée](../stage8-mean-persistence/STAGE8A_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-17.md) et [audit indépendant](../stage8-mean-persistence/STAGE8A_INDEPENDENT_READONLY_AUDIT_RESULT_2026-11-17.md). Sa décomposition **POST HOC** donne : stable +12,862, depletion +14,549, pulse +16,051 pas. Les écarts observés entre familles sont petits et très dispersés ; sur ces anciennes 32 populations, un omnibus descriptif de Hotelling aurait donné p≈0,865. **Aucun effet d'interaction spécifique n'a été démontré.**

**Question Stage8-B, distincte :** le bénéfice (positif ou négatif) d'une sélection de parents selon la persistance corporelle effectivement financée varie-t-il entre les **trois écologies F0** `stable`, `depletion`, `pulse`, lorsque de nouveaux descendants G2 sont évalués sur des **mondes jamais ouverts, réservés avant naissance, indépendants des mondes servant à sélectionner leurs parents** ?

Pour chaque population p et famille f, comparer **les mêmes opportunités World dans les deux bras G2** : `D[p,f] = mean(steps_lived G2 selected sur 24 génomes × 2 répétitions de f) − mean(steps_lived G2 random_parent sur les mêmes 2 World)`. Le témoin `random_parent` sélectionne des parents uniformément **sans consulter leurs scores** ; le bras `selected` tire selon des poids de rang 24…1, déterminés seulement par les 6 vies de persistance G1 déjà scellées. Le génome v4 muté est transmis, jamais la mémoire. Le moteur P1.3 funded-v2, les paiements énergie/vigilance, le code de décision et le traitement de la mort sont identiques aux deux bras. **Une mort exactement au pas 400 est distincte d'une vie censurée vivante au pas 400.**

## Effectif, réservation et holdout de mondes

- **32 NOUVELLES populations** indépendantes *selon le plan* (deux sous-panneaux de 16), chacune avec 24 fondateurs G0. Les 32 populations sont les **seules unités inférentielles**, et non les 23 040 vies.
- Par génération, six opportunités écologiques (trois familles F0 × deux répétitions) pour chaque génome. G0 commun aux bras, G1/G2 deux bras. Chaque exécution comprend 4 608 vies G0, 9 216 G1 et 9 216 G2 = **23 040 vies natives** et 576 opportunités World, avec 18 phases scellées (2 × 9). **192 identités de monde G2** (`population,family,repeat`) sont préallouées et publiées dans `g2_holdout_reserved_worlds` avec graines, index, et empreinte SHA avant toute naissance.
- Nouvelle racine de 256 bits issue de l'OS pour CHAQUE exécution, domaine HMAC **`i3-stage8b-new-ecology-heldout-v1`** séparé du générateur historique Stage8-A/Stage7/Stage6. Les mondes G2 sont précommis avant G0, ne sont **pas** utilisés pour sélectionner G1 ou les parents G2, et les deux bras G2 sont exposés aux mêmes conditions pour un contraste apparié. Les graines G0, G1 et G2 sont disjointes ; ne jamais rééchantillonner une allocation après échec ou résultat défavorable.
- Ces nouveaux mondes sont des **nouveaux tirages des mêmes trois familles F0**, pas de nouvelles familles hors F0 ni une preuve de généralisation écologique complète. Aucune intervention ne force les décisions motrices des individus.

## Test confirmatoire unique, fixé AVANT naissance

L'hypothèse nulle est **H0 : l'avantage moyen de la sélection est identique dans les trois écologies F0**. Elle n'implique pas un avantage nul : les trois familles peuvent être toutes favorables, avec un gain moyen comparable.

Construire les **32 vecteurs de deux contrastes populationnels** :
```text
x[p] = D[p,depletion] − D[p,stable]
y[p] = D[p,pulse] − D[p,stable]
m = (mean(x), mean(y))
S = covariance empirique 2×2 de (x,y), diviseur 31
T² = 32 × mᵀ × inverse(S) × m
F = (32−2)/(2×(32−1)) × T² = (30/62) × T²
p = Pr(F_{2,30} ≥ F_observé) = (1 + 2F/30)^(−15)
```

**Succès : `STAGE8B_SELECTION_BY_ECOLOGY_INTERACTION_F0` si et seulement si S est définie positive non singulière et p strictement inférieur à 0,025.** Le test est **omnibus, bilatéral et à deux degrés de liberté** : il peut détecter une hétérogénéité entre familles quel que soit son sens, sans choisir `pulse` après coup. Sinon : `STAGE8B_NO_INTERACTION_DEMONSTRATED_F0`. Une covariance singulière ou quasi singulière ne produit **jamais** de succès automatique ; les hypothèses de validité et le statut doivent rester visibles. Les 32 populations négatives, positives ou nulles sont conservées, sans exclusion. Toute violation de provenance, original manquant, matrice de populations incomplète, panne ou archive rompue signifie **`TECHNICAL_NO_VERDICT_NO_RETRY`**, pas un résultat scientifique négatif.

**Limites statistiques préenregistrées :** l'inférence de Hotelling requiert des populations statistiquement suffisamment indépendantes et une approximation multivariée normale raisonnable. La séparation cryptographique des graines ne démontre pas ces hypothèses. Les familles F0 ne sont pas elles-mêmes randomisées (mécanismes physiques spécifiques) et les étiquettes de bras ne possèdent pas de randomisation indépendante. Les comparaisons directes entre écologies reposent ainsi sur un modèle conditionnel et non sur une intervention biologique causale pure. Les 32 observations historiques Stage8-A suggèrent une très faible puissance pour des différences d'environ 1 à 3 pas face à des SD pairées d'environ 23 à 33 pas : **un résultat non significatif n'établirait pas l'équivalence écologique**. Aucun ajout de populations après observation n'est permis.

## Secondaires et publication des négatifs

Rapporter **tous les 32 D[p,f]** et les 32 `D[p,G2]`, les trois moyennes écologiques, les effectifs +/−/0 par famille, l'écart entre chaque paire de familles et les intervalles descriptifs de Student 95 % au **niveau population**, sans les transformer en trois tests confirmatoires non corrigés. Rapporter aussi G0, G1, G2, survie censurée à 400, familles perdantes, parents distincts et mutations d'ascendance, mais aucun indicateur secondaire ne remplace l'unique test omnibus. G0→G1→G2 ne constitue pas une trajectoire causale brute car les mondes changent.

## Séquence technique et garantie de non-relance

Un seul workflow `i3-stage8b-ecology-heldout-once-20261117.yml`, déclenché **une seule fois par son ajout sur `main`** sur un HEAD propre et source-verrouillé. CI logiciel Python 3.11/3.12 d'abord, avec tests synthétiques **sans aucune vie**. Ensuite :
1. Deux **répétitions d'ingénierie complètes**, Python 3.11 puis 3.12 indépendantes (en parallèle), **23 040 vies natives chacune** et deux racines d'entropie différentes. Publier chaque plan **avant la première vie** ; conserver 18 phases scellées, toutes les vies gzip, décès/censures, reçus source-exacts et noms d'archives distincts. Ne pas divulguer les effets d'ingénierie comme résultats scientifiques.
2. **Seulement après les DEUX succès complets**, vérifier les deux reçus Stage8-B (anciens reçus Stage8-A rejetés), puis allouer une **troisième nouvelle racine** scientifique avec nouveau plan, nouvelles graines G2 réservées et empreinte publiée avant première vie.
3. Exécuter l'unique cohorte scientifique G0/G1/G2 (23 040 vies) avec traces originales complètes ; reconstruire toutes les familles G2, les 3 072 tirages parentaux et mutations, vérifier les scellés et publier le résultat, même négatif, ainsi que les 32 × 3 effets et les originaux.

**Total maximal : 69 120 vies natives** (46 080 d'ingénierie + 23 040 scientifiques), sans rerun, remplacement, extension d'échantillon, tirage favorable ni changement de seuil. Un `run_attempt >1` est bloqué. Les plans, méthodes, autorisations ADR-0022 et schémas sont source-locked ; les allocations consommées restent consommées même si l'upload échoue. Le stockage GitHub est à rétention limitée ; conserver copies des ZIP originaux et SHA-256.

## Statut scientifique et éthique de publication

- Stage8-A demeure **`STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0 / CLOSED_NO_RETRY`**. Son bénéfice moyen n'établit pas l'interaction écologique recherchée.
- Stage7 conserve son verdict négatif directionnel, indépendamment de Stage8-B.
- Un Stage8-B positif prouverait au mieux une **hétérogénéité statistique entre les mécanismes écologiques F0** dans ce protocole ; il n'identifierait ni gène causal ni impact hors F0, ni intelligence générale, ni promotion du moteur.
- Provenance `INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED` : témoins externes non requis par ADR-0022, mais aucune attestation extérieure revendiquée. I1 actif, I3 référence de développement non enregistrée, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT` inchangé.

**Statut à la publication initiale de ce document : `PROSPECTIVE_PLAN_FROZEN_NO_LIVES`.** Le code, les tests synthétiques ou un plan publié ne constituent jamais un résultat scientifique.
