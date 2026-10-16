# Individual Zero — Spécification MVP v1.3.3

**Titre :** Modèles partiels de transitions physiques, incertitude explicite et frontières de preuve.  
**Date :** 16 octobre 2026. **Langue normative :** anglais ; cette version française est informative.  
**État :** contrat d'un modèle expérimental, validation scientifique et activation cognitive autonome **NON AUTORISÉES**.  
**Héritage :** v1.3.2 GA-01 à GA-08, v1.3.1 et v1.2.1 intégralement maintenues.  
**Référence de développement :** `main` `0dee00823c3256223bb503d2a9eccd8cc0ac6408`.

## 0. Autorité, portée et invariants

Cette révision additive traite le modèle prédictif de Stage 6 à la lumière d'A2.30. Elle ne modifie pas les textes historiques ni les exigences antérieures, n'introduit pas un nouveau moteur de décision et n'autorise aucun branchement du modèle expérimental sur Action Control. La physique WorldBody, la mortalité définitive, une transition effective au maximum par commande admise, l'interdiction de cognition postmortem, les propriétaires canoniques, les six phases, les UC, l'état atomique M11, le journal causal complet chaîné, les mémoires consolidées séparées, l'indépendance Oracle/Bench/Observer et DC-05 sont maintenus. Stage 9 reste scientifiquement NO-GO et Stage 12 PARTIAL ; option B désactivée par défaut. Aucune donnée cachée ni responsabilité causale distale ne peut être inférée par analogie numérique.

## 1. Matrice des preuves scientifiques

| Réf. | Source originale et contre-vérification | Mesure et portée | Conclusion autorisée ; limite |
|---|---|---|---|
| E133-01 | A2.30-ZG/ZH, PR #200 | Huit racines autonomes visibles B deviennent mécaniquement explorables avec un modèle **externe** | Couverture limitée du modèle exact ; ni décision I0 ni mémoire vécue transférée |
| E133-02 | A2.30-ZM/ZN, PR #207, CI #38788052317 | 64 boucles, 260 actes physiques ; seulement 4/64 retours au même état complet | Dérive corporelle et jour/nuit ; aucune autorisation de supprimer ces dimensions |
| E133-03 | A2.30-P/Q/R, PR #189, CI #38730415503/#38731532528/#38732185501 | 128 mondes, 352 actions, audit et replay physique | Trajectoires visibles similaires, dangers et mortalités différents ; pas de certification de sûreté |
| E133-04 | A2.30-ZO/ZP, PR #208/#210, CI #38792466785/#38796472497 | 64/64 prévisions nominales exactes sur six variables, 16 abstentions aux limites, 4 morts cachées, 8 blessures, 8 échecs d'effet | Généralisation partielle de laboratoire uniquement ; aucune intégrité, terminalité ni sûreté prédite |
| E133-05 | A2.30-ZS/ZT, PR #213–#215, CI #38801013480/#38802690308 | 16 entraînements, 104 essais tenus à l'écart, 208 enveloppes pré/postaction ; 26 tests négatifs sous chaque Python | Prévision préaction reconstruite ; ni signature temporelle de tiers, ni nouvelles cohortes autonomes |
| E133-06 | A2.18/A2.20/A2.25/A2.27, #110 et PR #184 | Confusions d'agence, historicité des jugements, essais autonomes bornés | Agence proximale et responsabilité distale distinctes |
| E133-07 | Stage 9 #89/DC-05, CI #38451074883 | Causes toxiques confondues, abstention prudente | Danger indiscernable ; pas de changement de validation scientifique |
| E133-08 | M11 H600 ; PR #217 CI #38839538564 | Archives de 600 pas et huit jobs transversaux réussis sur le HEAD de PR | Résultats techniques ciblés, pas validation du nouveau modèle |

Les sources d'origine conservent les protocoles, SHA, dénominateurs, témoins, exceptions et limites. Un audit indépendant des mêmes archives n'est pas une cohorte physique indépendante. Deux interpréteurs rejouant les mêmes mondes déterministes ne doublent pas l'effectif.

