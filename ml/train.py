import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split, cross_val_score , StratifiedKFold,RandomizedSearchCV, cross_val_predict
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression 
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score
)
import json
from xgboost import XGBClassifier
import numpy as np
from sklearn.base import clone
from scipy.stats import loguniform
import joblib
from tracking import track_experiment
import matplotlib.pyplot as plt




engine = create_engine(
"postgresql+psycopg2://churn:churn@localhost:5432/churn"
)
df = pd.read_sql("SELECT * FROM analytics.customer_features", engine)


customer_ids = df["customer_id"].copy()

y = df["churn"].astype(int)
X = df.drop(columns=["customer_id", "churn"])



categorical_features = X.select_dtypes(
include=["object", "category", "string"]
).columns.tolist()

numerical_features = X.select_dtypes(
include=["number", "bool"]
).columns.tolist()



numerical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="mean")),
    ("scaler", StandardScaler())
]
)
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
]
)
processor = ColumnTransformer([
    ("numerical", numerical_pipeline, numerical_features),
    ("categorical", categorical_pipeline, categorical_features)
]
)

model_pipeline = Pipeline([
    ("preprocessor", processor),
    ("classifier", LogisticRegression(max_iter=1000,class_weight="balanced",random_state=42))
]
)



X_train, X_test, y_train, y_test = train_test_split(
X,
y,
test_size=0.2,
random_state=42,
stratify=y
)
joblib.dump(
    {"X_test": X_test, "y_test": y_test},
    "ml/joblib/test_data.joblib"
)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

cross_val_scores = cross_val_score(model_pipeline , X_train,y_train, cv=cv, scoring="roc_auc")

model_pipeline.fit(X_train, y_train)
y_pred = model_pipeline.predict(X_test)
y_proba=model_pipeline.predict_proba(X_test)[:, 1]

metrics_LR = {
    "roc_auc": roc_auc_score(y_test, y_proba),
    "pr_auc": average_precision_score(y_test, y_proba),
    "precision": precision_score(y_test, y_pred, zero_division=0),
    "recall": recall_score(y_test, y_pred, zero_division=0),
    "f1": f1_score(y_test, y_pred, zero_division=0),
}





xgb_pipeline_unweighted=Pipeline([
    ("preprocessor",clone(processor)),
    ("classifier",XGBClassifier(objective="binary:logistic",
        eval_metric="auc",
        tree_method="hist",
        max_depth=6,
        learning_rate=0.1,
        n_estimators=100,
        random_state=42))

])

cv_scores_unweighted=cross_val_score(xgb_pipeline_unweighted,X_train,y_train, cv=cv, scoring="roc_auc")
xgb_pipeline_unweighted.fit(X_train,y_train)
y_xgb_pred_unweighted = xgb_pipeline_unweighted.predict(X_test)
y_xgb_proba_unweighted = xgb_pipeline_unweighted.predict_proba(X_test)[:, 1]




metrics_XGB = {
    "roc_auc": roc_auc_score(y_test, y_xgb_proba_unweighted),
    "pr_auc": average_precision_score(y_test, y_xgb_proba_unweighted),
    "precision": precision_score(y_test, y_xgb_pred_unweighted, zero_division=0),
    "recall": recall_score(y_test, y_xgb_pred_unweighted, zero_division=0),
    "f1": f1_score(y_test, y_xgb_pred_unweighted, zero_division=0),
}








scale_pos_weight=((y_train == 0).sum() / (y_train == 1).sum())
xgb_pipeline_weighted=Pipeline([
    ("preprocessor",clone(processor)),
    ("classifier",XGBClassifier(objective="binary:logistic",
        eval_metric="auc",
        tree_method="hist",
        random_state=42,
        scale_pos_weight=scale_pos_weight,
        n_jobs=1))

])
params = {
    "classifier__learning_rate": loguniform(0.01, 0.3),
    "classifier__max_depth": [3, 4, 5, 6, 8, 10],
    "classifier__min_child_weight": [1, 3, 5, 7],
    "classifier__gamma": [0.0, 0.1, 0.2, 0.3, 0.4],
    "classifier__colsample_bytree": [0.3, 0.4, 0.5, 0.7, 0.9, 1.0],
    "classifier__subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
    "classifier__n_estimators": [100, 200, 300, 400, 500]
}

rs_model=RandomizedSearchCV(estimator=xgb_pipeline_weighted,param_distributions=params,n_iter=30,scoring='roc_auc',n_jobs=-1,cv=cv,verbose=3,random_state=42,refit=True)

