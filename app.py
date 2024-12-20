from flask import Flask, request, jsonify
import os
from functools import wraps
import requests

app = Flask(__name__)

# Configuration
AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            return jsonify({'error': 'No authorization header'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/oauth/token', methods=['POST'])
def exchange_token():
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': os.environ['CLIENT_ID'],
        'client_secret': os.environ['CLIENT_SECRET'],
        'redirect_uri': os.environ['REDIRECT_URI']
    }
    
    response = requests.post(TOKEN_URL, data=data)
    return jsonify(response.json())

@app.route('/oauth/refresh', methods=['POST'])
@require_auth
def refresh_token():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({'error': 'No refresh token provided'}), 400
    
    data = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'client_id': os.environ['CLIENT_ID'],
        'client_secret': os.environ['CLIENT_SECRET']
    }
    
    response = requests.post(TOKEN_URL, data=data)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
