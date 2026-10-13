# Stage 12 #133 : sélection incrémentale UC et lots multi-épisodes (13 octobre 2026)

**État : correctif expérimental versionné et testé, pas de nouvelle validation scientifique du Stage 12.** Les protocoles prospectifs restent intacts : `stage12-issue133-batch-prereg-2026-10-13.fr.md` et `stage12-issue133-longscan-prereg-2026-10-13.fr.md`. La décision opérateur est toujours **w_C=0 comme référence de développement**. Aucun changement de la spécification MVP v1.3.1 ou des anciennes campagnes.

## Implémentation, sécurité et coûts

- Nouveau propriétaire causal `IncrementalChargedSelection` dans `src/i0/modules/consolidation_incremental_scan.py`, activé **explicitement** par `Stage10Config.incremental_selection=True` en mode six passes. L'ancien chemin et les snapshots existants restent inchangés par défaut.
- Fixe un cut causal, la version `h`, le nombre d'épisodes examinables et le registre de références déjà consolidées **avant** de commencer. Les épisodes arrivant plus tard ne rentrent jamais dans ce lot.
- Chaque tranche est **facturée dans P-42 avant d'inspecter la moindre projection** : `episode_scan` multiplié par le nombre d'épisodes, borné par `step_slot_uc` et `period_capacity_uc`. Son curseur et les projections déjà payées font partie de l'état causal sauvegardable, sans remboursement lors d'un réveil.
- Aucun lot incomplet ne peut être transmis au sélecteur de transaction. Lorsque toutes les tranches sont enregistrées, la sélection reprend **exactement** la politique de priorités originale, sans modifier ses scores ni inventer les résultats du monde.
- Le sélecteur P-42 existant accepte déjà `maximum_episodes>1`. Le profil d'essai utilise 3 et vérifie que les **six passes** s'appliquent à toutes les références du lot avant publication h ; transaction suspendue/reprise et cut demeurent dans leurs propriétaires.
- Test d'un scan en trois périodes UC (3 + 3 + 2 unités pour huit épisodes), avec export/restauration du propriétaire entre périodes, rejet d'une publication anticipée, comparaison exacte au classement d'un scan intégral, et rejets des états invalides.

**Limite à garder visible :** le chargement d'une projection et son classement final restent payés comme scan P-42. La mémoire épisodique enregistre actuellement tous les épisodes ; l'optimisation n'est pas encore un index persistant de coût sous-linéaire. Une vie très longue conserve un coût total O(N), même si le refus immédiat à N>slot UC est évité en répartissant N sur plusieurs pas.

## Essai 1 : lot de 1 versus lot de 3, 80 pas, w_C=0

| Configuration | Vrais pas physiques | Pas dormir | Checkpoints six-passes | Commit h | Références réellement consolidées | Reports UC |
|---|---:|---:|---:|---:|---:|---:|
| Lot 1 | 80 | 22 | 11 | 1 | 1 | 0 |
| Lot 3 | 80 | 22 | 11 | 1 | **2** | 0 |

Deux vies distinctes dans chaque version Python (3.11 et 3.12), résultats identiques. Le premier lot à trois épisodes disposait de **deux épisodes éligibles seulement** au cut ; il n'était pas bloqué à deux par un plafond caché. Le deuxième lot à trois épisodes était en cours à la fin des 80 pas. Ne pas assimiler nombre de passes et nombre d'épisodes consolidés.

## Essai 2 : balayage historique versus incrémental, 240 pas, w_C=0

| Configuration (même budget P-42) | Pas physiques | Dormir | Épisodes créés | Références consolidées | En attente | Publications h | Reports |
|---|---:|---:|---:|---:|---:|---:|---:|
| Balayage entier, `step_slot_uc=100` | 240 | 96 | 119 | 14 | 105 | 5 | **11** |
| Balayage incrémental, `step_slot_uc=100` | 240 | 96 | 119 | **17** | **102** | 6 | **0** |

Les résultats de cette expérience sont identiques entre Python 3.11 et 3.12. Le scan incrémental a réellement traversé le seuil : à une sélection, **100 épisodes facturés lors d'un pas et 3 lors d'un pas ultérieur** pour finir la lecture d'un inventaire gelé de 103 épisodes. Une deuxième sélection a lu 100 puis 13 épisodes pour un inventaire de 113 épisodes. Aucun scan n'a utilisé une projection future ou une UC non débitée.

Contrôle externe des ZIP : archives de chaque vie contenant export canonique + WAL + manifeste, SHA-256 vérifiés, **chaînes causales recalculées événement par événement**, 240 clôtures physiques/vie, six checkpoints par commit h, toutes les références consolidées liées à un lot figé. Aucun échec d'audit, décès, résurrection ou résultat omis. Archives dans [Actions de la PR #138](https://github.com/josselin-orta-lab/individual-zero/pull/138), comparer les jobs `issue133-batch` et `issue133-longscan`.

## Verdict sur l'hypothèse du goulot d'étranglement

- **SUPPORTED, cible logicielle étroite :** la taille du lot limite le nombre d'épisodes publiés ; l'obligation historique de facturer un scan complet dans un **seul** slot UC finit par provoquer des reports. La sélection incrémentale payée traverse ce seuil sans publication partielle.
- **NOT YET SUPPORTED, équilibre mémoire/sommeil à long terme :** malgré l'amélioration, **102 sur 119** épisodes sont encore non consolidés dans la vie de 240 pas, à w_C=0. La nouvelle sélection ne suffit pas à rattraper le taux de création avec seulement six passes séquentielles par transaction. Il faut distinguer le flux de création, le temps réellement dormi, le travail sémantique et la saturation future.
- **INCONCLUSIVE :** effet sur l'utilité cognitive des souvenirs consolidés, mondes/graines indépendants, bornes UC très contraignantes et redémarrage de processus après crash. Le runtime Stage12/M11 n'est pas certifié atomique par cette campagne.

**Décision d'intégration :** garder l'option opt-in et le poids w_C=0 dans les profils du laboratoire tant que les tests adversariaux et l'opérateur n'ont pas validé un déploiement plus large. L'issue #133 demeure ouverte pour l'équilibre durable et les expériences cognitives de consolidation. Les travaux #110, #136, la mortalité, l'Oracle et le statut historique du Stage9 restent distincts.
