"""P16.5 (#96) probe: cost of a regeneration-prescription choice in Model I.

Run: ``PYTHONPATH=src python scripts/probe_p16_regen_choice.py <landbase> <horizon>``
(scratch models go to ``tmp/p16/``). Findings: ``planning/p16-regen-choice-probe.md``.

Builds the case-study model twice: as is (harvest regenerates to a fixed
prescription) and with one harvest action per target prescription
(``harvest_rxK``: harvest, then regenerate under prescription K, valid per
ecoclass per thesis Table 5.2). Both get an NPV-only problem without flow rows;
the probe reports LP columns (Model I tree leaves), build and solve time. The
choice model's objective is undiscounted volume (a size probe, not economics):
the case-study objective has no per-prescription costs to make the choice
meaningful (see the findings note).
"""

from __future__ import annotations

import pathlib
import re
import sys
import tempfile
import time

import ws3

from fresh_daugherty.instance.landbases import landbase_areas
from fresh_daugherty.instance.reconstruct import calibrated_params
from fresh_daugherty.lp import add_open_loop_problem
from fresh_daugherty.model import (
    bootstrap_model,
    build_woodstock_sections,
    ecoclass_code,
    prepare_optimization,
)

SCRATCH = pathlib.Path("tmp/p16")


def _write_choice_sections(model_dir: pathlib.Path) -> list[str]:
    """Rewrite the .act/.trn sections with one harvest action per target rx."""
    valid: dict[str, list[int]] = {}
    for eco, rx in calibrated_params():
        valid.setdefault(ecoclass_code(eco), []).append(int(rx))
    targets = sorted({r for rxs in valid.values() for r in rxs})
    operable = re.findall(r"\*OPERABLE harvest\n(.*)\n", (model_dir / "daugherty.act").read_text())
    act: list[str] = []
    trn: list[str] = []
    for k in targets:
        act.append(f"*ACTION harvest_rx{k} Y\n")
        for line in operable:
            if k in valid[line.split()[1]]:
                act.append(f"*OPERABLE harvest_rx{k}\n{line}\n")
        # ONE *CASE per action: ws3's transition parser resets an action's
        # masks at every *CASE block, so DTs created later would only see the
        # last block's masks (found by this probe).
        trn.append(f"*CASE harvest_rx{k}\n")
        for eco, rxs in valid.items():
            if k in rxs:
                trn.append(
                    f"*SOURCE ? {eco.lower()} ? ? baseline\n"
                    f"*TARGET ? {eco.lower()} rx{k} regenerated baseline 100 _AGE 0\n"
                )
    (model_dir / "daugherty.act").write_text("".join(act))
    (model_dir / "daugherty.trn").write_text("".join(trn))
    return [f"harvest_rx{k}" for k in targets]


def _volume(fm, path) -> float:
    total = 0.0
    for t, n in enumerate(path, start=1):
        d = n.data()
        if fm.is_harvest(d["acode"]):
            total += fm.compile_product(t, "totvol", d["acode"], [d["dtk"]], d["age"], coeff=False)
    return total


def run(landbase: int, horizon: int, choice: bool) -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    model_dir = pathlib.Path(tempfile.mkdtemp(dir=SCRATCH)) / "m"
    build_woodstock_sections(model_dir, areas=landbase_areas(landbase))
    acodes = _write_choice_sections(model_dir) if choice else ["harvest"]
    model = bootstrap_model(model_dir, horizon=horizon)
    if choice:
        null_oe = f"_age >= 0 and _age <= {300 + horizon * 10}"
        model.add_null_action()
        model.oper_expr["null"] = {tuple(["?"] * model.nthemes()): null_oe}
        for dt in model.dtypes.values():
            dt._max_age = 300 + horizon * 10
            dt.oper_expr["null"] = [null_oe]
            dt.operability.pop("null", None)
        model.reset_actions()
        for a in acodes:
            model.actions[a].is_harvest = True
    else:
        model = prepare_optimization(model, horizon=horizon)
    t0 = time.time()
    if choice:
        problem = model.add_problem(
            name="probe",
            coeff_funcs={"z": _volume},
            cflw_e=None,
            cgen_data=None,
            acodes=("null", *acodes),
            sense=ws3.opt.SENSE_MAXIMIZE,
            mask=tuple(["?"] * model.nthemes()),
            workers=1,
            verbose=False,
        )
    else:
        problem = add_open_loop_problem(model, flow_geometry="none", discount_rate=0.04)
    build = time.time() - t0
    t0 = time.time()
    problem.solve(verbose=False)
    solve = time.time() - t0
    columns = sum(len(list(tree.leaves())) for tree in problem.trees.values())
    print(
        f"landbase {landbase} H={horizon} choice={choice}: columns {columns}, "
        f"build {build:.1f}s, solve {solve:.1f}s, status {problem.status()}",
        flush=True,
    )


if __name__ == "__main__":
    lb = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    h = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    run(lb, h, choice=False)
    run(lb, h, choice=True)
