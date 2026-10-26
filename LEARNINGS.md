# Phase 0 — Environment Setup & Raw Data Ingestion

**Date:** October 25, 2026  
**Status:** Completed

## 1. What I Did

- Set up the project repository structure, Python virtual environment, and dependencies.
- Configured and launched PostgreSQL 16 using Docker Compose, with a named volume for persistent data storage and port `5432` exposed.
- Loaded the Telco Customer Churn dataset into PostgreSQL using the following pipeline:

  `CSV → pandas DataFrame → SQLAlchemy Engine → PostgreSQL`

- Stored the raw dataset in the `raw_customers` table.

## 2. What I Learned

- **SQLAlchemy Engine:** Manages database connections using a connection URL and allows pandas to interact with PostgreSQL.
- **pandas `to_sql()`:** Creates a database table and inserts DataFrame records using a SQLAlchemy engine.
- **Docker Named Volumes:** Persist database data even when the container is stopped or recreated, provided the volume is retained.
- **Raw Data Ingestion:** Loading source data into a raw table preserves the original structure for downstream transformation and cleaning.

## 3. Results

- **Database:** PostgreSQL 16
- **Source:** Telco Customer Churn CSV
- **Target Table:** `raw_customers`
- **Rows Ingested:** 7,043
- **Data Quality Observation:** The `totalcharges` column is stored as `TEXT` because some records contain blank strings instead of valid numeric values.

# Phase 1 — data staging and features

**Date:** October 26, 2026  
**Status:** Completed

## 1. What I Did
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
## 2. What I Learned
how to connect the a postgres db to dbt and process the data , creating bdt models,sources,  tests
## 3. Results
the mart contains 7,043 customer rows.
data types changed for totalcharges column.
customerid uniqueness and non-null .
### What I learned
- `source()` points to raw tables, `ref()` points to other dbt models, and dbt builds the dependency graph from them.
- Staging models are views ; marts are tables .
- dbt tests are SQL queries that return failing rows; a test passes when it returns none.
- Print and check the DataFrame's column names before writing to the database.
### Results
- `customer_features` has 7,043 rows.
- `total_charges` is now numeric.
- `customer_id` is unique and not null.
- `dbt test`: 5 tests passed, 0 failed.
