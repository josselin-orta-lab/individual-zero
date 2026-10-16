# A2.33 — Perception, mémoire et continuité décisionnelle chez I1

**Date : 16 octobre 2026. Statut : exploration ciblée, apprentissage adaptatif non démontré.**  
**Protocole préenregistré** : `docs/research/i1-a233-firstperson-continuity-prereg-2026-10-16.en.md` au SHA `9008a2e9f18a0da13bf758d37ae0723a2935c8da`, antérieur au runner `8136eff3cc125586eed1bf97284a005de4eeaab3`. Le premier workflow a échoué avant la première vie car il appelait un nom de script absent. Cette erreur technique a été corrigée au SHA `0b795a1a83d686b96bd2d5ae6289ec5e106eb2ed`, sans modifier les populations ni les seuils. [CI de la campagne, Python 3.11 et 3.12](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38862398914) : les deux jobs ont réussi.

## Population et conservation des preuves

- **32 paires et 64 vies mortelles distinctes**, **232 transitions physiques**, **0 exception**, **0 journal invalide**, **0 assertion explicite de sûreté ou de causalité distale sans preuve** dans les sorties du modèle. 8 morts mortelles cachées sur 8 vies exposées, 0 chez les témoins : elles restent définitives et dans le dénominateur.
- Corpus externe d'apprentissage physiquement exécuté, distinct des vies testées : SHA-256 `e2b3fa7354d51e3859f53cf23889d9c8d42b68fa8655cc4e7b9b9c46652f91f8`. Aucune donnée d'entraînement externe n'a été attribuée à une mémoire vécue.
- Vies et WALs indépendants ; artefacts bruts `lives.jsonl`, `summary.json` et journaux par vie archivés dans la CI pour chaque version Python. Deux répétitions du même programme et des mêmes mondes déterministes constituent une répétabilité logicielle, pas deux réplications scientifiques indépendantes.

## Résultats des quatre axes

| Axe | Résultat physique et première personne | Statut étroit |
|---|---|---|
| CUE | Dans les 8 vies exposées, une créature figure réellement dans la **première capture autorisée** (0/8 contrôles). 8/8 réflexes Stage 3 précèdent le cycle cognitif ordinaire; 0 alerte Stage 11 parce que le réflexe court-circuite le producteur. | **Perception présente ; pas de preuve d'apprentissage.** L'absence d'alerte Stage11 n'est pas une absence de sensation. |
| INJURY | Dans 8/8 vies exposées, une perte d'intégrité non terminale apparaît dans la **deuxième capture** et pas dans les 8 témoins. Les 16 vies comportent une mémoire épisodique fermée et des accès autobiographiques techniques. | **Observation vécue démontrée ; causalité spécifique et adaptation non démontrées.** |
| FAILURE | 8/8 premières collectes exposées échouent physiquement et leur inventaire reste inchangé dans la deuxième capture (0/8 contrôles inchangés). Les deux bras disposent d'une mémoire épisodique fermée. | **Occasion d'apprentissage démontrée ; apprentissage comportemental non démontré.** |
| INDISTINGUISHABLE | La première commande est `se_deplacer` dans les 16 vies, mais 8/8 exposées meurent dans une zone cachée. 0 capture postmortem ; 0 épisode postmortem. | **Indiscernabilité physique attendue ; mortalité non créditée comme erreur de reconnaissance de danger invisible.** |

**Mesures manquantes avant attribution d'apprentissage :** la campagne identifie les captures et un décompte des épisodes fermés, mais ne démontre pas que l'épisode disponible a été effectivement *rappelé*, relié à l'échec ou à la blessure, ni crédité comme cause d'un **changement de décision ultérieur**. La présence d'une mémoire n'implique pas son exploitation par la compétition.

## Distinction entre chaînes causales

1. **Physique → perception :** réussite vérifiée dans INJURY/FAILURE. Le corps blessé et l'inventaire inchangé sont accessibles à la première personne au pas suivant.
2. **Perception → journal autobiographique → épisode :** traces d'accès et d'épisodes fermés présentes, sans preuve encore suffisante d'un contenu autobiographique discriminant complet lié aux événements.
3. **Épisode → rappel / modèle vécu → option / sélection :** non démontré par les mesures exécutées.
4. **Situation mortelle indiscernable :** une vie morte ne reçoit pas sa propre observation de mort. Aucun dispositif de transfert de connaissances entre individus n'est autorisé.

L'absence d'alerte Stage11 en CUE est expliquée par la priorité du **réflexe Stage3** ; celle-ci est distincte d'une lacune perceptive ou d'un dysfonctionnement du modèle factorisé.

## Conclusion et suite

**GO uniquement pour l'étude diagnostique des preuves mémorielles ; NO-GO pour la validation scientifique et l'activation générale du nouveau modèle.** Aucun changement des lois WorldBody, du Stage9/DC-05, des protections Action Control, de la mortalité ou de la branche I0.

La prochaine question falsifiable est : *I1 dispose-t-il d'un épisode autobiographique pertinent et d'une référence de rappel réellement consommée avant sa prochaine décision, et si oui pourquoi le comportement ne change-t-il pas ?* La réponse exige une analyse des événements autorisés et une comparaison contrôlée de la compétition, pas une injection directe de vérités cachées. Une éventuelle évolution architecturale propre à I1 devra être versionnée, facturée en UC, rester expérimentale et faire l'objet d'une nouvelle campagne distincte.