rs_model.fit(X_train,y_train)
print(f"Best CV ROC-AUC: {rs_model.best_score_:.4f}")
print("Best parameters:")
print(rs_model.best_params_)
# Evaluate the best model on the test set
best_model = rs_model.best_estimator_

cv_scores_weighted = cross_val_score(
    clone(best_model),
    X_train,
    y_train,
    cv=cv,
    scoring="roc_auc"
)
y_xgb_pred_weighted = best_model.predict(X_test)
y_xgb_proba_weighted = best_model.predict_proba(X_test)[:, 1]

joblib.dump(best_model, "ml/joblib/best_xgboost_weighted.joblib")


metrics_XGB_weighted = {
    "roc_auc": roc_auc_score(y_test, y_xgb_proba_weighted),
    "pr_auc": average_precision_score(y_test, y_xgb_proba_weighted),
    "precision": precision_score(y_test, y_xgb_pred_weighted, zero_division=0),
    "recall": recall_score(y_test, y_xgb_pred_weighted, zero_division=0),
    "f1": f1_score(y_test, y_xgb_pred_weighted, zero_division=0),
}






# ============================================================
# SAVE TRAINING REPORT
# ============================================================

report = {
    "logistic_regression": {
        "cross_validation": {
            "roc_auc_mean": float(cross_val_scores.mean()),
            "roc_auc_std": float(cross_val_scores.std()),
        },
        "test_metrics": metrics_LR,
    },

    "xgboost_unweighted": {
        "cross_validation": {
            "roc_auc_mean": float(cv_scores_unweighted.mean()),
            "roc_auc_std": float(cv_scores_unweighted.std()),
        },
        "test_metrics": metrics_XGB,
    },

    "xgboost_tuned_weighted": {
        "cross_validation": {
            "roc_auc_mean": float(cv_scores_weighted.mean()),
            "roc_auc_std": float(cv_scores_weighted.std()),
            "roc_auc_best": float(rs_model.best_score_),
            
        },
        "best_params": rs_model.best_params_,
        "test_metrics": metrics_XGB_weighted,
    },
}

with open("ml/reports/training_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=4, ensure_ascii=False)

print("\nTraining report saved to ml/reports/training_report.json")


engine.dispose()



# 1. Logistic Regression baseline — after fitting lr_model
track_experiment(
    model_name="logistic_regression_baseline",
    model=model_pipeline,
    X_test=X_test,
    y_test=y_test,
    params=model_pipeline.named_steps["classifier"].get_params(),
)

# 2. Untuned XGBoost — after fitting xgb_model
track_experiment(
    model_name="xgboost_baseline",
    model=xgb_pipeline_unweighted,
    X_test=X_test,
    y_test=y_test,
    params=xgb_pipeline_unweighted.named_steps["classifier"].get_params(),
)

# 3. Tuned XGBoost — after RandomizedSearchCV
track_experiment(
    model_name="xgboost_tuned",
    model=best_model,
    X_test=X_test,
    y_test=y_test,
    params=best_model.named_steps["classifier"].get_params(),
    extra_artifacts=[
        "reports/shap_summary.png",
        "reports/shap_importance.png",
        "reports/shap_waterfall_high_risk.png",
    ],
)


# Business cost assumptions
fn_cost = 5
fp_cost = 1
thresholds = np.arange(0.10, 0.91, 0.01)

models = {
    "logistic_regression": model_pipeline,
    "xgboost_unweighted": xgb_pipeline_unweighted,
    "xgboost_tuned_weighted": best_model
}

threshold_results = {}

for model_name, model in models.items():

    oof_proba = cross_val_predict(
        clone(model),
        X_train,
        y_train,
        cv=cv,
        method="predict_proba",
        n_jobs=-1
    )[:, 1]

    costs = []

    for threshold in thresholds:
        predictions = (oof_proba >= threshold).astype(int)

        fn = ((y_train == 1) & (predictions == 0)).sum()
        fp = ((y_train == 0) & (predictions == 1)).sum()

        total_cost = fn_cost * fn + fp_cost * fp
        costs.append(total_cost)

    best_index = np.argmin(costs)
    best_threshold = float(thresholds[best_index])

    threshold_results[model_name] = {
        "threshold": best_threshold,
        "estimated_cost": float(costs[best_index])
    }

    

# Save threshold results
with open(
    "ml/reports/threshold_results.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(threshold_results, f, indent=4)