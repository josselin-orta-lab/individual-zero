# Individual Zero — Spécification normative MVP v1.3.0

**Titre :** Mortalité réelle, conséquences irréversibles du monde, persistance minimale et preuves proportionnées aux étapes  
**Langue faisant autorité :** anglais  
**Date :** 11 octobre 2026  
**État du document :** **CIBLE NORMATIVE APPROUVÉE, NON ENCORE ACTIVÉE SUR LA BASE DE DÉVELOPPEMENT**  
**Condition d'activation :** validation explicite par l'opérateur des Stages 10 et 11 terminés, suivie d'une décision de migration enregistrée. Aucune activation ni fusion automatique.  
**Référence historique :** [MVP v1.2.1](mvp-specification-v1.2.1.md), conservée sans modification.

## 0. Autorité et frontière de migration

Ce document définit le **prochain contrat du MVP**, sans prétendre que le logiciel actuel y est déjà conforme. Pendant le développement des Stages 10 et 11, leurs branches, tests, expériences et Pull Requests restent régis par leur référence v1.2.1 déclarée. Ils ne doivent être ni réécrits, ni rebasés, ni fusionnés du seul fait de cette publication.

Une fois la condition d'activation satisfaite, la v1.3.0 devient la référence d'implémentation. Elle **remplace les obligations incompatibles de la v1.2.1** concernant le rollback létal, les checkpoints, les journaux exhaustifs, le replay intégral de l'histoire et la validation scientifique à chaque étape de développement. Toutes les autres règles cognitives, comportementales et physiques de la v1.2.1 demeurent applicables, sauf remplacement explicite ci-dessous : les six phases cognitives, l'ordonnancement déterministe, une seule capture physique par pas, l'isolement de l'oracle, le tempérament, S_t, la compétition, les réflexes, les veto informés, Valeur et Besoins, Planification, le raisonnement causal, l'apprentissage en ligne, les cinq mémoires, le sommeil, la consolidation et la physique ordinaire du monde.

La suppression d'une infrastructure de journalisation ou d'instantanés **n'autorise pas la suppression d'une fonction cognitive qui en dépend**. Avant son retrait, une source équivalente des mêmes informations légitimement accessibles doit être établie.

En cas de divergence entre les textes français et anglais, la version anglaise v1.3.0 prévaut. Une batterie de tests logiciels réussie ou une approbation de l'opérateur ne constituent jamais, à elles seules, une validation scientifique.

## 1. Principes non négociables

1. **La mortalité est réelle.** Une transition physique létale s'applique au monde et au corps et termine irréversiblement cet individu. Elle n'est ni annulée ni transformée en blocage de sécurité.
2. **Les conséquences du monde sont inchangées.** Déplacements, obstacles, dégâts, nourriture, eau, baies toxiques, dangers, créatures, consommation des ressources, rythmes temporels et conditions terminales restent ceux de la version de physique applicable en v1.2.1. Aucune immunité cachée, limitation artificielle des dégâts, intervention de secours ou filtre létal n'est ajouté.
3. **Aucun rollback de la vie, quel que soit le mode.** Il est interdit de restaurer, rembobiner, retenter ou rejouer un état de vie déjà validé pour éviter une conséquence, y compris la mort. Aucun masque de commande ni reprise de délibération après un résultat létal.
4. **Pas d'archive exhaustive des événements.** Ni l'individu ni le laboratoire ne conservent durablement chaque contribution, version de S_t, événement de cycle interne ou transition physique sur toute une vie. Seuls subsistent l'état causal courant nécessaire, les connaissances et épisodes pertinents, des données transitoires bornées et des preuves ciblées.
5. **Non-interférence cognitive.** Le détecteur externe de mort, le banc d'évaluation, l'oracle et la persistance ne peuvent fournir à I0 de nouveaux faits de danger, récompenses, croyances, souvenirs, modifications de politique ou décisions. La perception ordinaire et les règles de sécurité déjà établies sont conservées.
6. **Publication atomique, jamais réparation du passé.** Les modifications sont préparées et validées avant publication. Abandonner un *candidat privé non publié* ne constitue pas un rollback de la vie. Une transition physique validée ne peut être compensée par une modification rétroactive de l'histoire.
7. **Preuves par niveaux.** Une campagne reproductible de 600 pas physiques réels soutient une **hypothèse de fonctionnement**, pas une preuve scientifique définitive. Chaque Stage requiert la validation de l'opérateur. La validation scientifique approfondie, module par module, est exigée en fin de projet.

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

## 5. Persistance minimale et mémoire sans journal complet

Les exigences de journal technique append-only couvrant toute la vie, d'historique complet `JournalEvent`, de chaîne de hachage de chaque événement, de projection historique `AutoSegmentCommit`, de replay intégral obligatoire et d'instantanés historiques périodiques sont **supprimées du contrat runtime**.

### 5.1 État causal courant

