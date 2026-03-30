import config


def calcular_size(precio):

    riesgo_total = config.CAPITAL_USDT * config.RIESGO_POR_TRADE

    size = riesgo_total / precio

    return round(size, 4)