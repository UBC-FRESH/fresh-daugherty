Architecture
============

Module map (see ``planning/v0.1.0a1-plan.md`` for the phase scope):

- ``fresh_daugherty.instance.thesis`` — the transcribed Daugherty (1991)
  case-study reference data (Tables 5.1-5.5, horizon, objective), the
  anchors the reconstruction is calibrated against.
- ``fresh_daugherty.instance.reconstruct`` — the documented reconstruction of
  the case-study yield/economics model (Chapman-Richards yield + Faustmann
  PNV, 4% discount, price escalation), calibrated to the thesis anchors and
  grounded in the Umpqua LRMP CMAI culmination ages.
- ``fresh_daugherty.instance.landbases`` — the 18 initial forest conditions
  (Table 5.5) as public-safe area datasets.
- ``fresh_daugherty.model`` — build the case-study as a ws3 ``ForestModel``
  (Model I) from the reconstruction (Woodstock sections + bootstrap +
  optimization prep).
- ``fresh_daugherty.lp`` — the open-loop NPV-max harvest-scheduling LP
  (even-flow or target-flow harvest policy).
- ``fresh_daugherty.replan`` — the sequential-replanning simulator and the
  inconsistency metrics (the dynamic-inconsistency measurement).
- ``fresh_daugherty.experiments`` — the experiment runner sweeping landbases
  x discount rates x harvest-flow policies (occurrence/magnitude table).
- ``fresh_daugherty.cli`` — thin CLI wrappers over the Python APIs.

Design invariants:

- Reuse, never re-implement: the model is built on ws3 (``ForestModel``, LP
  machinery); ws3's Model II path is a deferred ws3 enhancement.
- CLI commands are thin wrappers over Python APIs.
- Typed records at boundaries; the inner problem stays linear (continuous
  LP).
- Provenance on every input, formulation, reconstruction assumption, seed,
  and result.
- The scanned thesis is never committed (archival, not redistributable); all
  tests use the public-safe reconstructed fixtures.
