# Archivo: db_service/routes/logs.py
# ENDPOINTS REST PARA LOGS

from flask import Blueprint, request, jsonify
from database import Database

logs_bp = Blueprint('logs', __name__)
db = Database()

@logs_bp.route('', methods=['POST'])
def create_log():
    """
    POST /api/logs
    Crear un nuevo log
    
    Body:
        {
            "batch_id": int (opcional),
            "image_id": int (opcional),
            "node_id": int (opcional),
            "log_level": str ("info"|"warning"|"error"|"debug"),
            "message": str
        }
    """
    try:
        data = request.get_json()
        
        # Validación básica
        if not data or not data.get('message'):
            return jsonify({'error': 'message es requerido'}), 400
        
        # Validar que node_id existe si se proporciona
        if data.get('node_id'):
            check_query = "SELECT node_id FROM processing_nodes WHERE node_id = %s"
            node_exists = db.execute_query(check_query, (data.get('node_id'),))
            if not node_exists:
                print(f"[LOGS] ⚠️ node_id {data.get('node_id')} no existe, guardando como NULL")
                data['node_id'] = None
        
        # Validar que batch_id existe si se proporciona
        if data.get('batch_id'):
            check_query = "SELECT batch_id FROM batch_requests WHERE batch_id = %s"
            batch_exists = db.execute_query(check_query, (data.get('batch_id'),))
            if not batch_exists:
                print(f"[LOGS] ⚠️ batch_id {data.get('batch_id')} no existe, guardando como NULL")
                data['batch_id'] = None
        
        # Validar que image_id existe si se proporciona
        if data.get('image_id'):
            check_query = "SELECT image_id FROM images WHERE image_id = %s"
            image_exists = db.execute_query(check_query, (data.get('image_id'),))
            if not image_exists:
                print(f"[LOGS] ⚠️ image_id {data.get('image_id')} no existe, guardando como NULL")
                data['image_id'] = None
        
        query = """
            INSERT INTO execution_logs 
            (node_id, batch_id, image_id, log_level, message)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            data.get('node_id'),
            data.get('batch_id'),
            data.get('image_id'),
            data.get('log_level', 'info'),
            data['message']
        )
        
        log_id = db.execute_update(query, params)
        
        return jsonify({
            'success': True,
            'log_id': log_id
        }), 201
        
    except Exception as e:
        print(f"[LOGS] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/batch/<int:batch_id>', methods=['GET'])
def get_batch_logs(batch_id):
    """
    GET /api/logs/batch/{batch_id}
    Obtener logs de un lote
    """
    try:
        query = """
            SELECT * FROM execution_logs 
            WHERE batch_id = %s 
            ORDER BY timestamp DESC
        """
        rows = db.execute_query(query, (batch_id,))
        
        logs = []
        for row in rows:
            logs.append({
                'log_id': row['log_id'],
                'node_id': row['node_id'],
                'batch_id': row['batch_id'],
                'image_id': row['image_id'],
                'log_level': row['log_level'],
                'message': row['message'],
                'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None
            })
        
        return jsonify(logs), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/image/<int:image_id>', methods=['GET'])
def get_image_logs(image_id):
    """
    GET /api/logs/image/{image_id}
    Obtener logs de una imagen
    """
    try:
        query = """
            SELECT * FROM execution_logs 
            WHERE image_id = %s 
            ORDER BY timestamp DESC
        """
        rows = db.execute_query(query, (image_id,))
        
        logs = []
        for row in rows:
            logs.append({
                'log_id': row['log_id'],
                'node_id': row['node_id'],
                'batch_id': row['batch_id'],
                'image_id': row['image_id'],
                'log_level': row['log_level'],
                'message': row['message'],
                'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None
            })
        
        return jsonify(logs), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/node/<int:node_id>', methods=['GET'])
def get_node_logs(node_id):
    """
    GET /api/logs/node/{node_id}
    Obtener logs de un nodo
    """
    try:
        query = """
            SELECT * FROM execution_logs 
            WHERE node_id = %s 
            ORDER BY timestamp DESC
            LIMIT 100
        """
        rows = db.execute_query(query, (node_id,))
        
        logs = []
        for row in rows:
            logs.append({
                'log_id': row['log_id'],
                'node_id': row['node_id'],
                'batch_id': row['batch_id'],
                'image_id': row['image_id'],
                'log_level': row['log_level'],
                'message': row['message'],
                'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None
            })
        
        return jsonify(logs), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/recent', methods=['GET'])
def get_recent_logs():
    """
    GET /api/logs/recent?limit=50
    Obtener logs recientes
    """
    try:
        limit = int(request.args.get('limit', 50))
        if limit > 500:
            limit = 500
        
        query = """
            SELECT * FROM execution_logs 
            ORDER BY timestamp DESC
            LIMIT %s
        """
        rows = db.execute_query(query, (limit,))
        
        logs = []
        for row in rows:
            logs.append({
                'log_id': row['log_id'],
                'node_id': row['node_id'],
                'batch_id': row['batch_id'],
                'image_id': row['image_id'],
                'log_level': row['log_level'],
                'message': row['message'],
                'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None
            })
        
        return jsonify(logs), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500