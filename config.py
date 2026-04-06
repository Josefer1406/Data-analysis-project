# =========================
# CAPITAL INICIAL
# =========================
CAPITAL_INICIAL = 1000  # puedes cambiarlo

# =========================
# RIESGO
# =========================
RIESGO_POR_TRADE = 0.02  # 2% base (se ajusta dinámicamente)

# =========================
# TIEMPO ENTRE CICLOS (segundos)
# =========================
CYCLE_TIME = 60  # cada 1 minuto

# =========================
# MÁXIMO DE POSICIONES ABIERTAS
# =========================
MAX_POSICIONES = 3

# =========================
# CRYPTOS A ANALIZAR
# =========================
CRYPTOS = [
    # principales
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "ADA/USDT",

    # alta liquidez
    "LTC/USDT",
    "LINK/USDT",

    # crecimiento / altcoins fuertes
    "AVAX/USDT",
    "MATIC/USDT",
    "ATOM/USDT",

    # más volátiles (más riesgo)
    "DOGE/USDT"
]

# =========================
# PARÁMETROS ADAPTATIVOS
# =========================
MIN_SCORE_BASE = 2   # mínimo para considerar entrada

# =========================
# LÍMITES DE SEGURIDAD
# =========================
MAX_RIESGO = 0.1     # máximo 10% del capital por trade

# =========================
# STOP LOSS / TAKE PROFIT
# =========================
STOP_LOSS = -0.02    # -2%
TAKE_PROFIT = 0.05   # +5%