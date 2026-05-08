import numpy as np
import pandas as pd

def mp_risk(mp):
    if mp == 0:
        return 10, "No liquidity (Market count = 0)"
    elif mp == 1:
        return 8, "Very illiquid (Market count = 1)"
    elif mp == 2:
        return 4, "Low liquidity (Market count = 2)"
    elif mp == 3:
        return 2, "Borderline liquidity (Market count = 3)"
    else:
        return 0, None

def spread_risk(spread):
    if spread < 0.01:
        risk = spread / 0.01
        return risk, None
    elif 0.01 <= spread <= 0.048:
        risk = 2500/19 * spread - 0.3157
        reason = f"Moderate spread ({spread:.2f}%) - risk: {risk:.2f}"
        return risk, reason
    else:
        risk = 10 - 5.085 * np.exp(-5 * spread)
        reason = f"Wide spread ({spread:.2f}%) - risk: {risk:.2f}"
        return risk, reason

def jim_risk(jim, order_value):
    if jim == 0 or jim is None or pd.isnull(jim):
        return 10, "No Jim value provided, high risk"
    if order_value < 5000:
        if jim > order_value:
            return order_value * 2 / 5000, "Jim value can cover small order, very low risk"
        else:
            return 10, "Jim value is less than order value, high risk for small order"
    elif 5000 <= order_value <= 9000:
        if jim > order_value:
            return 0.001 * order_value - 3, "Jim value can cover medium order, with low risk"
        else:
            return 10, "Jim value is less than order value, high risk for medium order"
    elif order_value > 9000:
        if jim > order_value:
    # For a smoother, more realistic log growth: score goes from 6 at 9000 to 10 at 100000 and above
            def capped_log_risk(x, lower=9000, score_min=6, score_max=10, cap_val=100000):
                log_ratio = np.log(x / lower)
                log_cap = np.log(cap_val / lower)
                score = score_min + (score_max - score_min) * (log_ratio / log_cap)
                return min(score, score_max)
            y = capped_log_risk(order_value)
            return y, "Jim value can cover large order (above 9000), risk increases logarithmically with order size"

        else:
            return 10, "Jim value is less than order value, high risk for large order"

def tgv_risk(tgv, order_value):
    if tgv == 0 or tgv is None or pd.isnull(tgv):
        return 10, "No Trade Gate Volume value provided, high risk"
    if tgv < order_value:
        return 10, "Trade gate volume is less than order value, High Risk"
    if order_value < 0:
        raise ValueError("Order value must be non-negative")
    if order_value <= 3360:
        risk = (order_value / 3360) * 3
        return risk, "Order value is small, low risk"
    elif order_value <= 5160:
        risk = ((order_value - 3360) / (5160 - 3360)) * 3 + 3
        return risk, "Order value is medium, moderate risk"
    else:
        base_value = 5160
        max_score = 10
        min_score = 6
        target_value = 10000
        target_score = 9
        stretch = np.log(target_value / base_value)
        x = order_value
        score = min_score + (max_score - min_score) * (np.log(x / base_value) / stretch)
        if score > max_score:
            score = max_score
        return score, "Order value is large (above 5160), high risk"

def make_per_field_decision(mp_score, spread_score, jim_score, tgv_score, jim_value_present):
    manual_components = []

    if jim_score == 10 and tgv_score == 10:
        manual_components.append('jim+tgv')

    if jim_value_present:
        if jim_score > 8 or (jim_score > 6 and mp_score >= 2):
            manual_components.append('jim')
        if mp_score >= 8:
            manual_components.append('mp')
        if spread_score > 6:
            manual_components.append('spread')
    else:
        if tgv_score > 8 or (tgv_score > 6 and mp_score >= 2):
            manual_components.append('tgv')
        if mp_score >= 8:
            manual_components.append('mp')
        if spread_score > 6:
            manual_components.append('spread')

    if manual_components:
        return 'Manual', manual_components
    else:
        return 'Automatic', []


def assess_trade(order_qty, price, jim, mp, spread, tgv, stockname="(N/A)", wkn="(N/A)"):
    order_value = order_qty * price
    mp_score, mp_reason = mp_risk(mp)
    spread_score, spread_reason = spread_risk(spread)
    jim_score, jim_reason = jim_risk(jim, order_value)
    tgv_score, tgv_reason = tgv_risk(tgv, order_value)

    # Detect if Jim value is valid for decision
    jim_value_present = jim is not None and not pd.isnull(jim) and jim != 0

    # Always sum all components (for informational/statistical risk score)
    risk_score = mp_score + spread_score + jim_score + tgv_score

    # Decision and reasoning logic: only use tgv if jim is missing
    decision, manual_components = make_per_field_decision(
        mp_score, spread_score, jim_score, tgv_score, jim_value_present
    )
    reasons_dict = {
        'mp': mp_reason,
        'spread': spread_reason,
        'jim': jim_reason,
        'tgv': tgv_reason
    }
    if decision == 'Manual':
        reasons = [reasons_dict[comp] for comp in manual_components if reasons_dict[comp]]
    else:
        reasons = ["All risk factors within automatic limits"]

    return {
        "Stock Name": stockname,
        "WKN": wkn,
        "Order Qty": order_qty,
        "Price": price,
        "Order Value": order_value,
        "MP": mp,
        "Spread": spread,
        "Jim": jim,
        "TGV": tgv,
        "Risk Score": risk_score,
        "Decision": decision,
        "Reasons": "; ".join(reasons),
        "mp_risk": mp_score,
        "spread_risk": spread_score,
        "jim_risk": jim_score,
        "tgv_risk": tgv_score
    }

