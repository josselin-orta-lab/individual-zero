# Transition scientifique contrôlée I1 → I2

**Décision approuvée le 31 octobre 2026.** I2 est un candidat architectural distinct, pas une promotion automatique ni un remplacement d'I1. Aucun nouvel individu ne doit être instancié pendant cette phase documentaire.

## Référence Git épinglée (protection encore incomplète)
- Dépôt : `josselin-orta-lab/individual-zero`
- I1 code baseline : `1e19f02db14b64a35f8bb014d69cc061f311002c`
- Sous-arbre `src/i1` : `cf7968d3ee94a5792d37d76241a55d4c8406a3fb`
- Branche de conservation : `archive/i1-reference-2026-10-31` (pointe sur le commit épinglé, **`protected=false` observé via API le 31/10/2026**). Ne pas supprimer, réécrire ni force-push ; protection/règle externe encore à établir, voir #661.
- I0 demeure inchangé. I1 reste `active` dans le registre tant que I2 n'a pas franchi ses portes.

## Faits et limites
- A1-P : 8 vies H48, relecture froide et signal exploratoire hétérogène ; aucune généralisation.
- A1-C : 48 vies H48, 24 paires/12 blocs ; résultat confirmatoire ciblé **NO_GO** ; bénéfice adaptatif L3 **NOT_ESTABLISHED**.
- A1-C relecture rétrospective (#305) : interactions `collecter` / `manger` et persistance des options associées à des décisions alimentaires inefficaces dans plusieurs trajectoires. Il s'agit d'observations historiques, pas d'une démonstration causale que modifier la durée de vie des OptionRefs corrigerait le problème.
- A2-R : **NOT_EXECUTED 0/96**, ne pas lancer pour « clôturer » I1. Conserver le protocole et les issues.
- Archives M11 historiques sauvegardées séparément dans la bibliothèque scientifique privée ; leur disponibilité publique, leur dépôt durable et leur audit par un tiers restent distincts de la branche source.

## Hypothèses I2 à falsifier
**H1 Continuité sémantique** : une intention fondée sur des preuves vécues peut persister au-delà d'un pas, tout en reconstruisant à chaque capture les offres physiques, la compétition, la sécurité et l'admission des commandes. Aucun accumulateur moteur, droit acquis à l'action, oracle ni état d'un I1 vivant n'est hérité.

**H2 Crédit instrumental différé** : des traces personnellement acquises permettent de créditer une préparation coûteuse (par exemple collecter) à une conséquence ultérieure (manger), sans stratégie codée « nourriture d'abord ». Comparer aux mêmes traces de contrôle et aux résultats nuls/dangereux.

**H3 Arbitrage intégré** : besoins, exploration, mémoire et apprentissage contribuent sans multiplier des candidats impossibles à départager ; examiner non-offre, coût UC, non-évaluation, seuil, veto, action physique et récompense séparément.

## Invariants
- Naissance indépendante, aucune connaissance cachée ou expérience préchargée.
- Corps et monde simplifiés identiques pour le test comparatif, sans oracle d'alimentation ou danger.
- UC honnêtes ; Perception, Competition, Action Control et WorldBody gardent des responsabilités distinctes.
- M11 authentique, propriétaires distincts, mort irréversible et reprise seulement de génération courante sûre.
- I2 possède son propre `src/i2/lab`, ses `src/i2/runtime`, `modules`, `config`, `tests/i2` et documentation ; pas d'import du moteur `i1lab` comme exécuteur sous un nouveau nom.
- Les expériences de I1 ne deviennent pas des connaissances de naissance d'I2.

## Plan séquentiel et portes
**G0 Archive** : ancre Git I1, tree SHA, manifeste des résultats A1-P/A1-C et de leurs limitations, disponibilité durable des originaux, protection contre suppression/réécriture attestée (non acquise), politique de non-réécriture. Archive source != gel complet des artefacts externes.

**G1 Théorie et contrats** : documenter causalité, provenance, propriétaire des intentions, expiration/renouvellement, coût UC, contexte de remise à zéro et transitions M11 ; spécifier H1–H3 avec réfutations possibles et risques. Revue architecturale obligatoire avant moteur.

**G2 Prototype isolé** : créer seulement le squelette inerte via `tools/new_engine.py --generation I2 --parent I1` et analyser avec `tools/assess_engine_proposal.py`. La présence de dossiers ne signifie aucune activation. Développer un noyau autonome minimal, sans réutiliser les couches de I1 sans examen RAI.

**G3 Garde logiciel** : tests positifs et adversariaux 3.11/3.12 : provenance first-person, comptage UC, identité de naissance, chronologie, veto moteur, décès, crash avant/après COMMIT, continuité d'intention sans continuité d'option motrice. Pas de passe-droit « réessayer » après décès.

**G4 Préenregistrement scientifique** : fixer mondes contrebalancés, vrais nouveaux tempéraments, bras I1/I2, N et unités indépendantes, H et censure, outcomes/CI/statistiques, critères d'arrêt et de validité, publication de tous les échecs. Les huit vies A1-P et 48 vies A1-C sont historiques, jamais le nouvel échantillon de confirmation.

**G5 Exécution comparative** : seulement après G0–G4 et revue indépendante; mêmes lois physiques, naissances distinctes, aucune action forcée. Mesurer exposition → apprentissage → décision → conséquence corporelle → adaptation durable, plus coût UC, mortalité, erreurs et généralisation.

**G6 Promotion** : uniquement sur preuve confirmatoire robuste, revue humaine d'architecture/science et décision explicite ; avant cela I1 est l'actif et I2 `PROPOSAL_ONLY`.

## Politique d'exécution
- Un lot documentaire cohérent, pas de CI moteur sur les éditions Markdown.
- CI légère ciblée sur les invariants modifiés; une CI cross-version finale seulement pour les changements logiciels significatifs et le SHA exact.
- Pas de cohortes longues avant le préenregistrement et la chaîne de custody.
- Toute expérience négative est conservée ; pas d'ajustement opportuniste de seuils après résultat.

**Statut au dépôt initial de la décision : G0 PARTIAL (branche et SHA existants, non protégée) ; G1 cadre proposé ; G2–G6 NOT_STARTED.**
