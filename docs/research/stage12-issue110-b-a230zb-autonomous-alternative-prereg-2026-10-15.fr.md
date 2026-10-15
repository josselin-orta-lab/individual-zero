# A2.30-ZB : préenregistrement, opportunité alimentaire alternative et véritables vies I0 autonomes

**15 octobre 2026 : enregistré AVANT code ZB, avant toute nouvelle naissance et avant les résultats.** Nouvelle branche de recherche construite au-dessus de **#195 / `d4c3d286b5eafeba335483762d05fac6bf21137c`**. Les résultats physiques Z/Z(I/R) et ZA sont déjà connus : 168 mondes de laboratoire, 244 transitions, 40 réussites alimentaires parmi 80 ingestions B, 20 décès, et 80/80 recherches Stage6 shadow à modèle incomplet. Ces mondes **n'étaient pas des individus I0**. Ne pas les recompter comme naissances ZB.

## Problème falsifiable : l'opportunité physique devient-elle un acte autonome ?

Le banc Z a montré qu'une `berry_b` accessible peut nourrir certains corps, mais pas que l'individu choisit de la collecter ou de la manger. Une perception alimentaire n'est ni un plan Stage6, ni un succès d'objectif, ni une attribution causale subjective justifiée. La présente campagne **fait réellement naître de nouveaux I0 autonomes**. Aucun de leurs actes n'est imposé par le banc.

- **ZB1, effet d'accessibilité :** une `berry_b` réellement visible sur la case initiale, ou visible à l'est, peut modifier les propositions ou commandes `collecter/manger`, **comparée à un contrôle B absente**. Le résultat peut être nul; ne pas remplacer cet échec par des commandes forcées.
- **ZB2, limite de couverture :** le modèle exact prénatal A2.30-J historique, entraîné sur des transitions physiques de `berry_a` seulement, n'a **aucune transition B présumée connue**. Mesurer les vrais diagnostics Stage6, et distinguer un éventuel mouvement/repas spontané d'un plan alimentaire Stage6 attesté et physiquement réalisé.
- **ZB3, indiscernabilité des effets cachés :** à percepts identiques et sans interaction B, la variante bénigne et la variante physiquement mortelle de B ne peuvent être distinguées à partir d'une observation accessible. Toute divergence de commandes avant exposition doit être publiée et rend **non interprétable comme causalité simple** le contraste correspondant. Les identifiants de naissance resteront obligatoirement distincts.
- **ZB4, sujet/Oracle/sûreté :** suivre les vrais reçus UC, journaux WAL, commandes physiques, issue terminale et jugements B proximaux/distaux. Aucun décès n'est réactivé; aucune observation postmortem n'est présentée comme vécue; aucun jugement `self` distal n'est crédité comme responsabilité objective sans preuve causale indépendante.

## Cohorte entièrement fixée avant le code

**Deux profils physiologiques préexistants :** `restored` (nourriture initiale 35, gain A=30, décroissance A=0) et `sustained` (initiale 24, gain A=6, décroissance A=0.7). Le reste de la physique Stage11/12 normative et de la faim propre au profil reste intact.

**Trois layouts B, identiques sauf présence/position B :**
1. `B_NONE` : aucune `berry_b`, témoin sans opportunité B; garder `berry_a` originelle à (3,1).
2. `B_LOCAL` : deux `berry_b` sur **la position initiale propre à WorldPhysicsConfig**, visibles localement dès la première capture; conserver A.
3. `B_EAST` : deux `berry_b` sur **la cellule immédiatement à l'est**, visible dès la première capture et physiquement passable; conserver A.

**Deux effets corporels cachés de B** dans **chaque layout**, même si B est absente, afin d'obtenir des témoins physiquement jumelés :
- `benign`: `food_gain=30`, `integrity_delta=0`.
- `toxic_lethal`: `food_gain=30`, `integrity_delta=-100` ; **une ingestion peut conduire à un décès terminal immédiat**.

