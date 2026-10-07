# P17 hand-off to the manuscript (issue #107)

> **Superseded (P18, #110).** Numbers below predate the P18 re-run; use
> `planning/p18-manuscript-handoff.md`.


Supersedes `planning/p16-manuscript-handoff.md`. All records at `042c345`
(P17.5, #106). Headline basis: the thesis's observation window, **periods
2–11** (thesis p. 83; record columns `*_2_11`); full horizon, periods 1–15, as
sensitivity. Sources: `results/analysis/p17_headline/` (both bases),
`results/analysis/p17_thesis_comparison/`, `results/analysis/p15_*` (gap
diagnostic, descriptives, seeds; full horizon unless stated),
`results/analysis/p17_rerun/old_vs_new.md`.

## Model changes since P16 (Methods / Limitations)

- E4 realized-history window now reads the most recent realized harvests (#102).
- Mature volumes calibrated so the model's discounted period-1 value (4%, end-of-period discounting, 1%/yr escalation) equals Table 5.4; period 2: 0.87–0.93 of Table 5.4 (CM-CE 1.15) (#103; `model.mature_value_check`).
- History loosening one-sided; per-period provenance (#104).

## Core grid (`p17_headline/t1`–`t5`) — periods 2–11 (1–15)

- Flow-constrained: 187/360 = 52% (239/360 = 66%); magnitude 0.078 (0.101).
- NHF control: 19/72 = 26% (28/72); by rate 18/18, 1/18, 0, 0 (18, 10, 0, 0); magnitude 0.13.
- By rate, flow-constrained: 0% 89/90 (0.174); 2% 26/90 = 29% (0.041); 4% 37/90 = 41% (0.045); 6% 35/90 = 39% (0.053). [1–15: 90, 54, 46, 49; 0.211, 0.064, 0.057, 0.071.]
- By policy (2–11): ±20% 52/72 (72%, 0.096); NDY 43/72 (60%, 0.059); ±10% 37/72 (51%, 0.065); −20% 28/72 (39%, 0.090); −10% 27/72 (38%, 0.082). [1–15: NDY 62/72 = 86% most frequent, ±20% 60/72 = 83%.]
- By landbase (2–11): occurrence 25–90%; magnitude 1–6: 0.059–0.143; 7–10: 0.063–0.114; 11–18: 0.055–0.065.
- Paired CM-CE landbases (1,3,5,7 vs 2,4,6,8), 2–11: 66/80 vs 42/80 (1–15: 79/80 vs 51/80).
- Tolerance (2–11) 2/3/5/7.5/10%: 69/64/52/37/29% (1–15: 87/77/66/46/40%).
- Landbase 1, NDY, 4%: announced 11,078 MCF/period (313,700 m³); realized below it in every period 2–15, declining steadily to 10,006 by period 11 (8,972 in 13–14); realized total vs announced periods 2–11 −6.8% (1–15 −8.5%); at 0% −16.2% (−20.2%), 2% −8.2%, 6% −6.9%.
- Landbase 2 (the other all-mature landbase), NDY: realized below announced in 13–14 of 14 later periods at every rate.

## Thesis comparisons on matched populations (`p17_thesis_comparison`)

Thesis volume inconsistency (eq. 5-1, periods 2–11), our full-choice equivalents of the thesis's sets (Tables 5.8, 6.1) vs Table 6.2 (p. 99; thesis subsets include reduced-choice runs, sets 3–8):

| Subset | n | mean | median | thesis n | thesis mean | thesis median |
| --- | --- | --- | --- | --- | --- | --- |
| landbases 1–6 | 54 | 7.3% | 5.4% | 90 | 11.9% | 9.6% |
| landbases 7–10 | 36 | 4.6% | 4.9% | 48 | 6.8% | 6.6% |
| landbases 11–18 | 40 | 4.5% | 4.9% | 40 | 5.3% | 5.2% |
| all | 130 | 5.7% | 5.0% | 178 | 9.0% | 7.2% |

- Same ordering as the thesis (over-mature > young growth > random), lower magnitudes; closest on the random landbases (identical design, sets 2, 11–14).
- Carried-history test (landbases 1–10, 4%, five flow policies, n = 50; thesis pp. 118–120): rolling/carried 0.8% (median 0.05%) vs thesis 1.9%; rolling/reset 6.8%.
- Reference run per landbase (NDY, 4%; p. 124): thesis > 5% on 1–8 and 10, < 3% on 9 and 11–18. Ours: > 5% on 1, 2, 3, 7, 9, 10 (5.2–9.4%); 4.96% on 5; < 3% on 4, 6, 8 (0–1.1%); 11–18 4.7–6.4% (not < 3%). Agreement on 5 of 18 landbases.

## Objective-gap diagnostic (core institution)

- Replans 2–11: announced plan strictly suboptimal or infeasible in 54% of flow-constrained replans, 21% of NHF replans (all at 0–2%). [Replans 2–15: 63% / 24%.]
- Landbase 1, NDY: non-optimal in all 10 replans of periods 2–11 at every rate; NHF optimal in all at 2–6%, 4 of 10 non-optimal at 0%.
- First deviation (flow-constrained): 358/360 scenarios have one; 83 start infeasible; first suboptimal gap median 0.089% of the replan objective (p90 3.6%); median period 5.
- Gap-flagged among metric-consistent scenarios: 171 of 173 (2–11 basis); 119 of 121 (1–15).

## Replanning institutions (`p17_headline/t6`; tails from gaps, periods 2–11)

| Horizon | History | Flow-constrained 2–11 (1–15) | Magnitude 2–11 | Plan optimal 2–11 | NHF 2–11 (1–15) |
| --- | --- | --- | --- | --- | --- |
| rolling | reset (core) | 187/360, 52% (239) | 0.078 | 46% | 19/72 (28) |
| fixed | reset | 137/360, 38% (143) | 0.063 | 62% | 0/72 (2) |
| rolling | carried | 87/360, 24% (124) | 0.042 | 65% | 19/72 (28) |
| fixed | carried (exact tail) | 0/360, 0% (4) | 0.000 | 100% | 0/72 (2) |

- Exact tail: on periods 2–11 no scenario is inconsistent and every replan finds the announced period-1 harvest optimal; the four full-horizon residuals (landbases 12, 13, 15, 18; 0%, −20%) are period-14/15 end-of-horizon ties. Loosening: 63 numerical (1e-5), 1 at 1e-4, none material.
- Rolling/carried: anchor materially loosened in 9.9% of flow-constrained replans.
- Landbase 1, NDY, 4% (2–11): 0.068 rolling/reset, 0.052 fixed/reset, 0.007 rolling/carried, 0 exact tail.

## Extensions (2–11; 1–15 in brackets)

- E1: flow-constrained occurrence linear 4→0% 74% (98%), linear 6→0% 72% (93%), inverse-j k=1 92% (100%), k=2 94% (100%); magnitude 0.075–0.154 (0.129–0.199); constant-rate control 4% 41% (0.045), 6% 39% (0.053), 0% 99% (0.174). NHF control under the paths 12–18 of 18 (all 18 on 1–15); NHF replans 2–11 suboptimal 12–52%, infeasible 0–24%.
- E2: 0/72 inconsistent on both bases; magnitude 0.0001 (0.0015), max 0.0064; 1/72 single period > 5% (6.9%); cap binds 97% planned / 92% realized periods; tails optimal 95.3%, infeasible 3.1%, suboptimal 1.6%. Landbase 1, 4%: cap 9,724 MCF/period, 12% below announced NDY (11,078); vs realized NDY total −4% volume, −7% NPV. Medians over scenarios vs realized NDY: volume +1.7%, NPV −0.4% (0%: +7.7/+8.0%; positive rates: volume +1.3 to +2.5%, NPV +0.4 to −0.7%); ranges volume −27% to +13%, NPV −22% to +13%; vs announced NDY −9.5%.
- E3 (volume-scored): revenue 158/360 = 44% (187 = 52%) vs volume 187/360 = 52% (239 = 66%); magnitude 0.081 vs 0.078. Revenue-scored: 154/360 (180), 0.079 (0.097). By policy (2–11, volume → revenue): NDY 60% → 25%; −10% 38% → 28%; −20% 39% → 29%; ±10% 51% → 63%; ±20% 72% → 75%. Paired landbases (2–11) revenue 45/80 vs 45/80. CM-CE share of landbase 1 volume-NDY projected harvest 4.2% (0%) and 4.3% (4%), zero under revenue NDY (only 0% and 4% solved). Revenue-NDY period-1 harvest 33% above volume NDY (landbase 1, 4%: 14,704 vs 11,078 MCF). Revenue replans 2–11 non-optimal 57%.
- E4: within-plan 95/144 = 66% (125 = 87%), 0.065 (0.084) vs pointwise NDY 60% (86%); realized-history 23/144 = 16% (50 = 35%), 0.028 (0.050); by rate 2–11: 31%, 28%, 6%, 0% at 0/2/4/6%. Floor loosened beyond numerical tolerance in 52% of replans (51% in 2–11; 12% at 0%, 65–67% at 2–6%), median 0.9%, max 3.1% of the floor, never dropped.
- Seeds (landbases 11–18, flow-constrained, 2–11): 39–46% across five draws (tracked 39%), magnitude 0.058–0.064 [1–15: 47–56%, 0.079–0.085].

## Statements that change vs the P16 draft

- Headline numbers move to periods 2–11 (52% not 65%; NHF 19/72, all but one at 0%).
- Exact tail: 0/360 on 2–11 (was "4/360, near-ties at 0%").
- Landbase 1 NDY now declines steadily (no dip-and-recover); announced level 11,078 MCF.
- E2 landbase 1: 12% below announced, −4% volume / −7% NPV vs realized NDY.
- E3 front-loading 33% (was 12%); CM-CE share 4.2–4.3%.
- E4 realized-history 16% (2–11), loosening median 0.9%, max 3.1% (was 22% under the indexing defect).
- Thesis comparison: matched subsets and Table 6.2; per-landbase agreement 5/18.
