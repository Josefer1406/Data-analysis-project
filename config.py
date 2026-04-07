# ================================
# CONFIGURACIÓN CUANT INSTITUCIONAL PRO
# ================================

CRYPTOS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "DOGE/USDT",
    "AVAX/USDT",
    "LINK/USDT",
    "LTC/USDT",
    "ATOM/USDT"
]

TIMEFRAME = "5m"

CAPITAL_INICIAL = 1000

CYCLE_TIME = 60

MAX_POSICIONES = 3

# ================================
# 🔥 RISK ENGINE PRO
# ================================

MAX_EXPOSICION_TOTAL = 0.60   # máximo 60% del capital invertido
RESERVA_CAPITAL = 0.40        # 40% siempre en liquidez

MAX_PESO_EXCELENTE = 0.30     # oportunidades top
MAX_PESO_BUENO = 0.20         # buenas
MAX_PESO_NORMAL = 0.15        # normales

MIN_PROBABILIDAD = 0.60       # filtro IA

MIN_CAPITAL_OPERAR = 50       # evita operar con capital residual

# ================================
# 🔴 CONTROL DE RIESGO
# ================================

STOP_LOSS = 0.03     # 3%
TAKE_PROFIT = 0.06   # base

# ================================
# 🧠 FILTROS AVANZADOS
# ================================

CORRELACION_MAXIMA = 0.85

# ================================
# 📊 EJECUCIÓN
# ================================

SLIPPAGE = 0.001
COMISION = 0.001