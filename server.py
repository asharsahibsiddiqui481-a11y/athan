import json
import os
import re
import secrets

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

SPECIAL_CHARS = r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~/]'


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


# ── Pages ──────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/quran.html')
@app.route('/quran')
def quran():
    return send_from_directory('public', 'quran.html')


# ── Accounts ───────────────────────────────────────────────────
@app.post('/api/register')
def register():
    body = request.get_json() or {}
    username = (body.get('username') or '').strip().lower()
    password = body.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400
    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': 'Username must be 3–20 characters.'}), 400
    if not re.fullmatch(r'[a-z0-9_.]+', username):
        return jsonify({'error': 'Username may only contain letters, numbers, underscores, and periods.'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters.'}), 400
    if not re.search(r'[A-Z]', password):
        return jsonify({'error': 'Password must contain at least one uppercase letter.'}), 400
    if not re.search(r'[a-z]', password):
        return jsonify({'error': 'Password must contain at least one lowercase letter.'}), 400
    if not re.search(r'[0-9]', password):
        return jsonify({'error': 'Password must contain at least one number.'}), 400
    if not re.search(SPECIAL_CHARS, password):
        return jsonify({'error': 'Password must contain at least one special character (e.g. !, @, #, $).'}), 400

    users = load_users()
    if username in users:
        return jsonify({'error': 'Username already taken.'}), 409

    users[username] = generate_password_hash(password, method='pbkdf2:sha256')
    save_users(users)
    session['username'] = username
    session['auth_type'] = 'password'
    return jsonify({'username': username})


@app.post('/api/login')
def login():
    body = request.get_json() or {}
    username = (body.get('username') or '').strip().lower()
    password = body.get('password') or ''

    users = load_users()
    if username not in users or not check_password_hash(users[username], password):
        return jsonify({'error': 'Invalid username or password.'}), 401

    session['username'] = username
    session['auth_type'] = 'password'
    return jsonify({'username': username})


@app.post('/api/guest')
def guest():
    session['username'] = 'Guest'
    session['auth_type'] = 'guest'
    return jsonify({'username': 'Guest'})


@app.post('/api/logout')
def logout():
    session.clear()
    return jsonify({'ok': True})


@app.get('/api/me')
def me():
    if 'username' in session:
        return jsonify({'username': session['username'],
                        'auth_type': session.get('auth_type', 'password')})
    return jsonify({'username': None})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'\n  Athan Clock running at http://localhost:{port}\n')
    app.run(port=port, debug=False)
