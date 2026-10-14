# Issue #110 Option A : préenregistrement de corpus physiquement situé, avant nouvelle expérimentation

Date : 14 octobre 2026. **Fixé avant tout code du nouveau runner et avant son exécution**. Continuation distincte du [run #38486482616](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38486482616) (4 vies, 200 pas, zéro option de but et zéro critère spatial malgré activation logicielle réussie). Le nouveau protocole ne modifie aucun résultat historique.

## Cause candidate

L'Equipment exact physique pré-natal des vies antérieures enregistrait des transitions nord, sud, collecte puis ingestion d'une baie **sur la case initiale (2,2)**. Les vies de faisabilité étaient nées avec ressource ou eau adjacente en (3,2). Le modèle n'était donc pas démontré capable de simuler leur approche. Ceci est une hypothèse explicative, pas une preuve universelle.

## H1-H3

H1 : un nouveau corpus d'entraînement sur WorldBody externe avant naissance, dans une disposition de ressource/eau **adjacente perçue**, peut rendre le chemin Stage 6 `se_deplacer est -> collecter -> manger` (nourriture) ou `se_deplacer est -> boire` (eau) simulable et sélectionner spontanément une commande dirigée vers le but dans un monde libre. Ne pas garantir que la décision sera choisie.

H2 : si l'agent exécute réellement un mouvement correspondant à une cible perçue, le préenregistrement spatial doit posséder son propre coût UC, être vérifié à t+1 depuis la nouvelle position, et Action Control doit produire `self/world/unknown` seulement à partir de la copie efférente et de l'indice de passabilité perçu avant l'action. Aucun label du résultat n'est fourni au jugement.

H3 : dans la configuration bloquée (obstacle sur l'Est), une éventuelle commande spontanée réellement admise vers la cellule bloquée pourrait produire un `world`, mais l'absence de cette commande est un résultat nul. Il est interdit d'injecter une commande ou de requalifier une erreur de prédiction P-47 en responsabilité extérieure.

## Configurations fixées

Quatre vies neuves, 50 pas physiques maximum chacune : `near_food_free`, `near_food_blocked`, `near_water_free`, `near_water_blocked`. Individu (2,2), cible Est (3,2), même configuration physique 32x32, quantité baie=2, `food=35` pour les vies nourriture, `water=70` pour éviter la soif concurrente ; vies eau : `water=20`, `food=70` pour éviter la faim concurrente. Aucune action commandée depuis le laboratoire dans les vies nées.

**Corpus externalisé**, créé par vraies transitions WorldBody d'un monde d'entraînement **libre** et construit avant chaque naissance, sans Oracle ni Bench. Nourriture : Est → collecter berry_a → manger berry_a ; eau : Est → boire. Enregistrer familles, versions et empreinte Equipment. Les lignes d'entraînement sont issues de l'environnement externe, **pas un apprentissage d'I0 pendant sa vie**. Pour les mondes bloqués, utiliser le **même corpus libre du même type de besoin**, sans injecter l'obstacle ou son effet comme étiquette cognitive.

Conserver `h_eff=3`, mêmes coûts UC et diagnostics que l'étude activée précédente (`spatial_goal_progress=True`, `spatial_goal_cost_uc=1`, `spatial_agency_cost_uc=1`, GoalAgency et jointure UC=1). Le sommeil reste autorisé, seuils `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75` inchangés. Python 3.11 et 3.12 sont un contrôle déterministe, **pas huit vies statistiques**.

## Mesures et conditions d'arrêt

Avant consultation des résultats : pas réellement appliqués, intents pris ou refusés, planification Stage6, mouvements Est vers cibles préperçues, passabilité antérieure et absence/presence d'obstacle, résultats spatiaux/corporels `success/failure/unknown`, jugements cognitifs `self/world/unknown/unavailable`, coûts UC acceptés/refusés, couples admis/appliqués/expirés, audits indépendants WAL/JSONL, mortalité. Conserver les résultats négatifs et les données de chaque vie. Refuser tout journal incohérent, coût gratuit, preuve de passabilité manquante, label hors-fenêtre, confusion entre perception et vérité extérieure.

Même si plusieurs `self` sont obtenus, un détecteur `attribution_bias=None` reste correct sans deux références indépendantes de chaque classe de résultat et jugements pertinents. Le niveau scientifique final n'est pas évalué ici. Aucune modification normative historique, aucun merge, Stage 12 non réceptionné, issue #110 ouverte et Stage 9 NO-GO.
