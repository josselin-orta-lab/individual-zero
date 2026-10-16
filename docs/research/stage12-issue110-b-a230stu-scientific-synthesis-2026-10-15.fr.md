# A2.30-S/T/U : frontière de l'acquisition d'information, prédiction alimentaire et responsabilité

**15 octobre 2026.** Dossier de clôture **technique de la sous-campagne S/T/U**, non clôture du Stage6/Stage12 ni de la campagne A2.30 complète. Norme `docs/architecture/reference/en/mvp-specification-v1.3.1.md` **inchangée** ; issue #110 OPEN ; PR #190 (S) et PR #192 (T/U) DRAFT, empilées sur #189/#188/#187 et ses dépendances. Aucun changement dans `src/i0`, Stage9/DC-05, l'Oracle ou les budgets UC.

## Observé, démontré, non démontré

### 1. Observation versus connaissance avant le risque

**S**, préenregistrée au commit `906a74eb`, [CI #38740205272](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38740205272) **PASS**, mesure physiquement **36 mondes et 104 transitions**. Les états initiaux des causes cachées sont observationnellement identiques. `attendre` ne permet pas de distinguer la toxicité avant `manger`, ni une zone mortelle cachée avant de s'y déplacer. Chez les survivants, la conséquence devient accessible **après** exposition ; une victime terminale ne peut pas effectuer de capture vécue postmortem. En revanche, une première attente peut rendre visible une variation de faim/soif, car ces variables corporelles font partie de la perception autorisée. 20 paires sur 36 deviennent accessibles aux deux survivants, 16 ne le sont pas dans le parcours testé avant le décès de l'une des branches.

### 2. Branches plausibles versus résultat alimentaire vécu

**T**, préenregistrée au commit `1df0a78f`, [CI #38741620906](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38741620906) **PASS**, entraîne son modèle exclusivement avec les **48 mondes d'entraînement scellés de P**, antérieurs aux 40 nouveaux mondes T. **40 mondes et 132 transitions physiques**, 20 paires avec/sans attente.

Une lecture shadow *optimiste* de la présence d'une seule branche vivante gagnant de la nourriture suggère 20 possibilités par bras, mais seulement 12 mondes par bras obtiennent physiquement un gain alimentaire suffisant **avec survie**. Dans les 8 autres mondes par bras, soit le fruit est létal (4), soit le gain de nourriture est nul (4). Le catalogue connaissait déjà une issue terminale possible : le critère shadow conservateur refuse de **certifier** toute trajectoire dans cette matrice, mais ce veto **ne constitue pas** un repas ni un apprentissage utile par lui-même.

L'attente préalable ne discrimine aucune des cinq causes latentes du fruit avant ingestion et n'améliore aucun des 20 résultats appariés. Elle consomme au contraire **0,5 énergie, 0,5 nourriture et 0,2 eau** supplémentaires dans les paramètres physiques contrôlés.

### 3. Audits externes sans falsifier la conscience d'I0

**U**, préenregistrée après résultats S/T mais avant son code (`107c7534`), [CI #38742839615](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38742839615) **PASS après correction explicite de deux contrôles négatifs**. L'auditeur reconstitue sans les scripts S/T/P les 4 branches du corpus P et recalcule **les 76 mondes et 236 transitions d'origine**. Cela **ne compte aucune nouvelle exécution physique** : S (36/104) + T (40/132) sont les expériences originales. Les six fichiers JSON d'archives de S/T ont les mêmes octets entre Python 3.11 et 3.12, avec SHA-256 documentés. Les cas falsifiés (effets, morts, perception postterminale, fausse sécurité, faux progrès) échouent. U vérifie la cohérence des fichiers, **pas** indépendamment l'application physique, qui relève des runners S/T.

## Diagnostic H1, H2 et H3 à ce point

- **H1, couverture exacte limitée** : soutenue pour les 121 recherches sans première arête dans A2.30-E et son analyse G/H ; S/T ne modifient pas leur naissance ni leur Equipment. Ces expériences affinent plutôt **quand une nouvelle donnée physique deviendrait accessible** et si une sonde préalable serait sûre.
- **H2, impossibilité/horizon** : allonger la profondeur de BFS ne résout pas les racines sans transition modélisable. Les résultats S/T montrent par ailleurs que des conséquences dangereuses non perçues peuvent rester compatibles avec des préfixes envisageables, sans démontrer d'impossibilité physique générale.
- **H3, planificateur ou représentation** : aucun défaut BFS additionnel observé ici, car S/T n'exécutent pas `SimulatorPlanner.search` et **ne prétendent pas tester de plans complets**. Le seul audit Stage6 consiste à vérifier l'accès aux commandes candidates `collecter` et `manger` lorsque leurs préconditions sont effectivement visibles. Un modèle de branches n'est pas remplaçable silencieusement par un `EquipmentModel` déterministe.

**Planifier ≠ sélectionner une commande ≠ agir ≠ vivre un résultat ≠ l'attribuer causalement.** Ici les décisions de shadow sont des objets scientifiques calculés par le banc. Aucun jugement subjectif de l'I0 réel n'a été créé, modifié ni validé.

## Décision et prochaine expérience discriminante

**A2.30 PARTIELLE ; S/T/U PASS technique à portée limitée ; prédicteur cognitif NO-GO ; Stage12 PARTIAL et #110 OPEN.** La couverture et l'incertitude sont mieux décrites, mais la planification alimentaire sûre, les risques non observés et l'agence causale subjective restent non validés. Les PR scientifiques ne doivent pas être fusionnées au seul motif que les tests sont verts et les exigences normatives du MVP ne peuvent pas être modifiées sans approbation de l'opérateur.

**Prochain test prioritaire proposé A2.30-V :** mesurer *hors runtime I0* si des préconditions **véritablement visibles** (espèce, ressource, passabilité, voisin et mémoire d'effets corporels déjà vécus) permettent de construire un **ensemble explicite de preuves de conséquences**, de conserver des branches dangereuses connues et de représenter `cause_latente_non_identifiable` pour toute incertitude cachée. Comparer ensuite ce contrat à une décision shadow d'abstention/planification sur des mondes *nouveaux*, non représentés dans le corpus P, avec calibrage des faux positifs potentiellement mortels et du coût de l'information. S'il faut ajouter une nouvelle sonde du monde ou modifier la définition de l'Equipment, **soumettre un amendement motivé du MVP à l'opérateur AVANT intégration** plutôt que de transformer la capacité d'observer une conséquence *après coup* en certitude anticipée.
