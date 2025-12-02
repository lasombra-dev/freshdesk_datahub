import os
from dotenv import load_dotenv

# Cargamos las variables del .env
load_dotenv()

# Datos para conectarse a Freshdesk
FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN")
FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY")
FRESHDESK_START_DATE = os.getenv("FRESHDESK_START_DATE", "2025-10-14")

# Datos pa la base de datos
DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER", "{SQL Server}")