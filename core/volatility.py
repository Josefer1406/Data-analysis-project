def ajustar_por_volatilidad(precio, volatilidad, capital):

    if volatilidad == 0:
        return capital / precio

    # menos tamaño si es muy volátil
    factor = 1 / (1 + volatilidad * 10)

    capital_ajustado = capital * factor

    size = capital_ajustado / precio

    return size