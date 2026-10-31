# Global research coordinator

**Global understanding comes first; task routing comes second.** A development agent should explain what Individual Zero has actually demonstrated, which hypotheses remain unproven, what blocks the next scientific gate, and which intervention reduces the most uncertainty before inspecting individual modules.

The [research program](../../config/research-program.json) contains a **curated, source-linked** set of falsifiable questions (I1-L3 and I2-H1/H2/H3), I2 gates G0–G6, and intervention candidates. Its initial coverage is **not exhaustive**: it does not automatically summarize every historic report or GitHub issue. Extend it as reviewed questions are added. Never overwrite negative results or turn this manifest into a second evidence authority.

## Start with global research state

From the repository root:

```bash
python tools/research_coordinator.py audit
python tools/research_coordinator.py status
python tools/research_coordinator.py recommend --top 5
python tools/research_coordinator.py recommend --generation I2 --format json
python tools/research_coordinator.py graph
```

The tool rereads the local generation registry, I2 contract and cited status/research texts. A `PIN_MATCH` means the **entire referenced Git blob** matches the SHA pinned in `config/research-program.json` and its quoted marker remains present. `SOURCE_BLOB_DRIFT`, a missing source or a changed marker invalidates automatic recommendations until an agent inspects the new text and explicitly updates the source pin. A byte-for-byte match is **not scientific validation**. Dated reports remain dated even when markers match. Real code determines what can execute; original evidence and reviewed verdicts determine what science established.

A recommendation contains question and gate, issue link, expected new knowledge, likely falsifying result, deliverables, blockers and an owner route. `REVIEW_CANDIDATE` means **review**, not execute. `BLOCKED_GATE` means required reviews are missing. A closed issue is not evidence of scientific success.

The planning heuristic combines downstream gate dependency count, ordinal information gain (1–3), estimated effort (1–3) and risk (1–3). **Scores are not probabilities, measured scientific confidence or statistical significance.**

## Traceability graph and the unreviewed research corpus

For decisions grounded in actual source claims (not only in gate labels), use the **typed research-provenance graph**:

```bash
python tools/research_coordinator.py graph --mode knowledge --format json
python tools/research_coordinator.py graph --mode knowledge
python tools/research_coordinator.py trace --id question:I1-L3 --format json
python tools/research_coordinator.py trace --id gate:I2-G3
python tools/research_coordinator.py catalog --limit 30
```

Graph entities include research questions, reported findings (including negative/null results), gate dependencies, intervention candidates, source quotations, source documents and linked issues. The edge `reported_in` means **document attribution**, not proof. `qualifies_question` communicates a result or limitation, **not causal inference**. Gate edges remain blocked pending explicit independent review.

The catalog inspects Markdown names across `docs/research/`, `src/i1/docs/`, `src/i2/docs/`, `docs/architecture/proposals/` and `experiments/`. It reports the number of documents directly cited in the curated program and returns **unreviewed candidates** with filename-derived hints. A historical report not directly cited is **not** necessarily missing from all research; it simply has not been linked into this small index. A file called `results.md` is not verified evidence.

**Research coordination loop:** global status → trace the selected question and its negative/uncertain findings → inspect the original source at the exact SHA → identify gated dependencies → select a falsifiable intervention → scope its code through `agent_context.py` → submit a handoff with remaining uncertainties. Use `catalog` to expand curated coverage gradually, with explicit review and without migrating or rewriting original scientific records.


### Updating source pins without laundering old evidence

To obtain the exact Git blob hash for an existing tracked file, use:

```bash
git rev-parse HEAD:src/i1/docs/STATUS.md
```

After reviewing changes and original evidence, update the corresponding `blob_sha` in `config/research-program.json` and record why the cited assessment still applies (or revise/retract the finding). The file SHA is about **document identity**, not scientific merit. A source file that changes while keeping the same marker is flagged as `SOURCE_BLOB_DRIFT`; human reconciliation is mandatory before recommending new work on it.

The knowledge graph’s `source` nodes and `trace` reports include both pinned and observed blob hashes. The full-repository navigation CI checks graph construction, traces and corpus inventory without running I1 or I2.

## Agent decision cycle

1. Re-read HEAD, registry, engine contracts, current statuses, evidence matrix and this program. Flag contradictions.
2. Inspect live GitHub issues, relevant open PRs on the exact SHA, original traces and negative findings. This tool does not fetch authenticated GitHub state.
3. Identify the **critical research dependency**. Distinguish code existence, tested software, observed behavior and independently established science.
4. Propose the smallest falsifiable intervention that closes a consequential gap, including competing explanations and a potential negative result.
5. Obtain review/protocol approval where required; never launch a study just to fill missing rows.
6. Only then call `python tools/agent_context.py route --route <agent-route>` for scoped ownership and tests.
7. Produce an [agent handoff](AGENT_HANDOFF.md): exact SHA, evidence, test results and next independent research question.

In the dated 31 October 2026 source reports, I1 A1-C has a targeted **NO_GO**, L3 is **NOT_ESTABLISHED**, A2-R is **NOT_EXECUTED**, and I2 G2 is synthetic/non-living. Independent G1 review (#662) and G0 archive/custody verification (#661) deserve examination **before** G3 living architecture or G5 comparisons. These are recorded assessments, not verified live issue states.

## Optional issue-state snapshot

A separately connected agent can supply temporary JSON with `schema`, `repository`, `commit_sha`, `captured_at` and `issues`. Example:

```json
{
  "schema": "individual-zero-github-snapshot/v1",
  "repository": "josselin-orta-lab/individual-zero",
  "commit_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "captured_at": "2026-11-01T00:00:00+00:00",
  "issues": [
    {"number": 661, "state": "open", "url": "https://github.com/josselin-orta-lab/individual-zero/issues/661"}
  ]
}
```

The SHA and timestamp above are **illustrative placeholders**. The tool validates structure, issue URLs, exact-SHA agreement and a 24-hour freshness window:

```bash
python tools/research_coordinator.py recommend --format json \
  --at-sha <exact-current-SHA> --github-snapshot /tmp/issues.json
```

**User-supplied JSON cannot be authenticated by this script.** Even a fresh, structurally valid snapshot cannot certify issue completion, evidence, G1/G3 approval or authorization. Verify directly in the GitHub connector before deciding. Do not commit transient snapshots as canonical evidence.

## Guardrails and maintenance

I2 remains `PROPOSAL_ONLY` without birth or motor rights. Synthetic witness tests do not establish independent M11. The coordinator cannot run cohorts, approve gates, edit the registry or promote a generation. These are explicit review and scientific decisions.

When evidence or an accepted decision changes, update the **owning source document first**, then review the research program in a PR with traceable citations and falsifiable alternatives:

```bash
python tools/research_coordinator.py audit
python -m unittest discover -s tests -p test_research_coordinator.py -v
python tools/agent_context.py audit --json
```

This is an initial, inspectable research-planning layer. Expand its reviewed coverage over time, rather than claiming full understanding of hundreds of historical files from filenames alone.
