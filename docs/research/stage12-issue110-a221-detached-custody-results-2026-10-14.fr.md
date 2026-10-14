# Stage12 issue #110 : A2.21, authenticité par garde de source indépendante

**14 octobre 2026. Résultat du code expérimental SHA `2552b6e854c09892093e69d3c3bde65ed67c4c50`.** Préenregistrement `5e5cf93ec0da9aef8ecf9ec18d836d387ac271a3` réalisé avant instrumentation. [CI #38640831492](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38640831492) : **SUCCESS Python 3.11 ET 3.12**. Les deux versions rejouent les mêmes seeds 121–128, elles ne forment pas 16 seeds indépendantes.

## Résultats effectifs

32 mondes physiques distincts, 64 véritables transitions `WorldBody.apply`, 16 déplacements initialement causés par `set_position` après une commande physiquement empêchée, 16 déplacements ultérieurs opérés après la commande réelle `attendre`. Les expériences `normal` et `confounded` appariées sont perceptivement égales t1/t2/t3 malgré des causes distinctes. Le vrai `GoalAgencyService` émet `self` au premier jugement ; 16 révisions candidates `unknown` apparaissent uniquement dans les mondes où un déplacement passif est visible.

**32/32 registres honnêtes acceptés. 192 attaques / 192 refus par la garde source**, exactement 32 pour chacune des six familles préenregistrées : capture falsifiée avec recalcul SHA, jugement d'origine falsifié, substitution entre épisodes, mauvaise identité de vie, capture terminale manquante, permutation temporelle. **128/192 attaques passent pourtant l'audit interne** du candidat, ce qui établit expérimentalement la limite de l'auto-vérification du journal. Aucun label d'intervention extérieure n'entre dans le jugement candidat ; les identifiants subjectifs utilisent un condensat opaque.

Ce sont **192 tentatives d'attaque instrumentées**, pas 192 vies autonomes ni 192 transitions physiques supplémentaires. L'intégrité de la source scellée est une hypothèse de menace du laboratoire : si l'adversaire réécrit à la fois le registre et sa garde, la preuve ne protège plus. SHA-256 ne garantit jamais seul l'authenticité ; celle-ci exige une provenance indépendante, durable et correctement contrôlée.

## Limites et conclusion

La garde et le candidat sont deux objets séparés dans un banc extérieur, **pas deux propriétaires matériels/systémiques isolés**, pas un WAL indépendant et pas une preuve de résistance à tous les crashs. Les captures ont bien été produites par WorldBody et Perception, mais ce protocole ne crée **aucune vie cognitive autonome**. Aucun vrai coût UC, stockage I0, reprise M-11 ou protection post-mortem n'a été exercé. Aucun entraînement, calibration probabiliste, résultat alimentaire distal ou attribution causale de l'action initiale n'a été prouvé. Ces preuves ne deviennent pas des paires GA-06 du détecteur.

**Statut scientifique : PASS borné des critères physiques, de l'audit et des attaques du laboratoire ; Stage12 PARTIAL, #110 OPEN, réception opérateur non effectuée.** Le MVP normatif v1.3.1, l'Oracle, Stage9/DC-05, ActionControl, WorldBody, UC, Memory, le WAL, la mortalité et les seuils 2+2/12 restent inchangés.

La prochaine phase devra tester séparément les garanties d'une garde durable authentiquement isolée, le contrat mémoire/UC et l'atomicité M-11, sans autoriser de révision cognitive de production ni modifier la frontière agence proximale / résultat distal sans arbitrage explicite de l'opérateur.
