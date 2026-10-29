# #305 — Audit de crédit TD différé dans la vie naturelle Oasis B, pas 19–24

**Préenregistré le 28 octobre 2026, avant instrumentation**, à partir de `main` `e5e8bdb8c4d94dd5e9d3becd2df63585ed000ad5`. Reprendre le **même** test naturel M11 v4 `tests/i1/test_i1_natural_postcollect_followthrough_305.py` intégré par #604 : une seule naissance déterministe canonique `i1:304:heldout:oasis:b`, 24 pas maximum, sans prolongation, sans intervention, sans deuxième individu ni coûts UC supplémentaires. Le journal M11 a déjà validé les actes libres `manger` t19, `collecter` t20, `manger` t21, `dormir` t22–24. Ce résultat moteur sert de **condition de provenance**, non de nouvelle réplication statistique.

## Question scientifique indépendante du contraste #605

Le mécanisme `LinearTDValues.update_segment` utilise le retour physiologique différé `return_g`, un bootstrap `q_next` pondéré par `beta`, et des traces d'éligibilité `lambda_e`. Une récompense issue de `manger` au pas 21 peut alors modifier, lors d'une publication TD ultérieure, les poids de la signature `collecter` précédemment active. **Ce que l'on veut prouver est d'abord une transmission interne de crédit avec provenance, pas une amélioration causale du choix libre**.

Hypothèse H1 : après `collecter` t20 puis `manger` t21, une publication TD portant sur `previous_signature=manger` peut mettre à jour aussi `collecter` via une trace persistante ; le delta des poids de `collecter` doit être égal, composante par composante, à `eta * update.delta * eligibility_after` suivant la formule normative. H0 : aucune telle publication, ou trace nulle, delta nul/non positif, ou attribution impossible; publier un résultat négatif/indéterminé sans modifier `lambda_e` ou les actions.

## Instrumentation d'opérateur, exclusivement en lecture après expérience

1. Dans la boucle M11 *déjà présente* de #604, capturer `q_active.export_causal_state()` **avant et après** chacun des pas 19–24. Ne pas appeler `learned_value` ni modifier l'état propriétaire. Résumer uniquement les vecteurs de poids, traces et comptes de mises à jour des signatures `i1:affordance:collecter:target=berry_a` et `i1:affordance:manger:target=berry_a`, ainsi que le segment pending. Aucun état n'est réinjecté.
2. Après audit froid SQLite M11 (génération/head/status/pending transaction), lire les seuls événements réels `td_update_published` sur 19–24, avec `(step,cycle,previous_signature,next_signature,segment_length,return_g,q_previous,q_next,delta,updated_signatures)`. Conserver également les commandes appliquées et corps/inventaire avant/après.
3. Calculer **en dehors** du moteur, depuis les snapshots corporels et les `weights/setpoints` déjà fixés à la naissance, le reward physiologique `before_deviation - after_deviation` de t20 (collecte) et t21 (ingestion). Cela ne consulte aucun Q et n'injecte aucun événement.
4. Pour la première publication TD `previous_signature=manger` à t22 ou après la consommation t21, vérifier si `collecter` figure dans `updated_signatures`, si sa trace était non nulle et si son poids change exactement selon la formule `eta * delta * eligibility_after` (tolérance numérique 1e-9). Distinguer explicitement **le moment du reward vécu** (t21) du **moment de publication de l'update** (t22 ou plus tard). Si la publication a lieu sous un autre pas, rapporter ce pas exact; ne pas déplacer la chronologie pour favoriser H1.
5. Contrôler qu'aucune action, compte UC, simulation, signature ou configuration moteur n'est modifiée par cette capture. Les sorties existantes `I1_305_POSTCOLLECT_FOLLOWTHROUGH` et leurs verdicts sont conservés; nouveau sous-rapport `td_delayed_credit_305` exclusivement descriptif.

## Verdicts préenregistrés

- `LINKED_ELIGIBILITY_UPDATE_OBSERVED` si et seulement si une publication après ingestion t21, dont la signature précédente est `manger`, met à jour `collecter`, avec trace non nulle et égalité numérique des deltas poids/éligibilité. **C'est L2 mécanisme TD audité, pas L3 choix adaptatif.**
- `NO_LINKED_ELIGIBILITY_UPDATE` si une publication réelle est disponible mais n'actualise pas `collecter` ou n'a pas de trace.
- `NOT_EXPOSED` si aucune publication post-ingestion appariée n'existe dans la fenêtre (par exemple, sommeil reflex).
- `MECHANISM_MISMATCH` : trace, poids, identités ou journal incohérents; le test doit échouer et aucun verdict scientifique positif ne peut être publié.

Une publication TD positive peut augmenter une valeur sans avoir causé la décision qui l'a précédée. Même avec une vraie consommation t21 et un lien d'éligibilité t22, **la causalité de la recollecte t20, le bénéfice différé comparé à un témoin, l'indépendance hors-Oasis et la survie longue restent `NOT_ESTABLISHED`**. #605 examine séparément l'usage de preuve Q par Stage8 et ne doit pas être confondu avec cette publication de crédit interne.

La CI exacte sur Python 3.11/3.12 doit réussir les quatre gates, les variations minuscules d'arrondi seront tolérées à l'échelle de la vérification de formule; les deux exécutions ne sont pas deux cohortes indépendantes. Aucun changement I1/I0/TD, `lambda_e=0.8` inchangé, aucune action imposée, aucun état caché du monde et aucune lecture Q gratuite.
