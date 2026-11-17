import pandas as pd
import numpy as np


# 1. Generate Statistical Summary
def get_statistical_summary(df):

    numeric_df = df.select_dtypes(include=np.number)

    summary = numeric_df.describe().T

    summary["missing_values"] = df[
        numeric_df.columns
    ].isnull().sum()

    return summary


# 2. Calculate Total Sales
def calculate_total_sales(df):

    if "sales" not in df.columns:
        return 0

    return df["sales"].sum()


# 3. Calculate Total Profit
def calculate_total_profit(df):

    if "profit" not in df.columns:
        return 0

    return df["profit"].sum()


# 4. Calculate Total Orders
def calculate_total_orders(df):

    if "order_id" not in df.columns:
        return 0

    return df["order_id"].nunique()


# 5. Calculate Total Quantity Sold
def calculate_total_quantity(df):

    if "quantity" not in df.columns:
        return 0

    return df["quantity"].sum()


# 6. Calculate Profit Margin
def calculate_profit_margin(df):

    total_sales = calculate_total_sales(df)

    total_profit = calculate_total_profit(df)

    if total_sales == 0:
        return 0

    profit_margin = (total_profit / total_sales) * 100

    return profit_margin


# 7. Calculate All KPIs Together
def calculate_all_kpis(df):

    kpis = {

        "Total Sales": calculate_total_sales(df),

        "Total Profit": calculate_total_profit(df),

        "Total Orders": calculate_total_orders(df),

        "Total Quantity Sold": calculate_total_quantity(df),

        "Profit Margin (%)": calculate_profit_margin(df)

    }

    return kpis