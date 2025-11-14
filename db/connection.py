import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class DBConnection:
    def __init__(self):
        # Obtener las credenciales desde las variables de entorno
        self.server = os.getenv("DB_SERVER")
        self.database = os.getenv("DB_DATABASE")
        self.username = os.getenv("DB_USERNAME")
        self.password = os.getenv("DB_PASSWORD")
        self.driver = os.getenv("DB_DRIVER", "{SQL Server}")  # Valor por defecto

        # Cadena de conexión
        self.conn_str = (
            f"DRIVER={self.driver};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
        )

    def connect(self):
        """Establece la conexión a la base de datos."""
        try:
            conn = pyodbc.connect(self.conn_str)
            print("Conexión establecida exitosamente")
            return conn
        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")
            raise

    def test_connection(self):
        """Prueba la conexión realizando una consulta simple."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS Test;")
            result = cursor.fetchone()
            if result and result.Test == 1:
                print("Conexión probada exitosamente")
            conn.close()
        except Exception as e:
            print(f"Error en la prueba de conexión: {e}")

# Imprimir variables cargadas
print("DB_SERVER:", os.getenv("DB_SERVER"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))
print("DB_NAME:", os.getenv("DB_NAME"))