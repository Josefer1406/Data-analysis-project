# =========================
# CONFIG GLOBAL
# =========================

TIMEFRAME = "5m"
CYCLE_TIME = 20

MAX_POSICIONES = 4

# Capital
CAPITAL_INICIAL = 1000
RESERVA_CAPITAL = 0.40

# Inversión
RIESGO_ELITE = 0.15
RIESGO_NORMAL = 0.10

# IA
IA_ADAPTATIVA = True

# Filtro base (se ajusta dinámicamente)
PROB_MIN = 0.70
SCORE_MIN = 1

# Rotación
ROTACION_UMBRAL = 0.15

# Cooldown por activo
COOLDOWN_SYMBOL = 120  # segundos

# Volatilidad
VOLATILIDAD_LIMITE = 0.05
VOLATILIDAD_MIN = 0.001

# Universo (luego se puede hacer dinámico)
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