import portfolio
import config

def calcular_size(precio):

    capital = portfolio.capital

    # riesgo dinámico
    riesgo = config.RIESGO_POR_TRADE

    size = (capital * riesgo) / precio

    return size