# Archive custody and historical references

This directory is for preserved historical material, **not** for a second active runtime.

- [I0 frozen archive](i0/README.md): historical Lab, tests and workflows. Never rewrite, rename, or mix archived bytes into an I1/I2 runtime. The [registered archive manifest](../config/archives/i0-20261017.json) records the frozen custody boundary.
- [Research historical files](../docs/research/archive/README.md) and [dated research records](../docs/research/README.md): experiment-specific source snapshots (including Issue 110 GA08) are **separate** from the frozen I0 manifest. Historical studies may remain outside `archive/` because their paths are referenced by reports, code, or source-pinned evidence.
- [Versioned architectural references](../docs/architecture/reference/README.md): historical specifications, not current engine authority.
- [Current architecture and generation status](../docs/architecture/ATLAS.md): consult this before comparing the archived material with a living generation.

For a path-oriented inventory, from the repository root:

```bash
python tools/repository_layout.py inventory --kind archives --match i0 --limit 20
python tools/repository_layout.py audit --json
```

**Placement rule:** never move evidence or frozen code merely because its filename is old. First establish the owning generation, provenance and blob identity, GitHub/CI references, imports and replay constraints. Make any verified migration a dedicated change with explicit link and compatibility impact; preserve the original historical artifact where custody requires it. New active code does not belong here.

This index is current navigation guidance. It does not change the frozen I0 content, source authenticity, or any scientific verdict.
