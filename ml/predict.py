import joblib
import pandas as pd
from sqlalchemy import create_engine
import json

with open("ml/reports/threshold_results.json", "r") as f:
    threshold_results = json.load(f)

threshold = threshold_results["xgboost_tuned_weighted"]["threshold"]

engine=create_engine('postgresql+psycopg2://churn:churn@localhost:5432/churn')

model=joblib.load("ml/joblib/best_xgboost_weighted.joblib")

df=pd.read_sql("select * from analytics.customer_features",engine)

customer_ids=df["customer_id"]

X=df.drop(columns=["customer_id","churn"])

churn_probabilities=model.predict_proba(X)[:,1]



predicted_churn = (
    churn_probabilities >= threshold
).astype(int)

#  BUILD PREDICTIONS TABLE

predictions=pd.DataFrame(
    {
        "customer_id":customer_ids,
        'churn_probability':churn_probabilities,
        "predicted_churn":predicted_churn,
         "model_version":"xgboost_weighted_v1",
         "scored_at":pd.Timestamp.now(tz="UTC")


    }
)
predictions.to_sql("predictions",engine,schema="analytics",if_exists="replace",index=False)
engine.dispose()