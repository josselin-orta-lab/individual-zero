# Stage 12 / #110 : préenregistrement A2.5, diversité physique, P-48 et nourriture

**Date :** 14 octobre 2026. **Base figée :** `main` à `e94e86a868594ed3dac8bee2cec74a8b419876e5`. **État scientifique de départ :** PARTIAL, détecteur `attribution_bias` non évaluable dans 0/16 vies de la dernière campagne instrumentale. Ce texte est committé **avant** le nouvel instrument et avant l'exécution A2.5.

## Hypothèses et distinctions

- **H1 (diversité)** : l'intérêt géographique instrumental (opt-in) accroît des préengagements sans réduire substantiellement les cellules physiquement atteintes. Un même nombre de mouvements ne prouve pas une diversité conservée.
- **H2 (alimentaire)** : le sous-objectif `spatial_distance` ne prouve pas la compétence alimentaire. Seuls une commande `manger`, un effet physique `ate` et, séparément, une évolution du niveau `food` attestent les phénomènes correspondants. Ne pas relabeliser `spatial_distance` en satiété.
- **H3 (P-48)** : les alternatives exploration autonome et progression instrumentale peuvent légitimement partager **une même référence de frontière**. Ce partage est rapporté comme une source informationnelle commune, jamais comme deux preuves causales indépendantes. Les références répétées **au sein d'une même évaluation** sont une erreur ; des valeurs numériques égales pour des frontières différentes ne prouvent ni perte ni gain de discrimination causale.
- **H4 (attribution)** : le signal P-48 reste distinct des jugements `self/world/unknown` et des paires consommées. Le census ne crée aucun nouveau couple.

## Cohorte, contrôles et logiciel

Reprendre sans modification la fabrique et les conditions de `scripts/run_stage12_issue110_instrumental_ab.py`, à l'état de la base ci-dessus : 4 profils de nourriture `restored/sustained/replenished/urgent` × monde `free/A2` × intérêt instrumental OFF/ON, soit **16 vies indépendantes** de **42 transitions physiques maximum** et **672 pas maximum**. Les mêmes conditions et identités de cohorte seront exécutées sous Python **3.11 et 3.12**, sans compter chaque interpréteur comme une vie indépendante. Les scénarios A2 (obstacle après admission au pas 2 puis levée au pas 4), les budgets, le sommeil, `w_m=0.75`, les seuils de Competition, les contrats Stage12 et la physique restent inchangés. Les seeds/identités, la configuration et les empreintes Equipment sont celles imprimées par la fabrique existante et archivées par le runner; **aucune diversité aléatoire supplémentaire n'est inventée**.

Nouvelle instrumentation **externe en lecture seule** des journaux canoniques et des preuves WAL déjà auditées : (i) positions initiales perceptibles et positions finales physiques, avec nombre de sites distincts et trajets; (ii) mouvements tentés/réussis/bloqués; (iii) commandes `manger`, effets `ate`, augmentations nettes observables de `body_after.food` après un pas précédent; (iv) `stage11_intrinsic_evaluation` : nombre de signal IDs distincts, collisions intra-évaluation, recouvrement inter-options au même pas/cycle, égalités numériques; (v) recensement original des engagements, jugements et paires. Une augmentation nette corporelle est distincte de la quantité ingérée, et la première transition sans état corporel antérieur dans ce flux n'est pas utilisée pour un delta artificiel.

L'auditeur ne doit pas être importé par I0 ; aucun `Oracle` ni banc d'évaluation n'est injecté en amont. Les fichiers bruts, le SHA de code, les comptes et les erreurs restent conservés, y compris les résultats nuls.

## Critères fixés a priori

1. **T1, intégrité** : 16/16 vies de 42 pas et audits physique, WAL, objectif, agence et A2 réussis; les tests négatifs de recensement P-48 refusent les doublons internes. Un résultat technique rouge arrête toute conclusion comportementale positive.
2. **C3, diversité exploratoire** : comparer chaque paire ON/OFF de même profil/monde. Critère exploratoire de conservation : au moins **80 %** des sites physiques distincts dans chacune des 8 paires, et aucun profil où l'intérêt ON supprime tous les mouvements physiquement réussis alors que OFF en a. Les sites sont ceux du monde vécu, pas seulement le registre borné d'Exploration.
3. **C4, alimentation** : rapporter séparément `manger`, `ate` et hausses nettes du `food` ; aucun PASS alimentaire sur la seule distance spatiale. Au moins une ingestion `ate` vérifiée et un gain net corporel dans une vie ON seraient nécessaires à une **première preuve positive locale**, mais ne démontreraient pas une compétence alimentaire généralisée.
4. **C5, P-48** : zéro répétition d'un même signal **dans** une évaluation; rapport explicite des signal IDs partagés **entre** options concurrentes. Pas de PASS de discrimination de l'agence sur ces seules identités informationnelles.
5. **C1/C2/C6** : l'ancien seuil `2 success + 2 failure` dans une même fenêtre de douze reste inchangé; si absent, calibration non évaluable. Pas de conclusion de stabilité à 600 pas à partir de 42.

Une comparaison dérivée 3.11/3.12 doit indiquer les métriques identiques ou divergentes. L'identité binaire des journaux n'est **pas** une exigence prétendue remplie ; la dérive Stage8 IEEE-754 déjà signalée demeure possible.

## Décision après expérience

Publier les résultats positifs, négatifs et indéterminés **par vie et par paire**, sans passer opportunément d'une mesure à une autre. Ne corriger le modèle que sur défaut reproductible et isolé; aucune retouche normative v1.3.1. Stage12 reste PARTIAL tant qu'une série de jugements `self/world` calibrable, le progrès alimentaire vécu et la stabilité à plus long terme n'ont pas été vérifiés. L'opérateur conserve seul la réception finale.
