# A2.17b : séparer l'agence d'un effet proximal de la responsabilité d'un objectif distal

**Préenregistrement du 14 octobre 2026 avant code ou exécution A2.17b.** Base `main ecfbf96b90aa2195dec4806815f2f1cc24d28143`, issue #110 ouverte, Stage12 PARTIAL et non réceptionné. Spécification normative v1.3.1 inchangée.

## Motivation et portée
Le banc A2.17a (48 transitions physiques, 6 familles ×8 seeds 71–78, deux Python) montre 24/24 `unknown` pour des collectes, tandis qu'un mouvement réellement constaté peut donner `self`, un obstacle visible `world` et un mouvement échoué sans indice discriminant `unknown`. **Ce banc physique externe n'était pas un apprentissage d'I0.** Il n'autorise donc pas à réétiqueter rétroactivement les six collectes infructueuses de A2.16 en `self` ou `world`.

Question centrale : le changement local de l'inventaire réellement perçu est-il un indice **proximal** pertinent de l'action de collecte, sans transformer ce changement en preuve de responsabilité du résultat alimentaire **distal** ? Une variation du corps peut aussi provenir d'une intervention extérieure, sans ingestion ni collecte.

## Hypothèses indépendantes
- **Hprox** : après une collecte préengagée, le gain discret de l'espèce ciblée dans l'inventaire, sans mouvement, fournit un indice sensible d'une contribution proximale. Ce n'est pas encore une preuve métaphysique de causalité, et l'origine d'un gain d'inventaire extérieur reste non testée par le monde actuel.
- **Hfail** : en cas de collecte absente ou rendue inefficace par le banc, l'absence de gain d'inventaire ne justifie ni `self` ni `world` et le candidat proximal doit s'abstenir.
- **Hdistal** : un résultat `body.food` favorable obtenu sans ingestion ni acquisition doit demeurer distinct de toute attribution de l'objectif à la collecte. Il s'agit d'un confondeur extérieur observé, pas d'une récompense causée par la commande.
- **Hboundary** : le service de première personne actuellement intégré reste inchangé ; l'expérience mesure un candidat externe seulement, séparément de `GoalAgencyService`. Aucun mécanisme ne doit être introduit dans ActionControl ou le détecteur pendant A2.17b.

## Scénarios physiques préenregistrés
Huit seeds 81–88, coordonnées corporelles intérieures distinctes par seed et condition. Cinq conditions, **40 mondes physiquement instanciés et 40 véritables `WorldBody.apply`** : collecte d'une baie présente, collecte sans ressource, collecte volontaire rendue infructueuse par `set_action_failure_schedule`, collecte infructueuse suivie d'une intervention `set_body` augmentant `food` avant la capture suivante, et collecte réussie suivie d'une intervention `set_body` diminuant `food`. Les interventions externes sont recensées par le laboratoire mais ne sont jamais transmises comme étiquettes à la politique cognitive.

Comparer pour chaque monde : (a) jugement first-person réel OFF, (b) **sonde expérimentale hors-ligne** d'indice proximal fondée sur le préengagement de collecte, la même position et le différentiel positif exact d'inventaire, (c) delta alimentaire physique observé et (d) interprétation de l'objectif distal, qui reste **non attribuable à partir de ce delta seul**. Le banc mesure un contraste et ne crée ni jugement `world` ni jugement distal `self`.

## Critères préalables
T1 : 40 vrais mondes, 40 transitions appliquées, 8 seeds documentées, code/SHA/effets observés sous Python 3.11 et 3.12, zéro accès Oracle au candidat, aucune transition simulée.
T2 : la sonde proximale reconnaît exactement 8/8 collectes réussies et 8/8 collectes réussies malgré intervention corporelle nocive ; elle s'abstient sur les 24 autres cas (collecte absente, échouée ou échec avec gain alimentaire extérieur). Ce critère **ne valide pas une responsabilité causale générale**, car le monde ne propose pas d'intervention extérieure directe sur l'inventaire.
T3 : le service de référence reste `unknown` sur 40/40 cas de collecte du but alimentaire ; un éventuel gain de labels par la sonde ne doit pas être attribué à la politique cognitive actuelle.
T4 : aucun effet `body.food` ne permet d'inférer l'agence proximale à la place de la capture d'inventaire. La responsabilité du but alimentaire distal reste **INCONCLUSIVE**.
T5 : si les critères échouent, conserver le résultat négatif et ne pas adapter seeds, scénarios, seuils ou code après observation pour obtenir PASS. Ne pas déployer un mécanisme susceptible de confondre acquisition et alimentation.

**Réception** : aucun PASS du Stage12, aucun changement normatif, aucune fermeture #110. Un vrai changement de `GoalAgencyService` exigerait un contrat de portée explicite et une ablation autonome multi-seeds, avec faux positifs et risques nocifs/retardés.
