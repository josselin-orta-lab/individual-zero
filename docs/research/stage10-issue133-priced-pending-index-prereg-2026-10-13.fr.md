# EXP #133-I1 : index causal et payant des épisodes non consolidés, 600 pas

**Préenregistrement, 13 octobre 2026. Écrit avant toute implémentation de l'index et avant les nouveaux résultats.**

## Fondement documenté
Issue #133 ; PR #139, tête source `0b071014ebcdc9031139b2d846fb430b5e657d81`. Les archives H600 préenregistrées de `12a46813940758439515ed3478f04f403dc48020` : 299 épisodes créés et 242/238 consolidés selon le monde, 57/61 en attente au pas 600. Backlog +28/+27 sur les pas 401-600 ; 6 733/5 872 UC de scan sur 10 827/9 791 UC P-42 (>60 %). Aucune UC supplémentaire n'est autorisée.

## Hypothèse réfutable
Sous le même ordonnancement physique, les mêmes plafonds P-42, le même classement P-42 et le même `w_C=0`, un index versionné ne lisant et réévaluant que les épisodes encore candidats, et **facturant** chaque découverte, examen et retrait, réduit les rescans et peut améliorer le débit. L'amélioration peut échouer si la maintenance, les réveils ou le travail sémantique saturent les créneaux.

## Bras et mondes gelés
- Contrôle **F** : scan incrémental complet déjà intégré, P6-B6 (6 passes maximales / pas réel de sommeil, 6 épisodes / lot).
- Expérimental **I** : index opt-in des seuls épisodes encore non consolidés, même sélecteur, même cut causal et même priorité. **Aucune modification du contrat par défaut F**.
- Mondes distincts A `reference_untrained`, B `trained_water` avec point d'eau et équipement prénatal déjà définis dans `scripts/run_stage10_issue133_horizon600.py`. Même valeur initiale d'eau 20, chaque bras repart d'une naissance autonome distincte ; aucune restauration d'une vie antérieure.
- 600 pas physiques maximum par vie, exécution Python 3.11 et 3.12. En tout 2 bras x 2 mondes x 2 interpréteurs. La paire inter-Python teste le déterminisme logiciel, **pas** la puissance statistique. Deux mondes ne suffisent pas à un GO scientifique général.
- `w_C=0` (intouchable), `p_cons_min=0` inchangé, plafonds `step_slot_uc=100`, `period_capacity_uc=600`, coûts déjà déclarés `episode_scan=1`, `index_maintenance=1`, et tous coûts sémantiques inchangés. Aucun travail d'index ne reçoit une enveloppe supplémentaire ni une remise UC.

## Règles de facturation et d'intégrité préengagées
1. L'inventaire Memory est **append-only**. Utiliser seulement son compteur O(1) avant debit ; pour chaque nouveau record découvert, débiter `episode_scan` **avant** lecture/projection, même si jamais consolidé.
2. Les anciennes projections non consolidées sont détenues dans un propriétaire causal indexé, pas dans une copie technique de vérité Oracle ; les réexaminer pour le classement à chaque nouvelle coupure coûte **`episode_scan` par candidat**. Les épisodes nouveaux peuvent être facturés une fois pour la découverte et une seconde fois pour le classement dans le même cut : conservatisme délibéré, sans décompte négatif.
3. La suppression des candidats choisis après publication h coûte **`index_maintenance` par référence**, débitée **avant** le commit h ; aucun retrait si publication échoue. Si budget insuffisant, rester suspendu au dernier point validé, ne jamais créer une publication incomplète.
4. Rien n'est supprimé de Memory ni du journal causal ; h, six passes, WAL, snapshots propriétaires et décès irréversible conservent leurs garanties. Les nouveaux épisodes après le cut ne peuvent pas intégrer le batch courant.
5. La sélection doit produire **la même liste ordonnée de références** et les mêmes scores qu'un scan intégral payé sur les mêmes épisodes candidats à la même coupure. Tester les répétitions de but, vieillissement, lots incomplets, reprises et refus sous budget nul. Le digest peut différer à cause du nombre de scans facturés, mais **pas** le classement.
6. Aucun événement causal d'index ne peut être caché ; chaque chunk payé et chaque maintenance est traçable. Les archives doivent conserver tous les résultats négatifs/échecs, sans les promouvoir en GO.

## Mesures et décisions gelées
- Traces complètes : SHA source, préenregistrement, WAL et export, six checkpoints de h dans l'ordre, listes de lots et duplications, coût P-42 **par pas et période**, coût découverte/scan/maintenance, reports, épisodes créés, éligibles, consolidés, backlog, âge/P90, sommeil/veille, comportements vitaux.
- Pentes backlog sur [1,200], [201,400], [401,600], et [521,600]. **Soutien local de stabilité** uniquement si le backlog est non croissant sur [401,600] **et** [521,600] et que les besoins vitaux/veille ne sont pas systématiquement privés dans chaque monde.
- **Réfutation** si les deux pentes demeurent positives sur les 200 et 80 derniers pas. **Inconclusif** si mort prématurée ou trajectoire physique non comparable ; pas de remplissage artificiel des pas.
- **FAIL technique** à la moindre UC >100/pas ou >600/période, lecture avant paiement, corruption index/snapshot/WAL, h non atomique, doublon, épisode futur/Oracle admis, restauration après décès, succès revendiqué pour vie tronquée, défaut de classement non expliqué.
- Comparer l'efficacité UC par ref publiée et le pourcentage d'UC de rescans, non seulement le backlog final. La qualité cognitive des hypothèses et la validation M11/Stage12 restent des études séparées.
- Ne fusionner ni l'expérience ni la PR #139 avant CI et évaluation des invariants ; issue #133 maintenue ouverte jusqu'à validation opérateur.

**Aucun ajustement du MVP v1.3.1 autorisé dans cette étude.** Si un coût nécessaire ne peut pas être représenté par P-42, bloquer et demander une décision plutôt qu'introduire une UC gratuite.
