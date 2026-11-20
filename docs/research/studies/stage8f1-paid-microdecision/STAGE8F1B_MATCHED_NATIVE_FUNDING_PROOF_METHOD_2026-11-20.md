# Stage8-F1B · parité des coûts natifs sous états de décision identiques

**20 novembre 2026, développement seulement, aucune nouvelle vie ni cohorte.** Le résultat causal Stage8-E2 demeure `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`.

## Question falsifiable

Dans une copie exactement identique du même corps, de la même perception native `World.capture()` et de la même mémoire privée apprise, le candidat F1 et le contrôle F1 « calcul payé, résultat écarté » paient-ils **exactement la même énergie et vigilance** réellement débitées par `World.step`, y compris lorsque la sortie motrice de l'un est supprimée ?

Le contrôleur P1.3 `Mind` reçoit la même situation, mais **n'est pas une comparaison à calcul égal** lorsque sa première allocation de 3 cycles est refusée. L'égalité de dépense n'est requise qu'entre F1 et F1-discard. Il est incorrect de confondre coût de la cognition et coûts corporels distincts après leurs actions.

Base logicielle F1 : `4014a59027cc53bcfb6e7a9c6e6c827e017711b9`. Moteur historique immuable P1.3 : `03faff4b9c194a5288b92e394f6a75cbe62cd095`. Forfait F1 : `CognitiveWork(cycles=1,memory_items=64)` soit **0,0328 énergie et 0,05 vigilance** sous BodyLaws v2.

## Procédure déclarée avant exposition aux nouveaux reçus

Construire huit états synthétiques fixes : (1) sommeil prédit bénéfique par apprentissage personnel, (2) sommeil défavorable, (3) modèle non renseigné, (4) énergie inférieure au microforfait, (5) vigilance inférieure au microforfait, (6) eau observée mais boisson motrice inabordable, (7) nourriture proche de zéro avec décès non secouru, (8) traitement P1.3 financé normalement. Le monde de test est un `WorldSpec` synthétique 3×3 au temps zéro, **pas une vie**. Les observations sont apprises au moyen de la véritable API `EffectsModel.observe`, sans monkeypatch de valeur ou oracle caché.

Pour chaque cas, cloner le même état privé de `Mind` (modèle appris, carte, graines RNG, accumulateurs et mémoire), et le même `World`. Vérifier les SHA des états/captures initiaux, appeler les trois contrôleurs depuis cette condition, puis **exécuter un seul vrai `World.step(action,param,CognitiveWork)`** par bras. Conserver les reçus de `cognitive_accounting` energy/vigilance, les corps avant/après, les morts et les positions. Zéro `run_life`, zéro naissance.

Une seconde réduction indépendante et limitée à la bibliothèque Python standard recalcule les coûts des cycles, mémoire, simulation, replay, puis la physiologie native sur un pas (y compris sommeil réellement non débité au moteur, coût moteur des autres commandes, restauration conditionnelle, décroissance vitale) et vérifie les 24 reçus pour huit triplets, les empreintes et les égalités du financement candidat/discard.

**Règle d'arrêt :** toute entrée privée ou corps dépareillé, débit absent/non réel, recharge non financée, action postmortem, mortalité effacée, réécriture du primaire E2 ou résultat dépendant d'un original G2 non archivé empêche le statut de parité. Les tests synthétiques sont falsifiables, mais ce ne sont pas un test de bénéfice adaptatif.

## Limites de preuve et suite

Les originaux G2 E3C n'archivent pas un instantané complet du `Mind` au premier échec. L'appariement de la mémoire **historiquement vécue** est donc inaccessible avec ces archives ; les huit cas sont synthétiques même si `World`, `Mind` et les factures sont bien natifs. La preuve produit un **reçu de pas physique** et des empreintes d'ingénierie, **pas** une chaîne de vie entière `run_life`/manifest/evidence_head, ni une preuve d'apprentissage post-action, de parité des coûts moteurs ou de causalité génétique.

Tout résultat positif de parité restera `SOFTWARE_ONLY_MATCHED_NATIVE_DECISION_BILL_PARITY_PASS`. Le moteur de référence, les racines E2 et la promotion i3 sont inchangés. Une nouvelle version de preuves et un protocole prospectif distinct seraient nécessaires avant toute cohorte.