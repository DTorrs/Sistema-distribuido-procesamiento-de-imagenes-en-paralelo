from flask import Blueprint

def register_routes(app):
    """Registrar todos los blueprints de rutas"""
    from .users import users_bp
    from .batches import batches_bp
    from .images import images_bp
    from .nodes import nodes_bp
    from .transformations import transformations_bp
    from .logs import logs_bp
    from .image_transformations import image_transformations_bp
    from .downloads import downloads_bp  # ← NUEVO
    
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(batches_bp, url_prefix='/api/batches')
    app.register_blueprint(images_bp, url_prefix='/api/images')
    app.register_blueprint(nodes_bp, url_prefix='/api/nodes')
    app.register_blueprint(transformations_bp, url_prefix='/api/transformations')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    app.register_blueprint(image_transformations_bp, url_prefix='/api/image-transformations')
    app.register_blueprint(downloads_bp, url_prefix='/api/batches')  # ← NUEVO
    
    print("[API] Rutas registradas exitosamente")