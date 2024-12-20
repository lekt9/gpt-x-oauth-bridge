from flask import Flask, request, jsonify, redirect, url_for
import os
from functools import wraps
import requests
import urllib.parse

app = Flask(__name__)

# Configuration
AUTH_URL = "https://api.twitter.com/2/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

SCOPES = "tweet.read tweet.write"

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            return jsonify({'error': 'No authorization header'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/authorize')
def authorize():
    """
    Generate authorization URL and redirect user to X.com OAuth page
    """
    params = {
        'response_type': 'code',
        'client_id': os.environ['CLIENT_ID'],
        'redirect_uri': os.environ['REDIRECT_URI'],
        'scope': SCOPES,
        'state': 'state'  # You should generate a random state for security
    }
    
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """
    Handle the OAuth callback from X.com
    """
    error = request.args.get('error')
    if error:
        return jsonify({'error': error}), 400

    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    state = request.args.get('state')
    # TODO: Validate state parameter

    # Exchange code for token
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': os.environ['CLIENT_ID'],
        'client_secret': os.environ['CLIENT_SECRET'],
        'redirect_uri': os.environ['REDIRECT_URI']
    }
    
    response = requests.post(TOKEN_URL, data=data)
    token_data = response.json()
    
    # Return token data to the client
    # In a real implementation, you might want to store this securely
    # and/or redirect to a frontend application
    return jsonify({
        'access_token': token_data.get('access_token'),
        'refresh_token': token_data.get('refresh_token'),
        'token_type': token_data.get('token_type'),
        'expires_in': token_data.get('expires_in')
    })

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
