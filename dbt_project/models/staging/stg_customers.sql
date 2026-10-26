with source as (
    select * from {{ source('raw', 'raw_customers') }}
),
renamed as (
    select
        customerid as customer_id,
        gender ,
        seniorcitizen as senior_citizen,
        partner,
        dependents,
        tenure,
        phoneservice as phone_service,
        multiplelines as multiple_lines,
        internetservice as internet_service,
        onlinesecurity as online_security,
        onlinebackup as online_backup,
        deviceprotection as device_protection,
        techsupport as tech_support,
        streamingtv as streaming_tv,
        streamingmovies as streaming_movies,
        contract,
        paperlessbilling as paperless_billing,
        paymentmethod as payment_method,
        monthlycharges as monthly_charges,
        nullif(trim(totalcharges), '')::numeric(10, 2) as total_charges,
        CASE
        WHEN churn = 'Yes' THEN 1
        WHEN churn = 'No' THEN 0
        ELSE NULL
        END 
        AS churn
    from source
)

select * from renamed