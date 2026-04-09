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

# Trailing
TRAILING_START = 0.02
TRAILING_GAP = 0.015

# IA thresholds
UMBRAL_EXCELENTE = 0.9
UMBRAL_BUENO = 0.75

# Cooldown
COOLDOWN_BASE = 20

# Volatilidad
VOLATILIDAD_LIMITE = 0.10
VOLATILIDAD_MIN = 0.003

# ==============================
# 🔥 UNIVERSO AMPLIO
# ==============================
CRYPTOS = [
    "BTC/USDT","ETH/USDT",
    "SOL/USDT","AVAX/USDT","ADA/USDT",
    "LINK/USDT","ATOM/USDT",
    "INJ/USDT","NEAR/USDT","APT/USDT",
    "OP/USDT","RNDR/USDT","AR/USDT",
    "MATIC/USDT","XRP/USDT"
]

# ==============================
# CORRELACIÓN
# ==============================
CORRELACION = {
    "L1": ["BTC/USDT", "ETH/USDT"],
    "L2": ["SOL/USDT", "AVAX/USDT"],
    "L3": ["ADA/USDT", "XRP/USDT", "MATIC/USDT"],
    "L4": ["LINK/USDT", "ATOM/USDT"],
    "L5": ["INJ/USDT", "NEAR/USDT", "APT/USDT"],
    "L6": ["OP/USDT", "AR/USDT", "RNDR/USDT"]
}