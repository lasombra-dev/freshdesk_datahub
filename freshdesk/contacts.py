from db.queries import MERGE_CONTACTS
from utils.logger import setup_logger

logger = setup_logger(__name__)

def sync_contacts(api, db_conn):
    """Sincroniza los contactos desde Freshdesk a la base de datos."""
    logger.info("Iniciando sincronización de Contactos...")
    
    contacts = api.get_all_pages("contacts")
    if not contacts:
        logger.warning("No se encontraron contactos.")
        return

    logger.info(f"Procesando {len(contacts)} contactos...")
    
    cursor = db_conn.cursor()
    count = 0
    for contact in contacts:
        try:
            id_contacto = contact.get("id")
            nombre = contact.get("name", "Sin Nombre")
            correo = contact.get("email", None)
            
            cursor.execute(MERGE_CONTACTS, id_contacto, nombre, correo)
            count += 1
        except Exception as e:
            logger.error(f"Error al insertar contacto {id_contacto}: {e}")
            
    db_conn.commit()
    logger.info(f"Sincronización de Contactos completada. {count} registros procesados.")
