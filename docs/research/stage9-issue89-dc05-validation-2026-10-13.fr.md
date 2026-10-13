# Issue #89 — validation de la frontière épistémique DC-05

**Date :** 2026-10-13  
**Statut :** READY FOR OPERATOR REVIEW une fois la matrice CI finale verte.  
**Stage 9 historique :** SCIENTIFIC NO-GO, inchangé.

## Périmètre et défaut original

L'issue #89 concerne l'attribution de dommages observés après ingestion à un aliment lorsque la vérité physique complète est volontairement redacted de l'expérience accessible à I0. Le défaut résiduel reproduit sur `main` permettait à des épisodes indépendants `attendre propre -> danger invisible activé seulement au repas -> baie bénigne -> blessure` d'atteindre le seuil `n_sec` et de produire `etabli_pour_securite`, alors que la cause concurrente restait compatible avec toute l'expérience autorisée.

Les PR #77, #93 et #98 avaient déjà supprimé l'usage cognitif direct des champs physiques cachés, ajouté le contrôle vécu, bloqué les créatures perceptibles pertinentes et construit une paire de mondes observationnellement équivalents. Le résidu provenait de la transformation répétée d'une association vécue ambiguë en crédit alimentaire définitif.

## Carte auditéе

`Perception locale + télémétrie corporelle -> projection autobiographique DC-09 -> CausalModel.ingest_closed_autobiographical_episode -> SafetyEvidence / CausalObservation / LivedNumericOutcome -> publication CausalModel -> CanonicalSafetyFacts -> ActionControl / Simulator`.

Aucune autre voie de production utilisée en runtime Stage 9 n'a été trouvée pour injecter directement un crédit `toxic_item`. Oracle, Bench et le journal technique complet restent hors cognition. Le journal complet conserve les causes physiques pour audit externe.

## Contrat d'admission final

- concurrent perceptible physiquement pertinent : expérience conservée, aucun crédit alimentaire, aucune observation causale alimentaire, aucune correction numérique ;
- contrôle absent ou lui-même dommageable : expérience conservée, aucune attribution alimentaire ;
- contrôle vécu propre puis dommage après ingestion : `ambiguous_food_association`, sans crédit DC-05, sans observation causale alimentaire et sans correction numérique ;
- répétition, changement de position ou multiplicité de vies : ne convertissent pas l'ambiguïté en étiologie ;
- ingestion sans dommage : observation no-harm admissible pour la logique existante de démotion ;
- vérité technique cachée : disponible seulement à l'opérateur/auditeur, jamais consommée par I0.

## Limite d'identifiabilité

Deux mondes peuvent produire la même histoire autorisée pour I0 : aliment réellement toxique sans danger externe, ou aliment bénin avec danger invisible activé exactement au repas. Si les observations accessibles sont identiques, aucune règle cognitive respectant la frontière épistémique ne peut attribuer une étiologie différente aux deux mondes sans information supplémentaire.

Par conséquent, la v1.3.1 actuelle ne permet pas simultanément de garantir zéro fausse attribution étiologique dans cette classe de mondes et de garantir l'apprentissage d'une toxicité spécifique de l'aliment à partir de ces seules observations.

## Coût de la prudence

Le correctif fail-closed retient aussi des blessures dues à de vrais aliments toxiques lorsqu'elles restent observationnellement indiscernables d'un confondeur caché. Il évite le faux `known_toxic`, mais peut donc retarder ou empêcher le veto alimentaire appris sous la sémantique actuelle.

Un delta normatif séparé est proposé dans `docs/architecture/proposals/mvp-v1.3.2-dc05-food-safety-semantics-delta.md` : distinguer un fait de **risque empirique de consommation** d'une affirmation étiologique de **toxicité physique**. Ce delta n'est pas appliqué à v1.3.1 et nécessite une décision opérateur séparée.

## Scénarios de validation

La campagne ciblée couvre baie bénigne propre, danger invisible statique, danger invisible dynamique, créature perceptible, toxicité réelle multi-contexte, et paire observationnellement équivalente toxique/danger dynamique. Les pas sont des transitions WorldBody réellement appliquées ; les décès arrêtent les trajectoires ; les journaux sont vérifiés indépendamment sans importer I0, Oracle ou Bench dans la voie d'audit.

## Résultats

À compléter automatiquement après la matrice finale du SHA de PR : Python 3.11 et 3.12, campagne 600 pas, métriques d'ingestions, blessures, ambiguïtés, admissions DC-05, promotions, faux positifs, preuves retenues, vies, morts et ancres de journal.

## Conclusion

1. **Correction logicielle :** le défaut de promotion de blessures alimentaires observationnellement ambiguës est corrigé en fail-closed sur la branche de #89.
2. **Hypothèse de développement :** à confirmer par la campagne finale 600 pas et la matrice 3.11/3.12.
3. **Limite fondamentale :** l'étiologie physique n'est pas identifiable dans les mondes observationnellement équivalents sans nouvelle information accessible.
4. **Acceptation opérateur :** non acquise. L'issue doit rester ouverte jusqu'à réponse explicite.
5. **Validation scientifique finale :** non acquise et hors portée de cette issue. Le Stage 9 historique reste SCIENTIFIC NO-GO.
