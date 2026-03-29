"""
Sistema simplificado de alertas Supertrend
"""

import requests
import pandas as pd
import numpy as np
import time
import logging
import re
from datetime import datetime
import pytz
from typing import Dict


PAIR = "DOGEUSDT"  # Legacy placeholder


def setup_dynamic_logging():
    """Configura el logging dinámicamente usando la ruta del ConfigManager."""
    import sys
    from pathlib import Path

    # Necesitamos importar el ConfigManager antes de configurar el log
    # El archivo está en PanterBots/utils/config_manager.py
    base_path = Path(__file__).parent.parent / "utils"
    sys.path.append(str(base_path))

    try:
        from config_manager import ConfigManager

        config = ConfigManager()
        log_path = config.LOG_FILE

        # Asegurar que el directorio existe (aunque ConfigManager ya lo hace)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        return config
    except Exception as e:
        # Fallback a consola si algo falla
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        print(f"[!] Error configurando log dinámico: {e}")
        return None


class SupertrendCalculator:
    """Calculadora del indicador Supertrend"""

    def __init__(self, atr_period=10, atr_multiplier=3.0):
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier

    def calculate_atr(self, data: pd.DataFrame) -> pd.Series:
        """Calcula el Average True Range (ATR)"""
        high = data["high"]
        low = data["low"]
        close = data["close"]

        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.ewm(span=self.atr_period).mean()

        return atr

    def calculate_supertrend(self, data: pd.DataFrame) -> Dict:
        """Calcula el indicador Supertrend y retorna señales"""
        if len(data) < self.atr_period + 1:
            return {"trend": 0, "supertrend": 0, "signal": None, "price": 0}

        # Calcular ATR
        atr = self.calculate_atr(data)

        # Fuente de precios (hl2)
        src = (data["high"] + data["low"]) / 2

        # Calcular bandas
        up = src - (self.atr_multiplier * atr)
        dn = src + (self.atr_multiplier * atr)

        # Inicializar arrays
        up_band = np.zeros(len(data))
        dn_band = np.zeros(len(data))
        trend = np.zeros(len(data))

        # Primer valor
        up_band[0] = up.iloc[0]
        dn_band[0] = dn.iloc[0]
        trend[0] = 1

        # Calcular bandas y tendencia
        for i in range(1, len(data)):
            # Banda superior
            up_band[i] = up.iloc[i]
            if data["close"].iloc[i - 1] > up_band[i - 1]:
                up_band[i] = max(up.iloc[i], up_band[i - 1])

            # Banda inferior
            dn_band[i] = dn.iloc[i]
            if data["close"].iloc[i - 1] < dn_band[i - 1]:
                dn_band[i] = min(dn.iloc[i], dn_band[i - 1])

            # Determinar tendencia
            if trend[i - 1] == -1 and data["close"].iloc[i] > dn_band[i - 1]:
                trend[i] = 1
            elif trend[i - 1] == 1 and data["close"].iloc[i] < up_band[i - 1]:
                trend[i] = -1
            else:
                trend[i] = trend[i - 1]

        # Calcular Supertrend
        supertrend = np.where(trend == 1, dn_band, up_band)

        # Detectar señales
        current_trend = trend[-1]
        previous_trend = trend[-2] if len(trend) > 1 else current_trend

        signal = None
        if current_trend == 1 and previous_trend == -1:
            signal = "LONG"
        elif current_trend == -1 and previous_trend == 1:
            signal = "SHORT"

        return {
            "trend": current_trend,
            "supertrend": supertrend[-1],
            "signal": signal,
            "price": data["close"].iloc[-1],
        }


class SymbolInvalidError(Exception):
    """Excepción para cuando un símbolo no existe en el exchange."""

    pass


