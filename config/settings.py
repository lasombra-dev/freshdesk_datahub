import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Freshdesk
FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN")
FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY")
FRESHDESK_START_DATE = os.getenv("FRESHDESK_START_DATE")

# Configuración de Base de Datos
DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER", "{SQL Server}")