# Daugherty (1991) — authoritative formulation spec (from the scan)

Captured from the thesis scan
(`fresh-fuchs/tmp/daugherty1991credibility.pdf`, image-only; page numbers below
are the **printed** thesis pages; PDF page = printed + 12). This is the
reproduction target for the Phase-7 fixes (#42). It corrects several places
where the current stack/paper diverge from the thesis.

## The forest-planning LP (ch. 3, "The Forest Planning Model", p. 27-29)

Strata-based long-term timber harvest-scheduling LP, **Model II formulation**
(existing strata `x_smij` vs regenerated strata `y_rqjk` distinguished by
separate decision variables, to ease analysis of management intensification
and rotation flexibility). Objective: maximize NPV `Z` (eq. 3-1). Constraints:
land-area (3-2), regeneration area transfer (3-3), **harvest flow (3-4, 3-5)**,
nonnegativity (3-6, 3-7).

### Harvest-flow constraints (p. 29) — CONSECUTIVE-period bounded deviation

```
H_{n+1} - (1 - alpha_n) H_n >= 0     n = 1..N-1   (maximum decrease)  (3-4)
H_{n+1} - (1 + beta_n)  H_n <= 0     n = 1..N-1   (maximum increase)  (3-5)
```

`H_n` = total harvest volume in period n. Each period is constrained relative
to the **previous** period, with a maximum fractional decrease `alpha_n` and a
maximum fractional increase `beta_n`. This is NOT the period-1-anchored
symmetric band the current stack implements (`lp.py` ties every period to
period 1 via ws3 `cflw_e` ref_period=1). **This is a fidelity defect to fix.**

### Harvest-flow policy sets actually simulated (Table 5.6, p. 80)

| Code | Type            | Limits                    | Formula (decrease / increase)        |
|------|-----------------|---------------------------|--------------------------------------|
| NHF  | No harvest flow | no limits                 | none                                 |
| NDY  | Nondeclining yield | no decrease            | H_{n+1} - H_n     >= 0               |
| -10% | Sequential flow | max decrease 10%          | H_{n+1} - 0.9 H_n >= 0               |
| -20% | Sequential flow | max decrease 20%          | H_{n+1} - 0.8 H_n >= 0               |
| +/-10% | Sequential flow | max dec 10% & max inc 10% | H_{n+1} - 0.9 H_n >= 0 ; H_{n+1} - 1.1 H_n <= 0 |
| +/-20% | Sequential flow | max dec 20% & max inc 20% | H_{n+1} - 0.8 H_n >= 0 ; H_{n+1} - 1.2 H_n <= 0 |

The experiment's "harvest policy" factor is these six sets — NOT the current
grid's arbitrary "even-flow tolerance 1%/5%/15%". **Fix the grid to use the
thesis's policy sets.**

### Ending-period (terminal) constraints (p. 77)

Used with all harvest-flow-constrained runs (not with NHF): (i) ending
inventory >= 80% of the average inventory of the forest regulated under the
selected regenerated prescriptions; (ii) final-period harvest <= 120% of the
long-term sustained yield under the chosen regenerated prescriptions. Not
currently reproduced — note as a fidelity gap.

## Experiment design (ch. 5)

- Landbases (Table 5.5, p. 78): 18 initial forest conditions, each 10,000 ac.
  1-2 all-mature (2 excludes CM-CE); 3-8 = landbase 1/2 after 40 or 70 yrs of
  area-control harvest at 70/100-yr rotation; 9-10 young-growth (9 equal acres
  by age class, 10 unequal); 11-18 randomly generated young-growth.
- Replanning: models "updated and re-solved for **eleven periods**" (p. 80) —
  not the current stack's full 15-period horizon. Reconcile.
- Interest rates: base 4% (USDA practice); a set of runs at 0%, 2%, 6% (p. 80).
- Factor combinations (Table 5.8, p. 81): 15 sets crossing interest rate
  (0.04/0.02/0.06/0.00), harvest flow (NHF/NDY/-10%/-20%/+/-10%/+/-20%),
  intensity range (Full/Mod/Low) and timing range (Full/Mod/Low).

## Discount-rate finding (corrects the paper's overstatement)

- p. 58 (Interest Rate Effects): Strotz's required form for consistent
  planning is an exponential discount function `lambda(t) = k^t`; the model's
  factor `delta^{-1(n-0.5)}` (delta = 1+i) satisfies it. "The discount factor
  should not be required for the **occurrence** of inconsistency... With a zero
  interest rate the discount factor becomes 1.0 and drops out of the
  consistency requirements... its removal does not substantially change the
  consistency requirements (no terms drop out)."
- => The thesis's claim is **occurrence-invariance** to the rate, NOT that the
  solutions/magnitude are identical across rates. The McQuillan re-examination
  (p. 24) shows the rate DOES shape the trajectory and the timing/magnitude of
  the decline (0% -> harvest drops to zero by the 2nd decade; 10% -> decline
  delayed to the 6th decade).
- => Our grid's bit-identical solutions across 0/2/4/6% (all 12
  landbase x tolerance combos identical to 16 sig figs) indicate an **inert
  objective** in a constraint-pinned test bed, not the thesis's mechanism.
  P1.5 must diagnose this: the objective should bind so the rate shapes the
  plan while the *occurrence* stays invariant. Rewrite the paper's claim to
  occurrence-invariance and drop "results are identical".

## The mechanism (for the paper's framing)

- p. 24 (Re-examination of McQuillan's Model): "When constrained by a NDY
  constraint, the model scheduled harvest in all decades in order to meet the
  constraints, while delaying harvest of the highest-valued stands" and
  scheduled immediate harvest of negatively-valued acres; on re-solving, the
  inherited structure allowed delaying all harvest. This is the
  "declining non-declining yield" engine (Gunn 2007, p. 331-332).
- Metric (abstract, p. 1): inconsistency "measured in terms of the changes in
  decisions and the changes in projected output levels over time."
