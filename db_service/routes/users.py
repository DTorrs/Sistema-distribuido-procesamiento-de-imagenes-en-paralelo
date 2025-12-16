# Archivo: db_service/routes/users.py
# Endpoints REST para gestión de usuarios (sin JWT, simple)

from flask import Blueprint, request, jsonify
from database import Database
import bcrypt

users_bp = Blueprint('users', __name__)
db = Database()

@users_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/users/register
    Registrar nuevo usuario
    
    Body:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "first_name": "string" (opcional),
            "last_name": "string" (opcional)
        }
    """
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({'error': 'username, password y email son requeridos'}), 400
        
        if len(data['username']) < 3:
            return jsonify({'error': 'username debe tener al menos 3 caracteres'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'error': 'password debe tener al menos 6 caracteres'}), 400
        
        # Verificar si ya existe
        check_query = "SELECT user_id FROM users WHERE username = %s OR email = %s"
        existing = db.execute_query(check_query, (data['username'], data['email']))
        
        if existing:
            return jsonify({'error': 'Usuario o email ya existe'}), 409
        
        # Hashear contraseña con bcrypt
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insertar usuario
        insert_query = """
            INSERT INTO users (username, email, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            data['username'],
            data['email'],
            password_hash,
            data.get('first_name'),
            data.get('last_name')
        )
        
        user_id = db.execute_update(insert_query, params)
        
        print(f"[USERS] Usuario registrado: {data['username']} (ID: {user_id})")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'Usuario registrado exitosamente'
        }), 201
        
    except Exception as e:
        print(f"[USERS] Error en registro: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@users_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/users/login
    Verificar credenciales de usuario
    
    Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Response:
        {
            "success": true,
            "user_id": 1,
            "username": "usuario",
            "email": "email@example.com"
        }
    """
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'username y password son requeridos'}), 400
        
        # Buscar usuario
        query = """
            SELECT user_id, username, email, password_hash, is_active 
            FROM users 
            WHERE username = %s
        """
        rows = db.execute_query(query, (data['username'],))
        
        if not rows:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        user = rows[0]
        
        # Verificar si está activo
        if not user['is_active']:
            return jsonify({'error': 'Usuario desactivado'}), 403
        
        # Verificar contraseña
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # Actualizar last_login
        update_query = "UPDATE users SET last_login = NOW() WHERE user_id = %s"
        db.execute_update(update_query, (user['user_id'],))
        
        print(f"[USERS] Login exitoso: {user['username']} (ID: {user['user_id']})")
        
        return jsonify({
            'success': True,
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email']
        }), 200
        
    except Exception as e:
        print(f"[USERS] Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    GET /api/users/{user_id}
    Obtener información de un usuario
    """
    try:
        query = """
            SELECT user_id, username, email, first_name, last_name, created_at, last_login
            FROM users 
            WHERE user_id = %s
        """
        rows = db.execute_query(query, (user_id,))
        
        if not rows:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        user = rows[0]
        return jsonify({
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'created_at': user['created_at'].isoformat() if user['created_at'] else None,
            'last_login': user['last_login'].isoformat() if user['last_login'] else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500