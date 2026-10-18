# I1 : première intoxication survivable, récompense subjective et réexposition

## Preuves physiques nouvelles, 18 octobre 2026

Matrice [Actions #39120129262](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39120129262), code physique exact `91c2a6b1d325e18b582a09b55b67b3d9efba030b`. Monde `berry-b-first-v1`, trois dispositions 71/72/73, graines 993071/72/73 appariées, curiosité 0.30, fatigue cognitive 0.00. I0 et main inchangés. La toxicité est appliquée uniquement avant chaque naissance, aucune commande manger n'est imposée.

Les groupes -100 et -10 ont terminé techniquement, archives WAL indépendantes auditées. Groupe neutre 0 encore en cours au moment de ce constat; **pas d'estimation finale à trois bras**.

| Variante | Première ingestion | Vies contrôle -100 | Vies -10 | Toutes ingestions -10 | Intégrité après première ingestion -10 |
| --- | ---: | ---: | ---: | --- | ---: |
| 71 | 54 | mort 54 | mort 249 | 54,55 | 82.6 |
| 72 | 39 | mort 39 | mort 242 | 39 | 82.6 |
| 73 | 4 | mort 4 | mort 248 | 4,45,84,85 | 80.0 |

À -100, les trois ingestions spontanées sont mortelles au même pas. À -10, les trois ingestions sont effectivement survivables, et les trois individus disposent de nombreuses occasions personnelles ultérieures de réévaluer berry_b. Tous meurent plus tard; ne pas exclure ces morts.

## Attribution de récompense TD et tempérament

Le modèle courant donne à l'intégrité une pondération **variable dès la naissance**, déterminée par le tempérament. L'évaluateur de récompense `ValueAndNeeds.reward_between` additionne les variations de distance aux setpoints énergie/nourriture/eau/intégrité. L'ingestion donne +5 nourriture, mais inflige -10 intégrité; la variabilité subjective en résulte.

Un audit direct de la WAL vérifie, après chaque ingestion, la récompense calculée depuis les captures et `world_transition_experienced` contre `td_update_published.return_g` au pas suivant lorsque la vie est encore active. Les trois premières récompenses TD sont :
- Variante 71 : **-1.93221** (poids d'intégrité 0.683221 ; tempérament menace -0.633558).
- Variante 72 : **-0.880705** (poids 0.5780705 ; tempérament -0.843859).
- Variante 73 : **+0.002725** (poids 0.5697275 ; tempérament -0.860545).

La troisième expérience, physiquement nuisible, est donc **subjectivement légèrement gratifiante**, ce qui contribue à expliquer ses ingestions répétées. Ce n'est pas un bug de synchronisation de la récompense TD : les retours immédiats reproduisent les calculs de besoins sur ces WAL. **Cela n'établit pas une aversion apprise causalement.**

Une réserve : des mises à jour TD ultérieures continuent à modifier les signatures antérieures via les traces d'éligibilité. Ainsi, une valeur `manger berry_b` peut devenir positive après d'autres actions (par ex. berry_a), même quand la récompense de l'ingestion berry_b était négative. Il faut étudier séparément la diffusion temporelle et l'attribution causale du crédit, pas écraser artificiellement le poids du tempérament.

Nouvelle instrumentation sans modification du moteur : `tools/audit_i1_berry_valence.py`, validée localement contre les 6 WAL -100/-10, relit naissance individuelle, corps perçu, action, physique et retour TD, sans injecter de connaissances. Elle est exécutée dans le workflow modifié pour de **nouvelles** vies, [Actions #39120910356](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39120910356), SHA physique distinct `49cadacf4beadf488c5109ed34b499cd13e075d2`. Les résultats d'anciens et nouveaux commits restent séparés.

## Décision

**CONDITIONAL / apprentissage non démontré.** -10 est une valeur prometteuse comme sensibilité de recherche, car la première erreur devient survivable. Mais certains individus répètent l'erreur, et une survie à long terme est absente. Étape suivante : comparaison neutre 0, analyse des propositions ultérieures avec véritable contexte de besoin, puis ablation expérimentale de la réutilisation du Q après le premier résultat négatif, en gardant moteur canonique/I0 et mort irréversible. Aucune fusion de la PR scientifique dans main à ce stade.
