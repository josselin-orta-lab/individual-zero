# Résultats A2.23b : captures subjectives activées à la naissance sous M-11

**15 octobre 2026.** Préenregistrement [A2.23b](stage12-issue110-a223b-born-enabled-prereg-2026-10-15.fr.md) au commit `ff83c608`, avant instrumentation. Code expérimental évalué au commit `790ffc4f`. [GitHub Actions #38646420815](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38646420815) **SUCCESS sur Python 3.11 ET 3.12**, mêmes cas reproduits deux fois, non 48 vies indépendantes.

## Résultats

Quatre configurations spatiales (positions 8,8 ; 12,8 ; 16,8 ; 20,8), six fenêtres de crash M-11 avec `os._exit(76)` par configuration, soit **24 naissances distinctes d'instances Stage12 autonomes mortelles**, dotées de `subjective_goal_agency=True` et `m11_sqlite_custody=True` dès leur construction. La fixture hérite du modèle physique standard et la source d'eau est deux cellules à l'est.

**24/24 interruptions réelles** ; **16/16 intentions pendantes sans reçu perceptif committé ni reprise permise** ; **8/8 commits avec le reçu `stage12-first-person-cue-v1`** contenant quatre voisins, position, inventaire, identité de tentative et ordre avant `step_closed` ; **8/8 reprises à froid de la génération 1 et nouvelles exécutions arrivant à la génération 2**, avec deux reçus natifs ordonnés et le premier préservé. **32/32 substitutions post-journal** sont incompatibles avec les occurrences canoniques ; **8/8 factories nées avec la mauvaise identité** sont refusées.

## Réconciliation avec A2.23a

A2.23a, sur la fixture historique `subjective_goal_agency=False`, ne pouvait produire que le reçu minimal. A2.23b répond spécifiquement à cette déviation en testant un autre contrat de naissance explicitement activé, sans modifier le runtime de production. L'identification des positions de départ rend les configurations physiques distinctes ; ce sont des variantes déterministes, pas des seeds indépendantes de découverte causale.

Ce succès confirme la persistance **transactionnelle** du reçu d'agence visible et sa continuité après crash avec le propriétaire unique M-11. Il ne signifie pas qu'I0 a produit un jugement subjectif révisé, ni que l'état alimentaire distal lui soit causalement imputable.

## Limites et dette ouverte

Le **contrôle négatif de compromission de `SymbolicPerception.capture` avant inscription M-11**, pourtant prévu dans le préenregistrement, **n'a pas encore été exécuté par ce script**. T5 reste donc **PENDING**, et il serait scientifiquement incorrect de marquer A2.23b entièrement terminé. Les comparaisons de substitutions post-journal détectent seulement les désaccords à l'archive canonique. Une modification de la production perceptive *avant* le commit peut être archivée de manière cohérente et doit être expérimentée séparément. La CI focused transversale est une vérification indépendante des deux jobs ciblés.

Aucune modification du code cognitif, Stage3/Stage10/M11, des UC, du WAL, de la mortalité, d'Action Control, de l'Oracle, de Stage9/DC-05, de la spécification v1.3.1 ni des seuils `2+2/12`. **0 nouvelle paire de calibration GA-06**, pas de validation à 600 pas et pas de réception opérateur.

**Verdict : T1-T4/T6 PASS dans les limites du banc ; T5 non encore exécuté ; Stage12 PARTIAL ; issue #110 OPEN ; PR #179 maintenue sans fusion tant que les contrôles négatifs et les CI finales ne sont pas clos.**
