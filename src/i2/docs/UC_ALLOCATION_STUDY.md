# I2 : étude synthétique de l'allocation UC, sans moteur ni naissance

**31 octobre 2026. G2 : étude de logiciel uniquement. Aucun GO G3, L3 ou scientifique.**

Source : `src/i2/modules/uc_allocation_study.py`. Tests :
`tests/i2/test_uc_allocation_study.py`. Référence source verrouillée de
comparaison : `bd4b447423a82bb05300171d22677fffa3464465` (PR #672).
Le prototype de décision en vigueur, `competition_preview.py`, reste **inchangé**.
Cette étude ne mesure ni une vie I2, ni un événement de perception authentifié,
ni une décision physique. Elle ne relit aucune expérience H48 comme si c'était
un apprentissage d'I2.

## Question et hypothèses falsifiables

À plafond UC par capture fixé, un lot indivisible peut refuser d'évaluer un
ensemble de candidats si le budget est inférieur au nombre de possibilités.
Un sous-échantillonnage permet de payer des observations partielles, mais
risque de rater un candidat meilleur et de sous-exposer certains concurrents.
Les politiques sont **témoins analytiques**, pas une présélection de stratégies
pour un organisme I2 :

| Mode | Mécanisme de banc | Statut de décision |
| --- | --- | --- |
| `full_frame` | Évalue tous les candidats, ou aucun | Réplique le contrat UC du prototype Competition #672 |
| `fixed_prefix_control` | Évalue les `k` premiers candidats (témoin négatif d'ordre) | Diagnostic partiel seulement, jamais une commande |
| `rotating_quota` | Évalue une fenêtre circulaire de `k` candidats décalée de `phase*k` dans la liste canonique | Diagnostic partiel seulement, jamais une commande |

Le prefix fixe est *délibérément biaisé* pour révéler qu'une amélioration du
taux d'évaluation n'est pas nécessairement une amélioration de qualité. La
rotation produit une exposition équilibrée sur une fenêtre complète si la liste
des signatures reste stable et si les phases progressent régulièrement ; elle
n'est pas garantie équitable lorsque la perception varie, que le sommeil crée
des trous, ou que l'identité de vie n'est pas authentifiée.

## Méthode figée avant l'interprétation

- Monde **synthétique uniquement**, aucune physiologie et aucun état vivant.
- Comptes de candidats : 3 et 5 ; plafond UC par frame : 0, 1, 2, 3, 5.
- Profils de valeurs entières bornées : croissant, décroissant, égalité
  positive, tout nul, cas adverse. Aucun candidat ne représente une nourriture,
  une ressource favorable, ni un oracle du monde.
- Horizon fixe : deux fois le nombre de candidats, soit 6 ou 10 captures
  synthétiques ; **50 scénarios** appariés, chacun répété pour **3 politiques**.
  Il y a 400 frames de banc par politique, **pas 400 individus**.
- Les fonctions d'allocation reçoivent **uniquement** un `CandidateFrame`, la
  politique, le plafond UC et l'indice expérimental `phase`. Elles n'ont pas
  accès aux valeurs. `advise_on_sample_only` refuse explicitement la présence
  de la valeur d'un candidat non évalué. L'« oracle » complet n'apparaît que
  dans `audit_heldout_after_choice`, **après** la sélection, pour quantifier les
  opportunités non évaluées, et ne constitue aucune connaissance de l'individu.
- La borne UC proposée d'une unité par candidat n'est **pas** un tarif
  authentifié du Scheduler. `uc_scheduled` est une charge de simulation,
  jamais un reçu signé. Les plafonds sont égaux, mais **les consommations
  effectives peuvent différer** entre les modes.
- Toutes les sorties portent `motor_authority=NONE`. Une valeur positive
  évaluée dans un lot partiel reste `PARTIAL_UNVERIFIED` même si elle s'avère
  être la meilleure de la table cachée. Aucun passage vers Action Control.
- Le meilleur de la table complète est défini seulement s'il est unique et
  strictement positif ; les cas nuls et égalités sont exclus du décompte de
  correspondance pour éviter les « succès » fictifs.

## Résultat exact du banc déterministe

| Politique | Plafond UC cumulé | UC programmées | Frames `UNFUNDED` | Avis complets | Diagnostics partiels | Correspondances avec l'optimum unique synthétique |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `full_frame` | 880 | 430 | 290 | 44 | 0 | 44 |
| `fixed_prefix_control` | 880 | 820 | 80 | 44 | 116 | 86 |
| `rotating_quota` | 880 | 820 | 80 | 44 | 120 | 80 |

Les 160 occasions d'optimum unique synthétique constituent une **référence
hors ligne** et non une récompense reçue, un Q appris ou un résultat moteur.
Ces chiffres ne sont pas des estimateurs de probabilité, ne constituent aucune
preuve de supériorité et ne justifient aucune promotion. Le préfixe fixe
obtient ici 86 correspondances, contre 80 pour la rotation, malgré sa mauvaise
couverture : le taux de correspondance dépend du profil construit. Il serait
incorrect de choisir la politique « gagnante » sur ces seules valeurs.

Contrôle ponctuel reproductible, 3 candidats, plafond 2, profil croissant,
6 frames : `full_frame` programme 0 UC et laisse 6 frames sans financement ;
le préfixe fixe utilise 12 UC mais ne voit jamais le troisième candidat ; la
rotation utilise aussi 12 UC et évalue chaque candidat exactement 4 fois,
reconnaissant le meilleur synthétique dans 4/6 frames, sans droit moteur.

## Refus et limites

Le code refuse les budgets booléens/fractionnaires, valeurs hors borne,
plans réécrits, candidats forgés, valeurs cachées injectées, résultats
incomplets, faux statuts et tentative de faire passer un diagnostic pour une
admission motrice. Les tests vérifient également la neutralité vis-à-vis du
marqueur d'intention, et rapprochent le cas `full_frame` du `CompetitionPreview`
actuel avec des ports synthétiques.

Aucune source M11, aucun Scheduler UC, aucun état corporel, aucune connaissance
personnelle, aucun arbitre actif et aucune issue d'action ne sont présents.
Il n'existe aucun registre d'exposition persistant authentifié et aucune
preuve que les candidats non évalués seraient sans danger. La politique de
rotation n'est **pas intégrée** dans Competition. Son efficacité comportementale
et son coût cognitif supplémentaire demeurent inconnus.

## Reproduire sans naissance

```bash
python -m unittest discover -s tests/i2 -p 'test_*.py' -v
PYTHONPATH=src python -m i2.modules.uc_allocation_study --output reports/i2-uc-allocation-synthetic.json
```

La première commande exécute les tests logiciels isolés; la seconde écrit le
jeu complet de **150 lignes de politique×scénario**. Les scripts ne
construisent aucun individu. La CI I2 légère Python 3.11/3.12 doit réussir
sur le SHA de PR avant intégration.

**Décision : ne pas modifier `CompetitionPreview` ou les seuils.** La suite
doit préenregistrer un cadre de confrontation indépendant sous vrai budget
UC, provenance authentifiée et décisions réellement reconsidérées avant toute
vie. G0 archive I1 reste partielle, G1 en revue, G3–G6 non établies.
