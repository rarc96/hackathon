import pandas as pd

# === LOAD DATA ===
df = pd.read_excel('consolidated_orders_risk.xlsx')  # Make sure your file name is correct

# === DATA CLEANING ===

# Convert key columns to numeric and drop rows where they are missing
df['Limit'] = pd.to_numeric(df['Limit'], errors='coerce')
df['Spread_Prozentual'] = pd.to_numeric(df['Spread_Prozentual'], errors='coerce')
df['Risk Score'] = pd.to_numeric(df['Risk Score'], errors='coerce')

before = len(df)
df = df.dropna(subset=['Limit', 'Spread_Prozentual', 'Risk Score']).reset_index(drop=True)
after = len(df)
print(f"Dropped {before - after} rows with missing 'Limit', 'Spread_Prozentual', or 'Risk Score'. {after} remain.")

# === ENSURE FLAG COLUMNS ===
manual_keywords = ["abgelehnt", "schwebend", "aussetzung", "timer"]
manual_statuses = ["gelöscht", "löschung"]

if 'Manual_Actual' not in df.columns:
    df['Status_norm'] = df['Status'].astype(str).str.lower()
    def status_to_manual(s):
        if any(k in s for k in manual_keywords):
            return 1
        if any(s.startswith(ms) for ms in manual_statuses):
            return 1
        return 0
    df['Manual_Actual'] = df['Status_norm'].apply(status_to_manual)
if 'Algo_Manual' not in df.columns:
    df['Decision_norm'] = df['Decision'].astype(str).str.lower()
    df['Algo_Manual'] = (df['Decision_norm'] == 'manual').astype(int)

# === FALSE POSITIVE (EXCESS MANUAL) ANALYSIS ===
false_pos = df[(df['Manual_Actual'] == 0) & (df['Algo_Manual'] == 1)]
print(f"Total false positives (after cleaning): {len(false_pos)}\n")

# Columns of interest:
out_cols = [
    "WKN", "Limit", "Nom", "Order_Value", "JIM_Value",
    "Spread_Prozentual", "Target_Market_Count", "Tradegate_Volume",
    "mp_risk", "spread_risk", "jim_risk", "tgv_risk",
    "Risk Score", "Reasons", "Status"
]
cols_exist = [c for c in out_cols if c in false_pos.columns]

display_cols = false_pos[cols_exist].copy()
display_cols['Expected_Algo_Decision'] = 'Automatic'

print("\nFalse positives – risk scores and reasons (head 20):")
print(display_cols.head(20))

# Export to Excel for audit/review
display_cols.to_excel("false_positives_risks_and_reasons.xlsx", index=False)
print("\nDetailed false positives saved to: false_positives_risks_and_reasons.xlsx")
