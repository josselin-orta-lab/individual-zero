# Stage12 #110 : A2.11b, ablation prospective de corpus Equipment physiquement observé

**Préenregistrement 14 octobre 2026, avant toute modification comportementale, tout nouvel entraînement et toute CI A2.11b.** Référence `main@24ef3feefb0527aaa7bfd18b75e3ad0d2f81a24e`. Issue #110 OPEN, Stage12 scientifique PARTIAL et non reçu. Norme v1.3.1 **inchangée**.

## Pourquoi cette expérience

L'audit [A2.11](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38609000117) a observé **372 diagnostics `incomplete_model`** sur les 16 vies 42 pas archivées, **zéro refus explicite d'UC Planning**. Cela ne donne **pas** le taux exact de couples état × commande manquants. Le préentraînement de naissance alimentaire contient **quatre transitions réelles externes** seulement (nord, est, collecter, manger). Le modèle est strict : `SHA256(SimulationState, PrimitiveCommand)` complet, aucune extrapolation de corps, de jour/nuit ou de ressources inconnues.

## Plan comparatif prospectif

**H1** : élargir **avant la naissance** le corpus d'exemples `WorldBody.apply` observables peut diminuer certaines recherches `incomplete_model` sans permettre d'affirmer la conséquence d'une commande jamais vécue. **H0** : aucun progrès de planification ou de consommation en environnement A2, éventuellement à cause de la correspondance exacte trop restrictive.

Témoin **OFF** : corpus canonique d'origine de 4 transitions, inchangé. Traitement **ON** : corpus étendu exclusivement par des épisodes physiques **nouvellement instanciés, externes et prénataux**, à configurations corporelles distinctes `food` et commandes de déplacement, attente, collecte, ingestion, perturbation explicitement observée dans le monde externe. Jamais de copie d'une trace future d'une vie I0 ni d'accès `ground_truth` dans I0. Ne pas mélanger corps de `restored` et `sustained` dans un même modèle ; chaque paire reçoit des corpus alignés sur la même naissance. Les scénarios doivent être fixés avant de voir les résultats.

Matrice pilote : **2 profils** (`restored/sustained`) × **2 environnements** (`free/A2` avec blocage after-admission t2, levée before-step t4) × **2 corpus** (OFF/ON) × **1 gain extrinsèque fixé** (`1.6`) = **8 vies neuves ×42 pas max**, donc au plus **336 pas réels uniques**. Rejouer sur Python 3.11/3.12 (mêmes identités, répétition technique seulement). Contrôles négatifs : prédiction d'une commande physiquement jamais entraînée **doit lever `LookupError`** ; deux entrées avec résultat contradictoire doivent être rejetées. L'intervention n'ajoute pas de politique alimentaire spécifique, ni action forcée, ni nouveau modèle généralisant.

## Critères préalables

**T1** : corpus OFF=4 transitions, corpus ON augmenté d'au moins 4 nouveaux reçus `WorldBody.apply` provenant de mondes indépendants prénataux ; version/SHA d'Equipment distincts, et aucun recouvrement de provenance d'une vie test. Tout nouveau résultat prédit doit avoir une correspondance exacte dans le corpus. Conserver `unavailable` sinon.

**T2** : journaux canoniques/WAL/survie et interventions A2, alimentation, planification, UC et sécurité vérifiés par auditeurs indépendants, sans erreur et sans restauration après mort. Aucune action spéciale imposée au sujet.

**C4** : progrès alimentaire **uniquement** si `effects.ate` puis augmentation vraie de `body.food`. Exiger au moins **une vie sustained/A2 avec repas en ON** et **zéro dans son OFF** pour un bénéfice exploratoire A2; sinon l'hypothèse alimentaire est **FAIL ou INCONCLUSIVE** selon preuves. Déclarer l'effet `restored` et les éventuelles régressions.

**C3** : mesurer les sites réels et comparaisons OFF/ON. Si repas supplémentaire ON, retenir au moins 50 % des sites du témoin et des actions exploratoires après la satiété ; si aucun repas supplémentaire, exiger au moins 80 % des sites témoins.

**C1/C2/C5** : les jugements `self/world/unknown` ne doivent pas hériter des résultats de l'entraînement externe ; fenêtre 12 et seuil 2 succès +2 échecs restent inchangés. Évaluer P-48 indépendamment de l'amélioration de prédictions.

**C6/C7** : vie de 42 pas n'établit pas stabilité longue ni généralisation inter-seeds. Ne lancer 600 pas que si un véritable bénéfice observé justifie le test, avec nouveau protocole. Les écarts de flottants cross-Python restent distincts de la reproductibilité physique.

**C8** : aucune modification de Stage9, Oracle, Action Control, UC, mortalité, journal causal ni de la norme v1.3.1. Si le traitement nécessite une révision de contrat architectural, l'arrêter et soumettre la demande à l'opérateur.

## Ordre des travaux

(1) Tests de provenance corpus et contrôle adversarial des clés, (2) fabrique prénatale expérimentale OFF/ON avec observables physiques, (3) campagne 8×42, (4) rapport séparant technique et comportement, (5) intégration seulement si conformité prouvée. Ne jamais optimiser des paramètres après observation des résultats; conserver les résultats négatifs. **Stage12 restera ouvert en attente de réception opérateur.**
