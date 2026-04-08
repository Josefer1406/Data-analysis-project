# ==============================
# CONFIG INSTITUCIONAL FINAL
# ==============================

CAPITAL_INICIAL = 1000

# Uso de capital
USO_CAPITAL = 0.60

# Posiciones
MAX_POSICIONES = 3

# Tamaño dinámico
SIZE_EXCELENTE = 0.30
SIZE_BUENO_MIN = 0.15
SIZE_BUENO_MAX = 0.20

# Riesgo
STOP_LOSS = -0.02

# Trailing adaptativo
TRAILING_START = 0.015
TRAILING_GAP = 0.01

# IA thresholds
UMBRAL_EXCELENTE = 0.90
UMBRAL_BUENO = 0.75

# Control
MIN_TRADE_USD = 30
COOLDOWN = 20

# Correlación
CORRELACION = {
    "L1": ["BTC/USDT", "ETH/USDT"],
    "L2": ["SOL/USDT", "AVAX/USDT"],
    "L3": ["ADA/USDT", "XRP/USDT"],
    "L4": ["ATOM/USDT", "LINK/USDT"]
}