"""
Student Loan Application Funnel Optimizer
Step 2: Compute real stage-wise funnel conversion and drop-off.
"""

import pandas as pd

df = pd.read_csv("/home/claude/student_loan_funnel/data/applications.csv")

N = len(df)

stages = [
    ("Acquisition", N),
    ("Passed Eligibility", df["passed_eligibility"].sum()),
    ("Completed Onboarding", df["completed_onboarding"].sum()),
    ("Submitted Documents", df["submitted_documents"].sum()),
    ("Approved", df["approved"].sum()),
]

print("=" * 70)
print("FUNNEL: Stage-wise conversion and drop-off")
print("=" * 70)

funnel_rows = []
prev_count = N
for i, (name, count) in enumerate(stages):
    pct_of_total = count / N * 100
    pct_of_prev = (count / prev_count * 100) if i > 0 else 100.0
    drop_off = prev_count - count if i > 0 else 0
    drop_off_pct = (drop_off / prev_count * 100) if i > 0 else 0
    funnel_rows.append(
        {
            "stage": name,
            "count": int(count),
            "pct_of_total": round(pct_of_total, 1),
            "pct_of_previous_stage": round(pct_of_prev, 1),
            "drop_off_count": int(drop_off),
            "drop_off_pct": round(drop_off_pct, 1),
        }
    )
    print(
        f"{name:22s} | n={count:6,d} | {pct_of_total:5.1f}% of total | "
        f"{pct_of_prev:5.1f}% of prev stage | dropped {drop_off:5,d} ({drop_off_pct:4.1f}%)"
    )
    prev_count = count

funnel_df = pd.DataFrame(funnel_rows)
funnel_df.to_csv("/home/claude/student_loan_funnel/output/funnel_summary.csv", index=False)

print("\n" + "=" * 70)
print("HIGHEST-IMPACT DROP-OFF POINT")
print("=" * 70)
worst = funnel_df.iloc[1:].sort_values("drop_off_count", ascending=False).iloc[0]
print(f"-> {worst['stage']}: lost {worst['drop_off_count']:,} applicants ({worst['drop_off_pct']}% of those who reached the previous stage)")

print("\n" + "=" * 70)
print("DROP-OFF BY CREDIT TIER (at eligibility stage)")
print("=" * 70)
elig_by_tier = df.groupby("credit_tier")["passed_eligibility"].mean().sort_values(ascending=False) * 100
print(elig_by_tier.round(1))

print("\n" + "=" * 70)
print("DROP-OFF BY ACQUISITION CHANNEL (end-to-end approval rate)")
print("=" * 70)
approval_by_channel = df.groupby("channel")["approved"].mean().sort_values(ascending=False) * 100
print(approval_by_channel.round(1))
