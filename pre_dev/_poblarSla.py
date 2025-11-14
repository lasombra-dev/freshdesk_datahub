import requests
import pyodbc

# Configuración de Freshdesk
FRESHDESK_DOMAIN = "grupoempack.freshdesk.com"  # Cambia esto por tu dominio
API_KEY = "NcWk2UUwZSPC6WCWn3VZ"
HEADERS = {
    "Content-Type": "application/json"
}

# Endpoint de SLA Policies
ENDPOINT = f"https://{FRESHDESK_DOMAIN}/api/v2/sla_policies"

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

# Función para obtener las políticas SLA
def obtener_sla_policies():
    response = requests.get(
        ENDPOINT,
        auth=(API_KEY, "X"),
        headers=HEADERS
    )

    if response.status_code != 200:
        print(f"Error al consultar la API de SLA Policies: {response.status_code}")
        return []

    return response.json()

# Poblar SLA Policies
def poblar_sla_policies(sla_policies):
    for policy in sla_policies:
        id_policy = policy.get("id")
        nombre = policy.get("name", "Sin Nombre")
        sla_target = policy.get("sla_target", {})

        # Insertar datos por prioridad
        for prioridad, tiempos in sla_target.items():
            respond_within = tiempos.get("respond_within", 0) // 60  # Convertir segundos a minutos
            resolve_within = tiempos.get("resolve_within", 0) // 60  # Convertir segundos a minutos

            try:
                cursor.execute("""
                    MERGE SLA_Policies AS target
                    USING (SELECT ? AS ID, ? AS Nombre, ? AS Prioridad, ? AS RespondWithin, ? AS ResolveWithin) AS source
                    ON target.ID = source.ID AND target.Prioridad = source.Prioridad
                    WHEN MATCHED THEN
                        UPDATE SET Nombre = source.Nombre,
                                   TiempoRespuesta = source.RespondWithin,
                                   TiempoResolucion = source.ResolveWithin
                    WHEN NOT MATCHED THEN
                        INSERT (ID, Nombre, Prioridad, TiempoRespuesta, TiempoResolucion)
                        VALUES (source.ID, source.Nombre, source.Prioridad, source.RespondWithin, source.ResolveWithin);
                """, id_policy, nombre, prioridad, respond_within, resolve_within)
            except Exception as e:
                print(f"Error al insertar la política SLA {id_policy}, prioridad {prioridad}: {e}")

    conn.commit()

if __name__ == "__main__":
    print("Extrayendo políticas SLA desde Freshdesk...")
    sla_policies = obtener_sla_policies()

    print(f"Políticas SLA obtenidas: {len(sla_policies)}")
    poblar_sla_policies(sla_policies)

    print("¡Tabla de SLA actualizada con éxito!")
    conn.close()