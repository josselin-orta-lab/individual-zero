# Individual Zero — Spécification normative MVP v1.3.2

**Titre :** Attribution subjective des résultats d'objectif, conséquences vécues indépendantes et diagnostic sans promotion injustifiée  
**Langue faisant autorité :** anglais, [version anglaise](../en/mvp-specification-v1.3.2.md)  
**Date :** 13 octobre 2026  
**Statut :** **CIBLE NORMATIVE AUTORISÉE, IMPLÉMENTATION ET RÉCEPTION NON ENCORE DÉMONTRÉES**  
**Portée :** issue #110, Stage 12 uniquement.

## 0. Autorité et portée

Cette nouvelle version complète [v1.3.1](mvp-specification-v1.3.1.md) sans modifier ses textes historiques ni les obligations de v1.2.1, hormis les ajouts explicites ci-dessous. Les six phases, les budgets UC, la mortalité irréversible, l'état courant transactionnel M-11, les propriétaires canoniques, le journal intégral, l'isolation Oracle/Bench, les quatre détecteurs du Stage 12, la réception opérateur et la validation scientifique finale subsistent. Le Stage 9 conserve son **NO-GO scientifique**.

La proposition distincte `docs/architecture/proposals/mvp-v1.3.2-dc05-food-safety-semantics-delta.md` n'est **pas adoptée** par cette version ; DC-05 et les règles alimentaires demeurent inchangées. Publier cette norme ne prouve pas son implémentation.

## 1. Trois propositions distinctes, GA-01

1. `goal_criterion_outcome=success|failure|unknown` : réussite ou non-réalisation d'un critère observable **préenregistré avant l'action**, vérifié ensuite. Un non-gain ne prouve pas l'échec global du but, un gain ne prouve pas que l'individu en est la cause.
2. `prediction_status=conforming|nonconforming|indeterminable` : exactitude des prédictions P-47. Ne signifie jamais réussite d'objectif ou responsabilité personnelle.
3. `subjective_agency=self|world|unknown` : **jugement faillible réellement produit par I0**, sur sa contribution à la conséquence pertinente pour le but. Ce jugement n'est pas la vérité causale physique. `unknown` est un jugement effectivement formulé dans l'incertitude ; `unavailable` signifie qu'aucun calcul valable n'a été produit.

Les étiquettes P-47 `self_compatible|world_justified|uncertain` conservent leur sens. Leur conversion automatique en `self|world|unknown` est interdite.

## 2. Propriétaires uniques, GA-02

**Action Control** possède un sous-service borné `GoalAgencyJudgement`, sans nouveau composant de premier rang. Lui seul forme et publie la croyance subjective de responsabilité avec des indices accessibles à I0. Il n'accède ni aux causes cachées, ni au WorldBody brut, à l'Oracle, au Bench, au diagnostic du laboratoire, au résultat `success/failure` du registre, ni au journal technique comme entrée cognitive.

**Metacognition and Health** conserve le registre préexistant `Stage12GoalProgressLedger`, les couples admis et son historique de détection. Le Causal Model conserve seul les états de causalité établis : un jugement subjectif n'établit pas une intervention, ne modifie ni κ ni les règles de sécurité, et ne confère aucun pouvoir moteur.

## 3. Engagements antérieurs et jugement ultérieur, GA-03/GA-04

Avant une commande volontaire, autorisée et rattachée au but actif, deux engagements immuables sont associés à la commande exécutée :

- **Critère d'objectif** : `life_id, intent_ref, goal_ref, option_ref, command_digest, sent_world_step, baseline_measure, baseline_value, comparator, threshold, observe_deadline, version`. Réutiliser le registre de progression existant.
- **Engagement d'appréciation d'agence** par Action Control : `life_id, agency_assessment_ref, intent_ref, goal_ref, option_ref, command_digest, sent_world_step, observe_deadline, policy_version, pre_action_cues_ref, candidate_mechanism, allowed_cue_mask`. Cela préenregistre l'hypothèse d'influence et les indices autorisés, **pas** une conclusion postérieure.

Lors de la perception suivante légalement disponible, Action Control évalue ses propres indices, indépendamment du succès/échec mesuré par Metacognition. Politique déterministe et versionnée, figée à la naissance :

