# A2.30-J : préenregistrement d'une couverture pré-natale des premières actions

**15 octobre 2026. Préenregistrement avant code, observations et résultats A2.30-J.** Dépendances : PR #187 au SHA `72523d4193e68ea1241b4d57003e75d43b1f446c`, A2.30-I et les diagnostics A2.30-G/H. Le résultat négatif A2.11b (petit enrichissement prénatal) est connu et **ne doit pas être réinterprété**. L'issue #110 reste ouverte, Stage12 PARTIAL, aucune modification de `mvp-specification-v1.3.1.md`.

## Problème et hypothèses

Dans la cohorte A2.30-E, 121/121 recherches `incomplete_model` n'ont **aucune** première arête prédictible; 620 demandes initiales refusées, dont 468 commandes exactes jamais démontrées et 152 états complets jamais démontrés pour des commandes pourtant connues. Une augmentation de l'horizon n'aide pas **ces états-là**. Le fait que le planificateur retourne `incomplete_model` ne démontre pas que la première action physiquement utile à manger est absente du monde.

- **J1, effet technique :** des transitions nouvelles, **réellement appliquées sur des mondes prénataux indépendants**, enrichissent le corpus exact sans extrapoler la sécurité d'autres états et augmentent au moins certains premiers pas prédictibles.
- **J2, transfert comportemental :** l'amélioration de couverture accroît les propositions alimentaires ou les vrais actes de collecte/ingestion de la cohorte nouvellement née, plutôt que simplement faire baisser le nombre brut d'arêtes indisponibles.
- **J3, effet nul persistant :** le corpus enrichi reste disjoint des états réellement rencontrés ; les refus exacts et comportements subsistent.
- **J4, absence de régression :** aucune fuite Oracle, généralisation de toxicité, altération du moteur ActionControl, UC, mortalité, sommeil, jugements B ou chaîne WAL. Les résultats de Stage9/DC-05 doivent rester inchangés.

## Matrice fixée avant toute naissance

Quatre profils de faim préexistants `restored`, `sustained`, `episodic`, `marginal` × obstacle OFF/ON (blocage A2 préexistant t2, retrait t4) × modèle **OFF** exact-baseline / **ON** exact enrichi = **16 vies indépendantes** (`a230j0` / `a230j1`) de **32 pas physiques maximum**, soit **512 pas projetés** sous réserve de mortalité ou d'arrêt, qui seront décomptés réellement. Réutiliser l'environnement, les moteurs B et le paramétrage A2.30-E : profondeurs Stage6 = 3, progressive planning + prospective prefix + revalidation, `extrinsic_gain=1.6`, GA-06 hérité désactivé et dual-scope B né activé. Aucune commande forcée pendant les vies.

L'intervention est **exclusivement prénatale** : en OFF, les 4 transitions historiques issues de `build_prebirth_equipment`; en ON, les mêmes 4 transitions **plus** des enregistrements exacts `EquipmentCorpusExample` indépendants du corps I0 cible, avec un modèle `FrozenTableEquipment` immuable et une identité SHA/corpus distincte. Les exemples supplémentaires sont appliqués réellement via `WorldBody.apply` et `EquipmentCorpusRecorder`, sous le même monde configuré et le même plan fixe pour chaque profil, sans consulter aucune future exécution de I0 :

1. Sonde indépendante à t1 de **`attendre`, `dormir`, `boire`**, et mouvements `north/south/east/west` : un nouveau monde WorldBody par commande, dont `north` peut dupliquer sans conflit l'entrée historique.
2. Trajectoire de **8 attentes** consécutives `attendre`, t1..8, dans un monde indépendant.
3. Trajectoire de **4 sommeils** consécutifs `dormir`, t1..4, dans un monde indépendant.
4. **Trois chemins temporels retardés** avec 1, 2, 3 attentes initiales respectivement, suivis de `north`, `east`, `collecter berry_a`, `manger berry_a` dans des mondes indépendants.
5. Un chemin `dormir` puis `north`, `east`, `collecter berry_a`, `manger berry_a`.
6. Une boucle spatiale `south`, `east`, `north`, `west` dans un monde indépendant.

Le traitement doit préserver **octet pour octet les prédictions** des quatre clés historiques et **refuser toujours** toute entrée non démontrée, notamment `manger berry_b`. Aucun apprentissage depuis des journaux de vies cibles, un Oracle ou des conséquences futures. Le nombre d'exemples, doublons, collisions, versions et empreintes sera déclaré avant les résultats des vies ; toute contradiction d'une même clé exacte invalide le traitement.

## Métriques et décision prévues

**Critères de validité préalables :** les 16 identités distinctes, vraies transitions et journaux WAL vérifiés; corpus OFF/ON distincts par profil, sous-échantillon historique conservé; tests adversariaux inconnus inchangés; absence de toute injection `set_body` ou commande opérateur pendant la vie; aucun rejet de l'observateur; deux Python répètent **les mêmes cohortes**, sans doubler N.

**Critères primaires :** pour chaque bras/paire et horizon de 32 pas réellement exécutés : nombre de recherches Stage6 nouvelles, `incomplete_model`, `no_predictable_first_step`, `root_available_edges`, `root_unavailable_edges`, `plan_found`, `partial_progress`, avec nombre de recherches comme dénominateur pour limiter l'effet du replan et sommeil. La réduction de refus d'arêtes n'est pas une preuve que leurs connaissances étaient nécessaires.

**Critères secondaires :** propositions, commandes `collecter/manger` réellement émises, ingestion physique vérifiée par auditeur indépendant P-48, gains corporels, premier/dernier `food` perçu, morts et pas survivants, comptes UC refusés, jugements B proximaux et distaux (ces derniers jamais crédités `self` sans preuve causale personnelle). Explorer la parité OFF/ON sous les mêmes conditions, mais **aucune égalité forcée** des décisions entre les bras : elles peuvent diverger dès que les modèles diffèrent.

**Contrastes préenregistrés :** J1 fortement soutenue si une différence de couverture exploitable est mesurée sur des recherches réelles; J2 seulement si des actes alimentaires vécus, vérifiés indépendamment, augmentent et les coûts/risques ne s'aggravent pas; J3 soutenue si pas de gain de couverture des premières arêtes et pas de gain alimentaire. Toute régression physique ou scientifique entraîne FAIL borné, non une rationalisation a posteriori. Sans efficacité ou si le bénéfice reste minime, ne pas agrandir arbitrairement le corpus ou changer Stage6.

## Limites et clôture

Une CI verte ne prouve pas la représentativité, la validité scientifique finale ou l'attribution causale subjective. Ce protocole **ne change pas** la politique de Stage6, les contraintes normatives, l'inférence de danger Stage9 ni les seuils Stage12. Les 512 pas projetés ne constituent qu'une campagne de développement, sans preuve scientifique définitive ni réception opérateur. **A2.30 reste PARTIELLE** tant que la comparaison et ses limites ne sont pas documentées.
