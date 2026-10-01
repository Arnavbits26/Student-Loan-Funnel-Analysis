import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

funnel = pd.read_csv("/home/claude/student_loan_funnel/output/funnel_summary.csv")
ab = pd.read_csv("/home/claude/student_loan_funnel/output/ab_test_results.csv", index_col=0).squeeze("columns")
ab = pd.to_numeric(ab, errors="coerce")

DEEP = "#0A055A"
GREEN = "#1B7F3B"
GREY = "#888888"

# ---------- Funnel chart ----------
fig, ax = plt.subplots(figsize=(8, 5))
stages = funnel["stage"]
counts = funnel["count"]
colors = [DEEP, "#2B3F91", "#4A5FB5", "#7A8AD0", GREEN]

bars = ax.barh(stages[::-1], counts[::-1], color=colors[::-1], height=0.6)
for bar, cnt, pct in zip(bars, counts[::-1], funnel["pct_of_total"][::-1]):
    ax.text(bar.get_width() + 250, bar.get_y() + bar.get_height()/2,
             f"{cnt:,} ({pct:.0f}%)", va="center", fontsize=9.5)

ax.set_xlabel("Applicants")
ax.set_title("Student Loan Application Funnel\n(20,000 applicants, stage-wise conversion)", fontsize=12, color=DEEP, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.set_xlim(0, max(counts) * 1.22)
plt.tight_layout()
plt.savefig("/home/claude/student_loan_funnel/output/funnel_chart.png", dpi=170)
plt.close()

# ---------- Drop-off chart ----------
fig, ax = plt.subplots(figsize=(8, 4.5))
transitions = [f"{a}\n\u2193\n{b}" for a, b in zip(funnel["stage"][:-1], funnel["stage"][1:])]
dropoffs = funnel["drop_off_pct"][1:]
bars = ax.bar(range(len(transitions)), dropoffs, color="#C0392B", width=0.5)
for i, v in enumerate(dropoffs):
    ax.text(i, v + 0.5, f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(range(len(transitions)))
ax.set_xticklabels(transitions, fontsize=8.5)
ax.set_ylabel("Drop-off rate (% of previous stage)")
ax.set_title("Where applicants are lost at each funnel transition", fontsize=12, color=DEEP, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("/home/claude/student_loan_funnel/output/dropoff_chart.png", dpi=170)
plt.close()

# ---------- A/B test chart ----------
fig, ax = plt.subplots(figsize=(6.5, 5))
groups = ["Control\n(original flow)", "Treatment\n(simplified flow)"]
rates = [ab["rate_control"] * 100, ab["rate_treatment"] * 100]
errs = [
    [ab["rate_control"]*100 - ab["ci_control_low"]*100, ab["ci_control_high"]*100 - ab["rate_control"]*100],
    [ab["rate_treatment"]*100 - ab["ci_treatment_low"]*100, ab["ci_treatment_high"]*100 - ab["rate_treatment"]*100],
]
errs = list(zip(*errs))  # reshape to [lower, upper] per bar for yerr

bars = ax.bar(groups, rates, color=[GREY, GREEN], width=0.45,
               yerr=[[errs[0][0], errs[0][1]], [errs[1][0], errs[1][1]]], capsize=8)
for bar, rate in zip(bars, rates):
    ax.text(bar.get_x() + bar.get_width()/2, rate + 1.8, f"{rate:.1f}%", ha="center", fontsize=12, fontweight="bold")

ax.set_ylabel("Onboarding completion rate")
ax.set_ylim(0, 95)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_title(f"A/B Test: Simplified Onboarding Flow\n+{ab['absolute_lift_pp']*100:.1f}pp lift, p < 0.001 (statistically significant)",
              fontsize=11.5, color=DEEP, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("/home/claude/student_loan_funnel/output/ab_test_chart.png", dpi=170)
plt.close()

print("Saved 3 charts to output/")