Le runtime maintient de façon persistante **un seul état causal logiquement courant, cohérent et versionné**, mis à jour à des points de synchronisation sûrs. Il contient tout ce qui permet à ce même individu de continuer sans modifier son comportement : identité/filiation ; tempérament et versions d'équipement ; monde/corps et scénario externe ; représentations mnésiques ; intentions et plans ; S_t et tampons autorisés ; apprentissages et formes actives ; accumulateurs et horloges ; fatigue/sommeil et état privé de consolidation ; cartes d'incertitude et de calibration ; états aléatoires ; statut terminal.

Exiger une sérialisation canonique, des contrôles de version/schéma et une empreinte d'intégrité. Un fichier temporaire de remplacement, un tampon privé de commit ou une transaction atomique de base de données sont possibles ; ce ne sont **pas des instantanés historiques successifs librement restaurables**. Aucune archive indéfinie des anciens états courants.

Tout snapshot ancien non reconnu est refusé ou migré par une procédure explicite et hors ligne approuvée par l'opérateur, jamais interprété comme une permission de restaurer un mort.

### 5.2 Expérience vécue et apprentissage en ligne

Donner à Mémoire et Consolidation une **interface d'événements vécus transitoire et versionnée** contenant *exactement* les observations, contributions, décisions, actions et résultats physiques non mortels auxquels ces modules avaient légitimement accès en v1.2.1. Préserver l'ordre causal, les frontières de phase, les identifiants de provenance, la propriété des données, la déduplication et l'origine réellement vécue des connaissances.

Le tampon d'événements en vol est borné au pas ou à l'épisode actif et libéré après accusé d'intégration par les consommateurs responsables. Conserver les souvenirs épisodiques/sémantiques/procéduraux/prospectifs utiles, sans copier la totalité du journal technique. Aucun fait brut d'oracle ni résultat hypothétique non exécuté.

**Rebasage de consolidation :** les mises à jour en ligne postérieures à la coupure restent accessibles sous forme de deltas locaux aux propriétaires, bornés et sans perte, ou d'une méthode équivalente démontrée, jusqu'au commit atomique. Ne jamais effacer les deltas avant consommation. Si ces garanties ne tiennent pas, **ne pas retirer encore le journal**.

### 5.3 Preuves de laboratoire et diagnostics

Le banc peut conserver des compteurs agrégés bornés, résultats terminaux, observations de test normalisées, manifestes de versions/graines, empreintes et données scientifiques ciblées. La durée de conservation et tout échantillonnage diagnostique sont définis par protocole. Une expérience peut préserver des **mesures sélectionnées et justifiées**, mais pas réintroduire par défaut un journal exhaustif de l'existence.

Des empreintes causales calculées en flux, les comparaisons d'états finaux et des exécutions jumelées avec manifestes d'entrée remplacent la reconstruction systématique des événements passés. Le déterminisme local et l'isolement causal restent obligatoires. Aucun replay historique complet ne doit être revendiqué s'il a été supprimé.

### 5.4 Copies

Une copie demandée explicitement part d'un état causal **courant disponible et cohérent**, reçoit une nouvelle identité et une filiation, puis vit indépendamment. Il n'y a ni copie de secours implicite ni bifurcation périodique automatique. Un individu décédé ne peut redevenir vivant sous sa même identité. Les copies jetables de la batterie suivent leur protocole d'arrêt et ne réinjectent pas leurs apprentissages dans leur parent.

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

## 8. Coexistence des Stages 10 et 11 et condition d'activation

Les Stages 10 et 11 continuent sans interférence jusqu'à la fin du travail de leurs agents **et leur validation par l'opérateur**. Leur référence reste la v1.2.1 pendant ces travaux, même si ses exigences de rollback et de journal seront remplacées après la migration.

La migration ne peut commencer que lorsque :

1. Le Stage 10 fournit ses SHA et périmètres finaux revus, avec ses branches/PR d'intégration le cas échéant.
2. Le Stage 11 fournit ses SHA et périmètres finaux revus.
3. L'opérateur consigne explicitement la validation des Stages 10 et 11 ainsi que les exceptions éventuelles.
4. Un audit de dépendances en **lecture seule** est relancé sur la base d'intégration finale et établit les impacts code/tests/docs, conflits de versions et risques.
5. L'opérateur autorise **une PR d'implémentation de migration distincte**. Ne jamais fusionner ni greffer automatiquement la PR expérimentale de mortalité existante.

