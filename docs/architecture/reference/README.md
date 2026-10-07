# Architecture reference documents

This directory contains the long-form conceptual and normative reference documents used by Individual Zero.

## Language layout

Reference documents are organized by ISO 639-1 language code:

```text
reference/
├── fr/
│   ├── architecture-v2.md
│   └── mvp-specification-v1.2.md
└── en/
    ├── architecture-v2.md
    └── mvp-specification-v1.2.md
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

| Reference document | French | English | Source language |
| --- | --- | --- | --- |
| Conceptual architecture v2 | current | pending | French |
| Normative MVP specification v1.2 | current | pending | French |

When an English equivalent is added, it should use the exact matching path under `en/`.

## Scope

These files are reference material. Repository-specific architecture notes such as the executable bootstrap boundary, I0 overview, and generation templates remain one level above in `docs/architecture/`.
