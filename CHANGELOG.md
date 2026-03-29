# Changelog

All notable changes to this project will be documented in this file.

## 2026-03-29

### Added
- Dependency management via `requirements.txt` for core components and planned integrations.
- Periodic "Heartbeat" logging to provide visual confirmation of system activity and monitoring status.
- Automatic Telegram notification on startup to confirm monitoring parameters (symbol and timeframes).
- Robust Markdown escaping for Telegram notifications to handle special characters in prices and trading pairs.
- Configuration template `config.json.example` in the root directory for easier setup.
- Auto-initialization: The bot now automatically creates a default configuration file at `~/.panterbots/config.json` on its first run if it doesn't already exist.
- Multi-symbol support: The `SYMBOL` field in `config.json` can now contain a comma-separated list of coins (e.g., "BTCUSDT,ETHUSDT").
- Centralized Logging: Logs are now stored at `~/.panterbots/supertrend_simple.log` alongside the configuration file, keeping the project directory clean.
- Added `active_pairs.txt` to the root directory containing a verified list of Bybit USDT-Linear symbols for reference.
- Added auto-removal of invalid symbols: The bot now detects symbols not supported by Bybit and removes them from active monitoring to prevent log spam and wasteful API calls.
- Updated `.gitignore` to explicitly exclude local logs, internal configuration files, AI agent configuration directories, and security tool baselines.
- Integrated `pre-commit` hooks for automatic secret detection (`detect-secrets`), code linting, and formatting (`ruff`).
- Added comprehensive documentation in English (`README.md`) and Spanish (`README.es.md`) with virtual environment (venv) and security setup instructions.
- Added MIT License under the name of comgunner.

### Removed
- Legacy documentation and history files (`actualizaciones.md`, `bienvenido.md`, and `actualizaciones Script Bot/` directory) to streamline the repository and focus on current features.
- Legacy `config.py` template, fully replaced by the dynamic `ConfigManager` from `local_work`.
- Hardcoded `PAIR` variable in the main script (now `PanterTrend.py`) to allow dynamic symbol monitoring through configuration.

### Changed
- Renamed main script from `DOGETrend.py` to `PanterTrend.py` to reflect its multi-symbol monitoring capability.
- Standardized console logging format with component-based prefixes (`[MAIN]`, `[BYBIT]`, `[TELEGRAM]`) for improved debugging.
- Improved logging isolation for market data and notification components.
- Disabled web page previews in Telegram alerts for a cleaner user interface.
- Enhanced signal message formatting and escaping for consistent delivery.
