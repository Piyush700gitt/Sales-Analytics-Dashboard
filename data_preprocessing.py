import pandas as pd
import numpy as np


# 1. Standardize column names
def standardize_columns(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


# 2. Handle missing and invalid values
def handle_missing_values(df):

    df = df.copy()

    # Replace invalid values with NaN
    df.replace(
        ["unknown", "Unknown", "N/A", "n/a",
         "not available", "?", "inf", "-inf"],
        np.nan,
        inplace=True
    )

    # Convert numerical columns
    numeric_columns = ["sales", "profit", "quantity", "discount"]

    for col in numeric_columns:

        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

            median_value = df[col].median()

            if pd.notna(median_value):
                df[col] = df[col].fillna(median_value)

    # Fill categorical missing values
    categorical_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for col in categorical_columns:

        df[col] = df[col].fillna("Unknown")

    return df


# 3. Remove duplicate records
def remove_duplicates(df):

    initial_rows = len(df)

    df = df.drop_duplicates()

    removed_rows = initial_rows - len(df)

    return df, removed_rows


# 4. Standardize categorical values
def standardize_categories(df):

    df = df.copy()

    categorical_columns = [
        "region",
        "category",
        "segment",
        "ship_mode",
        "sub_category"
    ]

    for col in categorical_columns:

        if col in df.columns:

            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.title()
            )

    # Handle common inconsistent values
    if "ship_mode" in df.columns:

        df["ship_mode"] = df["ship_mode"].replace({
            "Sameday": "Same Day",
            "Standard Class": "Standard Class"
        })

    return df


# 5. Convert date columns
def convert_dates(df):

    df = df.copy()

    date_columns = ["order_date", "ship_date"]

    for col in date_columns:

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                format="mixed",
                errors="coerce",
                dayfirst=False
            )

    return df


# 6. Validate numerical values
def validate_numeric_data(df):

    df = df.copy()

    numeric_columns = [
        "sales",
        "profit",
        "quantity",
        "discount"
    ]

    # Convert columns into numeric format
    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # Replace infinite values
    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    # Handle invalid sales
    if "sales" in df.columns:

        df.loc[
            df["sales"] < 0,
            "sales"
        ] = np.nan

    # Handle invalid quantity
    if "quantity" in df.columns:

        df.loc[
            df["quantity"] <= 0,
            "quantity"
        ] = np.nan

    # Handle invalid discount
    if "discount" in df.columns:

        df.loc[
            (df["discount"] < 0) |
            (df["discount"] > 1),
            "discount"
        ] = np.nan

    return df

# 7. Complete preprocessing pipeline
def preprocess_data(df):

    df = df.copy()

    df = standardize_columns(df)

    df, duplicates_removed = remove_duplicates(df)

    df = standardize_categories(df)

    df = convert_dates(df)

    df = validate_numeric_data(df)

    df = handle_missing_values(df)

    return df, duplicates_removed