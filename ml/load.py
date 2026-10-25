from sqlalchemy import create_engine
import pandas as pd
engine = create_engine('postgresql+psycopg2://churn:churn@localhost:5432/churn')
df=pd.read_csv("data/raw/telco_churn.csv")
df.columns=[df.columns.str.lower()]
df.to_sql("raw_customers", engine, if_exists='replace', index=False)
print(len(df))