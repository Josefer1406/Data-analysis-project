# ==============================
# CONFIG HEDGE FUND PRO
# ==============================

# Capital
CAPITAL_INICIAL = 1000
USO_CAPITAL = 0.60  # 40% reserva

# Trading
MAX_POSICIONES = 4

# Timeframe
TIMEFRAME = "5m"
CYCLE_TIME = 20

# Riesgo
STOP_LOSS = -0.03

# Trailing
TRAILING_START = 0.02
TRAILING_GAP = 0.015

# Volatilidad
VOLATILIDAD_LIMITE = 0.05
VOLATILIDAD_MIN = 0.001

# Universo
CRYPTOS = [
    "BTC/USDT","ETH/USDT",
    "SOL/USDT","AVAX/USDT","NEAR/USDT",
    "ATOM/USDT","INJ/USDT",
    "ARB/USDT","OP/USDT","SEI/USDT","SUI/USDT",
    "LINK/USDT","APT/USDT"
]

# Correlación REAL
CORRELACION = {
    "L1": ["BTC/USDT", "ETH/USDT"],
    "L2": ["SOL/USDT", "AVAX/USDT", "NEAR/USDT"],
    "L3": ["ARB/USDT", "OP/USDT"],
    "L4": ["ATOM/USDT", "INJ/USDT"],
    "L5": ["SEI/USDT", "SUI/USDT"],
    "L6": ["LINK/USDT", "APT/USDT"]
}