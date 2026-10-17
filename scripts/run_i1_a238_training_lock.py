"""A2.38 external-training prebirth seal; zero individual births."""
import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from build_i1_fork import generate

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    with TemporaryDirectory(prefix="a238-external-") as tmp:
        generated=Path(tmp)/"generated"
        generate(generated)
        sys.path.insert(0,str(generated))
        from i1.equipment import EquipmentCorpus,EquipmentCorpusExample,SimulationState,SimulationNeighbor
        from i1.interfaces import PrimitiveCommand
        from i1.experimental.stage6_visible_delta_shadow import fit_external_lab_shadow
        from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
        from i1lab.world import BerryEffect,Position,WorldBody
        source=build_stage11_reference_runtime(autonomous_mortal=True)
        origin=Position(12,12)
        costs=dict(source.world.config.action_energy_costs)
        costs.update({"se_deplacer":2.0,"collecter":1.0,"manger":0.5,
                      "boire":0.5,"attendre":0.35,"dormir":0.25,
                      "poser_une_pierre":1.5,"fabriquer_outil":1.5})
        def visible(w,t):
            c=w.capture_local(t_monde=t)
            return SimulationState(schema_version="simulation-state-v1",
                x=c.position.x,y=c.position.y,body=w.telemetry(),
                inventory=w.inventory(),current_water_source=c.current_water_source,
                current_resources=c.current_resources,
                adjacent=tuple(SimulationNeighbor(direction=n.direction,
                    x=n.position.x,y=n.position.y,passable=n.passable,
                    water_source=n.water_source,resources=n.resources,
                    creature=n.creature) for n in c.adjacent),
                known_shelter_here=False,is_night=w.is_night(t))
        examples=[]
        rows=[]
        for action in ("MOVE_E","COLLECT_B"):
            for i in range(8):
                p=replace(source.world.config,version="a238-training-physics-v1",
                    initial_position=origin,
                    initial_body=replace(source.world.config.initial_body,
                        energy=float(72+i),food=float(43+i),
                        water=float(58+i),integrity=100.0),
                    food_decay_per_step=0.2,water_decay_per_step=0.4,
                    action_energy_costs=costs,berry_effects={
                        "berry_a":BerryEffect(0,-100),"berry_b":BerryEffect(6,0)})
                layout=replace(source.world._layout,obstacles=frozenset(),
                    water_sources=frozenset(),danger_zones=frozenset(),
                    lethal_zones=frozenset(),creatures=frozenset(),
                    resources=((origin,"berry_b",5+i),) if action=="COLLECT_B" else ())
                world=WorldBody(config=p,layout=layout)
                before=visible(world,1)
                cmd=(PrimitiveCommand("se_deplacer",{"direction":"east"})
                    if action=="MOVE_E" else
                    PrimitiveCommand("collecter",{"target":"berry_b"}))
                transition=world.apply(cmd,t_monde=1)
                assert not transition.lethal
                after=visible(world,2)
                examples.append(EquipmentCorpusExample(
                    f"a238:{action}:{i}",before,cmd,after,False))
                rows.append({"id":f"a238:{action}:{i}",
                    "before":before.as_dict(),"command":cmd.as_dict(),
                    "after":after.as_dict(),"physics_sha256":p.digest()})
        corpus=EquipmentCorpus("a238-external-training-v1",tuple(examples))
        model=fit_external_lab_shadow(corpus=corpus)
        assert model.corpus_sha256==corpus.digest()
        assert dict(model.counts)=={"MOVE_E":8,"COLLECT_B":8}
        result={"schema":"a238-prebirth-seal-v1",
                "input_lock_blob":"e1f276ffdc086c80a0360c3df7bd60fc2b7652dd",
                "samples":16,"individual_births":0,"corpus_sha256":corpus.digest(),
                "model_version":model.version,"model_deltas":model.deltas,
                "rows":rows}
        (out/"seal.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print(json.dumps({"corpus_sha256":corpus.digest(),
            "individual_births":0,"samples":16},sort_keys=True))

if __name__=="__main__":
    main()
