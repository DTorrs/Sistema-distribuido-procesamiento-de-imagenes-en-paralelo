# Archivo: db_service/routes/downloads.py
# ENDPOINT PARA DESCARGAR LOTES EN ZIP

import os
import zipfile
from io import BytesIO
from flask import Blueprint, send_file, jsonify
from database import Database

downloads_bp = Blueprint('downloads', __name__)
db = Database()

@downloads_bp.route('/<int:batch_id>/download', methods=['GET'])
def download_batch(batch_id):
    """Descargar todas las imágenes procesadas de un lote en ZIP"""
    try:
        print(f"\n[DOWNLOAD] Solicitud de descarga para batch_id={batch_id}")
        
        # CONSULTAR IMÁGENES DEL LOTE EN DB
        query = """
            SELECT 
                i.image_id,
                i.original_filename,
                pr.result_filename,
                pr.storage_path,
                pr.status
            FROM images i
            JOIN processed_results pr ON i.image_id = pr.image_id
            WHERE i.batch_id = %s AND pr.status = 'success'
            ORDER BY i.image_id
        """
        rows = db.execute_query(query, (batch_id,))
        
        if not rows:
            print(f"[DOWNLOAD] No se encontraron imágenes para batch {batch_id}")
            return jsonify({
                'error': f'No hay imágenes procesadas para el lote {batch_id}'
            }), 404
        
        print(f"[DOWNLOAD] Encontradas {len(rows)} imágenes procesadas")
        
        # CREAR ZIP EN MEMORIA
        zip_buffer = BytesIO()
        files_added = 0
        files_missing = 0
        
        # Ruta absoluta al directorio raíz del proyecto
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for row in rows:
                # Construir ruta completa
                file_path = os.path.join(
                    project_root,
                    'server',
                    'output',
                    row['storage_path']
                )
                
                print(f"[DOWNLOAD] Buscando: {file_path}")
                print(f"[DOWNLOAD] ¿Existe? {os.path.exists(file_path)}")
                
                if os.path.exists(file_path):
                    # Agregar al ZIP
                    zip_file.write(file_path, row['result_filename'])
                    files_added += 1
                    print(f"[DOWNLOAD] ✓ Agregado: {row['result_filename']}")
                else:
                    files_missing += 1
                    print(f"[DOWNLOAD] ✗ Archivo no encontrado: {file_path}")
        
        print(f"[DOWNLOAD] Resumen: {files_added} agregados, {files_missing} faltantes")
        
        if files_added == 0:
            return jsonify({
                'error': 'No se encontraron archivos físicos para este lote',
                'details': f'Se esperaban {len(rows)} archivos pero no se encontraron en el disco'
            }), 404
        
        # POSICIONAR AL INICIO DEL BUFFER
        zip_buffer.seek(0)
        
        # ENVIAR ZIP
        print(f"[DOWNLOAD] Enviando ZIP al cliente: batch_{batch_id}.zip")
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'batch_{batch_id}.zip'
        )
        
    except Exception as e:
        print(f"[DOWNLOAD] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@downloads_bp.route('/<int:batch_id>/info', methods=['GET'])
def batch_download_info(batch_id):
    """
    GET /api/batches/{batch_id}/info
    Obtener información sobre las imágenes del lote (sin descargar)
    
    Útil para verificar qué contiene un lote antes de descargarlo
    
    Args:
        batch_id (int): ID del lote
        
    Returns:
        JSON con información del lote
    """
    try:
        query = """
            SELECT 
                i.image_id,
                i.original_filename,
                pr.result_filename,
                pr.status,
                pr.processing_time_ms
            FROM images i
            JOIN processed_results pr ON i.image_id = pr.image_id
            WHERE i.batch_id = %s
            ORDER BY i.image_id
        """
        rows = db.execute_query(query, (batch_id,))
        
        if not rows:
            return jsonify({
                'error': f'No se encontraron imágenes para el lote {batch_id}'
            }), 404
        
        images_info = []
        total_success = 0
        total_failed = 0
        total_time = 0
        
        for row in rows:
            images_info.append({
                'image_id': row['image_id'],
                'original_filename': row['original_filename'],
                'result_filename': row['result_filename'],
                'status': row['status'],
                'processing_time_ms': row['processing_time_ms']
            })
            
            if row['status'] == 'success':
                total_success += 1
            else:
                total_failed += 1
            
            total_time += row['processing_time_ms'] or 0
        
        return jsonify({
            'batch_id': batch_id,
            'total_images': len(rows),
            'successful': total_success,
            'failed': total_failed,
            'total_processing_time_ms': total_time,
            'images': images_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500