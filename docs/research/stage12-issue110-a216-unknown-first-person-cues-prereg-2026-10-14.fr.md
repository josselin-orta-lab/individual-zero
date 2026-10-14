# Stage12 issue #110 : préenregistrement A2.16, décomposition des jugements subjectifs suspendus

**14 octobre 2026 ; protocole déposé AVANT toute instrumentation A2.16.** Référence `main@055daf6443bd3f88a2e94330378984298e876a80`. Stage12 PARTIAL, issue #110 OPEN, réception opérateur absente. MVP normatif v1.3.1 inchangé.

## Point de départ

Le bilan A2.15 sur 16 vies scellées (672 pas) atteste 22 intentions et résultats connus, 14 jugements `self/world` et **8 `unknown`**, 14 paires formées, 10 appliquées, 4 indisponibles pour `no_waking_diagnostic_at_due_step`, aucun refus UC de jointure. La fenêtre 12 n'a jamais plus d'un échec admissible par vie. La campagne A2.6 sur six vies ×600 pas sous deux Python confirme zéro vie calibrable, mais ne donne pas à elle seule l'origine des huit `unknown`.

## Questions et hypothèses prospectives

- **H_unresolved** : les `unknown` sont produits parce que le mécanisme préengagé est `unresolved`, faute de relation indépendante entre l'action exécutée et le but (par exemple, attente ou action indirecte).
- **H_ingestion** : une action `manger` préengagée avec inventaire ne produit pas le décrément perceptible voulu, ou le corps a changé de cellule ; un jugement `unknown` est alors cohérent, même si un critère `success/failure` corporel est connu.
- **H_spatial** : le mouvement vers une ressource visuellement attestée ne produit ni déplacement vers la cible ni nouvel obstacle observé ; la prudence `ambiguous_spatial_displacement_cue` est légitime.
- **H_source** : toutes les abstentions `unknown` sont payées, ancrées à une capture perceptive authentique et à une pré-intention unique. La présence d'une capture ou d'un résultat conforme ne justifie **pas** de transformer l'abstention en `self` ou `world`.

## Corpus et instrumentation

Lire, après vérification des audits indépendants `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_first_person_agency` et `audit_stage12_attribution_pairs`, les mêmes **16 archives scellées A2.10b du run #38607070724**, chacune avec SHA-256 ; retenir Python 3.11 pour les conclusions et Python 3.12 comme répétition technique. Un observateur totalement externe, sans Oracle ni `WorldBody`, joint chaque `stage12_goal_agency_judgement` à son `stage12_goal_agency_precommitted` par `assessment_ref`. Ventiler **toutes** les étiquettes `unknown/self/world/unavailable` par `mechanism`, `reason`, `action_primitive`, `goal_measure`, `criterion_outcome`, pas et vie. Mesurer si les paires `unknown` possèdent un suivi d'objectif `success/failure` réel, sans les rendre admissibles au détecteur. Extraire uniquement les métadonnées publiques autorisées du journal, jamais les étiquettes causales externes ou une carte cachée.

## Critères préalables

- **T1 :** exactement 16 journaux, 672 pas, provenance cryptographique et audits GA indépendants acceptés ; chaque jugement doit correspondre à un engagement unique, antérieur et dans la même vie, sans doublons.
- **T2 :** exactement 8 jugements `unknown` et 14 `self/world` sur cette cohorte ; aucune classification produite artificiellement. Chaque jugement `unknown` doit avoir un `cue_ref` réellement présent ou être signalé comme incohérent, pas transformé en `unavailable`.
- **T3 :** partition exhaustive par `mechanism`, `reason`, commande et résultat ; chercher de véritables témoins contradictoires entre causes plausibles plutôt que considérer `world` le complément logique de `self`.
- **T4 :** aucune commande ni état de corps envoyé à I0 depuis le laboratoire ; aucune généralisation d'innocuité ou mécanisme spécial pour obtenir un `PASS`.
- **C1/C2 :** les `unknown` ont un statut épistémique légitime jusqu'à preuve perceptive discriminante, la compatibilité prédictive ne valide pas l'agence.
- **C3/C4/C5/C6 :** relecture de 672 pas déjà vécus : ne pas déclarer une compétence nouvelle, ni stabilité, ni diversité accrue ; A2.6 3600 pas est un contrôle distinct.
- **C7/C8 :** reproduction Python 3.11/3.12 et norme inchangée ; un nouvel algorithme cognitif doit être préenregistré et validé **dans une autre PR** après ces résultats.

Le verdict Stage12 restera **PARTIAL**, issue #110 ouverte en attente de la réception opérateur. Aucune révision de la politique de `unknown` et aucun abaissement des seuils de calibration dans ce protocole.
