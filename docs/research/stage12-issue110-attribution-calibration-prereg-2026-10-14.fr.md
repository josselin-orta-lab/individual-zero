# Issue #110 : campagne exploratoire de calibration du détecteur d'attribution (14 octobre 2026)

**Préenregistrement avant code de la nouvelle campagne.** Statut exploratoire, sans validation scientifique implicite.

## Question et verrou précis

L'implémentation inchangée `Stage12LivedDetectors` utilise exactement `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`. Elle ne calcule `attribution_bias` que si **au moins deux couples vérifiés success et deux failure** ont été consommés **dans la même vie et la même fenêtre de 12 observations éveillées**. Chaque couple demande un objectif réellement pré-engagé, une commande réellement admise et appliquée, une mesure Metacognition et une interprétation Action Control fondée sur perception légitime, puis une consommation au pas physique suivant. Le nombre total de pas ni l'agrégation entre individus ne remplace ces critères.

## Deux niveaux d'expérience

**Exploration de faisabilité** : quatre variantes physiques de la vie alimentaire A2, construites avant naissance, 16 pas (ou arrêt mortel) : libre sans intervention, obstacle persistant à t=2 après admission, obstacle t=2 après admission avec retrait à t=3 avant perception, obstacle t=2 après admission avec retrait à t=4 avant perception. Une variante contrôle mouvement bloqué sans nouvel obstacle peut être ajoutée après l'exploration et sera alors qualifiée **post-hoc**, non confirmatoire. Aucune commande ne sera imposée ni réécrite et aucune observation cachée ne sera transmise à I0. Les conditions du planificateur et les paramètres du détecteur sont inchangés. Les programmes du monde doivent rester définis à naissance.

**Calibration intégrée indépendante** : si l'exploration trouve plusieurs couples dans la fenêtre (dont >=2 de chaque classe) avec une cause environnementale fixée avant naissance et réellement observée, répéter les mêmes conditions dans des vies **nouvelles**, avec identités uniques et journaux WAL et ancres SHA. Distinguer délibérément données de choix de scénario (développement) et preuve scientifique hors échantillon (validation). Si aucun essai ne fournit la couverture, déclarer le résultat **NON-ÉVALUABLE** et ouvrir explicitement le verrou architectural scientifique; ne pas abaisser les seuils pour inventer une calibration.

## Métriques et contrôle épistémique

Pour chaque pas: source motrice, position et direction réellement commandées, cible adjacente réellement perceptible, sous-critère de but préengagé, résultat `success/failure/unknown`, agence `self/world/unknown/unavailable`, paires admises puis consommées, diagnostics (observations et comptes positifs/négatifs), interventions externes et leur phase, sommeil et UC. Les fichiers JSONL, WAL, provenance et empreintes sont exigés.

Calculer l'indicateur de « couverture 2+2 dans fenêtre » indépendamment sur les journaux, puis confronter exactement les valeurs annoncées par `Stage12LivedDetectors` aux vérifications de l'auditeur de paires. Contre-exemples : geste qui échoue sans apparition d'obstacle, obstacle préexistant exclu par Stage6, événement externe hors trajectoire, absence d'intention, sommeil, duplicate pair et falsifications rechaînées. Ne jamais fusionner des fenêtres inter-vies.

**Important : `self_serving_pattern` est une différence descriptive P(self|success) - P(self|failure), pas un constat de biais psychologique.** Un individu qui se juge correctement causalement responsable du succès et qui reconnaît correctement une contrainte extérieure derrière un échec produira le même motif. Une conclusion de « biais cognitif » nécessite une comparaison causale indépendante, sans fuite vers I0, et des vrais négatifs.

## Arrêt et critères

Ne pas prolonger arbitrairement au-delà de 16 pas exploratoires si aucun engagement répété ne se produit et si le verrou est déjà apparent. L'intégration A2 ancienne de quatre vies / 200 pas et un `world` est une hypothèse exploratoire de fonctionnement du jugement, non une calibration du biais. Toute évolution de norme v1.3.1 reste soumise à l'opérateur. PR #155 et issue #110 restent ouvertes, Stage12 pas reçu, Stage9 NO-GO.