class BybitDataFetcher:
    """Manejador de datos de Bybit"""

    def __init__(self, symbol=""):
        self.symbol = symbol
        self.base_url = "https://api.bybit.com"
        self.logger = logging.getLogger("BYBIT")

    def get_klines(self, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """Obtiene datos de klines"""
        url = f"{self.base_url}/v5/market/kline"

        params = {
            "category": "linear",
            "symbol": self.symbol,
            "interval": timeframe,
            "limit": limit,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data["retCode"] == 0:
                klines = data["result"]["list"]
                if not klines:
                    return pd.DataFrame()

                # Los datos vienen en orden inverso
                klines.reverse()

                df = pd.DataFrame(
                    klines,
                    columns=[
                        "start_time",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "turnover",
                    ],
                )

                # Convertir tipos de datos
                df["start_time"] = pd.to_datetime(
                    df["start_time"].astype(int), unit="ms"
                )
                df["open"] = df["open"].astype(float)
                df["high"] = df["high"].astype(float)
                df["low"] = df["low"].astype(float)
                df["close"] = df["close"].astype(float)
                df["volume"] = df["volume"].astype(float)

                df.set_index("start_time", inplace=True)
                return df
            else:
                msg = data.get("retMsg", "")
                if "Symbol Is Invalid" in msg or "not support" in msg.lower():
                    raise SymbolInvalidError(f"{self.symbol}: {msg}")

                self.logger.error(f"Error en API: {msg}")
                return pd.DataFrame()

        except SymbolInvalidError:
            raise
        except Exception as e:
            self.logger.error(f"Error al obtener datos: {e}")
            return pd.DataFrame()


class TelegramNotifier:
    """Notificador de Telegram"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.mexico_tz = pytz.timezone("America/Mexico_City")
        self.logger = logging.getLogger("TELEGRAM")

    def escape_markdown(self, text: str) -> str:
        """
        Escapa caracteres especiales de Markdown v1 EXCEPTO dentro de URLs.
        Deja [label](url) intacto para que los enlaces funcionen.
        Basado en BASE_CCXT.
        """

        def _escape(segment: str) -> str:
            return re.sub(r"([_*`])", r"\\\1", segment)

        parts = []
        last_end = 0
        # Encontrar todos los enlaces Markdown v1: [texto](url)
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
            # escapamos el texto antes del enlace
            parts.append(_escape(text[last_end : m.start()]))
            label = m.group(1)
            url = m.group(2)
            # escapamos solo el label, no la URL
            parts.append(f"[{_escape(label)}]({url})")
            last_end = m.end()
        # escapamos el resto del texto después del último enlace
        parts.append(_escape(text[last_end:]))
        return "".join(parts)

    def get_mexico_time(self) -> str:
        """Obtiene la hora actual en la zona horaria configurada"""
        now = datetime.now(self.mexico_tz)
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def send_message(self, text: str) -> bool:
        """Envía un mensaje genérico a Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": "true",
            }
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Error enviando mensaje a Telegram: {e}")
            return False

    def send_alert(self, signal_data: dict, symbol: str = "CRYPTOCURRENCY") -> bool:
        """Envía una alerta a Telegram"""
        try:
            timeframe_map = {"30": "30 minutos", "60": "1 hora", "240": "4 horas"}

            timeframe_name = timeframe_map.get(
                signal_data["timeframe"], signal_data["timeframe"]
            )
            mexico_time = self.get_mexico_time()

            # Crear mensaje
            if signal_data["signal"] == "LONG":
                emoji = "🟢"
                action = "COMPRA"
            else:
                emoji = "🔴"
                action = "VENTA"

            message = f"""{emoji} **ALERTA SUPERTREND - {self.escape_markdown(symbol)}**

**Hora CDMX:** {mexico_time}
**Timeframe:** {timeframe_name}
**Precio:** ${signal_data["price"]:.4f}
**Supertrend:** ${signal_data["supertrend"]:.4f}
**Señal:** {signal_data["signal"]} ({action})

#Supertrend #{self.escape_markdown(symbol)} #{signal_data["signal"]}
            """.strip()

            # Enviar mensaje
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": "true",
            }

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            self.logger.info(
                f"Alerta enviada: {signal_data['signal']} en {timeframe_name}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error enviando alerta a Telegram: {e}")
            return False


