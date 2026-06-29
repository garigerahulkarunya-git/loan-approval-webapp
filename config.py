"""
config.py
---------
Central configuration loader. Reads all settings from environment variables
(populated by .env via python-dotenv). Never hardcodes secrets.
"""

import os
from dotenv import load_dotenv

# Load .env file into environment (no-op if already set)
load_dotenv()


class Config:
    # ------------------------------------------------------------------ Flask
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # --------------------------------------------------------- IBM watsonx.ai
    IBM_API_KEY: str = os.environ.get("IBM_API_KEY", "")
    IBM_DEPLOYMENT_URL: str = os.environ.get(
        "IBM_DEPLOYMENT_URL",
        "https://eu-de.ml.cloud.ibm.com/ml/v4/deployments/"
        "019f13f6-fcea-76eb-939d-d14f7df1da2e/predictions",
    )
    IBM_VERSION: str = os.environ.get("IBM_VERSION", "2021-05-01")

    # IBM IAM token endpoint (public — not a secret)
    IBM_IAM_URL: str = "https://iam.cloud.ibm.com/identity/token"

    # Seconds before proactively refreshing a cached token (IBM tokens last ~3600 s)
    TOKEN_REFRESH_BUFFER: int = 300  # refresh 5 minutes before expiry

    # ---------------------------------------------------------------- Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
