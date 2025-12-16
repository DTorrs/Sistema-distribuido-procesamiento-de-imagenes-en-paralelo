# Archivo: db_service/routes/nodes.py
# ENDPOINTS REST PARA GESTIÓN DE NODOS

from flask import Blueprint, request, jsonify
from database import Database
from models import ProcessingNode

nodes_bp = Blueprint('nodes', __name__)
db = Database()

@nodes_bp.route('', methods=['GET'])
def get_all_nodes():
    """
    GET /api/nodes
    Obtener todos los nodos registrados
    """
    try:
        query = "SELECT * FROM processing_nodes ORDER BY node_id"
        rows = db.execute_query(query)
        
        nodes = [ProcessingNode.to_dict(row) for row in rows]
        return jsonify(nodes), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nodes_bp.route('/active', methods=['GET'])
def get_active_nodes():
    """
    GET /api/nodes/active
    Obtener solo nodos activos
    """
    try:
        query = "SELECT * FROM processing_nodes WHERE status = 'active'"
        rows = db.execute_query(query)
        
        nodes = [ProcessingNode.to_dict(row) for row in rows]
        return jsonify(nodes), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nodes_bp.route('/<int:node_id>/heartbeat', methods=['PUT'])
def update_heartbeat(node_id):
    """
    PUT /api/nodes/{node_id}/heartbeat
    Actualizar heartbeat de un nodo (con auto-registro)
    
    Body (opcional):
        {
            "ip_address": str,
            "port": int,
            "status": str,
            "cpu_cores": int,
            "ram_gb": int
        }
    """
    try:
        data = request.get_json() if request.is_json else {}
        
        print(f"[HEARTBEAT] PUT recibido de nodo_id={node_id}")
        
        # ⭐ VERIFICAR SI EL NODO EXISTE
        check_query = "SELECT node_id FROM processing_nodes WHERE node_id = %s"
        result = db.execute_query(check_query, (node_id,))
        
        if not result or len(result) == 0:
            # ⭐ NODO NO EXISTE - CREAR AUTOMÁTICAMENTE
            print(f"[HEARTBEAT] Nodo {node_id} no existe, creando...")
            
            ip_address = data.get('ip_address', 'localhost')
            port = data.get('port', 50050 + node_id)
            cpu_cores = data.get('cpu_cores')
            ram_gb = data.get('ram_gb')
            
            insert_query = """
                INSERT INTO processing_nodes 
                (node_id, node_name, ip_address, port, cpu_cores, ram_gb, status, last_heartbeat)
                VALUES (%s, %s, %s, %s, %s, %s, 'active', NOW())
            """
            db.execute_update(
                insert_query,
                (node_id, f'Node-{node_id}', ip_address, port, cpu_cores, ram_gb)
            )
            
            print(f"[HEARTBEAT] ✓ Nodo {node_id} creado exitosamente")
            
            return jsonify({
                'success': True,
                'message': 'Nodo registrado y heartbeat actualizado'
            }), 201
        
        else:
            # ⭐ NODO EXISTE - ACTUALIZAR
            print(f"[HEARTBEAT] Nodo {node_id} existe, actualizando heartbeat...")
            
            updates = ["last_heartbeat = NOW()", "status = 'active'"]
            params = []
            
            if 'cpu_cores' in data:
                updates.append("cpu_cores = %s")
                params.append(data['cpu_cores'])
            
            if 'ram_gb' in data:
                updates.append("ram_gb = %s")
                params.append(data['ram_gb'])
            
            if 'current_load' in data:
                updates.append("current_load = %s")
                params.append(data['current_load'])
            
            if 'ip_address' in data:
                updates.append("ip_address = %s")
                params.append(data['ip_address'])
            
            if 'port' in data:
                updates.append("port = %s")
                params.append(data['port'])
            
            params.append(node_id)
            
            query = f"UPDATE processing_nodes SET {', '.join(updates)} WHERE node_id = %s"
            db.execute_update(query, tuple(params))
            
            print(f"[HEARTBEAT] ✓ Nodo {node_id} actualizado")
            
            return jsonify({
                'success': True,
                'message': 'Heartbeat actualizado'
            }), 200
        
    except Exception as e:
        print(f"[HEARTBEAT] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@nodes_bp.route('', methods=['POST'])
def register_node():
    """
    POST /api/nodes
    Registrar un nuevo nodo manualmente
    
    Body:
        {
            "node_name": str,
            "ip_address": str,
            "port": int,
            "cpu_cores": int,
            "ram_gb": int
        }
    """
    try:
        data = request.get_json()
        
        query = """
            INSERT INTO processing_nodes 
            (node_name, ip_address, port, cpu_cores, ram_gb, status)
            VALUES (%s, %s, %s, %s, %s, 'active')
        """
        params = (
            data['node_name'],
            data['ip_address'],
            data['port'],
            data.get('cpu_cores'),
            data.get('ram_gb')
        )
        
        node_id = db.execute_update(query, params)
        
        return jsonify({
            'success': True,
            'node_id': node_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500