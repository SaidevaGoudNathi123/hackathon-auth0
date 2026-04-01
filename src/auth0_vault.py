import base64
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
AUTH0_AUDIENCE = os.environ["AUTH0_AUDIENCE"]


def get_notion_token(user_access_token: str) -> str:
    """
    Exchange the user's Auth0 access token for a Notion access token
    stored in Token Vault, using RFC 8693 token exchange.

    Args:
        user_access_token: The user's current Auth0 access token.
                           In OpenClaw this comes from the session context.

    Returns:
        A fresh Notion access token string.

    Raises:
        RuntimeError: If the exchange fails or no token is returned.
    """
    url = f"https://{AUTH0_DOMAIN}/oauth/token"

    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": AUTH0_AUDIENCE,
        "subject_token": user_access_token,
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "requested_token_type": "urn:auth0:params:oauth:token-type:connection",
        "connection": "notion",
        "requested_subject": _extract_sub(user_access_token),
    }

    response = requests.post(url, json=payload, timeout=10)

    if not response.ok:
        raise RuntimeError(
            f"Auth0 token exchange failed: {response.status_code} {response.text}"
        )

    data = response.json()
    token = data.get("access_token")

    if not token:
        raise RuntimeError(f"No access_token in Token Vault response: {data}")

    return token


def _extract_sub(jwt_token: str) -> str:
    """
    Decode the JWT payload (without signature verification) to extract the
    'sub' claim, which tells Auth0 Token Vault which user's token to return.
    """
    parts = jwt_token.split(".")
    if len(parts) < 2:
        raise ValueError("Not a valid JWT — cannot extract sub claim")
    padding = 4 - len(parts[1]) % 4
    payload = base64.urlsafe_b64decode(parts[1] + "=" * padding)
    return json.loads(payload)["sub"]
