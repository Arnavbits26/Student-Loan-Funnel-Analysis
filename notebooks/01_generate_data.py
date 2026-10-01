"""
Student Loan Application Funnel Optimizer
Step 1: Generate a realistic synthetic dataset.

Why synthetic: no public dataset matches this exact funnel (acquisition ->
eligibility -> onboarding -> document submission -> approval) with an
A/B-testable onboarding variant, so we generate one with realistic,
non-uniform drop-off rates and a genuine (simulated) treatment effect.
"""

import numpy as np
import pandas as pd
from datetime import timedelta

rng = np.random.default_rng(42)  # fixed seed -> reproducible

N = 20000

# ---- Base applicant attributes ----
channels = rng.choice(
    ["Organic", "Paid Search", "Referral", "Partner College"],
    size=N,
    p=[0.35, 0.30, 0.20, 0.15],
)

credit_tier = rng.choice(
    ["Thin File", "Fair", "Good", "Excellent"],
    size=N,
    p=[0.25, 0.35, 0.28, 0.12],
)

requested_amount = rng.integers(50_000, 2_000_001, size=N)  # INR

acquisition_date = pd.Timestamp("2025-01-01") + pd.to_timedelta(
    rng.integers(0, 365, size=N), unit="D"
)

# ---- A/B assignment: Control = original onboarding, Treatment = simplified ----
group = rng.choice(["Control", "Treatment"], size=N, p=[0.5, 0.5])

df = pd.DataFrame(
    {
        "application_id": [f"APP{100000+i}" for i in range(N)],
        "acquisition_date": acquisition_date,
        "channel": channels,
        "credit_tier": credit_tier,
        "requested_amount": requested_amount,
        "ab_group": group,
    }
)

# ---- Stage 1 -> 2: Eligibility check ----
# Credit tier genuinely affects eligibility pass rate (realistic, not random)
elig_base_rate = {
    "Thin File": 0.55,
    "Fair": 0.68,
    "Good": 0.80,
    "Excellent": 0.90,
}
df["p_eligible"] = df["credit_tier"].map(elig_base_rate)
df["passed_eligibility"] = rng.random(N) < df["p_eligible"]

# ---- Stage 2 -> 3: Onboarding completion ----
# This is the stage the A/B test targets. Control = harder onboarding flow,
# Treatment = simplified flow -> genuinely higher completion probability.
onboarding_base_rate = 0.70
treatment_lift = 0.08  # true simulated effect: +8pp completion rate
df["p_onboarding"] = np.where(
    df["ab_group"] == "Treatment",
    onboarding_base_rate + treatment_lift,
    onboarding_base_rate,
)
df["completed_onboarding"] = (rng.random(N) < df["p_onboarding"]) & df["passed_eligibility"]

# ---- Stage 3 -> 4: Document submission ----
doc_base_rate = 0.72
df["submitted_documents"] = (rng.random(N) < doc_base_rate) & df["completed_onboarding"]

# ---- Stage 4 -> 5: Approval ----
# Approval probability depends on credit tier and requested amount (realistic)
approval_base_rate = {
    "Thin File": 0.55,
    "Fair": 0.68,
    "Good": 0.82,
    "Excellent": 0.92,
}
df["p_approval"] = df["credit_tier"].map(approval_base_rate)
# Larger requested amounts are modestly harder to approve
df["p_approval"] = df["p_approval"] - (df["requested_amount"] / 2_000_000) * 0.10
df["approved"] = (rng.random(N) < df["p_approval"]) & df["submitted_documents"]

# ---- Clean up helper columns, keep only observed outcome columns ----
df = df.drop(columns=["p_eligible", "p_onboarding", "p_approval"])

# ---- Add realistic stage timestamps (for time-to-approval analysis) ----
df["eligibility_date"] = df["acquisition_date"] + pd.to_timedelta(
    rng.integers(0, 3, size=N), unit="D"
)
df["onboarding_date"] = df["eligibility_date"] + pd.to_timedelta(
    rng.integers(1, 5, size=N), unit="D"
)
df["document_date"] = df["onboarding_date"] + pd.to_timedelta(
    rng.integers(1, 7, size=N), unit="D"
)
df["approval_date"] = df["document_date"] + pd.to_timedelta(
    rng.integers(1, 10, size=N), unit="D"
)

# Null out downstream dates for applicants who didn't reach that stage
df.loc[~df["passed_eligibility"], ["eligibility_date", "onboarding_date", "document_date", "approval_date"]] = pd.NaT
df.loc[~df["completed_onboarding"], ["onboarding_date", "document_date", "approval_date"]] = pd.NaT
df.loc[~df["submitted_documents"], ["document_date", "approval_date"]] = pd.NaT
df.loc[~df["approved"], "approval_date"] = pd.NaT

out_path = "/home/claude/student_loan_funnel/data/applications.csv"
df.to_csv(out_path, index=False)
print(f"Generated {len(df):,} rows -> {out_path}")
print(df.head())
