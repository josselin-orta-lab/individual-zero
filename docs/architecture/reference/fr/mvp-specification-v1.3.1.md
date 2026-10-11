# Individual Zero — Spécification normative MVP v1.3.1

**Titre :** Mortalité irréversible, journal causal exhaustif interne, mémoires consolidées distinctes et évaluation indépendante  
**Langue faisant autorité :** anglais  
**Date :** 11 octobre 2026  
**État du document :** **CIBLE NORMATIVE DE MIGRATION, CONFORMITÉ LOGICIELLE NON ENCORE DÉMONTRÉE**  
**Condition d'activation :** Stages 10 et 11 déjà validés par l'opérateur et intégrés dans main ; chaque PR suivante nécessite ses propres preuves et la protection de main.  
**Références historiques :** [MVP v1.2.1](mvp-specification-v1.2.1.md) et [MVP v1.3.0](mvp-specification-v1.3.0.md), conservées sans modification.

## 0. Autorité, remplacement et non-rétroactivité

**La version anglaise v1.3.1 constitue la nouvelle cible normative.** La traduction française est cohérente mais l'anglais prévaut en cas de conflit. Les versions historiques v1.2.1 et v1.3.0 restent intactes. Cette version **annule explicitement la décision v1.3.0 de supprimer le journal causal exhaustif**, son chaînage cryptographique, la provenance autobiographique attestée par le journal et l'audit complet de la vie. Elle conserve la mortalité irréversible, la physique inchangée, l'interdiction des rollbacks, les hypothèses de développement sur 600 pas, la validation opérateur et la validation scientifique finale module par module.

Les Stages 10 et 11 sont terminés et intégrés dans `main`. Le logiciel reste transitoire : un mode mortel existe, mais d'anciens constructeurs instancient encore l'oracle et le banc, tandis qu'un chemin historique de rollback subsiste. **Cette publication ne démontre pas la conformité du code et n'autorise aucune fusion automatique.**

En l'absence de remplacement explicite, conserver les comportements cognitifs, les six phases, l'identité, le tempérament, les mémoires, la planification, l'apprentissage TD et causal, la métacognition, l'exploration, le sommeil, les six passes privées de consolidation, les budgets UC, les droits de propriété des états, l'ordre déterministe et toutes les conséquences du monde des versions v1.2.1 et v1.3.0. Ne pas réécrire les tests scientifiques historiques ni le NO-GO du Stage 9.

**Direction normative des dépendances :** I0 → *son journal causal exhaustif et ses mémoires propres* ; Oracle → *interface de lecture autorisée de la vérité du monde* ; Banc → *observations autorisées, oracle facultatif, journal exporté*. Ni l'oracle ni le banc ne sont obligatoires pour importer, construire ou exécuter I0 en autonomie.

## 1. Principes non négociables

