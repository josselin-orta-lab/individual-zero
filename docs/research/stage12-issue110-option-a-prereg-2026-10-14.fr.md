# Stage 12 #110 — Option A : protocole d'implémentation et de falsification préenregistré

Date : 2026-10-14. Décision opérateur : « Lancer la campagne A ». Branche dédiée dérivée de la PR #153, non fusionnée. La présente déclaration précède tout code nouveau d'attribution spatiale et toute campagne physique Option A.

## Hypothèse falsifiable
I0 peut éventuellement produire un jugement faillible `world` relatif à **une tentative spatiale dirigée vers une cible réellement perçue** et entravée par un obstacle directement perceptible, sans lire le résultat de réussite calculé par le registre de but, P-47, l'Oracle ou l'état caché WorldBody. Un `world` valide n'est ni une preuve de responsabilité physique objective ni une propriété d'un simple échec de mouvement.

## Critère spatial candidat (norme proposée, en attente de preuve)
`spatial_progress_v1` : avant toute commande admise, inscrire vie, pas, but, action, position et cible *observées*, direction, distance Manhattan initiale et test strict `distance_after < distance_before`, échéance `t+1`. Si la cible n'est pas perçue ou stable, la capture absente, l'action refusée, la vie différente, le pas annulé ou le critère hors fenêtre : `unknown`, jamais `failure`. Le jugement d'agence n'accède ni à la comparaison de distances du registre, ni au booléen `outcome`.

## Producteur subjectif candidat
Action Control conserve la propriété de GoalAgencyService. Pour un mouvement admis, copie efférente et perception avant/après sont nécessaires. `self` est admissible seulement si la variation de position perçue concorde avec le mouvement voulu et la cible. `world` exige un indice extérieur directement perceptible sur la cellule **de la direction tentée**, déjà disponible pour I0, et une absence de progression, sans convertir l'échec lui-même en cause. `unknown` pour obstacle non perçu, cible absente, commande non admise, autre direction, indices contradictoires, ou attribution non spécifique. Une commande qu'Action Control/Safety interdit ne peut pas être forcée dans l'expérience pour obtenir `world`. Si ce garde-fou rend `world` impossible en comportement autonome, résultat **NO-GO pour la voie proposée**, pas de fabrication.

## Plan expérimental préfixé
1. Audit de la politique de sécurité et des captures réellement visibles ; produire des cas de contrôle négatif obstacle non perçu, mauvaise direction, cible non perçue et commande refusée.
2. Implémenter en réutilisant le registre Stage12GoalProgressLedger et le producteur GoalAgencyService ; aucun registre mutable concurrent ; contrats versionnés et coûts UC positifs à la naissance.
3. Vérifier indépendamment les deux preuves (résultat spatial et jugement) dans un auditeur externe, avec journaux rechaînés après falsification de la passabilité, de la direction, de la cible et du reçu UC.
4. Tests M-11 : WAL, restauration froide atomique, `os._exit` si état persistant modifié, absence de réanimation, pas de cognition durant sommeil ni après mort.
5. Campagne exploratoire avec mondes contrastés accessibles, graines et horizon préfixés avant exécution ; au moins une vie de 600 pas si mortalité et protocole le permettent. Comptage des actions admises, tentatives empêchées, préengagements, jugements `self/world/unknown`, UC, couples admis/appliqués, refus et diagnostics.
6. Régression Stages 9–12 et compatibilité Python 3.11/3.12. Stage9 reste NO-GO.

## Conditions d'arrêt et verdict
Une preuve perceptive insuffisante, l'interdiction systématique par Action Control des mouvements connus bloqués, un coût UC refusé ou une absence de jugement autonome produisent `unknown` / diagnostic `None` et un rapport d'impossibilité. Aucun seuil du détecteur n'est réduit. Ne pas déclarer un détecteur validé par la seule présence d'un champ `agency` ou par des fixtures. Aucune PR fusionnée ni issue clôturée sans réception opérateur.
