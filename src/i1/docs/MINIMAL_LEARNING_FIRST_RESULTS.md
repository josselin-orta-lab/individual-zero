# I1 : résultats intermédiaires du laboratoire minimal, 18 octobre 2026

## État et provenance

Première série : [Actions #39121970996](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39121970996), SHA physique **1e2b861a46438d2778f6af9ee52b3110feab64da**. 4/4 jobs PASS, 20/20 vies actives et censurées à l'horizon 200, 4 000 pas physiques. Les quatre archives WAL ont été relues indépendamment, chaînes continues et têtes égales aux rapports; aucune mort occultée. CI de la première instrumentation validée au commit 36df882 (#39122057097).

## Résultats (5 graines appariées par monde/bras)

| Monde | Q_active consultable | Manger nourricière | Manger neutre | Parts sommeil | Vies avec nourriture à 0 au pas 200 |
|---|---|---:|---:|---:|---:|
| A nourrit | Oui | 13 | 18 | 41.8 % | 3/5 |
| A nourrit | Non, lecture masquée | 22 | 34 | 77.6 % | 0/5 |
| B nourrit | Oui | 31 | 3 | 59.9 % | 0/5 |
| B nourrit | Non, lecture masquée | 17 | 21 | 83.5 % | 0/5 |

Il existe des essais réels, des effets corporels et des mises à jour TD. L'agent **n'apprend pas robustement quelle baie nourrit** lorsque le rôle alimentaire est inversé : dans le monde A nourricier, certaines vies avec Q actif continuent de privilégier B (neutre), et trois atteignent nourriture et eau nulles. Leur intégrité est encore positive au pas 200, donc elles sont **censurées, pas durablement survivantes**.

## Biais établi

Dans les quatre conditions, des premières propositions favorisent la collecte de B ; apprendre la valeur de la **collecte** ne prouve pas la valeur de la **consommation**. Les TD `collecter berry_b` reçoivent initialement une récompense homeostatique positive, y compris quand B ne nourrit pas, notamment parce que l'énergie initiale de 70 dépasse le setpoint 50 et que le premier mouvement énergétique vers ce niveau réduit la distance. La balance de sommeil varie également fortement entre bras TD actif/masqué, ce qui complique l'attribution. Le témoin masque la lecture générale de Q et pas exclusivement la valeur des baies.

**Verdict A/B : NO-GO à une preuve générale d'apprentissage causal ;** les 20 vies démontrent des capacités partielles, pas une amélioration robuste lorsque la récompense est inversée.

## Nouvelle série plus élémentaire

[Workflow one-resource](https://github.com/josselin-orta-lab/individual-zero/actions/workflows/i1-one-resource-learning.yml), campagne de **32 nouvelles vies**, monde `learning-cell-one`. Une seule baie A physiquement accessible, eau sur le point de naissance et quatre sorties bloquées; l'énergie initiale est **50**, égale au setpoint, pour retirer le biais initial d'énergie. Test deux effets alimentaires réellement cachés pour le nouveau-né (0 ou +10) x valeur Q lisible ou lecture masquée x **8 graines** (301–308). Trois pressions cognitives de sommeil fixées à zéro **uniquement à la naissance dans cette expérience**, sommeil physique/énergie et mortalité conservés. Aucun ordre de consommation, aucun savoir injecté. Horizon 300 ; WALs distinctes ; nouveau commit différent de la série A/B.

**Règles de conclusion :** alimentation réelle, valeur corporelle après ingestion, changement de Q, réutilisation volontaire à la prochaine occasion, survie avec eau/nourriture sur plusieurs naissances. Si aucun effet causal malgré ce monde simple, diagnostiquer modèle, évaluation, seuil Competition et attribution TD avant toute optimisation de sommeil. La série 32 vies mesure l'effet nutritif, mais sans choix alternatif n'est pas suffisante à elle seule pour une preuve de sélection alimentaire comparative. Elle doit être suivie d'une inversion A/B corrigée.

I0 et main inchangés. Mort définitive, pas de rollback. Les anciens résultats restent séparés par SHA.
