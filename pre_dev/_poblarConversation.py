import requests
import pyodbc
import time

# Configuración de Freshdesk
FRESHDESK_DOMAIN = "grupoempack.freshdesk.com"  # Cambia esto por tu dominio
API_KEY = "NcWk2UUwZSPC6WCWn3VZ"
HEADERS = {
    "Content-Type": "application/json"
}

# Conexión a la base de datos SQL
conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    #"DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=ge-db-dev02.c904tqksriup.us-east-1.rds.amazonaws.com;"
    "DATABASE=freshdesk_datahub;"
    "UID=sysdev;"
    "PWD=Lg9oAnCywBmKNh;"
)
cursor = conn.cursor()

# Función para obtener conversaciones de un ticket específico
def obtener_conversaciones(ticket_id, intentos=3):
    conversaciones = []
    page = 1

    while intentos > 0:
        try:
            response = requests.get(
                f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}/conversations?page={page}",
                auth=(API_KEY, "X"),
                headers=HEADERS
            )

            if response.status_code == 200:
                data = response.json()
                if not data:
                    break  # No hay más conversaciones
                conversaciones.extend(data)
                page += 1
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                print(f"Error 429: esperando {retry_after} segundos...")
                time.sleep(retry_after)
                continue
            else:
                print(f"Error al consultar la API para el ticket {ticket_id}: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Error de red al consultar el ticket {ticket_id}: {e}")
            intentos -= 1
            time.sleep(5)  # Espera antes de reintentar

    return conversaciones

# Función para poblar la tabla Conversations
def poblar_conversaciones(ticket_id, conversaciones):
    for conversacion in conversaciones:
        id_conversacion = conversacion.get("id")
        user_id = conversacion.get("user_id")
        body = conversacion.get("body_text", "Sin Contenido")
        body = body[:500] if body else "Sin Contenido"  # Sanitización
        creado = conversacion.get("created_at")

        try:
            cursor.execute("""
                MERGE Conversations AS target
                USING (SELECT ? AS ID, ? AS TicketID, ? AS UserID, ? AS Body, ? AS CreatedAt) AS source
                ON target.ID = source.ID
                WHEN MATCHED THEN
                    UPDATE SET TicketID = source.TicketID,
                               UserID = source.UserID,
                               Body = source.Body,
                               CreatedAt = source.CreatedAt
                WHEN NOT MATCHED THEN
                    INSERT (ID, TicketID, UserID, Body, CreatedAt)
                    VALUES (source.ID, source.TicketID, source.UserID, source.Body, source.CreatedAt);
            """, id_conversacion, ticket_id, user_id, body, creado)
        except Exception as e:
            print(f"Error al insertar la conversación {id_conversacion}: {e}")

    conn.commit()

if __name__ == "__main__":
    print("Extrayendo conversaciones de los tickets...")

    # Obtener lista de tickets desde la tabla Tickets
    cursor.execute("SELECT ID FROM Tickets")
    tickets = cursor.fetchall()

    for ticket in tickets:
        ticket_id = ticket[0]
        print(f"Procesando conversaciones del ticket {ticket_id}...")
        
        # Obtener las conversaciones del ticket
        conversaciones = obtener_conversaciones(ticket_id)
        
        # Poblar la tabla Conversations
        poblar_conversaciones(ticket_id, conversaciones)

    print("¡Tabla de conversaciones actualizada con éxito!")
    conn.close()