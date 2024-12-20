# X.com API Bridge for GPT Assistants

A lightweight Flask server that provides a simple API key-based authentication bridge between X.com (formerly Twitter) and OpenAI GPT assistants using Tweepy.

## Features

- Simple API key authentication
- Direct Tweepy client integration
- Secure environment variable configuration
- Docker support for easy deployment

## Prerequisites

- Python 3.6+
- X.com Developer Account
- API Key and API Key Secret from X.com

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gpt-bridge.git
cd gpt-bridge
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
```
API_KEY=your_api_key
API_KEY_SECRET=your_api_key_secret
ACCESS_TOKEN=your_access_token
ACCESS_TOKEN_SECRET=your_access_token_secret
```

## Usage

### Running Locally

```bash
python app.py
```

The server will start on `http://localhost:5000`

### Using Docker

```bash
docker build -t gpt-bridge .
docker run -p 5000:5000 --env-file .env gpt-bridge
```

## API Endpoints

### Authenticate
```http
POST /auth
Content-Type: application/json

{
    "api_key": "your_api_key"
}
```

Response:
```json
{
    "authenticated": true,
    "user": "username"
}
```

### Tweet
```http
POST /tweet
Content-Type: application/json
Authorization: Bearer your_api_key

{
    "text": "Your tweet content"
}
```

### Get User Info
```http
GET /user
Authorization: Bearer your_api_key
```

## Configuration for OpenAI

In your OpenAI/ChatGPT interface, use these settings:

- Authentication Type: API Key
- API Key: Your X.com API Key
- API Base URL: https://your-domain.com

## Security Notes

- API keys are transmitted securely over HTTPS
- Keys are never logged or stored on the server
- All requests are validated against X.com's API
