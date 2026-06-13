import time
import os
import jwt
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")

def get_jwt():
    """Generate a short-lived JWT to authenticate as the GitHub App"""
    # Read from env variable instead of file
    private_key = os.getenv("GITHUB_PRIVATE_KEY")
    
    # If running locally, fall back to file
    if not private_key:
        path = os.getenv("GITHUB_PRIVATE_KEY_PATH")
        with open(path, "r") as f:
            private_key = f.read()

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": APP_ID
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

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
