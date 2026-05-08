# -*- coding: utf-8 -*-
"""
Created on Fri May  8 02:41:27 2026

@author: riru401e
"""

import tkinter as tk
from tkinter import ttk


#%% Auxiliary Functions
def calculate_risk(wkn, order_type, quantity, price):
    """
    Add Rashmis function for the risk score
    Returns a list with:
    [JIM Value, Nr. MM, Relative Spread,
     TG Quote, Risk Score, Decision]
    """

    quantity = float(quantity)
    price = float(price)

    # Dummy calculations
    jim_value = round(quantity * price * 0.01, 2)
    nr_mm = 5
    relative_spread = round(price * 0.002, 4)
    tg_quote = round(price * 1.01, 2)

    # Example risk logic
    risk_score = round((quantity * price) / 1000, 2)

    if risk_score > 50:
        decision = "REJECT"
    elif risk_score > 20:
        decision = "CHECK"
    else:
        decision = "ACCEPT"

    return [
        jim_value,
        nr_mm,
        relative_spread,
        tg_quote,
        risk_score,
        decision
    ]


#%% Main Application
class RiskApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Risk Calculator")

        # ----------------------------
        # Button at the top
        # ----------------------------
        enter_button = ttk.Button(
            root,
            text="Enter Order",
            command=self.open_order_window
        )
        enter_button.grid(row=0, column=0, columnspan=2, pady=15)

        # ----------------------------
        # Labels for main fields
        # ----------------------------
        self.field_names = [
            "WKN",
            "JIM Value",
            "Nr. MM",
            "Relative Spread",
            "TG Quote",
            "Risk Score",
            "Decision"
        ]

        self.value_labels = {}

        # Fonts
        normal_font = ("Arial", 12)
        big_font = ("Arial", 18, "bold")

        # Create fields automatically
        for i, field in enumerate(self.field_names):

            label = ttk.Label(
                root,
                text=field + ":",
                font=normal_font
            )
            label.grid(row=i + 1, column=0, sticky="w", padx=10, pady=8)

            # Bigger font for Risk Score and Decision
            if field in ["Risk Score", "Decision"]:
                font_to_use = big_font
            else:
                font_to_use = normal_font

            value_label = ttk.Label(
                root,
                text="",
                font=font_to_use,
                foreground="blue"
            )

            value_label.grid(
                row=i + 1,
                column=1,
                sticky="w",
                padx=10,
                pady=8
            )

            self.value_labels[field] = value_label

    # ------------------------------------------------
    # Open second window
    # ------------------------------------------------
    def open_order_window(self):
        """
        Opens the second mask to introduce the 
        order details for later score computation
        """
        def insert_order():
            """
            Updates the Main values from the main window
            """
            wkn = entries["WKN"].get()
            order_type = entries["Order Type"].get()
            quantity = entries["Quantity"].get()
            price = entries["Price"].get()

            # Call calculation function
            result = calculate_risk(
                wkn,
                order_type,
                quantity,
                price
            )

            # Update main window fields
            self.value_labels["WKN"].config(text=wkn)
            self.value_labels["JIM Value"].config(text=result[0])
            self.value_labels["Nr. MM"].config(text=result[1])
            self.value_labels["Relative Spread"].config(text=result[2])
            self.value_labels["TG Quote"].config(text=result[3])
            self.value_labels["Risk Score"].config(text=result[4])
            self.value_labels["Decision"].config(text=result[5])

            # Close order window
            order_window.destroy()

        order_window = tk.Toplevel(self.root)
        order_window.title("Enter Order")

        fields = [
            "WKN",
            "Order Type",
            "Quantity",
            "Price"
        ]

        entries = {}

        # Create input fields
        for i, field in enumerate(fields):

            label = ttk.Label(order_window, text=field + ":")
            label.grid(row=i, column=0, padx=10, pady=8)

            entry = ttk.Entry(order_window)
            entry.grid(row=i, column=1, padx=10, pady=8)

            entries[field] = entry

        

        insert_button = ttk.Button(
            order_window,
            text="Insert Order",
            command=insert_order
        )

        insert_button.grid(
            row=len(fields),
            column=0,
            columnspan=2,
            pady=15
        )


#%% Main
if __name__ == "__main__":

    root = tk.Tk()
    app = RiskApp(root)

    root.mainloop()