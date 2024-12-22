from flask import Flask, request, jsonify
import asyncio
from twikit import Client
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Twikit client configuration
client = Client('en-US')

# Initialize the client and login
async def initialize_client():
    await client.login(
        auth_info_1=os.environ['TWITTER_USERNAME'],
        auth_info_2=os.environ['TWITTER_EMAIL'],
        password=os.environ['TWITTER_PASSWORD']
    )

# Run initialization
asyncio.run(initialize_client())

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header'}), 401
        api_key = auth.split(' ')[1]
        if api_key != os.environ.get('LOCAL_API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/tweet', methods=['POST'])
@require_auth
def create_tweet():
    """
    Create a new tweet
    """
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'No tweet text provided'}), 400
    
    try:
        response = asyncio.run(client.create_tweet(text=data['text']))
        return jsonify({
            'id': response.id,
            'text': response.text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tweet/<tweet_id>/reply', methods=['POST'])
@require_auth
def reply_to_tweet(tweet_id):
    """
    Reply to an existing tweet
    """
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'No reply text provided'}), 400
    
    try:
        response = asyncio.run(client.create_tweet(
            text=data['text'],
            reply_to=tweet_id
        ))
        return jsonify({
            'id': response.id,
            'text': response.text,
            'in_reply_to': tweet_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/thread', methods=['POST'])
@require_auth
def create_thread():
    """
    Create a thread of tweets
    """
    data = request.json
    if not data or 'tweets' not in data or not isinstance(data['tweets'], list):
        return jsonify({'error': 'No tweets provided'}), 400
    
    thread = []
    previous_tweet_id = None
    
    try:
        for tweet_text in data['tweets']:
            response = asyncio.run(client.create_tweet(
                text=tweet_text,
                reply_to=previous_tweet_id
            ))
            tweet_data = {
                'id': response.id,
                'text': response.text
            }
            thread.append(tweet_data)
            previous_tweet_id = response.id
        
        return jsonify({
            'thread': thread
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tweet/<tweet_id>', methods=['GET'])
@require_auth
def get_tweet(tweet_id):
    """
    Get a specific tweet
    """
    try:
        response = asyncio.run(client.get_tweet_by_id(tweet_id))
        if not response:
            return jsonify({'error': 'Tweet not found'}), 404
        
        return jsonify({
            'id': response.id,
            'text': response.text,
            'author': {
                'id': response.user.id,
                'name': response.user.name,
                'username': response.user.username
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tweets/search', methods=['GET'])
@require_auth
def search_tweets():
    """
    Search for tweets
    """
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    try:
        tweets_data = asyncio.run(client.search_tweet(query, 'Latest'))
        
        tweets = []
        for tweet in tweets_data:
            tweets.append({
                'id': tweet.id,
                'text': tweet.text,
                'author': {
                    'id': tweet.user.id,
                    'name': tweet.user.name,
                    'username': tweet.user.username
                },
                'created_at': tweet.created_at
            })
        
        return jsonify({
            'tweets': tweets
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
