# Issue #89 — validation de la frontière épistémique DC-05

**Date :** 2026-10-13  
**Statut :** READY FOR OPERATOR REVIEW.  
**Stage 9 historique :** SCIENTIFIC NO-GO, inchangé.  
**Base main auditée :** `12df9e5ce8c51f6a378a7ab4313daf0710679dd2`.  
**SHA logiciel + campagne testé :** `b55bae28d757727f09f280125d2a82ae54dc6183`.  
**Matrice de validation :** GitHub Actions run [#38451074883](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38451074883), Python 3.11 et 3.12 SUCCESS.

## Périmètre et défaut original

L'issue #89 concerne l'attribution de dommages observés après ingestion à un aliment lorsque la vérité physique complète est volontairement redacted de l'expérience accessible à I0. Le défaut résiduel reproduit sur `main` permettait à des épisodes indépendants `attendre propre -> danger invisible activé seulement au repas -> baie bénigne -> blessure` d'atteindre le seuil `n_sec` et de produire `etabli_pour_securite`, alors que la cause concurrente restait compatible avec toute l'expérience autorisée.

Les PR #77, #93 et #98 avaient déjà supprimé l'usage cognitif direct des champs physiques cachés, ajouté le contrôle vécu, bloqué les créatures perceptibles pertinentes et construit une paire de mondes observationnellement équivalents. Le résidu provenait de la transformation répétée d'une association vécue ambiguë en crédit alimentaire définitif.

## Carte auditée

`Perception locale + télémétrie corporelle -> projection autobiographique DC-09 -> CausalModel.ingest_closed_autobiographical_episode -> SafetyEvidence / CausalObservation / LivedNumericOutcome -> publication CausalModel -> CanonicalSafetyFacts -> ActionControl / Simulator`.

Aucune autre voie de production utilisée en runtime Stage 9 n'a été trouvée pour injecter directement un crédit `toxic_item`. Le bas niveau `CausalModel.integrate(SafetyEvidence)` reste utilisé par des tests unitaires typés, mais n'est pas un producteur runtime. Oracle, Bench et le journal technique complet restent hors cognition. Le journal complet conserve les causes physiques pour audit externe.

La restauration de snapshot a également été renforcée : un témoin numérique alimentaire publié ou pending doit rejoindre l'observation causale vécue exacte, même épisode, même transition, même pas et même aliment. Un snapshot ne peut donc pas fabriquer une correction numérique que la voie runtime n'a jamais gagnée.

## Contrat d'admission final

- concurrent perceptible physiquement pertinent : expérience conservée, aucun crédit alimentaire, aucune observation causale alimentaire, aucune correction numérique ;
- contrôle absent ou lui-même dommageable : expérience conservée, aucune attribution alimentaire ;
- contrôle vécu propre puis dommage après ingestion : `ambiguous_food_association`, sans crédit DC-05, sans observation causale alimentaire et sans correction numérique ;
- répétition, changement de position ou multiplicité de vies : ne convertissent pas l'ambiguïté en étiologie ;
- ingestion sans dommage : observation no-harm admissible pour la logique existante de démotion ;
- vérité technique cachée : disponible seulement à l'opérateur/auditeur, jamais consommée par I0.

La présence d'une créature perceptible sur la même cellule ou à distance 1 bloque correctement l'attribution alimentaire. Une créature visible mais trop éloignée ne devient pas artificiellement une cause concurrente locale. Cette décision utilise uniquement la Perception autorisée.

## Limite d'identifiabilité

Deux mondes peuvent produire la même histoire autorisée pour I0 : aliment réellement toxique sans danger externe, ou aliment bénin avec danger invisible activé exactement au repas. Les tests vérifient que les autobiographies sont équivalentes alors que les journaux techniques et leurs empreintes diffèrent.

Si les observations accessibles sont identiques, aucune règle cognitive respectant la frontière épistémique ne peut attribuer une étiologie différente aux deux mondes sans information supplémentaire. L'auditeur externe peut certifier la chaîne, l'ordre et les ancres du journal ; il retourne explicitement `physical_truth_verified = false` et n'injecte aucune causalité dans I0.

Par conséquent, la v1.3.1 actuelle ne permet pas simultanément de garantir zéro fausse attribution étiologique dans cette classe de mondes et de garantir l'apprentissage d'une toxicité spécifique de l'aliment à partir de ces seules observations.

## Campagne contrastive

Campagne `issue89-dc05-epistemic-boundary-v1`, graines 41 à 48, huit vies indépendantes de 75 transitions physiques réellement appliquées chacune, soit **600 pas physiques**.

Scénarios : baie bénigne propre, danger invisible statique, danger invisible dynamique, créature perceptible, deux vies de toxicité réelle multi-contexte, monde toxique de la paire équivalente, monde bénin + danger dynamique de la paire équivalente.

Résultats identiques sous Python 3.11 et 3.12 :

- vies : **8** ;
- morts : **0** ;
- pas physiques : **600** ;
- ingestions : **14** ;
- blessures : **13** ;
- associations `ambiguous_food_association` : **11** ;
- admissions DC-05 : **1**, correspondant à l'ingestion bénigne sans dommage ;
- promotions `etabli_pour_securite` : **0** ;
- faux positifs de promotion : **0** ;
- blessures dues à de vrais aliments toxiques volontairement retenues : **7**.

Les huit vies ont chacune un journal de **375 événements**, vérifié par l'auditeur indépendant. Les ancres de tête sont reproductibles entre Python 3.11 et 3.12 :

- seed 41, benign_clean : `89b253713f75cafca723797b12944c6199f493dd4b66a2b0edaf9265c1e77dda` ;
- seed 42, hidden_static : `9b687a6c7081673934a6d5953ddd08be622edadd656d0c233760e7915644e38a` ;
- seed 43, hidden_dynamic : `ac66561d46f13e8b269bfaa01eb5caadc53cd5012884d158a078914d01376583` ;
- seed 44, visible_creature : `4972b2732f55b8eb09ead7c1988808aae21643e87e8b1301e5c8ed11e40172df` ;
- seed 45, toxic_multicontext : `a078f93a6a758a39749051f3762968381ce2244409502194e0d6163efd46585a` ;
- seed 46, toxic_multicontext : `d658cb27823efedb3365319beb0bf1039d70ddeab5090d52972c396ae1bdbf28` ;
- seed 47, equivalent_toxic : `b11a27200fc72efd70b0fec80a619b2f2a1472cc360807fc9cc139bc47f77a50` ;
- seed 48, equivalent_dynamic : `a69bd5571b7e8f1c1075784d21f08536511d903f66a862dddbc79240076de9ee`.

Artefacts GitHub conservés :
- `issue89-campaign-python-3.11`, digest `sha256:3ef35d4170336b12ada460ec59e1bcc7fe60076561df4d9eebefa4a63f93fc32` ;
- `issue89-campaign-python-3.12`, digest `sha256:64797ea9fb5d3348bb97b47d95e544f78e0c093dbadc3aea390e424a91c8c6ee`.

## Régressions Python 3.11 / 3.12

Sur chaque version :

- 8 tests adversariaux de causes concurrentes : SUCCESS ;
- 41 tests Stage 9 vécus ciblés : SUCCESS ;
- 393 tests `test_stage9*.py` : SUCCESS ;
- 15 tests d'isolation épistémique journal / autobiographie : SUCCESS ;
- 13 tests de l'auditeur indépendant : SUCCESS ;
- 1 test d'absence d'import Bench dans la cognition : SUCCESS ;
- campagne 600 pas : SUCCESS ;
- artefact de campagne : SUCCESS.

La CI générale du dépôt est filtrée pour ce périmètre et apparaît `skipped`; la matrice Stage 9 dédiée est la preuve Python 3.11/3.12 pertinente.

## Coût de la prudence

Le correctif fail-closed retient aussi des blessures dues à de vrais aliments toxiques lorsqu'elles restent observationnellement indiscernables d'un confondeur caché. La campagne mesure ce coût à **7 preuves toxiques vraies retenues sur 7 blessures toxiques ciblées**. Il évite le faux `known_toxic`, mais peut donc empêcher le veto alimentaire appris sous la sémantique v1.3.1 actuelle.

Un delta normatif séparé est proposé dans `docs/architecture/proposals/mvp-v1.3.2-dc05-food-safety-semantics-delta.md` : distinguer un fait de **risque empirique de consommation** d'une affirmation étiologique de **toxicité physique**. Si adopté dans une nouvelle version normative, le premier pourrait justifier un veto à partir d'épisodes nocifs indépendants sans prétendre que l'aliment est la cause physique, tandis que le second resterait soumis au cycle causal complet. Ce delta n'est pas appliqué à v1.3.1.

## Fichiers de la correction

Le périmètre reste limité au modèle causal Stage 9, son câblage runtime, ses tests, la campagne, le workflow et la documentation/proposition normative. Aucun fichier de `WorldBody.apply`, Stage 10, Stage 11, WAL/persistance M-11 ou consolidation n'est modifié.

## Conclusion

1. **Correction logicielle : SUPPORTÉE.** Le défaut de promotion de blessures alimentaires observationnellement ambiguës est corrigé en fail-closed ; aucune vérité cachée, Oracle, Bench ou journal technique n'est utilisée comme perception.
2. **Hypothèse de développement : PARTIELLEMENT SUPPORTÉE.** La frontière négative recherchée est supportée sur 600 pas avec zéro faux positif et journaux audités. En revanche, la sémantique v1.3.1 ne permet plus l'apprentissage étiologique alimentaire dans les cas toxiques observationnellement équivalents : les 7 preuves toxiques ciblées sont volontairement retenues.
3. **Limite fondamentale : DÉMONTRÉE.** Des causes physiques différentes peuvent rester indiscernables à partir de la seule expérience accessible à I0 ; une archive hashée intègre ne ferme pas cette indétermination.
4. **Acceptation opérateur : NON ACQUISE.** L'issue #89 reste ouverte et la PR #145 reste en brouillon jusqu'à réponse explicite.
5. **Validation scientifique finale : NON ACQUISE.** Cette campagne de développement n'inverse pas le résultat historique. **Stage 9 reste SCIENTIFIC NO-GO.**

## Décisions demandées à l'opérateur

Décision obligatoire pour #89 :

> « Acceptes-tu que l'issue #89 soit considérée comme résolue au niveau logiciel et épistémique, tout en conservant le Stage 9 historique en SCIENTIFIC NO-GO et la limite documentée selon laquelle des causes physiques différentes peuvent être indiscernables à partir de la seule expérience accessible à I0 ? »

Décision normative séparée :

> Acceptes-tu le principe du delta v1.3.2 qui sépare le **risque empirique de consommation utilisable par le veto** de la **toxicité physique causale**, afin de restaurer un apprentissage de sécurité sans fabriquer une causalité ?
