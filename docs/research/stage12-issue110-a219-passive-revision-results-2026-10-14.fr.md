# Stage12 issue #110 : A2.19, révision prudente de l'agence après déplacement passif

**14 octobre 2026. Verdict Stage12 PARTIAL.** Préenregistrement avant code : `6daa30ecb508f433307594d06cd06fab3e7eb1a6`. Exécution de référence au SHA `74909e2dbfcc59cb837ba43759cd4d932ecf6325`. [CI A2.19 #38637933554](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38637933554) **SUCCESS sous Python 3.11 ET Python 3.12**. La dernière CI du commit ajoutant ce rapport reste à confirmer indépendamment.

## Résultat physique

**32 mondes séparés, 64 transitions réellement appliquées**, huit seeds `101..108` (les deux Python répliquent les mêmes seeds et ne doublent pas leur effectif). Chaque monde utilise une première action de déplacement, suivie d'un véritable `WorldBody.apply(PrimitiveCommand("attendre", {}), t_monde=2)`.

| Condition extérieure réelle | Mondes | Attribution originale | Candidat `reconsider_to_unknown` |
|---|---:|---|---:|
| Premier déplacement volontaire réussi, seconde attente immobile | 8 | `self` | 0 |
| Premier déplacement volontaire réussi, seconde attente avec déplacement passif extérieur | 8 | `self` | **8** |
| Première commande empêchée puis corps relocalisé extérieurement, seconde attente immobile | 8 | `self` | 0 |
| Première commande empêchée puis corps relocalisé extérieurement, seconde attente avec déplacement passif extérieur | 8 | `self` | **8** |
| **Total** | **32** | **32 `self`** | **16** |

Les paires initialement normales et physiquement confondues ont des captures accessibles **t1/t2/t3 identiques** dans chacune des 16 paires. Le vrai service de première personne conserve son premier `self`. La sonde externe n'a accès qu'à ce jugement, à sa preuve perceptive, à la commande `attendre` et aux captures t2/t3. Les labels d'intervention et effets physiques restent exclusivement du côté du banc d'audit.

## Ce que signifie « réviser »

La sonde reconnaît **16/16 déplacements passifs** et s'abstient dans **16/16 témoins immobiles**. Elle ajoute un événement référencé de **reconsidération à `unknown`**, sans réécrire l'ancien jugement. Ce signal montre que, dans ce monde, un corps peut bouger sans commande motrice de déplacement.

**Mais 8/16 révisions suspectent à tort un premier jugement qui était physiquement correct**. Les 8 autres doutent d'un premier jugement réellement faux. Puisque ces histoires sont perceptivement indiscernables, aucune règle de première personne n'est fondée à classer rétrospectivement les premières causes comme `self` ou `world` avec certitude. Le candidat apprend au mieux à diminuer son assurance sur une explication, pas à connaître la cause passée.

La robustesse minimale de la sonde est examinée par refus d'un indice avec la même référence, d'une référence vide, d'une observation au mauvais pas, d'une commande non `attendre`, d'une attribution initiale non `self` et de la **duplication d'un événement append-only**. Ces garde-fous restent internes au laboratoire et ne constituent ni une garantie WAL ni une charge UC cognitive.

## Verdict et étapes restantes

- **H1 et T1–T3 : PASS borné** pour la matrice physique préenregistrée et l'indiscernabilité appariée.
- **T4 : PASS laboratoire uniquement** : reçu de révision séparé, preuve et anti-duplication ; aucun journal mortel ou owner cognitif de production n'a été étendu.
- **T5 : PASS reproductibilité** des mêmes seeds sous deux Python.
- **T6 : PASS quant au code de cette PR** : changements limités au laboratoire, à la documentation et au workflow.
- **Étendue : 0 vie autonome, 0 révision de cognition intégrée, 0 nouvelle paire GA-06**, aucune compétence alimentaire distale démontrée. Ces résultats ne sont pas des métriques de sensibilité et de spécificité sur une population ouverte de vies.

**Conclusion architecturale :** une révision utile peut être *épistémique* (réduire l'assurance) sans être une correction causale vérifiée. Pour aller au-delà d'un candidat de laboratoire, il faudrait une décision normative sur la portée du jugement (agence de la commande proximale vs responsabilité du résultat distal) et sur une mémoire non destructive des révisions. Une campagne ON/OFF autonome avec vrais coûts UC, journal/WAL, sécurité, mortalité et critères de compétence serait ensuite nécessaire.

MVP normatif v1.3.1 inchangé. **Stage12 PARTIAL, issue #110 OPEN et pas de réception opérateur**. Cette expérience n'autorise aucune fusion de vérités du banc vers la cognition ni changement de seuil `2+2/12`.
