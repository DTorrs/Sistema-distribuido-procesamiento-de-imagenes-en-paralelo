# Archivo: db_service/routes/image_transformations.py
# ENDPOINTS PARA TRANSFORMACIONES APLICADAS A IMÁGENES

from flask import Blueprint, request, jsonify
import json

image_transformations_bp = Blueprint('image_transformations', __name__)

# Importar Database
from database import Database
db = Database()

@image_transformations_bp.route('', methods=['POST'])
def add_transformation():
    """
    POST /api/image-transformations
    Agregar transformación a una imagen
    
    Body:
        {
            "image_id": int,
            "transformation_name": str,
            "parameters": dict,
            "execution_order": int
        }
    """
    try:
        data = request.get_json()
        
        image_id = data.get('image_id')
        transformation_name = data.get('transformation_name')
        parameters = data.get('parameters', {})
        execution_order = data.get('execution_order', 1)
        
        if not image_id or not transformation_name:
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        print(f"[IMAGE_TRANSFORMATIONS] Registrando {transformation_name} para imagen {image_id}")
        
        # Convertir parameters a JSON string
        if isinstance(parameters, dict):
            parameters_json = json.dumps(parameters)
        else:
            parameters_json = str(parameters)
        
        # ⭐ BUSCAR transformation_id A PARTIR DEL NOMBRE
        lookup_query = """
            SELECT transformation_id 
            FROM transformations 
            WHERE name = %s AND is_active = 1
        """
        
        rows = db.execute_query(lookup_query, (transformation_name,))
        
        if not rows:
            print(f"[IMAGE_TRANSFORMATIONS] ✗ Transformación '{transformation_name}' no encontrada")
            return jsonify({'error': f'Transformación {transformation_name} no existe'}), 400
        
        transformation_id = rows[0]['transformation_id']
        print(f"[IMAGE_TRANSFORMATIONS] → Mapeado: {transformation_name} → ID {transformation_id}")
        
        # INSERCIÓN CON transformation_id
        query = """
            INSERT INTO image_transformations 
            (image_id, transformation_id, parameters, execution_order)
            VALUES (%s, %s, %s, %s)
        """
        
        result = db.execute_update(
            query,
            (image_id, transformation_id, parameters_json, execution_order)
        )
        
        if result:
            print(f"[IMAGE_TRANSFORMATIONS] ✓ Transformación registrada: ID {result}")
            return jsonify({
                'success': True,
                'image_transformation_id': result
            }), 201
        else:
            print(f"[IMAGE_TRANSFORMATIONS] ✗ Error al insertar")
            return jsonify({'error': 'Error al registrar transformación'}), 500
            
    except Exception as e:
        print(f"[IMAGE_TRANSFORMATIONS] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@image_transformations_bp.route('/image/<int:image_id>', methods=['GET'])
def get_image_transformations(image_id):
    """
    GET /api/image-transformations/image/{image_id}
    Obtener todas las transformaciones de una imagen
    """
    try:
        query = """
            SELECT 
                image_transformation_id,
                image_id,
                transformation_name,
                parameters,
                execution_order,
                created_at
            FROM image_transformations
            WHERE image_id = %s
            ORDER BY execution_order
        """
        
        rows = db.execute_query(query, (image_id,))
        
        transformations = []
        for row in rows:
            # Parsear parameters
            params = {}
            if len(row) > 3 and row[3]:
                try:
                    params = json.loads(row[3])
                except:
                    params = {}
            
            transformations.append({
                'image_transformation_id': row[0],
                'image_id': row[1],
                'transformation_name': row[2],
                'parameters': params,
                'execution_order': row[4],
                'created_at': str(row[5]) if len(row) > 5 and row[5] else None
            })
        
        return jsonify(transformations), 200
        
    except Exception as e:
        print(f"[IMAGE_TRANSFORMATIONS] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@image_transformations_bp.route('/batch/<int:batch_id>', methods=['GET'])
def get_batch_transformations(batch_id):
    """
    GET /api/image-transformations/batch/{batch_id}
    Obtener todas las transformaciones de un lote
    """
    try:
        query = """
            SELECT 
                it.image_transformation_id,
                it.image_id,
                it.transformation_name,
                it.parameters,
                it.execution_order,
                i.original_filename
            FROM image_transformations it
            INNER JOIN images i ON it.image_id = i.image_id
            WHERE i.batch_id = %s
            ORDER BY i.image_id, it.execution_order
        """
        
        rows = db.execute_query(query, (batch_id,))
        
        transformations = []
        for row in rows:
            # Parsear parameters
            params = {}
            if len(row) > 3 and row[3]:
                try:
                    params = json.loads(row[3])
                except:
                    params = {}
            
            transformations.append({
                'image_transformation_id': row[0],
                'image_id': row[1],
                'transformation_name': row[2],
                'parameters': params,
                'execution_order': row[4],
                'filename': row[5] if len(row) > 5 else None
            })
        
        return jsonify(transformations), 200
        
    except Exception as e:
        print(f"[IMAGE_TRANSFORMATIONS] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500