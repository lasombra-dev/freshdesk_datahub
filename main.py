from db.connection import DBConnection
from freshdesk.api import FreshdeskAPI
from freshdesk.contacts import sync_contacts
from freshdesk.companies import sync_companies
from freshdesk.agents import sync_agents
from freshdesk.tickets import sync_tickets
from utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("Iniciando proceso de sincronización Freshdesk Datahub...")
    
    # Inicializar conexión a BD
    db = DBConnection()
    
    try:
        with db as conn:
            # Inicializar API
            api = FreshdeskAPI()
            
            # Ejecutar sincronizaciones
            sync_contacts(api, conn)
            sync_companies(api, conn)
            sync_agents(api, conn)
            sync_tickets(api, conn)
            
            logger.info("¡Proceso de sincronización completado exitosamente!")
            
    except Exception as e:
        logger.critical(f"El proceso falló: {e}")

if __name__ == "__main__":
    main()
