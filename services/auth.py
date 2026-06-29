"""
services/auth.py
----------------
IBM IAM token management.
- Fetches a bearer token using the API key (client_credentials grant).
- Caches the token in memory and auto-refreshes before expiry.
- Thread-safe for single-worker Flask development server.
"""

import time
import logging
import requests

logger = logging.getLogger(__name__)


class IBMAuthService:
    """Manages IBM IAM bearer-token lifecycle."""

    def __init__(self, api_key: str, iam_url: str, refresh_buffer: int = 300):
        """
        Parameters
        ----------
        api_key        : IBM Cloud API key
        iam_url        : IBM IAM token endpoint
        refresh_buffer : seconds before expiry to proactively refresh (default 300)
        """
        self._api_key = api_key
        self._iam_url = iam_url
        self._refresh_buffer = refresh_buffer

        self._token: str = ""
        self._expires_at: float = 0.0  # UNIX timestamp

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_token(self) -> str:
        """Return a valid bearer token, fetching a new one if necessary."""
        if self._is_token_expired():
            self._fetch_token()
        return self._token

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _is_token_expired(self) -> bool:
        """True when the cached token is missing or close to expiry."""
        return time.time() >= (self._expires_at - self._refresh_buffer)

    def _fetch_token(self) -> None:
        """Call IBM IAM and cache the new token + expiry timestamp."""
        if not self._api_key:
            raise ValueError(
                "IBM_API_KEY is not set. "
                "Copy .env.example to .env and add your API key."
            )

        payload = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self._api_key,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        logger.info("Fetching new IBM IAM token …")
        try:
            response = requests.post(
                self._iam_url,
                data=payload,
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise RuntimeError("IBM IAM request timed out. Check your network.")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Cannot reach IBM IAM endpoint. Check your network.")
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"IBM IAM returned HTTP {exc.response.status_code}: "
                f"{exc.response.text}"
            )

        data = response.json()
        self._token = data["access_token"]
        # expires_in is seconds from now; add a small safety margin
        self._expires_at = time.time() + int(data.get("expires_in", 3600))
        logger.info("IBM IAM token acquired, expires in %s s.", data.get("expires_in"))
