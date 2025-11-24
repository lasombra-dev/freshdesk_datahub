import requests
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FreshdeskAPI:
    def __init__(self):
        self.domain = settings.FRESHDESK_DOMAIN
        self.api_key = settings.FRESHDESK_API_KEY
        self.base_url = f"https://{self.domain}/api/v2"
        self.auth = (self.api_key, "X")
        self.headers = {"Content-Type": "application/json"}

    def _get(self, endpoint, params=None):
        """Método interno para realizar peticiones GET."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición a {url}: {e}")
            return None

    def get_all_pages(self, endpoint, params=None):
        """Obtiene todos los resultados paginados de un endpoint."""
        if params is None:
            params = {}
        
        results = []
        page = 1
        while True:
            params['page'] = page
            # Algunos endpoints usan per_page, otros no. Asumimos 100 por defecto si es soportado.
            if 'per_page' not in params:
                params['per_page'] = 100
                
            logger.info(f"Obteniendo página {page} de {endpoint}...")
            data = self._get(endpoint, params)
            
            # Manejo de diferentes estructuras de respuesta (lista o dict con 'results')
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'results' in data:
                items = data['results']
            
            if not items:
                break
                
            results.extend(items)
            page += 1
            
            # Si recibimos menos del límite, es la última página (aproximación)
            if len(items) < params.get('per_page', 30): # 30 es el default de Freshdesk
                 break
                 
        return results

    def search_tickets(self, query):
        """Busca tickets usando la API de búsqueda."""
        # La API de búsqueda tiene una estructura diferente y paginación limitada (max 300 items total en deep pagination, pero aquí usaremos paginación normal hasta 10 paginas max por query)
        # Nota: La API de búsqueda de Freshdesk devuelve 'results' y 'total'.
        # Para simplificar, usaremos la lógica de paginación manual.
        
        tickets = []
        page = 1
        while True:
            url = f"{self.base_url}/search/tickets"
            params = {"query": f'"{query}"', "page": page}
            
            logger.info(f"Buscando tickets (página {page})...")
            try:
                response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    break
                    
                tickets.extend(results)
                page += 1
                
                if len(results) < 30: # 30 es el tamaño de página por defecto en búsqueda
                    break
            except requests.exceptions.RequestException as e:
                logger.error(f"Error buscando tickets: {e}")
                break
                
        return tickets
