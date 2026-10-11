# Abrupt process termination: the current MVP v1.3.1 durability boundary

**Scope:** negative software evidence and a recovery-design gate. This is not a
journal implementation, a scientific proof, or an operator-approved recovery mechanism.

The complete `HashChainedJournal` remains owned by I0 and in RAM. 
`export_immutable_journal` is an explicit, never-overwrite, fsynced operator
export. It is **not** a per-event write-ahead log or a paired atomic current-state
commit. Both live and terminal states can therefore advance after the latest
durable operator archive, leaving an unapplied suffix missing on abrupt exit.

## Reproduce safely in disposable subprocesses

`python -m unittest tests.test_mortal_abrupt_crash_window -v`

The harness first executes and archives one coherent physical step. It then
starts physical step 2 and performs one of three **hard exits with `os._exit`**:

| Injection | Exit | Controlled witness | Expected durable journal |
| --- | --- | --- | --- |
| Immediately after `WorldBody.apply`, before transition journal receipt | 72 | Test-only witness saw physical step 2 | Only previously exported completed step 1 |
| After a genuinely lethal applied step and in-RAM terminal closure, before export | 73 | Test-only witness saw terminal step 2 | Only previously exported completed step 1; no durable death record |
| After the same terminal step and an explicit fsynced final export | 74 | Test-only witness saw terminal step 2 | Both archives exist; final independent audit sees exactly 2 closed steps and 1 death |

Each child is independent and uses a new identity. The test-only witness is not
part of the individual and does not certify physical truth. The parent validates
exports with `lab.independent_journal_audit`. No old prefix is loaded into a
surviving I0 and **no restart is attempted**.

The successful negative test demonstrates the absence of an automatic durable
life journal since the last explicit export. It does **not** prove exactly which
bytes a real disk would preserve after a hardware power cut, nor characterize
filesystem-specific journal/barrier guarantees. A separate fault-injection
suite must cover disk-full, partial writes, interrupted `fsync`, rename/directory
sync, concurrent writers and corrupt/truncated tails.

## Minimum safe design gate before changing the runtime

1. Keep the append-only full journal under I0 ownership, with verified event
   sequence, canonical hash chain and no Oracle or Bench dependency.
2. Define a single immutable individual ID, monotonic transition generation
   and a durably committed **current** state receipt. No selectable old lives.
3. Enforce fail-closed behavior for uncertain intent, applied physical outcome,
   durable journal entry, terminal marker or cognitive owner publication.
4. Test crashes before/after every persistence and physical publication
   boundary. A recovered terminal marker must never admit new actions.
5. Correlate the current full world/body state, cognitive owners and final
   journal head. Never replay a committed command into the same identity.
6. Keep operator exports and audits independently usable, even for halted or
   partially published lives. Treat missing event suffixes as incidents, not
   silently repaired success.
7. Provide separately assessed Linux/filesystem and Python 3.11/3.12 behavior.
   Never claim atomic physical/journal persistence merely from successful
   `fsync` of a journal file.

**Outstanding operator-sensitive issue:** whether a crash during
`WorldBody.apply` may qualify as an unpublished private transition or must
permanently halt that identity. Until the atomicity semantics can be demonstrated,
select `technical_halt`, not restoration or continued life. No new normative
rule is adopted here.

**Conformity:** M-11 remains unachieved; M-12 in-process and explicit export
properties do not imply hard-crash event durability. The 600-step software
diagnostic remains independent and non-scientific.
