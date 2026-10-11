# Architecture reference documents

This directory contains the long-form conceptual and normative reference documents used by Individual Zero.

## Reference roles

Two document families currently coexist:

- **Conceptual architecture**: explains the broader model, scientific hypotheses, building blocks, implementation diagrams, limitations, and research framing.
- **Normative MVP specification**: defines the software contract for the MVP and is the implementation authority for that version.

**Current target:** [MVP v1.3.1 English](en/mvp-specification-v1.3.1.md) / [French](fr/mvp-specification-v1.3.1.md) explicitly supersedes v1.3.0's proposal to delete the full causal journal. The complete journal and consolidated history remain distinct, while Oracle/Bench become optional external observers. v1.3.0 and v1.2.1 remain historical; software migration is incomplete.

The conceptual architecture informs the project. The normative MVP specification tells an implementation team what must actually be built, tested, replayed, owned, and versioned for the MVP.

## Language layout

Reference documents are organized by ISO 639-1 language code:

```text
reference/
├── fr/
│   ├── architecture-v2.md
│   ├── mvp-specification-v1.2.1.md
│   ├── mvp-specification-v1.3.0.md
│   └── mvp-specification-v1.3.1.md
└── en/
    ├── mvp-specification-v1.2.md
    ├── mvp-specification-v1.2.1.md
    ├── mvp-specification-v1.3.0.md
    └── mvp-specification-v1.3.1.md
```

The **basename and document version stay identical across languages**. The language is expressed by the directory, not by changing the filename.

This makes translation pairs predictable:

```text
fr/mvp-specification-v1.2.md
en/mvp-specification-v1.2.md
```

## Naming rules

- use lowercase ASCII filenames;
- use `fr/`, `en/`, and later other ISO 639-1 language directories when needed;
- keep the same basename for equivalent translations;
- keep the document's own version in the filename;
- a translation does **not** create a new document version;
- a substantive change to the specification creates a new source version first, then translations are brought to that same version;
- never silently mix revisions across languages;
- licensing remains document-specific and is preserved inside each document.

## Translation status

| Reference document | French | English | Source language | Role |
| --- | --- | --- | --- | --- |
| Conceptual architecture v2 | current | pending | French | conceptual reference |
| Normative MVP specification v1.2.1 | retained | retained | English | historical implementation baseline |
| Normative MVP specification v1.3.0 | superseded | superseded | English | historical proposal to remove full journal |
| Normative MVP specification v1.3.1 | target | target | English | retain exhaustive journal; decouple Oracle and Bench |

When an English equivalent is added, it should use the exact matching path under `en/`.

## Scope

These files are reference material. Repository-specific architecture notes such as the executable bootstrap boundary, I0 overview, and generation templates remain one level above in `docs/architecture/`.

Repository-specific notes may summarize or operationalize the references, but they must not silently override a normative MVP rule.
