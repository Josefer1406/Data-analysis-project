import config

def calcular_size(precio):

    monto = config.CAPITAL_INICIAL * config.RIESGO_POR_TRADE

    size = monto / precio

    return size