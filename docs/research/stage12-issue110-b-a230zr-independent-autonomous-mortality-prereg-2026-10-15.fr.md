# A2.30-ZR : préenregistrement de la contre-expertise indépendante sur les vies autonomes ZQ

**15 octobre 2026.** Contrôle de provenance **POST-HOC par rapport aux résultats physiques ZQ déjà connus**, mais **AVANT l'écriture du code de contre-audit ZR**. Ne pas prétendre à une deuxième cohorte scientifique. Provenance primaire : [CI ZQ #38796937894](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38796937894), commit exact `850256d02cdc9a2fc9be78f7ce1f66ca5dc98347`, 19 tests ZQ PASS dans les jobs Python 3.11/3.12. Le protocole ZQ a été préenregistré indépendamment au commit `cbd95fc2f0d6a5d66b682b7c97db6782605dbf1b` avant les naissances.

## Sources originales scellées avant le code ZR

Télécharger directement les deux artefacts originaux de ZQ : `a230zq-py3.11`, `a230zq-py3.12` du run #38796937894. Vérifier **exactement un** `a230zq-summary.json` et `a230zq-pairing.json`, **24** `a230zq-life.json`, **24** `canonical.jsonl` et **24** `life.wal` par archive. Refuser copie de source modifiée ou pièce absente. Le résumé global contient des dérives ULP documentées du journal : les deux SHA source sont **distincts** et fixés séparément ci-dessous; les résultats appariés sont identiques en octets.

- SHA-256 **résumé Python 3.11** : `fba7f4011aac074ab1106f604fae912fec4170c6f8aa8e9e0012accad7fda650`.
- SHA-256 **résumé Python 3.12** : `edafcaa281082af05aa7cd0a74ff72ff573485fc2f82a0068b6d315cea367ac6`.
- SHA-256 **appariements identiques** : `99643f0a40069be640eaf2c4a02565953288ecb362a4fa00f9ee9c2e4a03c437`.
- Origine historique des captures initiales : [run ZB #38767643472](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38767643472), deux résumés à SHA distincts `ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b` et `ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362`.

## Mission d'audit ZR indépendante

Écrire un script **qui N'IMPORTE PAS le runner ZQ, les corps WorldBody, le code Stage12Runtime, le planificateur Stage6 ni les modules de jugement subjectif**. Il peut utiliser l'audit officiel du journal canonique et du WAL M11 pour contrôler l'intégrité **à partir d'archives uniquement**, sans naissance, sans simulation, sans déploiement, sans action physique.

Le script doit :
1. Réexaminer **chacun des 24 WALs durables** et le journal canonique correspondant, confirmer son ancre `head_hash`, compte d'événements et SHA, et refaire le bilan de clôture du journal sans se fier uniquement aux 24 résultats du runner. Refuser les fichiers de vie absents/doublés, tous événements de cognition/monde au-delà du pas d'un décès, toute divergence `attempt_ref` ou `command_hash` entre `command_experienced`, `world_transition_experienced` et `individual_death_confirmed`.
2. Recompter directement à partir des **événements bruts** : les 24 identités, les pas réellement physiques, la mortalité, les commandes `east`, les `collecter/manger berry_b`, les requêtes UC `requested_uc` reconnues/refusées, les recherches Stage6 réellement effectuées et les jugements proximal/dual-scope. Une demande UC acceptée est **une écriture explicite**, pas une estimation du solde disponible.
3. Vérifier que les 24 premières perceptions ont le schéma accessible canonique et reprennent les douze roots scellés de ZB. Une absence réelle de `perceptual_capture` au cours d'un sommeil reste **`unavailable`**, jamais une expérience sensorielle fabriquée. Recompter ces absences explicitement.
4. Pour chaque paire de naissance correspondant au même profil, layout et toxicité B : comparer la perception de la naissance, le vrai préfixe moteur `north → east` aux pas 1 et 2, **les captures perceptives des mêmes pas**, le hash de l'Equipment prénatal A, l'identité des charges UC effectivement enregistrées jusqu'à la divergence et l'effet du déplacement `(2,1)→(3,1)`. La cause terminale `lethal_zone` n'est visible que dans `individual_death_confirmed` de la vie affectée, **jamais** dans la perception, le choix ou un jugement vécu sur la mort. Les deux individus distincts ne constituent pas une renaissance ou un contrefactuel personnel parfait.
5. Refuser le moindre décès « imputé au choix subjectif » sur la base seule d'une commande `self`; la cause externe doit être exactement jointe à la commande et à la dernière transition. Contrôler le bornage mortel et l'absence de jugement B produit après décès; signaler explicitement les **0 nouveaux I0 et 0 nouvelles actions** exécutées par ZR.
6. Si la réexécution du code ZR sous Python 3.11 et 3.12 voit les mêmes sources scellées et les mêmes résultats, publier un seul résultat scientifique original ZQ, pas deux cohortes. Conserver les divergences ULP entre les journaux historiques et nouveaux, sans les masquer.

## Contrôles négatifs préenregistrés

Altérer le SHA d'un des résumés originaux; supprimer un WAL; changer l'identité du mort; faire apparaître `lethal_zone` dans une perception; faire disparaître l'événement de mort; faire correspondre le décès à un autre `attempt_ref`; inventer une consommation `berry_b`; afficher un `self` sur la mort postmortem; inventer un refus UC ou des UC « estimées »; traiter un pas de sommeil sans capture comme une perception disponible; produire une parité au t2 avec commandes, positions ou sens différents; compter les anciennes vies ZB comme des naissances ZQ.

Chaque altération que le protocole juge observable doit faire **FAIL**; une absence d'événement authentique doit rester `unavailable`, jamais supposée nulle ou présente.

## Résultat ZQ déjà connu, à reproduire ou contester

**24 nouveaux I0, 408 pas autonomes, 12 morts physiques à t2 / 12 témoins survivants au maximum t32, 12/12 vrais contrastes appariés, 274 déplacements east, 0 B collectée/mangée, 208 recherches Stage6, 7 954 UC demandées/acceptées, 0 refus, 20 jugements dual-scope uniquement dans les vies continuées.** Ces effectifs ne sont **PAS des hypothèses ZR nouvelles**. ZR doit les reproduire à partir des sources sinon refuser l'attestation.

Verdict **ZR PASS technique** si SHA, WAL, causalité motrice, frontières des sens, UC, falsifications et cross-Python réussissent, sinon FAIL sans réviser les critères après coup. Pas de changement `src/i0`, Stage9/DC-05, Oracle, M11, MVP v1.3.1. A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 **CLOSED administrativement**; aucun PASS scientifique global ni autorisation de déploiement.
