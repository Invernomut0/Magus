"""GitHub Copilot Client for Magus."""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)

# Constants for GitHub Device Flow
GITHUB_DEVICE_CODE_URL = "https://github.com/login/device/code"
GITHUB_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_COPILOT_TOKEN_URL = "https://api.github.com/copilot_internal/v2/token"
COPILOT_CHAT_URL = "https://api.githubcopilot.com/chat/completions"

# Client ID for VSCode (commonly used for this integration)
CLIENT_ID = "01ab8ac9400c4e429b23cb99b9409569"

class MagusCopilotClient:
    """Client for interacting with GitHub Copilot."""

    def __init__(self, session: aiohttp.ClientSession, access_token: Optional[str] = None):
        """Initialize the client."""
        self._session = session
        self._access_token = access_token
        self._copilot_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def request_device_code(self) -> Dict[str, Any]:
        """Request a device code for authentication."""
    async def request_device_code(self) -> Dict[str, Any]:
        """Request a device code for authentication."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "GithubCopilot/1.155.0",
        }
        data = {
            "client_id": CLIENT_ID,
            "scope": "read:user"
        }
        
        try:
            async with self._session.post(GITHUB_DEVICE_CODE_URL, json=data, headers=headers) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    _LOGGER.error("GitHub Device Flow Error %s: %s", resp.status, error_text)
                
                resp.raise_for_status()
                return await resp.json()
        except Exception as e:
            _LOGGER.error("Error requesting device code from %s: %s", GITHUB_DEVICE_CODE_URL, e)
            raise
        except Exception as e:
            _LOGGER.error("Error requesting device code from %s: %s", GITHUB_DEVICE_CODE_URL, e)
            raise

    async def poll_for_token(self, device_code: str, interval: int, expires_in: int) -> Optional[str]:
        """Poll GitHub for the access token."""
        headers = {
            "Accept": "application/json",
        }
        data = {
            "client_id": CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }

        start_time = time.time()
        while time.time() - start_time < expires_in:
            async with self._session.post(GITHUB_ACCESS_TOKEN_URL, json=data, headers=headers) as resp:
                result = await resp.json()
                
                if "access_token" in result:
                    self._access_token = result["access_token"]
                    return self._access_token
                
                if "error" in result:
                    if result["error"] == "authorization_pending":
                        pass  # user hasn't authorized yet
                    elif result["error"] == "slow_down":
                        interval += 5
                    elif result["error"] == "expired_token":
                        _LOGGER.error("Device code expired")
                        return None
                    else:
                        _LOGGER.error("Error polling for token: %s", result["error"])
                        return None

            await asyncio.sleep(interval)
        
        return None

    async def _get_copilot_token(self) -> Optional[str]:
        """Exchange GitHub access token for Copilot token."""
        if not self._access_token:
            raise ValueError("No access token available")

        # Check if current token is valid
        if self._copilot_token and self._token_expires_at and datetime.now() < self._token_expires_at:
            return self._copilot_token

        headers = {
            "Authorization": f"token {self._access_token}",
            "Accept": "application/json",
            "User-Agent": "GithubCopilot/1.155.0", # Mimic VSCode extension
        }

        async with self._session.get(GITHUB_COPILOT_TOKEN_URL, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                self._copilot_token = data["token"]
                # Token usually lasts 30 mins, refresh earlier
                self._token_expires_at = datetime.fromtimestamp(data["expires_at"]) - timedelta(minutes=5)
                return self._copilot_token
            else:
                _LOGGER.error("Failed to get Copilot token: %s", await resp.text())
                return None

    async def chat_completion(self, prompt: str) -> str:
        """Get chat completion from Copilot."""
        token = await self._get_copilot_token()
        if not token:
            raise RuntimeError("Could not obtain Copilot token")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "GithubCopilot/1.155.0",
            "X-Request-Id": str(time.time()),
            "Openai-Organization": "github-copilot", 
            "Vscode-Sessionid": str(time.time()) # Dummy session ID
        }

        data = {
            "messages": [
                {"role": "system", "content": "Sei un assistente domotico intelligente per Home Assistant. Rispondi in modo conciso e utile."},
                {"role": "user", "content": prompt}
            ],
            "model": "gpt-4", # Or gpt-3.5-turbo if preferred
            "temperature": 0.1,
            "top_p": 1,
            "n": 1,
            "stream": False
        }

        async with self._session.post(COPILOT_CHAT_URL, headers=headers, json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_text = await resp.text()
                _LOGGER.error("Copilot API Error: %s", error_text)
                raise RuntimeError(f"Copilot API returned {resp.status}: {error_text}")
