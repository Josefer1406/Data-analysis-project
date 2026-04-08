# ==============================
# CONFIG INSTITUCIONAL PRO
# ==============================

CAPITAL_INICIAL = 1000
USO_CAPITAL = 0.60

MAX_POSICIONES = 3

# Tamaño por convicción
SIZE_EXCELENTE = 0.30
SIZE_BUENO_MIN = 0.10
SIZE_BUENO_MAX = 0.18

# Riesgo
STOP_LOSS = -0.015  # más conservador

# Trailing inteligente
TRAILING_START = 0.02
TRAILING_GAP_BASE = 0.008

# IA thresholds (más estrictos)
UMBRAL_EXCELENTE = 0.92
UMBRAL_BUENO = 0.80

# Control
MIN_TRADE_USD = 40

# Cooldown dinámico base
COOLDOWN_BASE = 30

# Volatilidad
VOLATILIDAD_LIMITE = 0.04

# Correlación
CORRELACION = {
    "L1": ["BTC/USDT", "ETH/USDT"],
    "L2": ["SOL/USDT", "AVAX/USDT"],
    "L3": ["ADA/USDT", "XRP/USDT"],
    "L4": ["ATOM/USDT", "LINK/USDT"]
}