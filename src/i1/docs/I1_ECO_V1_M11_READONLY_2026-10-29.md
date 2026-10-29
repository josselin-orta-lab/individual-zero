# I1-ECO-v1 — extraction physique M11 indépendante, phase A

Enregistré avant le code, 29 octobre 2026. Base `main 7006beee5c5262ff392818b9424455f22e8c4ead`.

Raccorder les métriques descriptives ECO-v1 aux **occurrences M11 originales**, après vérification complète par `SQLiteLifeLedger.audit_read_only`. Le lecteur ne peut ni écrire le SQLite ni restaurer une vie, appeler I1, lire Q, inventer un événement, importer les effets cachés du monde dans la cognition ou modifier les UC.

Chaque pas compté exige exactement un `command_experienced`, un `world_transition_experienced`, et un `step_closed` normal ou mortel, partageant `t_monde` et `attempt_ref`, dans l'ordre original. Le `body_before` doit être identique au dernier `body_after` ; l'état corporel initial provient de la **première transition authentifiée**, pas d'une inférence. Un décalage, un doublon, des pas manquants, une mort sans reçu terminal, un statut technique ou une génération incompatible doivent faire échouer le calcul.

La méthode M11 officielle vérifie identité, chaîne et état avant la lecture SQL indépendante. Un simple `SELECT` non validé n'est pas une preuve. Le lecteur réconcilie le nombre d'événements SQL et le head au reçu d'audit, puis transmet la trajectoire au scoreur ECO-v1.

**Bornes explicites** : cet outil ne certifie pas une cohorte indépendante, ne mesure pas l'avantage causal, ne vérifie pas l'exposition d'une ablation et ne fournit jamais un GO intégré. Les consignes et échelles normalisées doivent être fournies et préenregistrées depuis la configuration de naissance. Le statut `active` à l'horizon est censuré, jamais assimilé à une survie illimitée. Les premières exécutions de connexion seront des tests sur des vies déjà connues, pas une cohorte confirmatoire.

Aucune modification de I1/I0, TD, mémoire, politique, physique, sommeil, Competition ou Action Control. Test exact-head Python 3.11/3.12 obligatoire avant fusion.
