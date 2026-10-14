# Stage 12 / issue #110, Option A : identité des vies et reprise transactionnelle des états spatiaux

**Date : 14 octobre 2026. Statut : preuves logicielles ciblées positives, validation scientifique finale non effectuée.**
PR de travail [#155](https://github.com/josselin-orta-lab/individual-zero/pull/155), non fusionnée. Cette investigation reprend les résultats autonomes positifs `(success,self)` et l'absence de tout `world` vérifié du protocole spatial précédent, sans réinterprétation rétrospective de ses journaux.

## 1. Défaut trouvé et correction

L'ancien Stage12 utilisait `individual_id="i0-v1.3.1-stage12-mortal"` pour plusieurs naissances séparées. Or la création déterministe de références `stage12_goal_progress_preregistered`, `stage12_goal_agency_judgement` et `stage12_attribution_pair_admitted` via le journal Stage4 pouvait donc reproduire **le même identifiant d'événement dans deux vies distinctes**. L'audit d'une vie seule restait cohérent, mais un agrégateur multi-vies qui ne prenait que `pair_ref` perdait sa garantie d'unicité globale.

La correction fournit :
- un `birth_life_id` **optionnel, immuable dès la construction Stage12** et validé (identifiant limité à 128 caractères) ; les anciennes fixtures conservent explicitement l'ancienne identité pour éviter un changement silencieux de leurs traces historiques ;
- un domaine de références `Stage4._write` incluant cet identifiant **uniquement pour les naissances opt-in** ; les références de préengagements, de jugements et de couples émis via Stage4 se distinguent donc pour deux naissances réellement différentes ;
- des vies de campagne `run_stage12_issue110_first_planning_state.py` avec identifiant de cohorte explicite : GitHub Actions fournit son run ID et son attempt, partagés entre Python 3.11 et 3.12 pour comparer **le même protocole déterministe** sans ajouter de pseudo-réplication. Une exécution locale scientifique exige `--cohort-id`, unique pour sa cohorte. Les fixtures logicielles ont un marqueur distinct ne valant pas revendication scientifique ;
- un vérificateur strict **hors cognition** `scripts/audit_stage12_issue110_birth_cohort.py` qui vérifie chaque WAL exporté/journal canonique via les auditeurs existants, le SHA-256, les identifiants de vie distincts, la cohérence `life_id` dans les événements cognitifs et l'absence de collision de références entre journaux. Cet outil ne réinjecte rien à I0 et ne constitue pas une preuve causale physique indépendante.

**Limite importante :** les identifiants des événements de Perception et de WorldBody peuvent rester locaux au journal. La garantie nouvelle est celle du **domaine de références cognitives Stage12** chez les naissances opt-in. Aucun audit ne doit prétendre que tous les identifiants de toutes les infrastructures sont globalement uniques. Le marqueur de cohorte fourni par un opérateur doit être géré de façon unique entre essais réellement indépendants.

## 2. Contrat M-11

`M11TransactionalMortal` conserve la compatibilité du fingerprint des vieux runtimes ; les nouvelles naissances avec GA spatial ou identité explicite ajoutent au fingerprint durable leur identifiant d'individu, les options et les coûts UC d'attribution/jointure spatiale. Un runtime fraîchement construit pour la restauration doit posséder **la même identité explicite** que le slot SQLite et les mêmes paramètres cognitifs. Le constructeur rejettera un mauvais nom de vie à la naissance ; la restauration froide rejette une mauvaise fabrique et n'accepte pas un ancien propriétaire mutable comme image.

Test d'intégration `tests/test_stage12_spatial_m11_identity.py` :
1. Deux vies autonomes de même scénario mais identités distinctes exécutent leurs vrais pas WorldBody, produisent des couples `(success,self)` valides et présentent des références cognitives disjointes.
2. Une vie SQLite M11 exécute deux pas réels, laissant une intention `spatial_distance` et un jugement spatial en attente. L'unique génération courante est restaurée à froid, sans rejouer un pas physique ni créer un second propriétaire actif ; au pas 3 les sorties sont auditables.
3. De **vrais sous-processus tués par `os._exit(73)`** avant et après COMMIT SQLite : avant COMMIT, l'intention durable en attente empêche la reprise d'une vie précédente ; après COMMIT, la génération 2 complète peut être reconstruite puis progresser vers la génération 3.
4. Régressions M11 Stage12 déjà existantes et vérifications cognitives historiques.

[Run #38494047774](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38494047774) : **SUCCESS sur Python 3.11 et 3.12** au SHA `9035a588b5efb349834f38033fd698baa9e22e5a`. Nouvelle campagne de vérification M11 au SHA intégrant également le contrôleur de cohorte : exécution spécifique à examiner avant toute certification supplémentaire.

### Vérification finale croisée sur SHA exact

- [Run M11 #38494268696](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38494268696) : **SUCCESS Python 3.11/3.12**, commit `5ac7c8a8504ad0cd692c683cf9144d5640cf041c` ; même test de naissances distinctes, froid, `os._exit` avant/après COMMIT et non-régressions M11.
- [Run de vies #38494268718](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38494268718) : **SUCCESS Python 3.11/3.12**, même SHA, 4/4 vies et 200 pas par interpréteur, 5 propositions d'objectif, 2 intentions spatiales, 3 jugements `self`, 0 `world`, 3 couples admis et 2 appliqués. Le nouvel audit indépendant de cohorte retourne exactement **4 identités de naissance distinctes et 23 références cognitives distinctes** dans chacun des deux interpréteurs, sans collision. La source individuelle est hashée avant toute agrégation ; les deux Pythons partagent le même `cohort_id=gha38494268718a1`.
- Les archives de cette campagne, les deux variantes Python et les rapports de chaque vie sont disponibles depuis GitHub Actions. La comparaison entre interpréteurs est un contrôle de reproductibilité **et non huit individus indépendants**. Les anciens corpus et journaux ne sont pas réécrits. Pas de `world` positif.

## 3. Procédure opérateur minimale

```bash
python -m unittest discover -s tests -p 'test_stage12_spatial_m11_identity.py' -v
python scripts/run_stage12_issue110_first_planning_state.py \
    --output-dir /tmp/i0-issue110-spatial-mytrial \
    --cohort-id operator-trial-20261014-01
python scripts/audit_stage12_issue110_birth_cohort.py \
    --cohort-dir /tmp/i0-issue110-spatial-mytrial
```

Les dossiers contiennent `index.json`, `summary.json`, chaque `life-result.json`, WAL et `canonical.jsonl`. Ne jamais joindre deux journaux indépendants pour en faire l'historique d'un même sujet. L'auditeur refuse toute preuve manquante ou collision. Pour Python 3.11 et 3.12, utiliser **le même cohort-id** pour contrôler le déterminisme ; pour deux essais physiques indépendants, utiliser **deux cohort-id distincts**.

## 4. Limites scientifiques et sécurité

Ces essais démontrent une capacité de restauration atomique **pour les cas testés**, pas toutes les interruptions possibles, les identités mortes de longue durée ni une conformité scientifique générale. Les six points de crash M11 historiques et la campagne globale de 600 pas restent des non-régressions distinctes. Aucun nouvel élément n'apporte de jugement autonome `world` : le planificateur ne propose toujours pas de tentative admissible sur la cellule perçue bloquée dans les mondes expérimentés. **Ne pas forcer cette action**, ne pas traiter un échec de gain comme une cause du monde et ne pas diminuer les seuils de biais.

**Verdict : amélioration du périmètre de preuve et de la robustesse des restaurations, pas réception Stage12.** Issue #110 ouverte, Stage 9 scientifique NO-GO, PR #155 en brouillon, aucune fusion.
