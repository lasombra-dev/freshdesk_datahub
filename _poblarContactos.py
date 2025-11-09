import requests
import pyodbc

# Configuración de Freshdesk
FRESHDESK_DOMAIN = "grupoempack.freshdesk.com"  # Cambia esto por tu dominio
API_KEY = "NcWk2UUwZSPC6WCWn3VZ"
HEADERS = {
    "Content-Type": "application/json"
}

# Endpoint de contactos
ENDPOINT = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts"

# Conexión a la base de datos SQL
conn = pyodbc.connect(
    #"DRIVER={SQL Server};"
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=ge-db-dev02.c904tqksriup.us-east-1.rds.amazonaws.com;"  # Cambia esto por tu servidor
    "DATABASE=freshdesk_datahub;"  # Cambia esto por tu base de datos
    "UID=sysdev;"
    "PWD=Lg9oAnCywBmKNh;"
)
cursor = conn.cursor()

# Función para obtener contactos con paginación
def obtener_contactos():
    contactos = []
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
            break  # Termina cuando no hay más contactos

        contactos.extend(data)  # Agrega los contactos de esta página
        page += 1

    return contactos

# Poblar contactos
def poblar_contactos(contactos):
    for contacto in contactos:
        id_contacto = contacto.get("id")
        nombre = contacto.get("name", "Sin Nombre")  # Valor por defecto si no tiene nombre
        correo = contacto.get("email", None)

        try:
            cursor.execute("""
                MERGE Contactos AS target
                USING (SELECT ? AS ID, ? AS NombreCompleto, ? AS Correo) AS source
                ON target.ID = source.ID
                WHEN MATCHED THEN
                    UPDATE SET NombreCompleto = source.NombreCompleto,
                               Correo = source.Correo
                WHEN NOT MATCHED THEN
                    INSERT (ID, NombreCompleto, Correo)
                    VALUES (source.ID, source.NombreCompleto, source.Correo);
            """, id_contacto, nombre, correo)
        except Exception as e:
            print(f"Error al insertar el contacto {id_contacto}: {e}")

    conn.commit()

if __name__ == "__main__":
    print("Extrayendo contactos desde Freshdesk...")
    contactos = obtener_contactos()

    print(f"Contactos obtenidos: {len(contactos)}")
    poblar_contactos(contactos)

    print("¡Tabla de contactos actualizada con éxito!")
    conn.close()