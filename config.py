# ==============================
# CONFIG INSTITUCIONAL PRO
# ==============================

CAPITAL_INICIAL = 1000

# 🔥 USO GLOBAL (CLAVE)
USO_CAPITAL = 0.60

# Posiciones
MAX_POSICIONES = 3

# Tamaño institucional
SIZE_EXCELENTE = 0.30
SIZE_BUENO = 0.18

# Riesgo
STOP_LOSS = -0.025

# Trailing institucional dinámico
TRAILING_START = 0.02
TRAILING_GAP = 0.012

# IA thresholds (más estrictos)
UMBRAL_EXCELENTE = 0.92
UMBRAL_BUENO = 0.78

# Control
MIN_TRADE_USD = 40
COOLDOWN_BASE = 25

# Mercado
TIMEFRAME = "5m"

CRYPTOS = [
    "BTC/USDT","ETH/USDT","SOL/USDT","ADA/USDT",
    "XRP/USDT","AVAX/USDT","LINK/USDT","ATOM/USDT"
]

# Correlación institucional
CORRELACION = {
    "L1": ["BTC/USDT", "ETH/USDT"],
    "L2": ["SOL/USDT", "AVAX/USDT"],
    "L3": ["ADA/USDT", "XRP/USDT"],
    "L4": ["ATOM/USDT", "LINK/USDT"]
}