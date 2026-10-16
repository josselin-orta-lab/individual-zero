# A2.30-T : préenregistrement de l'audit indépendant des captures et du Shadow Stage6 de S

**15 octobre 2026, après connaissance des résultats de l'expérimentation S-shadow mais AVANT tout code T.** La campagne S-shadow a été **préenregistrée avant code** au commit `ea7b1374212e0fd6888b8e37a181c1bea40908e2`. Son [run initial #38740664255](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38740664255), code `0046d8b2b30f44fe5e4fd0b4b165c88e724a8881`, réussit sous Python 3.11 et 3.12 avec données identiques. **Les résultats sont déjà connus** : 72 mondes indépendants (64 avec actions, 8 observations passives), 196 transitions physiques, 44 ingestions, 24 décès externes, 8 paires avant/après ingestion causalement ambiguës, 4 contrastes d'attente informatifs et coûteux, 4 répétitions alimentaires toujours ambiguës, 8 contrastes danger spatial attendre vs retrait, et **56 recherches Stage6 shadow toutes `incomplete_model` faute de première transition connue**.

Une autre campagne indépendante [PR #190](https://github.com/josselin-orta-lab/individual-zero/pull/190) explore 36 mondes/104 pas de sondes perceptives. Cette PR #191 teste **une intervention environnementale confondante et le véritable Stage6 en shadow** ; elle ne doit **pas** se substituer à #190 ni dédoubler ses effectifs. Les fichiers et workflow ont des noms distincts afin d'éviter un conflit de fusion.

## Archives verrouillées

Source : artefacts `a230s-py3.11` et `a230s-py3.12` du **run #38740664255** (pas les replays techniques ultérieurs). Les 3 JSON sont identiques entre les deux Pythons. SHA-256 complets déjà calculés sur les octets originaux et figés **avant code T** :

| JSON | SHA-256 |
|---|---|
| `a230s-acted-worlds.json` | `b905535a67c72b912e0b384dbc7e189e8446ee4954631e559928bd922edd0e36` |
| `a230s-passive-worlds.json` | `2863bb4e4d820cb3cc9b7492a0264e23f888e6b12e6225313f3c40766f8c27e6` |
| `a230s-summary.json` | `969de41c916df3210f8c9e0c1f033edc769bd49536f7fd20b14eaee03deee048` |

## Audit indépendant, sans import du runner S ou Stage6

1. Télécharger ces deux archives en lecture seule. Rejeter tout octet divergent, SHA changé, archive incomplète, doublon de mondes, viol de protocole (variante/position/nourriture/suite) ou inconsistance de pas physique. Recalculer le SHA de chaque exemple `state × command → next_state`, les chaines `after_i == before_(i+1)`, l'état initial accessible et le premier pas terminal. **Ne jamais utiliser un état postterminal comme preuve d'une observation vécue accessible à un individu futur.**
2. Reconstituer depuis les seuls états cognitivement accessibles les couples `toxic_mild` / `exogenous_confounded` au pas 3, avant et après `manger`; vérifier la stricte identité des observations et commandes, mais **les sources physiques distinctes ne sont prouvées que par la configuration/intervention externe documentée**, pas par une attribution subjective. Vérifier l'attente t4 informative (4 contrastes, coût d'intégrité 7 dans la zone) et le second repas t4 non discriminant (4 contrastes).
3. Reconstituer la géométrie visible (baie présente/absente, obstacle est passable/bloqué) dans les 8 contrôles sans commander d'action. Recalculer les 8 contrastes de décès dans les mondes appariés par **première action réellement identique** et suite d'actions préengagée `wait` vs `escape`, jamais comme décisions de Stage6.
4. **Shadow Stage6 :** sans importer `SimulatorPlanner` ou `FrozenTableEquipment`, reconstruire chaque corpus `EquipmentCorpus` à partir **uniquement** des exemples déjà vécus dans le **même monde** avant `t_query`, vérifier son SHA, énumérer indépendamment les commandes candidates accessibles à cette date et compter les paires exactes `SimulationState × PrimitiveCommand` connues au premier pas. Contrôler les 56 diagnostics Stage6 et le but alimentaire déclaré 65 (R=1, profondeur3) sans prétendre reconstituer les chemins plus profonds lorsque la racine est bloquée.
5. Contrôles négatifs obligatoires : falsification du SHA d'un exemple, d'une terminalité, d'un état corporel après ingestion, d'une branche exogène, du nombre de premières arêtes connues, d'un exemple de transition **issu du futur dans le corpus shadow**, ou d'une fausse identité de mondes doit déclencher FAIL.

## Limite et issue

Ce recalcul de fichiers **ne prouve pas indépendamment** que `WorldBody.apply` a exécuté les commandes. Si l'audit T passe, préparer une relecture pure de la physique du scénario S-shadow sur des mondes détachés et séparer strictement ces *replays techniques* de nouvelles vies I0.

Ne jamais présenter la comparaison de deux mondes à physique différente comme une attribution causale subjectivement acquise par un même individu; aucune interpolation de l'Oracle vers Stage12 ou changement du statut public `incomplete_model`. **A2.30 PARTIELLE ; Stage12 PARTIAL ; #110 OPEN ; PR #191 DRAFT.** La validation cognitive reste NO-GO.
