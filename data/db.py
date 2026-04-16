import os
from pathlib import Path
import sqlalchemy
from dotenv import load_dotenv

# Carrega .env local se existir (funciona na sua máquina)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

def get_engine() -> sqlalchemy.Engine:
    # Tenta st.secrets primeiro (Streamlit Cloud), depois .env (local)
    try:
        import streamlit as st
        host     = st.secrets["DB_HOST"]
        port     = st.secrets.get("DB_PORT", "3306")
        user     = st.secrets["DB_USER"]
        password = st.secrets["DB_PASSWORD"]
        database = st.secrets["DB_NAME"]
    except Exception:
        host     = os.environ["DB_HOST"]
        port     = os.environ.get("DB_PORT", "3306")
        user     = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        database = os.environ["DB_NAME"]

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return sqlalchemy.create_engine(url, pool_pre_ping=True)
