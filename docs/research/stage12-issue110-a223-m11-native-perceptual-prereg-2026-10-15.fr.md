# A2.23 : audit du reçu perceptif natif sous l'unique transaction M-11

**Préenregistrement du 15 octobre 2026, avant code A2.23**, base `main 4c2c34fb643ec086e8487d5664cda7867051733b`. Issue #110 OPEN ; Stage12 PARTIAL ; spécification normative v1.3.1 inchangée.

## Hypothèse

Stage3 journalise déjà `perceptual_capture` au même pas et avec le même `attempt_ref` que la commande ; Stage10 utilise la même projection pour les réveils. M11 commite le suffixe de ce journal dans **la même transaction SQLite** que l'état canonique et l'avancement du pas. Un auditeur extérieur pourra retrouver **un reçu perceptif authentiquement journalisé** pour chaque génération committée, sans donner à I0 de cause physique cachée et sans ajouter de WAL. Le hachage garantit cohérence et propriété transactionnelle, non véracité du capteur physique.

## Matrice prospective

**4 seeds 141–144 × six frontières M11 réelles** `after_intent`, `before_private_execution`, `after_private_execution`, `before_sql_commit`, `after_sql_commit`, `after_publication` : **24 vies Stage12 réellement autonomes et mortelles**, une seule tentative de pas chacune. Processus enfant distinct, vrai `M11TransactionalMortal.birth`, vrai `run_step` et vrai `os._exit(76)` au crochet injecté. Auditeur parent lit la base SQLite à froid, sans relecture d'objets du processus tué.

Pour les 16 crashs pré-COMMIT : génération 0, intention pendante, refus `cold_recover`, **zéro reçu `perceptual_capture` publié**. Pour 8 crashs post-COMMIT : génération 1, intention absente, un reçu `perceptual_capture` au pas 1, `emitter=stage3-runtime`, un `attempt_ref` non vide et unique, version `stage12-first-person-cue-v1`, capture `position`/voisinage/inventaire depuis le premier pas authentiquement vécu. Le reçu doit précéder `step_closed`, être haché dans le journal exporté et correspondre au head et au nombre d'entrées M11. La reprise à froid peut poursuivre seulement la génération courante ; aucun ancien état ne doit être choisi. Les seeds ne sont pas des tests de causalité et les deux Python rejouent la même matrice.

**Contrôle négatif falsifiable :** sur les quatre seeds, un candidat de preuve hors journaux (une position modifiée, une identité de vie remplacée, un pas/attempt_ref falsifié, ou une capture prétendue issue d'un pas précommit) doit être refusé par l'auditeur externe comparant les occurrences originales. Contrôle limite distinct : un acteur capable de modifier `Perception.capture` *avant* son entrée dans le journal peut faire durablement enregistrer une fausse perception ; l'infrastructure logicielle M11 ne prouve pas la vérité physique des sensations. Cette limite doit être déclarée et ne doit pas déclencher une modification secrète du runtime.

## Critères T1–T7

1. Exactement 24 processus enfants et 24 injections `os._exit(76)`, états attendus 16 pending / 8 committed et 8 reçus valides.
2. Aucune preuve perceptive n'est lisible comme committée lorsque l'intention reste pendante ; pas de reprise d'une vie incertaine.
3. 8/8 reçus committés contiennent les données subjectives permises, les bonnes identités de tentative et ordre de clôture.
4. 4/4 substitutions postérieures détectées par comparaison à l'archive SQLite canonique.
5. La source de Perception reste une frontière de confiance ; pas de prétention à authentifier un capteur compromis avant journalisation.
6. GitHub CI sur Python 3.11/3.12 ; journal audit réutilise les garanties existantes, sans créer une autre source autoritative.
7. Zéro changement à I0/Stage3/Stage10/M11/Oracle/Stage9/DC05, zéro nouvelle UC, zéro GA-06 ni norme v1.3.1 modifiée. Aucune réception opérateur.

Un PASS validerait une **preuve de conservation du reçu natif** et une piste d'intégration, pas la révision cognitive, pas un jugement distal. La séparation *agence de la commande proximale / responsabilité du résultat distal* reste à arbitrer explicitement avant toute évolution normative.
