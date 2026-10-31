# I2 : premier propriétaire d'intentions sémantiques (prototype G2)

**Source-only, inactive, non-executable, no scientific GO.** La proposition d'architecture est `docs/architecture/proposals/i2-continuity-and-learning-contract-2026-10-31.md` (G1 REVIEW_REQUIRED). Aucune vie I2 n'existe et `config/engine-registry.json` reste inchangé.

## Contrat effectivement implémenté

- `src/i2/modules/intention_continuity.py` : seul registre sémantique, un emplacement, état `active` ou `suspended` ; aucune option motrice, seuil, gagnant ou commande.
- `FirstPersonCapture` : entrée déclarée par un futur runtime, avec étape physique, référence de capture, but actif, signatures sémantiques accessibles et contradictions subjectivement observées. **Le module ne sait pas prouver leur origine** : références et contenu sont des affirmations du fournisseur externe.
- `open` : accepte uniquement une possibilité visible et un but actuel, avec référence de preuve, TTL bornée de 1 à 64 pas physiques et référence de travail cognitif. Le plafond de 64 est un garde logiciel de prototype, pas une calibration scientifique I2.
- `observe` : une seule transition par nouvelle capture ; continuité lorsque la signature reste accessible ; suspension quand elle n'est plus visible sans prétendre qu'elle a disparu du monde ; retour si elle redevient visible ; abandon en cas de but différent, contradiction signalée ou expiration.
- `export_state` et `from_untrusted_snapshot` : schéma exact de données ordinaires, vérifications de chronologie et d'identité sémantique, refus des champs supplémentaires dont `command`, `winner` ou `accumulator`. **Ce n'est PAS un M11 signé, durable ou récupérable.**

La référence `work_ref` est seulement un identifiant de corrélation qui doit être rapproché d'un **vrai débit UC** par un runtime futur. Ce code n'effectue aucune dépense et ne valide aucun reçu UC. La continuité ne produit aucune autorisation d'action, ni accumulation Competition ni protection/veto.

## Tests logiciels isolés

`python -m unittest discover -s tests/i2 -p 'test_*.py' -v`

La suite comprend les gardes du squelette non enregistré et 17 tests du propriétaire pur (déterminisme, visibilité, changement de but, disparition apparente, contradiction, expiration, rejeu, anomalies d'entrée, sérialisation, tentative de contamination motrice). Les tests restent des preuves logicielles **locales et ciblées**, pas des vies, et la CI exacte du nouveau SHA doit être vérifiée séparément.

## Portes non franchies

- G0 : protection contre suppression/réécriture de la branche archive I1 et conservation indépendante auditable restent à attester.
- G1 : revue architecturale et scientifique substantielle encore nécessaire.
- G2 : une boucle cognitive SQLite synthétique v4 est testée, mais aucun Lab fonctionnel, propriétaire moteur ni expérience première personne réelle n'existe.
- G3 : pas de comptabilité UC authentifiée, d'Action Control, de corps, de mort, de M11 ni de reprise froide pour I2.
- G4-G6 : pas de préenregistrement comparatif final, de nouvelles vies, de preuve d'amélioration ni de promotion.

Le vérificateur `tools/assess_engine_proposal.py --generation I2 --json` doit rester `BLOCKED` tant que le moteur et le Lab indépendants sont absents.