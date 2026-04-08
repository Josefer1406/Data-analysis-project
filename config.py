# ==============================
# CONFIGURACIÓN INSTITUCIONAL PRO
# ==============================

CAPITAL_INICIAL = 1000

# Capital
USO_CAPITAL = 0.60

# Tamaños de posición
SIZE_EXCELENTE = 0.30
SIZE_BUENO_MIN = 0.15
SIZE_BUENO_MAX = 0.20

# Riesgo
STOP_LOSS = -0.015

# Trailing dinámico
TRAILING_START = 0.01
TRAILING_GAP = 0.008

# Control
MAX_POSICIONES = 3
MIN_TRADE_USD = 25

# IA thresholds
UMBRAL_EXCELENTE = 0.90
UMBRAL_BUENO = 0.75

# Cooldown institucional (anti overtrading)
COOLDOWN_BASE = 15

# Correlación
CORRELACION_GRUPOS = {
    "L1": ["BTC/USDT", "ETH/USDT"],
    "L2": ["SOL/USDT", "AVAX/USDT"],
    "L3": ["ADA/USDT", "XRP/USDT", "ATOM/USDT"],
    "L4": ["LINK/USDT"]
}