## 2. Exigences normatives stables

### V133-MDL-01 — Résultat typé et provenance

Toute prévision doit porter : version du modèle, identifiant immuable du corpus, portée exacte/partielle, origine vécue ou laboratoire, instant de prévision, composantes connues et inconnues, raison d'abstention et autorisation éventuelle d'usage cognitif. Le modèle partiel ne doit jamais se déclarer `EquipmentModel.predict` ni construire une `EquipmentPrediction` ou un `SimulationState` complet. Inconnu, absent et non calculé ne signifient ni « faux », ni « sûr », ni risque nul.

### V133-MDL-02 — Prototype à six dimensions

Le modèle de recherche initial peut estimer uniquement les variations de `x`, `y`, énergie, nourriture, eau et inventaire `berry_b` sur des transitions antérieures non terminales effectivement observées. Intégrité, terminalité, voisinage futur complet, toxicité, sûreté alimentaire/motrice et responsabilité causale distale restent inconnus. Le prototype initial couvre exclusivement déplacement est et collecte non ingestive B. Une prévision exacte de ces six dimensions ne certifie aucune sûreté.

### V133-MDL-03 — Admission des données et absence de fuite

Chaque apprentissage doit reposer sur la chaîne authentifiée et ordonnée : perception préaction, commande réellement exécutée, conséquence accessible, références et versions. La prédiction gelée précède l'issue évaluée. Aucun résultat futur, secret WorldBody, Oracle ou Bench ne doit entrer dans la prédiction. Un corpus de laboratoire indépendant ne devient jamais automatiquement une mémoire vécue par I0. Les audits, replays et interpréteurs partagent explicitement l'identité de la cohorte d'origine.

### V133-MDL-04 — Abstention conservative

S'abstenir avec raison traçable si commande hors domaine, observation ou exemple manquant, delta non stable, contexte hors distribution, borne numérique, risque physique non observable ou budget insuffisant. Ne jamais déduire la sûreté d'une confiance nominale élevée. Les échecs physiques cachés comptent comme erreurs de prévision et non comme exclusions opportunistes.

### V133-MDL-05 — Isolation et décisions

Le modèle est **désactivé par défaut dans la cognition vivante**, ne peut pas envoyer de commande, affaiblir Stage 9, se substituer au simulateur exact de Stage 6 ni produire d'état physique complet. Une évaluation shadow embarquée demande préalablement : protocole autorisé à la naissance, propriétaire canonique, UC bornées, reçus durables, continuité M11 authentifiée, témoins autonomes appariés et absence d'interférence. Ni élargissement arbitraire de l'horizon ni branchement silencieux à BFS n'est permis.

### V133-MDL-06 — UC

Le temps machine d'un laboratoire externe ne constitue pas des UC de l'individu. Aucun coût UC vécu de ce modèle n'est démontré par ZO/ZS. Avant emploi vivant, définir propriétaire, charges positives déterministes, nombre de recherches et horizon bornés, réponse à un refus de budget, coût d'opportunité et distinction entre travail indisponible et absence de causalité.

### V133-MDL-07 — Mémoire, journal et mortalité

Maintenir identité et origine des perceptions et effets, non-rétroactivité des jugements, six passes privées de consolidation, coupure et événements postérieurs, publication atomique, journal intégral, audit vérifiable et génération M11 courante uniquement. Aucune résurrection, réécriture historique, cognition postmortem ou apprentissage externe déguisé en vécu.

### V133-MDL-08 — Conditions scientifiques d'activation

Statut **NO-GO** jusqu'à une nouvelle campagne indépendante préenregistrée : prévisions prospectives, témoins avec table exacte inchangée, décisions et transitions autonomes réelles, observation vécue, vérité physique externe séparée, dangers mortels cachés, abstentions, coûts UC, trajectoires longues, audit des archives brutes et critères GO/INCONCLUSIVE/NO-GO prédéfinis. Ni augmentation de couverture ni succès en laboratoire ne suffisent. Activation uniquement après décision explicite de l'opérateur. Statuts des Stages 9 et 12 séparés.

