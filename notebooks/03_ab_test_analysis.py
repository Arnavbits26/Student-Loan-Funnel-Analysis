"""
Student Loan Application Funnel Optimizer
Step 3: A/B test -- did the simplified onboarding flow (Treatment) actually
improve onboarding completion vs. the original flow (Control)?

Uses a two-proportion z-test (standard for comparing conversion rates
between two groups) rather than just eyeballing a percentage difference.
"""

import pandas as pd
import numpy as np
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

df = pd.read_csv("/home/claude/student_loan_funnel/data/applications.csv")

# Only applicants who passed eligibility are actually exposed to the
# onboarding flow -- that's the correct denominator for this test.
elig = df[df["passed_eligibility"]]

control = elig[elig["ab_group"] == "Control"]
treatment = elig[elig["ab_group"] == "Treatment"]

n_control = len(control)
n_treatment = len(treatment)
conv_control = control["completed_onboarding"].sum()
conv_treatment = treatment["completed_onboarding"].sum()

rate_control = conv_control / n_control
rate_treatment = conv_treatment / n_treatment

print("=" * 70)
print("A/B TEST: Onboarding completion rate, Control vs. Treatment")
print("=" * 70)
print(f"Control   (original onboarding):   n={n_control:,}, conversions={conv_control:,}, rate={rate_control:.2%}")
print(f"Treatment (simplified onboarding):  n={n_treatment:,}, conversions={conv_treatment:,}, rate={rate_treatment:.2%}")

abs_lift = rate_treatment - rate_control
rel_lift = abs_lift / rate_control * 100
print(f"\nAbsolute lift: {abs_lift:+.2%} (percentage points)")
print(f"Relative lift: {rel_lift:+.1f}%")

# Two-proportion z-test
count = np.array([conv_treatment, conv_control])
nobs = np.array([n_treatment, n_control])
z_stat, p_value = proportions_ztest(count, nobs)

# 95% confidence intervals for each group's conversion rate
ci_control = proportion_confint(conv_control, n_control, alpha=0.05, method="wilson")
ci_treatment = proportion_confint(conv_treatment, n_treatment, alpha=0.05, method="wilson")

print("\n" + "=" * 70)
print("STATISTICAL SIGNIFICANCE")
print("=" * 70)
print(f"z-statistic: {z_stat:.3f}")
print(f"p-value: {p_value:.6f}")
print(f"Control 95% CI:   [{ci_control[0]:.2%}, {ci_control[1]:.2%}]")
print(f"Treatment 95% CI: [{ci_treatment[0]:.2%}, {ci_treatment[1]:.2%}]")

alpha = 0.05
if p_value < alpha:
    print(f"\n-> RESULT: Statistically significant at alpha={alpha} (p={p_value:.4f} < {alpha}).")
    print(f"   The simplified onboarding flow produced a real, measurable lift.")
else:
    print(f"\n-> RESULT: NOT statistically significant at alpha={alpha} (p={p_value:.4f}).")
    print(f"   Cannot conclude the treatment caused the observed difference.")

# Save results for the dashboard / report
results = {
    "n_control": n_control,
    "n_treatment": n_treatment,
    "conversions_control": int(conv_control),
    "conversions_treatment": int(conv_treatment),
    "rate_control": rate_control,
    "rate_treatment": rate_treatment,
    "absolute_lift_pp": abs_lift,
    "relative_lift_pct": rel_lift,
    "z_statistic": z_stat,
    "p_value": p_value,
    "ci_control_low": ci_control[0],
    "ci_control_high": ci_control[1],
    "ci_treatment_low": ci_treatment[0],
    "ci_treatment_high": ci_treatment[1],
    "significant_at_05": bool(p_value < alpha),
}
pd.Series(results).to_csv("/home/claude/student_loan_funnel/output/ab_test_results.csv")
print(f"\nSaved results -> output/ab_test_results.csv")
