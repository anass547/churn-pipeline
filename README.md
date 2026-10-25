# churn_pipeline :

End-to-end customer churn prediction pipeline: raw data is loaded into PostgreSQL, cleaned with SQL transformations, used to train a model that flags at-risk customers, and shown in a dashboard.

**Status:** in progress (Phase 0 done: database + raw data load).

## The planned stack:
- PostgreSQL (storage)
- dbt (SQL transformations and tests)
- XGBoost + SHAP (model and explainability)
- Airflow (orchestration)
- Streamlit (dashboard)

## data :
Telco Customer Churn dataset (IBM sample data) from
[Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn).
## How to run (current state)
Prerequisites: Docker, Python 3.10+.
1. Create and activate a virtual environment, then install dependencies:
   `pip install -r requirements.txt`
2. Start the database: `docker compose up -d`
3. Load the data: `python ml/load.py`
