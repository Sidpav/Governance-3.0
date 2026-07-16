import json
from pathlib import Path

SETTINGS_FILE = (
    Path(__file__).parent /
    "llm_settings.json"
)

def load_settings():

    if not SETTINGS_FILE.exists():

        return {
            "provider": "Ollama",
            "model": "qwen2.5:1.5b",
        }

    with open(
        SETTINGS_FILE,
        "r"
    ) as f:

        return json.load(f)


def save_settings(data):

    with open(
        SETTINGS_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )