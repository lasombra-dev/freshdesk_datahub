import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# ============================================
# CONFIGURACIÓN DE FRESHDESK API
# ============================================

FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN", "grupoempack.freshdesk.com")
API_KEY = os.getenv("FRESHDESK_API_KEY")

# Headers para las peticiones HTTP
HEADERS = {
    "Content-Type": "application/json"
}

# Parámetros de paginación
PER_PAGE = 100  # Máximo permitido por Freshdesk

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================

DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER", "{SQL Server}")

# ============================================
# CONFIGURACIÓN DE SINCRONIZACIÓN
# ============================================

# Fecha de inicio para sincronización de tickets
START_DATE = os.getenv("START_DATE", "2025-10-14")

# Mapeo de estados de Freshdesk (opcional, para referencia)
TICKET_STATUS = {
    2: "Open",
    3: "Pending",
    4: "Resolved",
    5: "Closed"
}

# Mapeo de prioridades de Freshdesk (opcional, para referencia)
TICKET_PRIORITY = {
    1: "Low",
    2: "Medium",
    3: "High",
    4: "Urgent"
}

# ============================================
# ENDPOINTS DE FRESHDESK API
# ============================================

BASE_URL = f"https://{FRESHDESK_DOMAIN}/api/v2"

ENDPOINTS = {
    "contacts": f"{BASE_URL}/contacts",
    "companies": f"{BASE_URL}/companies",
    "agents": f"{BASE_URL}/agents",
    "tickets": f"{BASE_URL}/tickets",
    "tickets_search": f"{BASE_URL}/search/tickets",
    "conversations": f"{BASE_URL}/tickets/{{ticket_id}}/conversations",
    "sla_policies": f"{BASE_URL}/sla_policies"
}

# ============================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================

def validate_config():
    """Valida que todas las variables de entorno requeridas estén configuradas."""
    required_vars = {
        "FRESHDESK_API_KEY": API_KEY,
        "DB_SERVER": DB_SERVER,
        "DB_DATABASE": DB_DATABASE,
        "DB_USERNAME": DB_USERNAME,
        "DB_PASSWORD": DB_PASSWORD
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(
            f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}\n"
            f"Por favor, configúralas en el archivo .env"
        )
    
    return True