Command Line Reference
======================

The CLI is a thin wrapper over the Python APIs. Commands:

- ``version`` — print the package version.
- ``open-loop`` — solve the open-loop harvest-scheduling LP (Model I) on a
  landbase (Phase 1).
- ``replan-run`` — run the sequential-replanning simulator and report the
  dynamic-inconsistency metrics (Phase 3).
- ``consistency-run`` — the consistent-solution construct (documented;
  post-v0.1.0a1).

``open-loop``
-------------

.. code-block:: bash

   fresh-daugherty open-loop \
     --landbase 1 --horizon 15 --discount-rate 0.04 --flow-tolerance 0.05 \
     --out-dir outputs/open_loop

Options:

- ``--landbase`` — initial forest condition (1-18; 1 = all mature).
- ``--horizon`` — number of 10-year periods (default 15 = 150 years).
- ``--discount-rate`` — PNV discount rate (default 0.04, the thesis value).
- ``--flow-tolerance`` — even-flow band half-width (default 0.05).
- ``--out-dir`` — where to write the model and the per-period results CSV.

``replan-run``
--------------

.. code-block:: bash

   fresh-daugherty replan-run \
     --landbase 1 --horizon 15 --discount-rate 0.04 --flow-tolerance 0.05 \
     --out-dir outputs/replan

Runs the sequential-replanning simulator (re-solve from the realized state
each period) and reports the inconsistency metrics: the mean absolute
relative deviation between the open-loop projection and the realized
replanned trajectory, and the total-volume change. Options match
``open-loop``.

The experiment grid (inconsistency occurrence/magnitude across landbases,
discount rates, and harvest-flow policies) is available from the Python API
(``fresh_daugherty.experiments.run_experiment_grid``); see
:doc:`quickstart`.
