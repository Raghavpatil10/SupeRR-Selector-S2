# SupeRR Selector Season 2 — Pressure Player Intelligence

> **Identify the Most Reliable Players Under Pressure** · Round 1 submission (Rajasthan Royals analytics challenge).

A data-driven system that measures how **batters** and **bowlers** perform in high-pressure match situations compared with their usual performance levels, and ranks the players who deliver most consistently when it matters. Built on IPL ball-by-ball data (2022–2026) and used to drive Rajasthan Royals' IPL 2027 mini-auction strategy.

**Author:** Raghav Patil · **Auction:** 16 Dec 2026, Goa 

---

## Table of Contents

1. [Overview](#overview)
2. [Hackathon Context](#hackathon-context)
3. [Dataset](#dataset)
4. [Project Structure](#project-structure)
5. [Methodology](#methodology)
   - [Pressure Definitions](#pressure-definitions)
   - [Batter Metrics](#batter-metrics)
   - [Bowler Metrics](#bowler-metrics)
   - [Composite Index](#composite-index)
   - [Eligibility & Sample Sizes](#eligibility--sample-sizes)
6. [Data Processing Notes](#data-processing-notes)
7. [Results — Top 10 Under Pressure](#results--top-10-under-pressure)
8. [Auction Application (RR IPL 2027)](#auction-application-rr-ipl-2027)
9. [How to Run](#how-to-run)
10. [Outputs](#outputs)
11. [Reliability & Limitations](#reliability--limitations)
12. [Assumptions](#assumptions)

---

## Overview

Not every player thrives when the game is on the line. This project builds a reproducible analytics pipeline that:

- Reconstructs **match context** (target, required run rate, wickets, phase) from ball-by-ball data.
- Tags every delivery as **pressure** or **non-pressure** using five distinct pressure scenarios.
- Computes per-player **pressure vs. baseline** metrics for both batting and bowling.
- Combines them into a single **Composite Pressure Index (0–1)** with transparent, tunable weights.
- Produces two ordered **Top-10 lists** (batters and bowlers) plus auction-priority recommendations.

The core question the index answers: *"Who rises above their own baseline when the situation tightens?"*

---

## Hackathon Context

**Challenge — SupeRR Selector Season 2 (Round 1):** *"Identify the Most Reliable Players Under Pressure"*

- Build a data-driven system measuring batter and bowler performance in high-pressure match situations vs. usual levels.
- Identify and rank players who deliver most consistently when it matters.
- Pressure definition is left to the solver — must be justified and shown to distinguish pressure from ordinary situations.
- Method must work for **both** batting and bowling.
- Data: historical IPL + T20I ball-by-ball (2022 onwards) plus supporting metadata.

**Required submission components:**
1. **Player Rankings** — two ordered Top-10 lists (batters, bowlers), Rank 1 → 10, selected via Unstop dropdowns.
2. **Methodology Report** — document covering pressure definition, performance measurement, fair comparisons, evidence for Top-10, reliability & limitations.

This repository is the full working codebase + generated report behind that submission.

---

## Dataset

Source: supplied hackathon data under `data/`.

| File | Rows | Purpose |
|---|---|---|
| `ball_by_ball.csv` | 200,999 deliveries | Delivery-level records (runs, wickets, extras, striker/bowler, over) |
| `matches.csv` | 883 | Match metadata (stage, result, knock_out, revised_target) |
| `competitions.csv` | 141 | Competition/season (IPL 2022–2026 + T20I series) |
| `teams.csv` | 353 | Team mappings per competition |
| `playing_eleven.csv` | 28,381 | Playing XIs |
| `competition_team_player_mapping.csv` | 6,413 | Player → team/nationality mapping |
| `Round 1 Problem Statement …pdf` | — | Official problem statement |

**Scope used for analysis:** IPL 2022–2026 only (5 seasons, **371 matches, 87,687 deliveries**). T20I data exists in the DB but is excluded to keep rankings auction-relevant (franchise T20 context). 20 knockout matches, ~35 close finishes identified.

---

## Project Structure

```
RR_HACKATHON/
├── README.md
├── code/
│   ├── pressure_analysis.py        # v1 pipeline (initial)
│   ├── pressure_analysis_v2.py    # v2 corrected pipeline (canonical)  ← use this
│   ├── build_slides.py            # Slide deck v1 (RR brand theme)
│   └── build_slides_v2.py         # Slide deck v2 (Tactical Vision theme) ← final report
├── data/
│   ├── ball_by_ball.csv
│   ├── matches.csv, competitions.csv, teams.csv
│   ├── playing_eleven.csv, competition_team_player_mapping.csv
│   ├── batter_results.txt, bowler_results.txt
│   ├── batter_scores_full.json, bowler_scores_full.json   # top-50 scored players
│   └── Round 1 Problem Statement …pdf
├── reports/
│   ├── RR_Auction_2027_Raghav_Patil.pdf   # final methodology report (tactical)
│   ├── RR_Auction_2027_SupeRR_Selector.pdf # v1 report
│   └── slides/                             # individual slide PNGs
└── (generated) batter_results.txt, bowler_results.txt
```

---

## Methodology

### Pressure Definitions

Pressure is defined at **delivery level**. Five pressure scenarios are tagged (a delivery can qualify for multiple):

| Code | Scenario | Definition |
|---|---|---|
| **P1** | Death Overs | `overid ≥ 16`, both innings. Highest-leverage batting phase. |
| **P2** | Chase Pressure | Innings 2, **Required Run Rate (RRR) > 10** at the time of delivery. |
| **P3** | Collapse Recovery | Innings 1, batter enters after **3+ wickets in first 10 overs** (over > 10). |
| **P4** | Knockout Match | `knock_out = 1` or stage ∈ {Qualifier, Eliminator, Final, Semi Final}. |
| **P5** | Close Finish | Match decided by **≤ 9 runs or ≤ 2 wickets**. |

Bowling pressure is captured via phase: **PB1** death (16–20), **PB2** middle (7–15), **PB3** powerplay (1–6). The composite focuses on death-over bowling (highest leverage) plus middle-over support.

RRR is reconstructed per delivery from cumulative runs/wickets and the innings-1 total (+1) as target.

### Batter Metrics

Per player, across IPL 2022–2026 (min 100 death-over balls to qualify):

- **Death SR** — strike rate in overs 16–20.
- **Death Average** — runs per dismissal in death.
- **Boundary %** — (4s + 6s) / balls in death.
- **Dot %** — legal zero-run deliveries / balls (lower better).
- **Chase SR** — SR in deliveries where RRR > 10 (clutch proxy).
- **Delta SR** — Death SR − Overall SR (how much SR rises under pressure).
- **Consistency** — `1 − CV` of innings-level death SR (≥ 3 innings with ≥ 3 balls).
- **Knockout SR** — SR in knockout matches.
- **Sample confidence** — `log(balls) / log(400)`.

### Bowler Metrics

Per player (min 60 death-over balls to qualify):

- **Death Economy** — runs/over in overs 16–20 (lower better).
- **Death Dot %** — zero-run legal deliveries / balls.
- **Boundary % Conceded** — (4s + 6s conceded) / balls (lower better).
- **Wickets per Innings** — death wickets / death innings.
- **Middle Economy** — economy in overs 7–15.
- **Middle WPI** — middle-over wickets per innings.
- **CV of Economy** — innings-level consistency of death economy.
- **Delta Economy** — Death Econ − Overall Econ (negative = specializes in death).
- **Sample confidence** — `log(balls) / log(400)`.

### Composite Index

All metrics are min-max normalized to [0,1] (inverted where lower is better). Then:

**Batter composite** (weights):
```
Performance (40%)  = 0.55·DeathSR + 0.30·Boundary% + 0.15·(1−Dot%)
Chase clutch (25%) = normalized Chase SR
Consistency (20%)  = normalized consistency
Delta (10%)        = normalized Delta SR
Sample (5%)        = sample confidence
Composite = 0.40·Perf + 0.25·Chase + 0.20·Consistency + 0.10·Delta + 0.05·Sample
```

**Bowler composite**:
```
Performance (40%)  = 0.50·(1−Econ) + 0.25·Dot% + 0.25·(1−Boundary%)
Wickets/inn (25%)  = normalized death WPI
Consistency (20%)  = normalized (1−CV)
Delta (10%)        = normalized (1−DeltaEcon)
Sample (5%)        = sample confidence
Composite = 0.40·Perf + 0.25·WPI + 0.20·Consistency + 0.10·Delta + 0.05·Sample
```

Weights are configurable and were stress-tested (sensitivity analysis) — top picks remain stable across alternative weight schemes.

### Eligibility & Sample Sizes

- **Batters:** ≥ 100 death-over balls (IPL) → 50+ qualified players scored.
- **Bowlers:** ≥ 60 death-over balls (IPL) → 50+ qualified players scored.
- Normalization is computed over the **qualified pool** only, so scores are relative to peers with sufficient sample.
- Consistency metrics require ≥ 3 innings with ≥ 3 balls; otherwise default neutral (0.5).
- Chase SR defaults to `0.85 × Death SR` when < 20 chase-pressure balls.

---

## Data Processing Notes

Key data-quality fixes applied (v2 pipeline):

1. **`extras1_runs` is a delivery-type code** (6 = regular, 2 = wide, 1 = no-ball, 3 = leg-bye, 4 = bye), **not extra runs**. Run totals use the `runs` column plus an extras penalty (+1 for wide/no-ball). v1 incorrectly summed `extras1_runs` into totals.
2. **Dot ball** = legal delivery (not wide/no-ball) with 0 runs off the bat. Byes on a 0-run ball count as a dot for the bowler but **not** for the batter.
3. **Bowler wicket** = `is_wicket = true` AND dismissal type ≠ run-out (run-outs not credited to bowler).
4. **Legal delivery** for economy/balls-faced = `extras_type ∉ {wide, Overstep}`.
5. Target = innings-1 total + 1, reconstructed from ball data (cross-checked with `revised_target` where present).
6. Nationality (Indian vs Overseas) inferred from `competition_team_player_mapping` team names — verified manually for top targets.

---

## Results — Top 10 Under Pressure

Data-driven rankings (IPL 2022–2026, composite index). These are the raw Top-10; availability filtering for the auction is applied separately (see below).

### Top 10 Batters (Composite Pressure Index)

| Rank | Player | Death SR | Death Avg | Chase SR | Consistency | Death Balls | Index |
|---|---|---|---|---|---|---|---|
| 1 | Shreyas Iyer | 213.8 | 35.7 | 178.8 | 0.69 | 217 | 0.844 |
| 2 | Liam Livingstone | 223.7 | 28.3 | 174.5 | 0.59 | 152 | 0.844 |
| 3 | Rishabh Pant | 214.1 | 34.5 | 167.4 | 0.60 | 177 | 0.814 |
| 4 | Sai Sudharsan | 206.8 | 21.6 | 157.7 | 0.67 | 146 | 0.780 |
| 5 | Naman Dhir | 194.7 | 26.9 | 193.3 | 0.60 | 152 | 0.769 |
| 6 | Ishan Kishan | 197.1 | 29.3 | 154.8 | 0.78 | 104 | 0.764 |
| 7 | Rinku Singh | 192.5 | 42.6 | 178.0 | 0.65 | 398 | 0.763 |
| 8 | Jos Buttler | 198.4 | 35.9 | 174.1 | 0.57 | 253 | 0.762 |
| 9 | Heinrich Klaasen | 197.4 | 27.6 | 178.6 | 0.69 | 350 | 0.760 |
| 10 | Tilak Varma | 198.2 | 27.1 | 161.4 | 0.65 | 274 | 0.756 |

### Top 10 Bowlers (Composite Pressure Index)

| Rank | Player | Type | Death Econ | Dot % | W/Inn | Death Balls | Index |
|---|---|---|---|---|---|---|---|
| 1 | Dwayne Bravo | Pace | 8.64 | 26.0 | 1.33 | 100 | 0.689 |
| 2 | Sunil Narine | Spin | 5.94 | 39.8 | 0.54 | 216 | 0.673 |
| 3 | Matheesha Pathirana | Pace | 8.32 | 31.3 | 1.16 | 403 | 0.665 |
| 4 | Jasprit Bumrah | Pace | 7.10 | 32.6 | 0.75 | 393 | 0.662 |
| 5 | Obed McCoy | Pace | 8.40 | 40.0 | 1.00 | 65 | 0.646 |
| 6 | Nandre Burger | Pace | 7.33 | 44.4 | 0.55 | 63 | 0.644 |
| 7 | Lungi Ngidi | Pace | 8.28 | 32.8 | 0.75 | 116 | 0.634 |
| 8 | Riley Meredith | Pace | 9.38 | 34.8 | 1.08 | 112 | 0.628 |
| 9 | Mitchell Starc | Pace | 10.14 | 31.6 | 1.18 | 155 | 0.609 |
| 10 | Noor Ahmad | Spin | 7.63 | 40.4 | 0.59 | 151 | 0.605 |

> Note: some Top-10 names (Bravo, retired; Bumrah, retained by MI; Narine, retained by KKR) are not auction-available. The auction-targeted, availability-filtered lists used for RR's bidding plan are in `build_slides_v2.py` (`REVISED_BATTERS` / `REVISED_BOWLERS`) and the final report PDF.

---

## Auction Application (RR IPL 2027)

The analysis feeds a real bidding plan. Key availability filter (who is definitely NOT in the pool): Rinku Singh (KKR), Rishabh Pant (LSG), Suryakumar Yadav (MI), Nitish Reddy (SRH), Rashid Khan (GT), Jasprit Bumrah (MI), Virat Kohli (RCB), Tilak Varma (MI), Shreyas Iyer (PBKS), Arshdeep Singh (PBKS), Shubman Gill (GT), Ravi Bishnoi (RR, retained).

**Availability-filtered Top Targets (tactical report):**

| # | Batters (available) | Bowlers (available) |
|---|---|---|
| 1 | Liam Livingstone (SRH, OS) | Varun Chakravarthy (KKR, IND) |
| 2 | Tim David (RCB, OS) | Harshal Patel (SRH, IND) |
| 3 | Shashank Singh (PBKS, IND) | Noor Ahmad (CSK, OS) |
| 4 | Ashutosh Sharma (DC, IND) | Matheesha Pathirana (KKR, OS) |
| 5 | Jitesh Sharma (RCB, IND) | T Natarajan (DC, IND) |
| 6 | Rovman Powell (KKR, OS) | Avesh Khan (LSG, IND) |
| 7 | Tristan Stubbs (DC, OS) | Harshit Rana (KKR, IND) |
| 8 | Venkatesh Iyer (RCB, IND) | Yuzvendra Chahal (PBKS, IND) |
| 9 | Marcus Stoinis (PBKS, OS) | Mustafizur Rahman (KKR, OS) |
| 10 | Glenn Maxwell (PBKS'25, OS) | Mohit Sharma (DC, IND) |

**Bidding priority (ceiling in ₹ Cr):** Varun Chakravarthy (13, MUST BID) → Harshal Patel (10) → Noor Ahmad (9) → Tim David (14) → Liam Livingstone (11) → Shashank Singh (9) → Matheesha Pathirana (10) → Ashutosh Sharma (7) → Tristan Stubbs (8) → T Natarajan (7).

**Overseas slot plan:** 4 retained (Archer, Burger, Maphaka, Ferreira) + 4 new (Noor, Pathirana, Tim David, Stubbs/Livingstone/Powell) = 8 total.

---

## How to Run

**Requirements:** Python 3.9+, `matplotlib`, `numpy`, `pypdf` (for reading the problem statement only).

```bash
# 1. Corrected pressure analysis (canonical) — prints rankings + saves JSON/txt
cd code
python3 pressure_analysis_v2.py

# 2. Generate slide decks / report PDFs
python3 build_slides.py          # v1 report
python3 build_slides_v2.py       # tactical report (final)
```

Paths are resolved relative to the project root via `Path(__file__).resolve().parent.parent`, so the scripts run from anywhere.

Outputs written:
- `data/batter_scores_full.json`, `data/bowler_scores_full.json` (top-50 scored players)
- `data/batter_results.txt`, `data/bowler_results.txt` (full ranked tables)
- `reports/RR_Auction_2027_Raghav_Patil.pdf` (final tactical report)
- `reports/slides/*.png` (individual slides)

---

## Outputs

- **`reports/RR_Auction_2027_Raghav_Patil.pdf`** — final 7-slide tactical methodology report (title, availability filters, top-10 batters, top-10 bowlers, auction priority, methodology, risks/limitations).
- **`reports/RR_Auction_2027_SupeRR_Selector.pdf`** — v1 9-slide report.
- **`data/*_scores_full.json`** — machine-readable Top-50 with all raw + normalized metrics and composite.
- **`data/*_results.txt`** — human-readable ranked tables.

---

## Reliability & Limitations

- **Consistency checks:** rankings re-computed under alternative weight schemes (perf-heavy, consistency-heavy, chase-heavy); top picks (Rinku Singh, Tim David, Noor Ahmad, Harshal Patel) remain stable. Rinku Singh is stable in **all** scenarios → MUST BID.
- **Small samples:** Noor Ahmad (151 death balls), Suyash Sharma (95 balls), Obed McCoy (65 balls) — treat rankings as directional.
- **Recency:** all 5 IPL seasons weighted equally; 2026 breakout/slump not separately weighted.
- **Availability uncertainty:** KKR/SRH retention decisions unconfirmed; Varun/Harshal availability is "maybe".
- **RRR reconstruction:** computed from ball-by-ball, not live scorecard; leg-byes/byes introduce minor target discrepancies.
- **Nationality inference** from team names, not 100% reliable — manually verified for top targets.
- **Injury status** not in data; Harshal Patel (shoulder surgery 2025) must be cleared pre-auction.
- **Maxwell** included on profile only (below data threshold) — risk of past form not repeating.

---

## Assumptions

1. IPL-only analysis (T20I data present but excluded for auction relevance).
2. `extras1_runs` is a delivery-type code, not runs (fixed in v2).
3. Dot = legal delivery with 0 runs off bat; byes on 0 not a batter dot.
4. Bowler wickets exclude run-outs.
5. Target = innings-1 total + 1.
6. Min thresholds: 100 death balls (batters), 60 death balls (bowlers).
7. All 5 IPL seasons (2022–2026) weighted equally.
8. Nationality inferred from `competition_team_player_mapping`.
9. No real-time retention/injury data; availability based on franchise logic as of Nov 2026.

---

*Prepared by Raghav Patil · SupeRR Selector Season 2 · Rajasthan Royals Auction Analytics · Nov 2026*
