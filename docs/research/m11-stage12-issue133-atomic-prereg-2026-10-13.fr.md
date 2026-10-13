# M11/Stage12-I133-TX1 : transaction atomique physique + h + index (préenregistrement)

Date : 2026-10-13. Ce document est écrit **avant** tout changement d'exécution transactionnelle Stage12 et avant les essais. Branche expérimentale `exp/m11-stage12-atomic-paid-index-20261013` créée à partir de la PR #139 commit `c65a5e245a0fbecb1ad432039224058a8baf728b`. Base normative inchangée `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, §§1-5, M-11/M-12, avec Stage10 P-42 et Stage12 P-43.

## Verrou reproduit et hypothèse

Le runtime intégré Stage12 exige actuellement son WAL JSONL fsyncé. `M11TransactionalMortal.birth` et `cold_recover` autorisent seulement les classes exactes Stage10/Stage11 et **rejettent Stage12**. Les expériences #133 P6-B6 sur 600 pas montrent des améliorations 295/299 et 296/299 consolidés contre 242/299 et 238/299, avec un backlog 4 et 3, mais `os._exit` après l'activation h laisse un état Stage12 non atomiquement recouvrable. La validité du WAL seule ne certifie pas le dernier état propriétaire.

Hypothèse : une exécution en **candidat Stage12 privé et sans WAL latéral**, engagée dans la transaction de génération SQLite M11 unique, permet de récupérer *seulement* la dernière génération entièrement validée, sans rejouer de commande physique, sans rollback historique, en enregistrant WorldBody, Scheduler, h, index, Memory, état diagnostique et journal exhaustif dans le même commit. Si une intention reste indécidable, refuser et sceller la vie ; ne jamais ressusciter la génération précédente.

## Paramètres gelés

- Vrai Stage12Runtime, un WorldBody, un Scheduler, même moteur physique, mêmes propriétaires cognitif/sommeil/diagnostic, Oracle et Bench absents.
- Deux modes **exclusifs** : chemin existant WAL pour les vies ordinaires, et opt-in `M11TransactionalMortal` avec stockage SQLite seulement. Le premier ne change pas, aucun second journal vivant n'est toléré.
- `w_C = 0`, pas de hausse des plafonds P-42 100 UC/pas et 600 UC/période, ni de coûts P-43, ni de changement de priorité, de sélection, de six passes, de taille de lot ou de naissance physique.
- Préserver l'exactitude du contrat du constructeur, de tous les états mutables y compris états Stage12 (détecteurs, alertes, progression, derniers déficits) et index expérimental ; une donnée qu'on ne peut restaurer fidèlement bloque la reprise.
- Aucun relancement d'anciennes vies. Paramètres/monde/graines publiés et versionnés; 600 pas sont un plafond, une vraie mort termine plus tôt.

## Ordre des expériences

1. **Contrat d'entrée** : classe Stage12 sans opt-in SQLite rejetée par M11, et constructor WAL obligatoire sur chemin historique. Le runtime opt-in privé n'a ni WAL adjacent ni second droit d'exécution, et l'instance remise au code appelant après birth est frappée d'arrêt; le candidat est créé et exécuté seulement par M11.
2. **Round-trip exact** : naissance SQLite, 1 à N étapes réelles, h, index, alertes et progression si observés ; fermeture, `cold_recover` depuis la **dernière génération seulement**, hachage des propriétaires/journal/WorldBody/Scheduler identique à la génération engagée, puis continuité de transition physique autorisée; pas d'action rejouée.
3. **Crashs réels `os._exit`** au minimum après intent, après exécution privée, avant SQL COMMIT, après COMMIT avant publication en mémoire et après publication ; inspecter SQLite par lecteur autonome. Seule une génération atomique actuellement engagée sans intent ambivalent est éligible; sinon blocage définitif. Pas d'export antérieur comme source de vie.
4. **Cas négatifs** : WAL adjacent, propriétaire absent, schéma Stage12 altéré, mauvaise politique/cout UC, mauvaise identité/branche, candidat modifié, source Oracle/Bench, doublon de h/index, décès et terminalité, index incomplet.
5. **Comparaison physique/UC** : quand la trajectoire le permet, vérifier que l'opt-in SQLite ne modifie aucune action ni résultat du runtime Stage12 normal sur même monde/configuration, `w_C=0`; reproduction Python 3.11/3.12.

## Critères GO/NO-GO

Un GO technique limité suppose l'intégrité de SQLite, la parité de la physique et des sorties h/index, la capture exhaustive et hachée de tous les propriétaires Stage12 et la récupération de la génération courante lors des crashs éprouvés sans ambiguïté. Les interruptions avec intention durable incertaine ou après un commandement irréversible doivent **fail-closed** sans création d'une seconde vie. Un seul test favorable ou une CI verte n'est pas une preuve de sûreté générale.

La validation scientifique du comportement de mémoire et la réception opérateur restent séparées. Ce protocole ne modifie pas les références MVP. Le `main` et la PR #139 ne sont pas fusionnés automatiquement. La campagne conserve ses résultats négatifs et documente tout verrou normatif.
