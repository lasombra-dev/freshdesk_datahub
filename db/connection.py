import pyodbc
from config import settings

class DBConnection:
    def __init__(self):
        self.conn_str = (
            f"DRIVER={settings.DB_DRIVER};"
            f"SERVER={settings.DB_SERVER};"
            f"DATABASE={settings.DB_DATABASE};"
            f"UID={settings.DB_USERNAME};"
            f"PWD={settings.DB_PASSWORD};"
        )
        self.conn = None

    def connect(self):
        """Se conecta a la base de datos al toque."""
        try:
            self.conn = pyodbc.connect(self.conn_str)
            print("Conexión a BD establecida exitosamente")
            return self.conn
        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")
            raise

    def close(self):
        """Cierra la conexión si está abierta, pa no dejarla colgando."""
        if self.conn:
            self.conn.close()
            print("Conexión a BD cerrada")

    def __enter__(self):
        self.connect()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def test_connection(self):
        """Prueba si la conexión funca con una consulta simple."""
        try:
            with self as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 AS Test;")
                result = cursor.fetchone()
                if result and result.Test == 1:
                    print("Prueba de conexión exitosa")
        except Exception as e:
            print(f"Error en la prueba de conexión: {e}")