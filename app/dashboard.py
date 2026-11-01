
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text

# Make the project root importable
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from ml.db import get_engine


st.set_page_config(
    page_title="Customer Churn Dashboard",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# DATA
# --------------------------------------------------

@st.cache_data(ttl=60)
def load_dashboard_data():
    engine = get_engine()

    query = text("""
        SELECT
            customer_id,
            churn_probability,
            predicted_churn,
            model_version,
            scored_at,
            contract,
            tenure,
            tenure_bucket,
            monthly_charges,
            internet_service,
            payment_method
        FROM analytics.churn_dashboard
    """)

    try:
        with engine.connect() as connection:
            return pd.read_sql(query, connection)
    finally:
        engine.dispose()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("Customer Churn Dashboard")
st.caption("Customer churn predictions and retention insights")


try:
    df = load_dashboard_data()
except Exception as error:
    st.error(
        "Unable to load dashboard data. "
        "Make sure the predictions table and dbt model exist."
    )
    st.exception(error)
    st.stop()


if df.empty:
    st.warning("No prediction data is currently available.")
    st.stop()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

contracts = sorted(df["contract"].dropna().unique())

selected_contracts = st.sidebar.multiselect(
    "Contract type",
    contracts,
    default=contracts
)

internet_services = sorted(
    df["internet_service"].dropna().unique()
)

selected_internet = st.sidebar.multiselect(
    "Internet service",
    internet_services,
    default=internet_services
)

min_probability = st.sidebar.slider(
    "Minimum churn probability",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.05
)


filtered_df = df[
    df["contract"].isin(selected_contracts)
    & df["internet_service"].isin(selected_internet)
    & (df["churn_probability"] >= min_probability)
].copy()


if filtered_df.empty:
    st.warning("No customers match the selected filters.")
    st.stop()


# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

total_customers = len(filtered_df)

predicted_churn_rate = (
    filtered_df["predicted_churn"].mean() * 100
)

high_risk_customers = (
    filtered_df["churn_probability"] >= 0.70
).sum()

last_scoring_time = pd.to_datetime(
    filtered_df["scored_at"],
    utc=True
).max()

st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total customers",
    f"{total_customers:,}"
)

col2.metric(
    "Predicted churn rate",
    f"{predicted_churn_rate:.1f}%"
)

col3.metric(
    "High-risk customers",
    f"{high_risk_customers:,}"
)

col4.metric(
    "Last scoring time",
    last_scoring_time.strftime("%Y-%m-%d %H:%M UTC")
)


# --------------------------------------------------
# TOP AT-RISK CUSTOMERS
# --------------------------------------------------

st.divider()
st.subheader("Top 20 At-Risk Customers")

top_customers = (
    filtered_df
    .sort_values("churn_probability", ascending=False)
    .head(20)
    .copy()
)

top_customers["churn_probability"] = (
    top_customers["churn_probability"] * 100
).round(1)

top_customers["monthly_charges"] = (
    top_customers["monthly_charges"].round(2)
)

st.dataframe(
    top_customers[
        [
            "customer_id",
            "churn_probability",
            "contract",
            "tenure",
            "monthly_charges"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# SEGMENT ANALYSIS
# --------------------------------------------------

st.divider()
st.subheader("Churn by Customer Segment")

col1, col2 = st.columns(2)

with col1:
    contract_churn = (
        filtered_df
        .groupby("contract", as_index=False)
        .agg(predicted_churn_rate=("predicted_churn", "mean"))
    )

    contract_churn["predicted_churn_rate"] *= 100

    fig_contract = px.bar(
        contract_churn,
        x="contract",
        y="predicted_churn_rate",
        title="Predicted churn rate by contract",
        labels={
            "contract": "Contract",
            "predicted_churn_rate": "Predicted churn (%)"
        }
    )

    st.plotly_chart(fig_contract, use_container_width=True)


with col2:
    internet_churn = (
        filtered_df
        .groupby("internet_service", as_index=False)
        .agg(predicted_churn_rate=("predicted_churn", "mean"))
    )

    internet_churn["predicted_churn_rate"] *= 100

    fig_internet = px.bar(
        internet_churn,
        x="internet_service",
        y="predicted_churn_rate",
        title="Predicted churn rate by internet service",
        labels={
            "internet_service": "Internet service",
            "predicted_churn_rate": "Predicted churn (%)"
        }
    )

    st.plotly_chart(fig_internet, use_container_width=True)


# --------------------------------------------------
# MODEL EXPLAINABILITY
# --------------------------------------------------

st.divider()
st.subheader("Model Explainability")

shap_path = ROOT_DIR / "ml" / "reports" / "shap_summary.png"

if shap_path.exists():
    st.image(
        str(shap_path),
        caption="SHAP global feature importance"
    )
else:
    st.info("SHAP summary image not found in ml/reports/.")


# --------------------------------------------------
# MODEL COMPARISON
# --------------------------------------------------

st.subheader("Model Comparison")

comparison_path = (
    ROOT_DIR / "ml" / "reports" / "training_report.json"
)

if comparison_path.exists():
    comparison_df = pd.read_json(comparison_path)
    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info(
        "Model comparison CSV not found. "
        "Add your evaluation results to ml/reports/."
    )


st.markdown("""
**Model interpretation:** SHAP values explain how features contribute
to model predictions. They indicate associations learned by the model,
not causal relationships.
""")



