from sqlalchemy import create_engine
import pandas as pd
from db import get_engine

engine = get_engine()

df=pd.read_csv("data/raw/telco_churn.csv")
df.columns = df.columns.str.lower()
df.to_sql("raw_customers", engine, if_exists='replace', index=False)
