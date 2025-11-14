import requests
import pyodbc

# Configuración de Freshdesk
FRESHDESK_DOMAIN = "grupoempack.freshdesk.com"  # Cambia esto por tu dominio
API_KEY = "NcWk2UUwZSPC6WCWn3VZ"
HEADERS = {
    "Content-Type": "application/json"
}

# Endpoint de agentes
ENDPOINT = f"https://{FRESHDESK_DOMAIN}/api/v2/agents"

# Conexión a la base de datos SQL
conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    #"DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=ge-db-dev02.c904tqksriup.us-east-1.rds.amazonaws.com;"  # Cambia esto por tu servidor
    "DATABASE=freshdesk_datahub;"  # Cambia esto por tu base de datos
    "UID=sysdev;"
    "PWD=Lg9oAnCywBmKNh;"
)
cursor = conn.cursor()

# Función para obtener agentes con paginación
def obtener_agentes():
    agentes = []
    page = 1
    per_page = 100  # Máximo permitido por Freshdesk

    while True:
        response = requests.get(
            f"{ENDPOINT}?page={page}&per_page={per_page}",
            auth=(API_KEY, "X"),  # Autenticación básica
            headers=HEADERS
        )

        if response.status_code != 200:
            print(f"Error al consultar la API: {response.status_code}")
            break

        data = response.json()
        if not data:
            break  # Termina cuando no hay más agentes

        agentes.extend(data)  # Agrega los agentes de esta página
        page += 1

    return agentes

# Poblar agentes
def poblar_agentes(agentes):
    for agente in agentes:
        id_agente = agente.get("id")
        
        # Extraer datos desde el campo 'contact'
        contacto = agente.get("contact", {})
        nombre = contacto.get("name", "Sin Nombre")  # Nombre desde 'contact'
        correo = contacto.get("email", None)         # Correo desde 'contact'

        try:
            cursor.execute("""
                MERGE Agentes AS target
                USING (SELECT ? AS ID, ? AS Nombre, ? AS Correo) AS source
                ON target.ID = source.ID
                WHEN MATCHED THEN
                    UPDATE SET NombreCompleto = source.Nombre,
                               Correo = source.Correo
                WHEN NOT MATCHED THEN
                    INSERT (ID, NombreCompleto, Correo)
                    VALUES (source.ID, source.Nombre, source.Correo);
            """, id_agente, nombre, correo)
        except Exception as e:
            print(f"Error al insertar el agente {id_agente}: {e}")

    conn.commit()

if __name__ == "__main__":
    print("Extrayendo agentes desde Freshdesk...")
    agentes = obtener_agentes()

    print(f"Agentes obtenidos: {len(agentes)}")
    poblar_agentes(agentes)

    print("¡Tabla de agentes actualizada con éxito!")
    conn.close()