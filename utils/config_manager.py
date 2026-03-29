import os
import json
import sys
from pathlib import Path
from typing import Any


class ConfigManager:
    """Gestor de configuración multiplataforma para PanterBots."""

    # Ruta universal: ~/.panterbots/config.json
    CONFIG_DIR = Path.home() / ".panterbots"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    LOG_FILE = CONFIG_DIR / "supertrend_simple.log"

    DEFAULT_CONFIG = {
        "SYMBOL": "DOGEUSDT,BTCUSDT,ETHUSDT",
        "TIMEFRAMES": ["15", "60", "240"],
        "ATR_PERIOD": 10,
        "ATR_MULTIPLIER": 3.0,
        "TELEGRAM_BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN",  # pragma: allowlist secret
        "TELEGRAM_CHAT_ID": "YOUR_TELEGRAM_CHAT_ID",  # pragma: allowlist secret
        "BYBIT_API_KEY": "YOUR_BYBIT_API_KEY",  # pragma: allowlist secret
        "BYBIT_API_SECRET": "YOUR_BYBIT_API_SECRET",  # pragma: allowlist secret
    }

    def __init__(self):
        self.config_data = {}
        self._initialize()

    def _initialize(self):
        """Crea la estructura de carpetas y archivos si no existen."""
        if not self.CONFIG_DIR.exists():
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if not self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=4)
            print("\n" + "=" * 50)
            print(" FIRST RUN: CONFIGURATION FILE CREATED")
            print(f" Path: {self.CONFIG_FILE}")
            print("=" * 50)
            print(" Please edit the file above with your API keys and")
            print(" Telegram credentials before running the bot again.")
            print("=" * 50 + "\n")
            sys.exit(0)  # Salir para que el usuario configure

        self._load()

    def _load(self):
        """Carga datos desde JSON y sobrescribe con variables de entorno si existen."""
        with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
            self.config_data = json.load(f)

        # Normalizar SYMBOLS (siempre como lista)
        symbols = self.config_data.get("SYMBOL", "DOGEUSDT")
        if isinstance(symbols, str):
            self.config_data["SYMBOL"] = [
                s.strip() for s in symbols.replace("\n", ",").split(",") if s.strip()
            ]

        # Soporte para Variables de Entorno (Prioridad alta)
        for key in self.DEFAULT_CONFIG.keys():
            env_val = os.getenv(f"PANTER_{key}")
            if env_val:
                # Intentar parsear si es una lista (para TIMEFRAMES)
                if isinstance(self.DEFAULT_CONFIG[key], list):
                    try:
                        self.config_data[key] = json.loads(env_val)
                    except Exception:
                        self.config_data[key] = env_val.split(",")
                # Intentar parsear números
                elif isinstance(self.DEFAULT_CONFIG[key], (int, float)):
                    try:
                        self.config_data[key] = type(self.DEFAULT_CONFIG[key])(env_val)
                    except Exception:
                        pass
                else:
                    self.config_data[key] = env_val

    def get(self, key: str) -> Any:
        return self.config_data.get(key)

    @property
    def is_configured(self) -> bool:
        """Verifica si el usuario ya cambió los valores por defecto."""
        placeholders = ["TU_BOT_TOKEN_AQUI", "TU_API_KEY_AQUI", ""]
        token = self.get("TELEGRAM_BOT_TOKEN")
        return token not in placeholders
