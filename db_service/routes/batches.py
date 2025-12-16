# Archivo: db_service/routes/batches.py
# ENDPOINTS REST PARA GESTIÓN DE LOTES

from flask import Blueprint, request, jsonify
from database import Database
from models import BatchRequest

batches_bp = Blueprint('batches', __name__)
db = Database()

@batches_bp.route('', methods=['POST'])
def create_batch():
    """
    POST /api/batches
    Crear un nuevo lote de procesamiento
    
    Body:
        {
            "user_id": int,
            "batch_name": str,
            "output_format": str (opcional),
            "compression_type": str (opcional)
        }
    """
    try:
        data = request.get_json()
        
        # Validación básica
        if not data.get('user_id'):
            return jsonify({'error': 'user_id es requerido'}), 400
        
        query = """
            INSERT INTO batch_requests 
            (user_id, batch_name, output_format, compression_type)
            VALUES (%s, %s, %s, %s)
        """
        params = (
            data['user_id'],
            data.get('batch_name', ''),
            data.get('output_format', 'jpg'),
            data.get('compression_type', 'zip')
        )
        
        batch_id = db.execute_update(query, params)
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'message': 'Lote creado exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batches_bp.route('/<int:batch_id>', methods=['GET'])
def get_batch(batch_id):
    """
    GET /api/batches/{batch_id}
    Obtener información de un lote específico
    """
    try:
        query = "SELECT * FROM batch_requests WHERE batch_id = %s"
        rows = db.execute_query(query, (batch_id,))
        
        if not rows:
            return jsonify({'error': 'Lote no encontrado'}), 404
        
        batch = BatchRequest.to_dict(rows[0])
        return jsonify(batch), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batches_bp.route('/<int:batch_id>/status', methods=['PUT'])
def update_batch_status(batch_id):
    """
    PUT /api/batches/{batch_id}/status
    Actualizar estado de un lote
    
    Body:
        {
            "status": str ("pending"|"processing"|"completed"|"failed"),
            "processed_images": int (opcional),
            "started_at": datetime (opcional),
            "completed_at": datetime (opcional)
        }
    """
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'status es requerido'}), 400
        
        # Construir query dinámicamente
        updates = ["status = %s"]
        params = [status]
        
        if 'processed_images' in data:
            updates.append("processed_images = %s")
            params.append(data['processed_images'])
        
        if status == 'processing' and 'started_at' not in data:
            updates.append("started_at = NOW()")
        elif 'started_at' in data:
            updates.append("started_at = %s")
            params.append(data['started_at'])
        
        if status in ['completed', 'failed'] and 'completed_at' not in data:
            updates.append("completed_at = NOW()")
        elif 'completed_at' in data:
            updates.append("completed_at = %s")
            params.append(data['completed_at'])
        
        params.append(batch_id)
        
        query = f"UPDATE batch_requests SET {', '.join(updates)} WHERE batch_id = %s"
        db.execute_update(query, tuple(params))
        
        return jsonify({
            'success': True,
            'message': 'Estado actualizado'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batches_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_batches(user_id):
    """
    GET /api/batches/user/{user_id}
    Obtener todos los lotes de un usuario
    """
    try:
        query = """
            SELECT * FROM batch_requests 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """
        rows = db.execute_query(query, (user_id,))
        
        batches = [BatchRequest.to_dict(row) for row in rows]
        return jsonify(batches), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500