# Individual Zero / Stage12 / #110 : A2.24, provenance sensorielle et indistinguabilité épistémique

**Préenregistrement le 15 octobre 2026, avant toute instrumentation A2.24.** Base `main 2599e4152a8bde38dd5cbb73bf7ada94b443edf1`. Les campagnes A2.18–A2.23 sont intégrées. Référence normative : `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, **inchangée**. Issue #110 ouverte, Stage12 PARTIAL.

## Question et modèle de menace

A2.23b a prouvé la durabilité d'un reçu `stage12-first-person-cue-v1` sous M11 lorsqu'I0 est né avec l'agence activée, mais a aussi établi que quatre sorties de Perception falsifiées *avant* journalisation étaient durablement committées. A2.24 décompose cette limite en trois contrats différents :

1. **Fidélité de projection** : `SymbolicPerception.capture` a-t-elle fidèlement représenté le `LocalWorldState` remis à son entrée ?
2. **Provenance de l'entrée** : ce `LocalWorldState` provient-il d'un producteur de données locales observé séparément ?
3. **Vérité physique** : le producteur observé représente-t-il réellement le corps et le monde, même si les deux premiers contrats concordent ?

La garde externe est du **code de laboratoire** injecté uniquement dans le processus d'évaluation, **pas** un nouveau propriétaire, pas un capteur de production, pas une vérité perceptive ajoutée à I0. Le journal M11 conserve ce qu'I0 a effectivement reçu, vrai ou faux. Un hash, un accusé de réception et deux témoins contrôlés par le même attaquant ne certifient pas la vérité du monde.

## Matrice physique préfixée

**Quatre positions de naissance** `151 -> (8,8)`, `152 -> (12,8)`, `153 -> (16,8)`, `154 -> (20,8)`, avec eau à deux cellules à l'est ; physique normative 32×32 de la fixture Stage12. Chaque condition crée un **nouvel individu Stage12 autonome et mortel** avec `subjective_goal_agency=True`, `m11_sqlite_custody=True`, aucune seconde WAL, identité unique, exactement **une génération vivante committée par M11**. Aucune commande ne vient du banc, aucun `WorldBody.apply` fictif. Quatre seeds sont des **positions déterministes**, pas quatre simulations comportementales aléatoires indépendantes.

Cinq conditions prospectives pour chaque position, soit **20 naissances/20 transitions physiques committées** :

| Condition | Corps physique initial | Entrée locale livrée à Perception | Sortie de Perception | Témoin-source *déclaré* |
| --- | --- | --- | --- | --- |
| `honest_base` | x | x | x | x |
| `honest_twin` | x+1 (vraie autre naissance) | x+1 | x+1 | x+1 |
| `output_spoof` | x | x | **x+1** | x |
| `input_spoof` | x | **x+1** | x+1 | x |
| `joint_spoof` | x | **x+1** | x+1 | **x+1 falsifié** |

La translation de x s'applique **à toutes les cellules adjacentes visibles** et entités visibles, et non seulement au centre, pour éviter une incohérence triviale de géométrie. Les champs corporels, eau locale, ressources et inventaire restent compatibles avec un vrai monde homologue décalé de +1 (même scène relative, source d'eau elle aussi translatée dans `honest_twin`). L'altération est installée *après la naissance* par un patch de laboratoire sur `WorldBody.capture_local` ou `SymbolicPerception.capture`. **Dans `joint_spoof`, l'attaquant falsifie aussi le reçu-source contrôlé par le laboratoire**, représentant une compromission commune de la garde et du producteur. L'évaluateur garde séparément les positions physiques de naissance ; I0 ne les reçoit pas.

## Prédictions et garde-fous fixés

- **T1 vie/M11 :** 20/20 naissances indépendantes et vraies exécutions `M11TransactionalMortal.run_step`, 20/20 générations 1 committées, 20 reçus `stage12-first-person-cue-v1` issus de Stage3, inventaire et quatre voisins, identité de tentative et ordre avant `step_closed`. Aucun événement physique caché / Oracle dans le reçu de première personne.
- **T2 fidélité de projection :** en audit extérieur, comparaison complète entre la capture issue de Perception et la projection calculée **sur l'entrée réellement reçue** : **4/4** `output_spoof` incompatibles, **16/16** autres compatibles.
- **T3 provenance de l'entrée :** comparaison entre l'entrée reçue et le témoin-source annoncé : **4/4** `input_spoof` incompatibles, **16/16** autres compatibles, y compris **4/4 `joint_spoof` faussement rassurants**.
- **T4 exactitude du monde :** l'évaluateur indépendant connaissant les **positions physiques effectivement choisies à la naissance** confirme les 12 captations physiquement fausses (`output_spoof`, `input_spoof`, `joint_spoof`), 8 captations correctes (`honest_base`, `honest_twin`). Dans la condition conjointe, les deux premières vérifications passent malgré une sensation physiquement fausse. **Aucun taux de « détection parfaite » ne doit être annoncé sans cette restriction.**
- **T5 indistinguabilité :** pour chaque seed, les **captures de première personne complètes** retournées par Perception *et* la projection du reçu journalisé sont identiques entre `honest_twin`, `output_spoof`, `input_spoof`, `joint_spoof`. L'identité de vie, les refs journal/attempt et les effets physiques ne sont pas comparés puisqu'ils ne font pas partie d'une même capture accessible et peuvent différer. Si l'égalité échoue, T5 = FAIL et l'expérience n'est pas « réajustée » après coup.
- **T6 reproductibilité :** matrice Python 3.11 et 3.12 sur **les mêmes** 20 naissances, sortie et preuves par monde ; aucun 600 pas et aucune calibration GA-06.
- **T7 sécurité :** zéro changement de runtime I0, Stage3/Stage10/Stage12, WorldBody, propriétaire journal/WAL M11, UC, mortalité, Oracle, Stage9/DC-05, détecteur `2+2/12`, spécification v1.3.1. Ne pas envoyer l'attestation du banc comme vérité à I0 ni annoncer de responsabilité alimentaire distale.

## Réfutabilité et interprétation

Une attestation au point d'entrée de Perception peut révéler certaines altérations **aval** ; une attestation du producteur local révèle certaines altérations **entre producteur et entrée**. **Aucune des deux, sans racine physique indépendante protégée, ne peut réfuter une falsification commune de toute la provenance**. Le sens exact de la preuve est : « ce qui a été remis à Perception et durablement journalisé », pas « ce qui s'est forcément produit ».

Même avec T1–T7 PASS, A2.24 n'implémente **aucune correction d'agence passée**, aucune authentification matérielle de capteur, aucune UC de révision, aucune responsabilité alimentaire, ni généralisation à la vie autonome de 600 pas. Stage12 demeure **PARTIAL** et #110 OPEN. Avant une nouvelle politique, l'opérateur doit arbitrer explicitement **agence proximale de l'action vs responsabilité distale du résultat**, indépendamment de la chaîne de possession des captures.
