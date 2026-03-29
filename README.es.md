# PanterBots 🐾 (Español)

PanterBots es un sistema automatizado de alertas de criptomonedas basado en el indicador **Supertrend**. Monitorea datos de mercado de **Bybit** en tiempo real y envía señales directamente a **Telegram**.

Este proyecto es una refactorización y mejora profesional mantenida por [comgunner](https://github.com/comgunner/PanterBots).
Proyecto original de [bitcoinalexis](https://github.com/bitcoinalexis/PanterBots).

## 🚀 Características Clave

- **Monitoreo Multi-Moneda**: Rastrea múltiples monedas simultáneamente (ej. BTC, ETH, DOGE) usando una lista separada por comas.
- **Sistema de Auto-Limpieza**: Detecta y elimina automáticamente símbolos inválidos no soportados por el exchange para evitar errores.
- **Monitoreo de "Latido" (Heartbeat)**: Confirmación visual en consola y logs de estado periódicos para asegurar que el bot sigue vivo.
- **Notificaciones Robustas**: Alertas de Telegram formateadas con escape de Markdown para evitar fallos en la entrega de mensajes.
- **Configuración Inteligente**: Generación automática de archivos de configuración y soporte para variables de entorno.
- **Timeframes Predefinidos**: Soporte para múltiples intervalos de análisis (ej. 15m, 1h, 4h).

## 🛠️ Requisitos

- Python 3.10+
- Dependencias listadas en `SuperTrendFree/requirements.txt` (`pandas`, `requests`, `numpy`, `pytz`).

## ⚙️ Instalación y Configuración

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/comgunner/PanterBots.git
   cd PanterBots
   ```

### 🍎 Configuración macOS / 🐧 Linux

2. **Crea y activa un entorno virtual**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Actualiza e Instala**:
   ```bash
   python -m pip install --upgrade pip setuptools
   pip install -r SuperTrendFree/requirements.txt
   ```

### 🪟 Configuración Windows (10/11)

2. **Crea y activa un entorno virtual**:
   ```bash
   python -m venv .venv
   
   # Si usas el Símbolo del Sistema (CMD):
   .venv\Scripts\activate
   
   # Si usas PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

3. **Actualiza e Instala**:
   ```bash
   python -m pip install --upgrade pip setuptools
   pip install -r SuperTrendFree/requirements.txt
   ```

---

4. **Primera Ejecución y Configuración (Todos los sistemas)**:
   Ejecuta el bot por primera vez para generar el archivo de configuración:
   ```bash
   python SuperTrendFree/PanterTrend.py
   ```
   El bot creará un archivo de configuración en `~/.panterbots/config.json`. Edita este archivo con tus credenciales de Telegram y Bybit.

## 🚦 Uso

Una vez configurado, simplemente inicia el bot:
```bash
python SuperTrendFree/PanterTrend.py
```

## 📝 Configuración (config.json)

- `SYMBOL`: Lista de pares separados por comas (ej: "BTCUSDT,ETHUSDT,DOGEUSDT").
- `TIMEFRAMES`: Lista de intervalos (ej: ["15", "60", "240"]).
- `ATR_PERIOD`: Período ATR del Supertrend (predeterminado: 10).
- `ATR_MULTIPLIER`: Multiplicador ATR del Supertrend (predeterminado: 3.0).
- `TELEGRAM_BOT_TOKEN`: Tu token de bot de @BotFather.
- `TELEGRAM_CHAT_ID`: El ID de tu canal o usuario de Telegram.
  - **Tip:** Reenvía un mensaje desde tu canal a [@username_to_id_bot](https://t.me/username_to_id_bot) para obtener el ID.
- `BYBIT_API_KEY`: Tu clave API de Bybit.
- `BYBIT_API_SECRET`: Tu secreto API de Bybit.

**Ejemplo:**
```json
{
    "SYMBOL": "1000CATUSDT,1000RATSUSDT,PNUTUSDT,SEIUSDT,BBUSDT,GUNUSDT,LQTYUSDT,KMNOUSDT,NAORISUSDT,APTUSDT,ARBUSDT,ACXUSDT,WIFUSDT,1MBABYDOGEUSDT,RONINUSDT,EDUUSDT",
    "TIMEFRAMES": ["15", "60", "240"],
    "ATR_PERIOD": 10,
    "ATR_MULTIPLIER": 3.0,
    "TELEGRAM_BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN",  # pragma: allowlist secret
    "TELEGRAM_CHAT_ID": "YOUR_TELEGRAM_CHAT_ID",
    "BYBIT_API_KEY": "YOUR_BYBIT_API_KEY",  # pragma: allowlist secret
    "BYBIT_API_SECRET": "YOUR_BYBIT_API_SECRET"  # pragma: allowlist secret
}
```

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Créditos

- Mantenido por: [comgunner](https://github.com/comgunner)
- Repositorio Original: [bitcoinalexis/PanterBots](https://github.com/bitcoinalexis/PanterBots)
