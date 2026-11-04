# I2 P4 #982 — audit des occasions d'exploration payantes

**Statut : analyse observationnelle uniquement.** Fondée sur [l'issue #982](https://github.com/josselin-orta-lab/individual-zero/issues/982), enregistrée après l'acceptation et la fusion de la [PR #981](https://github.com/josselin-orta-lab/individual-zero/pull/981) dans `main` au commit `178142f80a2429efa06d3145ee7f323bde457b5c`. Les six vies historiques #981, leurs réglages, résultats et interprétations restent inchangés. Aucun comportement, score, action ou mode de naissance n'est ajouté.

## Question scientifique

Dans le monde natif à trois lieux, la nourriture de la source est physiquement accessible depuis le passage. Pourtant aucune des six vies #981 n'a visité la source, et les variantes d'apprentissage ciblée et multidimensionnelle ont produit exactement les mêmes actions dans chaque monde.

On doit distinguer : destination adjacente physiquement possible, action de déplacement **offerte** localement, score de déplacement au **maximum de la compétition**, égalité admissible entre déplacements, destination encore inconnue du seul individu, bonus inné effectivement attribué, action réellement admise et nourriture ultérieurement consommée. Ces propositions ne sont pas équivalentes.

`origin_novelty_tie_scores` n'intervient que si le meilleur score strictement positif est partagé exclusivement entre au moins deux déplacements, avec un seul déplacement vers un lieu inédit, un autre vers un lieu connu, exploration innée positive et absence de réflexe urgent. Si manger, dormir, boire ou une autre action domine ou figure dans cette égalité, l'exploration est inéligible. Cette règle demeure **inchangée** ici.

## Contrat d'analyse en lecture seule

`src/i2/modules/native_exploration_opportunity.py` lit les événements cognitifs déjà payés et les événements physiques déjà commis par **l'unique propriétaire SQLite**, préalablement soumis à l'audit froid natif. Le module n'ouvre pas de base, ne possède pas de journal et ne produit ni moteur ni nouvelle décision. Il reconstruit le lieu et les lieux visités exclusivement depuis les déplacements effectivement admis. Les transitions illégales, les offres de déplacements non adjacents, les séquences corporelles discontinues, les candidats mal formés, les doublons et les preuves d'exploration incohérentes sont refusés.

Les scores enregistrés sont **postérieurs** au bonus de nouveauté : seul un suffixe de provenance effectivement signé `:visited-versus-unvisited-adjacent-tie` autorise à soustraire son point pour reconstituer l'entrée du mécanisme inné. Aucun score moteur n'est modifié dans le journal. La classification rend `NO_POSITIVE_TOP`, `SINGLE_TOP`, `NONMOVE_TIED_TOP`, `ONLY_ONE_MOVE`, `NO_UNSEEN`, `MULTIPLE_UNSEEN`, `URGENT_REFLEX`, `EXPLORATION_DISABLED` ou `ELIGIBLE`. Ces raisons n'expriment aucune connaissance d'une qualité alimentaire cachée. Les pressions des quatre besoins et l'état de réflexe viennent du corps effectivement enregistré **avant** le choix.

La synthèse par vie sépare notamment : présence effective au passage, offre du déplacement vers la source, déplacement au meilleur score, bonus éligible, mouvement choisi, source effectivement visitée, nourriture localement offerte à la source et nourriture réellement consommée. L'absence de repas ne signifie pas absence de connaissance du lieu.

## Vérification des six vies figées

Le test `tests/i2/test_native_exploration_opportunity_982.py` inclut des contrôles purs (égalité entre deux déplacements, égalité avec manger ou dormir, destination inconnue, destination déjà visitée, réflexe urgent, preuve manquante, offre non adjacente), ainsi qu'une vie native authentique non scriptée, auditée indépendamment avant lecture du journal.

Un contrôle supplémentaire recrée **six nouveaux individus distincts** sous les lois de naissance strictement identiques à celles de #981, sans ajouter de règle. Avant de compter leurs occasions d'exploration, chaque vie est auditée à froid ; son empreinte FNV-1a des 128 actions payées est comparée aux empreintes des traces #981 acceptées sous Python 3.11 et 3.12 :

| Vie | Empreinte moteur #981 |
| --- | --- |
| Danger passage, sans apprentissage | `5bfb9ce5` |
| Danger passage, apprentissage ciblé | `fc211253` |
| Danger passage, apprentissage corps entier | `fc211253` |
| Danger source, sans apprentissage | `1c57e03c` |
| Danger source, apprentissage ciblé | `0301463b` |
| Danger source, apprentissage corps entier | `0301463b` |

Ceci n'est **pas** la récupération de la base SQLite originale, détruite avec le dossier temporaire de l'ancien test, ni une nouvelle réplication scientifique indépendante. C'est une vérification de reproduction déterministe des **actions historiques**, complétée par un nouvel observateur des occasions de compétition. La sortie `I2_P4_EXPLORATION_OPPORTUNITIES_982` résume les catégories pour les six nouvelles exécutions, une fois les empreintes concordantes. Les traces originales #981 restent figées.

## Interprétation et décision suivante

Un lieu invisible n'a pas de valeur alimentaire anticipée. La présence d'une occasion de déplacement ne garantit ni sa sélection ni la réussite d'une recherche de nourriture. Même un bonus correctement appliqué ne démontre pas un apprentissage de survie. Le diagnostic doit expliquer pourquoi la source n'a pas été visitée, sans lui conférer de récompense cachée.

Si la plupart des offres restent dominées par les besoins non spatiaux, on pourra **ensuite** préenregistrer une nouvelle hypothèse sur l'arbitrage inné exploration/besoins, en conservant des mondes où l'exploration est dangereuse et des témoins sans apprentissage. **Aucune modification de cette compétition n'est autorisée par ce diagnostic.** Les conclusions G3/H3/M11, l'activation d'un moteur indépendant et la survie adaptative demeurent `NOT_ESTABLISHED`.

## Discipline CI

L'incrément comporte un observateur, ses tests et cette note, sans changement du runtime, de la physique, des modes de naissance ou des propriétaires. Une seule CI ordinaire à SHA exact, avec les matrices Python 3.11/3.12 et les six contrôles des frontières de génération et de non-activation. Les six reproductions ajoutent du temps à une validation déjà lourde ; aucun deuxième workflow ni réajustement des paramètres biologiques ne doit être lancé pour obtenir un résultat favorable.
