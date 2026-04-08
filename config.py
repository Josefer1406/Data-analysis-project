# ==============================
# CONFIG HEDGE FUND PRO FINAL
# ==============================

# Capital
CAPITAL_INICIAL = 1000
USO_CAPITAL = 0.60

# Trading
MAX_POSICIONES = 3
MIN_TRADE_USD = 30

# Timeframe
TIMEFRAME = "5m"
CYCLE_TIME = 15

# Riesgo
STOP_LOSS = -0.02

# Trailing institucional
TRAILING_START = 0.02
TRAILING_GAP = 0.015

# IA thresholds
UMBRAL_EXCELENTE = 0.9
UMBRAL_BUENO = 0.75

# Cooldown
COOLDOWN_BASE = 20

# 🔥 FILTRO DE MERCADO (CLAVE)
VOLATILIDAD_LIMITE = 0.06   # máximo permitido
VOLATILIDAD_MIN = 0.005     # mínimo para evitar mercado muerto

# Universo
CRYPTOS = [
    "BTC/USDT", "ETH/USDT",
    "SOL/USDT", "AVAX/USDT",
    "ADA/USDT", "XRP/USDT",
    "LINK/USDT", "ATOM/USDT"
]

# Correlación
CORRELACION = {
    "L1": ["BTC/USDT", "ETH/USDT"],
    "L2": ["SOL/USDT", "AVAX/USDT"],
    "L3": ["ADA/USDT", "XRP/USDT"],
    "L4": ["LINK/USDT", "ATOM/USDT"]
}