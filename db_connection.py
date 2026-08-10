import os
import struct
import pyodbc
import streamlit as st

from dotenv import load_dotenv
from sqlalchemy import create_engine
from azure.identity import ClientSecretCredential

load_dotenv()


# =========================================================
# Configuration
# =========================================================

def get_secret(name):
    """
    Get configuration from Streamlit Cloud Secrets.
    Fall back to .env when running locally.
    """
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name)


FABRIC_SERVER = get_secret("FABRIC_SERVER")
DATABASE = "insurance_lakehouse"

AZURE_CLIENT_ID = get_secret("AZURE_CLIENT_ID")
AZURE_TENANT_ID = get_secret("AZURE_TENANT_ID")
AZURE_CLIENT_SECRET = get_secret("AZURE_CLIENT_SECRET")


# =========================================================
# Microsoft Entra Service Principal
# =========================================================

credential = ClientSecretCredential(
    tenant_id=AZURE_TENANT_ID,
    client_id=AZURE_CLIENT_ID,
    client_secret=AZURE_CLIENT_SECRET
)


# =========================================================
# Fabric SQL Connection
# =========================================================

def get_connection():

    token = credential.get_token(
        "https://database.windows.net/.default"
    )

    token_bytes = token.token.encode("utf-16-le")

    token_struct = struct.pack(
        f"<I{len(token_bytes)}s",
        len(token_bytes),
        token_bytes
    )

    # Try Driver 18 first (works locally), fall back to 17 (Streamlit Cloud)
    drivers_to_try = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
    ]

    last_error = None

    for driver in drivers_to_try:
        try:
            connection_string = (
                f"Driver={{{driver}}};"
                f"Server={FABRIC_SERVER};"
                f"Database={DATABASE};"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
            )

            return pyodbc.connect(
                connection_string,
                attrs_before={1256: token_struct}
            )

        except pyodbc.Error as e:
            last_error = e
            continue

    raise last_error


# =========================================================
# SQLAlchemy Engine
# =========================================================

engine = create_engine(
    "mssql+pyodbc://",
    creator=get_connection
)