1. **Monde mortel irréversible.** Une transition létale est réellement appliquée une seule fois par la physique `WorldBody`, puis cet individu s'arrête définitivement. Aucune restauration d'une vie validée, deuxième tentative, masque létal ni résurrection.
2. **Journal exhaustif conservé.** Chaque I0 possède son `HashChainedJournal` technique complet et append-only, pendant sa vie et pour l'audit après sa mort. Aucun compactage destructif, expiration arbitraire, filtrage silencieux, suppression automatique ni service de stockage externe obligatoire.
3. **Intégrité cryptographique préservée.** Sérialisation canonique, identifiants d'événement NFC uniques, ordre causal déterministe, chaînage SHA-256 et exportation/vérification reproductibles sont obligatoires, y compris pour les événements qui ne produisent pas d'apprentissage.
4. **Journal consolidé distinct conservé.** Les expériences significatives, souvenirs et connaissances consolidés persistent indépendamment du journal exhaustif. Ce dernier n'est pas une mémoire cognitive omnisciente ; les sources sont filtrées par les projections autobiographiques autorisées.
5. **Aucun oracle ou banc obligatoire.** I0 autonome peut être construit, exécuté, apprendre, dormir, consolider, mourir et journaliser sans importer, initialiser ou exécuter ces services scientifiques externes. Leur indisponibilité ne modifie pas sa cognition ni les conséquences du monde.
6. **Frontière stricte de vérité.** L'oracle lit sans agir sur le monde. Le banc exploite facultativement l'oracle, les observations permises et une exportation de journal en lecture seule ; aucune vérité cachée ne revient dans I0.
7. **Audit indépendant.** Un outil opérateur vérifie un journal exporté sans importer ni démarrer I0, l'oracle ou le banc : structure, hachages, ordre, provenance, commandes/résultats, consolidation et frontières terminales. Il ne prétend pas prouver la vérité physique sans témoin indépendant.
8. **Validation mesurée.** Au moins 600 pas physiques réellement exécutés soutiennent uniquement une hypothèse de développement. Fin de Stage approuvée par l'opérateur ; validation scientifique approfondie séparée des modules en fin de projet.
9. **Pas de régression fonctionnelle pour changer l'architecture.** Conserver toutes les mises à jour Stage 10 post-coupure, la publication atomique, les événements Stage 11 et les souvenirs réels d'I0.

## 2. Cycle de vie et sémantique terminale

Le runtime distingue les états suivants :

| État | Signification | Nouveau pas physique possible ? |
| --- | --- | --- |
| `active` | L'individu et le monde évoluent | Oui |
| `dead` | La physique a atteint une condition terminale et la transition fatale a été validée | **Jamais** |
| `safety_block` | Aucune commande admissible selon la sécurité existante ; **aucune** transition létale n'a été exécutée | Seulement selon un protocole d'autorisation distinct, sans réécriture du passé |
| `technical_halt` | L'intégrité, l'atomicité des entrées ou la publication ne sont plus garanties | Non, tant que l'opérateur n'a pas instruit l'incident |
| `experiment_stopped` | Arrêt du test ou d'une copie par l'opérateur ou le protocole | Non pour cette instance de test ; **ce n'est pas une mort** |

Seuls le monde et le corps déterminent la létalité selon leurs règles existantes et versionnées (par exemple une intégrité nulle ou une zone létale). L'interruption administrative d'une campagne ne devient pas un événement mortel.

La mort survient **lors de la transition physique effectivement validée**. La position finale, l'inventaire, les ressources, les valeurs corporelles, les effets extérieurs et les raisons physiques de la mort restent dans l'état terminal du monde. Après cette mort, aucun cycle cognitif, apprentissage, mise à jour TD, consolidation, repos, récupération, visite d'exploration ni écriture autobiographique n'est effectué. Le banc externe peut relever le résultat et la cause, sans les révéler à l'individu.

Après `dead`, toute émission de commande et ouverture de pas échouent. Aucun mode runtime, mécanisme de copie, fonction de récupération ou contrôle opérateur ne peut ressusciter cette même instance. Une nouvelle naissance ou une copie indépendante possède une identité et une filiation distinctes.

## 3. Contrat exact entre commande et monde

Le Contrôle de l'action reste l'unique émetteur autorisé. Les veto informés, réflexes, validations de commande, évaluations de risque et d'incertitude, règles de danger connu et mécanismes de repli existants demeurent. **Seul le masque protocolaire créé par le rollback létal disparaît.** Le contrôle ne doit pas devenir omniscient par consultation des dangers cachés du monde.

Pour chaque commande primitive admise :

