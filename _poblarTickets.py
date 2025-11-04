import requests
import pyodbc
from datetime import datetime

# Configuración de Freshdesk
FRESHDESK_DOMAIN = "grupoempack.freshdesk.com"  # Cambia por tu dominio
API_KEY = "NcWk2UUwZSPC6WCWn3VZ"  # Cambia por tu API Key
HEADERS = {"Content-Type": "application/json"}
START_DATE = "2025-10-14"  # Fecha inicial para la población (14/OCT/2025)

# Conexión a la base de datos SQL
conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=ge-db-dev02.c904tqksriup.us-east-1.rds.amazonaws.com;"  # Cambia esto por tu servidor
    "DATABASE=freshdesk_datahub;"  # Cambia esto por tu base de datos
    "UID=sysdev;"
    "PWD=Lg9oAnCywBmKNh;"
)
cursor = conn.cursor()

# Función para obtener tickets desde Freshdesk
def obtener_tickets(fecha_inicio):
    tickets = []
    page = 1
    per_page = 100  # Máximo permitido por Freshdesk

    while True:
        # Filtrar tickets por fecha de creación
        query = f"created_at:>'{fecha_inicio}'"
        response = requests.get(
            f"https://{FRESHDESK_DOMAIN}/api/v2/search/tickets?query=\"{query}\"&page={page}",
            auth=(API_KEY, "X"),
            headers=HEADERS
        )

        if response.status_code != 200:
            print(f"Error al consultar la API: {response.status_code}")
            break

        data = response.json().get("results", [])
        if not data:
            break  # No hay más tickets

        tickets.extend(data)
        page += 1

    return tickets

# Función para poblar la tabla Tickets en SQL Server
def poblar_tickets(tickets):
    for ticket in tickets:
        id_ticket = ticket.get("id")
        asunto = ticket.get("subject", "Sin Asunto")
        estado = ticket.get("status")
        prioridad = ticket.get("priority")
        tipo = ticket.get("type")
        
        # Extraer subtipo de custom_fields
        custom_fields = ticket.get("custom_fields", {})
        subtipo = custom_fields.get("cf_subtipo", "Sin Subtipo")  # Valor por defecto si no está presente

        agente = ticket.get("responder_id", None)  # ID del agente asignado
        tiempo_creacion = ticket.get("created_at")
        tiempo_resolucion = ticket.get("due_by", None)
        requester_id = ticket.get("requester_id", None)
        company_id = ticket.get("company_id", None)
        etiquetas = ",".join(ticket.get("tags", []))  # Combina las etiquetas en un string

        try:
            cursor.execute("""
                MERGE Tickets AS target
                USING (SELECT ? AS ID, ? AS Asunto, ? AS Estado, ? AS Prioridad, ? AS Tipo, 
                              ? AS Subtipo, ? AS Agente, ? AS TiempoCreacion, ? AS TiempoResolucion, 
                              ? AS RequesterID, ? AS CompanyID, ? AS Etiquetas) AS source
                ON target.ID = source.ID
                WHEN MATCHED THEN
                    UPDATE SET Asunto = source.Asunto,
                               Estado = source.Estado,
                               Prioridad = source.Prioridad,
                               Tipo = source.Tipo,
                               Subtipo = source.Subtipo,
                               Agente = source.Agente,
                               TiempoCreacion = source.TiempoCreacion,
                               TiempoResolucion = source.TiempoResolucion,
                               RequesterID = source.RequesterID,
                               CompanyID = source.CompanyID,
                               Etiquetas = source.Etiquetas
                WHEN NOT MATCHED THEN
                    INSERT (ID, Asunto, Estado, Prioridad, Tipo, Subtipo, Agente, 
                            TiempoCreacion, TiempoResolucion, RequesterID, CompanyID, Etiquetas)
                    VALUES (source.ID, source.Asunto, source.Estado, source.Prioridad, source.Tipo,
                            source.Subtipo, source.Agente, source.TiempoCreacion, source.TiempoResolucion,
                            source.RequesterID, source.CompanyID, source.Etiquetas);
            """, id_ticket, asunto, estado, prioridad, tipo, subtipo, agente, tiempo_creacion, tiempo_resolucion, requester_id, company_id, etiquetas)
        except Exception as e:
            print(f"Error al insertar el ticket {id_ticket}: {e}")

    conn.commit()

# Función para obtener la última sincronización desde la tabla Sincronizacion
def obtener_ultima_sincronizacion(entity_freshdesk):
    cursor.execute("SELECT LastUpdate FROM Sincronizacion WHERE EntityFreshdesk = ?", entity_freshdesk)
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

# Función para actualizar la última sincronización en la tabla Sincronizacion
def actualizar_ultima_sincronizacion(entity_freshdesk, fecha):
    cursor.execute("""
        UPDATE Sincronizacion
        SET LastUpdate = ?
        WHERE EntityFreshdesk = ?
    """, fecha, entity_freshdesk)
    conn.commit()
    print(f"Última sincronización de {entity_freshdesk} actualizada a: {fecha}")

# Ejecutar todo el flujo
if __name__ == "__main__":
    # 1. Consulta la última sincronización
    ultima_sincronizacion = obtener_ultima_sincronizacion("tickets")
    if ultima_sincronizacion:
        print(f"Última sincronización de tickets: {ultima_sincronizacion}")
    else:
        print("Nunca se ha sincronizado tickets antes. Sincronizando desde 14/OCT/2025...")
        ultima_sincronizacion = START_DATE

    # 2. Llama a la API de Freshdesk usando la última fecha
    tickets = obtener_tickets(ultima_sincronizacion)

    # 3. Inserta o actualiza los tickets en la base de datos
    print(f"Tickets obtenidos: {len(tickets)}")
    poblar_tickets(tickets)

    # 4. Encuentra la fecha más reciente de los tickets sincronizados y actualiza la tabla Sincronizacion
    if tickets:
        ultima_fecha = max(ticket["updated_at"] for ticket in tickets)
        actualizar_ultima_sincronizacion("tickets", ultima_fecha)
    else:
        print("No hay tickets nuevos o actualizados.")

    # Cierra la conexión
    conn.close()