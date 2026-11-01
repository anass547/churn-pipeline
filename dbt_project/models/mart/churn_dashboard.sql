
SELECT
    cf.customer_id,
    p.churn_probability,
    p.predicted_churn,
    p.model_version,
    p.scored_at,
    cf.contract,
    cf.tenure,
    cf.tenure_bucket,
    cf.monthly_charges,
    cf.internet_service,
    cf.payment_method
FROM {{ ref('customer_features') }} AS cf
INNER JOIN {{ source('analytics', 'predictions') }} AS p
    ON cf.customer_id = p.customer_id
