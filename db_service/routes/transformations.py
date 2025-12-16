# Archivo: db_service/routes/transformations.py
# ENDPOINTS REST PARA TRANSFORMACIONES DISPONIBLES

from flask import Blueprint, jsonify
from database import Database
from models import Transformation

transformations_bp = Blueprint('transformations', __name__)
db = Database()

@transformations_bp.route('', methods=['GET'])
def get_all_transformations():
    """
    GET /api/transformations
    Obtener todas las transformaciones disponibles
    """
    try:
        query = "SELECT * FROM transformations WHERE is_active = TRUE"
        rows = db.execute_query(query)
        
        transformations = [Transformation.to_dict(row) for row in rows]
        return jsonify(transformations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transformations_bp.route('/<int:transformation_id>', methods=['GET'])
def get_transformation(transformation_id):
    """
    GET /api/transformations/{transformation_id}
    Obtener una transformación específica
    """
    try:
        query = "SELECT * FROM transformations WHERE transformation_id = %s"
        rows = db.execute_query(query, (transformation_id,))
        
        if not rows:
            return jsonify({'error': 'Transformación no encontrada'}), 404
        
        transformation = Transformation.to_dict(rows[0])
        return jsonify(transformation), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transformations_bp.route('/by-name/<string:name>', methods=['GET'])
def get_transformation_by_name(name):
    """
    GET /api/transformations/by-name/{name}
    Obtener transformación por nombre
    """
    try:
        query = "SELECT * FROM transformations WHERE name = %s AND is_active = TRUE"
        rows = db.execute_query(query, (name,))
        
        if not rows:
            return jsonify({'error': 'Transformación no encontrada'}), 404
        
        transformation = Transformation.to_dict(rows[0])
        return jsonify(transformation), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500