- `self` uniquement si la commande volontaire exécutée est reliée à un **indice perceptif spécifique à l'action**, daté et préautorisé (copie efférente + conséquence perceptible, par exemple déplacement proprioceptif), et si cet indice explique plausiblement la conséquence pertinente pour le but. L'envoi de la commande ou la seule conformité P-47 ne suffit pas.
- `world` uniquement si un **obstacle ou événement externe spécifiquement perçu**, temporellement pertinent, soutient une contribution extérieure dominante. Un échec d'objectif ou une discordance P-47 ne suffit pas.
- `unknown` si les indices sont insuffisants, concurrents, confondus ou étrangers à la variable d'objectif. Une créature proche après l'ingestion d'une baie ne prouve pas l'origine d'une perte d'intégrité.
- `unavailable` si la perception, la facturation ou le calcul sont absents. Ce n'est pas une attribution produite par I0.

Le résultat comprend `judgement_ref, agency_assessment_ref, life_id, intent_ref, command_ref, action_observed_ref, sent_world_step, observed_world_step, judged_cycle, cue_refs, policy_version, subjective_agency, uncertainty_reason`. Une seule clôture par engagement. Le changement de prédiction à commande et perception identiques ne doit pas changer le jugement, sauf modification légitime d'un indice efférent préenregistré. L'attribution reste subjective, sans prétention étiologique.

## 4. Ordre, coûts et persistance, GA-05

Les six phases cognitives ne changent pas. Une seule capture physique réelle par pas éveillé ; aucune publication rétroactive. L'engagement précède la transition. L'évaluation cognitive par Action Control a un coût UC positif et versionné `goal_agency_assessment`, déclaré avant la naissance. La jointure chez Metacognition a le coût positif et versionné `stage12_attribution_join`, sauf couverture démontrable par un coût diagnostique augmenté et versionné. Le refus du budget laisse `unavailable`. Les coûts réellement acceptés alimentent la fatigue.

Le jugement et son état en attente appartiennent au propriétaire Action Control, le registre de couplage et les références consommées au propriétaire Metacognition. Leurs images font partie de la même génération courante M-11, atomique et authentifiée. Refuser les duplications, une identité étrangère, une fenêtre expirée, les segments annulés, une restauration historique, une cognition après décès et une réactivation de vie. Le sommeil sans cognition autorisée ne crée aucun jugement artificiel.

## 5. Jointure indépendante et détecteur, GA-06

Le seul triplet admis `(outcome, agency, attribution_ref)` provient d'une jointure vérifiée de l'intention avant action, de la commande et transition réellement appliquées, du résultat observé ultérieurement, du jugement **original** d'Action Control et des justificatifs UC. Chaque référence, tentative, identité, délai et version doit concord­er ; les chaînes de calcul de `outcome` et `agency` sont distinctes. Le succès d'objectif ne peut fournir le jugement qu'on souhaite ensuite mesurer.

Les inconnus, absences, incohérences et doublons ne comptent pas comme couples. Les seuils préenregistrés exigent suffisamment de succès **et** d'échecs distincts ; sinon `attribution_bias=None`. Les sorties `self_serving_pattern`, `self_blame_pattern` ou `no_detected_pattern` décrivent une association locale, pas une cause physique ni une caractéristique universelle.

## 6. Vérification et campagne, GA-07

L'auditeur externe, sans importation d'I0, du WorldBody, de l'Oracle ni du Bench, reconstitue sources, ordre, attribution subjective, pertinence des indices, débits UC, état de vie, couples uniques et diagnostics. Il refuse un journal falsifié puis correctement rechaîné lorsque les contrats sémantiques ne sont pas respectés. La cohérence cryptographique ne prouve pas la réalité physique indépendante.

Tests nécessaires : réussite/non-gain/inconnu vécus, jugements `self/world/unknown` quand les indices sont effectivement accessibles, abstention légitime, contrôle négatif de prédictions différentes sur une même conséquence, faux journaux rechaînés, duplications, provenance tardive/illégitime, coût refusé, décès, reprise froide et interruption brutale M-11. Préserver les stages 9 à 12, Observer, Python 3.11/3.12 et l'isolation externe.

Une campagne préenregistrée de **600 pas physiques réellement exécutés**, éventuellement répartis sur plusieurs vies distinctes, permet seulement une hypothèse de fonctionnement exploratoire. Zéro couple admissible après 600 pas ne démontre rien sur la capacité positive du détecteur. La validation scientifique finale, séparée, demeure obligatoire.

## 7. Réception et compatibilité

