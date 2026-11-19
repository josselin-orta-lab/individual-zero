# i3 Stage8-C : résultat prospectif S−M positif, audit indépendant des 32 256 vies

**Observation : 18 novembre 2026 ; consolidation documentaire : 19 novembre 2026.**
**Verdict primaire figé : `STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0 / CLOSED_NO_RETRY`.**
Cette page est rétrospective : elle ne modifie ni le [protocole prospectif](STAGE8C_THREE_ARM_PROSPECTIVE_PROTOCOL_2026-11-18.md), ni l'[annexe d'admission](STAGE8C_SCIENCE_ADMISSION_APPENDIX_2026-11-18.md), ni la source expérimentale, les graines, les parents ou les vies. Aucune nouvelle vie n'a été créée pour ce rapport.

## 1. Sources et chaîne chronologique

- **Run scientifique unique :** [GitHub Actions #44320492293](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44320492293), `completed/success`, tentative 1, source verrouillée `a32b7bf50981e0bbaf688e3caf9973525888c05d`, terminé le 18 novembre à 21:58:41 UTC. Les jobs `preflight`, `engineering (3.11)`, `engineering (3.12)`, `technical_gate` et `science` ont tous réussi. Les deux répétitions techniques de **32 256 vies chacune** sont distinctes de la cohorte scientifique et n'ont pas servi à décider S−M.
- **Preexposition AVANT la cohorte :** artifact scientifique `14455899574`, publié à 18:07:16 UTC, allocation SHA-256 `bee65ba13a75eca1b283f1558aba2fc5418748aa84c35d8525fe6646b8dd22b6`, 192 mondes G2 réservés sous `9927f47772378559d714c8ef66b65b8dcfeb3766e39e1d1db69562245bf5683e`. La méthode prospective avait SHA `c63ef4730795f54d6fba282010a70e7fa32760717967af280ac4169d9bced8c4`. La publication a précédé la naissance scientifique.
- **Résultat et originaux :** `stage8c-new-prospective-scientific-result-44320492293` artifact `14475820464` ; `stage8c-new-prospective-original-science-lives-44320492293` artifact `14476010510` (**32 256 vies gzip scientifiques**, archive GitHub ~1,26 Go). Le reçu `SCIENCE_RECEIPT.json` renvoie à `SCIENCE_FINAL.json` par SHA-256 `ba75333cf293141917afe91768276576f3a6acf079ecde3685e3f65156b73b93`.
- **Deuxième audit indépendant, préfigé :** [Actions #44406977082](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44406977082), succès le 18 novembre à 22:04:11 UTC. Le job a utilisé le code auditeur immuable **antérieur au verdict** `23d0e3eabff0042123c84f4b292a2e4c72cfcc8f` (PR #1446), distinct du code scientifique d'origine ; rapport artifact `14476915655`. **Statut : `READ_ONLY_32K_ORIGINALS_REPRODUCED`**.
- Les deux **petits ZIP de résultat et d'audit** ont été récupérés et lus séparément pour cette consolidation : SHA-256 ZIP respectivement `b3fc4a0e5814607688be4ed1c8a972ba65506b0669229438811739fcee683b4c` et `ed7f9b2c3b48640fc4d73d8e7f704d61ba7b0b0e59c315ca3ecf667ed90433fb`. Le ZIP volumineux des vies n'a **pas** été téléchargé ni rehashé dans cette consolidation ; **son audit complet est celui du runner distinct #44406977082**, pas une prétendue troisième relecture locale.

L'[ancien registre de garde pré-verdict](STAGE8C_ORIGINALS_CUSTODY_HANDOFF_2026-11-18.md) reste conservé tel qu'il a été rédigé avant publication. Sa chronologie de `in_progress` n'est pas le statut scientifique actuel.

## 2. Hypothèse, trois bras et règle figée

Les trois lignées G1/G2 partent de G0 commun et reçoivent les mêmes six opportunités de World F0 par génome et génération, sans imposer leurs décisions motrices :
- **S, sélection fondée sur la persistance vécue** des parents, avec poids de rang 24 à 1 ;
- **M, témoin à multiplicité parentale exactement appariée** : permutation aléatoire préallouée des parents S vers les **propres parents du bras M** ; les multiensembles de nombres de descendants sont égaux, mais pas nécessairement la diversité réelle des génomes ;
- **U, contrôle parental uniforme**, sans lecture des scores.

Le génome v4 muté est transmis, mais **pas la mémoire vécue**. Les mondes G2 ont été préalloués avant G0, sans servir aux classements G0/G1. Moteur P1.3 funded-v2, cognition facturée, horizon 400 et décès irréversible sont identiques.

Pour chacun des **32 groupes-populations indépendants présumés**, l'estimand primaire est le contraste G2 `D[p] = moyenne_144_vies(S,p) − moyenne_144_vies(M,p)`. Le seuil a été gelé : Student **unilatéral** `alpha=0,025`, `df=31`, `tcrit=2,0395134463964077`; succès si écart-type populationnel non nul et `m−tcrit*s/sqrt(32) > 0`. Les **32 populations**, y compris les négatives, demeurent dans le test, jamais les 32 256 vies comme pseudoréplications.

## 3. Verdict préenregistré

| Mesure de l'unique critère primaire S−M | Résultat scientifique, indépendamment retrouvé |
| --- | ---: |
| Populations | **32** |
| Moyenne du gain de persistance G2 | **+8,6759982639 pas** |
| Écart-type des contrastes populationnels | **19,9913236769 pas** |
| Borne inférieure unilatérale Student à 97,5 % | **+1,4683574706 pas** |
| Statistique t descriptive dérivée | **2,4550** |
| Signes des 32 contrastes | **22 positifs / 10 négatifs / 0 nul** |
| Test primaire | **SUCCESS : `STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0`** |

**Interprétation bornée :** l'étude satisfait son critère prospectif de **gain moyen** au-delà de la concentration *en effectifs* des parents, dans les trois familles F0 combinées. Elle n'établit pas une amélioration pour chaque population. La taille minimale *intéressante pour le dimensionnement* déclarée avant l'étude était **10 pas**, tandis que l'effet observé est **+8,676** : ne pas confondre le succès statistique contre zéro avec la démonstration d'un gain pratique supérieur ou égal à 10 pas. L'indépendance entre populations et les hypothèses Student sont présumées, non démontrées par le scellé cryptographique.

## 4. Résultats descriptifs séparés du primaire

| Contraste ou mesure G2 | Valeur | Populations + / − |
| --- | ---: | ---: |
| **S−U**, contrôle uniforme (secondaire) | **+11,431424 pas** | **20 / 12** |
| **M−U**, concentration parentale appariée vs uniforme (secondaire) | **+2,755425 pas** | **18 / 14** |
| Moyenne durée vécue S | **254,286241 pas** | sans objet |
| Moyenne durée vécue M | **245,610243 pas** | sans objet |
| Moyenne durée vécue U | **242,854818 pas** | sans objet |
| Fraction G2 censurée vivante à 400, S / M / U | **31,684 % / 26,888 % / 25,608 %** | sans objet |

Ces mesures ne remplacent **pas** le test S−M et ne sont **pas** trois autres tests confirmatoires. Les décès survenant exactement à 400 sont distincts des censures de survivants. Les sous-panneaux P00–P15 et P16–P31 ont des moyennes descriptives S−M de **+7,6723** et **+9,6797 pas**, mais constituent ensemble **une seule étude** de n=32, pas deux réplications scientifiques.

## 5. Les dix populations défavorables conservées

Ces identifiants appartiennent uniquement à **Stage8-C**, sans confusion avec les populations homonymes de Stage7/Stage8-A/Stage8-B. Les trois contrastes sont des durées G2 en pas, non des changements causalement identifiés de gènes.

| Population | S−M (primaire) | S−U (secondaire) | M−U (secondaire) |
| --- | ---: | ---: | ---: |
| P00 | −3,465 | −11,104 | −7,639 |
| P01 | −23,042 | −15,139 | +7,903 |
| P03 | −26,958 | −19,250 | +7,708 |
| P11 | −7,208 | −6,729 | +0,479 |
| P16 | −3,951 | +29,188 | +33,139 |
| P18 | −20,000 | −2,021 | +17,979 |
| P19 | **−33,312** | +0,500 | +33,812 |
| P24 | −11,972 | −11,625 | +0,347 |
| P28 | −12,438 | −2,042 | +10,396 |
| P31 | −11,722 | +11,993 | +23,715 |

**Attention aux effets de couplage mathématique :** `S−M = (S−U) − (M−U)`. Les dix valeurs négatives S−M sont donc mécaniquement liées aux autres colonnes ; remarquer que M−U est positif pour neuf sur dix **n'identifie pas** un mécanisme avantageant M, ne prouve pas une sélection inverse et ne justifie pas un sous-test confirmatoire post hoc. Les tableaux des **32 populations**, y compris les 22 favorables, demeurent dans `SCIENCE_RECEIPT.json` et le rapport brut indépendant.

## 6. Portée de l'audit brut et décision

Le second auditeur a rapporté : `native_original_lives_rehashed=32256` (G0 **4 608**, G1 **13 824**, G2 **13 824**) ; `mutated_parentage_reconstructed=4608` ; **768 génomes fondateurs** vérifiés à partir des graines dans le programme d'audit ; deux chaînes de neuf phases et contrôle des engagements de World G2 ; **32 contrastes** et la **borne Student** reproduits à l'identique, avec `new_lives=0`, `new_worlds=0`. Chaque vie a été contrôlée sur empreintes compressées/décompressées, identité, génome, coût corporel, décès/censure et World ; l'audit ne rejoue pas le moteur ou la physique.

**Il ne prouve pas** un gène causal, le rôle fonctionnel de chaque variante génétique, l'égalité de diversité génomique S/M, une hérédité de la mémoire, l'indépendance statistique réelle des populations, l'équivalence écologique ou une généralisation hors F0. Les données proviennent d'un hébergeur interne non attesté par un tiers. Les archives d'Actions ont une rétention de 90 jours : prévoir conservation des octets exacts et de leurs SHA au-delà de l'échéance proche du **16 février 2027**.

**Décisions conservées indépendamment :** Stage7 négatif selon sa règle stricte 13/16 ; Stage8-A positif pour le gain moyen S−U ; Stage8-B négatif sur l'interaction spécifique entre familles ; **Stage8-C positif selon sa propre règle S−M**, fermé sans relance. Ni promotion de I3 (I1 actif), ni verdict général de Stage2.1 (`NOT_ISSUED/HOLD_NO_VERDICT`).

**Suite scientifique distincte à instruire, pas à supposer prouvée :** étude post hoc en lecture seule sur les génomes/scellés de Stage8-C pour mesurer diversité génétique, survie par variante et profils défavorables sans pseudoréplication ni choix de gènes après observation ; puis, uniquement si une hypothèse mécanistique falsifiable apparaît, nouveau protocole prospectif **préenregistré avant naissance**, avec contrôle de diversité réelle et généralisation hors F0. Les cohortes Stage8-C sont définitivement consommées.
