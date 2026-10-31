# I2 : reconstruction des possibilités sémantiques, sans autorité motrice

**31 octobre 2026. Prototype G2 isolé ; I2 reste non enregistré, non exécutable, sans naissance et sans preuve scientifique.**

Code : `src/i2/modules/option_reconstruction.py` ; tests : `tests/i2/test_option_reconstruction.py`. Le module exploite les **types** `ObservationClaim`, `IntentionTransition` et `SemanticIntention` déjà proposés, sans activer le moteur I1 ni un Lab I2. Ne pas confondre une possibilité sémantique avec une option admise dans Competition.

## Contrat exact

`reconstruct_candidates(claim, transition, current)` est une fonction pure : elle exige une capture déclarée, le résultat de consultation du propriétaire d'intentions sur cette **même** capture, et l'intention qui en résulte ou `None`. Les trois doivent être cohérents en identité, pas physique, but, état `active/suspended`, date de vérification et statut `opened/retained/resumed/suspended/expired/contradicted/goal_changed/idle`. Une combinaison incohérente est refusée. Cela vérifie seulement une **cohérence de données**, pas l'authenticité de leur émetteur.

1. Pour **chaque** signature déclarée accessible dans la capture subjective courante, créer un unique `SemanticCandidate`. Aucune signature issue de l'historique seul, de l'intention suspendue, d'une carte globale ou d'une préférence alimentaire ne crée un candidat supplémentaire.
2. Si l'intention courante est **active, cohérente et déjà vérifiée à ce pas**, ajouter uniquement son `intention_ref` en métadonnée au candidat correspondant. Toutes les autres possibilités, y compris exploration et besoins concurrents, sont conservées. Une intention suspendue ou éteinte ne confère aucune métadonnée à une possibilité.
3. Chaque `candidate_ref` dépend de l'identité déclarée de la vie, du digest canonique de **la capture actuelle** et de la signature sémantique. Le même contexte produit la même référence à la relecture; une nouvelle capture / transition physique fournit une nouvelle référence. L'identifiant d'un candidat **ne dépend pas** de la présence ou non d'une intention. Aucun accumulateur, vote ou score n'est transféré d'une capture à l'autre.
4. Le `CandidateFrame` contient seulement le pas, les références de contexte, le digest du contenu, un `work_correlation_ref` fourni par l'amont, et la liste de signatures. **Il ne contient aucune commande, option motrice exécutable, priorité, Q, score, admission, gagnant, seuil, récompense ou privilège de veto.** L'ordre lexical est une sérialisation stable, et **pas** une priorité. Le résultat peut être vide.

## Sécurité et limites qu'il ne faut pas dissimuler

- `ObservationClaim.digest()` est un hachage de données **non signé**. Il n'authentifie ni la vie, ni la capture, ni ses sources. `IntentionTransition.work_ref` est une **référence de corrélation**, pas la preuve d'un débit UC. Ce module ne débite aucun UC : un futur ordonnanceur devra facturer réellement l'évaluation des possibilités.
- Un enregistrement de l'intention dont les chaînes seraient forgées en accord avec une capture synthétique peut encore passer les vérifications de cohérence. En particulier, `SemanticIntention` ne porte pas aujourd'hui une identité cryptographique de vie : un transfert entre vies avec des références de capture volontairement identiques ne peut pas être rejeté par cette fonction seule. L'autorité M11 et le propriétaire de naissance devront vérifier cet invariant avant intégration vivante.
- La simple présence d'un candidat ne constitue ni un enregistrement dans Competition, ni une évaluation payée, ni un franchissement de seuil, ni une action possible dans le WorldBody. Le futur adaptateur devra reconstruire les options motrices à partir de **nouvelles** perceptions et faire passer chacune par Gatekeeper, Competition puis Action Control, avec veto et facturation normaux.
- Une fonction pure peut être invoquée plusieurs fois sur la même capture, de manière déterministe. Le producteur/registre de la future vie devra empêcher les inscriptions et paiements dupliqués. Ce composant ne certifie **pas** une fin de cycle ou une reprise après COMMIT.
- Aucun apport de connaissance I1, aucune action prescrite `collecter → manger`, aucune expérience H48 injectée. Les tests synthétiques ne prouvent ni amélioration alimentaire ni apprentissage autonome.

## Vérification

`python -m unittest discover -s tests/i2 -p 'test_*.py' -v`

Les 24 nouveaux tests vérifient la complétude des possibilités visibles, l'indépendance des références d'options et de l'intention, la continuité/suspension/résumption, le changement de but, les contradictions, l'expiration, l'absence de privilège, les références étrangères, les rejets de contexte ancien et deux liaisons avec `IntentionIngress` et ses ports **synthétiques**. L'absence de saisie motrice et la neutralité alimentaire sont des invariants de données ; l'efficacité comportementale reste `NOT_ESTABLISHED`.

**Portes : G0 archive I1 PARTIAL (branche non protégée), G1 REVIEW_REQUIRED, G2 prototype hors vie, G3 Scheduler/M11/physique NON INTÉGRÉS, G4-G6 non exécutées. I1 actif, I2 non enregistré.**
