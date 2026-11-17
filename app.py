import streamlit as st
import pandas as pd
import plotly.express as px

from data_preprocessing import preprocess_data
from data_analysis import (
    get_statistical_summary,
    calculate_all_kpis
)


# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)


# --------------------------------
# APPLICATION TITLE
# --------------------------------

st.title("📊 Sales Analytics Dashboard")

st.markdown(
    "### Interactive Business Intelligence & Data Analysis"
)

st.markdown("---")


# --------------------------------
# DATA UPLOAD
# --------------------------------

st.sidebar.header("Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV, Excel or JSON file",
    type=["csv", "xlsx", "json"]
)


# --------------------------------
# FILE READING FUNCTION
# --------------------------------

def load_data(file):

    extension = file.name.split(".")[-1].lower()

    if extension == "csv":
        return pd.read_csv(file)

    elif extension == "xlsx":
        return pd.read_excel(file)

    elif extension == "json":
        return pd.read_json(file)

    else:
        raise ValueError("Unsupported file format")


# --------------------------------
# MAIN APPLICATION
# --------------------------------

if uploaded_file is not None:

    try:

        # Read uploaded dataset
        raw_df = load_data(uploaded_file)

        if raw_df.empty:
            st.error("Uploaded dataset is empty.")
            st.stop()

        st.success("Dataset uploaded successfully!")

        # --------------------------------
        # DATA VALIDATION
        # --------------------------------

        st.header("1. Data Validation")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Rows", raw_df.shape[0])

        col2.metric("Total Columns", raw_df.shape[1])

        col3.metric(
            "Duplicate Records",
            raw_df.duplicated().sum()
        )

        with st.expander("View Dataset"):

            st.dataframe(raw_df, use_container_width=True)

        with st.expander("Column Names and Data Types"):

            schema = pd.DataFrame({
                "Column": raw_df.columns,
                "Data Type": raw_df.dtypes.astype(str).values,
                "Missing Values": raw_df.isnull().sum().values
            })

            st.dataframe(schema, use_container_width=True)

        # --------------------------------
        # DATA PREPROCESSING
        # --------------------------------

        st.header("2. Data Preprocessing")

        df, duplicates_removed = preprocess_data(raw_df)

        st.success("Data preprocessing completed!")

        st.write(
            f"Duplicate records removed: {duplicates_removed}"
        )

        st.write(
            f"Remaining records: {len(df)}"
        )

        with st.expander("View Cleaned Dataset"):

            st.dataframe(df, use_container_width=True)

        # --------------------------------
        # REQUIRED COLUMN VALIDATION
        # --------------------------------

        required_columns = [
            "sales",
            "profit",
            "quantity",
            "order_id",
            "region",
            "category"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            st.error(
                f"Required columns missing: {missing_columns}"
            )

            st.stop()

        # --------------------------------
        # INTERACTIVE FILTERS
        # --------------------------------

        st.header("3. Interactive Filters")

        filter1, filter2, filter3 = st.columns(3)

        filtered_df = df.copy()

        with filter1:

            regions = ["All"] + sorted(
                filtered_df["region"].dropna().unique().tolist()
            )

            selected_region = st.selectbox(
                "Select Region",
                regions
            )

        with filter2:

            categories = ["All"] + sorted(
                filtered_df["category"].dropna().unique().tolist()
            )

            selected_category = st.selectbox(
                "Select Category",
                categories
            )

        with filter3:

            segments = (
                ["All"] + sorted(filtered_df["segment"].dropna().unique().tolist())
                if "segment" in filtered_df.columns
                else ["All"]
            )

            selected_segment = st.selectbox(
                "Select Segment",
                segments
            )

        # Apply filters

        if selected_region != "All":

            filtered_df = filtered_df[
                filtered_df["region"] == selected_region
            ]

        if selected_category != "All":

            filtered_df = filtered_df[
                filtered_df["category"] == selected_category
            ]

        if selected_segment != "All":

            filtered_df = filtered_df[
                filtered_df["segment"] == selected_segment
            ]

        # --------------------------------
        # DATE FILTER
        # --------------------------------

        if "order_date" in filtered_df.columns:

            valid_dates = filtered_df["order_date"].dropna()

            if not valid_dates.empty:

                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()

                selected_dates = st.date_input(
                    "Select Order Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )

                if len(selected_dates) == 2:

                    start_date, end_date = selected_dates

                    filtered_df = filtered_df[
                        (filtered_df["order_date"].dt.date >= start_date) &
                        (filtered_df["order_date"].dt.date <= end_date)
                    ]

        if filtered_df.empty:

            st.warning("No records found for selected filters.")
            st.stop()

        # --------------------------------
        # KPI DASHBOARD
        # --------------------------------

        st.header("4. Key Performance Indicators")

        kpis = calculate_all_kpis(filtered_df)

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

        kpi1.metric(
            "Total Sales",
            f"${kpis['Total Sales']:,.2f}"
        )

        kpi2.metric(
            "Total Profit",
            f"${kpis['Total Profit']:,.2f}"
        )

        kpi3.metric(
            "Total Orders",
            f"{kpis['Total Orders']:,}"
        )

        kpi4.metric(
            "Quantity Sold",
            f"{kpis['Total Quantity Sold']:,.0f}"
        )

        kpi5.metric(
            "Profit Margin",
            f"{kpis['Profit Margin (%)']:.2f}%"
        )

        # --------------------------------
        # VISUALIZATIONS
        # --------------------------------

        st.header("5. Interactive Visualizations")

        # Chart 1: Sales by Region

        region_sales = filtered_df.groupby(
            "region"
        )["sales"].sum().reset_index()

        fig1 = px.bar(
            region_sales,
            x="region",
            y="sales",
            color="region",
            title="Sales by Region",
            labels={
                "region": "Region",
                "sales": "Total Sales"
            }
        )

        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: Profit by Category

        category_profit = filtered_df.groupby(
            "category"
        )["profit"].sum().reset_index()

        fig2 = px.bar(
            category_profit,
            x="category",
            y="profit",
            color="category",
            title="Profit by Category"
        )

        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3: Monthly Sales Trend

        if "order_date" in filtered_df.columns:

            monthly_data = filtered_df.dropna(
                subset=["order_date"]
            ).copy()

            if not monthly_data.empty:

                monthly_data["Month"] = (
                    monthly_data["order_date"].dt.to_period("M").astype(str)
                )

                monthly_sales = monthly_data.groupby(
                    "Month"
                )["sales"].sum().reset_index()

                fig3 = px.line(
                    monthly_sales,
                    x="Month",
                    y="sales",
                    markers=True,
                    title="Monthly Sales Trend"
                )

                st.plotly_chart(
                    fig3,
                    use_container_width=True
                )

        # Chart 4: Sales Distribution

        category_sales = filtered_df.groupby(
            "category"
        )["sales"].sum().reset_index()

        fig4 = px.pie(
            category_sales,
            names="category",
            values="sales",
            title="Sales Distribution by Category"
        )

        st.plotly_chart(fig4, use_container_width=True)

        # --------------------------------
        # STATISTICAL ANALYSIS
        # --------------------------------

        st.header("6. Statistical Analysis")

        summary = get_statistical_summary(filtered_df)

        st.dataframe(
            summary,
            use_container_width=True
        )

        # --------------------------------
        # DOWNLOAD CLEANED DATA
        # --------------------------------

        st.header("7. Download Processed Dataset")

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Cleaned CSV",
            data=csv_data,
            file_name="cleaned_sales_data.csv",
            mime="text/csv"
        )

    except Exception as e:

        st.error(f"An error occurred: {e}")

else:

    st.info(
        "Please upload a CSV, Excel or JSON dataset "
        "using the sidebar to get started."
    )

    st.markdown(
        """
        ### Dashboard Features

        - 📁 Multiple file format support
        - 🧹 Data preprocessing and validation
        - 🎛️ Interactive filters
        - 📈 Dynamic KPIs
        - 📊 Interactive charts
        - 📉 Statistical analysis
        """
    )