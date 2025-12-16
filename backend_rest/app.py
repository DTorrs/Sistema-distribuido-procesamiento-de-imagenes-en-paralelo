# Archivo: backend_rest/app.py
# SERVIDOR REST API - Capa intermedia entre cliente y SOAP

from flask import Flask, request, jsonify
from flask_cors import CORS
from soap_client import SOAPClient
from config import Config
import traceback
import requests  # ⭐ AGREGAR ESTA LÍNEA


app = Flask(__name__)
CORS(app)  # Permitir requests desde cualquier origen

# Cliente SOAP global
soap_client = SOAPClient(Config.SOAP_URL)

# ═══════════════════════════════════════════════════════
# ENDPOINT: Health Check
# ═══════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health():
    """Verificar que el servicio está activo"""
    return jsonify({
        'status': 'healthy',
        'service': 'Backend REST API',
        'version': '1.0.0'
    }), 200

# ═══════════════════════════════════════════════════════
# ENDPOINT: Registro de Usuario
# ═══════════════════════════════════════════════════════

@app.route('/api/register', methods=['POST'])
def register():
    """
    POST /api/register
    
    Body (JSON):
    {
        "username": "string",
        "password": "string",
        "email": "string",
        "first_name": "string" (opcional),
        "last_name": "string" (opcional)
    }
    
    Response:
    {
        "success": true,
        "user_id": 1,
        "message": "Usuario registrado exitosamente"
    }
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({'error': 'Body JSON requerido'}), 400
        
        if not data.get('username'):
            return jsonify({'error': 'username es requerido'}), 400
        
        if not data.get('password'):
            return jsonify({'error': 'password es requerido'}), 400
        
        if not data.get('email'):
            return jsonify({'error': 'email es requerido'}), 400
        
        print(f"[BACKEND REST] Registrando usuario: {data['username']}")
        
        # Llamar al servidor SOAP
        success, result = soap_client.register(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        if success:
            print(f"[BACKEND REST] Usuario registrado exitosamente: ID={result['user_id']}")
            return jsonify(result), 201
        else:
            print(f"[BACKEND REST] Error al registrar: {result.get('message')}")
            return jsonify(result), 400
            
    except Exception as e:
        print(f"[BACKEND REST] Error en registro: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500

# ═══════════════════════════════════════════════════════
# ENDPOINT: Login
# ═══════════════════════════════════════════════════════

@app.route('/api/login', methods=['POST'])
def login():
    """
    POST /api/login
    
    Body (JSON):
    {
        "username": "string",
        "password": "string"
    }
    
    Response:
    {
        "success": true,
        "token": "session-token-uuid",
        "user_id": 1,
        "message": "Login exitoso"
    }
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({'error': 'Body JSON requerido'}), 400
        
        if not data.get('username'):
            return jsonify({'error': 'username es requerido'}), 400
        
        if not data.get('password'):
            return jsonify({'error': 'password es requerido'}), 400
        
        print(f"[BACKEND REST] Login usuario: {data['username']}")
        
        # Llamar al servidor SOAP
        success, result = soap_client.login(
            username=data['username'],
            password=data['password']
        )
        
        if success:
            print(f"[BACKEND REST] Login exitoso: {data['username']}")
            return jsonify(result), 200
        else:
            print(f"[BACKEND REST] Login fallido: {result.get('message')}")
            return jsonify(result), 401
            
    except Exception as e:
        print(f"[BACKEND REST] Error en login: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500

# ═══════════════════════════════════════════════════════
# ENDPOINT: Logout
# ═══════════════════════════════════════════════════════

@app.route('/api/logout', methods=['POST'])
def logout():
    """
    POST /api/logout
    
    Body (JSON):
    {
        "token": "session-token-uuid"
    }
    
    Response:
    {
        "success": true,
        "message": "Logout exitoso"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('token'):
            return jsonify({'error': 'token es requerido'}), 400
        
        print(f"[BACKEND REST] Logout token: {data['token'][:10]}...")
        
        # Llamar al servidor SOAP
        success, result = soap_client.logout(token=data['token'])
        
        return jsonify(result), 200 if success else 400
            
    except Exception as e:
        print(f"[BACKEND REST] Error en logout: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500

# ═══════════════════════════════════════════════════════
# ENDPOINT: Procesar Lote de Imágenes
# ═══════════════════════════════════════════════════════

@app.route('/api/process-batch', methods=['POST'])
def process_batch():
    """
    POST /api/process-batch
    
    Body (JSON):
    {
        "token": "session-token",
        "batch_name": "Mi Lote",
        "images": [
            {
                "filename": "imagen1.jpg",
                "image_data_base64": "base64...",
                "transformations": [
                    {
                        "transformation_id": 1,
                        "name": "grayscale",
                        "parameters": {}
                    }
                ]
            }
        ]
    }
    
    Response:
    {
        "success": true,
        "batch_id": 1,
        "total_images": 1,
        "processed_images": 1,
        "failed_images": 0,
        "processing_time_ms": 1500
    }
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data:
            return jsonify({'error': 'Body JSON requerido'}), 400
        
        if not data.get('token'):
            return jsonify({'error': 'token es requerido'}), 400
        
        if not data.get('batch_name'):
            return jsonify({'error': 'batch_name es requerido'}), 400
        
        if not data.get('images') or not isinstance(data['images'], list):
            return jsonify({'error': 'images debe ser un array'}), 400
        
        print(f"[BACKEND REST] Procesando lote: {data['batch_name']}")
        print(f"[BACKEND REST] Número de imágenes: {len(data['images'])}")
        
        # Llamar al servidor SOAP
        success, result = soap_client.process_batch(
            token=data['token'],
            batch_name=data['batch_name'],
            images=data['images']
        )
        
        if success:
            print(f"[BACKEND REST] Lote procesado exitosamente")
            return jsonify(result), 200
        else:
            print(f"[BACKEND REST] Error procesando lote")
            return jsonify(result), 400
            
    except Exception as e:
        print(f"[BACKEND REST] Error en process_batch: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500


# ═══════════════════════════════════════════════════════
# ENDPOINT: Métricas de Nodos
# ═══════════════════════════════════════════════════════

@app.route('/api/metrics/nodes', methods=['GET'])
def get_nodes_metrics():
    """
    GET /api/metrics/nodes
    Obtener métricas de todos los nodos (vía SOAP)
    """
    try:
        print(f"[BACKEND REST] Solicitando métricas de nodos vía SOAP")
        
        success, nodes = soap_client.get_nodes_metrics()
        
        if success:
            return jsonify(nodes), 200
        else:
            return jsonify({'error': 'Error obteniendo métricas'}), 500
            
    except Exception as e:
        print(f"[BACKEND REST] Error en métricas: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/metrics/batches/<int:batch_id>', methods=['GET'])
def get_batch_metrics(batch_id):
    """
    GET /api/metrics/batches/{batch_id}
    Obtener métricas de un lote procesado (vía SOAP)
    """
    try:
        print(f"[BACKEND REST] Solicitando métricas de batch {batch_id} vía SOAP")
        
        success, metrics = soap_client.get_batch_metrics(batch_id)
        
        if success:
            return jsonify(metrics), 200
        else:
            return jsonify({'error': 'Lote no encontrado'}), 404
            
    except Exception as e:
        print(f"[BACKEND REST] Error en métricas de lote: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500

# ═══════════════════════════════════════════════════════
# MANEJO DE ERRORES
# ═══════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

# ═══════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════

def main():
    print("\n" + "="*60)
    print("BACKEND REST API INICIADO")
    print(f"Puerto: {Config.PORT}")
    print(f"SOAP Server: {Config.SOAP_URL}")
    print("="*60 + "\n")
    
    print("Endpoints disponibles:")
    print("  GET  /health")
    print("  POST /api/register")
    print("  POST /api/login")
    print("  POST /api/logout")
    print("  POST /api/process-batch")
    print("\n" + "="*60 + "\n")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )

if __name__ == '__main__':
    main()