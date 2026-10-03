import os
import logging
import streamlit as st
from supabase import create_client, Client

# Optional support for .env files via python-dotenv if installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logger
logger = logging.getLogger(__name__)


def get_config_value(key: str) -> str | None:
    """
    Retrieve configuration value prioritizing Streamlit secrets, then environment variables.
    Priority: st.secrets -> os.getenv() -> None
    """
    # 1. Check Streamlit secrets
    try:
        if key in st.secrets:
            val = st.secrets[key]
            if val and str(val).strip():
                return str(val).strip()
    except Exception:
        pass

    # 2. Check environment variables
    env_val = os.getenv(key)
    if env_val and env_val.strip():
        return env_val.strip()

    return None


# Load Supabase credentials
SUPABASE_URL = get_config_value("SUPABASE_URL")
SUPABASE_KEY = get_config_value("SUPABASE_KEY")

# Validate configuration
if not SUPABASE_URL or not SUPABASE_KEY:
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_KEY:
        missing.append("SUPABASE_KEY")

    error_msg = (
        f"Supabase configuration missing: {', '.join(missing)}. "
        "Please configure SUPABASE_URL and SUPABASE_KEY in `.streamlit/secrets.toml` or environment variables."
    )
    logger.error(error_msg)

    try:
        st.error(
            "Supabase configuration missing. Please configure SUPABASE_URL and SUPABASE_KEY."
        )
        st.stop()
    except Exception:
        raise RuntimeError(error_msg)

# Initialize Supabase client safely
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    init_error = f"Failed to initialize Supabase client: {e}"
    logger.error(init_error)
    try:
        st.error(f"Database connection error: {e}")
        st.stop()
    except Exception:
        raise RuntimeError(init_error)