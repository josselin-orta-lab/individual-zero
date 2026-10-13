# EXP #133-H600 : soutenabilité à 600 pas des six passes et lots de six (préenregistrement)

**Date : 13 octobre 2026.** Document gelé avant toute implémentation et tout essai de cette campagne. L'expérience précédente source `82eedf0117e4e4b9766cd91f21d5e5e3de32d62f` a produit 116/119 consolidations sur 240 pas (P6-B6), contre 47/119 (P3-B3), sans perte de veille ni dépassement UC sous les conditions étudiées. Ces données restent exploratoires et ne constituent pas une preuve de régime permanent.

## Hypothèse et risque de réfutation

Bien que les lots de six et six passes par pas aient résorbé le backlog à trois épisodes au pas 240, **le coût P-42 du scan de l'inventaire complet croît avec l'âge**. La file peut donc recommencer à croître après 240 pas. Le test cherche à savoir si la progression reste bornée sur les 600 pas physiques disponibles, sans utiliser plus d'UC, modifier le sommeil ou masquer des morts réelles.

## Conditions préenregistrées

- Un **seul profil** : six passes maximum/par pas de sommeil, maximum six épisodes/lot (P6-B6) ; aucun ajustement adaptatif des caps selon les résultats.
- Deux mondes distincts **et non interchangeables** : (A) `reference_untrained`, eau initiale 20 et équipement de référence ; (B) `trained_water`, eau initiale 20, point d'eau physique pré-établi et modèle d'équipement entraîné AVANT naissance selon l'implémentation déjà disponible dans `run_stage10_issue133_capacity.py`. Le monde B vérifie davantage les besoins vitaux, mais ses trajectoires ne sont pas des réplications statistiques du monde A.
- 600 pas physiques maximaux par vie ; quatre naissances réelles (2 mondes × Python 3.11 et 3.12), mêmes mondes et versions sur les deux Python. La reproduction entre interpréteurs vérifie le déterminisme logiciel, pas une variation de graines/monde.
- `w_C=0` obligatoire, `p_cons_min=0` comme dans le factoriel, mêmes budgets P-42 (100 UC/pas, 600 UC/période, `episode_scan=1`), mêmes six passes sémantiques, même priorité et même mécanique de réveil. Aucune modification des limites architecturales ni accès de I0 à la vérité Oracle.
- Le plafond externe des pas de l'Operator Console passe de 240 à 600 ; les autres paramètres du runtime et le code cognitif restent gelés. Chaque mort réelle peut terminer sa trajectoire avant 600, sans résurrection ou remplissage des pas manquants.

## Mesures, audits et critères de décision

Conserver les quatre ZIP complets, WAL, index de naissance, commits SHA, statut mortel, chemins/empreintes du monde, rapports JSON, toutes les erreurs. L'inspection **hors-runtime** recalcule les chaînes SHA-256, équivalence WAL, unicité/ref d'épisodes, six checkpoints avant h, maximum un h/pas, paiements P-42 et refus. Mesurer par fenêtres de 80 pas (et intervalle final [561,600]) ainsi que sur [1,200], [201,400], [401,600] : création, éligibilité, publications, backlog, âge moyen/P90, UC par pas, UC par épisode, UC de scans/résémantisation, dépenses croissantes dans l'inventaire et éveils/boissons/mouvements.

- **FAIL technique** si une UC dépasse 100/pas ou 600/période, journal ou WAL invalide, duplication, h sans six checkpoints, action physique après mort ou bilan erronément complet après une exception. Ne pas cacher une erreur par un succès de la CI.
- **Hypothèse locale de stabilité soutenue** seulement si la vie atteint effectivement 600 pas, le backlog ne montre pas de pente positive sur la dernière tranche de 200 pas ET sur les pas 521–600, que la veille ne soit pas systématiquement privée dans ce monde et que les preuves passent. Ce seuil est descriptif, non une validation finale du MVP.
- **Soutien partiel/inconclusif** si la mortalité limite l'horizon, si les budgets provoquent reports mais aucun dépassement, ou si l'un des deux mondes échoue le critère ; conserver séparément les résultats de chaque monde.
- **Refutation de soutenabilité** si sur une vie 600 pas la pente de backlog reste strictement positive sur les derniers 200 et 80 pas malgré l'absence de bug technique. Ne pas augmenter UC, `w_C`, modifier arbitrairement l'éligibilité ou réécrire les résultats du factoriel.
- Ne pas déduire la qualité cognitive de l'histoire h de son seul nombre de publications ; la preuve d'utilité est une étude séparée, et M11 Stage12 crash atomicity reste hors du protocole.

**Décision d'activation** : aucun GO scientifique général ni fusion automatique. Toujours laisser #133 ouverte jusqu'à preuve suffisante et validation opérateur. Si le coût O(N) provoque un recul à long terme, proposer une maintenance d'index *facturée* et une équivalence de priorité démontrée, sans supprimer l'historique ni créer des UC.
