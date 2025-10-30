from flask import Blueprint, request, current_app
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.db import get_conn
from utils.helpers import json_response, validate_required_fields

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    payload = request.get_json() or {}
    missing = validate_required_fields(payload, ['name', 'email', 'password'])
    if missing:
        return json_response('error', f'Missing fields: {missing}', {}, 400)

    name = payload['name'].strip()
    email = payload['email'].strip().lower()
    password = payload['password']
    mobile = payload.get('mobile', '')
    preferred_language = payload.get('preferred_language', 'en')

    # Hash password
    pw_hash = generate_password_hash(password).decode('utf-8')

    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        # check unique email
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            return json_response('error', 'Email already registered', {}, 400)

        cursor.execute(
            'INSERT INTO users (name, email, mobile, password, preferred_language) VALUES (%s, %s, %s, %s, %s)',
            (name, email, mobile, pw_hash, preferred_language)
        )
        conn.commit()
        return json_response('success', 'User registered', {}, 201)
    except Exception as e:
        current_app.logger.exception('Register error')
        return json_response('error', 'Registration failed', {'error': str(e)}, 500)
    finally:
        cursor.close()
        conn.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    payload = request.get_json() or {}
    missing = validate_required_fields(payload, ['email', 'password'])
    if missing:
        return json_response('error', f'Missing fields: {missing}', {}, 400)

    email = payload['email'].strip().lower()
    password = payload['password']

    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, password, name FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        if not user:
            return json_response('error', 'Invalid credentials', {}, 401)

        hashed = user['password']
        if not check_password_hash(hashed, password):
            return json_response('error', 'Invalid credentials', {}, 401)

        access_token = create_access_token(identity={'id': user['id'], 'email': email})
        return json_response('success', 'Login successful', {'access_token': access_token})
    except Exception as e:
        current_app.logger.exception('Login error')
        return json_response('error', 'Login failed', {'error': str(e)}, 500)
    finally:
        cursor.close()
        conn.close()


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    ident = get_jwt_identity()
    user_id = ident.get('id')
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, name, email, mobile, preferred_language FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        if not user:
            return json_response('error', 'User not found', {}, 404)
        return json_response('success', 'Profile fetched', {'user': user})
    except Exception as e:
        current_app.logger.exception('Profile error')
        return json_response('error', 'Failed to fetch profile', {'error': str(e)}, 500)
    finally:
        cursor.close()
        conn.close()
