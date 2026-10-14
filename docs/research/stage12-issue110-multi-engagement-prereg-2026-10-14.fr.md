# Stage12 / Issue #110 : préenregistrement d'une campagne alimentaire multi-engagements

Date : 14 octobre 2026. Branche : `feature/stage12-issue110-spatial-agency-option-a-20261014`. Ce protocole est figé **avant toute implémentation de variante ou exécution** et reste exploratoire, sans transfert d'informations de l'évaluateur vers I0.

## Question expérimentale

Est-ce que la rareté des couples vécus est une conséquence générale du contrat de perception/objectif ou une propriété de l'environnement alimentaire de référence (deux baies et gain de +30) ? La campagne précédente a observé 11 engagements, 7 couples admis, 4 consommés dans 4 vies × 16 pas ; 2 expirations sur sommeil et 1 horizon tronqué. Toute intervention après naissance pour rediriger une commande, modifier les préférences ou forcer un objectif est interdite.

## Mondes fixés avant naissance

Conserver l'architecture et les règles de décision, les politiques et le coût UC, la consolidation désactivée dans l'expérience précédente, la recette Equipment apprise par de vraies transitions **hors I0 avant naissance**, les coordonnées initiales et la ressource alimentaire (3,1), le monde 32×32, la mécanique du sommeil et les seuils du détecteur.

Créer trois **profils physiques expérimentaux pré-naissance** (paramètres déjà autorisés dans `WorldPhysicsConfig` et `WorldLayout`; aucune modification de v1.3.1) :

| Profil | Nourriture initiale | Gain de `berry_a` | Décroissance alimentaire / pas | Nombre de baies sur (3,1) |
|---|---:|---:|---:|---:|
| sustained | 24.0 | 6.0 | 0.7 | 12 |
| episodic | 33.0 | 12.0 | 1.6 | 8 |
| marginal | 22.0 | 3.0 | 1.3 | 12 |

Chaque profil a deux versions :
- contrôle : aucune intervention extérieure ;
- A2 : obstacle sur (3,1) au pas 2, phase `after_admission`, puis retrait au pas 4 phase `before_step`, sans dépendance à la commande ou au but choisi.

**Six vies indépendantes × au plus 36 vrais pas physiques = 216 pas maximum.** Aucun rééchantillonnage conditionnel au résultat. Le nombre de pas est borné pour éviter de prolonger un système qui ne renouvelle pas ses objectifs. Une vie qui meurt, se bloque ou échoue au contrôle est enregistrée négative. Tester Python 3.11 et 3.12 **sur les mêmes expériences** sans compter deux fois les sujets.

## Mesures préalables

Pour chaque vie et pas, conservation JSONL + WAL et SHA, commandes véritablement admises, intentions originales, jugements `self/world/unknown/unavailable`, suivis d'objectif, couples admis/consommés/expirés/pending, diagnostics payés, épisodes de sommeil et temps exact des interventions. Audits indépendants `audit_stage12_goal_progress`, `audit_stage12_first_person_agency`, `audit_stage12_attribution_pairs`, `audit_stage12_a2_causal_link` pour les causes extérieures A2, plus audit du WAL ; tout résultat non auditable devient `FAIL` et n'est pas inclus dans les estimations.

Critère de couverture : au moins **deux `success` et deux `failure` appliqués au détecteur** dans la même fenêtre de 12 observations éveillées, avec jugements subjectifs indépendants d'un diagnostic oracle. Ne pas additionner les vies. Comparer le nombre d'engagements par pas réellement éveillé et la répartition des pertes par sommeil. Une alerte `self_serving_pattern` n'est que le nom d'un contraste conditionnel descriptif, pas la preuve d'un biais causatif.

Si aucun profil n'atteint 2+2, conclure explicitement à une **non-évaluabilité sous les scénarios testés** et faire porter les travaux suivants sur la diversité des buts / la dynamique de sommeil, sans changer leurs règles sans justification et arbitrage opérateur. Les résultats de ces six vies sont exploratoires, pas un test de confirmation hors échantillon. Stage12, PR #155 et issue #110 conservent leurs statuts non reçus.
