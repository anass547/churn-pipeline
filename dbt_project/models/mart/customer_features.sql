with

source as (

    select * from {{ ref('stg_customers') }}

)

select
    customer_id,
    churn,

    gender,
    senior_citizen,
    partner,
    dependents,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies,
    contract,
    paperless_billing,
    payment_method,
    monthly_charges,
    total_charges,
    tenure,


    case
    when tenure between 0 and 12 then '0-12'
    when tenure between 13 and 24 then '13-24'
    when tenure between 25 and 48 then '25-48'
    when tenure between 49 and 60 then '49-60'
    else '61+'
    end as tenure_bucket,

    CASE
    WHEN total_charges IS NULL OR total_charges = 0  then 0
    else monthly_charges/total_charges end
    as monthly_to_total_ratio,

    (CASE WHEN phone_service = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN multiple_lines = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN online_security = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN online_backup = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN device_protection = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN tech_support = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN streaming_tv = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN streaming_movies = 'Yes' THEN 1 ELSE 0 END
    )
    as n_services,

    case contract
    when 'Month-to-month' then 1 
    else 0
    end as is_month_to_month

    from source
