# Issue #110, GA-08 : étude prospective de retour au site perçu, après campagne nulle

**Date de préenregistrement : 14 octobre 2026.** Ce protocole est créé **avant le runner et toute exécution** de ces nouvelles vies. La campagne précédente #38481590904 a été conservée sans changement : 6/6 vies auditées, 300 pas par interpréteur, 0 plan et 0 sous-critère spatial, 0 `world`. Cet échec avait déjà révélé que le modèle Equipment exact sur deux transitions `east→boire` n'était pas accessible après la première exploration autonome. Ne pas effacer ni fusionner les séries.

## Raison historique préexistante

Les campagnes indépendantes #132 et #151/#152 ont montré **avant GA-08** qu'I0 explore spontanément vers le nord au premier pas, puis, lorsqu'un objectif est actif, le corpus physiquement entraîné `north→south→boire` ou `north→south→collecter→manger` peut réellement fournir un plan et exécuter la commande **de retour** vers le site (2,2). Ce site est alors **adjacent et directement perceptible** au pas précédant le retour. La politique GA-08 peut enregistrer la distance au site sans recevoir un oracle ni imposer une action. L'étude compare la disponibilité de ce mécanisme à la politique corporelle déjà éprouvée. Elle ne cherche pas à construire artificiellement `world`.

## Protocole gelé avant code

**Quatre vies neuves et distinctes**, 2 types de buts (`water` / `food`) × 2 politiques de naissance (`GA08 spatial activé` / `GA08 spatial désactivé, contrôle corporel`). Toutes commencent au site (2,2), dans un monde libre avec **ressource au site d'origine** :
- `water`: eau accessible en (2,2), initial_body du Stage11 de référence, `water=20` seulement modifiée ; Equipment pré-natal indépendant enregistré physiquement `north, south, boire` et horizon Stage6 `h_eff=2`, comme #132.
- `food`: baie `berry_a:2` et eau en (2,2), `food=35`, `water=70`, `berry_a.food_gain=30`, `integrity_delta=0` ; corpus physique `north,south,collecter,manger`, horizon Stage6 `h_eff=3, h_max=3, max_depth=3`, comme #152.
- Profil sommeil de développement `consolidation_weight=0`, par ailleurs inchangé. Exploration géographique standard **activée** ; aucune suppression des options de sommeil.
- GA-01..GA-07 : jugement subjectif activé, coût UC d'Action Control 1, jointure 1, diagnostic 1, occupation 1, `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`. GA-08 optionnelle ajoute **1 UC** au diagnostic versionné lorsque activée. Pas d'allègement de seuil ni changement mid-life.
- Au plus **50 transitions physiques réellement appliquées** par individu. La graine/configuration sont déterministes. CPython 3.11 et 3.12 ne constituent pas deux expériences statistiques nouvelles : comparaison d'identité technique seulement. Tous les outils de jugement et résultat du laboratoire sont externes et **non réinjectés dans I0**.
- Le banc n'impose aucune commande et ne substitue pas la planification ; l'Equipment hors-vie n'est pas présenté comme apprentissage autonome.

## Prédictions avant expérience

**H1** : dans au moins une vie GA08 activée, I0 pourrait choisir librement une commande `se_deplacer south` dirigée vers le site perceptible et motivée par le but actif, créer un critère `spatial_progress_v1` avant la physique, puis constater la distance 1→0 au pas suivant. Ce critère **ne vaut ni consommation complète ni réussite globale de but**.

**H2** : Action Control pourrait formuler `self` par mouvement volontaire perçu **indépendamment** du calcul de réduction de distance ; un couple spatial `(success,self)` peut être joint/appliqué seulement au pas éveillé autorisé et à prix UC réel. Si la même action avec GA08 désactivé crée un non-gain corporel, il doit rester `failure/unknown`, et **ne pas** être requalifié a posteriori.

**H3** : la non-exécution autonome de l'action, la perte du plan, une veille refusée ou un UC non disponible donnent zéro sous-critère ou `unknown`, pas une réussite fabriquée. L'absence de `world` reste le verdict attendu pour les **mondes libres** ; ce protocole ne valide pas une attribution extérieure.

**H4** : chaque journal, WAL et génération M-11 restent sans duplication ; le vérificateur extérieur doit refuser des journaux rechaînés falsifiant cible, direction, passabilité ou débit UC.

## Mesures

Par vie et par interpréteur : plan Stage6 produit, buts actifs, commande réelle, nombre de pas et d'observations de la ressource, intentions de corps et d'espace séparées, résultats `success/failure/unknown`, jugements `self/world/unknown/unavailable`, couples admis/appliqués/expirés, coûts UC, captures d'obstacle et de position, état de vie, digest Equipment, digest JSONL et audit externe. Sauvegarder **tous** les essais, y compris négatifs. Une campagne positive ne valide pas les catégories `world` ni les sorties statistiques du détecteur sur plusieurs classes.

**Critère d'arrêt :** 50 transitions ou mort/arrêt technique par vie, sans allonger les vies pour obtenir une réussite. **Réception opérateur requise** pour Stage12 ; aucune fermeture #110 ni fusion des PR par ce protocole.