1. Vérifier que l'individu est `active` et qu'un pas physique est ouvert.
2. Préparer le contexte minimal permettant de rattacher la commande à son résultat, **sans checkpoint létal**.
3. Exécuter exactement **une fois** la fonction physique `WorldBody.apply(command, t_monde)`, en conservant ses effets et la consommation des aléas déterministes.
4. Recevoir le résultat, ses conséquences physiques et le prédicat de létalité calculé par le monde.
5. Si le résultat n'est pas mortel, fermer exactement une fois le pas sous `applied`, transmettre les seuls faits vécus autorisés au flux autobiographique transitoire et effectuer l'apprentissage ordinaire au moment prévu.
6. Si le résultat est mortel, fermer exactement une fois sous `dead`, persister l'état final et une mesure terminale externe, puis interdire toute exécution future de l'individu. Aucun commit autobiographique ni apprentissage post mortem.

Aucune branche active `rolled_back`, `masked`, `lethal_retry`, `resume_after_death`, `lethal_checkpoint`, `R_letal_consecutif` ou `R_letal_max` n'est permise. Un réflexe mortel termine immédiatement l'existence ; une décision mortelle ne rouvre pas la Compétition.

**Parité physique :** à état initial, commande, version du monde, scénario et états aléatoires identiques, les conséquences physiques complètes, y compris létales, doivent correspondre à la transition brute du monde de référence. Seul le protocole externe de continuité change.

## 4. Aucune correction rétroactive : transactions et incidents techniques

Le rollback est interdit à la frontière des **états de vie et de monde validés**, et pas seulement en cas de mort. Il est interdit de conserver un chemin caché de restauration pour une entrée de scénario rejetée, un accusé de journalisation défaillant, un évaluateur en échec ou un rappel tardif.

- **Entrées externes :** valider intégralement le lot échu, ses droits, types, bornes et représentation canonique *avant* application. Préparer les effets dans un état privé, puis les publier atomiquement. Un rejet ne provoque aucune nouvelle transition physique. S'il est impossible de garantir qu'une opération partielle n'a jamais été publiée, déclencher `technical_halt`, sans annuler un effet déjà validé.
- **Publication cognitive :** chaque propriétaire prépare ses modifications de manière privée et publie une version cohérente aux frontières des phases. Un candidat non publié peut être abandonné ; une version publiée de S_t, du corps, d'une commande ou d'un apprentissage ne peut être annulée.
- **Consolidation nocturne :** conserver les six passes et leur travail privé, suspendre ou écarter uniquement les travaux **non publiés**. Rebaser sur des deltas causaux **bornés et locaux aux propriétaires** depuis la coupure. Publier atomiquement h et les formes actives correspondantes Q/κ/précisions/modèle causal : tout devient visible ensemble ou rien. Une version h publiée n'est pas inversée.
- **Échec de persistance :** arrêter au point de défaillance plutôt que deviner un état antérieur ou reconstruire partiellement. Après panne, seul le **dernier état courant validé atomiquement** peut être chargé, jamais un instantané historique au choix. Les opérations non validées ne doivent produire aucun effet extérieur, et leur traitement doit être idempotent.
- **Réinitialisation des tests :** une fixture isolée peut créer une *nouvelle* simulation avec une graine initiale connue pour comparer des résultats. Cela ne reprend ni ne ressuscite l'individu précédent.

Les checkpoints de protection avant toute commande, les restaurations périodiques d'anciennes vies, l'annulation des événements externes validés et les tentatives après une commande fatale sont interdits.

## 5. Journal exhaustif, journal consolidé et audit indépendant

### 5.1 Journal causal technique exhaustif (obligatoire)

Chaque I0 possède **son journal causal technique complet, append-only et chaîné cryptographiquement**, depuis sa naissance jusqu'à la transition fatale éventuelle et sa clôture technique externe. Il conserve les événements cognitifs causalement utiles, les perceptions véritablement accessibles, décisions et commandes admises, conséquences physiques et corporelles, apprentissages validés, événements de mémoire et de consolidation, exploration et attribution causale Stage 11, causes de décès, versions et provenances. Les métadonnées techniques restent distinctes de l'expérience vécue. Ce journal appartient à l'infrastructure d'exécution I0 ; il n'est ni une base de données oracle ni une source de perception omnisciente.

