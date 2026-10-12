# Stage 12 : alertes opérateur persistantes, sans omniscience

**12 octobre 2026. Statut : EN COURS.** Référence normative : MVP v1.3.1 §0, v1.2.1 §16.1 et §20.3 Stage 12.

## Contrat réalisé

Un nouveau volet **interne au propriétaire Metacognition existant** reçoit les diagnostics déjà payés, un seul échantillon accepté par pas physique. Chaque alerte requiert `operator_alert_persistence_steps` pas physiques **consécutifs**, positifs et authentiquement observés. Les valeurs inconnues, les refus UC, les pas non observés et les signaux faux interrompent la persistance. Aucun événement d'alerte n'est émis deux fois dans le même épisode ; une guérison puis une récidive peut créer une nouvelle alerte.

Les quatre signaux surveillés sont : stagnation, boucle de raisonnement, entropie temporelle des contextes et biais d'attribution. Les catégories `no_detected_pattern` et `None` ne déclenchent pas de biais. La mesure **distincte** de l'occupation S_t par module se trouve dans la PR #112 et sera raccordée à un éventuel signal d'alerte dédié après validation de sa politique.

Chaque `stage12_operator_alert` est une occurrence technique **opérateur seulement**, jamais un ordre moteur, une récompense, un veto ou une évaluation scientifique. Les compteurs sont une partie du seul propriétaire `metacognition_health`, sous le schéma de garde v2 ; aucun second propriétaire ou historique restaurable n'est introduit. Le coût du suivi constant est compris dans le coût P-43 versionné de `stage12_diagnostic_sample`, et aucun travail n'est fait lors d'un refus UC.

## Audit et procédure opérateur

Le vérificateur externe autonome lit seulement l'export canonique complet ; il vérifie sa chaîne cryptographique, les débits UC et les épisodes de diagnostics réellement publiés. Il reconstruit et exige exactement les alertes correspondantes. Une archive dont les hachages sont recalculés après suppression ou modification d'une alerte échoue tout de même à l'audit métier. Sans hachage final et compteur externe de confiance, l'audit ne prouve pas l'absence d'une troncature en suffixe.

Depuis un checkout propre au SHA de la PR :

```bash
python -m pip install -e .
python -m unittest discover -s tests -p 'test_stage12_operator_alerts.py' -v
python -m unittest discover -s tests -p 'test_stage12_operator_alert_runtime.py' -v
python scripts/report_stage12_operator_alerts.py /chemin/vers/export-canonique.jsonl --expected-head <SHA256_DE_CONFIANCE> --expected-count <COMPTEUR_DE_CONFIANCE>
python scripts/report_stage12_operator_alerts.py /chemin/vers/export-canonique.jsonl --exit-on-alert
```

Codes de retour du CLI : `0` pour un journal conforme, `1` pour refus de validation, `2` (avec `--exit-on-alert`) pour un journal valide contenant une ou plusieurs alertes. Les alertes n'affectent pas la vie d'I0.

L'expérience de câblage emploie volontairement un seuil `entropy_warning_fraction=1.0` pour déclencher un **vrai calcul du détecteur** sur des pas physiques, sans simuler une observation. Ce seuil très permissif ne constitue **aucune preuve d'anomalie réelle ou de validité scientifique**. Tester séparément des seuils de campagne préenregistrés, des séquences longues, les refus UC et les cas de disparition/réapparition.

## Conditions non satisfaites

- L'attribution de réussite et d'échec réellement vécus et indépendamment vérifiés reste en **issue #110** ; une comparaison P-47 conforme n'en est pas une preuve.
- L'intégration avec la console de la PR #107, l'audit indépendant de la PR #111 et l'entropie de S_t de la PR #112 exige une campagne combinée au **dernier SHA**.
- M-11 demeure **FAIL** faute de coordinateur atomique complet de l'état courant après interruption brutale.
- Les modes dégradés DC-07, la détection des défaillances de tempérament extrême, la durée cible de 60 jours et l'acceptation opérateur complète doivent être évalués indépendamment.

**Ne pas déclarer Stage 12 terminé ni valider scientifiquement ses détecteurs sur la seule base de ce protocole.**
