# =========================
# CONFIG GLOBAL
# =========================

TIMEFRAME = "5m"
CYCLE_TIME = 20

# =========================
# PORTAFOLIO
# =========================
MAX_POSICIONES = 4

CAPITAL_INICIAL = 1000
RESERVA_CAPITAL = 0.40

# Tamaño por trade
RIESGO_ELITE = 0.15
RIESGO_NORMAL = 0.10

# =========================
# FILTROS BASE
# =========================
PROB_MIN = 0.70
SCORE_MIN = 1

# =========================
# ROTACIÓN
# =========================
ROTACION_UMBRAL = 0.08
COOLDOWN_SYMBOL = 120

# =========================
# VOLATILIDAD
# =========================
VOLATILIDAD_LIMITE = 0.05
VOLATILIDAD_MIN = 0.001

# =========================
# UNIVERSO OKX (VALIDADO)
# =========================
CRYPTOS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "AVAX/USDT",
    "ATOM/USDT",
    "OP/USDT",
    "ARB/USDT",
    "APT/USDT",
    "SEI/USDT"
]