- Garantir l'ordre déterministe, la représentation canonique des octets, l'unicité des ID NFC, l'immuabilité des contenus, le chaînage SHA-256 et le contrôle de tous les liens. Rejeter toute suppression, altération ou duplication.
- Conserver les occurrences techniques pertinentes, y compris tentatives rejetées et travaux non validés lorsqu'ils ont effectivement eu lieu, sans les transformer en événements physiques exécutés.
- Conserver l'intégralité pendant la vie et après la mort selon la garde opérateur. Pas de plafond arbitraire lié à la durée, compactage destructif, archivage limité ou dépendance externe obligatoire.
- Autoriser uniquement des optimisations **sans perte** : index, vérification incrémentale, append efficace, lecture partielle, pagination et export canonique complet en lecture seule.
- **Ne jamais utiliser le journal pour restaurer le passé d'une même vie.** Une expérience indépendante sur un autre individu expérimental est autorisée.

### 5.2 Journal consolidé et mémoires cognitives distincts

Le journal consolidé durable (`SlowHistory`/h actif et les enregistrements réels de consolidation), ainsi que les mémoires épisodique, sémantique, procédurale, prospective et de travail, demeurent **différents** du journal exhaustif. La consolidation intègre des expériences significatives ; elle ne purge pas ses preuves techniques. Ses seules entrées cognitives autorisées passent par des politiques versionnées et les `AutoSegmentCommit` attestant les événements effectivement vécus.

La présence d'un événement dans le journal technique n'autorise ni lecture d'un danger caché, ni accès aux champs oracle, ni connaissance du programme futur des scénarios, ni apprentissage posthume. Les clôtures terminales restent auditables de l'extérieur sans mémoire, apprentissage ou consolidation après la mort.

### 5.3 Cohérence des Stages 10 et 11

Conserver au Stage 10 l'index, l'ID et l'empreinte de la coupure figée ainsi que **toutes les mises à jour post-coupure correctement ordonnées** jusqu'à leur intégration par une publication atomique. Maintenir les six passes privées, budgets UC, interruptions au réveil, preuves d'origine et versions cohérentes h/Q/κ/précisions/modèle causal. Le journal exhaustif reste source de garde officielle ; des caches temporaires bornés sont permis **en plus**, jamais en remplacement destructif.

Au Stage 11, conserver la provenance physique, la chronologie exploration/déplacement, la distinction danger connu/inconnu et l'attribution causale. Une trace technique peut attester une mort sans transmettre de nouvelles connaissances au défunt.

### 5.4 Audit autonome et limite épistémique

Fournir à l'opérateur un **vérificateur indépendant, en lecture seule**, sur un export canonique. Sans importer ni démarrer le runtime I0, l'oracle ni le banc, il contrôle schémas/octets, chaîne SHA-256, unicité des ID, indices et ordre, références causales, paires commande/résultat, catégories autobiographiques et tentatives, liens de consolidation et absence d'activité cognitive après décès. Toute sémantique non établie est signalée, jamais inventée ; une altération entraîne un code de sortie non nul.

Cela prouve la cohérence des **enregistrements**, non la vérité du monde physique. Cette dernière demande un oracle autorisé, un témoin externe ou un protocole scientifique distinct. Une chaîne cohérente peut parfaitement contenir une déclaration factuellement fausse.

### 5.5 Externalisation future différée

Une version future pourrait déplacer le journal exhaustif vers un stockage externe seulement après **décision normative et validation opérateur expresses**, mesures de coût, évaluation de sécurité, stratégie sans perte et garantie de vérification indépendante sans dépendance cognitive à l'oracle. **La v1.3.1 n'autorise pas ce déplacement.**

### 5.6 Banc, oracle et trace scientifique séparés