- P-47 §9.6, DC-05 et DC-06 : **inchangés**.
- §16.1 et §20.3 du Stage 12 : **complétés par GA-01 à GA-07**.
- DC-11 et budgets : six phases inchangées, opérations nouvelles facturées.
- v1.3.1 M-01 à M-20 : **conservés** et étendus aux nouvelles données.
- Aucune requalification du NO-GO Stage 9.

**Le Stage 12 reste EN COURS** tant que les tests intégrés, les preuves vécues indépendantes et la réception explicite de l'opérateur ne sont pas acquis. La norme décrit un objectif de développement, non une réussite déjà démontrée.

## 8. Option A autorisée : sous-objectif spatial directement perçu (GA-08)

**Autorisation opérateur du 14 octobre 2026.** Cette extension complète uniquement la nouvelle cible normative v1.3.2. Les spécifications historiques v1.3.1/v1.2.1, DC-05, DC-06, Stage 9 NO-GO et M-11 ne sont pas modifiées. L'autorisation ne vaut pas validation logicielle ou scientifique.

`spatial_progress_v1` désigne uniquement **la diminution stricte, en un pas physique, de la distance de Manhattan entre la position perceptible d'I0 et une cible de ressource ou d'eau déjà perçue avant la commande**. L'objectif actif doit légitimement concerner cette ressource ; la commande volontaire `se_deplacer` doit être admise, motivée par `active_goal`, orientée vers une cible effectivement observable et reliée à une direction engagée. Un déplacement exploratoire non lié à l'objectif ne peut être compté. Toute cible issue du banc, d'une vérité WorldBody cachée ou de l'Oracle est interdite.

Metacognition étend son **registre existant** `Stage12GoalProgressLedger` : `life_id, intent_ref, goal_ref, option_ref, command_digest, sent_world_step, observable_target_ref, target_x_y, initial_x_y, authorized_direction, initial_manhattan_distance, strict_distance_decrease, observe_world_step=sent+1, version`. Le critère précède l'action. L'observation autorisée suivante vérifie indépendamment la distance. `success` signifie uniquement que la distance a diminué, `failure` qu'elle n'a pas diminué, `unknown` que la mesure est inaccessible, tardive ou refusée. Aucun de ces états n'est une explication physique. Les gains corporels restent définis comme auparavant, sans conversion implicite.

Action Control peut former un jugement d'agence propre `spatial_obstacle_cue_v1`, à partir de la copie efférente et des cellules adjacentes **réellement perçues** :
- `self` seulement lorsqu'un déplacement spécifique au but est perçu dans la direction volontairement commandée, sans prétention de causalité physique prouvée.
- `world` seulement si la cellule **précise** de destination est perçue comme non passable, que la position demeure inchangée et que la commande était pertinente pour le sous-objectif préengagé. Une position inchangée sans cellule bloquée ne suffit jamais. Les règles de sécurité restent maîtresses de l'admission, même si cela empêche toute observation positive.
- `unknown` si cellule/cible non observable, indices périmés ou contradictoires, cause concurrente, lien au but absent ou ambigu.
- `unavailable` si le calcul ou le prélèvement UC légitime est refusé. Une discordance P-47 et un échec corporel ne valent pas `world`.

L'agence ne consulte jamais le résultat `success/failure`, la vérité cachée ni le détecteur. Le calcul du résultat ne consulte pas le jugement. Les propriétaires uniques, phases, débits UC positifs versionnés, transaction atomique M-11, mortalité irréversible et vérification indépendante demeurent obligatoires. Aucune fenêtre diagnostique ni aucun seuil de biais n'est réduit ou allongé ; le sommeil n'est pas contourné.

L'auditeur externe doit reconstruire les sources réellement préaction, commande et transition physique, perception de la position et de la passabilité, débits UC, références uniques, jugement indépendant et diagnostic. Il rejette les journaux rechaînés qui inventent un obstacle, substituent une direction/cible, réutilisent une observation, changent de vie ou produisent une cognition postmortem. Une fixture positive `world` n'est **pas** la preuve qu'une vie autonome émet `world`.

**Réception :** préserver les résultats nuls. Si I0 n'exécute jamais librement de commande dirigée vers un obstacle, `world` peut légitimement rester absent et le détecteur rester `None`. Ne pas forcer une action, assimiler une conformité P-47 à une attribution, fusionner prématurément ni recevoir le Stage 12 sans campagne et validation opérateur.
