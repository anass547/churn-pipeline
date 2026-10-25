## Phase 0: Setup (2026-10-25)

**What I did**
- Set up the repo structure, a virtual environment, and requirements.
- Started Postgres 16 in Docker (Compose, named volume, port 5432).
- Loaded the Telco Churn CSV into the table `raw_customers`:
  CSV → pandas DataFrame → SQLAlchemy engine → Postgres.
**What I learned**
- The SQLAlchemy engine holds the connection URL and manages connections; `df.to_sql` uses it to create and fill the table.
- A named Docker volume keeps data after the container is stopped.
**Result**
- `raw_customers` has 7,043 rows.
- `totalcharges` is `text` because of blank strings. To be cleaned with dbt in Phase 1.
