# =========================
# CONFIG GLOBAL
# =========================

TIMEFRAME = "5m"
CYCLE_TIME = 20

# =========================
# PORTAFOLIO
# =========================
MAX_POSICIONES = 4

# Capital
CAPITAL_INICIAL = 1000
RESERVA_CAPITAL = 0.40  # 40% NO se usa

# Tamaño por trade
RIESGO_ELITE = 0.15
RIESGO_NORMAL = 0.10

# =========================
# IA
# =========================
IA_ADAPTATIVA = True

# Filtros base (IA los ajusta)
PROB_MIN = 0.70
SCORE_MIN = 1

# =========================
# ROTACIÓN
# =========================
ROTACION_UMBRAL = 0.15  # evita rotación por ruido

# Cooldown por activo (anti-recompra)
COOLDOWN_SYMBOL = 120  # segundos

# =========================
# VOLATILIDAD
# =========================
VOLATILIDAD_LIMITE = 0.05
VOLATILIDAD_MIN = 0.001

# =========================
# UNIVERSO
# =========================
CRYPTOS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "ATOM/USDT",
    "AVAX/USDT",
    "OP/USDT",
    "ARB/USDT",
    "SEI/USDT",
    "APT/USDT"
]