### V133-MDL-09 — Conformité logicielle

Exécuter sous Python 3.11 et 3.12 : nominal, obstacle visible, entraînement instable, ingestion interdite, borne corporelle, incertitude sur danger caché, provenance invalide, données absentes, stabilité de série, isolation de propriétaire et non-régression Stage 9/10/11/12, M11 et Observer. Conserver SHA exact du code testé et empreintes des résultats. Le succès d'une CI, d'une fusion ou d'un document normatif n'est pas un succès scientifique.

### V133-MDL-10 — Arbitrages opérateur

Activation cognitive, nouvelles compétences alimentaires, importation des démonstrations externes, changement d'horizon, acceptation d'actions dangereuses, modification d'Oracle, WorldBody ou de la mortalité exigent chacun une autorisation distincte et de nouveaux essais. Rien de tel n'est autorisé ici.

## 3. Responsabilités par Stage

Stages 1 à 3 : identité, monde physique et perception propre. Stages 4 et 5 : motifs, options et compétition. Stage 6 : simulateur exact borné, avec prédicteur factorisé **strictement externe et non décisionnel**. Stages 7 et 8 : motivation et apprentissage contraints par UC. Stage 9 : filtre causal/danger inchangé. Stage 10 : consolidation privée en six passes, publication atomique. Stage 11 : mémoire vécue et exploration avec provenance. Stage 12 : jugement d'agence proximal/distal incertain, jamais transformé par une simple prédiction en causalité démontrée. Action Control conserve exclusivement les commandes exécutables.

## 4. Migration depuis v1.3.2

| Contrat historique | Traitement v1.3.3 | Effet logiciel |
|---|---|---|
| Stage 6 / Equipment exact / horizon borné v1.2.1 | **Conservé**, complété V133-MDL-01/02/04 | Aucune modification de la planification active |
| v1.3.1 journal, M11, mortalité, Oracle/Bench et UC | **Conservé**, précisé V133-MDL-03/06/07 | Aucun changement du schéma de sauvegarde |
| GA-01 à GA-08 de v1.3.2 | **Conservé**, distinct de la prédiction | Aucune activation supplémentaire |
| DC-05 et NO-GO Stage 9 | **Conservé** | Aucun changement de seuil ou veto |
| Candidat A2.30 de laboratoire | **Ajout expérimental**, V133-MDL-01..10 | `src/i0/experimental/stage6_visible_delta_shadow.py` seulement |
| Généralisation cognitive et apprentissage vécu | **Différé** | Aucun import dans le runtime, nouveau propriétaire ou UC |

## 5. Préenregistrer la prochaine campagne

Geler le SHA de développement, l'hypothèse, les dénominateurs, graines, populations et critères d'arrêt **avant** les résultats. Constituer de nouveaux corpus d'entraînement et de test disjoints, avec conditions nominales, interventions létales/échecs cachés, saturation corporelle et hors distribution. Déclarer a priori l'erreur des six composantes, couverture, faux certificats, taux d'abstention, mortalités, données manquantes, origine des preuves, consommation UC, parité des décisions autonomes et comparaison avec la table exacte. Un modèle shadow ne modifie pas les commandes du témoin. Toute évaluation d'un effet sur les décisions attend une autre autorisation. Les archives ZO/ZS/ZP/ZT ne peuvent pas être recyclées comme validation prospective indépendante ; les SHA n'attestent pas à eux seuls l'ordre temporel contre un auteur privilégié.

## 6. Statuts de livraison

**Norme :** proposée en PR protégée. **Code :** prototype externe de diagnostic, à valider sur le SHA exact. **Science :** généralisation bornée au laboratoire A2.30 ; nouvelle campagne non exécutée. **Déploiement cognitif : NO-GO.** **Stage 9 : NO-GO scientifique. Stage 12 : PARTIAL.** Activation de nouvelles compétences et modification du statut des Stages : décisions explicites de l'opérateur uniquement.
