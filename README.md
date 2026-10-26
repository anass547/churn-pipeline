# churn_pipeline :

End-to-end customer churn prediction pipeline: raw data is loaded into PostgreSQL, cleaned with SQL transformations, used to train a model that flags at-risk customers, and shown in a dashboard.

**Status:** 
(Phase 0 done: database + raw data load)
(Phase 1 done: dbt staging and features)


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

4. Configure dbt (one time). Create `~/.dbt/profiles.yml` (outside the repo) with a profile matching the one in `dbt_project/dbt_project.yml`:
   - type: `postgres`
   - host: `localhost`, port: `5432`
   - user / password / dbname: `churn`
   - schema: `analytics`
5. From inside `dbt_project/`:
   - `dbt debug` (all checks should pass)
   - `dbt run` (builds `stg_customers` and `customer_features`)
   - `dbt test` (all tests should pass)


## Project structure
```
churn-pipeline/
├── data/raw/          # CSV (not committed)
├── dbt_project/       # dbt models and tests
├── ml/                # loading and training scripts
├── dags/              # Airflow DAGs (planned)
├── app/               # Streamlit dashboard (planned)
├── tests/
├── reports/
├── LEARNINGS.md       # what I did, what broke, how I fixed it
└── README.md