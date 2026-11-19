# VAKYR football probability calibration

Also on Hugging Face: https://huggingface.co/datasets/vakyr/vakyr-football-calibration

##  (pre-match, 38,241 matches)

How well do published football probabilities match reality? This dataset is the **reliability table** of
[VAKYR](https://vakyr.com), a free football site with pre-match probabilities for 600+ leagues and cups and a
live tracker. Every probability was **frozen before kick-off** and compared with the final result (90 minutes).

- **Period:** 2026-09-01 to 2026-11-18 · **Matches:** 38,241 · **Leagues:** top divisions, lower
  divisions, cups and friendlies worldwide.
- **Markets:** 1X2 (home / draw / away), Over 1.5 / 2.5 / 3.5 goals, both teams to score (BTTS).
- **What is inside:** only VAKYR's own aggregated numbers (no raw third-party match data):
  - `calibration_overall.csv` — per market and 10-point probability bin: matches, mean predicted, observed rate.
  - `calibration_by_month.csv` — the same, month by month (to see drift).
  - `summary.json` — Brier score, log loss and the constant base-rate baseline per market.
  - `build_tables.py` — the exact script that produced the tables from the frozen predictions.

## Headline

On every market VAKYR beats a constant forecast that already knows the period's base rate (lower Brier is better):

| Market | Matches | Brier (VAKYR) | Brier (constant base rate) | Log loss |
|---|---|---|---|---|
| 1X2_home | 38,241 | 0.2339 | 0.2466 | 0.6596 |
| 1X2_draw | 38,241 | 0.1779 | 0.1791 | 0.5402 |
| 1X2_away | 38,241 | 0.2073 | 0.2193 | 0.6023 |
| over_1_5 | 38,162 | 0.1695 | 0.1712 | 0.5209 |
| over_2_5 | 38,241 | 0.2436 | 0.2457 | 0.6802 |
| over_3_5 | 38,162 | 0.2278 | 0.2291 | 0.6486 |
| btts_yes | 38,241 | 0.2464 | 0.2483 | 0.6860 |

## Reliability: said vs. happened

1X2 — home win

| Predicted bin | Matches | Mean predicted | Observed |
|---|---|---|---|
| 10%–20% | 783 | 17.0% | 16.5% |
| 20%–30% | 4,421 | 26.0% | 28.2% |
| 30%–40% | 13,016 | 35.7% | 38.4% |
| 40%–50% | 13,076 | 44.3% | 47.5% |
| 50%–60% | 4,948 | 54.1% | 58.8% |
| 60%–70% | 1,456 | 64.1% | 68.4% |
| 70%–80% | 424 | 74.0% | 78.8% |

Over 2.5 goals

| Predicted bin | Matches | Mean predicted | Observed |
|---|---|---|---|
| 30%–40% | 4,717 | 38.0% | 43.0% |
| 40%–50% | 14,069 | 45.1% | 52.4% |
| 50%–60% | 17,228 | 55.2% | 61.8% |
| 60%–70% | 2,083 | 62.4% | 71.4% |

BTTS — yes

| Predicted bin | Matches | Mean predicted | Observed |
|---|---|---|---|
| 40%–50% | 4,274 | 48.1% | 46.6% |
| 50%–60% | 30,833 | 54.8% | 54.2% |
| 60%–70% | 3,064 | 62.3% | 63.8% |

## Known weaknesses (we publish them on purpose)

- **Goals were under-forecast** in this period: Over 2.5 ran 4–9 points below what happened, Over 3.5 by up to 12. A
  multiplicative correction on expected goals was switched on on 18 November 2026; later months will show whether it
  closed the gap.
- **Draws** are slightly over-forecast in the 30–40% bin (32% said, 28% happened).
- **August 2026 is excluded.** A pipeline bug (15 July – 1 August 2026) distorted probabilities, and its tail still
  affected early-August matches (e.g. home wins said 80–90% came in 54% of the time). Measuring from 1 September keeps
  the table honest instead of flattering or punishing the model for a fixed bug.
- Bins with fewer than 150 matches are left out of the tables above (they are in the CSV).

## How it is measured

Each probability is the one VAKYR published for that match, snapshotted **before kick-off** into a tracking table
that is never edited afterwards. Settlement is on 90 minutes (stoppage time included, extra time and penalties
excluded). The model itself is not described here; the point of this dataset is to let anyone check the output.

## Use

Free to use under CC BY 4.0 — please credit «VAKYR (vakyr.com)». Probabilities are statistical estimates, not
certainties and not betting advice. 18+.
