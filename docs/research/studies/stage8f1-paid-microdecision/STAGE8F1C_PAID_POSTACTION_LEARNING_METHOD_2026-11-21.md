# Stage8-F1C · apprentissage post-action payé et conservé, sans vie

**21 novembre 2026 · protocole de développement synthétique, pas un protocole scientifique de survie.** Base de développement `dd0d36a61cfce44c38efc2846a8c25f978da7266`. Le verdict F1B reste `SOFTWARE_ONLY_MATCHED_NATIVE_DECISION_BILL_PARITY_PASS`, avec son JSON original SHA256 `9e645b8aed70c5cf68047c2cd25ddd50d4d9a5441a147d9c6a11531aec91c65a`. Le primaire causal Stage8-E2 reste **négatif / CLOSED_NO_RETRY**.

## Question falsifiable

Après une décision volontaire F1 et sa conséquence réelle `World.step`, l'individu paie-t-il, **avant** l'actualisation de ses états appris, l'énergie **et** la vigilance que `Mind.prepare_learning` lui a allouées ? À action, corps, perception, mémoire, facture et conséquences physiques identiques, la mise à jour effectivement calculée est-elle présente **uniquement** dans le bras autorisé à la conserver ? Le modèle des effets reflète-t-il les changements corporels *réellement mesurés*, une fois inclus le débit d'apprentissage ?

Échec si débit gratuit, paiement fantôme, aucune modification de modèle/TD, copie mentale non appariée, effet contrefactuel fabriqué, observation de la physique cachée par l'individu, apprentissage après mort, divergence de répétition ou vérification indépendante contradictoire.

## Conditions fixées avant les nouveaux reçus

1. **Source personnelle synthétique :** reprendre le seul cas `learned_beneficial_sleep` de F1B, `WorldSpec` 3×3 et `EffectsModel.observe(("dormir",), ...)` pour l'état appris initial. C'est un apprentissage *préinstallé pour le test*, **pas** la reconstitution d'une mémoire G2. Clone complète du même `PaidMicrodecisionMind` (état mutable, RNG, cartes, valeurs et effets), même `World.capture`, même corps.
2. **Deux copies physiques réellement appariées :** toutes deux exécutent la décision volontaire F1 `dormir`, le même `World.step` natif et la chaîne `observe_outcome -> prepare_learning -> pay_cognition -> learn_from_outcome`. Le premier bras conserve la mise à jour ; le second **exécute le vrai calcul sur une copie détachée** et en écarte seulement la rétention. Aucune dérogation à la facturation.
3. **Contrôle létal :** reprendre le cas F1B de nourriture terminale, exécuter l'unique pas natif sans sauvetage, refuser la cognition postmortem. Pas d'apprentissage ni de réparation des ressources.
4. **Preuves de première personne et physique :** conserver des instantanés typés **complets mais observateurs** de l'état privé `Mind` aux frontières décision/apprentissage, avec SHA256 (pas de `repr` ambigu). Conserver les factures natives des deux monnaies, corps avant/après, `EffectsModel`, valeurs TD, mémoire de rejeu et mort. Les témoins complets ne sont **pas** un format de restauration natif authentifié ni une nouvelle chaîne de vie entière.
5. **Reproductibilité et contre-audit :** deux processus Python 3.11 indépendants génèrent chacun le même jeu de 3 `World.step` synthétiques ; comparer **octet pour octet** les deux JSON originaux. Un auditeur séparé Python 3.12, **standard library only** sans import `World`/`Mind`/générateur, recalcule les factures, la physique des trois pas, le débit post-action, la mise à jour arithmétique des moyennes des effets personnels et les empreintes/égalités des états complets.

Le paquet d'apprentissage attendu sur le cas synthétique initial est `CognitiveWork(cycles=2, simulated_steps=32, memory_items=3, replays=1)`, soit **0,1096 énergie** et **0,174 vigilance**, mais le verdict ne repose **jamais** sur ce calcul prévu : il doit être constaté dans les débits de `World.pay_cognition`, puis réétabli indépendamment.

## Frontières et règle de publication

Le contrôle F1-discard de Stage8-F1B reste le seul contrôle à **calcul de décision égal**. Ici la comparaison pertinente est F1 *apprentissage conservé* / F1 *apprentissage calculé puis écarté*, avec **la même action** et donc les mêmes coûts moteurs. Comparer une action réparatrice à un témoin physiquement inactif comme si leurs ressources post-action étaient égales serait incorrect.

**Statut initial : en attente de CI et du contre-audit des nouveaux reçus.** En cas de PASS, n'attribuer que `SOFTWARE_ONLY_NATIVE_POSTACTION_PAID_LEARNING_RETENTION_PASS`, avec IDs GitHub, SHA exacts et limites. Jamais : bénéfice de survie, équivalence à une mémoire G2 réellement vécue, nécessité d'une décision future modifiée, causalité gamma, génération complète, ou admission F1 au runtime. Aucun `run_life`, aucune naissance, aucune cohorte. Les artefacts CI ne sont conservés que 90 jours : conservation durable distincte nécessaire.