L'oracle lit la vérité autorisée du monde en lecture seule ; le banc peut consulter facultativement l'oracle et contrôler des observations ou exports complets en lecture seule. Il possède ses propres mesures et `EvaluationTrace`, hors du journal d'I0. Les lectures oracle et annotations scientifiques n'entrent jamais dans le journal exhaustif d'I0 sous forme de vérités cachées, dans le journal consolidé ni dans les propriétaires cognitifs. Leur panne n'empêche pas le journal d'I0 et ne déclenche ni rollback ni changement cognitif.

## 6. Sécurité et frontière épistémique

Les sept mécanismes distincts de sécurité de la v1.2.1 §18.1 restent à leur place : réflexe, veto existant, préemption cognitive, R_a, U_a, statut de sécurité de la preuve et statut causal établi. Leurs règles, seuils, droits d'accès et frontières de connaissance demeurent. **Le masque du protocole de rollback létal est supprimé.**

Une zone létale inconnue reste inconnue tant qu'une expérience légitimement accessible ne modifie pas les connaissances d'I0. Une zone mortelle déjà connue peut faire l'objet d'un veto existant ; une zone inconnue peut réellement tuer. Une baie toxique non mortelle enseigne par expérience ordinaire ; une baie mortelle termine l'instance, sans apprentissage posthume.

Il est interdit d'inventer des actions de sauvetage, une intégrité minimale forcée, un apprentissage fantôme, des pénalités de risque rétroactives, un veto guidé par l'oracle ou une mise à jour cognitive cachée par l'opérateur. Le banc et l'oracle mesurent mais n'orientent pas l'apprentissage.

L'absence non mortelle de commande admissible reste `safety_block`. Une incohérence technique reste `technical_halt`. Aucun de ces états n'est une mort, ni un retour temporel.

## 7. Preuves de développement et validation scientifique

Le MVP sépare délibérément **vérification logicielle**, **hypothèse de fonctionnement**, **validation opérateur** et **validation scientifique finale**.

### 7.1 Hypothèse de fonctionnement : 600 vrais pas physiques

Pour chaque Stage ou nouveau module comportemental, exécuter les tests ciblés d'unité, d'intégration et d'invariants, ainsi qu'une campagne transparente couvrant **au moins 600 pas physiques réellement exécutés au total** sur des scénarios et graines déclarés. Privilégier plusieurs trajectoires indépendantes et situations contrastées. Le rapport compact conserve les graines, SHA du code, configuration, version de la physique, observations attendues, résultats et limites connues.

Une mort termine une trajectoire. **Il est interdit de compter des pas hypothétiques après la mort.** Des individus de test nés indépendamment peuvent fournir d'autres vrais pas ; reporter séparément naissances, décès, dénominateurs et survie. Un module jamais sollicité par ces 600 pas **n'est pas démontré**. L'opérateur peut autoriser une exception explicitement documentée si 600 pas sont impossibles ou non pertinents ; cette exception n'est jamais présentée comme une preuve réussie.

Une campagne de 600 pas peut justifier **« hypothèse de développement soutenue / non soutenue / indéterminée »**. Elle ne démontre ni une preuve scientifique absolue, ni la validité de tous les modules, ni une évaluation sur graines cachées, ni un GO rétroactif du Stage 9 historiquement NO-GO.

### 7.2 Fin de chaque Stage

L'agent remet à l'opérateur un dossier de revue minimal : périmètre, versions/SHA, différences contractuelles, résultats et échecs, comptage des 600 pas, comportements significatifs, limites et éventuel essai en conditions réelles demandé. **L'opérateur seul valide la fin du Stage.** Sans validation explicite, il reste `IN_PROGRESS`, même si tous les tests logiciels passent. Quand c'est nécessaire, l'agent demande à l'opérateur d'exécuter ou d'autoriser le test en conditions réelles et n'invente jamais la validation.

### 7.3 Fin du projet complet

