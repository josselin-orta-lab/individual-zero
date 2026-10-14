# Issue #110 : campagne B, atteignabilité des objectifs alimentaires Stage6

14 octobre 2026. **Préenregistrement antérieur au code :** `f3fd2ee`. **Source exécutée :** `d7ca87dbbb866e9e5039f99bfd48f10437000460`. [GitHub Actions #38543304223](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38543304223) : **PASS Python 3.11 et 3.12**, six vies indépendantes de 36 transitions physiques chacune. Les deux versions exécutent les mêmes six conditions; ne pas doubler l'effectif.

## Cause technique caractérisée

L'étude précédente abaissait les gains alimentaires à 3, 6 ou 12 points alors qu'I0 devait combler un écart important au setpoint. Le planificateur Stage6 recherche le franchissement du seuil `food >= setpoint` dans un horizon inchangé de **trois commandes**. Une cible physiquement visible ne suffit donc pas à rendre ce but atteignable par le simulateur dans cette fenêtre. Il existait un but `eat` actif, mais aucune commande `active_goal` ; les options exploration et sommeil dominaient. La présente expérience n'a **pas** modifié Planning, Competition, les niveaux UC ou le détecteur, mais seulement trois régimes physiques fixés avant naissance, avec gains 30/40/50.

## Résultats des six vies, Python 3.11 (comptes identiques sous 3.12)

| Profil | Condition | Engagements Stage12 | Motifs active_goal | self | world | unknown | Couples appliqués | success / failure appliqués |
|---|---|---:|---:|---:|---:|---:|---:|---|
| restored | libre | 3 | 3 | 2 | 0 | 1 | 1 | 1 / 0 |
| restored | A2 | 3 | 3 | 1 | 1 | 1 | 2 | 1 / 1 |
| replenished | libre | 3 | 3 | 2 | 0 | 1 | 1 | 1 / 0 |
| replenished | A2 | 1 | 1 | 0 | 1 | 0 | 1 | 0 / 1 |
| urgent | libre | 3 | 3 | 2 | 0 | 1 | 1 | 1 / 0 |
| urgent | A2 | 1 | 1 | 0 | 1 | 0 | 1 | 0 / 1 |
| **Total descriptif externe** | **6 vies** | **14** | **14** | **7** | **3** | **4** | **7** | **4 / 3** |

La vraie intervention A2 est fixée t2, phase `after_admission`, retrait t4. Les couples et jugements sont bien propres à chaque naissance. L'évaluateur ne concatène **jamais** ces sept couples dans la fenêtre interne d'une vie. **0/6 vies ont une fenêtre contenant au moins 2 succès et 2 échecs : attribution_bias NON ÉVALUABLE**. Dans les vies libres, la plupart des jugements supplémentaires sont `unknown` ou les couples expirent au sommeil ; aucun `world` supplémentaire n'est imposé par le test.

### Reproductibilité

Les comptes des étapes, jugements et paires sont identiques entre Python 3.11 et 3.12, et les audits locaux passent. **Journaux SHA256 strictement identiques seulement pour restored_free** ; les cinq autres vies produisent des hachages différents, cohérents avec le problème déjà localisé de divergence numérique de valeur TD Stage8 entre interpréteurs. Ne pas déclarer la reproductibilité binaire générale.

### Portée

La réapparition de `active_goal` avec les profils à gain alimentaire suffisant soutient une cause d'inatteignabilité de plan au Stage6, au moins dans ces mondes. Elle ne prouve ni l'absence d'autres facteurs de compétition, ni une erreur normative du planificateur. **Aucune priorité artificielle n'a été accordée à l'objectif et aucun contrôle d'admissibilité n'a été contourné.**

**Statut : PASS logiciel/physique, PARTIAL scientifique.** La densité de couples au sein de la même vie reste insuffisante et le détecteur demeure non calibré. Ne pas prolonger artificiellement cette exploration, ne pas fermer #110, ne pas fusionner #155 et ne pas recevoir Stage12 sans validation opérateur.
