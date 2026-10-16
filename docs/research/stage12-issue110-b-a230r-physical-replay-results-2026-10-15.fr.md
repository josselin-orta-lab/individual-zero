# A2.30-R : relecture indépendante de la physique Stage 2 derrière les témoins P

**15 octobre 2026.** R a été **préenregistrée avant code** au commit `6053c92b2cb1f0a5a021898b248f2414c4ddfec6`. Contrairement à Q, qui recalcule des JSON sans réexécuter le monde, R crée de **nouvelles instances détachées `WorldBody`** et applique physiquement les commandes prédéclarées. [CI A2.30-R #38732185501](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38732185501) **SUCCESS Python 3.11 et 3.12**, résultats identiques, code `fcb40ac8bb9fc3e23e1950a9082b780407d8ecf3`.

## Indépendance de l'implémentation de test

`replay_stage12_issue110_b_a230r_physical.py` ne charge **ni le runner P, ni le modèle P, ni Q, ni `EquipmentCorpusRecorder`**. Il reconstitue explicitement `WorldPhysicsConfig` et `WorldLayout` depuis la matrice préenregistrée, compare leurs empreintes originales **avant tout pas**, capture les observations accessibles via `SymbolicPerception` et `state_from_capture`, puis applique les commandes sur les nouveaux mondes avec `WorldBody.apply`. Les configurations cachées servent uniquement à l'expérience externe et ne passent jamais dans un état cognitif I0.

Les paramètres physiques vérifiés incluent les variations de faim, de ressources, les coûts corporels et les zones/effets dangereux invisibles, et les fins anticipées pour les scénarios `lethal_east`, `toxin_100`, `danger_east_40/55` et `danger_here_40/55`. Après une issue létale, l'instance d'essai est figée par `WorldBody.freeze_terminal_state()` et **n'est jamais relancée**.

## Comparaison physique exhaustive à la source P

| Groupe | Mondes techniques rejoués | Pas physiquement appliqués |
|---|---:|---:|
| Entraînement original | 48 | 132 |
| Cas ordinaires hors entraînement | 48 | 132 |
| Risques cachés hors entraînement | 24 | 64 |
| Contexte perceptible ou préfixe inédit | 8 | 24 |
| **Total** | **128** | **352** |

Toutes les captures accessibles avant/après, les commandes, les terminalités et les empreintes SHA-256 des exemples correspondent **exactement** aux archives P : **0 divergence physique, 0 divergence de SHA, 0 continuation après décès**. Les tests négatifs montrent qu'une configuration altérée, une zone cachée changée, une conséquence corporelle falsifiée **même avec SHA recomputé**, une terminalité falsifiée, une commande réécrite ou un scénario latent non autorisé sont rejetés.

**Point de comptabilité scientifique :** R a bien effectué 352 actions physiques **supplémentaires dans des nouveaux mondes techniques**, mais ils rejouent **les 128 scénarios exacts** de P; ils ne créent donc **aucune condition scientifique indépendante** et **aucun I0 autonome**. Ne pas ajouter les 352 pas de R à la cohorte P de 352 comme s'il s'agissait de 704 observations scientifiques indépendantes.

## Frontière épistémique conservée

Cette vérification renforce la fiabilité des traces *relativement aux règles effectives de `WorldBody`* et vérifie le respect du décès terminal. Elle ne valide **pas** la conformité de ces règles au monde naturel, une probabilité calibrée, une extrapolation sûre à des situations nouvelles, ni l'agence subjective. Les labels cachés du laboratoire ne sont jamais présentés comme des sensations d'I0.

**R : PASS technique. A2.30 : PARTIELLE. Intégration dans I0 : NO-GO. Stage12 PARTIAL, #110 OPEN, #189 DRAFT**, aucune modification normative.
