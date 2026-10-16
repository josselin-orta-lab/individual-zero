# Stage12 / #110 / Option B : préenregistrement B-L600 et B-M48

**15 octobre 2026. Préenregistrement avant le code de campagne**, à partir de la PR #184 au commit `2ad79efc98a34f13c98498137e8f822c8fbbc2a6`. Le résultat déjà connu est que les six workflows du même commit sont PASS (le workflow CI générique est SKIPPED). La campagne historique de 600 pas utilise **le mode d'agence antérieur** : elle ne valide PAS B. Les tests B/M11 existants portent uniquement sur quelques générations, pas une vie longue.

**La décision opérateur B est acquise**, mais la réception du Stage12 et la migration normative v1.3.1 ne le sont pas. Ce protocole est une campagne d'ingénierie prospective, non une démonstration statistique de l'agence causale.

## Deux vies distinctes et deux périmètres de preuve

- **B-L600**, une vie nouvelle, mortelle et autonome issue de la factory actuelle `tests/test_stage12_dual_scope_runtime.py::born`, `dual=True`, `join=False`, `subjective_goal_agency=True`, coût UC `dual_scope_cost_uc=1` et `goal_agency_cost_uc=1`, avec journal WAL standard unique et **jusqu'à 600 transitions réellement exécutées**. Aucune commande externe injectée. Le journal et le WAL sont audités indépendamment. En fin de vie : audit `audit_stage12_first_person_agency`, `audit_stage12_dual_scope`, `audit_export_bytes`, preuve du même hash et du même nombre d'événements. Les valeurs `unknown` et `unavailable` ne sont pas des `self` distaux ; la réussite d'une commande n'est pas une réussite causale alimentaire.
- **B-M48**, une autre vie **autonome mortelle indépendante**, née sous M11 (`wal_path=None`, `m11_sqlite_custody=True`, aucun second WAL), visant **48 générations committées**. Effectuer un `cold_recover` véritable après la génération 24 ; puis 24 nouveaux pas (ni replay ni réparation rétroactive). Vérifier chaque `TransactionalStepReceipt` (génération, pas, état), les deux snapshots SQLite, puis le journal canonique final avec les **mêmes trois audits indépendants**. Vérifier que le premier `event_hash` au point de reprise est inchangé après continuation. Un refus de reprise, une mutation de naissance ou une collision de refs doit être compté FAIL, sans restaurer une vie incertaine.

Les **deux versions Python 3.11 et 3.12** rejouent la même paire de configurations, pas quatre vies distinctes aléatoires ; elles produisent des artefacts de provenance indépendants et des résultats comparables. Les mondes de référence déterministes ne sont pas statistiquement indépendants et ne prouvent pas la présence de contrastes `2+2/12` ni l'exactitude physique des sensations. Le mode de sommeil provient de la fixture B existante et ne sera pas ajusté pour susciter artificiellement des jugements.

## Critères d'acceptation préfixés

1. Chaque vie est réellement née avec B actif et `attribution_join=False`; un état `dead` ou un arrêt technique met immédiatement fin à toute commande supplémentaire. **600/600 ou 48/48** sont des objectifs falsifiables : si non atteints, archiver la preuve puis **CI FAIL**, sans inventer les pas manquants.
2. Audit de la chaîne exacte, du WAL ou du SQLite M11 et de la conservation du dernier `journal_head`. Aucun émetteur Oracle/Bench et aucune copie WAL indépendante pour la vie M11.
3. Au moins **un** préengagement et un jugement **duals réellement produits** par vie ; chaque jugement correspond à un préengagement, un jugement proximal, un débit UC et une perception `stage12-dual-scope-body-cue-v1`. La forme de refus `unavailable` est conservée et comptée, jamais convertie en preuve `self`. Aucun minimum artificiel de succès `self` proximal.
4. Aucun `stage12_attribution_pair_admitted` ou `stage12_attribution_pair_applied` en mode B ; le détecteur GA-06 hérité ne consomme pas le jugement proximal comme responsabilité distale. `2+2/12` demeure la contrainte initiale, non abaissée.
5. La reprise M11 à froid doit préserver le nombre et l'ordre des événements de la première moitié et l'image du propriétaire Action Control. Le test ciblé existant de naissance B ↔ historique incorrecte demeure requis.
6. Un reçu d'observation `food` `improved` reste une observation corporelle perçue, **jamais une preuve causale de responsabilité distale**. Les nouveaux journaux sont vérifiés par `audit_stage12_dual_scope` indépendamment du modèle propriétaire.
7. Aucun changement du runtime physique, des garanties M11/mortalité, UC de Stage6 autres que la réserve B déjà décidée, Stage9/DC-05, Oracle/Bench, ni des exigences normatives du MVP v1.3.1. Aucune réception opérateur présumée.

## Verdicts et conservation des preuves

Le **succès des deux modes** sous les deux Pythons autorise seulement un **PASS technique borné de la campagne B-L600/B-M48**, pas la clôture de #110. Une divergence de journal ou de reprise = FAIL. Une vie mortalement arrêtée est conservée et rapportée comme preuve négative et non prolongée. Les scripts écrivent un résumé et la preuve canonique avant de retourner un échec ; les workflows emploient `upload-artifact if: always()`. L'essai M48 n'est pas une validation M11 de 600 générations ; il ne doit jamais être présenté comme tel.

Ne pas déclarer de crédit GA-06, d'agence distale `self`, de certification du capteur, de 600 pas M11 ni de validation scientifique absolue. Stage12 **PARTIAL**, issue **#110 OPEN**, pas de validation finale opérateur.