class SupertrendAlertSystem:
    """Sistema principal de alertas Supertrend"""

    def __init__(self, config=None):
        if not config:
            # Si no se pasó config (para tests), intentamos cargar uno básico
            import sys
            from pathlib import Path

            base_path = Path(__file__).parent.parent / "utils"
            sys.path.append(str(base_path))
            from config_manager import ConfigManager

            config = ConfigManager()

        self.logger = logging.getLogger("MAIN")
        self.config = config

        # 2. Validar configuración
        if not self.config.is_configured:
            print("\n[!] ERROR DE CONFIGURACIÓN")
            print(f"[!] Las credenciales en {self.config.CONFIG_FILE} son inválidas.")
            print("[!] Por favor, edita el JSON con tus datos reales.\n")
            sys.exit(1)

        # 3. Asignar valores desde el Gestor JSON
        self.symbols = self.config.get("SYMBOL")
        self.timeframes = self.config.get("TIMEFRAMES")
        self.atr_period = self.config.get("ATR_PERIOD")
        self.atr_multiplier = self.config.get("ATR_MULTIPLIER")

        # Un fetcher por símbolo para mantener el estado del symbol
        self.fetchers = {sym: BybitDataFetcher(sym) for sym in self.symbols}
        self.calculator = SupertrendCalculator(self.atr_period, self.atr_multiplier)

        # 4. Inicializar Telegram con los nuevos campos
        self.telegram = TelegramNotifier(
            self.config.get("TELEGRAM_BOT_TOKEN"), self.config.get("TELEGRAM_CHAT_ID")
        )

        # Almacenar últimas señales para evitar duplicados: {symbol: {timeframe: signal}}
        self.last_signals = {
            sym: {tf: None for tf in self.timeframes} for sym in self.symbols
        }

        self.logger.info(
            f"Sistema inicializado para {len(self.symbols)} símbolos: {', '.join(self.symbols)}"
        )
        self.logger.info(f"Timeframes: {', '.join(self.timeframes)}")

        # Enviar notificación de inicio a Telegram
        sym_list_str = ", ".join(self.symbols)
        start_msg = f"🚀 **PanterBot Iniciado**\n\n**Símbolos:** {self.telegram.escape_markdown(sym_list_str)}\n**Timeframes:** {', '.join(self.timeframes)}\n**Estado:** Monitoreando..."
        self.telegram.send_message(start_msg)

    def check_signals(self):
        """Verifica señales en todos los símbolos y timeframes"""
        invalid_symbols = []

        for symbol in self.symbols:
            fetcher = self.fetchers.get(symbol)
            if not fetcher:
                continue

            symbol_error = False
            for timeframe in self.timeframes:
                try:
                    # Obtener datos
                    df = fetcher.get_klines(timeframe, limit=50)

                    if df.empty:
                        self.logger.warning(
                            f"No hay datos para {symbol} en {timeframe}"
                        )
                        continue

                    # Calcular Supertrend
                    result = self.calculator.calculate_supertrend(df)

                    # Verificar si hay nueva señal
                    if (
                        result["signal"]
                        and result["signal"] != self.last_signals[symbol][timeframe]
                    ):
                        self.last_signals[symbol][timeframe] = result["signal"]

                        # Crear datos de señal
                        signal_data = {
                            "timeframe": timeframe,
                            "signal": result["signal"],
                            "price": result["price"],
                            "supertrend": result["supertrend"],
                        }

                        # Enviar alerta
                        success = self.telegram.send_alert(signal_data, symbol=symbol)
                        if success:
                            self.logger.info(
                                f"Señal {result['signal']} enviada para {symbol} en {timeframe}"
                            )

                except SymbolInvalidError as e:
                    self.logger.error(f"Símbolo eliminado: {e}")
                    invalid_symbols.append(symbol)
                    symbol_error = True
                    break  # Detener este símbolo
                except Exception as e:
                    self.logger.error(
                        f"Error verificando señales para {symbol} en {timeframe}: {e}"
                    )

            if symbol_error:
                continue

        # Limpiar la lista de símbolos activos
        for sym in invalid_symbols:
            if sym in self.symbols:
                self.symbols.remove(sym)
                if sym in self.fetchers:
                    del self.fetchers[sym]
                if sym in self.last_signals:
                    del self.last_signals[sym]

    def run(self):
        """Ejecuta el sistema de alertas"""
        self.logger.info("Iniciando sistema de alertas...")

        iteration = 0
        while True:
            try:
                self.check_signals()

                # Heartbeat cada ~80 segundos (10 iteraciones de 8s)
                iteration += 1
                if iteration >= 10:
                    sym_count = len(self.symbols)
                    self.logger.info(
                        f"Bot activo - Monitoreando {sym_count} símbolos en {', '.join(self.timeframes)}"
                    )
                    iteration = 0

                time.sleep(8)  # Verificar cada 8 segundos

            except KeyboardInterrupt:
                self.logger.info("Sistema detenido por el usuario")
                break
            except Exception as e:
                self.logger.error(f"Error en el sistema: {e}")
                time.sleep(60)


def main():
    """Función principal"""
    import sys

    try:
        config = setup_dynamic_logging()
        if not config:
            sys.exit(1)

        system = SupertrendAlertSystem(config=config)
        system.run()
    except Exception as e:
        # Aquí todavía no podemos usar self.logger porque main es global
        logging.error(f"Error iniciando el sistema: {e}")


if __name__ == "__main__":
    main()
