# Student Loan Application Funnel Optimizer

A funnel analysis and A/B test on a simulated student loan application
process — from acquisition through approval — built to identify where
applicants drop off and test whether a simplified onboarding flow
genuinely improves completion.

**[Live dashboard →](https://claude.ai/artifact/K3C5vXKgfR6jXi9Xhhi8tq)**

## The problem

A student loan application funnel has five stages: acquisition,
eligibility check, onboarding, document submission, and approval.
Every stage loses applicants. The questions this project answers:

1. Where in the funnel is drop-off highest?
2. Does a simplified onboarding flow actually improve completion,
   or does it just look better anecdotally?
3. What applicant segments (credit tier, acquisition channel) behave
   differently, and where?

## Data

`data/applications.csv` — 20,000 simulated applications, generated with
realistic, non-uniform drop-off probabilities (not just random noise).
Credit tier genuinely drives eligibility and approval odds; acquisition
channel and requested loan amount are also modelled. Each applicant is
randomly assigned to a Control (original onboarding) or Treatment
(simplified onboarding) group, with a real simulated treatment effect
built into the generation process — see
`notebooks/01_generate_data.py` for the exact assumptions.

This is **synthetic data**, generated because no public dataset matches
this exact funnel with an A/B-testable onboarding variant. The
generation logic documents every assumption so the numbers are
traceable, not arbitrary.

## Method

| Step | Script | What it does |
|---|---|---|
| 1 | `notebooks/01_generate_data.py` | Generates the 20K-row synthetic dataset |
| 2 | `notebooks/02_funnel_analysis.py` | Computes stage-wise conversion and drop-off |
| 3 | `notebooks/03_ab_test_analysis.py` | Runs a two-proportion z-test on the onboarding A/B test |
| 4 | `notebooks/04_visualizations.py` | Generates the funnel, drop-off, and A/B charts |

Run them in order:

```bash
pip install pandas numpy matplotlib statsmodels
python notebooks/01_generate_data.py
python notebooks/02_funnel_analysis.py
python notebooks/03_ab_test_analysis.py
python notebooks/04_visualizations.py
```

## Key findings

- **25.7% of applicants are ultimately approved** (5,147 of 20,000).
  Drop-off is fairly evenly spread across all four transitions
  (27–32% lost at each stage) — there's no single bottleneck stage.
- **The simplified onboarding flow produced a statistically significant
  +8.1 percentage point lift** in completion (69.4% → 77.6%,
  two-proportion z-test, z = 10.97, p < 0.001). This is a genuine
  significance test with 95% confidence intervals, not an eyeballed
  percentage difference.
- **Credit tier is the strongest driver of eligibility** (55.5% pass
  rate for Thin File applicants vs. 89.5% for Excellent) — acquisition
  channel barely moves end-to-end approval (25.4–26.3% across all four
  channels), suggesting channel quality isn't the lever worth
  optimizing; onboarding and document friction are.

## Repository structure

```
student_loan_funnel/
├── data/
│   └── applications.csv
├── notebooks/
│   ├── 01_generate_data.py
│   ├── 02_funnel_analysis.py
│   ├── 03_ab_test_analysis.py
│   └── 04_visualizations.py
├── dashboard/
│   └── index.html
├── output/
│   ├── funnel_summary.csv
│   ├── ab_test_results.csv
│   ├── funnel_chart.png
│   ├── dropoff_chart.png
│   └── ab_test_chart.png
└── README.md
```

## Tech stack

Python (pandas, NumPy), statsmodels (two-proportion z-test, Wilson
confidence intervals), Matplotlib, and a Chart.js-based interactive
dashboard.
