"""P18.1 (#111): yields at rotation ages before and after the young-age fill.

Writes ``results/analysis/p18_young_yields/young_age_fill.{csv,md}``: for every
managed (ecoclass, prescription) cell, the first tabled FEIS age and the volume
at the minimum and the highest-PNV rotation ages under the old flat hold and
under the calibrated Chapman-Richards fill.

    PYTHONPATH=src python scripts/analyze_p18_young_yields.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fresh_daugherty.instance.feis import real_yield_curve, real_yield_table
from fresh_daugherty.instance.landbases import _managed_cells
from fresh_daugherty.instance.thesis import PNV_ROTATION_ANCHORS, ROTATION_RANGES

OUT = Path("results/analysis/p18_young_yields")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for eco, rx in _managed_cells():
        table = real_yield_table(eco, rx)
        pts = {
            e["age"]: float(e["values"][0])
            for e in table["entries"]
            if e["kind"] == "Regen" and e["values"] and e["values"][0] is not None
        }
        ages = sorted(pts)
        new = real_yield_curve(eco, rx, max_age=300)
        for label, age in (
            ("rotation min", ROTATION_RANGES[(eco, rx)].lo),
            ("max-PNV rotation", PNV_ROTATION_ANCHORS[(eco, rx)].optimal_rotation_yr),
        ):
            old = float(np.interp(age, ages, [pts[a] for a in ages]))  # flat hold below
            rows.append(
                {
                    "ecoclass": eco.value,
                    "rx": int(rx),
                    "first_tabled_age": ages[0],
                    "age": age,
                    "which": label,
                    "old_flat_mcf_ac": round(old, 3),
                    "new_mcf_ac": round(new[age], 3),
                    "change": round(new[age] / old - 1, 3) if old else 0.0,
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "young_age_fill.csv", index=False)
    header = "| " + " | ".join(df.columns) + " |"
    sep = "| " + " | ".join("---" for _ in df.columns) + " |"
    body = ["| " + " | ".join(str(v) for v in r) + " |" for r in df.to_numpy()]
    (OUT / "young_age_fill.md").write_text("\n".join([header, sep, *body]) + "\n")
    print(df[df.change != 0].to_string(index=False))


if __name__ == "__main__":
    main()
