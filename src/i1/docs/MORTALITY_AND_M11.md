# I1: irreversible mortality and transactional M11

I1's biological/physical death is terminal. A software process restarting is not the same thing as reviving an individual. The distinction is an engineering invariant and an experimental premise.

## Two persistence modes

- WAL natural birth: `runtime/i1_birth.py::birth_i1`, hash-chained technical journal, external custody; does not authorize arbitrary rewind.
- Transactional M11 natural birth: `runtime/i1_birth.py::birth_i1_m11`, `runtime/m11_transactional_mortal.py::M11TransactionalMortal`, `runtime/sqlite_life_store.py::SQLiteLifeLedger`.

A transactional step checks ownership and prepares a private candidate, fences durable intent and commits the candidate before publishing the new official generation. A published receipt and the authoritative SQLite generation must agree. Partial or ambiguous transitions are not an invitation to restore a prior living image and continue.

## Recovery versus resurrection

A cold start may authenticate **only** the current, committed, nonterminal generation under the same identity and runtime contract. Dead, corrupted or ambiguous states are refused. The engine must never recover from an arbitrarily selected older generation to compensate for a failure. Persistence compatibility also constrains changes to the transitional `i1lab` namespace.

## Required adversarial checks

- Failure before SQLite COMMIT
- Ambiguity after COMMIT but before external acknowledgment
- Failure after owner publication
- Unauthorized identity or constructor mismatch
- Invalid cognitive owner roster or published evidence
- Pending durable intent
- Real mortal termination followed by attempted recovery

Do not claim all paths are tested merely because this list exists. Consult the precise tests in `tests/i1/test_i1_m11_adversarial.py` and `tests/i1/test_i1_natural_m11_cold_recovery.py`, match them to the actual commit, and add a focused regression test for each changed boundary.

## Scientific interpretation

A death in `empty-land` or `dry-valley` is not itself a code failure. A postmortem step, hidden state restoration, invalid receipt or continuing from a previous generation **is** a contract failure. Distinguish human-readable reports from living identities: reporting on a dead life is allowed; continuing that life is not.
