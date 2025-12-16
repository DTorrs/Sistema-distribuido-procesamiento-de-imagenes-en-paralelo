# Archivo: backend_rest/config.py
# CONFIGURACIÓN DEL BACKEND REST

import os

class Config:
    """Configuración centralizada"""
    
    # Servidor REST
    HOST = os.getenv('REST_HOST', '0.0.0.0')
    PORT = int(os.getenv('REST_PORT', 3000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # URL del servidor SOAP
    SOAP_URL = os.getenv('SOAP_URL', 'http://localhost:8000/soap')
