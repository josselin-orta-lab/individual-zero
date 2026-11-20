# Stage8-E3A · protocole descriptif en lecture seule des vies originales G2

**Date : 20 novembre 2026. Version candidate antérieure à toute lecture comparative des résultats moteurs de G2.** Étude **FORENSIC / POSTHOC / NO_NEW_LIVES**. Cette nouvelle réduction n'est pas une expérience confirmatoire ; la science Stage8-E2 a déjà échoué sur son critère causal figé : `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`. Aucun résultat de cette étape ne peut modifier ce verdict.

## Sources exactes, pas de nouvelle naissance

[Workflow scientifique déjà clos #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471), protocole `404bdf6c844c048985659d6c4d03827ffb19d878`, moteur `03faff4b9c194a5288b92e394f6a75cbe62cd095`, empreinte de source `e816ff5f5ee679253fc57f6e9ee79d21dff73dd72d6adf3c7f55ba7aa0f3e7f6`. Prendre **exclusivement** les **36 864 vies G2 originales** de l'artefact `14601222013`, le manifeste natif de l'artefact `14601206944`, et la preuve scientifique et les deux réductions indépendantes des artefacts `14601838862` et `14601778656`. Le manifeste G2 doit avoir SHA-256 `61eb74a1f429c2f9189ee13da5c52593776d2b6f9d2b2d8ac41bfdea31a6ba00`, le résultat figé SHA-256 `18ad42a1e68a0a7c1c2390bd397ee90e7872bdf398f0f5bac37d06bbfff8af45`. Les vies G0/G1 ont déjà été intégralement auditées lors de la campagne originale et ne seront pas simulées ou resélectionnées ici.

## Falsificateurs techniques avant réduction

1. Télécharger **l'archive intégrale**, pas un échantillon de gzip. Pour chaque vie, vérifier l'identité native complète, empreinte **des octets gzip** et empreinte **des octets JSON décompressés**, source, génome, World, horizon, manifeste, compte des pas, chaîne de trace corporelle et chaîne de paiements cognitifs avec hash terminal. Refuser un seul fichier manquant, dupliqué, corrompu, étranger ou inconnu.
2. Vérifier exactement **64 populations × 4 bras × 24 génotypes × 3 écologies × 2 répétitions = 36 864** vies, **144 vies par population/bras**. Vérifier l'appariement des 384 WorldSpecs G2, sans partager le flux RNG individuel.
3. Refuser une action originale hors `se_deplacer, collecter, manger, boire, dormir, attendre, physical_inactivity` ; recalculer les compteurs d'actions, boissons, repas et pas sur les **traces originales**. Refuser les heures après la mort, coûts refusés présentés comme payés, dépenses sans phase, financements non apurés ou états corporels hors [0,100].
4. Reconstituer d'abord `mean_steps` par population/bras, et exiger une égalité exacte aux **64 valeurs primaires archivées**. Un nouveau résultat « favorable » découlant d'un décalage d'identité ou de source est un défaut à arrêter, pas un nouveau signal scientifique.

## Observables prédéclarés pour lecture exploratoire

**Unité de description primaire : population (n=64).** L'agrégation commence à `population×arm` (144 vies), avec taux d'actions **par pas réellement vécus**, non par vie ou par population artificiellement dupliquée. Le coût cognitif est ventilé en **énergie / vigilance**, puis en phases **décision / apprentissage** ; le dénominateur est le total des pas vécus. Les cycles, pas simulés, objets mémorisés, replays, mises à jour d'apprentissage et pas avec insuffisance de financement sont également rapportés par pas vécu. Les décès/censures sont rapportés **par vie**, avec causes `zero_food / zero_water / zero_integrity`. Les cinq réserves `energy / food / water / integrity / vigilance` sont rapportées en moyenne d'état de fin de pas, fraction des pas à moins de 10 unités, puis état final par vie. Un descriptif additionnel des actions **pendant les vingt premiers pas observés** réduit l'exposition tardive, mais son dénominateur reste les pas réellement observés : des vies mortes avant 20 pas sont sous-exposées.

Pour **toutes** les variables, conserver les valeurs des quatre bras et les **64 contrastes descriptifs** `(S_sham−M_sham)−(S_swap−M_swap)`, ainsi que `S_swap−S_sham` et `M_swap−M_sham`. Les écologies ne seront pas sélectionnées pour afficher une victoire ; les 33 populations défavorables de Stage8-E2 sont préservées. Aucun seuil favorable, nouvelle p-value, coefficient de médiation ou classement confirmatoire n'est défini.

**Interprétation bornée :** un changement dans les choix moteurs ou la facturation corporelle serait un **phénotype observé associé à la manipulation gamma**, pas une médiation causale isolée. Les moyennes par pas sont affectées par la survie différentielle et les réservoirs finaux par la durée de vie. Les coûts de phase `CognitiveWork` sont des unités de travail du moteur, pas le temps CPU. L'absence de changement ne prouve pas l'absence de mécanisme, notamment pour `gamma3` dont la variation était faible.

## Sortie et arrêt

Un JSON complet par population et bras, accompagné de SHA-256, d'un reçu de relecture de **36 864 gzip** et d'une validation indépendante pure des calculs, sans reproduction de vie. Tout défaut de provenance ou d'identité donne **NO_DESCRIPTIVE_VERDICT** ; les archives restent inchangées. Une erreur d'audit **en lecture seule** peut être diagnostiquée et corrigée sur une nouvelle source documentée, mais aucune naissance/relance Stage8-E2 n'est permise. Réductions non confirmatoires seulement.

La conservation durable des **neuf** archives G0/G1/G2 des trois racines reste une obligation séparée [#1463](https://github.com/josselin-orta-lab/individual-zero/issues/1463).
