# #305 / #438 — Stage8 : contraste sélectif du Q de « manger » après collecte libre

**Préenregistrement avant le code d'expérience**, 28 octobre 2026, main `bd484d1da41038acf6585e37c49d59b1c789625d`. Étude **exploratoire** motivée par l'observation intermédiaire de la PR #604 (run exact-head #40763483932, Python 3.11 naturel, trois autres jobs alors partiellement terminés). La fenêtre a été choisie après lecture des résultats de #604 : elle ne constitue donc **pas** une découverte confirmatoire indépendante.

## Fait de départ et question

Dans la vie canonique M11 v4 `oasis/b`, après `manger` au pas 11, `dormir` aux pas 12–17, et `collecter berry_a` au pas 18, la continuation **libre** observée a appliqué `manger berry_a` aux pas 19 et 21, avec vraie ingestion de nourriture (+9,8 nets dans les deux cas), et `collecter berry_a` au pas 20. Aux pas 19 et 21, Planning a consulté des Q personnels appris sur `collecter` et `manger`, tous deux positifs, et a proposé `manger` à travers des cycles réels. Mais l'ordre de départage amont favorise déjà `manger` aux pas impairs : le **Q amont n'est pas nécessaire au choix du gagnant** dans ce contexte.

Question expérimentale distincte : à contexte et histoire **identiques avant chaque intervention**, la **lecture Q de l'option `manger berry_a` par Stage8** contribue-t-elle de manière causale à l'admission/action physique, à la consommation ou à l'état corporel ? L'ablation du Stage8 n'est pas une ablation du classement amont ; ne pas les assimiler.

## Bras fixés avant lecture des nouveaux résultats

Exécuter exactement trois naissances M11 v4 mortelles, même identité `i1:304:heldout:oasis:b` sur **trois SQLite séparés**, même preset `oasis`, mêmes paramètres de naissance, noise=0. Aucun état/importation antérieur, rollback ou resurrection. Chaque naissance est libre jusqu'à **24 pas maximum**, arrêt sur décès :

1. `canonical` : aucune intervention.
2. `meal_stage8_mask_step19` : **au pas 19 seulement**, et seulement quand `Stage8OptionEvaluator.evaluate` évalue une proposition de signature `i1:affordance:manger:target=berry_a`, substituer **le résultat de son unique lecture propriétaire originale** par `LearnedValue(status="unlearned", value=None, evidence=None, update_count=0)`. Consulter d'abord `original_read` une fois, observer sa vraie valeur/status et l'authentifier; ne jamais lire Q deux fois. Tout le reste de Stage8 original.
3. `meal_stage8_mask_step21` : intervention identique **au pas 21 seulement**, aucun masquage au pas 19.

L'intervention ne concerne ni les propositions ni les lectures de Planning, ni TD écriture/éligibilité, ni Stage6, Competition, Action Control, physiologie, UC, I0 ou les autres options. Ne pas fabriquer une commande `manger` ni un objectif `eat`. Enregistrer même les résultats négatifs. Si la proposition exacte n'est jamais évaluée/si sa lecture n'est pas apprise, rapporter `NOT_EXPOSED`, sans corriger le monde pour la rendre disponible.

## Portes d'authenticité et observables

- Comparer les digests d'environnement/physique, config TD/needs et noise de chaque naissance. Vérifier le **préfixe M11 bit-identique** : journal et propriétaires avant le premier pas masqué (pas 1–18 pour le bras 19, pas 1–20 pour le bras 21), mêmes actions physiques, corps, position, inventaire, TD, GoalManager, Competition, fatigue et sommeil.
- Avant l'intervention, le vrai `learned_value` du propriétaire Stage8 est consulté **une seule fois**, statut `learned` et Q non nul; le wrapper retourne un objet de même signature mais marqué `unlearned`. Il ne change aucune politique et n'impute pas d'UC fictif.
- Après la naissance, auditer SQLite M11 **à froid** : nombre de générations, hash tête du journal et statut, aucune intention pendante; lire les `stage8_option_evaluation`, `competition_cycle`, `command_admitted`, `command_experienced`, `compute_charge`, `td_update_published` et images physiques avant/après.
- Joindre par `(t_monde, cycle, option_ref)` l'option Stage8 modifiée au reçu réellement publié, et contrôler `learned_value_status=unlearned` du reçu dans le bras masqué, contre `learned` dans le bras canonique à même temps/option lorsque disponible. Reporter le nombre de lectures authentiquement masquées, leurs Q/update_count et les débits Planning/Stage8/Competition **sans coûts supplémentaires**.
- Rapporter première divergence Stage8, première divergence Competition, première **commande appliquée** différente (pas/cycle), premier effet corps/inventaire différent. Rapporter les pas 19–24 des trois bras, y compris la mort éventuelle, pas seulement les choix positifs.