La PR #31 constitue seulement une **preuve de développement** : ce n'est pas un remplacement validé, et ses hypothèses devront être réévaluées après convergence des branches des agents. Il n'est pas autorisé de réécrire la physique, les tests historiques ou les résultats pour faire passer cette PR.

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
| M-07 | Mémoire, provenance des épisodes, preuves causales, plans et apprentissage en ligne sont conservés sur les trajectoires non mortelles équivalentes après remplacement du journal. |
| M-08 | Aucun delta post-coupure n'est perdu par la consolidation ; la publication reste cohérente après interruption du sommeil. |
| M-09 | Le rejet d'une entrée externe précède la publication et n'annule jamais une transition physique déjà validée. |
| M-10 | L'oracle et les métriques d'évaluation ne peuvent atteindre perception, mémoire, S_t, valeurs, modèle causal ni consolidation. |
| M-11 | Après panne non mortelle, l'état courant persistant se recharge de façon cohérente, sans possibilité de ressusciter une identité morte. |
| M-12 | La croissance des données techniques reste bornée indépendamment du nombre total d'événements passés, hors connaissances apprises et preuves scientifiques sélectionnées et autorisées. |
| M-13 | Les copies ont leur identité distincte ; une copie morte ou arrêtée ne modifie jamais son parent. |
| M-14 | Tests sur Python 3.11, graines déterministes, empreintes d'état final et smoke test accepté par l'opérateur ; échecs rapportés honnêtement. |
| M-15 | Statuts de Stage et scientifique séparés, règle des 600 pas et validation opérateur effective. |

Ces vérifications concernent la **conformité logicielle et l'intégration**, pas l'acceptation scientifique finale.

## 10. Carte des remplacements explicites de la v1.2.1

Ce tableau est normatif : après activation, en cas de conflit, la règle v1.3.0 prévaut.

| Ancien emplacement | Règle v1.3.0 |
| --- | --- |
| Principes P6, P9, P12 ; rôles Journal/Instantanés (§1–2) | Persistance cohérente de l'état courant et preuves minimales ; abandon des obligations de journal/historique/replay complets. |
| §3.4 `EXÉCUTER_PAS`, `REPRENDRE_DÉLIBÉRATION`, flèches de rollback et diagramme §3.5 | Remplacement par le §3 ci-dessus ; commande fatale appliquée une fois, puis `dead`, sans nouvelle délibération. |
| §4.6 entrées externes et §5 propriétaires journal/snapshots | Entrées déterministes et propriété causale préservées ; staging atomique des entrées et état courant à la place de l'enregistrement exhaustif. |
| §10.2, §10.6 mémoire issue du journal et traces des accès | Interface bornée des événements vécus autorisés, plus mémoires persistantes ordinaires. |
| §15.6–15.8 consolidation, rebasage, transactions | Six passes sémantiques, travaux privés, deltas locaux sans perte et publication atomique ; plus de dépendance à un journal technique complet. |
| §16 compteurs techniques et journal | Conservation des UC logiques et de la métacognition sans archivage de chaque variation. |
| **§17.1–17.8**, DC-08, DC-09, S-01 replay/snapshots intégrals | Remplacement par §§4–5 et 9 ; aucune restauration générale d'historique, journal complet, checkpoint létal ou replay intégral obligatoire. |
| **§18.2–18.6**, diagramme I, V-24/V-25/V-40 | Remplacement par §§2–3 et 6 ; la mort physique est terminale. |
| §19 journaux et banc | Isolation de l'oracle et métriques indépendantes ciblées, sans collecte totale des événements. |
| **§20, §21** critères de fin de Stage et matrice de tests | Remplacement par §7 et vérifications §9 ; invariants non incompatibles conservés. |
| DC-02 masque protocolaire ; DC-14 blocage après mort ; DC-15 segments restaurés ; DC-16 IDs ; glossaire | Suppression des tentatives/masques létaux, veto/repli ordinaires conservés, segments terminaux et provenance unique sans journal global. |
| INV-27, INV-28, INV-29, INV-33, INV-39, INV-44, INV-49, INV-52 exigeant journal/rollback/checkpoint | Remplacement par M-01 à M-15 et les invariants restants d'oracle/contrôle compatibles. |
| Paramètre P-55 fréquence des instantanés et R_letal_max | Retirés du MVP vivant. Un paramètre historique ne peut réactiver un chemin de rollback. |
| Toute autorisation de rejouer la vie d'un mort comme si c'était la même instance | Interdite. Les tests indépendants réinitialisés par graines et les copies expérimentales distinctes sont permis. |

Le NO-GO scientifique historique du Stage 9, les résultats négatifs déjà enregistrés, la provenance scientifique et la chronologie des expériences **restent inchangés**. L'adoption de ce MVP ne certifie rétrospectivement aucun Stage.

## 11. Gestion des changements et publication

- Conserver les fichiers anglais et français v1.2.1 intacts comme référence historique.
- Publier ensemble les versions anglaise et française v1.3.0, avec les mêmes contrats sémantiques.
- **Ne pas** modifier `main`, intégrer le code des branches Stage 10/11, clore les PR, modifier les résultats d'expérimentation ou lancer la migration du seul fait de cette publication.
- Consigner les SHA finaux des Stages 10 et 11, les validations opérateur, les différences de base et les preuves de migration revues avant de déclarer la v1.3.0 **ACTIVE**.
- L'[audit de migration après Stages 10 et 11](../../../research/audits/post-stage10-11-mortal-mvp-audit.md) décrit les vérifications en lecture seule et la porte de lancement. L'audit doit être actualisé sur le SHA réel de la base d'intégration figée.

**État actuel : cible normative définie ; aucune activation, autorisation de migration ou conclusion scientifique implicite.**
