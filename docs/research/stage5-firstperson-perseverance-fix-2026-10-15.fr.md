# Stage 5 : correction du témoin de persévérance, sans perception omnisciente

**15 octobre 2026.** Branche fille de [PR #205](https://github.com/josselin-orta-lab/individual-zero/pull/205) (Stage4 perception locale) ; réponse limitée au reliquat Stage5 de [l'issue #203](https://github.com/josselin-orta-lab/individual-zero/issues/203). **Statut initial : en attente des résultats CI sur la tête**, ne pas assimiler ce correctif de banc d'essai à une validation scientifique de Stage5.

## Reproduction originelle (contrôle négatif)

[L'audit de base run #38778262250](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38778262250) a établi en Python 3.11 et 3.12 que la batterie Stage5 d'origine échoue sur `test_perseverance_uses_explicit_forced_failure_mechanism` : `no_tested_action_observed` au lieu de `scored`/`right_censored`. L'échantillon original naît en (2,2), avec l'eau en (4,2), à distance Manhattan **2** ; le capteur de l'individu ne perçoit qu'à distance 1. Faute d'objectif d'eau géographiquement accessible, il ne choisit aucune commande `se_deplacer`. La séquence externe `set_action_failure_schedule` ne crée **jamais** d'action à la place d'I0 : elle n'intervient que si I0 l'a réellement choisie. Un score de persévérance est donc inobservable, et le statut `no_tested_action_observed` est **correct** pour ce témoin négatif.

La réparation consiste à **créer une véritable occasion perceptive**, et non à relâcher la frontière Stage3, injecter une option, forcer un mouvement ou traiter l'absence d'acte comme de la persévérance.

## Modification minimale

- La fixture de compatibilité `build_stage5_reference_runtime` accepte un paramètre **facultatif** `observed_water_source_position` appliqué à la **disposition physique de naissance**. La valeur par défaut ne change **pas** : la source historique en (4,2) reste invisible.
- Quand le paramètre est fourni, il ne peut désigner qu'une source à distance Manhattan au plus 1 de la position physique initiale. Toute demande de « voir » l'eau en (4,2) doit lever `ValueError`. La modification de disposition est externe à la cognition et n'intervient qu'avant l'instanciation du Stage5 à tester.
- Le seul test positif de persévérance utilise `Position(3,2)`, physiquement voisine, effectivement déclarée `water_source=True` par `WorldBody.capture_local`. **La primitive doit être choisie par Stage5**, puis la politique d'échec de commande déjà préenregistrée `[True,True,False]` produit un reçu réel. Le score `scored` ou `right_censored` n'est accepté que si le nombre de `forced_failures_observed` est au moins 1, c'est-à-dire une transition effectivement vécue sous scénario d'échec.
- Deux témoins nouveaux garantissent qu'une eau distant reste **invisible et non notée** (`no_tested_action_observed`, aucune persévérance fabriquée) et qu'on ne peut utiliser le paramètre visible pour franchir la portée perceptive.
- Le protocole protège les invariants de la PR #205 (Stage4, choix, comparateur et mortalité de compatibilité), Stage9/DC-05 et les tests Stage3. Aucune modification de `src/i0`, d'une commande choisie par le banc, du journal M11, des UC, de l'Oracle/Bench, ni de la norme `docs/architecture/reference/en/mvp-specification-v1.3.1.md`.

## Frontière d'interprétation et décision d'intégration

Ce changement n'est **pas** une modification du comportement propre de Stage5 : il restaure la validité d'un test de persévérance dans une **situation d'observation licite**. Même si le test est vert, le nombre de tentatives sous échec forcé ne démontre pas une disposition universelle de persévérance ni une propriété scientifique des UC. Le score reste une observation de batterie sur copie jetable, sans rétroinjection vers son parent.

**Avant fusion**, contrôler la tête exacte de PR #205, puis les tests Stage5, Stage4, Stage9, Stage3 sous Python 3.11 et 3.12, et les non-régressions après chaque fusion. Si la suite globale présente des défauts de base supplémentaires, les séparer des effets de ce correctif. Aucune fusion automatique dans ce travail.