**Une vie physique I0 nouvellement née pour chaque** combinaison de 2 profils ×3 layouts ×2 effets = **12 naissances uniques**, identités `i0:stage12:b:a230zb:{profile}:{layout}:{variant}`. Horizon strict : **32 pas autonomes maximum par vie**, **384 vrais pas I0 au maximum**, avec arrêt irréversible de toute vie devenue terminale. Chaque monde et son WAL restent indépendants. Le statut `experiment_stopped` à la borne d'observation **n'est pas** un décès biologique. Le modèle est figé **avant chaque naissance** et doit conserver le corpus exact prénatal `berry_a` original pour le profil; aucune nouvelle transition B ni hypothèse de sécurité ne lui est injectée.

**Variable manipulée entre vies :** uniquement la position visible de B et l'effet physique de B caché dans l'environnement; les profils et paramètres cognitifs (Stage12 B-born dual-scope, GA-06 legacy désactivé, Stage6 profondeur=3 avec recherche progressive, `extrinsic_gain=1.6`, sommeil/consolidation M11 inchangés) restent conformes au fixture A2.28/J. La physique n'est modifiée que **dans les arguments de naissance `Stage12Runtime`**, jamais après la naissance; aucune injection `set_body`, `safe` ou décision opérateur pendant la vie.

## Mesures et score strictement prospectif

Pour chaque identité :
- PAS appliqués, statut de mortalité, fermeture P-48 du journal causal et concordance **WAL durable**, hash final du journal, nombre de commandes, `collecter(B)` et `manger(B)` réellement exécutées, coordonnées B perceptibles avant acte, gains alimentaires corporels et intégrité; les **ingestions physiquement confirmées** doivent venir de l'audit P-48, pas de la seule proposition Stage6.
- Toutes les recherches Stage6 et `root_available_edges/root_unavailable_edges`, `plan_found/partial_progress/incomplete_model`, nombre de propositions de plans et **sous-ensemble de commandes B effectivement exécutées avec un motif causal attesté**; un plan proposé mais refusé n'est jamais une réussite.
- Reçus de motivation individuelle, actions Stage12 B-born, jugements `subjective_responsibility` proximaux et distaux, refus UC réellement enregistrés. Un nombre UC n'est publié que s'il provient du WAL vécu.
- **Paires contrastées** par profil×layout, bénin vs mortel : égalité/discordance des captures accessibles au premier pas, parité des commandes jusqu'à la première ingestion B, première divergence; toute comparaison post-exposition ne sert pas de prédiction t0. Déclarer explicitement les différences de personnalité/graines éventuelles liées à l'identité et s'abstenir d'une attribution causale globale.
- **Contrôles négatifs** : B inexistante ne doit jamais être rendue visible ou ingérée; B locale/à l'est doit apparaître dans la seule observation autorisée correspondante; Equipment prénatal doit refuser `manger(B)` à l'état de naissance; les éventuelles morts n'autorisent aucun pas supplémentaire ni observation cognitive postterminale.

**Un résultat positif ZB1** requiert un écart d'actions B **vécues et physiquement attestées** dans au moins une paire de layouts (l'absence de cet écart signifie ZB1 non soutenue). **ZB2 réussit cognitivement** seulement si une ingestion/proposition alimentaire B provient effectivement du Stage6 et se ferme comme acte vécu sans contamination causale; sinon la compétence Stage6 reste **NOT ESTABLISHED**. **ZB3** doit au minimum observer les captures initiales identiques entre variants; un effet du fruit que l'individu n'a pas rencontré ne peut pas être crédité comme ressenti. **ZB4** impose zéro restauration mortelle, pas de faux `self`, et vérification indépendante des journaux.

Deux CI Python 3.11/3.12 répéteront les **mêmes 12 configurations déterministes**, jamais 24 naissances scientifiques différentes. Toute nouvelle naissance de ZB doit avoir sa propre identité et son propre support WAL. Ne pas agréger le Z physique et le ZB vivant en une cohorte d'observation homogène. Les quelques centaines de pas ici sont un test de développement, pas une preuve scientifique universelle ni une validation opérateur.

**Statut pré-essai :** aucune vie ZB n'a encore été créée ; hypothèses et métriques figées, tous les résultats ouverts. **A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, PR nouvelle DRAFT. Aucune modification de `src/i0`, du WAL M11, de Stage9/DC-05 ni de la spécification v1.3.1.**
