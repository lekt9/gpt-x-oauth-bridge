from flask import Flask, request, jsonify
import tweepy
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Tweepy client configuration
client = tweepy.Client(
    consumer_key=os.environ['API_KEY'],
    consumer_secret=os.environ['API_KEY_SECRET'],
    access_token=os.environ['ACCESS_TOKEN'],
    access_token_secret=os.environ['ACCESS_TOKEN_SECRET']
)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header'}), 401
        api_key = auth.split(' ')[1]
        if api_key != os.environ['API_KEY']:
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
        response = client.create_tweet(text=data['text'])
        return jsonify({
            'id': response.data['id'],
            'text': response.data['text']
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
        response = client.create_tweet(
            text=data['text'],
            in_reply_to_tweet_id=tweet_id
        )
        return jsonify({
            'id': response.data['id'],
            'text': response.data['text'],
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
            response = client.create_tweet(
                text=tweet_text,
                in_reply_to_tweet_id=previous_tweet_id
            )
            tweet_data = {
                'id': response.data['id'],
                'text': response.data['text']
            }
            thread.append(tweet_data)
            previous_tweet_id = response.data['id']
        
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
        response = client.get_tweet(tweet_id, expansions=['author_id'])
        if not response.data:
            return jsonify({'error': 'Tweet not found'}), 404
        
        return jsonify({
            'id': response.data.id,
            'text': response.data.text,
            'author_id': response.data.author_id
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
        response = client.search_recent_tweets(
            query=query,
            max_results=10,
            expansions=['author_id']
        )
        
        tweets = []
        for tweet in response.data or []:
            tweets.append({
                'id': tweet.id,
                'text': tweet.text,
                'author_id': tweet.author_id
            })
        
        return jsonify({
            'tweets': tweets
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
