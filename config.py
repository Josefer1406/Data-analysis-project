# ==============================
# CONFIG HEDGE FUND PRO
# ==============================

# Capital
CAPITAL_INICIAL = 1000
USO_CAPITAL = 0.60

# Trading
MAX_POSICIONES = 3
MIN_TRADE_USD = 30

# Timeframe real de mercado
TIMEFRAME = "5m"   # 🔥 puedes cambiar a "1m", "15m", "1h"

# Ciclo del bot
CYCLE_TIME = 15

# Riesgo
STOP_LOSS = -0.02

# Trailing institucional
TRAILING_START = 0.02
TRAILING_GAP = 0.015

# IA thresholds
UMBRAL_EXCELENTE = 0.9
UMBRAL_BUENO = 0.75

# Cooldown base (dinámico luego)
COOLDOWN_BASE = 20

# Universo de trading (TOP liquidez)
CRYPTOS = [
    "BTC/USDT", "ETH/USDT",
    "SOL/USDT", "AVAX/USDT",
    "ADA/USDT", "XRP/USDT",
    "LINK/USDT", "ATOM/USDT"
]

# Clusters de correlación
CORRELACION = {
    "L1": ["BTC/USDT", "ETH/USDT"],
    "L2": ["SOL/USDT", "AVAX/USDT"],
    "L3": ["ADA/USDT", "XRP/USDT"],
    "L4": ["LINK/USDT", "ATOM/USDT"]
}