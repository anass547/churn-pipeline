
import pandas as pd
from sqlalchemy import text
from db import get_engine

engine = get_engine()

try:
    df = pd.read_csv("data/raw/telco_churn.csv")
    df.columns = df.columns.str.lower()

    with engine.begin() as conn:
        # Remove existing rows without dropping the table
        conn.execute(text("DELETE FROM public.raw_customers"))

        # Insert the latest dataset
        df.to_sql(
            "raw_customers",
            conn,
            schema="public",
            if_exists="append",
            index=False
        )

    print(f"Successfully loaded {len(df)} rows into raw_customers.")

finally:
    engine.dispose()
