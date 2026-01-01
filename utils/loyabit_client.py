"""
Cliente para integración con API de Loyabit
Ajusta las URLs y endpoints según la documentación oficial de Loyabit
"""
import os
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException

class LoyabitClient:
    """Cliente para interactuar con la API de Loyabit"""
    
    def __init__(self):
        # Obtener credenciales desde variables de entorno
        # Configura estas variables en tu archivo .env o variables de entorno
        self.api_key = os.getenv("LOYABIT_API_KEY", "")
        self.api_secret = os.getenv("LOYABIT_API_SECRET", "")
        self.base_url = os.getenv("LOYABIT_BASE_URL", "https://api.loyabit.com/v1")  # Ajustar según la URL real
        self.merchant_id = os.getenv("LOYABIT_MERCHANT_ID", "")
        
        if not self.api_key or not self.api_secret:
            # Si no hay credenciales, el servicio funcionará pero no hará llamadas reales
            self.enabled = False
        else:
            self.enabled = True
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtiene los headers necesarios para las peticiones"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",  # Ajustar según el tipo de autenticación de Loyabit
            "X-API-Key": self.api_key,  # Puede requerir otro formato
            # Agregar otros headers según la documentación de Loyabit
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Realiza una petición HTTP a la API de Loyabit
        Ajusta según el formato que use la API de Loyabit
        """
        if not self.enabled:
            raise HTTPException(
                status_code=503,
                detail="Servicio de Loyabit no configurado. Configura las variables de entorno LOYABIT_API_KEY y LOYABIT_API_SECRET"
            )
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self._get_headers(), params=data, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self._get_headers(), json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self._get_headers(), json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self._get_headers(), timeout=10)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # Log del error (en producción usar un logger apropiado)
            print(f"Error en petición a Loyabit: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    raise HTTPException(
                        status_code=e.response.status_code,
                        detail=f"Error en API de Loyabit: {error_detail}"
                    )
                except:
                    raise HTTPException(
                        status_code=e.response.status_code,
                        detail=f"Error en API de Loyabit: {e.response.text}"
                    )
            raise HTTPException(
                status_code=500,
                detail=f"Error de conexión con Loyabit: {str(e)}"
            )
    
    def crear_cliente(self, cliente_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un cliente en Loyabit
        Ajusta los campos según la documentación de la API de Loyabit
        
        Args:
            cliente_data: Diccionario con los datos del cliente
            
        Returns:
            Diccionario con la respuesta de Loyabit (incluye el ID del cliente)
        """
        # Ajustar el payload según la estructura que espera la API de Loyabit
        payload = {
            "name": f"{cliente_data.get('nombre')} {cliente_data.get('apellido_paterno', '')}",
            "first_name": cliente_data.get('nombre'),
            "last_name": cliente_data.get('apellido_paterno', ''),
            "email": cliente_data.get('correo'),
            "phone": cliente_data.get('celular'),
            # Agregar otros campos según la documentación de Loyabit
        }
        
        # Ajustar el endpoint según la documentación
        return self._make_request("POST", "customers", payload)
    
    def obtener_cliente(self, loyabit_id: str) -> Dict[str, Any]:
        """
        Obtiene información de un cliente desde Loyabit
        
        Args:
            loyabit_id: ID del cliente en Loyabit
            
        Returns:
            Diccionario con la información del cliente
        """
        return self._make_request("GET", f"customers/{loyabit_id}")
    
    def buscar_cliente_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Busca un cliente en Loyabit por email
        Ajustar según los endpoints disponibles en la API
        
        Args:
            email: Email del cliente
            
        Returns:
            Diccionario con la información del cliente o None si no existe
        """
        try:
            # Ajustar el endpoint según la documentación
            response = self._make_request("GET", "customers/search", {"email": email})
            # Ajustar según la estructura de respuesta
            if response and isinstance(response, dict) and "data" in response:
                customers = response.get("data", [])
                if customers:
                    return customers[0]
            elif response and isinstance(response, list) and len(response) > 0:
                return response[0]
            return None
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise
    
    def actualizar_cliente(self, loyabit_id: str, cliente_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza información de un cliente en Loyabit
        
        Args:
            loyabit_id: ID del cliente en Loyabit
            cliente_data: Datos actualizados del cliente
            
        Returns:
            Diccionario con la respuesta de Loyabit
        """
        payload = {
            "name": f"{cliente_data.get('nombre')} {cliente_data.get('apellido_paterno', '')}",
            "first_name": cliente_data.get('nombre'),
            "last_name": cliente_data.get('apellido_paterno', ''),
            "email": cliente_data.get('correo'),
            "phone": cliente_data.get('celular'),
        }
        
        return self._make_request("PUT", f"customers/{loyabit_id}", payload)
    
    def obtener_puntos_cliente(self, loyabit_id: str) -> Dict[str, Any]:
        """
        Obtiene los puntos de un cliente desde Loyabit
        
        Args:
            loyabit_id: ID del cliente en Loyabit
            
        Returns:
            Diccionario con información de puntos
        """
        # Ajustar el endpoint según la documentación
        return self._make_request("GET", f"customers/{loyabit_id}/points")
    
    def agregar_puntos(self, loyabit_id: str, puntos: float, motivo: str = "Compra") -> Dict[str, Any]:
        """
        Agrega puntos a un cliente en Loyabit
        
        Args:
            loyabit_id: ID del cliente en Loyabit
            puntos: Cantidad de puntos a agregar
            motivo: Motivo por el cual se agregan puntos
            
        Returns:
            Diccionario con la respuesta de Loyabit
        """
        payload = {
            "points": puntos,
            "reason": motivo,
            # Agregar otros campos según la documentación
        }
        
        # Ajustar el endpoint según la documentación
        return self._make_request("POST", f"customers/{loyabit_id}/points/add", payload)
    
    def canjear_puntos(self, loyabit_id: str, puntos: float, motivo: str = "Canje") -> Dict[str, Any]:
        """
        Canjea puntos de un cliente en Loyabit
        
        Args:
            loyabit_id: ID del cliente en Loyabit
            puntos: Cantidad de puntos a canjear
            motivo: Motivo del canje
            
        Returns:
            Diccionario con la respuesta de Loyabit
        """
        payload = {
            "points": puntos,
            "reason": motivo,
        }
        
        # Ajustar el endpoint según la documentación
        return self._make_request("POST", f"customers/{loyabit_id}/points/redeem", payload)

# Instancia global del cliente (singleton)
_loyabit_client = None

def get_loyabit_client() -> LoyabitClient:
    """Obtiene la instancia del cliente de Loyabit"""
    global _loyabit_client
    if _loyabit_client is None:
        _loyabit_client = LoyabitClient()
    return _loyabit_client


