import json
import keyring
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
KEYRING_SERVICE = "dispatcher_app"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    db_config = config.get("database", {})
    if db_config:
        user = db_config.get("user", "")
        password = keyring.get_password(KEYRING_SERVICE, user)
        if password:
            db_config["password"] = password

    return config


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def save_db_password(user: str, password: str) -> None:
    keyring.set_password(KEYRING_SERVICE, user, password)