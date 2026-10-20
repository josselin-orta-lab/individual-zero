#!/usr/bin/env python3
"""Read-only first-person I1 causal event audit for an existing mortal WAL.

Authenticates the original hash chain using the current isolated I1 builder
before interpreting any events. Never instantiates a living actor or world,
executes a command, or writes back to the original WAL. Missing proof is
INCONCLUSIVE, not a fabricated learned behavior.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from audit_i1_spatial_navigation_314 import audit as authenticate


def _fail(message):
    raise ValueError(message)


def classify(events):
    """Classify already authenticated events; synthetic calls prove no physics."""
    counts=Counter()
    proposals={}
    receipts={}
    evaluations={}
    crosses={}
    admitted={}
    commands={}
    transitions={}
    closures={}
    td_prior={}
    learned_with_td=0
    learned_without_td=0
    last_step=0
    for idx,e in enumerate(events):
        if not isinstance(e,dict):
            _fail("invalid causal event")
        kind=e.get("kind")
        t=e.get("t_monde")
        if type(t) is not int or t<1:
            continue
        counts[kind]+=1
        if kind=="td_update_published":
            for sig in e.get("data",{}).get("updated_signatures",[]):
                if isinstance(sig,str):
                    td_prior.setdefault(sig,[]).append((idx,t))
        elif kind=="i1_local_opportunity_proposed":
            d=e.get("data",{})
            opt=d.get("option_ref")
            if not isinstance(opt,str) or not opt.startswith("option:i1-local:"):
                _fail("malformed local candidate")
            k=(t,opt)
            if k in proposals:
                _fail("duplicate local proposal")
            proposals[k]=(idx,d)
            if d.get("learned_value_status")=="learned":
                sig=d.get("learning_signature")
                prior=any(ut<t and ui<idx for ui,ut in td_prior.get(sig,()))
                learned_with_td+=int(prior)
                learned_without_td+=int(not prior)
        elif kind=="i1_local_opportunity_registration":
            d=e.get("data",{})
            if d.get("registered") is True:
                receipts.setdefault((t,d.get("option_ref")),[]).append(idx)
        elif kind=="stage8_option_evaluation":
            d=e.get("data",{})
            evaluations.setdefault((t,d.get("option_ref")),[]).append(idx)
        elif kind=="competition_cycle":
            for trace in e.get("data",{}).get("traces",[]):
                if isinstance(trace,dict) and trace.get("crossed") is True:
                    crosses.setdefault((t,trace.get("option_ref")),[]).append(idx)
        elif kind=="command_admitted":
            admitted.setdefault(t,[]).append((idx,e.get("data",{})))
        elif kind=="command_experienced":
            if t in commands: _fail("duplicate physical command")
            commands[t]=(idx,e)
        elif kind=="world_transition_experienced":
            if t in transitions: _fail("duplicate world transition")
            transitions[t]=(idx,e)
        elif kind=="step_closed":
            if t in closures: _fail("duplicate physical closure")
            closures[t]=(idx,e)
        last_step=max(t,last_step)
    if commands:
        steps=set(range(1,len(commands)+1))
        if set(commands)!=steps or set(transitions)!=steps or set(closures)!=steps:
            _fail("physical sequence gap or missing closure")
        for t in sorted(commands):
            ci,cmd=commands[t]
            ti,_=transitions[t]
            si,closed=closures[t]
            d=closed.get("data",{})
            if not (ci<ti<si and cmd.get("emitter")=="action_control"
                    and d.get("applied_command_count")==1
                    and d.get("world_advance_count")==1
                    and d.get("outcome") in ("normal","dead")):
                _fail("command has no canonical physical commit")
            if d["outcome"]=="dead" and t!=len(commands):
                _fail("physical life continued after death")
    proven_local=0
    for (t,opt),(pi,_) in proposals.items():
        ri=[i for i in receipts.get((t,opt),()) if i>pi]
        ei=[i for i in evaluations.get((t,opt),()) if ri and i>ri[0]]
        xi=[i for i in crosses.get((t,opt),()) if ei and i>ei[0]]
        owners=[
            (i,d) for i,d in admitted.get(t,())
            if xi and xi[0]<i and d.get("option_ref")==opt
            and d.get("source")=="decision"
        ]
        if not owners or t not in commands: continue
        ci,cmd=commands[t]
        if any(i<ci and d.get("command_hash")==cmd.get("command_hash")
               and d.get("primitive")==cmd.get("primitive")
               for i,d in owners):
            proven_local+=1
    return {
        "schema":"i1-readonly-causal-WAL-audit/v1",
        "physical_steps":len(commands),
        "death_observed":bool(commands and
            closures[len(commands)][1].get("data",{}).get("outcome")=="dead"),
        "local_proposals":len(proposals),
        "local_physical_decision_chain_proven":proven_local,
        "learned_local_proposals_with_prior_personal_TD":learned_with_td,
        "learned_local_proposals_without_prior_personal_TD":learned_without_td,
        "scientific_verdict":"INCONCLUSIVE",
        "claim_of_survival_improvement":False,
    }


def audit(path):
    original=Path(path)
    # Authenticate a fixed snapshot and independently check local event
    # ordering. The canonical audit already copies/locks bytes for custody.
    before=original.read_bytes()
    certified=authenticate(original)
    after=original.read_bytes()
    if before!=after:
        _fail("WAL changed while being audited")
    events=[json.loads(row)["causal_event"] for row in before.splitlines()]
    if len(events)!=certified["journal_entries"] or not certified["independent_hash_chain_verified"]:
        _fail("original WAL hash-chain certification inconsistent")
    report=classify(events)
    report["original_wal_name"]=original.name
    report["verified_entries"]=certified["journal_entries"]
    report["verified_head"]=certified["journal_head"]
    report["independent_hash_chain_verified"]=True
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wal",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if args.output is not None and args.output.exists():
        _fail("output must not overwrite existing evidence")
    report=audit(args.wal)
    encoded=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.output: args.output.write_text(encoded,encoding="utf-8")
    else: print(encoded,end="")


if __name__=="__main__":
    main()
