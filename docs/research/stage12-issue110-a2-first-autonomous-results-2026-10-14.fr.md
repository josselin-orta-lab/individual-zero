# Issue #110 / A2 : première attribution autonome d'influence extérieure, observations du 14 octobre 2026

**Source figée:** `f036467b2789dad998288bbab3378ec074be2a31`. **CI:** [#38526909703](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38526909703), PASS Python 3.11/3.12. **Préenregistrement antérieur:** `9de2aeb`, `docs/research/stage12-issue110-a2-prereg-2026-10-14.fr.md`. **Statut:** exploratoire, Stage12 NON réceptionné, Stage9 NO-GO, PR #155 non fusionnée.

## Résultats réellement exécutés

Quatre vies autonomes, chacune 50 pas physiques, **200 pas réels au total**. Les deux matrices Python ne doublent pas l'effectif: les quatre SHA256 JSONL sont identiques entre les interpréteurs. La cible externe était fixe, (3,1), intervention au pas 2 dans la phase `after_admission`; aucune commande ou objectif n'a été imposé. Le modèle Equipment exact vient de transitions physiques **hors de l'individu avant naissance**. Les journaux complets et WAL sont conservés comme artefacts CI.

| Vie | Pas | Intentions spatiales observées | Jugements self/world/unknown | Couples admis | Couples appliqués | Intervention après admission |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| Food libre | 50 | 1 | 2 / 0 / 1 | 2 | 1 | non |
| Food obstacle A2 | 50 | 1 | 0 / **1** / 0 | 1 | **1 (failure,world)** | oui, ordre journalisé |
| Water libre | 50 | 0 | 0 / 0 / 0 | 0 | 0 | non |
| Water obstacle A2 | 50 | 0 | 0 / 0 / 0 | 0 | 0 | oui, mais sans engagement de but exploitable |
| **Total** | **200** | **2** | **2 / 1 / 1** | **3** | **2** | 2 interventions fixes |

Le `world` cognitif a été produit par le service Action Control avec son débit UC et sa référence perceptive, non par l'évaluateur. Le registre Metacognition a constaté distinctement l'absence de progression spatiale. L'auditeur des premières personnes a vérifié la cohérence de ces deux reçus, et l'audit des couples a confirmé leur consommation ultérieure. L'ordre `command_experienced < external_input_applied < world_transition_experienced` du pas 2 est observé dans les journaux des deux vies avec intervention. Une assertion d'ordre dans le runner n'est toutefois pas encore un audit causal externe suffisamment adversarial.

Le champ `attribution_bias` reste `null` : les classes vérifiées et la fenêtre de 12 pas ne sont pas suffisamment renseignées pour évaluer un biais. Aucun seuil n'a été modifié (`bias_min_outcomes_each=2`, `threshold=0.75`). **Ne pas transformer le `world=1` en succès du détecteur de biais.**

## Empreintes SHA256 des quatre journaux, identiques sous les deux Python

- Food libre: `f956f99387d8afedb258a6d028ef40e8f7d99187f5ab65376428b5f9f683a107`
- Food obstacle A2: `74e228ca726a82227418f5710157a66acfea2b5515f618d76989b987db7b664c`
- Water libre: `c521e9849d82b2edbf838b443eaf4940f9168a70044162d4b4658864338fb1d7`
- Water obstacle A2: `019ebfee870100f0e71a6fd1b10d46f1eb8a56fe38db8476281e1f106357a845`

## Portée et limites

- Premier positif original d'un jugement `world` en vie autonome, sur une contrainte apparue après une commande préengagée. Ceci soutient une hypothèse d'attribution subjective sensible à un changement perceptif pertinent.
- Ce jugement décrit **l'interprétation d'I0**, non une responsabilité causale absolue. L'intervention physique est explicitement inscrite dans le journal de scénario technique; elle n'a pas été copiée dans son état cognitif.
- Une seule occurrence `world`; pas d'estimation fiable de sensibilité, spécificité, faux `world` ou matrice de confusion multiclasse.
- Les deux vies eau n'ont aucun préengagement de but; leurs zéros sont des non-couvertures, pas des vrais négatifs de classification.
- Les contrastes logiciel « mouvement bloqué sans nouvel obstacle », obstacle antérieur et absence de source perceptive ont des tests, mais une campagne autonome variée et l'audit rechaîné falsifié des événements A2 restent nécessaires.
- Vérifier plus largement le contexte transactionnel du déclenchement `after_admission` lors de crash `os._exit` à cette frontière spécifique; les CI M11 existantes sont passées sur ce SHA mais ne couvrent pas encore explicitement la nouvelle frontière A2.
- La fenêtre du détecteur exige au moins deux résultats de chaque classe; une seule nouvelle paire `(failure,world)` ne suffit pas.

**Verdict:** **PARTIAL**. La condition B de l'issue est maintenant observée dans un scénario physique autonome, sous les limites ci-dessus; les conditions de robustesse scientifique et réception complète restent ouvertes. Aucun changement de la spécification historique v1.3.1; changement normatif candidat uniquement dans la PR.
