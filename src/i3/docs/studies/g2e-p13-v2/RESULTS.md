# I3 G2e — P1.3 contre P1.1 sur le substrat v2, sous sélection : résultat

**Décision préinscrite : `ADOPT_P1_3`.** Protocole : [G2E_P13_V2_PREREG.md](../../G2E_P13_V2_PREREG.md), commit `31c4429` ; méthode [ADR-0015](../../../../../docs/decisions/ADR-0015-i3-portes-sous-selection.md). Les deux bras utilisent la même physique v2 (cognition financée à l'avance, #1004). Données : `BASE.json`, `P1_3.json`, `g2-*.json`, `reference.json`, [verdict.json](verdict.json).

**Note d'exécution.** Le bras P1.3 a été interrompu une première fois à la fin d'une session, avant d'écrire quoi que ce soit ; il a été relancé du début avec le même code et les mêmes graines ([EXECUTION_NOTE.txt](EXECUTION_NOTE.txt)). C'est l'achèvement de l'exécution unique préinscrite, pas une seconde tentative.

## Critère principal : 5 génomes sélectionnés par bras, 100 mondes réservés neufs par famille

| | Base (P1.1-v2) | P1.3-v2 | Mondes meilleurs / pires |
| --- | --- | --- | --- |
| Révision de stratégie (R), sur 500 | 163 | **270** | 62 / 9 |
| Générale (dev), sur 500 | 201 | 208 | 30 / 20 |
| **Total, sur 1 000** | 364 | **478** | 92 / 29, **p = 4 × 10⁻⁹** |

Planchers remplis : régression G2 identique (10/10 vies boivent dans chacun des trois mondes, pour les deux bras), rejeu exact, **aucun pas en défaut de financement**, mêmes mondes, 1,27 et 1,28 ms par pas (garde-fou : 2 ms).

## Descriptif

| | Base | P1.3-v2 |
| --- | --- | --- |
| Vies où la source proche a été vidée (sélectionnés, R) | 325 | 346 |
| … puis qui ont bu à la source lointaine | 75 (23 %) | **206 (60 %)** |
| Latence de révision, médiane (quartiles), en pas | 124 (96–140) | 134,5 (82–182) |
| Génome aléatoire par monde, survivants R / dev (sur 100) | 21 / 35 | 35 / 39 |
| Part de pas inactifs faute de financement (sélectionnés) | 10,6 % | 7,8 % |
| Survie en sélection des 5 meilleurs candidats (sur 60) | 27, 27, 27, 26, 25 | 33, 32, 32, 31, 30 |

Sondes de laboratoire, **ni validées ni appariées en coût** : le chercheur de référence survit dans 95 mondes R et 70 mondes dev sur 100. Il paie environ 0,07 d'énergie par pas, contre environ 0,55 pour un individu I3 en v2 ; ces chiffres ne sont donc pas un plafond comparable.

## Lecture

La révision des croyances de lieu fait réviser bien plus souvent (60 % contre 23 % des vies dont la source proche a tari), mais **pas plus vite** : parmi les vies qui révisent, la latence médiane est comparable. Le gain en conditions générales est faible (+7 sur 500). Le gain apparaît aussi avec des génomes aléatoires.

En v2, la survie globale est nettement plus basse qu'en v1 : penser coûte réellement, et environ un pas sur dix est perdu faute de pouvoir financer la cognition. C'est l'enjeu de soi que l'ADR-0014 voulait rendre réel ; c'est aussi la raison de laisser la lignée régler la dépense cognitive (gènes `n_base`, `h_max`, `m_max`) plutôt que de l'ajuster à la main.

Limites : génomes de génération 0 choisis parmi 40, sans lignée ; deux familles générées par le laboratoire ; aucune affirmation d'apprentissage au sens scientifique du projet.

## Conséquences

- La cognition de référence devient **P1.3-v2** (génome `i3-genome-v3`, gène `belief_rate`).
- Suite du plan #1002 : P2 (valider générateurs et sondes, appariement des coûts, séparation développement / sélection / validation / réservé), puis P3 (pilote de lignée).
