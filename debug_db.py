import pyodbc
from config import settings

def check_schema():
    print("--- INICIO DIAGNOSTICO ---", flush=True)
    
    conn_str = (
        f"DRIVER={settings.DB_DRIVER};"
        f"SERVER={settings.DB_SERVER};"
        f"DATABASE={settings.DB_DATABASE};"
        f"UID={settings.DB_USERNAME};"
        f"PWD={settings.DB_PASSWORD}"
    )
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        table_name = "Agentes"
        print(f"Consultando columnas para la tabla: {table_name}", flush=True)
        
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
        columns = [row.COLUMN_NAME for row in cursor.fetchall()]
        
        if columns:
            print(f"COLUMNAS ENCONTRADAS: {columns}", flush=True)
        else:
            print(f"No se encontraron columnas para la tabla {table_name}.", flush=True)
            
            # Check if table exists with different casing or schema
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES")
            tables = [row.TABLE_NAME for row in cursor.fetchall()]
            print(f"TABLAS EXISTENTES: {tables}", flush=True)

        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
    
    print("--- FIN DIAGNOSTICO ---", flush=True)

if __name__ == "__main__":
    check_schema()
