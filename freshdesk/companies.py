from db.queries import MERGE_COMPANIES
from utils.logger import setup_logger

logger = setup_logger(__name__)

def sync_companies(api, db_conn):
    """Trae las empresas de Freshdesk y las guarda en la BD."""
    logger.info("Empezando a traer las empresas...")
    
    companies = api.get_all_pages("companies")
    if not companies:
        logger.warning("No se encontraron empresas.")
        return

    logger.info(f"Procesando {len(companies)} empresas, paciencia...")
    
    cursor = db_conn.cursor()
    count = 0
    for company in companies:
        try:
            id_empresa = company.get("id")
            nombre_empresa = company.get("name", "Sin Nombre")
            
            cursor.execute(MERGE_COMPANIES, id_empresa, nombre_empresa)
            count += 1
        except Exception as e:
            logger.error(f"Error al insertar empresa {id_empresa}: {e}")
            
    db_conn.commit()
    logger.info(f"Sincronización de Empresas completada. {count} registros procesados.")
