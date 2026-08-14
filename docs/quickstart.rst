Quickstart
==========

The reproduction runs on the reconstructed Umpqua case-study (public-safe; no
private data — the raw Umpqua yield/economics are reconstructed and calibrated
to the thesis anchors, and the yield shapes are grounded in the Umpqua LRMP).
Install::

   pip install -e ".[dev]"

Open-loop LP on a landbase (the all-mature landbase 1):

.. code-block:: python

   from pathlib import Path
   from fresh_daugherty.instance.landbases import landbase_areas
   from fresh_daugherty.model import (
       bootstrap_model, build_woodstock_sections, prepare_optimization,
   )
   from fresh_daugherty.lp import add_open_loop_problem, solve_open_loop

   areas = landbase_areas(1)
   build_woodstock_sections("outputs/model", areas=areas)
   model = prepare_optimization(bootstrap_model("outputs/model", horizon=15), horizon=15)
   problem = add_open_loop_problem(model)  # NPV-max, 4% discount, even-flow
   results = solve_open_loop(model, problem)
   print(results)

Sequential replanning (the dynamic-inconsistency demonstration):

.. code-block:: python

   from fresh_daugherty.replan import (
       inconsistency_metrics, open_loop_projection, sequential_replan,
   )

   projected = open_loop_projection(model)          # the open-loop plan
   realized = sequential_replan(model, workdir="outputs/replan")  # re-solved each period
   print(inconsistency_metrics(projected, list(realized["harvest_volume_mcf"])))

The experiment grid (inconsistency occurrence/magnitude across landbases,
discount rates, and harvest-flow policies):

.. code-block:: python

   from fresh_daugherty.experiments import run_experiment_grid

   grid = run_experiment_grid(
       landbases=(1, 2, 9, 10),
       discount_rates=(0.0, 0.04),
       flow_tolerances=(0.01, 0.05, 0.15),
       horizon=15,
       workdir="outputs/grid",
   )
   print(grid)

Outputs land under the directory you point them at (use ``outputs/`` or
``tmp/``, which are git-ignored working areas). The calibration runs once and
is cached for the process.
