from db.queries import MERGE_AGENTS
from utils.logger import setup_logger

logger = setup_logger(__name__)

def sync_agents(api, db_conn):
    """Sincroniza los agentes desde Freshdesk a la base de datos."""
    logger.info("Iniciando sincronización de Agentes...")
    
    agents = api.get_all_pages("agents")
    if not agents:
        logger.warning("No se encontraron agentes.")
        return

    logger.info(f"Procesando {len(agents)} agentes...")
    
    cursor = db_conn.cursor()
    count = 0
    for agent in agents:
        try:
            id_agente = agent.get("id")
            contacto = agent.get("contact", {})
            nombre = contacto.get("name", "Sin Nombre")
            correo = contacto.get("email", None)
            
            cursor.execute(MERGE_AGENTS, id_agente, nombre, correo)
            count += 1
        except Exception as e:
            logger.error(f"Error al insertar agente {id_agente}: {e}")
            
    db_conn.commit()
    logger.info(f"Sincronización de Agentes completada. {count} registros procesados.")
