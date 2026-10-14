# Stage12 #110 : A2.11 premier diagnostic Equipment et UC, sans correction comportementale

**14 octobre 2026. Verdict PARTIAL.** Préenregistrement `ae29c9fa64b59fc3e5fa3b40fbdca39f93655f09` créé avant le script. Base `main 57476d386d7a5b742c1abd0e078568395ebc3a47`. Ce checkpoint n'introduit aucun prédicteur généralisant, aucune simulation de conséquences non vécues, aucun gain alimentaire nouveau, aucun changement de mémoire, de sécurité, de politique ou de spécification normative v1.3.1.

## Données réelles et audit indépendant

Source exacte : les **16 archives causales scellées** de [A2.10b #38607070724](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38607070724), soit 16 vies ×42 pas = **672 transitions physiques uniques**. Les réexécutions Python 3.11 et 3.12 de cette même cohorte ont déjà produit des rapports physiques cohérents. A2.11 **ne prétend pas produire de nouvelles vies** : il analyse en lecture seule les reçus existants et n'exécute aucune action dans I0. La vérification locale du ZIP GitHub officiel Python 3.11 a trouvé :

- **372** reçus `stage6_planning_result.progressive_search_diagnostic.status=incomplete_model` répartis sur les 16 vies. Un reçu est un diagnostic de recherche, pas une transition ni un couple état/commande unique.
- **0** `compute_charge` de Planning avec `accepted=False`. Toutes les charges UC Planning explicitement émises et inspectées sont acceptées ; cela **n'exclut pas** d'autres limites UC, ni une saturation empêchant l'émission d'une nouvelle charge.
- Les options alimentaires peuvent être `not_evaluated` même lorsqu'un objectif existe. Une absence d'évaluation ne doit pas être assimilée à un veto de sécurité, ni à une réfutation de compétence future.
- La couverture **exacte** du modèle est **NON ÉVALUABLE** depuis les seuls reçus publics : ceux-ci ne publient pas chaque couple `SimulationState × PrimitiveCommand` essayé, ni sa clé SHA. On ne peut pas convertir le nombre de `incomplete_model` en taux de couverture.
- La fabrique de référence `build_prebirth_equipment` enregistre seulement quatre transitions externes physiques pour la version alimentaire : nord, est, collecte, ingestion. `FrozenTableEquipment.predict` exige un SHA strictement identique de l'état complet et de la commande, sinon `LookupError`.

Ces constats sont directement vérifiables à partir des archives et des sources. Le rapport CI A2.11 associé télécharge les mêmes preuves plutôt que d'exécuter à nouveau 672 pas uniquement pour des compteurs déjà présents.

## Analyse et limites

**H_exact : mécanisme explicite confirmé dans le code, niveau comportemental PARTIAL.** Les états de Simulation comprennent corps, inventaire, position, environnement local, jour/nuit. Un état inconnu est indisponible ; cette frontière ne doit pas être détournée en interpolation omnisciente. Les 372 diagnostics démontrent l'impact potentiel du déficit de modèle, pas quels couples exacts manquent ni combien ont une conséquence sûre.

**H_UC (refus explicite de Planning comme cause principale) : NON ÉTAYÉE** par les reçus émis (0 refus), mais l'audit n'observe pas toute décision de scheduling ou phase non lancée. **H_mem, H_val, H_control : encore PARTIAL/INCONCLUSIVE** faute d'une séparation expérimentale de tous les mécanismes. Dans A2.10b, la condition sustained libre gain1.6 ingère malgré un nombre élevé de recherches incomplètes : cette lacune n'explique pas seule l'échec après obstacle.

**H_coverage « augmenter les données physiques améliore réellement I0 » : NON TESTÉE.** Aucun corpus ON élargi n'a encore été construit, entraîné et apparié à une vie témoin. L'absence de cette expérience interdit de déclarer un succès alimentaire, une politique optimisée ou une généralisation validée.

## C1 à C8

| Critère | Verdict |
|---|---|
| C1 attribution subjective | PARTIAL, calibration inchangée/non acquise |
| C2 causalité distincte | PARTIAL, pas de nouvelle manipulation du comportement |
| C3 diversité | INCONCLUSIVE pour cette étude hors-ligne |
| C4 alimentation réellement vécue | PARTIAL hérité, aucun gain A2.11 testé |
| C5 P-48 | INCONCLUSIVE pour ce contrôle documentaire |
| C6 stabilité prolongée | INCONCLUSIVE |
| C7 reproductibilité | PARTIAL, preuves source reproductibles mais pas des seeds indépendantes |
| C8 conformité | PASS borné, auditeur externe uniquement et aucune vérité Oracle transmise à I0 |

**GLOBAL Stage12 PARTIAL. Issue #110 OPEN, réception opérateur non effectuée.**

## Prochain sous-protocole technique

Avant toute fusion d'un nouvel Equipment, comparer au moins un modèle exact-table enrichi avec des exemples **réellement appliqués sur un WorldBody extérieur avant naissance**, en contrôlant séparément les différentes échelles de nourriture et les observations locales. Conserver le témoin quatre exemples, mesurer les clés exactes réellement couvertes avec instrumentation isolée, les vrais repas, les erreurs, les risques et l'exploration, et conserver l'inconnu `unavailable`. Ne pas utiliser les états de la vie témoin pour fabriquer le corpus ON. Une modification architecturale de la norme v1.3.1 demandera une décision opérateur distincte.
