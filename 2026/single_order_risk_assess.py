import pandas as pd
import numpy as np
from risk_engine import assess_trade

# --- LOAD RISK TABLE ---
risk_df = pd.read_csv('scoring_ergebnisse_cleaned.csv', delimiter=';')
# Clean headers
risk_df.columns = risk_df.columns.str.strip().str.replace('[^a-zA-Z0-9_]', '', regex=True)

# --- USER INPUT SECTION ---
print("====== SINGLE ORDER RISK CHECK ======")
wkn = input("Enter WKN: ").strip()
stockname = input("Enter Stock name: ").strip()
try:
    price = float(input("Enter Order price (Limit): ").replace(',', '.').replace(' ', ''))
except Exception:
    price = float(input("Please enter a valid numeric value for Order price: ").replace(',', '.').replace(' ', ''))

# Try to use Nom first, else ask for ANom
try:
    qty = float(input("Enter Quantity (Nom - leave blank if not available): ").replace(',', '.').replace(' ', '') or 0)
except Exception:
    qty = 0

if qty == 0:
    try:
        qty = float(input("Enter Quantity (ANom): ").replace(',', '.').replace(' ', ''))
    except Exception:
        print("No valid quantity entered. Exiting.")
        exit()

# --- FIND RISK PARAMS ---
row = risk_df[risk_df['WKN'] == wkn]

if row.empty:
    print(f"WKN {wkn} not found in your risk feature table.")
    print(risk_df[['WKN']].head())
    exit()

params = row.iloc[0]

try:
    # --- ASSESS TRADE ---
    result = assess_trade(
        order_qty=qty,
        price=price,
        jim=float(params["JIM_Value"]),
        mp=int(params["Target_Market_Count"]),
        spread=float(params["Spread_Prozentual"]),
        tgv=float(params["Tradegate_Volume"]),
        stockname=stockname,
        wkn=wkn
    )
except Exception as ex:
    print(f"Error during risk assessment: {ex}")
    exit()

# --- PRINT DETAILED OUTCOME ---
print("\n====== RISK ASSESSMENT RESULT ======")
print(f"Stock:                 {result['Stock Name']} ({result['WKN']})")
print(f"Order Quantity:        {result['Order Qty']}")
print(f"Limit (Price):         {result['Price']}")
print(f"Order Value:           {result['Order Value']:.2f}")
print(f"Market Participation:  {result['MP']}")
print(f"Spread %:              {result['Spread']:.4f}")
print(f"Jim Value:             {result['Jim']}")
print(f"Tradegate Volume:      {result['TGV']}")
print(f"-------------------------------")
print(f"Risk Score (sum):      {result['Risk Score']:.2f}")
print(f"Decision:              {result['Decision']}")
print(f"Reasons:               {result['Reasons']}")
print(f"mp_risk:               {result['mp_risk']}")
print(f"spread_risk:           {result['spread_risk']:.2f}")
print(f"jim_risk:              {result['jim_risk']:.2f}")
print(f"tgv_risk:              {result['tgv_risk']:.2f}")
print("\n====================================")