Une **validation scientifique est obligatoire à l'achèvement du projet**, indépendamment des hypothèses sur 600 pas et des validations opérateur. Définir une campagne enregistrée avec conditions indépendantes/tenues à l'écart, hypothèses **module par module**, groupes de contrôle, effectifs suffisants, provenance, comportements mesurables, incertitudes et critères de falsification. Évaluer chaque module **séparément**, puis leur fonctionnement intégré, en présentant les résultats positifs, négatifs et indéterminés. Ne conserver que les preuves nécessaires à une revue indépendante, sans archive interne exhaustive.

Les verdicts sont `GO`, `NO-GO` ou `INCONCLUSIVE`. Aucun nombre de tests, aucune fusion de PR ni réécriture rétrospective d'un résultat négatif ne remplace la validation.

## 8. Bases historiques et portes de migration

Les Stages 10 et 11 sont terminés, validés par l'opérateur et intégrés dans `main`. Ne pas recommencer leurs expériences ni réécrire leurs résultats. Conserver leurs SHA et les preuves historiques, ainsi que le NO-GO du Stage 9.

La migration doit avancer par PR révisables : (A) cartographie réelle des dépendances, (B) spécification bilingue, (C) I0 autonome sans chargement Oracle/Banc, (D) vérificateur indépendant d'export, (E) équivalence Stage 10/11 et journal consolidé, (F) campagne logicielle 600 vrais pas. N'intégrer chaque PR qu'après ses propres tests et les règles de protection. Les anciennes branches de **remplacement** du journal complet par un flux borné doivent être réévaluées et ne doivent **pas** être fusionnées telles quelles.

La conformité v1.3.1 ne peut être annoncée avant parité des trajectoires autonome/évaluée et preuves sur les frontières terminales. Aucune modification de la physique, résurrection ou altération scientifique historique.

## 9. Vérifications d'intégration et de non-régression obligatoires

La migration doit démontrer tous les points suivants avant acceptation du runtime :

| ID | Critère observable |
| --- | --- |
| M-01 | Chaque commande admise provoque une seule transition réelle et une seule fermeture de pas, mortelle ou non. |
| M-02 | Zone létale, toxine mortelle, faim/perte d'intégrité, créatures et dangers cumulés conservent leurs conséquences physiques et peuvent tuer. |
| M-03 | Après `dead`, aucun pas, commande, réflexe, décision, apprentissage, TD, fermeture mnésique ou consolidation supplémentaire. |
| M-04 | Absence de checkpoint létal, masque, nouvelle tentative, restauration ancienne ou compensation d'un monde déjà modifié. |
| M-05 | Toute transition physique non mortelle est identique octet pour octet à la référence à commandes et aléas égaux. |
| M-06 | Les veto fondés sur les dangers connus, réflexes, compétition et comportements face à l'inconnu sont inchangés avant la première transition mortelle. |
| M-07 | Le journal complet et le journal consolidé restent distincts et persistants ; mémoire, provenance, raisonnement, planification et apprentissage sont identiques sur les trajectoires non mortelles. |
| M-08 | Le Stage 10 vérifie les coupures et mises à jour post-coupure dans le journal complet, sans perte et avec publication consolidée atomique après interruption. |
| M-09 | Le rejet d'une entrée externe précède la publication et n'annule jamais une transition physique déjà validée. |
| M-10 | L'oracle et les métriques d'évaluation ne peuvent atteindre perception, mémoire, S_t, valeurs, modèle causal ni consolidation. |
| M-11 | Après panne non mortelle, l'état courant persistant se recharge de façon cohérente, sans possibilité de ressusciter une identité morte. |
| M-12 | Le journal causal grandit sans perte avec l'histoire, tout préfixe reste vérifiable cryptographiquement, et l'audit complet est possible après décès. |
| M-13 | Les copies ont leur identité distincte ; une copie morte ou arrêtée ne modifie jamais son parent. |
| M-14 | Tests sur Python 3.11, graines déterministes, empreintes d'état final et smoke test accepté par l'opérateur ; échecs rapportés honnêtement. |
| M-15 | Statuts de Stage et scientifique séparés, règle des 600 pas et validation opérateur effective. |

