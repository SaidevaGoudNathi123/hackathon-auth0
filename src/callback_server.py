import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
BASE_URL = os.environ["BASE_URL"].rstrip("/")
STATE_SECRET = os.environ["STATE_SECRET"]
PORT = int(os.environ.get("PORT", "8000"))

# ---------------------------------------------------------------------------
# Provider registry — add a new entry here to support a new OAuth provider.
# No changes to routes are needed.
# ---------------------------------------------------------------------------

@dataclass
class ProviderConfig:
    connection: str     # Auth0 connection slug (must match dashboard exactly)
    scopes: str         # Space-separated OAuth scopes
    display_name: str   # Human-readable name used in responses

PROVIDERS: dict[str, ProviderConfig] = {
    "notion": ProviderConfig(
        connection="notion",
        scopes="openid profile email",
        display_name="Notion",
    ),
    # Uncomment to add Google Calendar:
    # "google-calendar": ProviderConfig(
    #     connection="google-oauth2",
    #     scopes="openid profile email https://www.googleapis.com/auth/calendar",
    #     display_name="Google Calendar",
    # ),
    # Uncomment to add YouTube:
    # "youtube": ProviderConfig(
    #     connection="google-oauth2",
    #     scopes="openid profile email https://www.googleapis.com/auth/youtube.readonly",
    #     display_name="YouTube",
    # ),
}

# ---------------------------------------------------------------------------
# CSRF state helpers
# ---------------------------------------------------------------------------

def _make_state(provider: str) -> str:
    """Generate a time-stamped HMAC state token for CSRF protection."""
    timestamp = str(int(time.time()))
    message = f"{provider}:{timestamp}"
    signature = hmac.new(
        STATE_SECRET.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    return f"{message}:{signature}"


def _verify_state(provider: str, state: str) -> bool:
    """Return True if the state token is valid and not older than 10 minutes."""
    try:
        parts = state.split(":")
        if len(parts) != 3:
            return False
        state_provider, timestamp, signature = parts
        if state_provider != provider:
            return False
        if abs(time.time() - int(timestamp)) > 600:
            return False
        expected = hmac.new(
            STATE_SECRET.encode(),
            f"{state_provider}:{timestamp}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Auth0 OAuth Callback Server")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/auth/{provider}/start")
def start(provider: str):
    """
    Redirect the user to Auth0's authorization endpoint for the given provider.
    Auth0 will forward them to the provider's consent screen.
    """
    config = PROVIDERS.get(provider)
    if config is None:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")

    state = _make_state(provider)
    params = urlencode({
        "response_type": "code",
        "client_id": AUTH0_CLIENT_ID,
        "redirect_uri": f"{BASE_URL}/auth/{provider}/callback",
        "connection": config.connection,
        "scope": config.scopes,
        "state": state,
    })
    auth_url = f"https://{AUTH0_DOMAIN}/authorize?{params}"
    return RedirectResponse(url=auth_url, status_code=302)


@app.get("/auth/{provider}/callback")
def callback(provider: str, code: str = None, state: str = None, error: str = None):
    """
    Receive the authorization code from Auth0 after the user approves the
    provider consent screen. Exchange it for tokens — this triggers Auth0
    Token Vault to store the provider's access + refresh tokens.
    """
    config = PROVIDERS.get(provider)
    if config is None:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")

    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    if not state or not _verify_state(provider, state):
        raise HTTPException(status_code=400, detail="Invalid or expired state token")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    # Exchange code for Auth0 tokens. Auth0 handles storing the provider token
    # in Token Vault as a side-effect of this exchange.
    response = requests.post(
        f"https://{AUTH0_DOMAIN}/oauth/token",
        json={
            "grant_type": "authorization_code",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": f"{BASE_URL}/auth/{provider}/callback",
        },
        timeout=10,
    )

    if not response.ok:
        raise HTTPException(
            status_code=502,
            detail=f"Auth0 token exchange failed: {response.status_code} {response.text}",
        )

    return JSONResponse({"status": "connected", "provider": config.display_name})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("callback_server:app", host="0.0.0.0", port=PORT, reload=False)
