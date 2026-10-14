# A2.27 : résultats autonomes de la séparation analytique agence proximale / résultat distal

**15 octobre 2026.** Préenregistrement [A2.27](stage12-issue110-a227-dual-scope-prereg-2026-10-15.fr.md) au SHA `f42019f7`, écrit avant l'instrumentation. [CI scientifique #38655243899](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38655243899) : **SUCCESS Python 3.11 ET 3.12** au commit `6794c54432df05aa2df9b3ba1a40ea357e87b3f5`. Les deux versions exécutent les **mêmes seize configurations**, non 32 vies indépendantes.

## Résultats bornés

**16 vies individuelles Stage12 autonomes mortelles, 32 pas chacun, 512 transitions authentiquement exécutées, huit interventions extérieures `set_body(food=75)`** au pas 6, préengagées avant la naissance. Les archives canoniques, le WAL et le témoin physique externe sont croisés par un auditeur de laboratoire en seconde lecture ; aucun accès de l'individu au banc ni à l'Oracle. **16/16 vies passent les auditeurs indépendants d'objectif et d'agence inchangés** dans cet échantillon, **0/16 vie évaluable pour le détecteur GA-06 `2+2/12`**. Le test comporte trois contrôles négatifs purement algorithmiques hors cohorte, explicitement non comptabilisés comme vie ou paire.

| Classification externe | Pas concernés | Ce qui est réellement établi |
| --- | ---: | --- |
| `ingestion_effect` | 7 | commande `manger` et effet physique `ate` |
| `collection_effect` | 7 | commande `collecter` et quantité physiquement collectée |
| `no_direct_effect_witness` | 498 | ni ingestion ni collecte directement étayée par l'effet sélectionné |
| `external_influenced` | 8 | intervention `set_body` reçue et appliquée ; attribution volontaire exclue |
| `ingestion_observed` | 7 | ingestion reconnue sans intervention au même pas |
| `other` | 497 | aucun des indicateurs distaux précédents |
| Responsabilité causale distale prouvée | **0** | attribution exclue par contrat de l'auditeur, **pas preuve physique d'absence de responsabilité** |

Les colonnes proximal et distal forment **deux partitions différentes** des 512 transitions. Elles ne doivent pas être additionnées entre elles. `no_direct_effect_witness` ne signifie pas qu'I0 n'a produit aucun autre effet de l'action (exemple : déplacement). La classification ne modifie aucun événement subjectif `self/world/unknown`.

**Aucun suivi d'objectif ne diverge** ici du corps committé malgré les huit injections. Ce cas confirme que la confusion observée en A2.25/A2.26 dépend du placement de l'intervention, de la naissance et du suivi effectivement produit ; on ne peut pas postuler que toute intervention extérieure provoque un rejet. L'absence de rejet ici n'invalide pas les trois refus reconnus dans chacun des deux protocoles précédents.

## Arbitrage architectural présenté à l'opérateur, non décidé

**Option A, conserver un unique jugement sur l'objectif (`GoalAgencyService` actuel).** Avantages : fidélité à v1.3.1, conservation UC/owner/journal, abstention `unknown` prudente. Coût : aucune expression cognitive distincte de l'effet proximal quand le résultat alimentaire est exogène ou confondu ; faible diversité de paires GA-06.

**Option B, séparer deux jugements internes versionnés** : `action_agency` se rapporte aux indices efférents/sensoriels de la commande ; `outcome_responsibility` se rapporte à la contribution causale à la mesure de l'objectif, avec `unknown` par défaut lorsque la source ou le calendrier ne suffit pas. Avantages : évite formellement de transférer une collecte réussie en succès alimentaire personnel ; peut enrichir l'abstention explicite. Coûts : nouveau contrat normatif, modèles de persistance, UC, auditeur, calibration scientifique et migration compatibles avec mortalité/M11 ; contre-exemples de relocalisation et de capteur conjointement compromis restent sans solution. **Non autorisé par cette campagne.**

**Option C, conserver la cognition normative actuelle et publier les deux axes seulement dans un audit externe.** Avantages : résultats lisibles et audités maintenant, sans nouveau signal de vérité injecté dans I0 et sans alourdir le MVP. Coût : l'individu ne développe pas lui-même un jugement proximal explicite, et cela ne résout pas directement la lacune cognitive visée par #110.

**Recommandation de laboratoire : C comme mesure provisoire de lecture, puis soumettre B à décision opérateur séparée.** Cette recommandation n'est pas une validation scientifique de B, ni un accord de modification v1.3.1. Tant que le critère GA-06 `2+2/12` n'est atteint dans aucune vie et que les cas confondus ne sont pas correctement représentés au niveau subjectif, **Stage12 PARTIAL ; #110 OPEN ; zéro réception opérateur**.

## Limites importantes

A2.27 réutilise le modèle de naissance d'A2.26, mais crée de **nouvelles vies autonomes** aux identités distinctes. Le test couvre 32 pas et pas 600. Le `set_body(food=75)` extérieur peut infléchir choix et besoins, ce qui interdit de lire les différences comportementales entre bras comme un effet causal isolé. Les quatre profils ne sont pas des expériences randomisées statistiquement indépendantes. Les comparaisons audit/physique sont des témoins d'ingénierie, non une preuve de l'intention véritable.

Aucune modification de la logique cognitive, du jugement existant, des UC, de M11/WAL, de Stage9/DC05, de l'Oracle, de la sécurité, de la mortalité ou de la spécification v1.3.1. La CI du rapport final est une vérification distincte de celle du code exécuté.
