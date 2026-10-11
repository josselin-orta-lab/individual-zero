# Export local immuable du journal causal exhaustif (MVP v1.3.1)

**Fonction** : conserver, sans dépendance à l'oracle ni au banc, une image complète du journal interne d'un individu, y compris après sa mort. Cet outil **ne restaure jamais une vie** et ne remplace ni les souvenirs, ni le journal consolidé `SlowHistory`.

## Export explicite au point de cohérence

À appeler par l'opérateur, sur une instance déjà créée et à un instant où **aucun pas physique n'est ouvert** :

```python
from pathlib import Path
from lab.journal_export import export_immutable_journal

receipt = export_immutable_journal(
    individual.journal, Path("./archives/i0-life-001.jsonl")
)
print(receipt.as_dict())
```

Le dossier de destination doit exister. L'export contrôle d'abord l'intégrité du journal et la cohérence des étapes physiques, copie **tous** les enregistrements canoniques dans un fichier temporaire local, synchronise les octets, puis publie atomiquement un nouveau nom de fichier. Il refuse d'écraser un export déjà existant. L'instance et son journal **ne sont pas modifiés**.

Après l'arrêt ou la mort, l'archive reste accessible sans redémarrer I0 :

```bash
python3 scripts/verify_i0_journal.py ./archives/i0-life-001.jsonl \
  --expected-head VOTRE_EMPREINTE_SHA256 \
  --expected-count VOTRE_NOMBRE_D_EVENEMENTS
```

Conserver l'empreinte et le nombre d'événements de la réception **dans une garde indépendante** du même dossier, car un attaquant pourrait sinon remplacer l'archive **et** son manifeste. Une chaîne auto-cohérente n'atteste pas la vérité externe des événements.

## Limites à ne pas masquer

- L'export explicite n'est **pas encore une persistance synchrone à chaque événement**. Une perte du processus avant le prochain export peut entraîner une perte du journal resté en mémoire. Le MVP v1.3.1 doit donc conserver cette garantie comme point d'amélioration et de validation opérateur.
- Un nouvel export est toujours créé à un nouveau nom, jamais par purge ou écrasement d'un fichier antérieur.
- La création d'un export peut utiliser une mémoire proportionnelle au volume du journal ; pas de compactage, d'externalisation obligatoire ni de rétention limitée.
- L'absence d'Oracle ou de banc ne change ni le comportement cognitif ni les traces internes ; cet export est une action de garde de l'opérateur, pas une connaissance d'I0.
