# Archivo: db_service/models.py
# MODELOS DE DATOS Y VALIDACIONES

from datetime import datetime
from typing import List, Dict, Optional

class BatchRequest:
    """Modelo para solicitudes de lotes"""
    
    @staticmethod
    def to_dict(row):
        """Convierte fila de DB a diccionario"""
        if not row:
            return None
        return {
            'batch_id': row['batch_id'],
            'user_id': row['user_id'],
            'batch_name': row['batch_name'],
            'status': row['status'],
            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
            'started_at': row['started_at'].isoformat() if row['started_at'] else None,
            'completed_at': row['completed_at'].isoformat() if row['completed_at'] else None,
            'total_images': row['total_images'],
            'processed_images': row['processed_images'],
            'output_format': row['output_format'],
            'compression_type': row['compression_type']
        }

class Image:
    """Modelo para imágenes"""
    
    @staticmethod
    def to_dict(row):
        """Convierte fila de DB a diccionario"""
        if not row:
            return None
        return {
            'image_id': row['image_id'],
            'batch_id': row['batch_id'],
            'original_filename': row['original_filename'],
            'storage_path': row['storage_path'],
            'file_size': row['file_size'],
            'width': row['width'],
            'height': row['height'],
            'format': row['format'],
            'created_at': row['created_at'].isoformat() if row['created_at'] else None
        }

class ProcessedResult:
    """Modelo para resultados procesados"""
    
    @staticmethod
    def to_dict(row):
        """Convierte fila de DB a diccionario"""
        if not row:
            return None
        return {
            'result_id': row['result_id'],
            'image_id': row['image_id'],
            'node_id': row['node_id'],
            'result_filename': row['result_filename'],
            'storage_path': row['storage_path'],
            'file_size': row['file_size'],
            'width': row['width'],
            'height': row['height'],
            'format': row['format'],
            'processing_time_ms': row['processing_time_ms'],
            'status': row['status'],
            'error_message': row['error_message'],
            'created_at': row['created_at'].isoformat() if row['created_at'] else None
        }

class ProcessingNode:
    """Modelo para nodos de procesamiento"""
    
    @staticmethod
    def to_dict(row):
        """Convierte fila de DB a diccionario"""
        if not row:
            return None
        return {
            'node_id': row['node_id'],
            'node_name': row['node_name'],
            'ip_address': row['ip_address'],
            'port': row['port'],
            'status': row['status'],
            'last_heartbeat': row['last_heartbeat'].isoformat() if row['last_heartbeat'] else None,
            'cpu_cores': row['cpu_cores'],
            'ram_gb': row['ram_gb'],
            'current_load': row.get('current_load', 0),
            'max_concurrent_jobs': row.get('max_concurrent_jobs', 5),
            'weight': row.get('weight', 1),
            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
            'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
        }

class Transformation:
    """Modelo para transformaciones"""
    
    @staticmethod
    def to_dict(row):
        """Convierte fila de DB a diccionario"""
        if not row:
            return None
        return {
            'transformation_id': row['transformation_id'],
            'name': row['name'],
            'description': row['description'],
            'parameters_schema': row['parameters_schema'],
            'is_active': row['is_active']
        }