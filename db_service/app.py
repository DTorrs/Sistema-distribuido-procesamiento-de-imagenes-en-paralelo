# Archivo: db_service/app.py
# SERVIDOR REST PRINCIPAL PARA LA BASE DE DATOS

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes import register_routes
from database import Database

def create_app():
    """
    FACTORY PARA CREAR LA APLICACIÓN FLASK
    
    Returns:
        app: Instancia configurada de Flask
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Habilitar CORS para permitir requests desde el servidor SOAP
    CORS(app)
    
    # Registrar todas las rutas ###############################################################################################
    register_routes(app)
    #############################################################################################################################
    # Ruta de health check
    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint para verificar que el servicio está activo"""
        return jsonify({
            'status': 'healthy',
            'service': 'Image Processing DB Service'
        }), 200
    
    # Ruta de información
    @app.route('/', methods=['GET'])
    def index():
        """Información básica del servicio"""
        return jsonify({
            'service': 'Image Processing Database REST API',
            'version': '1.0.0',
            'endpoints': {
                'batches': '/api/batches',
                'images': '/api/images',
                'nodes': '/api/nodes',
                'transformations': '/api/transformations'
            }
        }), 200
    
    # Manejador de errores 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint no encontrado'}), 404
    
    # Manejador de errores 500
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    return app

def main():
    """
    FUNCIÓN PRINCIPAL: Inicia el servidor REST
    """
    # Inicializar conexión a la base de datos
    try:
        db = Database()
        print("[REST API] Conexión a base de datos inicializada")
    except Exception as e:
        print(f"[REST API] ERROR: No se pudo conectar a la base de datos: {e}")
        return
    
    # Crear aplicación Flask
    app = create_app()
    
    # Iniciar servidor
    print(f"\n{'='*60}")
    print(f"REST API INICIADA")
    print(f"Host: {Config.REST_HOST}:{Config.REST_PORT}")
    print(f"Base de datos: {Config.DB_NAME}@{Config.DB_HOST}")
    print(f"{'='*60}\n")
    

#escuchando el puerto 5000
    app.run(
        host=Config.REST_HOST,
        port=Config.REST_PORT,
        debug=Config.DEBUG
    )

if __name__ == '__main__':
    main()