# Adapter example: external memory component

> Fictional example. Not project evidence.

Suppose the active I1 generation defines a memory query contract:

```text
MemoryQuery
- content
- context
- max_items
```

An external library expects:

```text
search(vector, top_k, namespace)
```

The adapter can:

1. convert `MemoryQuery.content` into the representation required by the library;
2. map `max_items` to `top_k`;
3. map project context to the external namespace;
4. convert external results into the owning generation's memory-result contract;
5. expose errors and instrumentation.

The adapter should **not** decide:

- whether episodic memory should be queried at all;
- how memory competes with action selection;
- which motivational state changes recall priority;
- when the global cognitive cycle invokes memory.

Those belong to the owning generation's cognitive architecture.

## Boundary

```text
Generation-owned cognition
    |
    | shared interface
    v
Adapter
    |
    | API translation
    v
External library
```

If the adapter begins adding ranking rules that materially affect recall, those rules must be treated explicitly as cognitive behavior and studied accordingly.
