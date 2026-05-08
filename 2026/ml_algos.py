import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# --- 1. LOAD & CLEAN DATA ---
df = pd.read_excel('consolidated_orders_risk.xlsx')

for col in ["Limit", "Spread_Prozentual", "Risk Score"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=['Limit', 'Spread_Prozentual', 'Risk Score']).reset_index(drop=True)
print(f"Loaded and cleaned: {len(df)} rows.")

# --- 2. ENSURE ACTUAL MANUAL LABEL ---
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

# --- 3. FEATURES FOR MACHINE LEARNING ---
feature_cols = [
    'Limit', 'Nom', 'ANom', 'Order_Value', 'JIM_Value',
    'Spread_Prozentual', 'Target_Market_Count', 'Tradegate_Volume'
]
for col in feature_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
X = df[feature_cols].fillna(0)
y = df['Manual_Actual']

# --- 4. DECISION TREE FOR RULE DISCOVERY ---
tree = DecisionTreeClassifier(max_depth=4, min_samples_leaf=10, random_state=42)
tree.fit(X, y)
tree_text = export_text(tree, feature_names=feature_cols)
print("\n=== TOP DECISION TREE RULES (predicting ACTUAL MANUAL) ===")
print(tree_text)

# --- 5. RANDOM FOREST FEATURE IMPORTANCES ---
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, y)
importances = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=False)

print("\n=== RANDOM FOREST FEATURE IMPORTANCES (actual manual status) ===")
print(importances)

plt.figure(figsize=(8, 5))
importances.plot(kind='bar')
plt.title("Feature Importances for Actual Manual Status")
plt.tight_layout()
plt.show()

# --- 6. (Optional) SHAP PLOT -- Uncomment if SHAP installed ---
# import shap
# explainer = shap.TreeExplainer(rf)
# shap_values = explainer.shap_values(X)
# shap.summary_plot(shap_values[1], X, feature_names=feature_cols)

# --- 7. DESCRIBE MANUAL TRADES ---
manual_trades = df[df['Manual_Actual'] == 1]
print("\n=== SUMMARY STATS FOR ACTUAL MANUAL TRADES ===")
print(manual_trades[feature_cols].describe())
print("\nMost common Status values for manual trades:")
print(manual_trades['Status'].value_counts())

# --- 8. Show a sample of manual trades for spot inspection ---
print("\nSample actual manual trades (with features/status):")
display_cols = ["WKN", "Limit", "Nom", "Order_Value", "JIM_Value",
    "Spread_Prozentual", "Target_Market_Count", "Tradegate_Volume", "Status"]
print(manual_trades[display_cols].head(10))
