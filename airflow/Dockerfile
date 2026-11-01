FROM apache/airflow:3.3.2

COPY airflow/requirements.txt /requirements.txt

RUN pip install --no-cache-dir \
    "apache-airflow==3.3.2" \
    -r /requirements.txt