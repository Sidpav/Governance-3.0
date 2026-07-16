# config/app_config.py
# ─────────────────────────────────────────────────────────────────────────
# Optional "hardcode it in a config file" path: fill in config/app_config.json
# with a real api_key and every user of the deployed app gets that key
# automatically — no sidebar field, nobody has to bring their own key.
#
# This is a deliberate alternative to Streamlit's own `st.secrets`
# mechanism (.streamlit/secrets.toml locally, the Secrets panel on
# Streamlit Cloud), which utils/helpers.get_api_key() already checks
# first and which keeps the key out of the repo entirely. Use secrets.toml
# instead of this file if the repo is public — anything committed here is
# visible to anyone who can read the source.
# ─────────────────────────────────────────────────────────────────────────

import json
from pathlib import Path

APP_CONFIG_FILE = Path(__file__).parent / "app_config.json"


def load_app_config() -> dict:
    try:
        with open(APP_CONFIG_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        data = {}
    return {
        "provider": (data.get("provider") or "").strip().lower(),
        "model": (data.get("model") or "").strip(),
        "api_key": (data.get("api_key") or "").strip(),
    }


def is_backend_configured() -> bool:
    """True once app_config.json has a real (non-empty) api_key filled in."""
    return bool(load_app_config().get("api_key"))
