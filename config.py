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

MAX_EXPOSICION_TOTAL = 0.60   # nunca usar más del 60% del capital
MAX_PESO_EXCELENTE = 0.30     # oportunidades top
MAX_PESO_BUENO = 0.20         # buenas
MAX_PESO_NORMAL = 0.15        # normales

MIN_PROBABILIDAD = 0.60       # filtro IA

# 🔴 CAPITAL MÍNIMO PARA OPERAR
MIN_CAPITAL_OPERAR = 50       # evita operar con capital residual

# ================================
# 🔴 CONTROL DE RIESGO
# ================================

STOP_LOSS = 0.03     # 3% pérdida máxima
TAKE_PROFIT = 0.06   # base (luego lo mejoramos con trailing)

# ================================
# 🧠 FILTROS AVANZADOS
# ================================

CORRELACION_MAXIMA = 0.85     # evita activos muy correlacionados

# ================================
# 📊 EJECUCIÓN
# ================================

SLIPPAGE = 0.001
COMISION = 0.001