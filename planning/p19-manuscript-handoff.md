# P19 hand-off to the manuscript (issue #117)

Adds to `planning/p18-manuscript-handoff.md` (all P18 numbers stand). Sources:
`results/analysis/p19_round5/`, `results/analysis/p15_descriptives/`.
Basis: periods 2-11 unless stated.

## Terminal-target rotations (V02, V03)

- The terminal targets use the thesis's Table 5.3 rotations. The model's own
  highest-PNV rotation (FEIS yields, model net values, 4%, 10-year grid, within
  the thesis's permitted range) is the shortest permitted rotation for every
  productive prescription, 0-40 years shorter than Table 5.3; the longest for
  CM-CE (190/200 vs 150) (`t5_rotations`).
- Sensitivity, core grid with model-optimal rotations
  (`grid_terminal_rotation_model.csv`, `t7a`, `t7b`): flow-constrained 161/360
  (45%) vs 178/360 (49%) [1-15: 212 vs 203]; positive rates 75/270 vs 88/270;
  magnitude 0.077 vs 0.072; by rate 86/24/22/29 vs 90/26/28/34; NHF identical
  (34/72, trajectories identical); same classification in 331/360 scenarios
  (155 both inconsistent, 23 core only, 6 sensitivity only).
- Landbase 1 NDY magnitude: 0.060 (4%) vs 0.095.

## Other round-5 numbers

- Paired CM-CE, 80 pairs: 67/80 vs 37/80; eq. 5-1 +4.7 points, higher in 84%
  (`t2_paired_cmce`).
- Exact tail: realized harvest departs from the plan by > 1% in some period in
  5/360 flow-constrained scenarios (4 within 2-11; 2 by > 5%; max 40%);
  stand-level ties (`t3a`, `t3b`).
- Institutions at 0% vs 2-6%: rolling/reset 90/90, 88/270; fixed/reset 40/90,
  58/270; rolling/carried 81/90, 6/270; fixed/carried 1/90, 0/270 (`t4`).
- E2 (periods 2-11): single period > 5% in 5/72 (1-15: 7/72), max 13.6%; cap
  binds 99% planned / 94% realized. E2 vs replanned NDY over periods 1-11:
  landbase 1 4% volume -2.3%, NPV -6.3%; medians +1.4%, -0.5%; ranges -15% to
  +35% (volume), -8% to +44% (NPV) (`p15_descriptives/t4`).
- Revenue NDY: projected volume period 2 / period 1 = 0.62 on landbase 1 at 4%;
  worst single-period ratio from a positive harvest 0.30 (`t6`).
- Net-value escalation (V15): disclosed, not changed (maintainer decision).
