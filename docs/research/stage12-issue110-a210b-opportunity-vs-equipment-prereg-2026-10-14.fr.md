# A2.10b, issue #110 : dissocier mémoire d'opportunité et couverture Equipment

**Préenregistré le 14 octobre 2026, avant tout nouveau mécanisme cognitif ou CI A2.10b.** Base main `d34f50bba79b352ef418324a6ee8308ac2f2d6fe`. Aucune modification normative v1.3.1, Stage12 toujours PARTIAL et non reçu.

## Observation de départ

Dans les journaux physiques A2.10a ([CI #38602987842](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38602987842)), la vie sustained/early/gain1.6 part (2,2), observe véritablement une baie à (3,1) à t2 depuis (2,1), et l'observe encore à t3. Le déplacement t2 est physiquement bloqué par le scénario, puis un déplacement vers la baie réussit à t3. À t4 I0 est sur la cellule de la baie, mais Planning indique `incomplete_model`, ne propose pas une suite `collecter → manger` exploitable, puis une option géographique remporte la compétition. L'exploration se poursuit. Le témoin sustained/none/gain1.6 collecte et ingère dans la même fenêtre courte. La référence baie n'est plus publiée dans `S_t` après t2 bien que la capture t3 voie encore la baie; cela **n'est pas une preuve d'amnésie** : Perception peut reconnaître et publier sans que cette contribution franchisse la compétition, et des états cognitifs supplémentaires peuvent persister.

## Hypothèses à départager

- **H_mem** : un souvenir vérifiable d'opportunité antérieure manque réellement au propriétaire Memory ou Exploration ; ce manque précède et explique l'absence de retour utile.
- **H_eq** : l'Equipment exact-table ne couvre pas l'état/action courant après le déplacement bloqué, donc une action pourtant physiquement possible reste `unavailable` au simulateur. Rechercher ce cas ne justifie pas de créer un résultat prédit fictif.
- **H_val** : une option alimentaire existe, mais sa valeur probante n'est pas compétitive face au signal exploratoire.
- **H_control** : le veto de sécurité ou le budget UC refuse, indépendamment de la connaissance spatiale. Aucun bypass, aucune charge implicite de crédits.

## Première étape, observateur indépendant uniquement

Créer un audit Python lisant uniquement les journaux JSONL immuables des vies A2.10a, avec SHA du fichier et provenance des conditions. Pour chaque pas : captations locales réellement publiées, observations de baie entrant dans `S_t`, nombre de `incomplete_model`, options réellement évaluées, actions physiques, déplacements bloqués, `effects.collected` et `effects.ate`. L'audit **n'a aucune voie de retour vers I0** et ne consulte pas `ground_truth` pour peupler un état cognitif. Ne jamais inférer une observation depuis la présence réelle de ressources dans une autre cellule. Conserver tous les résultats, y compris les absences.

Critères prospectifs : (T1) aucune observation distante non locale acceptée dans la preuve; (T2) comparaison au pas t2/t3/t4 libre contre early, provenance entrée et disparition de contribution distincte de mémoire autobiographique; (T3) `incomplete_model` décrit comme lacune de simulation et non danger avéré; (T4) consommation valable seulement avec `effects.ate` et gain `body.food`; (T5) 0 ordonnance d'action ou vérité Oracle ajoutée à l'agent. Un audit des archives n'est pas une nouvelle vie ou un nouveau seed.

## Décision conditionnelle sur le logiciel

Seulement après preuve de H_mem, développer avec ablation OFF/ON une trace bornée et datée des opportunités **déjà observées**, invalider/suspendre quand l'observation actuelle la contredit, et chercher un trajet uniquement sur les surveys physiques financés en UC, soumis à la vérification canonique de sécurité. Un lieu mémorisé ne prouve ni une ressource actuelle ni son innocuité. Si H_eq domine, tester d'abord une couverture Equipment entraînée depuis un corpus extérieur de vraies transitions observables, pré-natal et indépendant de l'Oracle, sans fallback omniscient ni prix UCs inventés. L'option de « retourner chercher les baies » codée en dur est interdite.

Aucun PASS de Stage12, ni fermeture #110, ni modification du MVP normatif avant une décision scientifique explicite. Les effets nocifs/retardés et la calibration `self/world/unknown` restent des expériences ultérieures séparées.
