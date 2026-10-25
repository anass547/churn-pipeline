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

