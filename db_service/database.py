# Archivo: db_service/database.py
# GESTOR DE CONEXIONES A LA BASE DE DATOS MYSQL

import mysql.connector
from mysql.connector import pooling, Error
from config import Config
import threading

class Database:
    """
    CLASE SINGLETON PARA GESTIONAR CONEXIONES A MYSQL
    
    Implementa un pool de conexiones para mejorar el rendimiento
    y evitar crear/destruir conexiones constantemente.
    """
    
    _instance = None
    _lock = threading.Lock()
    _pool = None
    
    def __new__(cls):
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """
        INICIALIZACIÓN DEL POOL DE CONEXIONES
        Crea un pool de conexiones que se reutilizan
        """
        try:
            print("[DB] Inicializando pool de conexiones...")
            self._pool = pooling.MySQLConnectionPool(**Config.get_db_config())
            print(f"[DB] Pool creado exitosamente con {Config.DB_POOL_SIZE} conexiones")
        except Error as e:
            print(f"[DB] ERROR al crear pool: {e}")
            raise
    
    def get_connection(self):
        """
        OBTENER CONEXIÓN DEL POOL
        
        Returns:
            connection: Conexión MySQL del pool
        """
        try:
            return self._pool.get_connection()
        except Error as e:
            print(f"[DB] ERROR al obtener conexión: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=True): #leer datos
        """
        EJECUTAR QUERY SQL (SELECT)
        
        Args:
            query (str): Query SQL a ejecutar
            params (tuple): Parámetros para query preparado
            fetch (bool): Si debe retornar resultados
            
        Returns:
            list: Lista de filas (si fetch=True)
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)  # Retorna filas como diccionarios
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
                return result
            
            return None
            
        except Error as e:
            print(f"[DB] ERROR en query: {e}")
            print(f"[DB] Query: {query}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_update(self, query, params=None):
        """
        EJECUTAR QUERY SQL (INSERT/UPDATE/DELETE)
        
        Args:
            query (str): Query SQL a ejecutar
            params (tuple): Parámetros para query preparado
            
        Returns:
            int: ID del último registro insertado (para INSERT)
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            connection.commit()
            last_id = cursor.lastrowid
            
            return last_id
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"[DB] ERROR en update: {e}")
            print(f"[DB] Query: {query}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_transaction(self, queries_with_params):
        """
        EJECUTAR MÚLTIPLES QUERIES EN UNA TRANSACCIÓN
        
        Args:
            queries_with_params (list): Lista de tuplas (query, params)
            
        Returns:
            bool: True si la transacción fue exitosa
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Deshabilitar auto-commit para transacción manual
            connection.start_transaction()
            
            for query, params in queries_with_params:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            
            connection.commit()
            return True
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"[DB] ERROR en transacción: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()