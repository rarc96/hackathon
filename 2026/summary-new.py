import pandas as pd

# Load and clean
df = pd.read_excel('consolidated_orders_risk.xlsx')

# Ensure required columns are numeric for cleaning
for col in ["Limit", "Spread_Prozentual", "Risk Score"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df_clean = df.dropna(subset=['Limit', 'Spread_Prozentual', 'Risk Score']).reset_index(drop=True)

# Lowercase normalization for status/decision
df_clean['Status_norm'] = df_clean['Status'].astype(str).str.lower()
df_clean['Decision_norm'] = df_clean['Decision'].astype(str).str.lower()

# Consider only executed trades
exec_df = df_clean[df_clean['Status_norm'] == 'ausgeführt'].copy()

# Handle Verursacher as int if possible
try:
    exec_df['Verursacher_num'] = exec_df['Verursacher'].astype(int)
except Exception:
    exec_df['Verursacher_num'] = exec_df['Verursacher'].astype(str)

# Prior execution tag
exec_df['Prev_Execution'] = exec_df['Verursacher_num'].apply(
    lambda x: "Auto (6166050093)" if str(x) == "6166050093" else "Manual (≠ 6166050093)"
)
# Current (algo) decision
exec_df['Now_Algo'] = exec_df['Decision_norm'].apply(
    lambda x: "Algo Auto" if x == "automatic" else ("Algo Manual" if x == "manual" else "Other")
)



# Pivot/cross-tab summary
summary_pivot = pd.pivot_table(
    exec_df,
    index='Prev_Execution',
    columns='Now_Algo',
    values='WKN',  # Just use any column as counting
    aggfunc='count',
    fill_value=0
).reset_index()

# Order columns neatly for display
summary_pivot = summary_pivot[['Prev_Execution'] +
                              [col for col in ['Algo Auto', 'Algo Manual', 'Other'] if col in summary_pivot.columns]]

print("\nSummary of Algo Decision by Previous Execution (Status == 'Ausgeführt'):\n")
print(summary_pivot.to_markdown(index=False))



# Save to Excel for records
summary_pivot.to_excel("algo_decision_by_prev_execution.xlsx", index=False)
