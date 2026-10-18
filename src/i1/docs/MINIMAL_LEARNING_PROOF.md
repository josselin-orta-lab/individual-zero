# I1 : protocole prioritaire, apprendre dans un environnement élémentaire

## Question unique

Sans sommeil optimisé ni toxine ni itinéraire complexe, un I1 naïf peut-il **essayer, comprendre une conséquence réellement vécue, utiliser cette information au prochain choix et survivre** ?

## Environnement

`learning-cell` : 1 cellule accessible entourée d'obstacles, eau sur la cellule de naissance, 100 baies de chaque type côte à côte, aucune créature ou zone dangereuse, intégrité initiale 100. Faim initiale 35 et eau 65, avec métabolisme et mortalité normaux. Ni action forcée ni savoir préalable sur l'effet des baies. C'est un test de politique alimentaire et d'expérience, **pas** un test de navigation. Physiquement, une baie apporte +10 de nourriture, l'autre 0 ; une seconde configuration inverse les deux rôles. Aucune baie toxique : toxicité 0 pour les deux, pour isoler l'apprentissage de valeur alimentaire. Les deux mondes apparaissent identiques à l'individu avant toute expérience ; seule la physique opérateur diffère.

## Témoins et appariement

Mêmes graines 246–250 et mêmes positions/corps initial, nouvelles naissances indépendantes dans quatre bras : A nourricière / TD lisible, A nourricière / valeurs TD masquées, B nourricière / TD lisible, B nourricière / valeurs TD masquées. **20 vies**, jusqu'à 200 pas ou décès. Le contrôle ne supprime PAS la perception, l'expérience, les mises à jour, la mémoire physique, les besoins ou Action Control : il masque la lecture `LinearTDValues.learned_value` dans le processus témoin dès avant la naissance ; les mises à jour continuent à être enregistrées. Il s'agit d'une ablation globale des lectures TD ; une différence entre les bras ne démontre pas, à elle seule, le rôle spécifique de la consolidation nocturne.

## Hypothèses vérifiables

1. **Essayer :** au moins une collecte/ingestion réellement choisie dans chaque classe de ressources, avant qu'I1 ait appris les effets ; sinon `BLOCKED_EXPLORATION_OR_AFFORDANCE`, pas un échec intellectuel déduit.
2. **Comprendre :** récompense et transition physique signées correctement à l'action effectivement exécutée, la valeur TD évolue dans un sens compatible et dépend de l'identité de la baie ; si l'attribution est ambiguë, `NOT_ESTABLISHED`.
3. **Réutiliser :** dans la seconde moitié de la vie, l'agent TD lisible choisit plus souvent la baie favorable que le témoin TD masqué, à opportunités comparables. L'inversion du monde doit **inverser la préférence** ; une préférence `berry_a` persistante dans les deux mondes ne prouve pas l'apprentissage.
4. **Survivre :** mortalité et durée jusqu'à l'horizon 200, nourriture/eau/énergie et intégrité, actions utiles et sommeil. Les morts restent dans le dénominateur ; la vie censurée à 200 n'est pas immortelle.

Les journaux WAL, commandes et transitions physiques doivent fournir la preuve avant/après. Les événements `td_update_published` sont nécessaires mais non suffisants. **GO scientifique uniquement si 1–4 sont effectivement observés sur plusieurs graines avec effet net ; sinon NO-GO (défaut) ou INCONCLUSIVE (exposition/puissance insuffisantes).** Le programme ne doit jamais fabriquer de courbe d'apprentissage à partir du nombre de souvenirs.

## Limites préenregistrées

Cinq graines seulement et un environnement géométrique fixe ne permettent pas de généraliser. Les bras peuvent ne jamais manger les deux baies, le sommeil peut l'emporter, les identifiants d'options peuvent empêcher la sélection, les bénéfices peuvent être trop faibles pour générer une divergence; ces cas constituent des diagnostics et non des preuves artificielles. L'ablation masque les lectures de toute signature TD et conserve les écritures; c'est un témoin d'utilité générale de l'apprentissage TD et **pas** un contrôle isolé de la consolidation. Le modèle est I1, I0 inchangé, mort définitive, aucune fusion avant revue.

Actions : [workflow I1 minimal learning causal proof](https://github.com/josselin-orta-lab/individual-zero/actions/workflows/i1-minimal-learning-proof.yml), PR #303.
