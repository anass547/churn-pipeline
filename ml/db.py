import os
from sqlalchemy import create_engine


def get_engine():
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://churn:churn@localhost:5432/churn"
    )
    return create_engine(database_url)