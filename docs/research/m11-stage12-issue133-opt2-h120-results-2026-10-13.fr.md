# M11 OPT2 : résultat indépendant H120 et décision scientifique

**13 octobre 2026.** Protocole préenregistré avant le run : `docs/research/m11-stage12-issue133-opt2-h120-prereg-2026-10-13.fr.md` (commit `72fb8d5281c273e4a03acb533860c6885fd51d93`). Code de vie OPT2 figé `8b68107cd5b7ea01420593c2f2db937a4c0f3321`. [GitHub Actions #38422296819](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38422296819) : **SUCCESS** Python 3.11 et 3.12. ZIP bruts `11826629929` (3.11), `11828100186` (3.12).

## Audit indépendant hors I0

Le lecteur Python externe a inspecté quatre archives ZIP (OPT1 H120 et OPT2 H120), sans importer I0, Oracle ou Bench. Pour chaque cas : SHA-256 recalculé événement par événement, sérialisation JSONL canonique, index et hash des occurrences SQL identiques à l'export pour les 14 397 événements H120, `PRAGMA integrity_check=ok`, empreinte des `state_bytes` valide, intention pendante absente et génération **121** retrouvée. Chaque vie a 120 pas, 59 épisodes clos, 57 consolidés sans doublon, 12 publications `h` et leurs 12 reçus de maintenance et 12 retraits, 72 passes, taille SQLite **17 956 864 octets**.

SHA-256 H120 du journal dans les quatre archives : `8b73d539a39fa6b7bf7583652a5f51e4a0427f9c0d203f015190d4641a648f82`. SHA-256 de l'export : `fa94b0312cc41ae07775fa8590bf5d26553ed34e243eee0db35f96d17e00719c`. **Aucune divergence causale constatée.**

## Performance mesurée, comparaison aux runners indépendants

| H120 non profilé | OPT1 | OPT2 | OPT2 vs OPT1 |
| --- | ---: | ---: | ---: |
| Python 3.11 | 141,983 secondes | **209,178 secondes** | **+47,33 %** plus lent |
| Python 3.12 | 135,048 secondes | **223,606 secondes** | **+65,58 %** plus lent |

Ces résultats sont **défavorables à OPT2** malgré les gains H30 sous cProfile (OPT1→OPT2 : 51,716→43,601s en Python 3.11 ; 50,641→27,808s en Python 3.12). Les profils sont enregistrés par cProfile et les runs H120 utilisent des machines GitHub différentes à des heures différentes ; les temps de ces comparaisons ne permettent **ni** de conclure que OPT2 accélère intrinsèquement **ni** de prouver qu'OPT2 ralentit intrinsèquement. Ils prouvent que le **critère préenregistré « gain non négatif dans les deux observations H120 » est NON SATISFAIT**.

## Décision

- **PASS : intégrité technique ciblée** de l'encodage, du journal et de la génération courante SQLite. Les tests de crashs réels, corruption historique et parité de l'ancien WAL sont SUCCESS aux SHA testés.
- **NO-GO : promotion de l'optimisation OPT2 au titre de la performance H120.** Les résultats défavorables sont conservés, sans changer le critère après coup. OPT2 reste dans la **PR #141 DRAFT**, non fusionnée ; PR #140 DRAFT et #139 OPEN inchangées.
- **Pas de H600 automatique** et aucun changement des politiques de sommeil/consolidation, `w_C=0`, limites P-42 (100/600), P-43, mortalité ou MVP v1.3.1.
- Prochaine investigation possible : benchmark A/B apparié sur une même famille de runners, répété et contrôlé, ainsi qu'un profilage précis du coût de `JournalEntry`, `_normalize` et des audits selon l'âge du journal. Ne pas supprimer les vérifications complètes ni restaurer une ancienne génération pour améliorer le temps.

Artefact d'audit local pour l'opérateur : `m11_opt2_h120_audit_2026-10-13.json`.
