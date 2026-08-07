import os
import struct
import pyodbc

from dotenv import load_dotenv
from sqlalchemy import create_engine
from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions

load_dotenv()

FABRIC_SERVER = os.getenv("FABRIC_SERVER")
DATABASE = "insurance_lakehouse"

# Microsoft Entra login
cache_options = TokenCachePersistenceOptions(
    name="insurance-ai-assistant",
    allow_unencrypted_storage=True
)

credential = InteractiveBrowserCredential(
    cache_persistence_options=cache_options
)

def get_connection():
    # Get Microsoft Entra access token for Azure SQL/Fabric SQL
    token = credential.get_token(
        "https://database.windows.net/.default"
    )

    # Convert token into format required by ODBC Driver 18
    token_bytes = token.token.encode("utf-16-le")
    token_struct = struct.pack(
        f"<I{len(token_bytes)}s",
        len(token_bytes),
        token_bytes
    )

    connection_string = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server={FABRIC_SERVER};"
        f"Database={DATABASE};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )

    return pyodbc.connect(
        connection_string,
        attrs_before={1256: token_struct}
    )


# SQLAlchemy engine
engine = create_engine(
    "mssql+pyodbc://",
    creator=get_connection
)