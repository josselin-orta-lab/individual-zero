# I3 — Limites et scénario de généralisation sans règles imposées (vérifié sur main e4eb3e8)

Nov 6, 2026 · @Josselin

## En bref

La vérification directe de `main` (commit `e4eb3e8`, issu de la PR #1058, sans commit plus récent) confirme presque tous les chiffres du rapport précédent, ainsi que la description du code. Une conclusion change : **P5e ne montre pas de défaut de la Competition.** Les repas « perdus » s'expliquent surtout par l'absence de faim, par des déficits concurrents ou par d'autres plans alimentaires.

- **Ce qui porte la survie en monde neuf :** le modèle d'effets appris (0/288 survivants sans lui, contre 112/288) et le bonus de curiosité (4/288 sans lui, contre 110/288).
- **Ce qui n'a pas d'effet mesurable :** la valeur TD (117/288), le replay (119/288), la prudence (105/288) et la sélection de lignée (47/144 contre 42/144).
- **Ce qui empêche de conclure :** avec n=4 populations, aucun test ne peut descendre sous p=0,125, même quand les 4 vont dans le même sens.
- **Ce qui change dans le scénario :** la « simplification de la Competition » descend au rang d'audit léger. La priorité reste de remplacer la curiosité additive par une valeur d'information exprimée en détresse prédite, puis de laisser l'individu décider combien penser.

## Ce qui a été vérifié et ce qui a été corrigé

Cette fois, les fichiers ont été lus directement par Git, et non plus à travers les issues :

- **Statut et plan :** `src/i3/docs/STATUS.md`, `DEVELOPMENT_PLAN.md`, `P2_COST_AUDIT_RESULTS.md`.
- **Résultats d'études :** les `RESULTS.md` de P3 et de P5a, et les analyses post hoc de P5b (`POSTHOC_SCORE_TERMS.md`) et de P5c (`POSTHOC_ACTIVE_MORTALITY.md`).
- **Code :** `modules/mind.py` et `modules/genome.py`.
- **Données originales de P5e :** le fichier compressé de 24 vies.

`main` compte 192 commits depuis la physique v2, et aucun après P5e.

| Point du rapport précédent | Statut | Correction |
| --- | --- | --- |
| Chiffres P2, P3, P4a, P4b, P5a, P5b, P5c | Confirmés | — |
| Code : détresse D(h), curiosité β\_u × u × pertinence, prudence λ\_r × u × (w\_I·d\_I + κ₀), veto à 10, seuil de Competition 1,5, 30 gènes | Confirmé dans `mind.py` et `genome.py` | — |
| Réserve P4 1 200 000–1 200 199, validations futures ≥ 120 | Confirmé | — |
| P5e : « 333 occasions de repas sur 342 perdues ; la Competition renverse le classement » | **Erroné** | Dans 333 cas, une autre option avait déjà un score brut strictement supérieur. Le seuil n'a changé l'issue que 6 fois (3 repas en tête perdus, 3 repas moins bien notés gagnants) |
| Limite (g) : « seuils de Competition, risque élevé de règle cachée » | **Surévalué** | Écarts rares, 6 sur 342 : risque faible à moyen |
| Étape « simplifier la Competition » en 3e priorité | **Rétrogradé** | Audit léger, priorité basse |
| P5c : « 809 attentes contre 383 » | Imprécis | 809 commandes de repos *ou* d'attente (dormir/attendre) contre 383, sur les 12 premiers pas |
| P5b post hoc : « l'exploration domine le choix » | Imprécis | 650, 4 587 et 837 décrivent les scores qui *changent* quand on aveugle la lecture par action. L'information apprise atteint donc la décision surtout par le terme de curiosité. Cela ne mesure pas la part de la curiosité dans les choix normaux |
| Replay « 422 400 opérations » | Imprécis | 391 323 replays payés dans le bras normal ; 422 400 dans le bras sans rétention |
| Accès aux sources | Corrigé | Fichiers lus directement par Git (le rapport précédent ne passait que par les issues et PR) |

## Ce que disent les campagnes

Toutes ces campagnes ont été exécutées le 5 et le 6 novembre. Statut constant : I1 actif, I3 non enregistré, réserve P4 scellée, aucun GO scientifique.

| Campagne | Dispositif | Résultat vérifié | Lecture |
| --- | --- | --- | --- |
| Physique v2 (#1004–#1007) | 16 vies de 400 pas, développement | Survie 14/16 → 8/16 | Le coût réel de penser est révélé, sans réajustement |
| G2e | Génomes sélectionnés, graines réservées | 478/1000 contre 364 ; révision 270/500 contre 163 | Croyances révisables adoptées |
| P2 | 36 vies sur 12 mondes, 3 écologies | 31 morts ; 3 483 pas inactifs sur 7 729 (45 %) ; aucun pas sur 7 729 au coût exact du tarif fixe ; référence financée 4/12, oracle 12/12 | Les sondes restent descriptives |
| P3 | 864 vies, 4 populations, 3 générations | G0 34 contre 34 ; G1 37 contre 50 (−13) ; G2 50 contre 45 (+3, +3, −1, 0) ; le bras sélectionné paie plus de cognition (24 817 contre 20 856 en énergie) | Sélection non concluante |
| P4a | 288 vies, 24 mondes de validation | 47/144 contre 42/144 (−2, +9, −1, −1) | Pas de généralisation évolutive démontrée |
| P4b | 576 vies | Apprentissage retenu 84/288 contre 0/288 si les calculs payés sont jetés ; 144/144 histoires distinctes à génome égal | L'apprentissage compte, mais coûts et activité diffèrent |
| P5a | 1 152 vies, mondes 48–71 | Normal 112 ; sans effets 0 ; sans TD 117 ; sans replay 119 ; inactivité 19,80 % contre 72,43 % sans effets | Modèle d'effets vital ; TD et replay sans effet mesurable |
| P5b | 1 152 vies, mondes 72–95 | Complet 98 ; lecture aveugle aux actions 0 ; a priori global 0 ; sommeil aveugle 90 ; inactivité 19,56 % contre 75,6 % | La lecture par action est indispensable |
| P5c | 1 152 vies, mondes 96–119 | Normal 110 ; sans curiosité 4 ; sans prudence 105 ; sans les deux 7 ; inactivité 18,65 % contre 1,13 % sans curiosité | La curiosité porte la survie ; la prudence n'a pas d'effet mesurable |
| P5c post hoc | Données originales | Morts : 178 contre 284, dont 146 contre 239 par soif ; 12 premiers pas : 392 contre 132 commandes ressource, 383 contre 809 repos ou attentes | Sans curiosité, mort *active* par soif, pas par paralysie |
| P5d | 24 vies de développement | Sans curiosité : 761 attentes contre 134, 193 déplacements contre 627 ; 11 contre 10 unités collectées, 0 contre 7 mangées ; 125/125 pas avec un repas payé proposé, 0 choisi | Cause non identifiée (scores complets non enregistrés) |
| P5e | 24 vies de développement, Competition enregistrée en entier | Normal : 342 occasions, 9 repas ; seuil décisif 6 fois ; sans curiosité : 0 collecte, 0 repas, 717 attentes, donc aucune occasion observable | La Competition suit les scores bruts ; voir la section suivante |

Réserve générale : n=4 populations indépendantes. Le test exact bilatéral ne peut pas descendre sous p=0,125 (p=0,375 après correction de Holm). Ces effets sont forts en criblage, mais non confirmatoires.

## Nouvelle lecture de P5e : faim, déficits concurrents, autres plans

Sur les 342 occasions de manger la nourriture portée, l'individu n'avait faim que dans 63 cas. Dans la plupart de ceux où il n'a pas mangé, il a arbitré en faveur d'un autre besoin ou d'un autre repas. On y voit des arbitrages entre enjeux, pas une Competition défaillante.

Cette analyse est la mienne. Elle est post hoc et descriptive, faite sur les données originales archivées du bras normal (`p5e-original.json.gz`), sans aucune nouvelle vie. La faim est mesurée par rapport au seuil θ\_F de chaque génome.

| Étape | Nombre | Ce qui l'explique |
| --- | --- | --- |
| Occasions de repas (nourriture portée, option `manger` payée) | 342 | — |
| … sans aucune faim (nourriture ≥ θ\_F) | 279 | Manger n'apporte aucun soulagement immédiat. Nourriture médiane 53, θ\_F médian 44 |
| … avec faim | 63 | — |
| … avec faim et repas en tête | 5 | — |
| … avec faim et repas battu | 58 | Gagnant : un autre plan alimentaire 27 fois (aller manger ailleurs 17, collecter puis manger 10), dormir 22, explorer 8, attendre 1 |

Parmi ces 58 cas, l'énergie était sous son seuil dans 57, et l'eau dans 44. Le gagnant l'emportait sur la seule détresse prédite dans 43 cas, et grâce au bonus seulement dans 15. Les écarts sont faibles : médiane 0,027 en valeur de base et 0,016 en bonus. La prévision du repas restait correcte, avec un gain de nourriture prévu positif dans 97 % des occasions et une médiane de +10,3.

Deux questions restent ouvertes :

- **P5d.** L'absence totale de repas sans curiosité (0 sur 125 pas avec nourriture portée) n'est pas expliquée. P5e n'a observé aucune nourriture portée dans ce bras.
- **Repas reportés.** Ce report pourrait coûter plus tard : la projection innée sous-estime-t-elle le risque d'attendre ? Seul un test préenregistré sur des mondes neufs peut le dire.

## Les limites d'I3, preuves à l'appui

La limite principale est structurelle : ce qui sauve l'individu en monde neuf passe par un terme ajouté par le concepteur (la curiosité), et non par l'évaluation de ses propres enjeux. Le reste de l'apprentissage est tabulaire ou inerte.

1. **Perception.** Une case de rayon plafonne la recherche : le chercheur systématique ne survit que dans environ 72 % des mondes de développement, et sa version financée dans 4/12 en P2. Les bords jamais touchés restent « inconnus » (artefact de bord vu en G2c). Aucune structure cachée n'est inférée.
2. **Modèle du monde.** Effets tabulaires par couple (action, jeton), avec repli action puis global : aucun transfert entre jetons, lieux ou contextes. Le repli global seul donne 0/288 (P5b). Le changement n'est suivi que par une moyenne mobile : la révision est plus fréquente mais pas plus rapide, environ 130 pas de latence médiane en G2e.
3. **Valeur et crédit.** Le TD linéaire sur 6 caractéristiques n'a pas d'effet mesurable (117 contre 112). L'auto-projection innée fait l'essentiel du travail. Le crédit différé n'est pas appris.
4. **Exploration.** La curiosité β\_u × incertitude × pertinence porte la survie (110 contre 4), mais c'est une formule additive conçue à la main, dans une autre unité que la détresse. Sans elle, l'individu se repose ou attend près de ce qu'il connaît et meurt de soif (239 morts par soif sur 288).
5. **Coût de penser (v2).** Cycles, horizon et mémoire sont des gènes fixes : l'individu ne décide pas combien penser. Inactivité de 19 % en temps normal, 45 % en P2, 72 à 76 % quand ses prédictions sont dégradées. En P3, le bras sélectionné paie plus de cognition sans gagner.
6. **Mémoire.** Capacité fixe ; croyances de lieu sans incertitude explicite ; replay payé (391 323 opérations en P5a) mais sans effet mesurable (119 contre 112).
7. **Ce qui ressemble à une règle cachée :**
   - **curiosité additive :** risque élevé, elle porte la survie ;
   - **prudence :** risque moyen, sans effet mesurable mais facturée ;
   - **veto d'intégrité à 10 :** acceptable seulement comme loi physique du corps ;
   - **seuils de Competition :** risque faible à moyen, 6 écarts sur 342 en P5e ;
   - **types d'options, BFS et frontière :** procédures générales, mais répertoire figé.
8. **Méthode.** n=4 populations (p ≥ 0,125) ; lignée de 3 générations ; sondes non appariées en coût (aucun pas sur 7 729) ; effets de l'énergie non isolés (chaque ablation change aussi la dépense) ; environ 1 ms par pas.
9. **Écologie.** Eau, nourriture, jetons toxiques et trois dynamiques (stable, épuisement, pulsations). Ni danger, ni saisons, ni toxicité différée, ni obstacles, ni concurrents.

## Principe directeur : une seule monnaie, la viabilité prédite

Chaque mécanisme ajouté doit s'écrire comme une contribution à une seule quantité : la détresse cumulée que l'individu prévoit pour ses propres canaux. Cette prévision inclut le coût en énergie et en vigilance de son propre calcul.

- **Un mécanisme général** calcule une conséquence prévue sur ses enjeux. Il ne pousse vers aucun comportement : inférence, planification, mémoire, valeur d'information, valeur du calcul.
- **Une règle cachée** ajoute un terme, un seuil ou un poids qui l'emporte sur cette prévision sans passer par elle. C'est le cas aujourd'hui de la curiosité additive.
- **Admis en plus :** des paramètres génériques héritables, invariants par renommage (ADR-0014), sélectionnés par la seule persistance.
- **Exclus :** les comportements scriptés, les termes propres à un monde, le façonnage de récompense et toute information d'oracle.

Deux cadres de la littérature valident ce principe. Le RL homéostatique ([Keramati et Gutkin 2014](https://elifesciences.org/articles/04811)) fait de la réduction d'écart aux consignes la récompense ; le r = −D d'I3 en est une variante proche. L'inférence active ([Pezzulo, Rigoli et Friston 2015](https://openaccess.city.ac.uk/id/eprint/16671/)) réunit valeur pragmatique et valeur épistémique dans un même objectif. C'est ce qui manque à I3 : une curiosité qui découle de l'évaluation au lieu de s'y ajouter. On garde le calcul explicite et peu coûteux d'I3 plutôt qu'un formalisme variationnel complet, coûteux sous v2 et difficile à auditer.

## Scénario de développement par étapes

Une modification ciblée par porte, préenregistrée avant toute exposition, évaluée sur des mondes neufs (indices ≥ 120, réserve P4 scellée) avec des génomes sélectionnés (ADR-0015). Les résultats négatifs sont conservés, et rien n'est réajusté sur un monde déjà ouvert.

1. **Étape 0 — Rendre les tests capables de conclure.**
   - Porter le nombre de populations génétiques indépendantes à 8 au moins : une unanimité donne alors p ≈ 0,008, contre 0,125 avec 4.
   - Préenregistrer les effets de l'énergie : dépense réalisée, fraction inactive, durée vécue.
   - Lancer le test « même génome, histoires différentes, défi commun » (#1026).
   - Garder l'enregistrement complet de la Competition (P5e) comme instrument standard.
   - Expliquer l'absence de repas de P5d dans un bras où l'individu porte vraiment de la nourriture.
2. **Étape 1 — Valeur d'information dans l'unité de l'enjeu.** C'est la réponse de principe à la priorité du dépôt (« expliquer la mort active sans curiosité »).
   - *Mécanisme :* pour une option exploratoire ou un aliment inconnu, l'individu calcule la réduction attendue de sa détresse prédite grâce à ce qu'il apprendrait. Il fait la moyenne sur les issues que ses croyances jugent possibles, puis replanifie.
   - *Ce qui disparaît :* β\_u, la pertinence et la prudence. L'urgence découle de la projection, et le risque de la distribution prédite des effets sur l'intégrité ([Behrens et al. 2007](https://www.nature.com/articles/nn1954)).
   - *Coût :* 2 à 3 branches simulées, facturées.
   - *Porte :* non-infériorité en survie, supériorité en latence de révision (famille R).
   - *Ablations :* projection figée (la survie doit chuter) ; valeur d'information sans coût (la dépense doit déraper).
3. **Étape 2 — Décider combien penser.**
   - *Mécanisme :* valeur du calcul ([Russell et Wefald 1991](<https://doi.org/10.1016/0004-3702(91)90015-C>) ; [Callaway et al. 2018](https://proceedings.mlr.press/r16/callaway18a.html)). Un cycle de plus n'est fait que si le gain de viabilité attendu dépasse son coût, converti en détresse par D elle-même. Le replay devient un calcul comme un autre.
   - *Gènes :* `n_base` et `h_max` deviennent des plafonds, plus des consignes.
   - *Porte :* survie et fraction inactive, contre budget fixe.
   - *Ablations :* coût mis à zéro ; budget tiré au hasard à moyenne égale.
4. **Étape 3 — Un modèle du monde qui généralise et voit le changement.** Une porte par mécanisme :
   - effets factorisés par attributs perçus génériques, avec a priori partagés ;
   - détection de rupture en ligne ([Adams et MacKay 2007](https://arxiv.org/abs/0710.3742)) ;
   - causes latentes ([Gershman, Blei et Niv 2010](http://www.cs.columbia.edu/~blei/papers/GershmanBleiNiv2010.pdf)).

   La probabilité de rupture alimente la valeur d'information de l'étape 1. *Porte :* latence de révision. *Tests :* éviter dès la première rencontre un jeton nouveau qui ressemble à un toxique connu ; ablation par rupture figée.
5. **Étape 4 — Une valeur réutilisable quand les besoins changent.**
   - *Mécanisme :* caractéristiques successeurs ([Barreto et al. 2017](https://arxiv.org/abs/1606.05312)) sur les variations prévues des canaux corporels, combinées à la D *actuelle*. Quand la faim dépasse la soif, la réévaluation est immédiate.
   - *Porte :* refaire l'ablation P5a. La suppression des valeurs apprises doit maintenant coûter des survies.
   - *Test :* toxicité différée de 20 à 50 pas.
6. **Étape 5 — Une carte pour les obstacles et les grands mondes.**
   - *Mécanisme :* un bord ou un mur adjacent est perçu comme infranchissable, ce qui supprime l'artefact de bord. Une carte topologique est apprise pendant la vie ([Behrens et al. 2018](<https://www.cell.com/neuron/fulltext/S0896-6273(18)30856-0>)) et planifiée sous le budget de l'étape 2.
   - *Porte :* famille F1 tenue à l'écart.
   - *Ablation :* la frontière actuelle. Rayon de perception inchangé.
7. **Étape 6 — Une lignée qui sélectionne des façons d'apprendre.**
   - *Mécanisme :* effet Baldwin ([Hinton et Nowlan 1987](https://www.complex-systems.com/abstracts/v01_i03_a06/) ; [Soltoggio, Stanley et Risi 2018](https://arxiv.org/abs/1703.10371)). La sélection porte sur des paramètres d'apprentissage génériques, sans jamais hériter de poids appris.
   - *Dispositif :* 8 populations au moins, 10 générations au moins, recombinaison, témoin à parent aléatoire, plusieurs familles.
   - *Porte :* P4a refait, sélectionné meilleur dans au moins 7 populations sur 8.
   - *Contrôle :* apprentissage désactivé.

**Audit léger, transversal : la Competition.** Les seuils n'ont décidé que 6 fois sur 342 en P5e. Il suffit de vérifier, par une porte peu coûteuse, qu'on peut les remplacer par « meilleur gain prédit, et continuité justifiée par un coût de changement prévu » sans perte de survie. On retire aussi la prudence, sans effet mesurable mais facturée. Le veto d'intégrité ne reste que s'il est requalifié en loi physique du corps.

## Progression des familles de mondes et mesure de la généralisation

La complexité vient des mondes, jamais de l'agent. Chaque famille est figée, ses graines comprises, avant toute évaluation. Elle peut être générée de façon progressive, à la manière de [POET](https://arxiv.org/abs/1901.01753), mais jamais retouchée après ouverture.

| Famille | Nouveauté | Capacité testée |
| --- | --- | --- |
| F0 (existant) | Stable, épuisement, pulsations | Base actuelle |
| F1 | Obstacles, terrains à coût de déplacement, cartes 2 à 4 fois plus grandes | Carte cognitive (étape 5) |
| F2 | Saisons : sources périodiques | Ruptures et causes latentes (étape 3) |
| F3 | Toxicité différée et cachée, jetons partageant des attributs | Crédit différé et transfert (étapes 3 et 4) |
| F4 | Zones de danger mobiles qui dégradent l'intégrité | Arbitrage entre canaux, information risquée |
| F5 | L'inventaire comme réserve transportable | Planification à long horizon |
| F6 | Autres individus I3 en concurrence | Modèle d'autrui (hors périmètre actuel) |

Pour mesurer la généralisation :

- **Familles disjointes :** sélection sur certaines familles, validation sur des familles entières tenues à l'écart.
- **Comparateurs :** à opportunité initiale égale (doctrine P2), avec la dépense réelle traitée comme un phénotype.
- **Sondes :** descriptives tant que l'équivalence de coût n'est pas démontrée.
- **Critères :** survie à horizon fixe comme critère principal ; latence de révision, première boisson et dépense cognitive par pas vécu comme critères secondaires, tous préenregistrés.

## Priorités révisées et anti-schémas

L'ordre change sur un point : l'audit de la Competition passe de la 3e place à la fin, puisque les seuils n'ont décidé que 6 fois sur 342.

1. Étape 0 : puissance des tests, effets de l'énergie, individualité, cas P5d.
2. Étape 1 : valeur d'information en détresse prédite, à la place de la curiosité et de la prudence.
3. Étape 2 : décider combien penser.
4. Étape 3 : ruptures et causes latentes, puis effets factorisés.
5. Étape 4 : caractéristiques successeurs.
6. Étape 5 avec la famille F1.
7. Étape 6 : lignée sur plusieurs familles.
8. Audit léger de la Competition et retrait de la prudence.

Ce qu'il ne faut pas faire :

- **Façonnage déguisé :** ajouter un bonus, un seuil ou un poids pour « faire boire » ou « faire manger » l'individu. P5e montre en outre que la plupart des repas non pris étaient cohérents avec ses enjeux.
- **Règles par monde :** des heuristiques ou des options propres à une famille.
- **Oracle :** l'accès aux stocks réels, aux sources non perçues ou aux changements programmés.
- **Réajustement :** retoucher tarifs, gènes ou seuils sur des mondes déjà ouverts, ou ouvrir la réserve P4.
- **Hérédité interdite :** hériter de cartes, de valeurs ou de souvenirs (ADR-0014).
- **Surinterprétation :** lire p=0,125 avec n=4 comme une confirmation, ou l'oracle comme un plafond à coût égal.

## Incertitudes et réserves

Les chiffres et le code sont maintenant vérifiés à la source. Les incertitudes portent sur l'interprétation et sur l'avenir.

- **Statut de la nouvelle lecture de P5e.** Elle est post hoc, faite sur 12 vies de développement et deux génomes. Elle n'a pas de valeur confirmatoire et n'explique pas P5d.
- **Gains attendus.** Ceux des étapes 1 à 6 sont des hypothèses issues d'autres cadres que la physique v2. Chaque étape peut échouer, et l'échec sera conservé.
- **Coût de calcul.** Le coût de la valeur d'information et du métaraisonnement peut annuler leur bénéfice sous v2. C'est précisément ce que les portes doivent trancher.
- **Individualité.** Des empreintes qui divergent (144/144) ne montrent pas encore des décisions stables et différentes face à un même défi.
- **Calendrier.** Le scénario suppose 8 populations ou plus. Au rythme d'environ 1 ms par pas, une porte complète prend plusieurs heures de calcul : à prévoir dans le calendrier, sans toucher au comportement.