| M-16 | I0 autonome n'importe ni n'instancie l'Oracle ou l'EvaluationBench et conserve les mêmes décisions et octets de journal interne que son équivalent évalué. |
| M-17 | L'oracle peut être instancié, lu et arrêté indépendamment sans modifier I0 ni le monde. |
| M-18 | Le banc lit observations approuvées et export complet sans devenir une dépendance ou un canal retour pour I0. |
| M-19 | L'auditeur autonome détecte falsification, réordonnancement, omission, duplication, fausse provenance et cognition après décès sans charger I0/Oracle/Banc. |
| M-20 | Une campagne de 600 vrais pas physiques produit un journal complet vérifiable indépendamment, sans troncature ni fuite de vérité oracle. |

Ces vérifications concernent la **conformité logicielle et l'intégration**, pas l'acceptation scientifique finale.

## 10. Remplacements explicites des versions v1.3.0 et v1.2.1

| Règle historique | Autorité v1.3.1 |
| --- | --- |
| **v1.3.0 §0, §1.4, §5, §9 M-07/M-12, §10** et toute suppression du `HashChainedJournal` complet | **ANNULÉE**. Conserver journal exhaustif, chaîne SHA-256, export indépendant intégral et preuves de provenance (§5). |
| v1.3.0 §5.1 état courant unique | Un état courant cohérent peut coexister avec le journal technique intégral append-only ; durabilité ne signifie pas restauration d'une vie passée. |
| v1.3.0 §5.2 queue vécue bornée/deltas post-cut | Optimisations temporaires uniquement, sans supprimer ni remplacer journal intégral ou mémoires consolidées. |
| v1.3.0 §5.3 preuves laboratoire ciblées / v1.2.1 §19 | Traces de banc/oracle **externes et indépendantes** ; journal I0 **complet**, mais exempt de vérité cachée externe. |
| v1.2.1 §17, INV-33/44/49 | **CONSERVÉS** : ordre, unicité, chaînage, intégrité et audit complet, sans rollback. |
| v1.2.1 §10/§15 mémoire/consolidation | **CONSERVÉS** : journal consolidé séparé, source technique complète et mises à jour post-cut vérifiées. |
| v1.3.0 §2–4/§6, v1.2.1 §18 rollback létal | **Mortalité v1.3 conservée** : mort irréversible et journalisation de la transition, sans apprentissage posthume. |
| v1.3.0 §7/§9 validations | **CONSERVÉES** : hypothèse 600 pas, validation opérateur par Stage et campagne scientifique finale indépendante module par module. |
| Transfert éventuel du journal hors I0 | **INTERDIT ICI** : nouvelle spécification et approbation opérateur avec coûts, sécurité et absence de perte. |

En cas de contradiction avec les principes ou §5, la v1.3.1 prévaut. Ne jamais présenter la compatibilité rollback héritée comme déjà conforme.

## 11. Publication, garde et validation

- Préserver intacts les fichiers anglais/français v1.2.1 et v1.3.0 ; publier les deux v1.3.1 ensemble, l'anglais prévalant.
- Classer P0 : dépendances obligatoires Oracle/Banc, restauration mortelle, fuite de vérité, perte d'événements ; P1 : provenance/consolidation/audit incomplet ; P2 : index, visibilité et performances.
- Préserver le NO-GO scientifique Stage 9 et les preuves logiciels déjà validées des Stages 10/11.
- Tester I0 autonome avec imports et constructeurs Oracle/Banc interdits, et comparer les trajectoires et octets du journal en présence d'un observateur externe.
- Vérifier les exports après la mort et détecter falsification, omission, réordonnancement, duplication et provenance erronée ; 600 vrais pas ne sont pas une preuve scientifique finale.
- Respecter la protection de `main` et l'évaluation indépendante de chaque PR. Reporter toute externalisation de journal à une nouvelle décision expresse.

**Cette version fixe la cible ; elle ne prétend pas que toutes les exigences sont déjà implémentées.**
