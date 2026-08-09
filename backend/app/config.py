"""
Environment configuration.

Reads settings from environment variables (populated from .env in local dev
via python-dotenv). Keep this the single place that touches os.environ so
nobody has to remember variable names elsewhere in the codebase.
"""

import os

from dotenv import load_dotenv


load_dotenv()


# PageSpeed API configuration
PAGESPEED_API_KEY = os.getenv(
    "PAGESPEED_API_KEY",
    "",
).strip()


# Gemini API configuration
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "",
).strip()


# Gemini model configuration
# This can be changed from the .env file without modifying source code.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
).strip()


# Comma-separated list of allowed frontend origins for CORS.
# Defaults to "*" for local development.
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "*",
).strip()


ALLOWED_ORIGINS = (
    [origin.strip() for origin in _raw_origins.split(",")]
    if _raw_origins != "*"
    else ["*"]
)