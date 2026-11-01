# Phase 0 — Environment Setup & Raw Data Ingestion

**Date:** October 25, 2026  
**Status:** Completed

## 0.1. What I Did

- Set up the project repository structure, Python virtual environment, and dependencies.
- Configured and launched PostgreSQL 16 using Docker Compose, with a named volume for persistent data storage and port `5432` exposed.
- Loaded the Telco Customer Churn dataset into PostgreSQL using the following pipeline:

  `CSV → pandas DataFrame → SQLAlchemy Engine → PostgreSQL`

- Stored the raw dataset in the `raw_customers` table.

## 0.2. What I Learned

- **SQLAlchemy Engine:** Manages database connections using a connection URL and allows pandas to interact with PostgreSQL.
- **pandas `to_sql()`:** Creates a database table and inserts DataFrame records using a SQLAlchemy engine.
- **Docker Named Volumes:** Persist database data even when the container is stopped or recreated, provided the volume is retained.
- **Raw Data Ingestion:** Loading source data into a raw table preserves the original structure for downstream transformation and cleaning.

## 0.3. Results

- **Database:** PostgreSQL 16
- **Source:** Telco Customer Churn CSV
- **Target Table:** `raw_customers`
- **Rows Ingested:** 7,043
- **Data Quality Observation:** The `totalcharges` column is stored as `TEXT` because some records contain blank strings instead of valid numeric values.

# Phase 1 — data staging and features

**Date:** October 26, 2026  
**Status:** Completed

## 1.1. What I Did
1. initializing the dbt project and setting the source db identifications 
2. set up two layer the first one is staging where i processed some columns renaming them to be in snake_case format , and changing the data type of churn from yes/no to 1/0 and type of totalcharges from string to numerical .
then the mart layer adding four features :
tenure_bucket: group tenure into ranges (for example 0-12, 13-24, 25-48, 49+ months).
monthly_to_total_ratio: monthly charges divided by total charges, protected against null or zero.
n_services: count how many of the add-on services are subscribed (phone, multiple lines, security, backup, device protection, tech support, streaming TV, streaming movies).
is_month_to_month: 1 if the contract is month-to-month, otherwise 0.
3. materializing the staging layer to view and marts to table
4. -adding tests : customerid should be unique and not_null  ,churn accepted_values (0 and 1) , tenure should be not_null in staging .
  -customeridshould be unique and not_null the mart.

### 1.2. What I learned
- `source()` points to raw tables, `ref()` points to other dbt models, and dbt builds the dependency graph from them.
- Staging models are views ; marts are tables .
- dbt tests are SQL queries that return failing rows; a test passes when it returns none.
- Print and check the DataFrame's column names before writing to the database.
### 1.3. Results
- `customer_features` has 7,043 rows.
- `total_charges` is now numeric.
- `customer_id` is unique and not null.
- `dbt test`: 5 tests passed, 0 failed.


# Phase 2 — ML + explainability

**Date:** October 29, 2026  
**Status:** Completed
## 2.1. What I Did
### preprocessing data: 
  1. Read the whole customer_features table into a DataFrame
  2. Separated the target variable (churn) from the input features.
  3. Removed customer_id from the model features while preserving it for customer-level predictions.
  4. train/test split (80/20)
  5. Imputed missing numerical values and encoded categorical variables using one-hot encoding.
### Model training and comparison:
  I trained and evaluated the following models:
  1. LogisticRegresson as the baseline modelas the baseline model 
  2. xgboost with unweighted churn class learning
  3. tuned and weighted xgboost using hyperparameters optimization
- Built a scikit-learn pipeline combining preprocessing and model training.
- compare between the tree models using metrics : 
    * roc_auc,
    * pr_auc,
    * precision,
    * recall,
    * f1 score
### Threshold optimization

- Generated OOF predictions for each model using cross-validation.
- Optimized an individual classification threshold for each model by minimizing estimated business cost (FN = 5, FP = 1).
- Saved optimal thresholds in ml/reports/threshold_results.json.

Used the optimized thresholds for test predictions.
### Model explainability
- explain each model's predictions using shap .
- Generated global feature importance reports and summary visualizations.
- Saved the explainability reports in ml/reports/.
### Experiment tracking
- Created ml/tracking.py module for MLflow experiment tracking.
- logged model parameters and metrics .
### Prediction storage
- Prepared the prediction results for storage in PostgreSQL.

## 2.2. What I learned
- Scikit-learn pipelines: Combining preprocessing and model training in a pipeline helps prevent data leakage during cross-validation because transformations are fitted within each training fold.
- Stratified splitting: Stratification preserves the approximate churn proportion in both training and test sets.
- Model comparison: A more complex model does not necessarily outperform a simpler baseline. Logistic Regression achieved a competitive ROC-AUC and the highest PR-AUC among the evaluated models.
SHAP: Global explanations show which features contribute most to predictions across a dataset, while local explanations help explain an individual prediction. 


## 2.3. Results

Three classification models were evaluated: Logistic Regression, unweighted XGBoost, and hyperparameter-tuned weighted XGBoost.

Cross-validation results showed that Logistic Regression and tuned weighted XGBoost achieved nearly identical ROC-AUC scores (0.8503 and 0.8502 respectively), while unweighted XGBoost obtained 0.8422.

On the test set, Logistic Regression achieved the highest PR-AUC (0.6764), whereas tuned weighted XGBoost achieved the highest F1-score (0.6301) at the default classification threshold of 0.5.

These results show that model selection should not rely on a single metric. The final choice should also consider the business cost of false negatives and false positives, using thresholds selected from training data rather than the test set.

## Phase 3: Airflow Orchestration

### What I Learned

- **Workflow orchestration with Apache Airflow:** Created a DAG to automate the customer churn pipeline, define task dependencies, configure retries, and monitor execution through the Airflow UI.
- **Docker networking:** Connected separate Docker Compose projects so Airflow could communicate with the PostgreSQL database using Docker service names.
- **Database ingestion:** Learned the difference between `if_exists="replace"` and `if_exists="append"` in pandas. Replacing a table can break dependent database views, while appending without clearing existing data creates duplicates. Using a transactional `DELETE` followed by an insert preserves the table and its dependencies.
- **Data transformation with dbt:** Integrated dbt models and data-quality tests into the Airflow workflow.
- **Failure handling:** Configured task dependencies so prediction generation only starts after ingestion, transformations, and data-quality tests succeed.
- **ML inference:** Integrated a saved XGBoost model into the pipeline to generate churn probabilities and classifications without retraining the model on every run.

### Pipeline Execution Order

1. `load_raw_data`: Loads customer data from CSV into PostgreSQL.
2. `dbt_run`: Builds the staging and customer feature models.
3. `dbt_test`: Executes data-quality tests.
4. `predict_churn`: Loads the trained model and writes predictions to PostgreSQL.

