# PanterBots 🐾

PanterBots is an automated cryptocurrency alert system based on the **Supertrend** indicator. It monitors market data from **Bybit** in real-time and sends signals directly to **Telegram**.

This project is a professional refactor and enhancement maintained by [comgunner](https://github.com/comgunner/PanterBots).
Original project by [bitcoinalexis](https://github.com/bitcoinalexis/PanterBots).

## 🚀 Key Features

- **Multi-Symbol Monitoring**: Track multiple coins simultaneously (e.g., BTC, ETH, DOGE) using a comma-separated list.
- **Auto-Cleaning System**: Automatically detects and removes invalid symbols not supported by the exchange to prevent errors.
- **Heartbeat Monitoring**: Console visual confirmation and heartbeat logs to ensure the bot is alive.
- **Robust Notifications**: Formatted Telegram alerts with Markdown escaping to prevent message delivery failures.
- **Smart Configuration**: Automatic generation of configuration files and support for environment variables.
- **Predefined Timeframes**: Support for multiple analysis intervals (e.g., 15m, 1h, 4h).

## 🛠️ Requirements

- Python 3.10+
- Dependencies listed in `SuperTrendFree/requirements.txt` (`pandas`, `requests`, `numpy`, `pytz`).

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/comgunner/PanterBots.git
   cd PanterBots
   ```

### 🍎 macOS / 🐧 Linux Setup

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Update and Install**:
   ```bash
   python -m pip install --upgrade pip setuptools
   pip install -r SuperTrendFree/requirements.txt
   ```

### 🪟 Windows Setup (10/11)

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   
   # If using Command Prompt (CMD):
   .venv\Scripts\activate
   
   # If using PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

3. **Update and Install**:
   ```bash
   python -m pip install --upgrade pip setuptools
   pip install -r SuperTrendFree/requirements.txt
   ```

---

4. **Initial Run & Configuration (All Systems)**:
   Run the bot for the first time to generate the configuration file:
   ```bash
   python SuperTrendFree/PanterTrend.py
   ```
   The bot will create a configuration file at `~/.panterbots/config.json`. Edit this file with your Telegram and Bybit credentials.

## 🚦 Usage

Once configured, simply start the bot:
```bash
python SuperTrendFree/PanterTrend.py
```

## 📝 Configuration (config.json)

- `SYMBOL`: Comma-separated list of pairs (e.g., "BTCUSDT,ETHUSDT,DOGEUSDT").
- `TIMEFRAMES`: List of intervals (e.g., ["15", "60", "240"]).
- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather.
- `TELEGRAM_CHAT_ID`: Your Telegram channel or user ID.

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- Maintained by: [comgunner](https://github.com/comgunner)
- Original Repository: [bitcoinalexis/PanterBots](https://github.com/bitcoinalexis/PanterBots)
