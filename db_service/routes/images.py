# Archivo: db_service/routes/images.py
# ENDPOINTS REST PARA GESTIÓN DE IMÁGENES

from flask import Blueprint, request, jsonify
from database import Database
from models import Image, ProcessedResult
import json

images_bp = Blueprint('images', __name__)
db = Database()

@images_bp.route('', methods=['POST'])
def create_image():
    """
    POST /api/images
    Registrar una nueva imagen
    
    Body:
        {
            "batch_id": int,
            "original_filename": str,
            "storage_path": str,
            "file_size": int,
            "width": int,
            "height": int,
            "format": str
        }
    """
    try:
        data = request.get_json()
        
        query = """
            INSERT INTO images 
            (batch_id, original_filename, storage_path, file_size, width, height, format)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['batch_id'],
            data['original_filename'],
            data['storage_path'],
            data.get('file_size'),
            data.get('width'),
            data.get('height'),
            data.get('format')
        )
        
        image_id = db.execute_update(query, params)
        
        # Actualizar contador de imágenes en el lote
        update_query = """
            UPDATE batch_requests 
            SET total_images = total_images + 1 
            WHERE batch_id = %s
        """
        db.execute_update(update_query, (data['batch_id'],))
        
        return jsonify({
            'success': True,
            'image_id': image_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@images_bp.route('/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """
    GET /api/images/{image_id}
    Obtener información de una imagen
    """
    try:
        query = "SELECT * FROM images WHERE image_id = %s"
        rows = db.execute_query(query, (image_id,))
        
        if not rows:
            return jsonify({'error': 'Imagen no encontrada'}), 404
        
        image = Image.to_dict(rows[0])
        return jsonify(image), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@images_bp.route('/<int:image_id>/transformations', methods=['POST'])
def add_transformations(image_id):
    """
    POST /api/images/{image_id}/transformations
    Agregar transformaciones a una imagen
    
    Body:
        {
            "transformations": [
                {
                    "transformation_id": int,
                    "parameters": dict,
                    "execution_order": int
                }
            ]
        }
    """
    try:
        data = request.get_json()
        transformations = data.get('transformations', [])
        
        queries_with_params = []
        for t in transformations:
            query = """
                INSERT INTO image_transformations 
                (image_id, transformation_id, parameters, execution_order)
                VALUES (%s, %s, %s, %s)
            """
            params = (
                image_id,
                t['transformation_id'],
                json.dumps(t.get('parameters', {})),
                t.get('execution_order', 0)
            )
            queries_with_params.append((query, params))
        
        db.execute_transaction(queries_with_params)
        
        return jsonify({
            'success': True,
            'message': f'{len(transformations)} transformaciones agregadas'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@images_bp.route('', methods=['GET'])
def get_images():
    """
    GET /api/images?batch_id={batch_id}
    Obtener imágenes de un lote con sus tiempos de procesamiento
    """
    try:
        batch_id = request.args.get('batch_id')
        
        if not batch_id:
            return jsonify({'error': 'batch_id es requerido'}), 400
        
        query = """
            SELECT 
                i.image_id,
                i.original_filename,
                i.status,
                pr.processing_time_ms,
                pr.result_filename
            FROM images i
            LEFT JOIN processed_results pr ON i.image_id = pr.image_id
            WHERE i.batch_id = %s
            ORDER BY i.image_id
        """
        
        rows = db.execute_query(query, (batch_id,))
        
        images = []
        for row in rows:
            images.append({
                'image_id': row['image_id'],
                'original_filename': row['original_filename'],
                'status': row['status'],
                'processing_time_ms': row.get('processing_time_ms', 0),
                'result_filename': row.get('result_filename', '')
            })
        
        return jsonify(images), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@images_bp.route('/<int:image_id>/result', methods=['POST'])
def add_result(image_id):
    """
    POST /api/images/{image_id}/result
    Registrar resultado procesado
    
    Body:
        {
            "node_id": int,
            "result_filename": str,
            "storage_path": str,
            "file_size": int,
            "width": int,
            "height": int,
            "format": str,
            "processing_time_ms": int,
            "status": str,
            "error_message": str
        }
    """
    try:
        data = request.get_json()
        
        # Validación de campos requeridos
        if not data:
            return jsonify({'error': 'Body vacío'}), 400
        
        required_fields = ['node_id', 'result_filename', 'storage_path']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({'error': f'Faltan campos requeridos: {", ".join(missing_fields)}'}), 400
        
        # Validar que image_id existe
        image_check = "SELECT image_id FROM images WHERE image_id = %s"
        image_exists = db.execute_query(image_check, (image_id,))
        if not image_exists:
            return jsonify({'error': f'image_id {image_id} no existe'}), 404
        
        # Validar que node_id existe
        node_check = "SELECT node_id FROM processing_nodes WHERE node_id = %s"
        node_exists = db.execute_query(node_check, (data['node_id'],))
        if not node_exists:
            return jsonify({'error': f'node_id {data["node_id"]} no existe'}), 404
        
        query = """
            INSERT INTO processed_results 
            (image_id, node_id, result_filename, storage_path, file_size, 
             width, height, format, processing_time_ms, status, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            image_id,
            data['node_id'],
            data['result_filename'],
            data['storage_path'],
            data.get('file_size'),
            data.get('width'),
            data.get('height'),
            data.get('format'),
            data.get('processing_time_ms', 0),
            data.get('status', 'success'),
            data.get('error_message', '')
        )
        
        result_id = db.execute_update(query, params)
        
        # Actualizar contador de imágenes procesadas en el lote
        if data.get('status') == 'success':
            # Obtener batch_id de la imagen
            batch_query = "SELECT batch_id FROM images WHERE image_id = %s"
            batch_rows = db.execute_query(batch_query, (image_id,))
            if batch_rows:
                batch_id = batch_rows[0]['batch_id']
                update_query = """
                    UPDATE batch_requests 
                    SET processed_images = processed_images + 1 
                    WHERE batch_id = %s
                """
                db.execute_update(update_query, (batch_id,))
        
        return jsonify({
            'success': True,
            'result_id': result_id
        }), 201
        
    except KeyError as e:
        print(f"[IMAGES] Error: Campo faltante - {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Campo requerido faltante: {str(e)}'}), 400
    except Exception as e:
        print(f"[IMAGES] Error al registrar resultado: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@images_bp.route('/batch/<int:batch_id>', methods=['GET'])
def get_batch_images(batch_id):
    """
    GET /api/images/batch/{batch_id}
    Obtener todas las imágenes de un lote
    """
    try:
        query = "SELECT * FROM images WHERE batch_id = %s"
        rows = db.execute_query(query, (batch_id,))
        
        images = [Image.to_dict(row) for row in rows]
        return jsonify(images), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Archivo: db_service/routes/images.py
# Al final del archivo, agregar:

@images_bp.route('/<int:image_id>/processed', methods=['PUT'])
def mark_image_processed(image_id):
    """
    PUT /api/images/{image_id}/processed
    Marcar imagen como procesada (actualiza processed_at)
    """
    try:
        query = """
            UPDATE images 
            SET processed_at = CURRENT_TIMESTAMP
            WHERE image_id = %s
        """
        db.execute_update(query, (image_id,))
        
        return jsonify({
            'success': True,
            'message': 'Imagen marcada como procesada'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@images_bp.route('/batch', methods=['POST'])
def create_images_batch():
    """
    POST /api/images/batch
    Registrar múltiples imágenes con sus transformaciones en una sola llamada (OPTIMIZADO)
    
    Body:
        {
            "batch_id": int,
            "images": [
                {
                    "original_filename": str,
                    "storage_path": str,
                    "file_size": int,
                    "transformations": [
                        {
                            "name": str,
                            "parameters": dict,
                            "execution_order": int
                        }
                    ]
                }
            ]
        }
    
    Returns:
        {
            "success": True,
            "images_created": int,
            "transformations_created": int,
            "image_ids": [int]
        }
    """
    try:
        data = request.get_json()
        batch_id = data['batch_id']
        images = data['images']
        
        image_ids = []
        total_transformations = 0
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Insertar cada imagen con sus transformaciones
            for img in images:
                # 1. Insertar imagen
                img_query = """
                    INSERT INTO images 
                    (batch_id, original_filename, storage_path, file_size)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(img_query, (
                    batch_id,
                    img['original_filename'],
                    img['storage_path'],
                    img.get('file_size')
                ))
                
                image_id = cursor.lastrowid
                image_ids.append(image_id)
                
                # 2. Insertar transformaciones de esta imagen
                transformations = img.get('transformations', [])
                for trans in transformations:
                    # Buscar transformation_id por nombre
                    trans_id_query = "SELECT transformation_id FROM transformations WHERE name = %s"
                    cursor.execute(trans_id_query, (trans['name'],))
                    trans_result = cursor.fetchone()
                    
                    if trans_result:
                        trans_id = trans_result[0]
                        
                        # Insertar en image_transformations
                        it_query = """
                            INSERT INTO image_transformations
                            (image_id, transformation_id, parameters, execution_order, status)
                            VALUES (%s, %s, %s, %s, 'pending')
                        """
                        cursor.execute(it_query, (
                            image_id,
                            trans_id,
                            json.dumps(trans.get('parameters', {})),
                            trans.get('execution_order', 1)
                        ))
                        total_transformations += 1
            
            # 3. Actualizar contador en batch (sin usar +=)
            # 3. Actualizar contador en batch_requests (sin usar +=)
            cursor.execute("SELECT total_images FROM batch_requests WHERE batch_id = %s", (batch_id,))
            current_total = cursor.fetchone()
            new_total = (current_total[0] if current_total else 0) + len(images)
            
            cursor.execute(
                "UPDATE batch_requests SET total_images = %s WHERE batch_id = %s",
                (new_total, batch_id)
            )
            
            # Commit de toda la transacción
            conn.commit()
            
            return jsonify({
                'success': True,
                'images_created': len(images),
                'transformations_created': total_transformations,
                'image_ids': image_ids
            }), 201
            
        except Exception as e:
            conn.rollback()
            print(f"[DB] Error en batch insert: {e}")
            import traceback
            traceback.print_exc()
            raise e
            
        finally:
            cursor.close()
            conn.close()
        
    except Exception as e:
        print(f"[API] Error en create_images_batch: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500