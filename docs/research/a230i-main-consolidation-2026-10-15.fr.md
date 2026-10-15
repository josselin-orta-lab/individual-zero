# Consolidation A2.30-I : diagnostic passif des premières arêtes de Stage 6

**Référence normative inchangée :** `docs/architecture/reference/en/mvp-specification-v1.3.1.md`.

**Portée de cette intégration :** récupération contrôlée des modifications de `src/i0/modules/stage6_planning.py` et des deux tests spécifiques depuis la PR scientifique [#187](https://github.com/josselin-orta-lab/individual-zero/pull/187), sans fusionner ses ancêtres empilés #184–#186, ni modifier les modèles prédictifs, la politique de sécurité, le Stage12 ou les paramètres du MVP.

## Matrice de traçabilité

| Expérience | Résultat démontré | Décision | Exigence | Code / test | État |
| --- | --- | --- | --- | --- | --- |
| A2.30-E/G/H | 121/121 recherches incomplètes avec 0 arête de racine prédictible; parmi 620 refus initiaux, 468 commandes non entraînées et 152 états complets jamais observés pour une commande connue | Diagnostiquer le manque exact de premier pas, non l'impossibilité physique | Exposer les compteurs réellement observés, maintenir `incomplete_model` | `stage6_planning.py` et `test_stage6_a230i_first_step_diagnostic.py` | Implémenté dans cette branche; validation sur son SHA exigée |
| A2.30-I | Relecture technique de 192 pas, décisions et sensations identiques à la base; hashes d'événements différents en raison des diagnostics | Observation seule, aucun nouvel état cognitif ni modification de décision | Un `no_predictable_first_step` requiert une racine épuisée et toutes arêtes indisponibles | `test_stage6_a230i_first_step_diagnostic.py`, `test_stage6_a230e_discriminants.py` | Réexécuter sur `main` consolidé |
| A2.30-J/K | Corpus prénatal enrichi, 4 → 4 ingestions et 0 différence de commande dans les 8 paires | **Pas de déploiement** de corpus élargi sur ce seul critère | Préserver les données vécues et la prudence de Stage9 | Aucun changement de comportement | NO-GO |
| A2.30-L/M/N/O/P–Z | Effets exogènes/toxiques cachés, collisions de conséquences et risques d'un prédicteur optimiste | **Pas de prédiction déterministe inférée de la similarité visible** | Conserver l'abstention et les frontières I0/Oracle | Aucun changement de `Equipment` / `Stage9` | Recherche partielle; modèle prospectif NO-GO |
| A2.18–A2.30 / option B | Compatibilité d'une prédiction avec une observation ≠ responsabilité causale du résultat | Ne pas créer d'attribution distale `self` depuis ces diagnostics | Respecter les observations subjectives et la charge UC | Stage12 inchangé ici | Stage12 PARTIAL / issue #110 ouverte |

## Invariants et réception

- Les quatre statuts historiques, les séquences d'actions, les appels `Simulator.rollout`, la compétition, la profondeur de planification, l'Equipment et les coûts UC ne sont pas modifiés par cette intégration.
- `root_candidate_edges`, `root_available_edges` et `root_unavailable_edges` sont des observations **du seul lancement de recherche**, pas un certificat physique. Un succès précoce ne prouve pas l'épuisement de toutes les arêtes. Le diagnostic d'absence de premier pas est réservé à une recherche `incomplete_model` réellement épuisée.
- L'option `progressive_subgoals=False` laisse `last_search_diagnostic=None`. Aucun accès Oracle, banc, état caché, mémoire subjective ou journal supplémentaire n'est ajouté.
- Validation requise : deux Python, tests A2.30-I + Stage6 + régression Goal Agency, vérification de la CI générale et vérification après fusion dans `main`. Les résultats précédents du run #38718639833 et du contrôle de parité #38718640403 sont historiques, ils ne remplacent pas cette validation.
- **Limitation non levée :** le planificateur peut toujours retourner `incomplete_model` et ne garantit ni repas, ni sûreté alimentaire, ni agence distale; A2.30 et Stage12 restent partiels. PR #199 explicitement hors périmètre.

Sources originales : [résultats A2.30-I dans #187](https://github.com/josselin-orta-lab/individual-zero/blob/science/stage12-b-a230-model-completeness-20261015/docs/research/stage12-issue110-b-a230i-root-diagnostic-results-2026-10-15.fr.md) et [bilan A2.30](https://github.com/josselin-orta-lab/individual-zero/blob/science/stage12-b-a230-model-completeness-20261015/docs/research/stage12-issue110-b-a230-technical-scientific-bilan-2026-10-15.fr.md).
