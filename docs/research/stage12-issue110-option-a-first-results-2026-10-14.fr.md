# Option A, issue #110 — premiers résultats logiciels et physiques, 14 octobre 2026

**Statut : faisabilité exploratoire INCONCLUSIVE pour `world`, contrôle logiciel de cues positif.**
Branche/PR [#155](https://github.com/josselin-orta-lab/individual-zero/pull/155), basée sur la PR #153 ; `main` et la norme v1.3.1 restent inchangés. La décision opérateur « lancer A » autorise la campagne, pas la réception du Stage 12.

## Provenance expérimentale

1. Préenregistrement du mécanisme et contrôles adversariaux, commit `1aa0fdb`, AVANT code ; préenregistrement prospectif physique séparé, commit `6750845`, AVANT runner.
2. Tests logiciels de politique locale `self/world/unknown` sur captures structurées et sur **vraies transitions WorldBody de fixture**. Les tests physiques sont exécutés avec commandes définies par la fixture et **ne sont pas des choix autonomes d'I0**.
3. Ajout à `perceptual_capture` de `agency_visible_adjacent` constitué exclusivement des quatre `PerceivedCell` visibles à I0 (direction, coordonnées, passabilité, eau, ressources). Pas d'accès à WorldBody brut comme entrée cognitive. Auditeur indépendant `audit_spatial_visible_cues` : identité temporelle, unicité de la source, schéma, coordonnées et direction adjacentes. Tests adversariaux avec chaîne SHA recalculée après altération ou effacement des cues.
4. Première [campagne CI #38484520946](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38484520946) sur SHA `763e8bf8`, **FAILURE dans l'agrégateur** : quatre vies ont bien effectué 50 pas chacune et leurs WAL/JSONL ont été conservés. La cause était une supposition incorrecte selon laquelle toute commande `se_deplacer` devait avoir un reçu GA complet d'adjacence. Certaines perceptions de position normales n'en comportent pas. L'absence d'indice n'est **pas** une revendication `world`, et ne rend pas la transition physique invalide.
5. Correction du reporter `d8eff61667d5e250b8b395febaaa9f2c5dc8abfc` : comptabiliser ces actions dans `east_without_first_person_cue` sans les promouvoir en attribution. [Campagne CI #38484769557](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38484769557) : **SUCCESS Python 3.11 et 3.12**, quatre vies et tous les audits opérateur acceptés.

## Bilan de la campagne autonome (par interpréteur)

| Mesure | Valeur |
| --- | ---: |
| Vies indépendantes nouvellement instanciées et auditées | 4/4 |
| Transitions physiques réellement appliquées | 200/200 |
| Déplacements `se_deplacer` | 144 |
| Pas de sommeil `dormir` | 56 |
| Commandes `se_deplacer` vers l'Est | 112 |
| Est sans preuve perceptive GA d'adjacence | 20 |
| Captures GA d'adjacence vérifiées | 144 |
| Commandes Est face à cellule bloquée *directement perçue* | **0** |
| Commandes Est vers la ressource ou eau adjacente préperçue | **0** |
| Commandes Est orientées vers la cible avec motif `active_goal` | **0** |
| Propositions de plans d'objectif | **0** |
| Critères d'objectif préenregistrés | 0 |
| Préengagements subjectifs GA | 0 |
| Jugements réellement produits `self/world/unknown` | 0 / 0 / 0 |
| Couples attribution/résultat admis puis appliqués | 0 / 0 |
| Vies rejetées par les audits | 0 |

Par condition, les **quatre** vies ont effectué 36 déplacements et 14 sommeils ; elles ont exploré des positions ne correspondant pas à la cellule Est immédiatement adjacente à la cible du départ. Les scénarios « cible libre » versus « cible bloquée » n'ont pas suscité de commande de but observable dans le protocole. On ne peut donc pas affirmer qu'I0 a connu puis attribué une causalité externe à un obstacle. En particulier, les 112 commandes Est sur 200 pas **ne sont pas** 112 tentatives d'atteindre la cible de but au départ.

### Reproductibilité Python 3.11 / 3.12

Comparaison **octet par octet** des quatre journaux canoniques des archives GitHub Actions (les deux Pythons ne sont pas huit vies indépendantes) :

| Monde | SHA-256 canonique, identique en 3.11 et 3.12 |
| --- | --- |
| near_food_blocked | `4109972f4062327334a3af4e77f351488ac19c8e11cec9613973771388be05e5` |
| near_food_free | `66fb3f4799420a5824e538ab3efdea6b8f116a08f731362b637fdc61aeefca4b` |
| near_water_blocked | `d3a997e981b852eff59249ec27870de409a73083f7750593da55eac207b542d3` |
| near_water_free | `67617e3519c60ee5302ae57ec2afc28525e4388e0391fbc3a704a6f1ac48c775` |

Les deux synthèses sont également binaires-identiques. Archives `issue110-option-a-autonomous-py3.11` et `issue110-option-a-autonomous-py3.12` dans le run final, contenant WAL et JSONL pour les quatre vies.

## Ce qui est acquis, ce qui ne l'est pas

- **Logiciel établi (cible limitée) :** la politique de cue spatial peut distinguer source passable et non passable dans une transition WorldBody réelle **commandée par une fixture**, et refuser de faux indices hors but ; les captures légalement accessibles peuvent être journalisées et auditées pour leur cohérence structurelle. La chaîne SHA ne prouve toutefois jamais, à elle seule, la vérité physique externe.
- **Résultat autonome observé :** quatre vies physiquement auditées, mais aucune opportunité `active_goal` dirigée vers la cible. Cette campagne ne confirme pas la production autonome de `world`. Elle ne démontre pas non plus que le mécanisme serait impossible dans toute configuration.
- **Travaux restant nécessaires :** implémenter `spatial_progress_v1` dans le **registre canonique existant** avec intention précommande et résultat perceptif, rattacher la politique spatiale au producteur Action Control (pas d'un second propriétaire), facturer ses nouveaux calculs UC, étendre M-11 current-generation et tests `os._exit`, auditer la jointure complète et la mortalité, puis préenregistrer des vies utilisant une cible réellement planifiée/atteignable. Une politique d'obstacle extérieure ne peut pas être déclarée positive si le seul mouvement bloqué provient d'une commande imposée ou si Action Control l'interdit.
- **Réception :** la spécification GA-SPATIAL-01 reste un **amendement candidat** non fusionné. L'issue #110 est ouverte et Stage12 non réceptionné. Pas de faux `world`, pas de réduction des seuils de biais, Stage9 scientifique NO-GO inchangé.

**Verdict : validation du prérequis logiciel et audit perceptif, expérience autonome de faisabilité négative/inconclusive pour `world`.**
