import mlflow
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    average_precision_score,
    recall_score,
    f1_score,
    RocCurveDisplay,
    PrecisionRecallDisplay,
)
import json 
with open("ml/reports/threshold_results.json", "r") as f:
    threshold_results = json.load(f)

threshold = threshold_results["xgboost_tuned_weighted"]["threshold"]

def track_experiment(model_name,model,X_test,y_test,params=None,threshold=threshold,extra_artifacts=None):
    params = params or {}
    extra_artifacts = extra_artifacts or []
    mlflow.set_experiment("churn_pipeline")
    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model_name",model_name)
        mlflow.log_param("threshold",threshold)
        mlflow.log_params(params)
        probabilities = model.predict_proba(X_test)[:, 1]
        predictions = (probabilities >= threshold).astype(int)
        metrics = {
            "roc_auc": roc_auc_score(y_test, probabilities),
            "pr_auc": average_precision_score(y_test, probabilities),
            "precision": precision_score(
                y_test, predictions, zero_division=0
            ),
            "recall": recall_score(
                y_test, predictions, zero_division=0
            ),
            "f1": f1_score(y_test, predictions, zero_division=0),
        }
        mlflow.log_metrics(metrics)
        plot_dir = os.path.join("ml","reports", "mlflow_plots")
        os.makedirs(plot_dir, exist_ok=True)
        roc_path=os.path.join(
            plot_dir, f"{model_name}_roc.png"
        )
        RocCurveDisplay.from_predictions(y_test,probabilities)
        plt.title(f"{model_name} — ROC curve")
        plt.tight_layout()
        plt.savefig(roc_path, dpi=200, bbox_inches="tight")
        plt.close()
        mlflow.log_artifact(roc_path, artifact_path="plots")


        pr_path = os.path.join(
            plot_dir, f"{model_name}_pr.png"
        )
        PrecisionRecallDisplay.from_predictions(y_test, probabilities)
        plt.title(f"{model_name} — Precision-recall curve")
        plt.tight_layout()
        plt.savefig(pr_path, dpi=200, bbox_inches="tight")
        plt.close()
        mlflow.log_artifact(pr_path, artifact_path="plots")

        for artifact_path in extra_artifacts:
            if os.path.isfile(artifact_path):
                mlflow.log_artifact(artifact_path)

      
