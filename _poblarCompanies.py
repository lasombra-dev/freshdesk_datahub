import requests
import pyodbc

# Configuración de Freshdesk
FRESHDESK_DOMAIN = "grupoempack.freshdesk.com"  # Cambia esto por tu dominio
API_KEY = "NcWk2UUwZSPC6WCWn3VZ"
HEADERS = {
    "Content-Type": "application/json"
}

# Endpoint de empresas
ENDPOINT = f"https://{FRESHDESK_DOMAIN}/api/v2/companies"

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

def obtener_empresas():
    empresas = []
    page = 1

    while True:
        response = requests.get(
            f"{ENDPOINT}?page={page}",
            auth=(API_KEY, "X"),  # Autenticación básica con API Key
            headers=HEADERS
        )

        if response.status_code != 200:
            print(f"Error al consultar la API: {response.status_code}")
            break

        data = response.json()
        if not data:
            break  # Termina si no hay más empresas

        empresas.extend(data)  # Agrega las empresas de esta página a la lista
        page += 1

    return empresas

def poblar_empresas(empresas):
    for empresa in empresas:
        id_empresa = empresa.get("id")
        nombre_empresa = empresa.get("name", "Sin Nombre")

        try:
            cursor.execute("""
                MERGE Empresas AS target
                USING (SELECT ? AS ID, ? AS NombreEmpresa) AS source
                ON target.ID = source.ID
                WHEN MATCHED THEN
                    UPDATE SET NombreEmpresa = source.NombreEmpresa
                WHEN NOT MATCHED THEN
                    INSERT (ID, NombreEmpresa)
                    VALUES (source.ID, source.NombreEmpresa);
            """, id_empresa, nombre_empresa)
        except Exception as e:
            print(f"Error al insertar la empresa {id_empresa}: {e}")

    conn.commit()


if __name__ == "__main__":
    print("Extrayendo empresas desde Freshdesk...")
    empresas = obtener_empresas()

    print(f"Empresas obtenidas: {len(empresas)}")
    poblar_empresas(empresas)

    print("¡Tabla de empresas actualizada con éxito!")
    conn.close()