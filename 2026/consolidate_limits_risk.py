import pandas as pd
import numpy as np
from risk_engine import assess_trade

# Load data
risk_df = pd.read_csv('scoring_ergebnisse_cleaned.csv', delimiter=';')
try:
    order_df = pd.read_csv('order_file.csv', delimiter=',', encoding='utf-8')
except UnicodeDecodeError:
    order_df = pd.read_csv('order_file.csv', delimiter=',', encoding='cp1252')

# Clean headers
risk_df.columns = risk_df.columns.str.strip().str.replace('[^a-zA-Z0-9_]', '', regex=True)
order_df.columns = order_df.columns.str.strip().str.replace('[^a-zA-Z0-9_]', '', regex=True)


# Only Limitiert orders
filtered_orders = order_df[order_df['Ordertyp'] == 'Limitiert'].copy()

# Merge risk data into orders by WKN
merged = filtered_orders.merge(
    risk_df, how='left', on='WKN', suffixes=('_order', '_risk')
)
def safe_float(val):
    if isinstance(val, str):
        # Remove thousands separator
        return float(val.replace(',', '').replace(' ', ''))
    return float(val)

def safe_int(val):
    if pd.isnull(val) or val == '' or (isinstance(val, float) and np.isnan(val)):
        return 0
    if isinstance(val, str):
        return int(val.replace(',', '').replace(' ', ''))
    return int(val)


def process_row(row):
    try:
        # Use 'Nom' if it exists and is not null/empty/zero, else fallback to 'ANom'
        order_qty = row.get('Nom', np.nan)
        if pd.isnull(order_qty) or order_qty in ['', 0, 0.0] or (isinstance(order_qty, str) and order_qty.strip() == ''):
            order_qty = row.get('ANom', np.nan)
        if pd.isnull(order_qty) or order_qty in ['', 0, 0.0] or (isinstance(order_qty, str) and order_qty.strip() == ''):
            raise ValueError("Both 'Nom' and 'ANom' are missing or empty for this row, cannot compute risk.")



        
        result = assess_trade(
            order_qty=safe_float(order_qty),
            price=safe_float(row['Limit']),
            jim=safe_float(row['JIM_Value']),
            mp=safe_int(row['Target_Market_Count']),
            spread=abs(safe_float(row['Spread_Prozentual'])),
            tgv=safe_float(row['Tradegate_Volume']),
            stockname=row.get('Krzel', ''),
            wkn=row['WKN']
        )

        return pd.Series({
            'Risk Score': result['Risk Score'],
            'Decision': result['Decision'],
            'Reasons': result['Reasons'],
            'mp_risk': result['mp_risk'],
            'spread_risk': result['spread_risk'],
            'jim_risk': result['jim_risk'],
            'tgv_risk': result['tgv_risk']
        })
    except Exception as ex:
        return pd.Series({
            'Risk Score': 'N/A',
            'Decision': 'Error',
            'Reasons': str(ex),
            'mp_risk': 'N/A',
            'spread_risk': 'N/A',
            'jim_risk': 'N/A',
            'tgv_risk': 'N/A'
        })
# Score each row
risked = merged.apply(process_row, axis=1)

def get_qty(row):
    qty = row['Nom']
    if pd.isnull(qty) or qty in ['', 0, 0.0] or (isinstance(qty, str) and qty.strip() == ''):
        qty = row['ANom']
    return safe_float(qty)

# Assume your merged DataFrame is called 'final' after merging risk and order data



# First concat everything to one big DataFrame
final = pd.concat([merged, risked], axis=1)

# Add the Order_Value column to 'final' BEFORE subsetting
final['Order_Value'] = final.apply(lambda row: safe_float(row['Limit']) * get_qty(row), axis=1)

# Now prepare your output columns as before
output_columns = [
    'Status', 'Ordertyp', 'WKN', 'Limit', 'Nom', 'ANom', 'Order_Value',
    'Timestamp', # Change this to your actual column if needed!
    'JIM_Value', 'Spread_Prozentual', 'Target_Market_Count', 'Tradegate_Volume',
    'Risk Score', 'Decision', 'Reasons', 'jim_risk', 'spread_risk', 'mp_risk', 'tgv_risk'
]
output_columns_existing = [c for c in output_columns if c in final.columns]

# Now you create the subset (ordering as you want)
final_subset = final[output_columns_existing]

# Save result
final_subset.to_excel('consolidated_orders_risk.xlsx', index=False)
final_subset.to_csv('consolidated_orders_risk.csv', index=False)


print("Created consolidated_orders_risk.xlsx and consolidated_orders_risk.csv")
