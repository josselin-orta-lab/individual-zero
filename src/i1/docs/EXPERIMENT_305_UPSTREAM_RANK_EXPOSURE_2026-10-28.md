# #305 : vérification préliminaire de l'exposition du classement Q en amont

Base : `ce8033ebe46730e092a40b55b51eac4b37b77f6b`, physiologie v4, naissance `oasis/b` et fenêtre M11 originelle de 18 pas. **Analyse descriptive rétrospective**, pas une expérience causale nouvelle.

La PR #598 a montré que le masquage de la contribution Q à l'adaptateur Stage8/Competition au pas 18 augmente la preuve de `collecter`, mais ne change pas la collecte. La nécessité causale de Q lors du **classement des candidats avant la proposition** demeure non démontrée.

Avant toute nouvelle ablation, lire les véritables événements `i1_unknown_affordance_proposed` du pas 18 : `candidate_count`, `candidate_primitives`, `command`, `learned_value_status`, `learned_value`, `option_ref` et cycle. Ces événements sont écrits par le propriétaire après la consultation Q et le tri naturel, avec coût Planning normalement facturé. Les deux bras déjà appariés de #598 permettent de contrôler la stabilité de ce **diagnostic** sans modifier la naissance.

L'événement ne contient ni signatures des candidats perdants ni leurs Q individuels : si plusieurs candidats existent, il ne permet **pas** d'affirmer lequel aurait gagné sans Q. Si un seul candidat existe à chaque cycle exposé, une ablation de classement serait mécaniquement non discriminante pour ce contexte. Si les événements sont absents, verdict `NOT_EXPOSED_IN_RECORDED_SOURCE`, sans supposer l'absence d'option physique.

Ne pas confondre une concurrence entre propositions locales et la concurrence ultérieure entre options de Competition; conserver les coûts UC, le filtre des actions perceptuellement disponibles, les autres propriétaires et les limites de mortalité. Aucun changement moteur I1/I0, aucun nouveau monde, aucun prolongement de vie, aucun succès imposé par les assertions. Quatre contrôles exact-head CI et vérification M11 avant intégration. Si la source existante s'avère insuffisante, une instrumentation purement opérateur des lectures authentiques de chacun des candidats sera étudiée dans un protocole séparé, sans déclencher des lectures Q supplémentaires gratuites.
