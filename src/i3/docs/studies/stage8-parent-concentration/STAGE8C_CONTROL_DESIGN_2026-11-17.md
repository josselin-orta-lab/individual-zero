# i3 Stage8-C : contrôle score-parent indépendant de la concentration parentale

**Statut au 17 novembre 2026 : `ENGINEERING_CONTROL_ONLY / NOT_PREREGISTERED / NO_WORLD / NO_NEW_LIVES`.** Ce document ne constitue ni une autorisation d'admission, ni un résultat d'expérience. Il succède au [Stage8-B conclu négatif sur l'interaction écologique](../stage8-ecology-interaction/STAGE8B_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-17.md), tout en conservant le gain moyen Stage8-A et les négatifs Stage7.

## Question falsifiable

La sélection de parents selon une persistance G1 réellement vécue améliore-t-elle la persistance des descendants G2 **au-delà du seul effet du nombre de parents distincts et de leurs multiplicités de reproduction** ? Stage8-A a obtenu +14,4874 pas en moyenne sur 32 populations, mais 14,00 parents distincts sur 24 tirages dans le bras sélectionné contre 15,25 sous tirage uniforme ; cette différence de concentration est attendue mécaniquement des poids de rang. Stage8-B n'a pas mis en évidence d'interaction parmi `stable`, `depletion` et `pulse` (p = 0,6578). **Ni l'un ni l'autre n'identifie le mécanisme génétique.**

## Architecture candidate des trois bras

1. **S, score lié** : sélection des parents pondérée par leur rang de persistance corporelle G0/G1 (24…1), suivie des mutations normales, comme dans Stage8-A.
2. **M, multiplicité appariée, identité brouillée** : pour chaque population et génération G1/G2, prendre les **24 indices de parents** retenus dans S. Appliquer aux indices **une bijection aléatoire uniforme sur les 24 slots**, générée avec une nouvelle clé indépendante du score. Réaliser ces tirages dans **le propre ensemble de génomes parents du bras M**, jamais dans celui de S. Les effectifs par parent sont permutés : **même nombre exact de parents distincts et même multiensemble de multiplicités** que S, sans associer délibérément le rang vécu du parent M à son nombre d'enfants.
3. **U, uniforme** : sélectionner les parents uniformément avec remise, indépendamment de leur score, comme témoin de référence.

Les trois bras partagent G0, les mêmes six occasions écologiques F0 par génération, le même moteur P1.3 funded-v2, les mêmes coûts corporels/cognitifs, la mutation génomique v4, l'absence de mémoire héritée, la possibilité de mourir sans réanimation et **aucune action motrice imposée**. G1 et G2 sont des lignées distinctes. Les mondes G2 doivent être réservés avant G0 et jamais utilisés pour classer les parents.

## Petit composant logiciel livré, sans naissance

`src/i3/lab/stage8c_parent_multiplicity_control.py` implémente une permutation Fisher–Yates par HMAC-SHA256, avec tirage sans biais de modulo, domaine distinct par population et génération et **clé de 32 octets à préallouer par une future étude**. `matched_parent_draws` reçoit seulement les 24 indices, population, génération et clé ; il n'accède ni aux scores, ni au moteur, ni au World. Il refuse les indices malformés et conserve exactement les multiplicités. Les tests de `tests/i3/test_stage8c_parent_multiplicity_control.py` exercent déterminisme, domaines indépendants, deux cas extrêmes, erreurs de coordonnées et API sans scores ; ce sont des **tests de logiciel**, pas des résultats biologiques.

## Estimand et falsificateur proposés, non figés

Sur de **nouvelles populations**, comparer principalement la moyenne des contrastes G2 `D[p] = mean_steps(S,p) − mean_steps(M,p)` avec unité d'inférence **population**, en tenant les Worlds appariés. Un résultat compatible avec zéro ou négatif ne permettrait pas d'attribuer le gain historique au couplage rang-identité. La comparaison S−U, puis M−U, les 32 ou autres profils individuels, la survie censurée à 400, le nombre de parents distincts **et la diversité réelle des génomes** seront des secondaires explicitement séparés. Aucun signe, intervalle ou seuil n'est décidé a posteriori.

**Limite majeure** : la bijection égalise **les multiplicités des parents**, **pas** les distances génomiques ni l'hétérozygotie réelle ; une permutation finie peut, par hasard, conserver une corrélation avec le score. Il faudra reporter les mesures de diversité des génomes, la conservation des mutations, les ancêtres et la compatibilité des distributions de score. Même un effet S−M positif ne nommerait pas de gène causal ni ne prouverait une adaptabilité hors F0. Une étude complémentaire factorielle génétique pourrait être requise.

## Conditions bloquantes avant une éventuelle cohorte

- Définir **avant toute exposition** l'effectif, la puissance attendue et le seuil unique du test S−M à partir d'un calcul préenregistré et non d'une recherche de cohorte favorable ; préciser les contrôles M−U et S−U et les corrections éventuelles de multiplicité.
- Prouver par tests de construction **sur allocations fictives** que les trois bras ont le même budget et les mêmes opportunités World, que S et M ont **exactement** le même multiensemble d'occupation parentale dans chaque population/génération, que le score est inaccessible au choix M, et que les mutations/neurodécisions ne sont pas altérées.
- Publier un protocole **nouveau** avec SHA de code, méthode, génération, nouvelles graines et clés HMAC, 192 ou davantage de World G2 réservés, nommage des archives, empreintes source avant naissance et refus de toute relance post-exposition.
- Exiger deux répétitions techniques intégrales scellées Python 3.11 et 3.12 **avant** la première cohorte scientifique, puis audit gzip indépendant et publication des effets défavorables. Le simple succès des tests purs actuels **n'est pas** cette validation.

ADR-0022 autorise la recherche prospective **si** ces préconditions propres à l'étude sont instanciées, mais aucune allocation scientifique Stage8-C, aucun témoin G/S/R et aucune source autorisée n'existent dans cette PR. I1 reste runtime actif, I3 n'est pas promu ; Stage2.1 scientifique `NOT_ISSUED/HOLD_NO_VERDICT`.
