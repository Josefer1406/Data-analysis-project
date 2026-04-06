import portfolio
import config
from filters.market_filter import mercado_favorable

def calcular_size(precio):

    capital = portfolio.capital

    # =========================
    # RIESGO BASE
    # =========================
    riesgo = config.RIESGO_POR_TRADE

    # =========================
    # MERCADO FUERTE → MÁS AGRESIVO
    # =========================
    if mercado_favorable():
        riesgo *= 2   # 🔥 DUPLICA inversión

    # =========================
    # LÍMITE DE SEGURIDAD
    # =========================
    riesgo = min(riesgo, 0.1)  # máximo 10% del capital

    size = (capital * riesgo) / precio

    return size