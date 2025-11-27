# Freshdesk Datahub

Este proyecto se encarga de bajar la data de Freshdesk (Contactos, Empresas, Agentes y Tickets) y guardarla en una base de datos SQL Server.

La idea es tener un espejo de los datos para poder hacer reportes o análisis sin pegarle directo a la API todo el tiempo.

## Estructura

El proyecto está ordenado así para que sea fácil de mantener:

- `config/`: Aquí va la configuración, como las credenciales y eso.
- `db/`: Todo lo que tiene que ver con la conexión a la base de datos y las queries.
- `freshdesk/`: La lógica para hablar con la API de Freshdesk y procesar cada entidad (tickets, contactos, etc).
- `utils/`: Cosas útiles que se usan en varios lados, como el logger.
- `main.py`: El script principal que corre todo el proceso.

## Cómo usarlo

1.  Asegúrate de tener Python instalado.
2.  Instala las librerías necesarias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Crea un archivo `.env` en la raíz (puedes copiar el `.env.example` si hubiera, pero básicamente necesitas tus credenciales de Freshdesk y de la base de datos). Tambien, si aun sigo en Empack, pideme el .env. 😒
4.  Corre el script:
    ```bash
    python main.py
    ```

El script va a ir imprimiendo en consola qué está haciendo, así que solo déjalo correr hasta que termine.

Cuando el código se encuentra con registros ya existentes o registros que le falten relaciones, como por ejemplo Contactos eliminados, arrojará errores de inserción y cosas de constraint. Solo ignoralos.

## Notas

- Si falla la conexión a la base de datos, revisa que estés en la VPN o que tengas acceso al servidor.
- La primera vez puede tardar un poco si hay muchos datos, después solo actualiza lo que cambió (usa `MERGE`).
