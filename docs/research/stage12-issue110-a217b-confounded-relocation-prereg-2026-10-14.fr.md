# Stage12 issue #110 : A2.17b, attribution subjective sous déplacement confondu

**Préenregistré le 14 octobre 2026 avant tout code A2.17b.** Base main `ecfbf96b90aa2195dec4806815f2f1cc24d28143`. Stage12 PARTIAL, issue #110 ouverte, aucune réception opérateur, norme v1.3.1 inchangée.

## Question

A2.17a a montré que le véritable service de première personne attribue `self` à un déplacement vers une ressource vue, `world` à un obstacle nouvellement perceptible, et `unknown` à un échec sans indice de cause. Cette observation peut-elle être fausse du point de vue physique **tout en étant cohérente pour I0** ? Il faut éviter de convertir la localisation externe en connaissance causale interne.

## Hypothèses, matrice prospective, témoins

H1 : une commande volontaire de déplacement exécutée librement et aboutissant à la cellule visée produit un jugement subjectif `self`, justifié par son indice efférent/perceptif, sans preuve absolue de causalité.

H2 : une commande volontaire **physiquement inhibée** sans nouvel obstacle, sans changement de cellule et sans indice perceptif supplémentaire, doit conduire à `unknown`, sans inférer automatiquement la responsabilité du monde.

H3 : la même commande inhibée, suivie d'une **relocalisation extérieure du corps au même emplacement visé avant la capture suivante**, peut produire **le même état de perception accessible que H1** et la même attribution `self`, malgré un mécanisme causal extérieur différent. L'évaluateur, et lui seul, doit identifier cette fausse attribution, sans informer I0.

**8 seeds spatiales fixes 81–88**, trois mondes `WorldBody` indépendamment créés par seed, tous appariés sur configuration, corps, ressources et coordonnées initiales : `normal_move`, `forced_failure`, `forced_failure_external_relocation`, soit **24 mondes physiques**, **24 commandes volontaires réellement soumises à `WorldBody.apply`**, et **8 événements de relocalisation externe**. La ressource hydrique à l'est est dans le voisinage cardinal réellement perçu ; aucune vue à distance non locale. Les engagements d'agence sont préenregistrés à t1 par `GoalAgencyService`, les jugements payés avec véritable capture à t2 ; le modèle n'accède ni à `effects.movement`, ni à `scenario_forced_failure`, ni à `set_position`.

## Critères fixés avant l'expérience

- **T1** : 24 captures antérieures et postérieures ainsi que 24 commandes et 8 relocalisations physiques externes attestées avec SHA ; 8/8 positions finales du cas déplacé de l'extérieur identiques à celles des mouvements réussis. Le cas sans relocalisation reste à sa case d'origine.
- **T2** : pour chaque seed, **captations accessibles avant et après strictement identiques** entre `normal_move` et `forced_failure_external_relocation`. Sans égalité perceptive, H3 est INCONCLUSIVE ; ne pas prétendre démontrer la confondabilité.
- **T3** : jugements `self/unknown/self` dans les trois conditions, et aucun `world` artificiel ; les huit `self` associés aux relocalisations externes sont signalés comme *attributions subjectives physiquement erronées* par le seul banc. Ne pas les convertir en preuve d'une erreur générale de cognition ou d'omniscience cachée.
- **T4** : ne jamais injecter la vérité de l'intervention dans `GoalAgencyService`, dans S_t ou dans les paires du Stage12. Aucun changement de modèle, UC, planification, sécurité, journal, mortalité ou norme v1.3.1.
- **T5** : résultats reproductibles sous Python 3.11 et 3.12. Les seeds sont des variations physiques, **pas 24 vies cognitives autonomes** ni des preuves de calibrabilité 2+2/12.
- **Décision** : H3 confirmée implique de documenter une frontière de non-identifiabilité, pas d'ajouter un correctif ad hoc détectant le déplacement extérieur. Un tel correctif réclamerait des indices réellement perceptibles ou un modèle d'incertitude préenregistré et une campagne multi-seeds de vies autonomes. Un résultat surprenant est conservé.

Stage12 scientifique **PARTIAL** ; issue #110 **OPEN**, réception opérateur requise pour toute clôture.
