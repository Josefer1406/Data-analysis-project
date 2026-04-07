# =========================
# CONFIG INSTITUCIONAL PRO
# =========================

CAPITAL_INICIAL = 1000

# Gestión de riesgo
RIESGO_POR_TRADE = 0.02  # 2%
MAX_POSICIONES = 5
MAX_EXPOSICION_TOTAL = 0.7  # 70% del capital máximo invertido

# Asignación dinámica
MAX_PESO_POR_ACTIVO = 0.30
MIN_PESO_POR_ACTIVO = 0.10

# Umbrales de decisión
UMBRAL_COMPRA = 0.65
UMBRAL_COMPRA_FUERTE = 0.85

# Stop / TP
STOP_LOSS = -0.03
TAKE_PROFIT = 0.05

# Filtro institucional
MIN_SCORE = 2  # mínimo factores cumplidos
COOLDOWN = 3  # ciclos sin reentrada

# Capital mínimo
MIN_CAPITAL_OPERAR = 50
RESERVA_CAPITAL = 0.30  # 30% siempre en cash