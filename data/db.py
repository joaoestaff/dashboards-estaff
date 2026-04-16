import os
from pathlib import Path
import sqlalchemy
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def get_engine() -> sqlalchemy.Engine:
    host     = os.environ["DB_HOST"]
    port     = os.environ.get("DB_PORT", "3306")
    user     = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    database = os.environ["DB_NAME"]
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return sqlalchemy.create_engine(url, pool_pre_ping=True)
