import time
import os
import jwt
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

def get_jwt():
    """Generate a short-lived JWT to authenticate as the GitHub App"""
    with open(PRIVATE_KEY_PATH,"r") as f:
        private_key = f.read()

    payload = {
        "iat" : int(time.time()),
        "exp" : int(time.time()) + 600, # Expire in 10 min 
        "iss" : APP_ID
    }

    return jwt.encode(payload,private_key,algorithm="RS256")

def get_installation_token(installation_id: int) -> str:
    """Exchange JWT for an installation access token"""

    jwt_token = get_jwt()
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.post(url, headers=headers)
    r.raise_for_status()
    return r.json()["token"]
