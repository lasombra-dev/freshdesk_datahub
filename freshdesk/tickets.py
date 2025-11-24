from datetime import datetime, timezone
from db.queries import MERGE_TICKETS
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

def sync_tickets(api, db_conn):
    """Trae los tickets de Freshdesk y los guarda en la BD."""
    logger.info("Empezando a traer los tickets...")
    
    start_date = settings.FRESHDESK_START_DATE
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Armando la query para buscar...
    query = f"created_at:>'{start_date}' AND created_at:<'{current_date}'"
    
    tickets = api.search_tickets(query)
    if not tickets:
        logger.warning("No se encontraron tickets.")
        return

    logger.info(f"Procesando {len(tickets)} tickets, esto puede tardar...")
    
    cursor = db_conn.cursor()
    count = 0
    for ticket in tickets:
        try:
            id_ticket = ticket.get("id")
            asunto = ticket.get("subject", "Sin Asunto")
            estado = ticket.get("status")
            prioridad = ticket.get("priority")
            tipo = ticket.get("type")
            
            custom_fields = ticket.get("custom_fields", {})
            subtipo = custom_fields.get("cf_subtipo", "Sin Subtipo")
            cf_empresa = custom_fields.get("cf_empresa", "Sin Empresa")
            
            agente = ticket.get("responder_id", None)
            tiempo_creacion = ticket.get("created_at")
            tiempo_resolucion = ticket.get("due_by", None)
            requester_id = ticket.get("requester_id", None)
            company_id = ticket.get("company_id", None)
            etiquetas = ",".join(ticket.get("tags", []))
            
            cursor.execute(MERGE_TICKETS, id_ticket, asunto, estado, prioridad, tipo, 
                           subtipo, cf_empresa, agente, tiempo_creacion, 
                           tiempo_resolucion, requester_id, company_id, etiquetas)
            count += 1
        except Exception as e:
            logger.error(f"Error al insertar ticket {id_ticket}: {e}")
            
    db_conn.commit()
    logger.info(f"Sincronización de Tickets completada. {count} registros procesados.")
