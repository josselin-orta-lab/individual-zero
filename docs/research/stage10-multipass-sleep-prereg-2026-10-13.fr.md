# EXP #133 : plusieurs passes facturées par pas de sommeil (préenregistré)

Source cognitive gelée : main `040f49832f6861edfbb606203b5446ffa633052d`, avant modification. Norme MVP v1.2.1 §15.8 : dans un créneau de consolidation, continuer les passes dans la limite du budget réellement disponible. Aucun travail hors d'une commande dormir appliquée, aucune accélération du temps simulé.

Hypothèse : avec la même politique de sélection incrémentale et les mêmes plafonds et tarifs P-42, un nombre maximal de passes par pas de sommeil de 3 au lieu de 1 améliore le nombre d'épisodes réellement consolidés sur une vie de 240 pas, sans dégrader les contraintes de budget ni publier h avant six checkpoints. Le traitement n'impose pas d'action à I0 : `w_C=0` est conservé conformément à la décision opérateur.

Deux individus mortels distincts par interpréteur Python 3.11 et 3.12 ; 240 transitions physiques maximales par vie, même monde et équipement initial ; profil 1 versus 3 passes maximales. Auditer les interruptions, le nombre de commandes dormir, les débits UC, les épisodes créés, sélectionnés, consolidés et en attente, les six checkpoints ordonnés et les WAL/exports. Critère d'amélioration : plus de références consolidées, à sommeil comparable, et aucun refus de budget non déclaré. Une absence de gain est NOT_SUPPORTED. Conserver les deux résultats même négatifs ; aucune réception opérateur ni validation scientifique finale n'en découle.

L'ancien comportement (une passe) demeure le défaut. Un changement au-delà de ce profil expérimental appelle une décision distincte après lecture des preuves.