## Verdicts préenregistrés

- `NOT_EXPOSED` : aucune lecture Stage8 réellement apprise et masquée au pas défini.
- `EXPOSED_NO_APPLIED_DIVERGENCE` : Q Stage8 modifié, aucune action physique différente pendant les 24 pas.
- `MATCHED_LOCAL_STAGE8_Q_MOTOR_EFFECT` : première action différente à ou après le pas de masquage **et** identité préintervention prouvée; cet effet est local et médie éventuellement Competition.
- `CONTEXT_MISMATCH` / échec technique : source/config/préfixe non identiques, journal incongru, Q lu plusieurs fois, option non authentifiée, ou divergence moteur avant l'intervention. Interdiction de promouvoir la preuve.

Même si `manger` est retenu en canonique et remplacé en témoin, ne déclarer un bénéfice physique que pour un **écart mesuré de nourriture/inventaire sur actions réellement appliquées**, en distinguant résultat immédiat et les étapes suivantes. Aucune preuve de préférence générale, de crédit causal `collecter→manger`, de survie durable ni de robustesse multi-mondes, et aucun `GO` d'apprentissage naturel à partir de ces seules trois vies. **C'est une étude exploratoire, sur une fenêtre choisie après #604.**

Respecter 4/4 CI exact-head Python 3.11 et 3.12 avant fusion du seul harnais + documentation. Deux versions Python répètent la même expérience déterministe, et ne sont pas six naissances indépendantes.

## Rectificatif de mécanisme, avant nouvelle exécution (29 octobre, selon chronologie GitHub)

Le premier run de #605 ne masque **aucune** lecture : `NOT_EXPOSED` sur les deux bras selon Python 3.12. L'inspection du moteur révèle la cause de protocole : pour une proposition de provenance `i1_unknown_affordance`, `I1PartialEvidenceAdapter.evaluate` traite directement les données déjà acquittées dans `self._pending["local_opportunity_evidence"]`; le `Stage8OptionEvaluator.evaluate` sous-jacent n'est **pas appelé pour cette option**. La proposition initiale de hook Stage8OptionEvaluator ne pouvait donc jamais activer une suppression de Q sur `manger berry_a`. **Il s'agit d'une non-exposition expérimentale, pas d'une résistance de l'apprentissage à une ablation.**

Pour tester **le même objet scientifique** (contribution de la preuve Q à l'évaluation Stage8), corriger seulement le harnais d'ablation : envelopper `I1PartialEvidenceAdapter.evaluate` et, uniquement pour `i1_unknown_affordance`, signature `i1:affordance:manger:target=berry_a` au pas 19 ou 21, remplacer **temporairement et exclusivement dans l'adaptateur** le triplet `learned_status/learned_value/learned_evidence` de `local_opportunity_evidence` par `unlearned/None/None`. Rétablir la référence originale immédiatement après `original_adapter.evaluate`. Ne pas toucher aux lectures Q originales de Planning, à ses propositions, à Q/TD, à la physique ni aux coûts UC; ne pas invoquer une lecture Q supplémentaire. Enregistrer la preuve authentique déjà stockée dans le `pending` (signature, Q, evidence), vérifier que le reçu Stage8 correspondant est bien `unlearned` dans le bras masqué, et conserver l'identité des propriétaires/journaux avant le pas de masque. Le libellé devient **ablation de l'évidence Q déjà transmise à Stage8 via l'adaptateur I1**, et non suppression d'un appel direct `LinearTDValues.learned_value` par Stage8. Le choix des deux fenêtres reste exploratoire, fixé avant la correction.

Les premiers `NOT_EXPOSED` sont conservés comme résultat négatif **du hook erroné**, jamais transformés rétroactivement en preuve. Le nouveau SHA doit repasser 4/4 CI et publier ses propres résultats avant toute fusion.