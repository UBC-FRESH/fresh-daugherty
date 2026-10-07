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

Experiment grids
----------------

Each grid command runs its scenarios in parallel (``--workers``) and writes a
summary CSV plus trajectory (and, where applicable, objective-gap) records.
The exact commands that produced the tracked records are in
``results/experiments/REPRODUCIBILITY.md``.

- ``grid`` — the core scenario grid (landbase x discount rate x harvest-flow
  policy).
- ``grid-discount-paths`` — E1, declining discount-rate paths.
- ``grid-cap-search`` — E2, calibrated max-harvest cap.
- ``grid-value-flow`` — E3, volume- vs revenue-denominated flow constraints.
- ``grid-rolling-mean`` — E4, rolling-mean non-declining yield.
- ``grid-institutions`` — the core grid under rolling/fixed horizon x
  reset/carried flow history.
- ``grid-seeds`` — the random landbases 11-18 under further generator seeds.
