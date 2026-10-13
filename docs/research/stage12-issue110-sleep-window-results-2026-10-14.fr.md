# Stage 12 issue #110 — résultats prospectifs : admission de vrais couples d'attribution et sommeil

**Date : 14 octobre 2026.** Protocole préenregistré avant implémentation : `docs/research/stage12-issue110-sleep-window-prereg-2026-10-14.fr.md`, commit `5d9b68c`. Runner code: `e6b87d9`, workflow : `6cff277f5ca36e4ecfcb6b175daac1e826470555`. Exécution [GitHub Actions #38478166448](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38478166448), **SUCCESS Python 3.11 et 3.12** sur SHA exact `6cff277f5ca36e4ecfcb6b175daac1e826470555`. Les 4 vies sous 3.11 et 3.12 sont le **même protocole déterministe**, pas 8 réplications statistiques.

## 1. Résultats mesurés, pour un interpréteur

| Indicateur | Valeur |
| --- | ---: |
| Vies autonomes nouvelles, validées et auditées | 4/4 |
| Pas physiques réellement appliqués | 200/200 |
| Plans d'objectif produits | 12 |
| Critères d'objectif préenregistrés | 12 |
| Critères vérifiés `success` | 4 |
| Critères vérifiés `failure` | 8 |
| Préengagements d'agence | 12 |
| Jugements cognitifs `self` | 4 |
| Jugements cognitifs `unknown` | 8 |
| Jugements cognitifs `world` | 0 |
| UC de jugement acceptées | 12 |
| Refus UC de jugement | 0 |
| Couples vérifiés et **admis** par Metacognition | 4 |
| UC de jointure acceptées | 4 |
| Couples **effectivement appliqués au détecteur** dans leur fenêtre | **3** |
| Couples expirés pendant le sommeil, sans diagnostic rétroactif | 1 |
| Diagnostics métacognitifs publiés | 193 |
| Diagnostics avec `attribution_bias != None` | **0** |
| Vies rejetées par l'audit externe | 0 |

La chaîne Action Control → résultat vécu → Metacognition → admission du couple → *application ultérieure par un diagnostic effectivement facturé* est désormais démontrée de façon **exploratoire**, à partir de transitions WorldBody réellement appliquées. Chaque vie réalise librement une collecte et une ingestion `berry_a`. `self` est fondé sur le **décrément d'inventaire perçu**, différent du succès de la variable corporelle `food`; il ne prouve aucune responsabilité physique indépendante. Les modèles Equipment ont été préparés sur un WorldBody d'entraînement **hors de l'individu, avant la naissance**. Ce n'est pas un apprentissage autonome du modèle.

## 2. Comparaison prospective des quatre configurations

| P39 fatigue_gain | Stage10 intrinsic_weight | Pas | `se_deplacer` | `dormir` | `collecter` | `manger` | Couples admis | Couples appliqués | Couples expirés |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.7 | 4.0 | 50 | 34 | 14 | 1 | 1 | 1 | **0** | 1 |
| 0.7 | 0.0 | 50 | 48 | 0 | 1 | 1 | 1 | **1** | 0 |
| 0.0 | 4.0 | 50 | 48 | 0 | 1 | 1 | 1 | **1** | 0 |
| 0.0 | 0.0 | 50 | 48 | 0 | 1 | 1 | 1 | **1** | 0 |

L'ablation est appliquée à la naissance et **ne modifie pas** les six phases cognitives, les règles WorldBody, le seuil d'attribution, ni la fenêtre d'admission. Le sommeil peut survenir dans toutes les configurations : cette étude observe qu'il est sélectionné dans la configuration de référence (les deux poids actifs) et non dans les trois autres, **dans ces vies déterministes**, sans généralisation causale/statistique externe. L'individu reste l'unique auteur de chaque choix moteur.

## 3. Vérification inter-interpréteurs, pas de double comptage

Les quatre journaux `canonical.jsonl` ont été comparés directement octet par octet entre les archives Python 3.11 et 3.12. **Quatre identités binaires exactes, synthèses identiques**.

| Configuration | SHA-256 du fichier canonique identique en 3.11 et 3.12 |
| --- | --- |
| fatigue=0.7, intrinsic=4.0 | `a0f003269278b566f27893ffb90e8efc1ecd365a337e16afed3f2354762d3f22` |
| fatigue=0.7, intrinsic=0.0 | `09da626d1f12a49b2e7b59145dda3b9ae81f19717c6ea58a09588906e180db3d` |
| fatigue=0.0, intrinsic=4.0 | `f507af142d6e2829aa30b8ef7c83f08d98e374dca29e3b0a4822f01a6608a048` |
| fatigue=0.0, intrinsic=0.0 | `fe2f9519b567443360fc040d7e687fd2cd553d57def1082acf72aef7cc63243a` |

Les archives originales sont conservées dans le run GitHub, noms `issue110-sleep-window-py3.11` et `issue110-sleep-window-py3.12`, avec WAL, événements, manifestes et audits. L'indépendance de la vérité physique externe **n'est pas établie** uniquement par le hash, et le passage CI ne prouve pas la conformité générale de l'architecture à M-11.

## 4. Verdicts préenregistrés

- **H1, passage effectif dans le détecteur : preuve exploratoire favorable.** Trois couples `(success,self)` différents, issus de trois vies réellement nées et vérifiées, sont admis au diagnostic dans leur fenêtre. Un quatrième est légitimement expiré pendant un pas de sommeil. Aucun rétrodiagnostic.
- **H2, rôle des paramètres de sommeil : différenciation observée sur les quatre contextes fixés.** Ne constitue pas une estimation populationnelle ni une justification pour supprimer le sommeil du MVP.
- **H3, filiation et UC : preuve logicielle/expérimentale ciblée favorable.** Le journal, WAL, reçus d'individu et les cinq auditeurs indépendants acceptent les quatre vies ; coût UC effectivement facturé.
- **Détecteur de biais : toujours NON VALIDÉ scientifiquement.** Les 3 couples appliqués sont de la **même classe** `(success,self)`. Aucun couple `failure,world`, `failure,self` ou `success,world` n'est observé, et aucun jugement cognitif `world` légitime n'existe dans cette politique. Les seuils inchangés `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`, `window=12` impliquent `None`. Ne pas changer le seuil pour obtenir une classe positive.

## 5. Blocage restant pour `world` et prochaine décision

L'actuel contrat de résultats mesure un **gain corporel strict sur un pas** ; ni un non-gain alimentaire ni une discordance de prédiction ne renseignent une influence extérieure spécifique. Perception montre des cellules adjacentes et leur passabilité, mais cela ne suffit pas pour une attribution `world` **pertinente au résultat du but**. L'évolution minimale scientifiquement honnête serait une **intention de sous-objectif spatial préenregistrée** (p. ex. distance jusqu'à une source de ressource déjà perceptible) et un mécanisme Action Control d'obstacle directement perçu **et temporellement pertinent** pour la tentative de déplacement, avec propre provenance. Ce type de critère et son coût de traitement devront être proposés comme modification normative séparée, **pas intégrés furtivement** sous le seul GA-04. L'audit devra démontrer que l'obstacle est perceptible avant ou après la commande, et que le jugement ne lit ni le résultat `success/failure` ni l'état caché du monde.

**Dossier final de cette étape : validation exploratoire positive de la chaîne du jugement `self` jusqu'au diagnostic, aucune preuve suffisante du détecteur statistique, issue #110 ouverte et Stage 12 non réceptionné.** Stage 9 reste NO-GO et PR empilées non fusionnées.
