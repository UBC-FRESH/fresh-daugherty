# fresh-daugherty Change Log

Append-only project narrative, reverse-chronological.

## 0.1.0a0 — 2026-08-14

Initial repository scaffold and master plan. No functional pipeline yet.

## 0.1.0a0 — 2026-08-14 (Phase 1)

Phase 1 (case-study instance + open-loop LP, Model I) in progress on
`feature/p1-open-loop`.

- P1.1 Case-study instance: transcribed thesis reference data
  (`instance/thesis.py`); calibrated reconstruction
  (`instance/reconstruct.py`) of the yield/economics model to the Table
  5.3/5.4 anchors, yield-curve shapes grounded in the Umpqua LRMP CMAI
  culmination ages; landbases (`instance/landbases.py`).
- P1.2 Open-loop Model I LP: case-study ws3 model (`model.py`) + NPV-max
  even-flow LP (`lp.py`, 4% discount, price escalation). Verified on
  landbase 1: optimal, even-flow holds, mature timber drawn down.
