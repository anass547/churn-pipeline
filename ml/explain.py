import joblib
import pandas as pd
import shap
import numpy as np
import matplotlib.pyplot as plt
# 1. LOAD MODEL AND TEST DATA
model=joblib.load("ml/joblib/best_xgboost_weighted.joblib")
test_data=joblib.load("ml/joblib/test_data.joblib")
X_test=test_data["X_test"]
y_test=test_data["y_test"]



# ============================================================
# 2. TRANSFORM TEST FEATURES
# ============================================================

preprocessor = model.named_steps["preprocessor"]
classifier = model.named_steps["classifier"]

X_test_transformed = preprocessor.transform(X_test)
features_names=preprocessor.get_feature_names_out()

X_test_transformed = pd.DataFrame(
    X_test_transformed,columns=features_names,index=X_test.index
)

# ============================================================
# 3. COMPUTE SHAP VALUES
# ============================================================

explainer = shap.TreeExplainer(classifier)
shap_values=explainer.shap_values(X_test_transformed)
shap_df=pd.DataFrame(
    shap_values,columns=features_names,index=X_test.index
)
shap_df.to_csv("ml/reports/shap_values_test.csv")

# ============================================================
# 5. GLOBAL FEATURE IMPORTANCE
# ============================================================
features_importance=pd.DataFrame(
    {
        "feature":features_names,
        "mean_abs_shap":np.abs(shap_values).mean(axis=0),
        
    }
).sort_values(
    "mean_abs_shap",
    ascending=False
)

features_importance.to_csv("ml/reports/features_importance.csv")
# ============================================================
# 6. SHAP SUMMARY PLOT
# ============================================================

shap.summary_plot(
    shap_values,
    X_test_transformed,
    show=False
)

plt.tight_layout()
plt.savefig("ml/reports/shap_summary.png", dpi=300, bbox_inches="tight")
plt.close()
# ============================================================
# 7. SHAP GLOBAL IMPORTANCE PLOT
# ============================================================
shap.summary_plot(
    shap_values,
    X_test_transformed,
    show=False,
    plot_type="bar"
)

plt.tight_layout()
plt.savefig("ml/reports/shap_importance.png", dpi=300, bbox_inches="tight")
plt.close()

# ============================================================
# LOCAL EXPLANATION: HIGHEST-RISK TEST CUSTOMER
# ============================================================

test_probabilities = model.predict_proba(X_test)[:, 1]

high_risk_position = int(np.argmax(test_probabilities))



# Build an Explanation object for the selected customer
shap_explanation = shap.Explanation(
    values=shap_values[high_risk_position],
    base_values=explainer.expected_value,
    data=X_test_transformed.iloc[high_risk_position].values,
    feature_names=list(features_names),
)

shap.plots.waterfall(
    shap_explanation,
    max_display=15,
    show=False
)

plt.tight_layout()
plt.savefig(
    "ml/reports/shap_waterfall_high_risk.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()