import numpy as np
import pandas as pd

# ======================================
# 1. Load and Clean Data
# ======================================
df = pd.read_excel('consolidated_orders_risk.xlsx')

# Convert columns to numeric
for col in ["Limit", "Spread_Prozentual", "Risk Score"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

before = len(df)
df = df.dropna(subset=['Limit', 'Spread_Prozentual', 'Risk Score']).reset_index(drop=True)
after = len(df)
print(f"After cleaning: {after}/{before} rows remain (no missing Limit/Spread_Prozentual/Risk Score).\n")

# ======================================
# 2. Ensure Manual/Algo Flags
# ======================================
manual_keywords = ["abgelehnt", "schwebend", "aussetzung", "timer"]
manual_statuses = ["gelöscht", "löschung"]

df['Status_norm'] = df['Status'].astype(str).str.lower()
def status_to_manual(s):
    if any(k in s for k in manual_keywords):
        return 1
    if any(s.startswith(ms) for ms in manual_statuses):
        return 1
    return 0
df['Manual_Actual'] = df['Status_norm'].apply(status_to_manual)

df['Decision_norm'] = df['Decision'].astype(str).str.lower()
df['Algo_Manual'] = (df['Decision_norm'] == 'manual').astype(int)

# ======================================
# 3. Summary and False Neg/Pos Checks (all using CLEANED DATA)
# ======================================
manual_count = df['Manual_Actual'].sum()
automatic_count = (df['Manual_Actual'] == 0).sum()
algo_manual_count = df['Algo_Manual'].sum()
algo_auto_count = (df['Algo_Manual'] == 0).sum()

false_neg = df[(df['Manual_Actual'] == 1) & (df['Algo_Manual'] == 0)]  # Missed manual
false_pos = df[(df['Manual_Actual'] == 0) & (df['Algo_Manual'] == 1)]  # Flagged manual, should be auto
true_manual = df[(df['Manual_Actual'] == 1) & (df['Algo_Manual'] == 1)]
true_auto = df[(df['Manual_Actual'] == 0) & (df['Algo_Manual'] == 0)]

total = len(df)
assert total == after, "Algorithm is NOT using the cleaned data!"

# ======================================
print(f"\n--- HIGH-LEVEL AUTOMATION IMPACT (CLEANED DATA) ---")
print(f"Total trades (clean):                   {total}")
print(f"Trades needing manual (actual):         {manual_count} ({(manual_count/total):.1%})")
print(f"Trades processed automatically(actual): {automatic_count} ({(automatic_count/total):.1%})")
print(f"Algo flagged manual:                    {algo_manual_count} ({(algo_manual_count/total):.1%})")
print(f"Algo flagged automatic:                 {algo_auto_count} ({(algo_auto_count/total):.1%})")
print(f"False Negatives (missed manual):        {len(false_neg)} ({(len(false_neg)/total):.1%})")
print(f"False Positives (unnecessary manual):   {len(false_pos)} ({(len(false_pos)/total):.1%})")
print(f"Correct Auto:                           {len(true_auto)}")
print(f"Correct Manual:                         {len(true_manual)}")

summary = pd.DataFrame({
    'Type': [
        "Actual Manual (Status)", "Actual Auto (Status)",
        "Algo Manual", "Algo Auto",
        "False Negatives (risk)", "False Positives (excess manual)",
        "True Manual (matched)", "True Auto (matched)"
    ],
    'Count': [
        manual_count, automatic_count,
        algo_manual_count, algo_auto_count,
        len(false_neg), len(false_pos),
        len(true_manual), len(true_auto)
    ],
    'Percent': [
        manual_count/total, automatic_count/total,
        algo_manual_count/total, algo_auto_count/total,
        len(false_neg)/total, len(false_pos)/total,
        len(true_manual)/total, len(true_auto)/total
    ]
})

print("\nSummary Table (clean data):\n", summary)
summary.to_excel("manual_auto_summary_clean.xlsx", index=False)
