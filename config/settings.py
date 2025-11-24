import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Freshdesk
FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN", "grupoempack.freshdesk.com")
FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY", "NcWk2UUwZSPC6WCWn3VZ")
FRESHDESK_START_DATE = os.getenv("FRESHDESK_START_DATE", "2025-10-14")

# Configuración de Base de Datos
DB_SERVER = os.getenv("DB_SERVER", "ge-db-dev02.c904tqksriup.us-east-1.rds.amazonaws.com")
DB_DATABASE = os.getenv("DB_DATABASE", "freshdesk_datahub")
DB_USERNAME = os.getenv("DB_USERNAME", "sysdev")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Lg9oAnCywBmKNh")
DB_DRIVER = os.getenv("DB_DRIVER", "{SQL Server}")