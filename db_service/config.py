# Archivo: db_service/config.py
# CONFIGURACIÓN DEL SERVICIO REST Y BASE DE DATOS

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """
    CLASE DE CONFIGURACIÓN CENTRALIZADA
    Maneja todas las configuraciones del servicio REST
    """
    
    # CONFIGURACIÓN DEL SERVIDOR REST
    REST_HOST = os.getenv('REST_HOST', '0.0.0.0')
    REST_PORT = int(os.getenv('REST_PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # CONFIGURACIÓN DE LA BASE DE DATOS MYSQL
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_NAME = os.getenv('DB_NAME', 'image_processing_system')
    
    # CONFIGURACIÓN DE POOL DE CONEXIONES
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 30))  # Aumentado para soportar procesamiento paralelo
    DB_POOL_NAME = 'image_processing_pool'
    
    @classmethod
    def get_db_config(cls):
        """Retorna diccionario con configuración de DB"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'pool_name': cls.DB_POOL_NAME,
            'pool_size': cls.DB_POOL_SIZE
        }