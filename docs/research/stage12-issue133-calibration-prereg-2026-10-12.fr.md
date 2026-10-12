# EXP-133-B | Profil temporaire et calibration sommeil/consolidation (2026-10-12)

**PRÉENREGISTREMENT AVANT EXÉCUTION, aucune donnée de cette nouvelle campagne connue à cette étape.**
Source cognitive verrouillée : `97f325e309ca19dd90b19644ce6775da6e5ddd95` (PR #135 déjà fusionnée). La campagne expérimentale est gelée par le SHA du commit de son runner avant la première exécution. Référence normative : `docs/architecture/reference/en/mvp-specification-v1.3.1.md` (hérite des P-39/P-40/P-41/P-42 du MVP v1.2.1), et théorie `docs/architecture/reference/fr/architecture-v2.md` §43. Conserver les preuves et résultats contradictoires de PR #134, sans réécrire cette expérience.

**Décision opérateur maintenue** : `w_C = consolidation_weight = 0` est le **profil temporaire de développement**, pas le changement silencieux de tout I0 ni la fin du besoin de consolidation. Les poids strictement positifs ci-dessous sont des traitements expérimentaux ; ne promouvoir aucun nouvel étalonnage sans une décision ultérieure, ni changer la spécification normative.

## Question / mécanisme vérifiable

Dans la campagne antérieure #134 avec véritables six passes, `w_C=0.5` impliquait 47/50 pas dormis et deux publications h ; `w_C=0` impliquait 14/50 pas dormis et une publication h. Ceci prouve une modulation, pas la valeur optimale. Est-il possible de conserver une contribution **non nulle** de consolidation à P-40 sans confisquer la délibération éveillée, avec les six passes payées et utiles ? Les mondes/exemples doivent également permettre d'observer la soif dans un contrôle positif sans agir à la place d'I0.

## Plan figé

**6 poids × 2 conditions du monde = 12 vies mortelles par version Python** : `w_C ∈ {0, 0.05, 0.10, 0.20, 0.35, 0.50}`; mêmes coefficients P-39, w_F, w_N, seuil naturel, limite de durée 2, pression p_cons toujours calculée ; **toutes les vies ont six passes P-42 réellement configurées** (sélecteur de 1 épisode, politique sémantique réelle, plafond UC explicite). Pas d'ablation supplémentaire du sommeil ou de suppression de six passes dans un traitement. `max 80` vrais pas WorldBody/vie, soit 960 pas prévus par version et 1920 avec la réplication Python 3.11/3.12, sans remplacer les morts ou arrêts précoces.

- Monde A `reference_untrained` : corps et disposition Stage11 de référence ; eau en (4,2) et équipement exact historique. Contrôle de couverture négatif (ne pas s'attendre à un succès magique ni à de l'Oracle).
- Monde B `trained_water` : même physique sauf source d'eau placée au point de naissance (2,2) ; un corpus de **transitions réellement appliquées** par un monde Lab distinct avant la naissance donne les exemples nord, sud et boire ; Stage6 `h_eff=2` comme suite de PR #135. Ceci est un contrôle positif logiciel d'accès à `boire`, **pas de l'apprentissage en vie** ni de la généralisation.
- Eau corporelle initiale 20, autres canaux de référence inchangés. Aucune action de l'individu n'est scriptée, aucune observation Oracle ne lui est donnée ; les vrais pas sont sélectionnés par Competition et validés par Action Control. Un nouvel I0 et WAL exclusif pour chaque cellule. L'ordre des traitements est fixé et aucune naissance de remplacement n'est permise.

## Hypothèses et critères a priori

**H133-B1 / pression :** au moins une cellule `w_C>0` a une fréquence de `dormir` strictement différente de `w_C=0` dans le même monde. Décrire la direction et la saturation, sans forcer monotonicité. Tout effet non reproduit entre Python 3.11 et 3.12 est un problème de reproductibilité, pas un succès scientifique.

**H133-B2 / utilité de sommeil :** comptabiliser par vie les checkpoints de passe, les *publications de versions h* et les références réellement consolidées à la fin (ensemble publié), séparément des épisodes encore dans Memory mais non consolidés. Les émissions de sommeil sans passe sont des coûts d'opportunité, pas des consolidations réussies. Une version h publiée sans preuve complète des six checkpoints => FAIL technique.

**H133-B3 / compétition vitale :** comparer, pour le monde B, les commandes `boire` **physiquement appliquées**, le gain d'eau observé au pas suivant et le retard du premier boire ; dans le monde A compter les buts `drink` sans succès sans maquiller l'absence du modèle. Une différence avec zéro sommeil ne suffit pas à établir la santé cognitive. Aucun gain d'eau n'est attribué à une prédiction non exécutée.

**H133-B4 / économie et garde-fous :** chaque cellule rapporte les pas réellement fermés, les refus et reports UC P-42, les sorties par durée maximale, les arrêts et décès, la progression de but et le journal d'intégrité. Éviter le sommeil est *non gagnant* si la consolidation utile s'interrompt ou si l'agent est incapable de répondre à un besoin accessible.

## Règle de décision développement avant résultat

Un `w_C>0` est qualifié **candidat d'évaluation supplémentaire**, pas paramètre recommandé/déployé, si dans les DEUX conditions : (a) chaque vie atteint son terme expérimental sans corruption ni mortalité imprévue, (b) une publication h réellement à six passes est observée pour au moins une vie, (c) part de sommeil ≤ 50 % sur 80 pas dans chaque monde, (d) le contrôle positif `trained_water` exécute `boire` et vérifie le gain hydrique, et (e) budget et journal passent les audits. Si aucun poids positif ne remplit ces critères d'ingénierie, conserver `w_C=0` provisoirement et classer la calibration INCONCLUSIVE ; ne pas ajuster le seuil après données. Même un candidat n'est **pas** une preuve scientifique confirmatoire.

Les verdicts descriptifs sont `SUPPORTED / NOT_SUPPORTED / INCONCLUSIVE`, par hypothèse. Les 80 pas d'une même vie sont corrélés et les six poids sont déterministes ; ne pas calculer une p-value sur 1920 pas. Python 3.12 répète les mêmes conditions pour compatibilité, **pas** six graines indépendantes. Aucune modification du code cognitif en réponse aux observations : les changements exigeraient une nouvelle étude.

## Audit, restitution et limites

Chaque vie écrit un export causal complet, WAL, empreintes config/layout/équipement, manifeste d'exécution, terminal stop/décès/blocage. Un processus d'audit **séparé** du runtime reconstruit depuis ces archives : intégrité physique et chaînage, décompte des actions/commandes, consolidation h/checkpoints et références, sous-totaux par condition, abstentions. Les erreurs et morts restent archivées, pas masquées par un passage vert des autres cellules. Les refus P-42 sont explicitement non nuls ou zéro sans extrapolation. La version de source et tous SHA sont consignés.

**Frontières** : ne certifie ni Stage 9, ni attribution vécue #110, ni acquisition en vie #136, ni atomicité Stage12/M-11. Stage12 conserve `IN_PROGRESS` jusqu'à la validation opérateur. La clôture de #133 exige des critères logiciels démontrés, pas simplement une courbe attractive.
