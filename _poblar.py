import requests
import pyodbc
import time
from datetime import datetime, timezone

# Configuración de Freshdesk
FRESHDESK_DOMAIN = "grupoempack.freshdesk.com"  # Cambia por tu dominio
API_KEY = "NcWk2UUwZSPC6WCWn3VZ"  # Cambia por tu API Key
HEADERS = {"Content-Type": "application/json"}
START_DATE = "2025-10-14"  # Fecha inicial fija en formato ISO 8601 (UTC)

# Conexión a la base de datos SQL
conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=ge-db-dev02.c904tqksriup.us-east-1.rds.amazonaws.com;"  # Cambia esto por tu servidor
    "DATABASE=freshdesk_datahub;"  # Cambia esto por tu base de datos
    "UID=sysdev;"
    "PWD=Lg9oAnCywBmKNh;"
)
cursor = conn.cursor()

# ---------------- FUNCIONES PARA CADA TABLA ----------------

# 1. Poblar Contactos
def obtener_contactos():
    contactos = []
    page = 1
    while True:
        response = requests.get(
            f"https://{FRESHDESK_DOMAIN}/api/v2/contacts?page={page}&per_page=100",
            auth=(API_KEY, "X"),
            headers=HEADERS
        )
        if response.status_code != 200:
            print(f"Error al obtener contactos: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        contactos.extend(data)
        page += 1
    return contactos

def poblar_contactos(contactos):
    for contacto in contactos:
        id_contacto = contacto.get("id")
        nombre = contacto.get("name", "Sin Nombre")
        correo = contacto.get("email", None)
        try:
            cursor.execute("""
                MERGE Contactos AS target
                USING (SELECT ? AS ID, ? AS NombreCompleto, ? AS Correo) AS source
                ON target.ID = source.ID
                WHEN MATCHED THEN
                    UPDATE SET NombreCompleto = source.NombreCompleto, Correo = source.Correo
                WHEN NOT MATCHED THEN
                    INSERT (ID, NombreCompleto, Correo)
                    VALUES (source.ID, source.NombreCompleto, source.Correo);
            """, id_contacto, nombre, correo)
        except Exception as e:
            print(f"Error al insertar el contacto {id_contacto}: {e}")
    conn.commit()

# 2. Poblar Empresas
def obtener_empresas():
    empresas = []
    page = 1
    while True:
        response = requests.get(
            f"https://{FRESHDESK_DOMAIN}/api/v2/companies?page={page}",
            auth=(API_KEY, "X"),
            headers=HEADERS
        )
        if response.status_code != 200:
            print(f"Error al obtener empresas: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        empresas.extend(data)
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

# 3. Poblar Agentes
def obtener_agentes():
    agentes = []
    page = 1
    while True:
        response = requests.get(
            f"https://{FRESHDESK_DOMAIN}/api/v2/agents?page={page}&per_page=100",
            auth=(API_KEY, "X"),
            headers=HEADERS
        )
        if response.status_code != 200:
            print(f"Error al obtener agentes: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        agentes.extend(data)
        page += 1
    return agentes

def poblar_agentes(agentes):
    for agente in agentes:
        id_agente = agente.get("id")
        contacto = agente.get("contact", {})
        nombre = contacto.get("name", "Sin Nombre")
        correo = contacto.get("email", None)
        try:
            cursor.execute("""
                MERGE Agentes AS target
                USING (SELECT ? AS ID, ? AS Nombre, ? AS Correo) AS source
                ON target.ID = source.ID
                WHEN MATCHED THEN
                    UPDATE SET Nombre = source.Nombre, Correo = source.Correo
                WHEN NOT MATCHED THEN
                    INSERT (ID, Nombre, Correo)
                    VALUES (source.ID, source.Nombre, source.Correo);
            """, id_agente, nombre, correo)
        except Exception as e:
            print(f"Error al insertar el agente {id_agente}: {e}")
    conn.commit()

# 4. Poblar Tickets con CF_Empresa
def obtener_tickets(fecha_inicio):
    tickets = []
    page = 1
    fecha_actual = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    while True:
        query = f"created_at:>'{fecha_inicio}' AND created_at:<'{fecha_actual}'"
        url = f"https://{FRESHDESK_DOMAIN}/api/v2/search/tickets?query=\"{query}\"&page={page}"
        response = requests.get(url, auth=(API_KEY, "X"), headers=HEADERS)
        if response.status_code != 200:
            print(f"Error al obtener tickets: {response.status_code}")
            break
        data = response.json().get("results", [])
        if not data:
            break
        tickets.extend(data)
        page += 1
    return tickets

def poblar_tickets(tickets):
    for ticket in tickets:
        id_ticket = ticket.get("id")
        asunto = ticket.get("subject", "Sin Asunto")
        estado = ticket.get("status")
        prioridad = ticket.get("priority")
        tipo = ticket.get("type")
        custom_fields = ticket.get("custom_fields", {})
        subtipo = custom_fields.get("cf_subtipo", "Sin Subtipo")
        cf_empresa = custom_fields.get("cf_empresa", "Sin Empresa")  # Aquí el CF_Empresa
        agente = ticket.get("responder_id", None)
        tiempo_creacion = ticket.get("created_at")
        tiempo_resolucion = ticket.get("due_by", None)
        requester_id = ticket.get("requester_id", None)
        company_id = ticket.get("company_id", None)
        etiquetas = ",".join(ticket.get("tags", []))
        try:
            cursor.execute("""
                MERGE Tickets AS target
                USING (SELECT ? AS ID, ? AS Asunto, ? AS Estado, ? AS Prioridad, ? AS Tipo, 
                              ? AS Subtipo, ? AS CF_Empresa, ? AS Agente, ? AS TiempoCreacion, 
                              ? AS TiempoResolucion, ? AS RequesterID, ? AS CompanyID, ? AS Etiquetas) AS source
                ON target.ID = source.ID
                WHEN MATCHED THEN
                    UPDATE SET Asunto = source.Asunto, Estado = source.Estado, Prioridad = source.Prioridad,
                               Tipo = source.Tipo, Subtipo = source.Subtipo, CF_Empresa = source.CF_Empresa,
                               Agente = source.Agente, TiempoCreacion = source.TiempoCreacion,
                               TiempoResolucion = source.TiempoResolucion, RequesterID = source.RequesterID,
                               CompanyID = source.CompanyID, Etiquetas = source.Etiquetas
                WHEN NOT MATCHED THEN
                    INSERT (ID, Asunto, Estado, Prioridad, Tipo, Subtipo, CF_Empresa, Agente, 
                            TiempoCreacion, TiempoResolucion, RequesterID, CompanyID, Etiquetas)
                    VALUES (source.ID, source.Asunto, source.Estado, source.Prioridad, source.Tipo,
                            source.Subtipo, source.CF_Empresa, source.Agente, source.TiempoCreacion,
                            source.TiempoResolucion, source.RequesterID, source.CompanyID, source.Etiquetas);
            """, id_ticket, asunto, estado, prioridad, tipo, subtipo, cf_empresa, agente, tiempo_creacion, tiempo_resolucion, requester_id, company_id, etiquetas)
        except Exception as e:
            print(f"Error al insertar el ticket {id_ticket}: {e}")
    conn.commit()

# ---------------- EJECUCIÓN DEL FLUJO ----------------
if __name__ == "__main__":
    print("Iniciando la sincronización completa...")

    print("1. Poblando Contactos...")
    contactos = obtener_contactos()
    poblar_contactos(contactos)

    print("2. Poblando Empresas...")
    empresas = obtener_empresas()
    poblar_empresas(empresas)

    print("3. Poblando Agentes...")
    agentes = obtener_agentes()
    poblar_agentes(agentes)

    print("4. Poblando Tickets...")
    tickets = obtener_tickets(START_DATE)
    poblar_tickets(tickets)

    print("¡Sincronización completa!")
    conn.close()