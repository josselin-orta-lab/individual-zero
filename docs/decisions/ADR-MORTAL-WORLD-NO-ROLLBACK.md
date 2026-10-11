# Décision d'architecture vNext : monde mortel sans rollback

**Statut : implémentation initiale, validation et migration non terminées.**

## Décision

Individual Zero est mortel. La physique du monde continue d'appliquer exactement les mêmes dégâts, dégradations, règles de déplacement, ressources, dynamiques corporelles, dangers et conditions terminales que dans la référence v1.2.1.

- Une commande admise est exécutée **une seule fois** par `WorldBody.apply`.
- Si la transition est non létale, le pas se clôt avec `applied`, l'apprentissage et la mémoire restent alimentés par les informations effectivement vécues.
- Si la transition est létale, le résultat physique est **conservé** ; le pas se clôt avec `dead` et l'instance ne peut plus exécuter de nouveau pas, même si le corps dispose encore de valeurs numériques observables.
- Il n'y a ni checkpoint létal, ni restauration du corps ou du monde, ni masque des commandes létales, ni nouvel essai, ni reprise de la délibération.
- Une mort est distincte d'un `safety_block` : le second n'arrive qu'en cas d'absence de commande admissible. Le blocage technique ne résuscite personne.
- La mort n'est pas interprétée comme une intention suicidaire sans preuve autonome d'intention.
- Les réflexes, veto fondés sur la connaissance disponible, valeurs, besoins, pénalités de risque et d'incertitude continuent à fonctionner ; aucune anticipation omnisciente du moteur physique n'est ajoutée à la cognition.
- Les événements techniques liés à la mort peuvent rester dans les mesures externes ; ils ne sont ni expériences apprises ni observations accessibles à l'individu après son dernier pas.

## Hors périmètre de cette première implémentation

La suppression du journal technique exhaustif et le nouveau contrat de persistance constituent un chantier **distinct**, à mener avec un flux autobiographique temporaire et un registre minimal des mises à jour nécessaires à la consolidation. Ne pas supprimer ces infrastructures à l'aveugle : des modules d'apprentissage s'y réfèrent encore.

Les copies expérimentales et les snapshots de diagnostic ne sont pas des moyens de réanimer l'instance décédée. La restauration des états dans les *tests isolés* et l'annulation d'une transaction technique invalide sont des notions différentes du rollback létal ; leur maintien ou remplacement reste à auditer.

## Invariants et vérification

1. Une commande admise implique une transition physique unique et une clôture unique du pas.
2. Les effets matériels et corporels d'une transition létale restent présents après la clôture.
3. Une instance morte refuse toute commande ou ouverture de pas ultérieure.
4. Aucune boucle de décision supplémentaire n'est lancée après `dead`.
5. Aucune mémoire/autobiographie posthume ou récompense d'une mort ne peut être produite.
6. Les transitions non létales restent identiques, à contexte et aléas constants.
7. Les causes et comptes de mortalité sont consultables par le banc d'essai, sans fuite vers la cognition.
8. Les états terminaux d'une copie ne sont jamais réinjectés dans son parent.

## Migration indispensable

- Migrer les tests Stage 2, Stage 3, Stage 4 et Stage 11 qui imposent `rolled_back`, `lethal_rollbacks`, des masques ou une continuation après décès.
- Mettre à jour les fixtures, sondes, métriques, rapports, spécifications et schémas qui supposaient la ré-exécution.
- Auditer les compatibilités de snapshots historiques et refuser explicitement les anciens états de protocole impossibles à interpréter.
- Valider le moteur sur Python 3.11 : syntaxe, tests unitaires et tests de non-régression à graines fixes, y compris mort par zone, poison, faim, créature et dangers cumulés.
- Documenter une nouvelle version normative. La spécification v1.2.1 est conservée **inchangée** comme référence historique ; cette décision la remplace uniquement pour le comportement mortel vNext.

**Les changements ne sont pas prêts à fusionner tant que les tests ne sont pas migrés et exécutés.**
